"""B1 production baseline and current Decision geometry. Author: 송예찬."""
from pathlib import Path
import sys,json,math,hashlib,copy
H=Path(__file__).resolve().parent; R=H.parents[1]; U=R/'Unity/After_Seconds_Build_V0.01'; A=U/'Assets/Afrer_Seconds'
sys.path.insert(0,str(U/'Temp/ZFightingReview/deps'))
from shapely.geometry import Point,LineString
from shapely.ops import unary_union
O=R/'Docs/Review/2026-11-11_B1_FullFloor';O.mkdir(parents=True,exist_ok=True)
d=json.loads(next((R/'Docs').glob('**/Decision/*/facility_layout.json')).read_text(encoding='utf8'))
f=copy.deepcopy(next(f for f in d['floors'] if f['id']=='B1')); f['art']=d['floor_art_direction']['B1']; f['sourceVersion']=d['version'];f['sourcePlacements']=[p for p in d['placements'] if p['floor']=='B1']
for t in f['tunnels']:t['path']=[t['p'],t['q']]
def conflicts():
 union=unary_union([Point(r['x'],r['v']).buffer(r['r']+.23) for r in f['rooms']]);bad=[]
 for i,t in enumerate(f['tunnels']):
  for u in f['tunnels'][i+1:]:
   o=LineString(t['path']).buffer(2.32).intersection(LineString(u['path']).buffer(2.32)).difference(union)
   if o.area>.025:bad.append(dict(a=t['id'],b=u['id'],area=round(o.area,4)))
 return bad
f['initialConflicts']=conflicts()
# The straight T08 crowds T02/T10 at the small domes. Keep its room connectivity,
# move both approaches to the north rim with a smooth, inspectable curve.
t=next(t for t in f['tunnels'] if t['id']=='B1-T08')
p0=(20, -25.8);p1=(12,-45);p2=(-25,-41);p3=(-26,-22.2)
t['path']=[[sum([((1-u)**3)*p0[j],3*(1-u)**2*u*p1[j],3*(1-u)*u*u*p2[j],u**3*p3[j]]) for j in range(2)] for u in [i/32 for i in range(33)]];t['p']=t['path'][0];t['q']=t['path'][-1]
for r in f['rooms']:
 r['doors']=[]
 for t in f['tunnels']:
  if r['id'] not in [t['a'],t['b']]:continue
  p=t['p'] if r['id']==t['a'] else t['q'];r['doors'].append(dict(id=t['id'],x=p[0]-r['x'],z=r['v']-p[1],angle=math.degrees(math.atan2(r['v']-p[1],p[0]-r['x']))))
f['tunnelConflicts']=conflicts();f['placements']=[];f['workspaces']=[]
(H/'plan.json').write_text(json.dumps(f,ensure_ascii=False,indent=2),encoding='utf8')
protected={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['02.Scripts','07.Animator','01.Scenes'] for p in (A/folder).rglob('*') if p.is_file()}
for p in (A/'05.Model/Props/B2').glob('VA_*'):
 if p.is_file():protected[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
if not (H/'protected_before.json').exists():(H/'protected_before.json').write_text(json.dumps(protected,indent=2))
print(json.dumps(dict(rooms=len(f['rooms']),tunnels=len(f['tunnels']),initial=f['initialConflicts'],remaining=f['tunnelConflicts'],protected=len(protected)),ensure_ascii=False))
