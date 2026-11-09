import bpy, json, sys
from pathlib import Path
p=Path(__file__).parent
target=p.parent.parent/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/07.Animator/Player/Clips/Crouch'
target.mkdir(parents=True,exist_ok=True)
reports=[]
for src in sorted((p/'Original').glob('*.fbx')):
    if '--sprint-only' in sys.argv and src.stem!='Crouch_Sprint': continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(src))
    rigs=[o for o in bpy.data.objects if o.type=='ARMATURE']
    if len(rigs)!=1: raise RuntimeError('Expected one skeleton '+src.name)
    rig=rigs[0]
    action=rig.animation_data.action if rig.animation_data else None
    if not action: raise RuntimeError('Missing action '+src.name)
    start,end=action.frame_range
    bpy.context.scene.frame_start=round(start)
    bpy.context.scene.frame_end=round(end)
    name='Player_'+src.stem
    action.name=name
    bpy.ops.object.select_all(action='DESELECT')
    rig.select_set(True)
    bpy.context.view_layer.objects.active=rig
    out=target/(name+'.fbx')
    bpy.ops.export_scene.fbx(filepath=str(out),use_selection=True,object_types={'ARMATURE'},add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0.0,axis_forward='-Z',axis_up='Y',use_armature_deform_only=False)
    reports.append(dict(file=out.name,frames=[float(start),float(end)],fps=bpy.context.scene.render.fps,bones=[b.name for b in rig.data.bones],bytes=out.stat().st_size))
(p/'preparation.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
print('CROUCH_PREPARED',json.dumps([{k:v for k,v in r.items() if k!='bones'} for r in reports]))
