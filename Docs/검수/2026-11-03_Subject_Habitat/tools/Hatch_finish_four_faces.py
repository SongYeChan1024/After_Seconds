"""작성자 송예찬 / 배식구 마감 V0.02
[의사코드]
현재 포드 제작 원본에서 두 문짝의 흰 뒷면에 동일한 인셋·손잡이·힌지 마감을 더한다.
기존 문 object/mesh 이름·피벗·재질 슬롯과 원래 바깥면 기하는 보존한다.
Hatch visual FBX만 다시 내보내며 유리·충돌 FBX 세 개의 바이트 보존을 확인한다.
문 양면과 열린 전달함을 렌더해 네 얼굴 모두 마감됐는지 확인한다.
"""
# [코딩]
import bpy,bmesh,math,json,hashlib,ast,shutil
from pathlib import Path
from mathutils import Vector,Matrix
from io_scene_fbx import parse_fbx,fbx_utils

HERE=Path(__file__).resolve().parent;REPO=HERE.parents[2]
SOURCE=REPO/'SourceAssets/SubjectHabitat/DualFoodHatch.blend'
manifest=json.loads((HERE/'manifest.json').read_text(encoding='utf8'))
assert manifest.get('version','V0.01')=='V0.01','Four-face finish already applied'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
bpy.context.preferences.filepaths.save_version=0
visual=bpy.data.collections['DualFoodHatch_Visual']
white=bpy.data.materials['OP_ClinicalWhite'];black=bpy.data.materials['OP_BlackFrame'];steel=bpy.data.materials['OP_BrushedSteel']
oldscript=(REPO/'tmp/Asset_Placement_20261103/ObservationPod/build_observation_pod.py').read_text(encoding='utf8')
for node in ast.parse(oldscript).body:
 if isinstance(node,ast.FunctionDef) and node.name in {'move_to','mesh_obj','box','tube','audit','export','material'}:
  exec(compile(ast.Module(body=[node],type_ignores=[]),'<shared_geometry>','exec'),globals())

