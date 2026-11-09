"""Static collision proxies from authored pre-bevel geometry; render meshes untouched."""
from pathlib import Path
import bpy,bmesh,json
H=Path(__file__).resolve().parent;R=H.parents[1]
rows=json.loads((H/'ghost_candidates.json').read_text());manifest=[]
for row in rows:
 if row['empty']<=3:continue
 name=Path(row['asset']).stem;source=next((R/'SourceAssets').rglob(name+'.blend'))
 bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.preferences.filepaths.save_version=0
 objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
 # Original base primitives already enclose their bevelled render surfaces.
 # Keep every part, including cables and panes, so the proxy never opens a solid panel.
 for o in objects:
  for m in list(o.modifiers):o.modifiers.remove(m)
 dep=bpy.context.evaluated_depsgraph_get();parts=[]
 for o in objects:
  me=bpy.data.meshes.new_from_object(o.evaluated_get(dep),depsgraph=dep)
  ob=bpy.data.objects.new(o.name+'_collision',me);bpy.context.collection.objects.link(ob);ob.matrix_world=o.matrix_world.copy()
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();parts.append(ob)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in parts:ob.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();ob=bpy.context.object;ob.name='PC_'+name;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 out=R/'Unity/After_Seconds_Build_V0.01'/Path(row['asset']).parent/(ob.name+'.fbx')
 bpy.ops.export_scene.fbx(filepath=str(out),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE')
 manifest.append(dict(original=row['asset'],asset=out.relative_to(R/'Unity/After_Seconds_Build_V0.01').as_posix(),triangles=len(ob.data.polygons),source=source.relative_to(R).as_posix()))
 print('COLLISION',name,len(ob.data.polygons),flush=True)
(H/'collision_models.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
