"""회전축 분리형 CCTV 아트 V0.01 · 송예찬.
의사코드: 고정 베이스/좌우 목/상하 헤드 분리 -> 연결축 기준 베벨 형상 -> 편집 원본/FBX.
게임 스크립트나 자동 회전은 만들지 않는다.
"""
import bpy,json,math
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
repo=Path(__file__).resolve().parents[2];source=Path(__file__).parent/'CCTV';source.mkdir(exist_ok=True)
dest=repo/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Enemy/CCTV_SecurityCamera_Articulated.fbx'
bpy.ops.wm.read_factory_settings(use_empty=True)
palette={'Housing':(.72,.77,.79,1),'Metal':(.12,.15,.18,1),'Rubber':(.025,.03,.035,1),'Lens':(.005,.03,.05,1),'LED':(.7,.025,.01,1)}
for name,color in palette.items():
    m=bpy.data.materials.new('CCTV_'+name);m.diffuse_color=color
pivots={'Fixed':(0,0,0),'Pan':(0,-.16,0),'Head':(0,-.46,.035)}
groups=defaultdict(list);bevels=[]
def xyz(x,y,z):return (-x,-z,y)
def finish(ob,part,mat,width):
    ob.data.materials.append(bpy.data.materials['CCTV_'+mat])
    for p in ob.data.polygons:p.use_smooth=True
    b=ob.modifiers.new('Manufactured_Bevel','BEVEL');b.width=width;b.segments=3;b.limit_method='ANGLE';b.angle_limit=math.radians(35);b.harden_normals=True;b.use_clamp_overlap=True
    n=ob.modifiers.new('Weighted_Normals','WEIGHTED_NORMAL');n.keep_sharp=True
    ob['bevel_width_m']=width;ob['bevel_segments']=3;ob['rotation_part']=part
    groups[(part,mat)].append(ob);bevels.append({'name':ob.name,'width_m':width,'segments':3})
def box(name,part,mat,at,size,width=.004):
    bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(*at));ob=bpy.context.object;ob.name=name;ob.dimensions=(size[0],size[2],size[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(ob,part,mat,min(width,min(size)*.22));return ob
def cyl(name,part,mat,at,r,depth,axis='Y',width=.002,sides=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=sides,radius=r,depth=depth,location=xyz(*at));ob=bpy.context.object;ob.name=name
    direction=Vector(xyz(*({'X':(1,0,0),'Y':(0,1,0),'Z':(0,0,1)}[axis])));ob.rotation_euler=Vector((0,0,1)).rotation_difference(direction).to_euler();bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);finish(ob,part,mat,width);return ob
box('Ceiling_Base','Fixed','Housing',(0,-.025,0),(.25,.05,.25),.006)
box('Ceiling_Gasket','Fixed','Rubber',(0,-.005,0),(.22,.01,.22),.002)
for x in (-.09,.09):
    for z in (-.09,.09):cyl('Mount_Screw','Fixed','Metal',(x,-.053,z),.009,.009,'Y',.001,12)
cyl('Fixed_Stem','Fixed','Metal',(0,-.105,0),.033,.12)
cyl('Pan_Bearing_Rotor','Pan','Metal',(0,-.16,0),.055,.07)
cyl('Pan_Bearing_Seal','Pan','Rubber',(0,-.198,0),.045,.012,'Y',.001)
cyl('Pan_Neck','Pan','Housing',(0,-.205,0),.032,.08)
box('Yoke_Crossbar','Pan','Housing',(0,-.24,-.06),(.38,.04,.08),.005)
for x in (-.17,.17):
    box('Yoke_Shoulder','Pan','Housing',(x,-.26,-.01),(.04,.04,.18),.004)
    box('Yoke_Arm','Pan','Housing',(x,-.36,.035),(.04,.22,.06),.004)
    cyl('Tilt_Axle','Pan','Metal',(x,-.46,.035),.029,.10,'X',.002)
    cyl('Tilt_Axle_Cap','Pan','Housing',(x*1.19,-.46,.035),.022,.018,'X',.002)
box('Camera_Housing','Head','Housing',(0,-.475,.165),(.24,.17,.40),.012)
box('Camera_Rear_Gasket','Head','Rubber',(0,-.475,-.04),(.22,.145,.014),.003)
box('Camera_Front_Bezel','Head','Rubber',(0,-.475,.378),(.245,.175,.035),.007)
box('Sunshade','Head','Housing',(0,-.36,.185),(.29,.025,.48),.005)
cyl('Lens_Outer','Head','Metal',(0,-.475,.412),.060,.042,'Z',.003,40)
cyl('Lens_Rubber','Head','Rubber',(0,-.475,.438),.049,.015,'Z',.002,40)
cyl('Lens_Glass','Head','Lens',(0,-.475,.450),.041,.010,'Z',.002,40)
cyl('Status_LED','Head','LED',(.092,-.52,.398),.007,.008,'Z',.001,16)
for x in (-.091,.091):
    for y in (-.418,-.532):cyl('Head_Screw','Head','Metal',(x,y,.399),.006,.008,'Z',.001,12)
bpy.ops.wm.save_as_mainfile(filepath=str(source/'CCTV_SecurityCamera_Articulated.blend'))
deps=bpy.context.evaluated_depsgraph_get();joined=[]
for (part,mat),obs in groups.items():
    baked=[]
    for ob in obs:
        me=bpy.data.meshes.new_from_object(ob.evaluated_get(deps),depsgraph=deps);cp=bpy.data.objects.new('Baked_'+ob.name,me);cp.matrix_world=ob.matrix_world.copy();bpy.context.scene.collection.objects.link(cp);baked.append(cp)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in baked:ob.select_set(True)
    bpy.context.view_layer.objects.active=baked[0];bpy.ops.object.join();ob=bpy.context.object;ob.name='CCTV_'+part+'_'+mat;bpy.context.scene.cursor.location=xyz(*pivots[part]);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');joined.append(ob)
bpy.ops.object.select_all(action='DESELECT')
for ob in joined:ob.select_set(True)
bpy.context.view_layer.objects.active=joined[0]
bpy.ops.export_scene.fbx(filepath=str(dest),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,use_mesh_modifiers=True,mesh_smooth_type='FACE',use_custom_props=True)
report={'title':'Articulated CCTV V0.01','author':'송예찬','pivots':pivots,'panAxis':'Unity local Y','tiltAxis':'Unity local X','reviewPanRange':[-90,90],'reviewTiltRange':[-25,25],'bevels':bevels,'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in joined),'model':str(dest),'source':str(source/'CCTV_SecurityCamera_Articulated.blend'),'gameScripts':0}
(source/'cctv_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('CCTV_RESULT',json.dumps({'triangles':report['triangles'],'parts':len(joined),'pivots':pivots}))
