"""기존 벽의 실제 삼각형으로 완전히 덮이는 영역에만 입체 마감 패널을 배치한다."""
# 의사코드: 기존 벽 평면 추출 → 실내 면 선택 → 월드 격자별 완전 피복 검사
# → 제작 패널을 기존 부모의 로컬 공간으로 변환 → 겹치지 않는 UV2와 메타데이터 저장.
import json,math
import numpy as np
from pathlib import Path
from collections import defaultdict
REPO=Path(__file__).resolve().parents[4];TMP=REPO/'tmp/ArchitectureDetail_20261104'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def signed(p):return sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))*.5 if len(p)>2 else 0
def area(p):return abs(signed(p))
def clean(p):
 result=[]
 for q in p:
  if not result or math.dist(result[-1],q)>1e-9:result.append(q)
 if len(result)>1 and math.dist(result[0],result[-1])<1e-9:result.pop()
 return result if len(result)>2 and area(result)>1e-12 else []
def half(poly,a,b,sign,inside):
 result=[]
 def side(v):return sign*((b[0]-a[0])*(v[1]-a[1])-(b[1]-a[1])*(v[0]-a[0]))
 for i,p in enumerate(poly):
  q=poly[(i+1)%len(poly)];sp=side(p);sq=side(q)
  if sp>=0 if inside else sp<=0:result.append(p)
  if sp*sq<0:
   t=sp/(sp-sq);result.append([p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])])
 return clean(result)
def difference(poly,cutter):
 sign=1 if signed(cutter)>0 else -1;remainder=poly;result=[]
 for i,a in enumerate(cutter):
  if not remainder:break
  b=cutter[(i+1)%3];outside=half(remainder,a,b,sign,False)
  if outside:result.append(outside)
  remainder=half(remainder,a,b,sign,True)
 return result
def covered(rect,triangles):
 fragments=[rect]
 for tri in triangles:
  fragments=[piece for p in fragments for piece in difference(p,tri)]
  if not fragments:return True
 return sum(area(p) for p in fragments)<1e-7
test=[[0,0],[1,0],[1,1],[0,1]]
assert covered(test,[[[0,0],[1,0],[0,1]],[[1,0],[1,1],[0,1]]])
assert not covered(test,[[[0,0],[1,0],[0,1]]])
assert not covered(test,[[[0,0],[1,0],[.5,.3]],[[1,0],[1,1],[.7,.5]],[[1,1],[0,1],[.5,.7]],[[0,1],[0,0],[.3,.5]]])
print('PANEL_COVERAGE_TESTS_OK',flush=True)

geometry=read(TMP/'geometry.json');instances=read(TMP/'instances.json');template=read(TMP/'panel_template.json')
tv=np.asarray(template['vertices'],dtype=float);tn=np.asarray(template['normals'],dtype=float);uv=np.asarray(template['uv'],dtype=float);ti=template['submeshes'][0]
output=TMP/'panels';output.mkdir(exist_ok=True);manifest=[]
for inst in instances:
 if inst['role']!='wall':continue
 source=geometry[inst['mesh']];matrix=np.asarray(inst['matrix'],dtype=float).reshape(4,4);inverse=np.linalg.inv(matrix);world=np.asarray(source['vertices'])@matrix[:3,:3].T+matrix[:3,3];axis=0 if inst['worldSize'][0]<inst['worldSize'][2] else 2;uaxis=2 if axis==0 else 0
 groups=defaultdict(list)
 for indices in source['submeshes']:
  for i in range(0,len(indices),3):
   v=world[indices[i:i+3]];n=np.cross(v[1]-v[0],v[2]-v[0]);length=np.linalg.norm(n)
   if length<.002 or abs(n[axis])/length<.99999 or np.ptp(v[:,axis])>.0001:continue
   sign=1 if n[axis]>0 else -1;plane=float(np.mean(v[:,axis]));groups[(sign,round(plane/.0005))].append(v[:,[uaxis,1]].tolist())
 if not groups:continue
 # 외곽 벽은 실내 방향만, 실내 독립 칸막이는 양쪽을 마감한다.
 center=inst['worldCenter'];near=min(abs(center[axis]-inst['spaceMin'][axis]),abs(center[axis]-inst['spaceMax'][axis]));facing=1 if inst['facing'][axis]>=0 else -1;signs=(-1,1) if near>.65 else (facing,)
 placements=[]
 for sign in signs:
  candidates=[(k,p) for k,p in groups.items() if k[0]==sign]
  if not candidates:continue
  key,triangles=max(candidates,key=lambda item:sum(area(p) for p in item[1]));points=[p for tri in triangles for p in tri];umin=min(p[0] for p in points)+.018;umax=max(p[0] for p in points)-.018;vmin=min(p[1] for p in points)+.018;vmax=max(p[1] for p in points)-.018;plane=key[1]*.0005
  for col in range(math.floor(umin),math.ceil(umax)):
   for row in range(math.floor(vmin/1.2),math.ceil(vmax/1.2)):
    lo=max(umin,col)+.009;hi=min(umax,col+1)-.009;bottom=max(vmin,row*1.2)+.009;top=min(vmax,(row+1)*1.2)-.009
    if hi-lo<.18 or top-bottom<.20:continue
    rect=[[lo,bottom],[hi,bottom],[hi,top],[lo,top]]
    relevant=[t for t in triangles if max(p[0] for p in t)>=lo and min(p[0] for p in t)<=hi and max(p[1] for p in t)>=bottom and min(p[1] for p in t)<=top]
    if not covered(rect,relevant):continue
    placements.append((sign,plane,(lo+hi)/2,(bottom+top)/2,hi-lo,top-bottom))
 if not placements:continue
 vertices=[];normals=[];uv0=[];uv2=[];indices=[];columns=math.ceil(math.sqrt(len(placements)));rows=math.ceil(len(placements)/columns)
 for number,(sign,plane,u,v,w,h) in enumerate(placements):
  normal=np.zeros(3);normal[axis]=sign;up=np.array([0.,1.,0.]);right=np.cross(up,normal);basis=np.stack((right,up,normal),axis=1);center=np.zeros(3);center[axis]=plane+sign*.011;center[uaxis]=u;center[1]=v;size=np.array([w,h,.018]);points=(tv*size)@basis.T+center;local=points@inverse[:3,:3].T+inverse[:3,3]
  world_n=(tn/size)@basis.T;local_n=world_n@matrix[:3,:3];local_n/=np.maximum(np.linalg.norm(local_n,axis=1)[:,None],1e-12)
  offset=len(vertices);vertices.extend(local.tolist());normals.extend(local_n.tolist());uv0.extend(uv.tolist());uv2.extend(((uv*.90+.05+np.array([number%columns,number//columns]))/np.array([columns,rows])).tolist());indices.extend(x+offset for x in ti)
 data={'vertices':vertices,'normals':normals,'uv':uv0,'uv2':uv2,'submeshes':[indices]}
 assert all(math.isfinite(x) for v in vertices+normals for x in v)
 (output/(inst['id']+'.json')).write_text(json.dumps(data,separators=(',',':')),encoding='utf-8')
 manifest.append({k:inst[k] for k in ('id','scene','floor','path')});manifest[-1].update({'panels':len(placements),'triangles':len(indices)//3,'sourceCoverageChecked':True,'maxProjectionBeyondOriginal':.020})
(TMP/'panel_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('WALL_PANEL_PLACEMENTS',sum(x['panels'] for x in manifest),'WALL_INSTANCES',len(manifest),'TRIANGLES',sum(x['triangles'] for x in manifest),flush=True)
