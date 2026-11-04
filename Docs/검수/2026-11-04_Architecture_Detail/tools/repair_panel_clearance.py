"""프레임 안쪽과 맞닿은 가운데 판을 좌우/상하 각 2mm 줄여 공면 중복을 제거한다."""
import json, shutil
from pathlib import Path
import numpy as np
repo=Path(__file__).resolve().parents[4];tmp=repo/'tmp/ArchitectureDetail_20261104'
path=tmp/'panel_template.json';data=json.loads(path.read_text())
v=np.asarray(data['vertices']);physical=v*[1.,1.2,.0176];indices=np.asarray(data['submeshes'][0]).reshape(-1,3)
parent=list(range(len(v)));lookup={}
def root(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
def union(a,b):parent[root(a)]=root(b)
for i,p in enumerate(physical):
 key=tuple(np.round(p,7))
 if key in lookup:union(i,lookup[key])
 else:lookup[key]=i
for a,b,c in indices:union(int(a),int(b));union(int(a),int(c))
groups={}
for i in range(len(v)):groups.setdefault(root(i),[]).append(i)
selected=[]
for members in groups.values():
 size=np.ptp(physical[members],axis=0)
 if np.allclose(size,[.966,1.166,.008],atol=1e-6):selected=members;break
assert selected,'Expected independent enamel plate component'
backup=tmp/'panel_template.before_clearance.json'
if not backup.exists():shutil.copyfile(path,backup)
scale=np.array([.962/.966,1.162/1.166,1.])
v[selected]*=scale
n=np.asarray(data['normals']);n[selected]/=scale;n[selected]/=np.linalg.norm(n[selected],axis=1)[:,None]
data['vertices']=v.tolist();data['normals']=n.tolist();path.write_text(json.dumps(data,separators=(',',':')))
report={'method':'Shrink independent center plate, preserve UV and topology','centerPlateBefore':[.966,1.166,.008],'centerPlateAfter':[.962,1.162,.008],'perSideClearanceMeters':.002,'affectedVertexCorners':len(selected)}
(repo/'Docs/검수/2026-11-04_Architecture_Detail/panel_clearance_fix.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report),flush=True)
