"""작성자 송예찬. [의사코드] 보존된 도어 부품의 실치수로 재질 인덱스를 복원하고 재검수한다."""
# [코딩]
import bpy,bmesh,math,json,hashlib,ast
from pathlib import Path
from mathutils import Vector,Matrix
from io_scene_fbx import parse_fbx,fbx_utils
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[2];SOURCE=REPO/'SourceAssets/SubjectHabitat/DualFoodHatch.blend'
manifest=json.loads((HERE/'manifest.json').read_text(encoding='utf8'))
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));bpy.context.preferences.filepaths.save_version=0
visual=bpy.data.collections['DualFoodHatch_Visual']
oldscript=(REPO/'tmp/Asset_Placement_20261103/ObservationPod/build_observation_pod.py').read_text(encoding='utf8')
for node in ast.parse(oldscript).body:
 if isinstance(node,ast.FunctionDef) and node.name in {'move_to','mesh_obj','box','tube','audit','export','material'}:exec(compile(ast.Module(body=[node],type_ignores=[]),'<shared_geometry>','exec'),globals())
S=Matrix.Diagonal(Vector((3,3,2,1)))
assignments=[]
for label in ['Exterior','Interior']:
 o=bpy.data.objects['DualFoodHatch_Door'+label+'_Pivot'];mesh=o.data
 assert [m.name for m in mesh.materials]==['OP_ClinicalWhite','OP_BrushedSteel','OP_BlackFrame']
 adjacency=[set() for v in mesh.vertices]
 for e in mesh.edges:a,b=e.vertices;adjacency[a].add(b);adjacency[b].add(a)
 unused=set(range(len(mesh.vertices)));groups=[]
 while unused:
  stack=[unused.pop()];group=set(stack)
  while stack:
   for other in adjacency[stack.pop()]:
    if other in unused:unused.remove(other);group.add(other);stack.append(other)
  groups.append(group)
 assert len(groups)==15,(o.name,len(groups))
 counts={0:0,1:0,2:0};parts=[]
 for group in groups:
  coords=[S@(o.matrix_world@mesh.vertices[i].co) for i in group]
  minimum=Vector(tuple(min(p[i] for p in coords) for i in range(3)));maximum=Vector(tuple(max(p[i] for p in coords) for i in range(3)));dims=maximum-minimum
  if abs(dims.x-.72)<.003 and abs(dims.z-.45)<.003:index=0;kind='Leaf'
  elif abs(dims.x-.63)<.003 and abs(dims.z-.355)<.003:index=1;kind='SteelInset'
  elif abs(dims.x-.042)<.003 and abs(dims.z-.085)<.003:index=1;kind='HingeKnuckle'
  else:index=2;kind='PullMountOrLatch'
  for p in mesh.polygons:
   if p.vertices[0] in group:p.material_index=index
  counts[index]+=1;parts.append({'kind':kind,'material':mesh.materials[index].name,'centerPhysical':list((minimum+maximum)/2),'dimensionsPhysical':list(dims)})
 assert counts=={0:1,1:6,2:8},(o.name,counts)
 assignments.append({'name':o.name,'components':len(groups),'counts':counts,'parts':parts})

before=json.loads((HERE/'four_face_preservation.json').read_text(encoding='utf8'))['fbxIdMap']
for tag,value in before.items():
 kind,name=tag.split(':',1);key='B'+{'Model':'Object','Geometry':'Mesh','Material':'Material'}[kind]+'#'+name;uid=fbx_utils.UUID(value);fbx_utils._keys_to_uuids[key]=uid;fbx_utils._uuids_to_keys[uid]=key
export(visual,Path(manifest['exports']['hatchVisual']))
root,_=parse_fbx.parse(manifest['exports']['hatchVisual']);objs=next(e for e in root.elems if e.id==b'Objects')
after={e.id.decode()+':'+e.props[1].decode('utf8').split('\x00')[0]:int(e.props[0]) for e in objs.elems if e.id in [b'Model',b'Geometry',b'Material']}
assert before==after
for key,value in manifest['fourFaceFinish']['preservedOtherFbxHashes'].items():assert hashlib.sha256(Path(manifest['exports'][key]).read_bytes()).hexdigest()==value,key
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
manifest['sha256']['hatchVisual']=hashlib.sha256(Path(manifest['exports']['hatchVisual']).read_bytes()).hexdigest()
manifest['topology']['DualFoodHatch_Visual']=audit(visual.objects)
manifest['fourFaceFinish']['materialIndexValidation']=assignments
(HERE/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
(HERE/'four_face_preservation.json').write_text(json.dumps(manifest['fourFaceFinish'],ensure_ascii=False,indent=2),encoding='utf8')
print('MATERIALS_VERIFIED',flush=True)

# 저장 후 QA만 확대해 네 면이 보이는 개폐 이미지를 생성한다.
qa=bpy.data.collections.new('QA_FourFaces');bpy.context.scene.collection.children.link(qa);qa_root=bpy.data.objects.new('QA_ExpandedPod',None);qa.objects.link(qa_root)
for cname in ['ObservationPod_Visual','ObservationPod_Collision','DualFoodHatch_Visual','DualFoodHatch_Collision']:
 for obj in list(bpy.data.collections[cname].objects):obj.parent=qa_root
qa_root.scale=(3,3,2)
floor=box('QA_Floor',(0,0,-.08),(14,14,.16),material('QA_Floor',(.24,.27,.29)),0,qa)
Y=-3.975;Z=1.05
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for i,(pos,energy,size) in enumerate([((2,-6,5),1100,3),((-3,-2,4),1000,4),((0,1,5),1400,3)]):
 data=bpy.data.lights.new('QA_Light'+str(i),'AREA');data.energy=energy;data.shape='DISK';data.size=size;obj=bpy.data.objects.new(data.name,data);qa.objects.link(obj);obj.location=pos;aim(obj,(0,Y,Z))
cd=bpy.data.cameras.new('QA_Camera');cam=bpy.data.objects.new('QA_Camera',cd);qa.objects.link(cam);bpy.context.scene.camera=cam
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True;scene.cycles.transmission_bounces=8;scene.cycles.transparent_max_bounces=8;scene.render.resolution_x=1000;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.world.color=(.22,.24,.27);scene.view_settings.view_transform='AgX'
def render(name,eye,target,size=1.8):
 cam.location=eye;cd.type='ORTHO';cd.ortho_scale=size;aim(cam,target);scene.render.filepath=str(HERE/name);bpy.ops.render.render(write_still=True)
render('hatch_four_faces_closed_exterior.png',(1.1,Y-2.6,1.7),(0,Y,Z),1.7)
render('hatch_four_faces_closed_interior.png',(-1.1,Y+2.3,1.7),(0,Y,Z),1.7)
for info in manifest['doorPivots']:bpy.data.objects[info['name']].rotation_euler.z=math.radians(info['openPreviewAngle'])
render('hatch_four_faces_open_exterior.png',(.7,Y-2.4,1.65),(0,Y,Z))
render('hatch_four_faces_open_interior.png',(-.7,Y+2.4,1.65),(0,Y,Z))
print('FOUR_FACE_MATERIAL_RENDERED',flush=True)
# [주석] 기하·원래 정점·피벗·재질 슬롯·FBX ID는 유지하며 부품별 재질 인덱스만 정확히 복원한다.
