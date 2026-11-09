from pathlib import Path
import json,math,copy
from shapely.geometry import LineString,Point
H=Path(__file__).resolve().parent;R=H.parents[1]
p=json.loads((R/'SourceAssets/B3_FullFloor/layout.json').read_text(encoding='utf-8'))
if not (H/'layout_before.json').exists():(H/'layout_before.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
rooms={r['id']:r for r in p['rooms']}; t=next(t for t in p['tunnels'] if t['id']=='B3-T08')
def unit(a,b):
 d=[b[0]-a[0],b[1]-a[1]];l=math.hypot(*d);return [v/l for v in d]
a=[-29,20];b=[24,15];knots=[[-17,33],[12,29]]
da=unit(a,knots[0]);db=unit(b,knots[-1])
t['p']=[a[i]+da[i]*5.2 for i in range(2)];t['q']=[b[i]+db[i]*7.2 for i in range(2)]
base=[t['p']]+knots+[t['q']];path=[base[0]]
for i in [1,2]:
 k=base[i];u=unit(k,base[i-1]);v=unit(k,base[i+1]);trim=5
 before=[k[j]+u[j]*trim for j in range(2)];after=[k[j]+v[j]*trim for j in range(2)]
 path.append(before)
 for n in range(1,25):
  s=n/24;path.append([(1-s)**2*before[j]+2*s*(1-s)*k[j]+s*s*after[j] for j in range(2)])
path.append(base[-1]);fine=[path[0]]
for a,b in zip(path,path[1:]):
 steps=max(1,math.ceil(math.dist(a,b)/.45))
 fine.extend([[a[j]+(b[j]-a[j])*n/steps for j in range(2)] for n in range(1,steps+1)])
t['path']=fine;t['control_points']=base;t['length']=round(LineString(fine).length,3);t['type']='곡선 터널';t['repair']='T02/T07 출입 접합 중첩 해소'
for rid in ['C03','C04']:
 r=rooms[rid];d=next(d for d in r['doors'] if d['id']=='B3-T08');pos=t['p'] if rid=='C03' else t['q']
 d.update(x=pos[0]-r['x'],z=-pos[1]+r['v'],angle=math.degrees(math.atan2(-pos[1]+r['v'],pos[0]-r['x'])))
issues=[]
for other in p['tunnels']:
 if other==t:continue
 footprint=LineString([other['p'],other['q']]).buffer(2.28,cap_style=2)
 overlap=LineString(fine).buffer(2.28,cap_style=2).intersection(footprint)
 for r in p['rooms']:overlap=overlap.difference(Point(r['x'],r['v']).buffer(r['r']))
 if overlap.area>.01:issues.append((other['id'],overlap.area))
assert not issues,issues
(H/'layout_route.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
print('T08 route',t['length'],'m',len(fine),'points; corridor overlap candidates',issues)
