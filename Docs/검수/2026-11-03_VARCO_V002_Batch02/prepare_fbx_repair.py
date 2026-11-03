import bpy,bmesh,json
from pathlib import Path
R=Path(__file__).parent;P=R.parent.parent/'Unity/After_Seconds_Build_V0.01'
for a in json.loads((R/'unity_prepared_manifest.json').read_text(encoding='utf-8-sig')):
 if a['id'] not in ['P01','P05']:continue
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.fbx(filepath=str(P/a['modelPath']),use_image_search=False)
 for o in [x for x in bpy.context.scene.objects if x.type=='MESH']:
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);isolated=[f for f in bm.faces if all(e.is_boundary for e in f.edges)];bmesh.ops.delete(bm,geom=isolated,context='FACES');bm.to_mesh(o.data);bm.free();o.data.update()
 bpy.ops.wm.save_as_mainfile(filepath=str(R/(a['id']+'_fbx_optimized.blend')))
