# [의사코드] 저장된 배치·반입 명세를 따라 모델/시각 배치와 검수 결과를 재현한다.
# [코딩]
"""의사코드: 내보낸 FBX를 새로 열어 실제 저장 파일의 형상, UV, 재질 수를 다시 검사한다."""
import ast,bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
module=ast.parse((R/'tools'/'prepare_models.py').read_text(encoding='utf-8'))
selected=[node for node in module.body if isinstance(node,(ast.Import,ast.ImportFrom,ast.FunctionDef))]
exec(compile(ast.Module(body=selected,type_ignores=[]),'preparation_helpers','exec'))
names=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [p.parent.name for p in (R/'prepared').glob('*/manifest.json')]
records=[]
for name in names:
    directory=R/'prepared'/name;manifest=json.loads((directory/'manifest.json').read_text(encoding='utf-8'))
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=manifest['fbx'],use_image_search=False)
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];meshes=[]
    for obj in objects:
        mesh=obj.data;bm=bmesh.new();bm.from_mesh(mesh)
        lo=Vector([min(v.co[i] for v in bm.verts) for i in range(3)]);hi=Vector([max(v.co[i] for v in bm.verts) for i in range(3)])
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=(hi-lo).length*1e-7);bm.to_mesh(mesh);bm.free();mesh.update()
        item=audit(mesh,strict=True);item['uvLayers']=len(mesh.uv_layers);item['nonFiniteUVs']=sum(not all(math.isfinite(c) for c in data.uv) for layer in mesh.uv_layers for data in layer.data);item['materialSlots']=len(mesh.materials);meshes.append(item)
    lo,hi=bounds(objects);result={'name':name,'blenderBoundsMin':list(lo),'blenderBoundsMax':list(hi),'unitySizeXYZ':[hi.x-lo.x,hi.z-lo.z,hi.y-lo.y],'meshes':meshes,'accepted':all(not m['strictCrossingPairs'] and not m['boundaryEdges'] and not m['overusedEdges'] and not m['zeroAreaFaces'] and not m['nonFiniteUVs'] and m['uvLayers']>0 for m in meshes)}
    records.append(result);(directory/'fbx_verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print('VERIFIED_FBX',name,result['accepted'],[(m['triangles'],m['strictCrossingPairs'],m['boundaryEdges']) for m in meshes],flush=True)
(R/'prepared'/'fbx_verification.json').write_text(json.dumps(records,indent=2),encoding='utf-8')

# [주석] 검수 자료의 작업 순서와 최신 경로표를 확인한 뒤 사용한다.
