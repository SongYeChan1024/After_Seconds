"""작성자 송예찬 / 2026-11-03
[의사코드]
기존 관찰 포드 원본을 복사해 유리와 충돌에 같은 배식구 개구를 낸다.
실치수 양면 문짝·손잡이·힌지와 비어 있는 전달함을 만들고 문 회전 중심을 둔다.
사용자 확대 스케일(Blender 3,3,2 / Unity 3,2,3)에 맞게 가구 치수를 보정한다.
원본과 Assets는 건드리지 않고 별도 FBX·Blender·검수 결과를 저장한다.
"""
# [코딩]
import bpy,bmesh,math,json,hashlib,ast,sys
from pathlib import Path
from mathutils import Vector,Matrix

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
SOURCE=REPO/'SourceAssets/SubjectHabitat';SOURCE.mkdir(parents=True,exist_ok=True)
ORIGINAL=REPO/'SourceAssets/ObservationPod/ObservationPod.blend'
bpy.ops.wm.open_mainfile(filepath=str(ORIGINAL))
bpy.context.preferences.filepaths.save_version=0
visual=bpy.data.collections['ObservationPod_Visual']
collision=bpy.data.collections['ObservationPod_Collision']
white=bpy.data.materials['OP_ClinicalWhite'];black=bpy.data.materials['OP_BlackFrame']
steel=bpy.data.materials['OP_BrushedSteel'];glass=bpy.data.materials['OP_ClearGlass']
led=bpy.data.materials['OP_CoolWhiteLED'];seal=bpy.data.materials['OP_HatchSeal']
# 기존 제작 도구의 원시 도형 함수를 현재 컬렉션에 결합한다.
oldscript=(REPO/'tmp/Asset_Placement_20261103/ObservationPod/build_observation_pod.py').read_text(encoding='utf8')
tree=ast.parse(oldscript)
for node in tree.body:
 if isinstance(node,ast.FunctionDef) and node.name in {'move_to','mesh_obj','lathe','box','tube','ring','audit','export','material'}:
  exec(compile(ast.Module(body=[node],type_ignores=[]),'<shared_geometry>','exec'),globals())

for o in list(visual.objects):
 if 'Hatch' in o.name or 'FoodHatch' in o.name:
  bpy.data.objects.remove(o,do_unlink=True)
# 작은 배식구에 맞춰 전면 자오선의 큰 빈 구간도 복원한 뒤 개구만 잘라낸다.
front=bpy.data.objects.get('ObservationPod_MeridianFrame_06')
if front:bpy.data.objects.remove(front,do_unlink=True)
R=1.33;E=1.86
pts=[(0,-1.344,.15),(0,-1.344,E)]
pts.extend((0,-(R+.014)*math.cos(math.pi*.5*j/28),E+(R+.014)*math.sin(math.pi*.5*j/28)) for j in range(1,27))
tube('ObservationPod_MeridianFrame_06',pts,.012,black)

def difference(obj,cutter):
 mod=obj.modifiers.new('ActualFoodPassage','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
 bpy.context.view_layer.objects.active=obj
 bpy.ops.object.modifier_apply(modifier=mod.name)
 bm=bmesh.new();bm.from_mesh(obj.data)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 bmesh.ops.triangulate(bm,faces=list(bm.faces))
 bm.to_mesh(obj.data);bm.free();obj.data.update()

# 도어가 열리면 유리/벽 충돌이 뒤를 막지 않는 .78 x .51m 관통 개구.
cut=box('Temporary_HatchCut',(0,-1.33,.525),(.78/3,.50,.51/2),white)
shell=bpy.data.objects['ObservationPod_GlassShell'];difference(shell,cut)
difference(bpy.data.objects['ObservationPod_MeridianFrame_06'],cut)
affected=[]
for o in list(collision.objects):
 xs=[v.co.x for v in o.data.vertices];ys=[v.co.y for v in o.data.vertices]
 if min(xs)<=.14 and max(xs)>=-.14 and min(ys)<-1.18:
  difference(o,cut);affected.append(o.name)
bpy.data.objects.remove(cut,do_unlink=True)

hatch=bpy.data.collections.new('DualFoodHatch_Visual');bpy.context.scene.collection.children.link(hatch)
hatch_collision=bpy.data.collections.new('DualFoodHatch_Collision');bpy.context.scene.collection.children.link(hatch_collision)
Y=-3.975;Z=1.05
def hb(name,loc,dims,mat,bev=.003):return box(name,loc,dims,mat,bev,hatch)
def ht(name,pts,r,mat):return tube(name,pts,r,mat,8,hatch)
def cylinder(name,loc,r,h,mat):
 bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=h,location=loc)
 o=bpy.context.object;o.name=name;o.data.materials.append(mat);move_to(o,hatch);return o
def join(objects,name,origin):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=objects[0];o.name=name
 bpy.context.scene.cursor.location=origin;bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 return o

