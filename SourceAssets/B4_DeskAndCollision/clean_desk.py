"""Re-export authored desk, removing microscopic bevel slivers after evaluation."""
from pathlib import Path
import bpy,bmesh,json
H=Path(__file__).resolve().parent;R=H.parents[1]
bpy.ops.wm.open_mainfile(filepath=str(H/'PD_ProtocolTable.blend'))
src=[o for o in bpy.context.scene.objects if o.type=='MESH'];dep=bpy.context.evaluated_depsgraph_get();out=[];removed=0
for o in src:
 me=bpy.data.meshes.new_from_object(o.evaluated_get(dep),depsgraph=dep);ob=bpy.data.objects.new(o.name,me);bpy.context.collection.objects.link(ob);ob.matrix_world=o.matrix_world.copy()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges));bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<2e-8];removed+=len(bad)
 bmesh.ops.delete(bm,geom=bad,context='FACES');bm.to_mesh(me);bm.free();out.append(ob)
bpy.ops.object.select_all(action='DESELECT')
for ob in out:ob.select_set(True)
bpy.context.view_layer.objects.active=out[0];bpy.ops.object.join();ob=bpy.context.object;ob.name='PD_ProtocolTable';bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
path=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B4/PD_ProtocolTable.fbx'
bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE')
models=json.loads((H/'models.json').read_text());models['PD_ProtocolTable']['triangles']=len(ob.data.polygons);models['PD_ProtocolTable']['removed_microscopic_slivers']=removed;(H/'models.json').write_text(json.dumps(models,indent=2),encoding='utf8')
print('CLEAN_DESK',len(ob.data.polygons),'removed',removed,flush=True)
