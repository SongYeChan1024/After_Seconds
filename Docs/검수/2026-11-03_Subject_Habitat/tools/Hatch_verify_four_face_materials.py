"""작성자 송예찬. [의사코드] 실제 저장 FBX의 앞뒤 부품별 재질과 전달함 빈 깊이를 검사한다."""
# [코딩]
import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parent;manifest=json.loads((HERE/'manifest.json').read_text(encoding='utf8'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=manifest['exports']['hatchVisual'])
S=Matrix.Diagonal(Vector((3,3,2,1)));reports=[];back_pulls={}
for side,label in [(-1,'Exterior'),(1,'Interior')]:
 o=bpy.data.objects['DualFoodHatch_Door'+label+'_Pivot'];mesh=o.data;face=-3.975+side*.215
 names=[m.name.split('.')[0] for m in mesh.materials];assert names==['OP_ClinicalWhite','OP_BrushedSteel','OP_BlackFrame'],names
 adjacency=[set() for v in mesh.vertices]
 for e in mesh.edges:a,b=e.vertices;adjacency[a].add(b);adjacency[b].add(a)
 unused=set(range(len(mesh.vertices)));groups=[]
 while unused:
  stack=[unused.pop()];group=set(stack)
  while stack:
   for other in adjacency[stack.pop()]:
    if other in unused:unused.remove(other);group.add(other);stack.append(other)
  groups.append(group)
 assert len(groups)==15,len(groups)
 parts=[];counts={'Front':{'steel':0,'black':0},'Back':{'steel':0,'black':0}}
 for group in groups:
  coords=[S@(o.matrix_world@mesh.vertices[i].co) for i in group]
  lo=Vector(tuple(min(p[i] for p in coords) for i in range(3)));hi=Vector(tuple(max(p[i] for p in coords) for i in range(3)));dims=hi-lo;center=(lo+hi)/2
  actual={names[p.material_index] for p in mesh.polygons if p.vertices[0] in group}
  if abs(dims.x-.72)<.003 and abs(dims.z-.45)<.003:expected='OP_ClinicalWhite';kind='SharedLeaf';side_name='Shared'
  elif abs(dims.x-.63)<.003 and abs(dims.z-.355)<.003:expected='OP_BrushedSteel';kind='Inset';side_name='Front' if (center.y-face)*side>0 else 'Back'
  elif abs(dims.x-.042)<.003 and abs(dims.z-.085)<.003:expected='OP_BrushedSteel';kind='Hinge';side_name='Front' if (center.y-face)*side>0 else 'Back'
  else:
   expected='OP_BlackFrame';side_name='Front' if (center.y-face)*side>0 else 'Back'
   kind='Pull' if dims.z>.15 else 'MountOrLatch'
  assert actual=={expected},(label,kind,side_name,actual,expected)
  if side_name!='Shared':counts[side_name]['steel' if expected=='OP_BrushedSteel' else 'black']+=1
  if side_name=='Back' and kind=='Pull':back_pulls[label]=(lo.y,hi.y)
  parts.append({'side':side_name,'part':kind,'expected':expected,'actual':list(actual),'centerPhysical':list(center),'sizePhysical':list(dims)})
 assert counts=={'Front':{'steel':3,'black':4},'Back':{'steel':3,'black':4}},counts
 reports.append({'name':o.name,'materialSlots':names,'parts':parts,'counts':counts,'accepted':True})
clear=back_pulls['Interior'][0]-back_pulls['Exterior'][1]
assert clear>=.30,clear
out={'accepted':True,'version':'V0.02','doors':reports,'actualEmptyDepthBetweenInwardHandles':clear,'fourFacesUseMatchingMaterials':True,'note':'Directly reimported final FBX, not inferred from source material slot existence.'}
(HERE/'four_face_material_verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print('FOUR_FACE_MATERIALS_ACCEPTED',clear,flush=True)
# [주석] 바깥/안쪽 각 문짝의 양면을 실제 부품 연결 성분으로 나누어 검사한다.