static=[]
# 전달함: 중앙은 빈 공간이며 네 벽과 앞뒤 마감 프레임만 있다.
for x in [-.39,.39]:static.append(hb('TunnelSide',(x,Y,Z),(.02,.42,.51),steel))
for z in [Z-.255,Z+.255]:static.append(hb('TunnelTopBottom',(0,Y,z),(.80,.42,.02),steel))
for side in [-1,1]:
 face=Y+side*.215
 for x in [-.445,.445]:static.append(hb('FaceSide',(x,face,Z),(.11,.035,.75),white,.008))
 for z in [Z-.315,Z+.315]:static.append(hb('FaceTopBottom',(0,face,z),(.89,.035,.12),white,.008))
 # 문 주변 고무 패킹은 두 얼굴에서 똑같이 보인다.
 for x in [-.376,.376]:static.append(hb('DoorGasket',(x,face,Z),(.018,.014,.49),seal,.001))
 for z in [Z-.233,Z+.233]:static.append(hb('DoorGasket',(0,face,z),(.75,.014,.018),seal,.001))
 static.append(hb('StatusRecess',(.30*side,face+side*.023,Z+.315),(.17,.012,.035),black,.003))
 static.append(hb('StatusLED',(.30*side,face+side*.031,Z+.315),(.10,.008,.012),led,.001))
static_obj=join(static,'DualFoodHatch_StaticTunnelAndFrames',(0,Y,Z))

door_info=[]
for side,label in [(-1,'Exterior'),(1,'Interior')]:
 face=Y+side*.215
 hinge_x=-.36 if side==-1 else .36
 handle_x=-hinge_x*.70
 items=[hb('DoorLeaf',(0,face,Z),(.72,.027,.45),white,.006)]
 items.append(hb('DoorSteelInset',(0,face+side*.017,Z),(.63,.008,.355),steel,.005))
 items.append(hb('HandleMountUpper',(handle_x,face+side*.024,Z+.085),(.05,.015,.045),black,.003))
 items.append(hb('HandleMountLower',(handle_x,face+side*.024,Z-.085),(.05,.015,.045),black,.003))
 items.append(ht('DoorPull',[(handle_x,face+side*.029,Z-.085),(handle_x,face+side*.080,Z-.085),(handle_x,face+side*.080,Z+.085),(handle_x,face+side*.029,Z+.085)],.012,black))
 for z in [Z-.135,Z+.135]:items.append(cylinder('HingeKnuckle',(hinge_x,face+side*.019,z),.021,.085,steel))
 items.append(hb('LatchCover',(-hinge_x*.92,face+side*.028,Z),(.06,.025,.065),black,.004))
 o=join(items,'DualFoodHatch_Door'+label+'_Pivot',(hinge_x,face,Z))
 door_info.append({'name':o.name,'physicalPivot':[hinge_x,face,Z],'sourcePivot':[hinge_x/3,face/3,Z/2],'hingeAxisUnity':'Y','physicalDoorSize':[.72,.45,.027],'openPreviewAngle':-105 if side==-1 else 105})
 # 별도 단순 충돌 상자. 문짝과 동일 좌표 및 문 회전 중심을 사용한다.
 c=box('DualFoodHatch_Door'+label+'_Collider',(0,face,Z),(.72,.027,.45),white,0,hatch_collision)
 bpy.context.scene.cursor.location=(hinge_x,face,Z);bpy.context.view_layer.objects.active=c;bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
for x in [-.39,.39]:box('DualFoodHatch_TunnelSideCollider',(x,Y,Z),(.02,.42,.51),white,0,hatch_collision)
for z in [Z-.255,Z+.255]:box('DualFoodHatch_TunnelCapCollider',(0,Y,z),(.80,.42,.02),white,0,hatch_collision)

# 모든 새 메시의 세계 좌표와 문 회전 중심을 동일한 역스케일로 변환한다.
S_INV=Matrix.Diagonal(Vector((1/3,1/3,1/2,1)))
for col in [hatch,hatch_collision]:
 for o in col.objects:
  world=o.matrix_world.copy();target_origin=S_INV@world.translation
  for v in o.data.vertices:v.co=(S_INV@(world@v.co))-target_origin
  o.matrix_world=Matrix.Translation(target_origin);o.data.update()

def normalize_meshes(objects):
 for o in objects:
  if o.type!='MESH':continue
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces))
  bm.to_mesh(o.data);bm.free();o.data.update()
normalize_meshes(list(visual.objects)+list(collision.objects)+list(hatch.objects)+list(hatch_collision.objects))
audits={col.name:audit(col.objects) for col in [visual,collision,hatch,hatch_collision]}
bad=[a for aa in audits.values() for a in aa if a['boundaryEdges'] or a['nonManifoldEdges'] or a['zeroAreaFaces'] or a['signedVolume']<=0]
if bad:raise RuntimeError('Topology failed '+json.dumps(bad))

