"""VARCO V03 NPC 반입 V0.01 · 송예찬.
의사코드: 원본 리그 GLB 보관 -> 보조 구체 제거 -> 실측 1.8m -> 예각만 1mm 베벨
-> PBR 채널 변환 -> 편집 원본/FBX/반입 검수 출력. 원본 모델은 덮어쓰지 않는다.
"""
import bpy,json,math,shutil
from pathlib import Path
from mathutils import Vector,Matrix
import numpy as np
repo=Path(__file__).resolve().parents[2]
work=repo.parent/'Management/AfterSeconds_B5_Stealth_20261105'
source=Path(__file__).parent/'NPC';source.mkdir(exist_ok=True)
dest=repo/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Enemy'
(dest/'Textures').mkdir(parents=True,exist_ok=True)
reports=[]
for role in ('Researcher','Guard'):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for suffix in ('rig.glb','raw.glb','reference.png'):
        src=work/'Varco_Raw'/f'{role}_{suffix}'
        if src.exists() and src.stat().st_size:shutil.copy2(src,source/src.name)
    bpy.ops.import_scene.gltf(filepath=str(source/f'{role}_rig.glb'))
    arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
    skin=[o for o in bpy.context.scene.objects if o.type=='MESH' and any(m.type=='ARMATURE' for m in o.modifiers)]
    for ob in list(bpy.context.scene.objects):
        if ob.type=='MESH' and ob not in skin:bpy.data.objects.remove(ob,do_unlink=True)
    coords=[o.matrix_world@v.co for o in skin for v in o.data.vertices]
    lo=min(v.z for v in coords);hi=max(v.z for v in coords);scale=1.8/(hi-lo)
    center=Vector(((min(v.x for v in coords)+max(v.x for v in coords))/2,(min(v.y for v in coords)+max(v.y for v in coords))/2,lo))
    transform=Matrix.Scale(scale,4)@Matrix.Translation(-center)
    original={o:o.matrix_world.copy() for o in [arm]+skin}
    for o in [arm]+skin:o.matrix_world=transform@original[o]
    bpy.ops.object.select_all(action='DESELECT')
    for o in [arm]+skin:o.select_set(True)
    bpy.context.view_layer.objects.active=arm;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bevels=[]
    for ob in skin:
        ob.name='AS_V03_'+role
        for p in ob.data.polygons:p.use_smooth=True
        mod=ob.modifiers.new('HardEdge_Bevel_1mm','BEVEL');mod.width=.001;mod.segments=2;mod.limit_method='ANGLE';mod.angle_limit=math.radians(65);mod.use_clamp_overlap=True;mod.harden_normals=True
        # Before skinning, so the bevel retains bone weights and deforms with the body.
        bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_move_up(modifier=mod.name)
        ob['bevel_width_m']=.001;ob['bevel_segments']=2;ob['bevel_angle_degrees']=65
        bevels.append({'mesh':ob.name,'width_m':.001,'segments':2,'angle':65})
        material=ob.data.materials[0];material.name='AS_V03_'+role+'_PBR'
        nodes=material.node_tree.nodes;bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
        base=bs.inputs['Base Color'].links[0].from_node.image
        normal=next(n.image for n in nodes if n.type=='TEX_IMAGE' and any(l.to_node.type=='NORMAL_MAP' for l in n.outputs[0].links))
        packed=next(n.image for n in nodes if n.type=='TEX_IMAGE' and n.image!=base and n.image!=normal)
        for key,im in [('Base',base),('Normal',normal)]:
            im.filepath_raw=str(dest/'Textures'/f'AS_V03_{role}_{key}.png');im.file_format='PNG';im.save()
        a=np.empty(len(packed.pixels),dtype=np.float32);packed.pixels.foreach_get(a);a=a.reshape((-1,4));out=np.ones_like(a);out[:,:3]=a[:,2,None];out[:,3]=1-a[:,1]
        im=bpy.data.images.new(f'AS_V03_{role}_MetallicSmoothness',width=packed.size[0],height=packed.size[1],alpha=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(out.ravel());im.filepath_raw=str(dest/'Textures'/f'AS_V03_{role}_MetallicSmoothness.png');im.file_format='PNG';im.save()
    arm.name='AS_V03_'+role+'_Rig'
    bpy.ops.wm.save_as_mainfile(filepath=str(source/f'AS_V03_{role}.blend'))
    bpy.ops.object.select_all(action='DESELECT')
    for ob in [arm]+skin:ob.select_set(True)
    bpy.context.view_layer.objects.active=arm
    bpy.ops.export_scene.fbx(filepath=str(dest/f'AS_V03_{role}.fbx'),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,add_leaf_bones=False,bake_anim=False,use_mesh_modifiers=True,mesh_smooth_type='FACE',use_custom_props=True,path_mode='AUTO')
    reports.append({'role':role,'sourceHeight':hi-lo,'targetHeight':1.8,'scale':scale,'removedDebugMeshes':True,'bones':len(arm.data.bones),'bevels':bevels,'source':str(source/f'AS_V03_{role}.blend'),'fbx':str(dest/f'AS_V03_{role}.fbx')})
(source/'npc_manifest.json').write_text(json.dumps(reports,indent=2,ensure_ascii=False),encoding='utf-8')
print('NPC_EXPORT_DONE',json.dumps(reports,ensure_ascii=False))
