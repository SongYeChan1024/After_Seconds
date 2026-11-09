import json,math,hashlib,copy
from pathlib import Path
from shapely.geometry import Point,LineString
from shapely.ops import unary_union
H=Path(__file__).resolve().parent;R=H.parents[1];U=R/'Unity/After_Seconds_Build_V0.01';A=U/'Assets/Afrer_Seconds'
(R/'Docs/Review/2026-11-09_B2_FullFloor').mkdir(parents=True,exist_ok=True)
d=json.loads((R/'Docs/도면/Decision/원형공동/facility_layout.json').read_text(encoding='utf8'));f=copy.deepcopy(next(f for f in d['floors'] if f['id']=='B2'))
f['art']=d['floor_art_direction']['B2'];f['sourceVersion']=d['version'];f['sourcePlacements']=[p for p in d['placements'] if p['floor']=='B2'];f['pipeSection']={'radius':2.5,'centerY':1.35,'floorWidth':4.208,'crown':3.85,'outerThickness':.18}
for t in f['tunnels']:t['path']=[t['p'],t['q']];t['h']=3.85;t['w']=4.2
for r in f['rooms']:
 r['doors']=[]
 for t in f['tunnels']:
  if r['id'] not in [t['a'],t['b']]:continue
  p=t['p'] if t['a']==r['id'] else t['q'];r['doors'].append(dict(id=t['id'],x=p[0]-r['x'],z=r['v']-p[1],angle=math.degrees(math.atan2(r['v']-p[1],p[0]-r['x']))))
union=unary_union([Point(r['x'],r['v']).buffer(r['r']+.25) for r in f['rooms']]);bad=[]
for i,t in enumerate(f['tunnels']):
 for u in f['tunnels'][i+1:]:
  overlap=LineString(t['path']).buffer(2.72).intersection(LineString(u['path']).buffer(2.72)).difference(union)
  if overlap.area>.025:bad.append({'a':t['id'],'b':u['id'],'area':overlap.area,'center':[overlap.centroid.x,overlap.centroid.y]})
f['initialTunnelConflicts']=bad
(H/'plan.json').write_text(json.dumps(f,ensure_ascii=False,indent=2),encoding='utf8');print('conflicts',bad)
protected={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['02.Scripts','07.Animator','01.Scenes'] for p in (A/folder).rglob('*') if p.is_file()}
(H/'protected_before.json').write_text(json.dumps(protected,indent=2))
(H/'before_B2.unity.backup').write_bytes((A/'01.Scenes/Stage/Level_B2_Circular.unity').read_bytes())
print('baseline',len(protected),'rooms',len(f['rooms']),'tunnels',len(f['tunnels']))
