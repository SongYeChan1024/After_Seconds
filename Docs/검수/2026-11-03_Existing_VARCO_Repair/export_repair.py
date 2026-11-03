import bpy,json
from pathlib import Path
R=Path(__file__).parent;P=R.parent.parent/'Unity/After_Seconds_Build_V0.01'
items=json.loads((R/'imported_sources.json').read_text(encoding='utf-8-sig'));report=json.loads((R/'local_retopology_report.json').read_text());out=[]
for a in items:
 if not next(x for x in report if x['floor']==a['name'])['accepted']:continue
 bpy.ops.wm.open_mainfile(filepath=str(R/(a['name']+'_retopo.blend')))
 root=Path(a['modelPath']).parent.parent;dst=root/'Repaired/Models'/(a['name']+'_Repaired.fbx');(P/dst).parent.mkdir(parents=True,exist_ok=True)
 bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.context.scene.objects:
  if o.type=='MESH':o.select_set(True)
 bpy.ops.export_scene.fbx(filepath=str(P/dst),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=False,path_mode='STRIP',use_mesh_modifiers=True)
 a['repairedModelPath']=str(dst).replace('\\','/');out.append(a)
(R/'repair_export_manifest.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
