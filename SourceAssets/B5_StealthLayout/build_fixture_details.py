"""B5 CCTV 천장 고정부·계단 벽등 V0.01 · 송예찬.
의사코드: 실측 위치의 고정부/등기구 -> 2~6mm 3분할 베벨 -> 편집 원본/FBX.
"""
import bpy,json
from pathlib import Path
repo=Path(__file__).resolve().parents[2];source=Path(__file__).parent
out=repo/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/B5/B5_Fixture_Details.fbx'
bpy.ops.wm.read_factory_settings(use_empty=True)
report=[]
for name,color in [('Metal',(.095,.125,.145,1)),('Light',(.62,.9,1,1))]:
    mat=bpy.data.materials.new('SL_'+name);mat.diffuse_color=color
def box(name,u,h,v,sx,sy,sz,kind,width):
    bpy.ops.mesh.primitive_cube_add(size=1,location=(24-u,16-v,h));o=bpy.context.object;o.name='SL_'+kind+'_'+name;o.dimensions=(sx,sz,sy);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(bpy.data.materials['SL_'+kind])
    for p in o.data.polygons:p.use_smooth=True
    mod=o.modifiers.new('Manufactured_Bevel','BEVEL');mod.width=width;mod.segments=3;mod.harden_normals=True;mod.use_clamp_overlap=True
    normal=o.modifiers.new('Weighted_Normals','WEIGHTED_NORMAL');normal.keep_sharp=True
    o['bevel_width_m']=width;o['bevel_segments']=3;report.append({'name':name,'width_m':width,'segments':3})
box('C1_MountPost',37.5,3.92,25,.06,.16,.06,'Metal',.005)
box('C1_MountPlate',37.5,3.985,25,.24,.025,.24,'Metal',.004)
box('StairA_LampLower_Body',42.15,5.2,18.18,1.0,.18,.09,'Metal',.006)
box('StairA_LampLower_Lens',42.15,5.2,18.235,.88,.10,.025,'Light',.003)
box('StairA_LampUpper_Body',39.18,9.6,28.25,.09,.18,1.0,'Metal',.006)
box('StairA_LampUpper_Lens',39.235,9.6,28.25,.025,.10,.88,'Light',.003)
bpy.ops.wm.save_as_mainfile(filepath=str(source/'B5_Fixture_Details.blend'))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.fbx(filepath=str(out),use_selection=True,axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,use_mesh_modifiers=True,mesh_smooth_type='FACE')
(source/'fixture_manifest.json').write_text(json.dumps({'title':'B5 Fixture Details V0.01','author':'송예찬','bevels':report},ensure_ascii=False,indent=2),encoding='utf-8')
print('FIXTURE_DETAILS_DONE')
