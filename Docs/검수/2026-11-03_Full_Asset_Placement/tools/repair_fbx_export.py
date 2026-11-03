# [의사코드] 저장된 배치·반입 명세를 따라 모델/시각 배치와 검수 결과를 재현한다.
# [코딩]
"""의사코드: FBX 정밀도 변환 뒤 재발한 국소 교차만 패치하고 내보낸 파일을 다시 읽어 통과까지 검사한다."""
import ast,bpy,bmesh,hashlib,json,math,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
module=ast.parse((R/'tools'/'prepare_models.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in module.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'helpers','exec'))
names=sys.argv[sys.argv.index('--')+1:]
for name in names:
    directory=R/'prepared'/name;manifest=json.loads((directory/'manifest.json').read_text(encoding='utf-8'));fbx=Path(manifest['fbx']);history=[]
    for attempt in range(4):
        bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(fbx),use_image_search=False)
        objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];measurements=[]
        for obj in objects:
            bpy.context.view_layer.objects.active=obj;obj.select_set(True);mesh=obj.data;bm=bmesh.new();bm.from_mesh(mesh)
            lo=Vector([min(v.co[i] for v in bm.verts) for i in range(3)]);hi=Vector([max(v.co[i] for v in bm.verts) for i in range(3)])
            bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=(hi-lo).length*1e-7);bm.to_mesh(mesh);bm.free();mesh.update();cleanup(mesh)
            check=audit(mesh,strict=True);measurements.append(check)
        good=all(not m['strictCrossingPairs'] and not m['boundaryEdges'] and not m['overusedEdges'] for m in measurements)
        history.append({'attempt':attempt,'measurements':measurements})
        if good:break
        for obj in objects:
            bpy.context.view_layer.objects.active=obj;check=patch_crossings(obj.data)
            if obj.data.has_custom_normals:obj.data.normals_split_custom_set([(0,0,0)]*len(obj.data.loops))
            obj.data.set_sharp_from_angle(angle=math.radians(40));mod=obj.modifiers.new('ExportWeightedNormals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=50;bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=False,object_types={'MESH'},add_leaf_bones=False,axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,use_mesh_modifiers=True,mesh_smooth_type='OFF',bake_anim=False,path_mode='STRIP',embed_textures=False)
    if not good:raise RuntimeError(name+' failed exported FBX repair')
    manifest['fbxSha256']=hashlib.sha256(fbx.read_bytes()).hexdigest();manifest['exportRepair']=history;manifest['triangles']=sum(m['triangles'] for m in measurements)
    for index,m in enumerate(measurements):manifest['meshes'][index]['final']=m
    for mat in manifest['materials']:mat['baseColorFactor']=[1,1,1,1]
    (directory/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');print('EXPORT_REPAIRED',name,history[-1],flush=True)

# [주석] 검수 자료의 작업 순서와 최신 경로표를 확인한 뒤 사용한다.
