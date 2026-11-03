from pathlib import Path
import json,collections,itertools
R=Path(__file__).parent;data=json.loads((R/'architecture_triangles.json').read_text());groups=collections.defaultdict(list)
def area(p):return sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))*.5
def overlap(a,b):
 poly=a[:];clip=b if area(b)>0 else b[::-1]
 for i in range(3):
  c,d=clip[i],clip[(i+1)%3]
  def side(p):return (d[0]-c[0])*(p[1]-c[1])-(d[1]-c[1])*(p[0]-c[0])
  out=[]
  for k,p in enumerate(poly):
   q=poly[(k+1)%len(poly)];sp,sq=side(p),side(q);ip,iq=sp>=-1e-9,sq>=-1e-9
   if ip:out.append(p)
   if ip!=iq:
    t=sp/(sp-sq);out.append([p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])])
  poly=out
  if len(poly)<3:return 0
 return abs(area(poly))
for x in data:
 x['bounds']=[min(p[0] for p in x['points']),max(p[0] for p in x['points']),min(p[1] for p in x['points']),max(p[1] for p in x['points'])];groups[x['axis'],x['sign'],round(x['plane']*10000)].append(x)
pairs=collections.defaultdict(float);examples=collections.defaultdict(list)
for group in groups.values():
 for a,b in itertools.combinations(group,2):
  if a['path']==b['path']:continue
  aa,bb=a['bounds'],b['bounds']
  if min(aa[1],bb[1])-max(aa[0],bb[0])<.0001 or min(aa[3],bb[3])-max(aa[2],bb[2])<.0001:continue
  v=overlap(a['points'],b['points'])
  if v>.00001:
   key=tuple(sorted([a['path'],b['path']]));pairs[key]+=v
   if len(examples[key])<2:examples[key].append({'axis':a['axis'],'plane':a['plane'],'area':v})
result={'trianglesChecked':len(data),'coplanarRendererPairs':len(pairs),'pairs':[{'a':a,'b':b,'overlapSquareMetres':v,'examples':examples[a,b]} for (a,b),v in sorted(pairs.items(),key=lambda x:-x[1])]};(R/'surface_overlap_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
