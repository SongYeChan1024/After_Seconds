import bpy, json
from pathlib import Path
p = Path(__file__).parent
target = p.parent.parent / 'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/07.Animator/Player/Clips/VarcoFirstPerson'
target.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(p / 'Original/throw_baseball.fbx'))
rigs = [o for o in bpy.data.objects if o.type == 'ARMATURE']
assert len(rigs) == 1
rig = rigs[0]
action = rig.animation_data.action
start, end = action.frame_range
bpy.context.scene.frame_start = round(start)
bpy.context.scene.frame_end = round(end)
action.name = 'Player_Overhand_Varco'
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.export_scene.fbx(filepath=str(target / 'Player_Overhand_Varco.fbx'),use_selection=True,object_types={'ARMATURE'},add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0.0,axis_forward='-Z',axis_up='Y',use_armature_deform_only=False)
(p / 'preparation.json').write_text(json.dumps(dict(frames=[float(start),float(end)],fps=bpy.context.scene.render.fps,bones=[b.name for b in rig.data.bones],source='throw_baseball'),indent=2),encoding='utf-8')
print('Prepared animation-only FBX', start, end)
