"""B5 소품 UV 유지 감면/LOD 제작 V0.02 · 송예찬.
의사코드: 원본 정점/UV/노멀/재질 슬롯 읽기 -> 동일 속성 정점만 병합 ->
Collapse 감면 L0/L1 -> 노멀 유지 -> 원본+수정자 blend 및 FBX 출력. 원본 모델은 보존.
"""
import bpy,json,math,bmesh
from pathlib import Path
from mathutils import Vector
source=Path(__file__).parent/'Optimized_Props';repo=Path(__file__).resolve().parents[2]
unity=repo/'Unity/After_Seconds_Build_V0.01'
data=json.loads((source/'mesh_input.json').read_text(encoding='utf-8-sig'))
bpy.ops.wm.read_factory_settings(use_empty=True)
hi=bpy.data.collections.new('Original_ReadOnly_Geometry');bpy.context.scene.collection.children.link(hi)
lo=bpy.data.collections.new('Optimized_LOD0_LOD1');bpy.context.scene.collection.children.link(lo)
report=[];exports=[]
def xyz(v):return (-v[0],-v[2],v[1])
for item in data:
    vv=item['vertices'];uv=item['uv'];norm=item['normals'];uv2=item['uv2'];lookup={};verts=[];norms=[];uvs=[];uvs2=[];indices=[]
    for k,v in enumerate(vv):
        key=tuple(round(x,7) for x in v)+tuple(round(x,6) for x in uv[k])+tuple(round(x,5) for x in norm[k])
        if key not in lookup:
            lookup[key]=len(verts);verts.append(xyz(v));norms.append(xyz(norm[k]));uvs.append(uv[k]);uvs2.append(uv2[k] if len(uv2)==len(vv) else (0,0))
        indices.append(lookup[key])
    faces=[];slots=[]
    for slot,tris in enumerate(item['submeshes']):
        for k in range(0,len(tris),3):faces.append((indices[tris[k]],indices[tris[k+2]],indices[tris[k+1]]));slots.append(slot)
    me=bpy.data.meshes.new(item['id']+'_SourceMesh');me.from_pydata(verts,[],faces);me.update()
    for slot in range(len(item['submeshes'])):me.materials.append(bpy.data.materials.new(item['id']+'_MaterialSlot_'+str(slot)))
    layer=me.uv_layers.new(name='UVMap');layer2=me.uv_layers.new(name='UV2') if len(uv2)==len(vv) else None
    for p,slot in zip(me.polygons,slots):
        p.material_index=slot;p.use_smooth=True
        for li in p.loop_indices:
            ix=me.loops[li].vertex_index;layer.data[li].uv=uvs[ix]
            if layer2:layer2.data[li].uv=uvs2[ix]
    me.normals_split_custom_set([norms[l.vertex_index] for l in me.loops])
    original=bpy.data.objects.new(item['id']+'_Original',me.copy());hi.objects.link(original);original.hide_render=True;original.hide_set(True)
    # Normal/UV split vertices in the earlier bevel mesh occupy the same point.
    # Weld geometric positions before collapse, while retaining loop UVs, to prevent cracks.
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=0.000001);bm.normal_update()
    for edge in bm.edges:
        if edge.is_manifold and edge.calc_face_angle()>math.radians(50):edge.smooth=False
    bm.to_mesh(me);bm.free();me.update()
    levels=[]
    stem=item['name'].replace('_BevelSmooth','').replace('_Repaired','')
    for level,factor in ((0,1.0),(1,.4)):
        target=int(item['target']*factor);obj=bpy.data.objects.new(stem+'_B5_L'+str(level),me.copy());lo.objects.link(obj)
        dec=obj.modifiers.new('UV_Layout_Preserving_Collapse','DECIMATE');dec.decimate_type='COLLAPSE';dec.ratio=min(1,target/item['triangles']);dec.use_collapse_triangulate=True
        if 'Workbench' in item['name']:
            dec.decimate_type='DISSOLVE';dec.angle_limit=math.radians(1.0 if level==0 else 6.0);dec.delimit={'UV','MATERIAL','SEAM'}
            tri=obj.modifiers.new('Planar_Triangulation','TRIANGULATE');tri.keep_custom_normals=True
        normal=obj.modifiers.new('Weighted_Surface_Normals','WEIGHTED_NORMAL');normal.keep_sharp='Workbench' not in item['name'];normal.weight=50
        obj['original_triangles']=item['triangles'];obj['target_triangles']=target;obj['uv_layout']='original atlas, no unwrap';obj['bevel']='existing source bevel retained by geometry simplification'
        dep=bpy.context.evaluated_depsgraph_get();ev=obj.evaluated_get(dep);mesh=ev.to_mesh();count=sum(len(p.vertices)-2 for p in mesh.polygons)
        old_bounds=[min(v[i] for v in verts) for i in range(3)]+[max(v[i] for v in verts) for i in range(3)]
        new_bounds=[min(v.co[i] for v in mesh.vertices) for i in range(3)]+[max(v.co[i] for v in mesh.vertices) for i in range(3)]
        levels.append({'level':level,'triangles':count,'vertices':len(mesh.vertices),'maxBoundsDelta':max(abs(a-b) for a,b in zip(old_bounds,new_bounds)),'fbx':item['folder']+'/'+obj.name+'.fbx','mesh':obj.name});ev.to_mesh_clear()
        exports.append((obj,unity/levels[-1]['fbx']))
    report.append({'id':item['id'],'source':item['source'],'name':item['name'],'originalTriangles':item['triangles'],'levels':levels})
bpy.ops.wm.save_as_mainfile(filepath=str(source/'B5_Optimized_Props.blend'))
for obj,path in exports:
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,use_mesh_modifiers=True,mesh_smooth_type='FACE')
(source/'optimization_manifest.json').write_text(json.dumps({'title':'B5 optimized props V0.02','author':'송예찬','method':'Weld coincident geometric vertices (1e-6m), retain per-loop UV atlas/material slots, collapse decimation and weighted normals. Workbench uses planar dissolve to preserve countertop/sink instead of aggressive collapse. Original geometry and editable modifiers retained.','meshes':report},ensure_ascii=False,indent=2),encoding='utf-8')
print('PROP_OPTIMIZATION_DONE',json.dumps([{'name':r['name'],'original':r['originalTriangles'],'levels':[x['triangles'] for x in r['levels']]} for r in report]))