def hashfile(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
preserved={k:hashfile(v) for k,v in manifest['exports'].items() if k!='hatchVisual'}
old_visual=Path(manifest['exports']['hatchVisual'])
backup=HERE/'DualFoodHatch_Visual_before_four_faces.fbx'
if not backup.exists():shutil.copy2(old_visual,backup)
assert hashfile(backup)==manifest['sha256']['hatchVisual'],'Original visual backup must match V0.01 manifest'
def fbx_ids(path):
 root,version=parse_fbx.parse(str(path))
 objs=next(e for e in root.elems if e.id==b'Objects')
 out={}
 for e in objs.elems:
  if e.id not in [b'Model',b'Geometry',b'Material']:continue
  name=e.props[1].decode('utf8').split('\x00')[0]
  out[e.id.decode()+':'+name]=int(e.props[0])
 return out
old_ids=fbx_ids(backup)
S_INV=Matrix.Diagonal(Vector((1/3,1/3,1/2,1)))
Y=-3.975;Z=1.05
changes=[]
for side,label in [(-1,'Exterior'),(1,'Interior')]:
 door=bpy.data.objects['DualFoodHatch_Door'+label+'_Pivot']
 assert door.type=='MESH'
 pose=door.matrix_world.copy();old_mesh_name=door.data.name
 old_materials=list(door.data.materials);old_slots=[m.name for m in old_materials]
 old_vertices=len(door.data.vertices);old_polygons=len(door.data.polygons)
 original_positions=[v.co.copy() for v in door.data.vertices]
 front_props=side
 back=-side;face=Y+side*.215
 hinge_x=-.36 if side==-1 else .36;handle_x=-hinge_x*.70
 added=[]
 def hb(name,loc,dims,mat,bev=.003):
  o=box(name,loc,dims,mat,bev,visual);added.append(o);return o
 def ht(name,points,r,mat):
  o=tube(name,points,r,mat,8,visual);added.append(o);return o
 hb('BackSteelInset',(0,face+back*.017,Z),(.63,.008,.355),steel,.005)
 hb('BackHandleMountUpper',(handle_x,face+back*.024,Z+.085),(.05,.015,.045),black,.003)
 hb('BackHandleMountLower',(handle_x,face+back*.024,Z-.085),(.05,.015,.045),black,.003)
 ht('BackDoorPull',[(handle_x,face+back*.029,Z-.085),(handle_x,face+back*.048,Z-.085),(handle_x,face+back*.048,Z+.085),(handle_x,face+back*.029,Z+.085)],.010,black)
 for z in [Z-.135,Z+.135]:
  bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.021,depth=.085,location=(hinge_x,face+back*.019,z))
  o=bpy.context.object;o.name='BackHingeKnuckle';o.data.materials.append(steel);move_to(o,visual);added.append(o)
 hb('BackLatchCover',(-hinge_x*.92,face+back*.028,Z),(.06,.025,.065),black,.004)
 for o in added:
  world=o.matrix_world.copy();origin=S_INV@world.translation
  for v in o.data.vertices:v.co=(S_INV@(world@v.co))-origin
  o.matrix_world=Matrix.Translation(origin)
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 bpy.ops.object.select_all(action='DESELECT');door.select_set(True)
 for o in added:o.select_set(True)
 bpy.context.view_layer.objects.active=door;bpy.ops.object.join()
 assert door.data.name==old_mesh_name,(door.data.name,old_mesh_name)
 # 마감에 사용한 기존 3개 재질의 슬롯 순서를 강제로 유지한다.
 current=list(door.data.materials);mapping={i:old_slots.index(m.name) for i,m in enumerate(current)}
 polygon_materials=[mapping[p.material_index] for p in door.data.polygons]
 door.data.materials.clear()
 for m in old_materials:door.data.materials.append(m)
 for p,mi in zip(door.data.polygons,polygon_materials):p.material_index=mi
 assert max(abs(a-b) for aa,bb in zip(pose,door.matrix_world) for a,b in zip(aa,bb))<1e-7
 assert len(door.data.vertices)>old_vertices
 # join은 기존 정점 순서를 유지하며 바깥면을 변경하지 않는다.
 original_position_error=max((door.data.vertices[i].co-p).length for i,p in enumerate(original_positions))
 assert original_position_error<1e-7,original_position_error
 changes.append({'door':door.name,'meshName':door.data.name,'materialOrder':old_slots,'originalVerticesPreserved':old_vertices,'oldPolygonsPreserved':old_polygons,'maxOriginalVertexError':original_position_error,'sourcePivot':list(door.matrix_world.translation),'finishedFaces':2,'partsPerDoor':{'leaf':1,'steelInsets':2,'pullHandles':2,'handleMounts':4,'hingeKnuckles':4,'latchCovers':2}})

audits=audit(visual.objects)
bad=[a for a in audits if a['boundaryEdges'] or a['nonManifoldEdges'] or a['zeroAreaFaces'] or a['signedVolume']<=0]
assert not bad,bad
visual.hide_viewport=False;visual.hide_render=False
# Blender's exporter derives new process-dependent IDs from Python hashes. Seed the
# existing name->UID map so all existing FBX Model/Geometry/Material IDs remain exact.
for tag,value in old_ids.items():
 kind,name=tag.split(':',1)
 key='B'+{'Model':'Object','Geometry':'Mesh','Material':'Material'}[kind]+'#'+name
 uid=fbx_utils.UUID(value);fbx_utils._keys_to_uuids[key]=uid;fbx_utils._uuids_to_keys[uid]=key
