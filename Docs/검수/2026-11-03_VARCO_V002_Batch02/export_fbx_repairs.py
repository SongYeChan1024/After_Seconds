import bpy,json
from pathlib import Path
R=Path(__file__).parent;P=R.parent.parent/'Unity/After_Seconds_Build_V0.01'
for a in json.loads((R/'unity_prepared_manifest.json').read_text(encoding='utf-8-sig')):
 if a['id'] not in ['P01','P05']:continue
 bpy.ops.wm.open_mainfile(filepath=str(R/(a['id']+'_fbx_retopo.blend')))
 bpy.ops.export_scene.fbx(filepath=str(P/a['modelPath']),use_selection=False,object_types={'MESH'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=False,path_mode='STRIP',use_mesh_modifiers=True)
