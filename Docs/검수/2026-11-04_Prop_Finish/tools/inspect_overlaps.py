"""실제 삼각형의 같은 방향 공면 면적을 구해 벽·문틀 접촉 후보를 만든다."""
import json,sys,math
from pathlib import Path
from collections import defaultdict
root=Path(sys.argv[1]);triangles=json.loads((root/'architecture_triangles.json').read_text(encoding='utf-8-sig'))
def area(p):return abs(sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p))))*.5 if len(p)>2 else 0
def clip(subject,cutter):
 sign=1 if sum(cutter[i][0]*cutter[(i+1)%3][1]-cutter[(i+1)%3][0]*cutter[i][1] for i in range(3))>=0 else -1
 for i in range(3):
  a,b=cutter[i],cutter[(i+1)%3];out=[]
  def side(p):return sign*((b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]))
  for j,p in enumerate(subject):
   q=subject[(j+1)%len(subject)];sp,sq=side(p),side(q)
   if sp>=-1e-9:out.append(p)
   if (sp>0 and sq<0) or (sp<0 and sq>0):
    t=sp/(sp-sq);out.append([p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])])
  subject=out
  if not subject:break
 return subject
groups=defaultdict(list);pairs={}
for t in triangles:
 axes=[i for i in range(3) if i!=t['axis']];t['poly']=[[p[i] for i in axes] for p in t['vertices']]
 t['bbox']=[min(p[0] for p in t['poly']),min(p[1] for p in t['poly']),max(p[0] for p in t['poly']),max(p[1] for p in t['poly'])]
 key=(t['scene'],t['axis'],t['sign'],round(t['plane']/.0005))
 for delta in (-1,0,1):
  for other in groups[(key[0],key[1],key[2],key[3]+delta)]:
   if other['path']==t['path'] or abs(other['plane']-t['plane'])>.0005:continue
   a,b=t['bbox'],other['bbox']
   if a[0]>=b[2]-1e-6 or b[0]>=a[2]-1e-6 or a[1]>=b[3]-1e-6 or b[1]>=a[3]-1e-6:continue
   polygon=clip(t['poly'],other['poly']);overlap=area(polygon)
   if overlap<.0001:continue
   names=tuple(sorted([t['path'],other['path']]));pk=(t['scene'],)+names
   if pk not in pairs:pairs[pk]={'scene':t['scene'],'a':names[0],'b':names[1],'area':0,'examples':[]}
   p=pairs[pk];p['area']+=overlap
   if len(p['examples'])<4:
    center=[sum(v[i] for v in t['vertices'])/3 for i in range(3)]
    center[t['axis']]=t['plane'];center[axes[0]]=sum(v[0] for v in polygon)/len(polygon);center[axes[1]]=sum(v[1] for v in polygon)/len(polygon)
    normal=[0,0,0];normal[t['axis']]=t['sign']
    p['examples'].append({'area':overlap,'center':center,'normal':normal,'planeGap':abs(t['plane']-other['plane'])})
 groups[key].append(t)
results=sorted((p for p in pairs.values() if p['area']>.002),key=lambda p:p['area'],reverse=True)
for p in results:p['classification']='door_frame_contact_candidate' if any(x in (p['a']+' '+p['b']).lower() for x in ('door','airlock','stair')) else 'wall_ceiling_contact_candidate'
(root/'overlap_candidates.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print('COPLANAR_CANDIDATES',len(results));print(json.dumps([{'scene':p['scene'],'a':p['a'],'b':p['b'],'area':p['area']} for p in results[:8]],indent=2))
