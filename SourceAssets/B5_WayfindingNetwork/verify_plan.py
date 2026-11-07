"""실제 선 폭·표기 영역으로 안내선 배치안의 교차/간격을 검사한다. 작성자 송예찬."""
from pathlib import Path
import json,math,itertools,collections
OUT=Path(__file__).resolve().parents[2]/'Docs/도면/Decision/원형공동/B5_안내체계'
p=json.loads((OUT/'wayfinding_plan.json').read_text(encoding='utf-8'))
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def pd(p,a,b):
 d=[b[0]-a[0],b[1]-a[1]];dd=d[0]**2+d[1]**2
 t=max(0,min(1,((p[0]-a[0])*d[0]+(p[1]-a[1])*d[1])/dd)) if dd else 0
 return math.dist(p,[a[0]+d[0]*t,a[1]+d[1]*t])
def sd(a,b,c,d):
 c1,c2,c3,c4=cross(a,b,c),cross(a,b,d),cross(c,d,a),cross(c,d,b)
 if c1*c2<0 and c3*c4<0:return 0
 return min(pd(a,c,d),pd(b,c,d),pd(c,a,b),pd(d,a,b))
def rect(l):
 f=l['forward'];r=[f[1],-f[0]];q=l['position'];return [[q[0]+r[0]*x*l['width']/2+f[0]*z*l['length']/2,q[1]+r[1]*x*l['width']/2+f[1]*z*l['length']/2] for x,z in [(-1,-1),(1,-1),(1,1),(-1,1)]]
def inside(q,poly):
 cs=[cross(a,b,q) for a,b in zip(poly,poly[1:]+poly[:1])];return all(x>=0 for x in cs) or all(x<=0 for x in cs)
segments=[(path['id'],path['code'],a,b) for path in p['paths'] for a,b in zip(path['points'],path['points'][1:])]
crossings=[];near=[];minimum=1e9
for (i,c,a,b),(j,d,e,f) in itertools.combinations(segments,2):
 if c==d:continue
 margin=(p['route_codes'][c]['width']+p['route_codes'][d]['width'])/2
 distance=sd(a,b,e,f);gap=distance-margin
 minimum=min(minimum,gap)
 if gap<-.00001:crossings.append(dict(a=i,b=j,gap=gap))
 elif gap<.10:near.append(dict(a=i,b=j,gap=gap))
label_collisions=[];line_label=[];label_min=1e9
for a,b in itertools.combinations(p['labels'],2):
 ra,rb=rect(a),rect(b)
 distance=0 if inside(ra[0],rb) or inside(rb[0],ra) else min(sd(x,y,z,w) for x,y in zip(ra,ra[1:]+ra[:1]) for z,w in zip(rb,rb[1:]+rb[:1]))
 if distance<.10:label_collisions.append(dict(a=a['id'],b=b['id'],gap=distance))
for l in p['labels']:
 r=rect(l)
 for i,c,a,b in segments:
  distance=0 if inside(a,r) or inside(b,r) else min(sd(a,b,x,y) for x,y in zip(r,r[1:]+r[:1]));gap=distance-p['route_codes'][c]['width']/2
  label_min=min(label_min,gap)
  if gap<.10:line_label.append(dict(label=l['id'],path=i,gap=gap))
graph=collections.defaultdict(list)
for e in p['corridors']:
 graph[e['a']].append((e['b'],e['code']));graph[e['b']].append((e['a'],e['code']))
destinations=[d['code'] for d in p['destinations']]
missing=[]
for start,end in itertools.permutations(destinations,2):
 queue=[start];visited={start}
 for n in queue:
  if n=='S01' and n!=start:continue
  for q,_ in graph[n]:
   if q not in visited:visited.add(q);queue.append(q)
 if end not in visited:missing.append([start,end])
r=dict(destinations=len(destinations),sectors=len(p['sectors']),corridors=len(p['corridors']),paths=len(p['paths']),segments=len(segments),labels=len(p['labels']),differentRouteOverlaps=crossings,belowTenCmClearance=near,minimumDifferentRouteEdgeGapM=minimum,labelOverlaps=label_collisions,lineLabelConflicts=line_label,minimumLineLabelGapM=label_min,directedDestinationPairs=210,unreachable=missing,roomRoutingFailures=p['room_routing_failures'],scope='2D full stroke widths and rectangular floor-label bounds; same-purpose junctions are intentional. Collision/floor confirmation is a separate Unity probe.')
(OUT/'geometry_validation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:(len(v) if isinstance(v,list) else v) for k,v in r.items()},ensure_ascii=False))
if crossings or near or label_collisions or line_label or missing or p['room_routing_failures']:raise SystemExit(1)
