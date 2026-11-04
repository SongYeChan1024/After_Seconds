"""패널 내부와 서로 다른 배치의 공면 중복을 수치 검사한다."""
import json
from pathlib import Path
import numpy as np
repo=Path(__file__).resolve().parents[4]
tmp=repo/'tmp/ArchitectureDetail_20261104'
data=json.loads((tmp/'panel_template.json').read_text())
vertices=np.asarray(data['vertices'])*[1.,1.2,.0176]
triangles=vertices[np.asarray(data['submeshes'][0]).reshape(-1,3)]
cross=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0])
normals=cross/np.maximum(np.linalg.norm(cross,axis=1)[:,None],1e-20)
def area(poly):
 return abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))*.5)
def intersection(subject,cutter):
 signed=sum(cutter[i][0]*cutter[(i+1)%3][1]-cutter[(i+1)%3][0]*cutter[i][1] for i in range(3));sign=1 if signed>0 else -1
 for i in range(3):
  a,b=cutter[i],cutter[(i+1)%3]
  def distance(v):return sign*((b[0]-a[0])*(v[1]-a[1])-(b[1]-a[1])*(v[0]-a[0]))
  result=[]
  for k,p in enumerate(subject):
   q=subject[(k+1)%len(subject)];dp,dq=distance(p),distance(q)
   if dp>=-1e-12:result.append(p)
   if dp*dq<0:result.append(p+(q-p)*dp/(dp-dq))
  subject=result
  if len(subject)<3:return 0
 return area(subject)
overlaps=[]
for i,tri in enumerate(triangles):
 if np.linalg.norm(cross[i])<1e-12:continue
 axis=int(np.argmax(abs(normals[i])))
 for j in range(i+1,len(triangles)):
  if abs(np.dot(normals[i],normals[j]))<.999999:continue
  if np.max(abs((triangles[j]-tri[0])@normals[i]))>1e-7:continue
  value=intersection(list(np.delete(tri,axis,axis=1)),np.delete(triangles[j],axis,axis=1))
  if value>1e-9:overlaps.append({'triangles':[i,j],'area':float(value),'normalDot':float(np.dot(normals[i],normals[j]))})
report={'triangles':len(triangles),'coplanarOverlapPairs':len(overlaps),'overlaps':overlaps}
(repo/'Docs/검수/2026-11-04_Architecture_Detail/panel_internal_overlap.json').write_text(json.dumps(report,indent=2))
print('INTERNAL_OVERLAP_PAIRS',len(overlaps),json.dumps(overlaps[:8]),flush=True)
instances={i['id']:i for i in json.loads((tmp/'instances.json').read_text(encoding='utf-8-sig'))}
manifest=json.loads((tmp/'panel_manifest.json').read_text())
boxes=[]
count=len(data['vertices'])
for item in manifest:
 if item['floor']!='B4':continue
 inst=instances[item['id']];m=np.asarray(inst['matrix']).reshape(4,4)
 mesh=json.loads((tmp/'panels'/(item['id']+'.json')).read_text());v=np.asarray(mesh['vertices'])@m[:3,:3].T+m[:3,3]
 for i in range(item['panels']):
  block=v[i*count:(i+1)*count];boxes.append((item['id'],i,block.min(axis=0),block.max(axis=0)))
pairs=[]
for i,(owner,num,lo,hi) in enumerate(boxes):
 axis=int(np.argmin(hi-lo))
 for other,num2,low,high in boxes[i+1:]:
  if other==owner or np.argmin(high-low)!=axis:continue
  if abs((hi[axis]+lo[axis]-high[axis]-low[axis])*.5)>.002:continue
  overlap=np.minimum(hi,high)-np.maximum(lo,low)
  planar=np.delete(overlap,axis)
  if np.all(planar>.0001):pairs.append({'owners':[owner,other],'panels':[num,num2],'area':float(np.prod(planar))})
print('B4_PANEL_OVERLAP_PAIRS',len(pairs),json.dumps(pairs[:8]),flush=True)
(repo/'Docs/검수/2026-11-04_Architecture_Detail/panel_placement_overlap.json').write_text(json.dumps({'B4Panels':len(boxes),'overlaps':pairs},indent=2))