exports={'shellVisual':'ObservationPod_HabitatShell.fbx','shellCollision':'ObservationPod_HabitatCollision.fbx','hatchVisual':'DualFoodHatch_Visual.fbx','hatchCollision':'DualFoodHatch_Collision.fbx'}
for col in [visual,collision,hatch,hatch_collision]:col.hide_viewport=False;col.hide_render=False
for key,col in [('shellVisual',visual),('shellCollision',collision),('hatchVisual',hatch),('hatchCollision',hatch_collision)]:export(col,HERE/exports[key])
for col in [collision,hatch_collision]:col.hide_render=True;col.hide_viewport=True
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'DualFoodHatch.blend'))

manifest={'name':'DualFoodHatch','author':'송예찬','date':'2026-11-03','sourceBlend':'SourceAssets/SubjectHabitat/DualFoodHatch.blend','exports':{k:str(HERE/v) for k,v in exports.items()},'sha256':{k:hashlib.sha256((HERE/v).read_bytes()).hexdigest() for k,v in exports.items()},'podUnityRootPosition':[0,0,10.32],'podUnityRootScale':[3,2,3],'fbxModelChildYawUnity':180,'alignment':'All four FBXs use original pod coordinates and the SAME original FBX axes. Parent under existing ObservationPod root, local position zero, local rotation(0,180,0), local scale one. Keep root scale(3,2,3). Hatch geometry is inverse-scaled already; do not apply another inverse scale. Source Blender forward -Y becomes Unity +Z before existing child yaw180, then world front -Z.','worldHatchCenterRelativePod':[0,1.05,-3.975],'worldHatchCenterInRoom':[0,1.05,6.345],'physicalDimensions':{'outerFrameWidth':1.0,'outerFrameHeight':.75,'doorWidth':.72,'doorHeight':.45,'tunnelDepth':.42,'wallOpeningWidth':.78,'wallOpeningHeight':.51},'doorPivots':door_info,'affectedShellCollisionPanels':affected,'materials':[{'name':m.name,'baseColor':list(m.diffuse_color)} for m in [white,black,steel,glass,led,seal]],'topology':audits,'notes':['Old white-backed decorative hatch was removed from new shell visual.','Glass and matching collision panels have actual openings.','New front meridian frame has only the hatch-sized cutout.','Tunnel is hollow between two identical opposing doors.','Both doors are exported closed with independent vertical hinges.','Separate simple door Collider objects must be parented to corresponding door pivots before future animation; no game code is included.','Root must preserve original old FBXs/prefab as backup; these are replacement derivatives.']}
(HERE/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print('EXPORTED',json.dumps({k:sum(a['triangles'] for a in v) for k,v in audits.items()}),flush=True)
if '--export-only' in sys.argv:raise SystemExit(0)

# 양쪽 실물 프리뷰와 실제 관통 프리뷰. QA만 확대하고 원본 FBX 좌표는 위에서 저장했다.
qa=bpy.data.collections.new('QA_DualHatch');bpy.context.scene.collection.children.link(qa)
qa_root=bpy.data.objects.new('QA_ExpandedPod',None);qa.objects.link(qa_root)
for col in [visual,collision,hatch,hatch_collision]:
 for o in list(col.objects):o.parent=qa_root
qa_root.scale=(3,3,2)
floor=box('QA_Floor',(0,0,-.08),(14,14,.16),material('QA_Floor',(0.24,.27,.29)),0,qa)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for i,(pos,energy,size) in enumerate([((2,-6,5),1000,3),((-3,-2,4),900,4),((0,1,5),1100,3)]):
 data=bpy.data.lights.new('QA_Light'+str(i),'AREA');data.energy=energy;data.shape='DISK';data.size=size;o=bpy.data.objects.new(data.name,data);qa.objects.link(o);o.location=pos;aim(o,(0,Y,Z))
cam_data=bpy.data.cameras.new('QA_Camera');cam=bpy.data.objects.new('QA_Camera',cam_data);qa.objects.link(cam);bpy.context.scene.camera=cam
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True;scene.cycles.transmission_bounces=8;scene.cycles.transparent_max_bounces=8
scene.render.resolution_x=1000;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.world.color=(.22,.24,.27);scene.view_settings.view_transform='AgX'
def render(name,eye,target,ortho=1.6):
 cam.location=eye;cam_data.type='ORTHO';cam_data.ortho_scale=ortho;aim(cam,target);scene.render.filepath=str(HERE/name);bpy.ops.render.render(write_still=True)
render('hatch_exterior.png',(1.1,Y-2.6,1.7),(0,Y,Z),1.7)
render('hatch_interior.png',(-1.1,Y+2.3,1.7),(0,Y,Z),1.7)
# 문 개방 프리뷰에서 관통함을 가로막는 숨은 유리/흰 판이 없는지 육안 확인한다.
for info in door_info:
 o=bpy.data.objects[info['name']];o.rotation_euler.z=math.radians(info['openPreviewAngle'])
render('hatch_both_open.png',(.7,Y-2.4,1.65),(0,Y,Z),1.8)
print('RENDERED',flush=True)
# [주석] 게임에는 닫힌 상태 FBX만 들어간다. 문 개방은 모델 피벗 검수이며 게임 로직이 아니다.