export(visual,old_visual)
new_ids=fbx_ids(old_visual)
assert old_ids==new_ids,{'changedIds':{k:[v,new_ids.get(k)] for k,v in old_ids.items() if new_ids.get(k)!=v}}
for k,before in preserved.items():assert hashfile(manifest['exports'][k])==before,k
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
manifest['version']='V0.02';manifest['sha256']['hatchVisual']=hashfile(old_visual)
manifest['topology']['DualFoodHatch_Visual']=audits
manifest['fourFaceFinish']={'doors':changes,'allFourVisibleFacesFinished':True,'frontFaceGeometryUnchanged':True,'materialOrderPreserved':True,'fbxObjectGeometryMaterialIdsPreserved':True,'fbxIdMap':new_ids,'innerBackHandleProjectionFromDoorCenter':.058,'minimumEmptyTunnelDepth':.43-2*.058,'preservedOtherFbxHashes':preserved}
manifest['notes'].append('V0.02: each of the two doors is finished on BOTH faces. Original front geometry, mesh/node IDs, pivots and material order preserved. Interior pull handles leave 0.314m clear tunnel depth between their tips.')
(HERE/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
(HERE/'four_face_preservation.json').write_text(json.dumps(manifest['fourFaceFinish'],ensure_ascii=False,indent=2),encoding='utf8')
print('FOUR_FACES_EXPORTED',json.dumps({'idsPreserved':old_ids==new_ids,'visualTriangles':sum(a['triangles'] for a in audits),'clearDepth':.43-2*.058}),flush=True)

# 실제 네 면 검수용 렌더. FBX와 원본 저장 후에만 QA 확대/문 열기를 적용한다.
qa=bpy.data.collections.new('QA_FourFaces');bpy.context.scene.collection.children.link(qa)
qa_root=bpy.data.objects.new('QA_ExpandedPod',None);qa.objects.link(qa_root)
for cname in ['ObservationPod_Visual','ObservationPod_Collision','DualFoodHatch_Visual','DualFoodHatch_Collision']:
 col=bpy.data.collections[cname]
 for o in list(col.objects):o.parent=qa_root
qa_root.scale=(3,3,2)
floor=box('QA_Floor',(0,0,-.08),(14,14,.16),material('QA_Floor',(0.24,.27,.29)),0,qa)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for i,(pos,energy,size) in enumerate([((2,-6,5),1100,3),((-3,-2,4),1000,4),((0,1,5),1400,3)]):
 data=bpy.data.lights.new('QA_Light'+str(i),'AREA');data.energy=energy;data.shape='DISK';data.size=size;o=bpy.data.objects.new(data.name,data);qa.objects.link(o);o.location=pos;aim(o,(0,Y,Z))
cam_data=bpy.data.cameras.new('QA_Camera');cam=bpy.data.objects.new('QA_Camera',cam_data);qa.objects.link(cam);bpy.context.scene.camera=cam
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True;scene.cycles.transmission_bounces=8;scene.cycles.transparent_max_bounces=8
scene.render.resolution_x=1000;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.world.color=(.22,.24,.27);scene.view_settings.view_transform='AgX'
def render(name,eye,target,ortho=1.8):
 cam.location=eye;cam_data.type='ORTHO';cam_data.ortho_scale=ortho;aim(cam,target);scene.render.filepath=str(HERE/name);bpy.ops.render.render(write_still=True)
render('hatch_four_faces_closed_exterior.png',(1.1,Y-2.6,1.7),(0,Y,Z),1.7)
render('hatch_four_faces_closed_interior.png',(-1.1,Y+2.3,1.7),(0,Y,Z),1.7)
for info in manifest['doorPivots']:bpy.data.objects[info['name']].rotation_euler.z=math.radians(info['openPreviewAngle'])
render('hatch_four_faces_open_exterior.png',(.7,Y-2.4,1.65),(0,Y,Z),1.8)
render('hatch_four_faces_open_interior.png',(-.7,Y+2.4,1.65),(0,Y,Z),1.8)
print('FOUR_FACES_RENDERED',flush=True)
# [주석] 양문은 게임 반입용 파일에서 계속 닫혀 있다. QA 개방은 저장하지 않는다.
