from pathlib import Path
import json,math
from shapely.geometry import Polygon
H=Path(__file__).resolve().parent;p=json.loads((H/'layout.json').read_text(encoding='utf-8'));moves=[]
def rot(x,z,y):a=math.radians(y);return x*math.cos(a)+z*math.sin(a),-x*math.sin(a)+z*math.cos(a)
def shape(q):
 cx,cy,cz=q['center'];w,h,d=q['size'];return Polygon([(q['position'][0]+rot(cx+x,cz+z,q['yaw'])[0],q['position'][2]+rot(cx+x,cz+z,q['yaw'])[1]) for x,z in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]])
servers=[q for q in p['placements'] if q['room']=='E02' and q['model'].startswith('BS_ServerRack')];others=[shape(q).buffer(.25) for q in p['placements'] if q['room']=='E02' and q not in servers]
found=None
for shift in [0,.4,-.4,.8,-.8]:
 proposed=[]
 for i,q in enumerate(servers):
  x=1.8 if i<6 else 5.3;z=(i%6-2.5)*1.02+shift;y=90 if i<6 else 270;dx,dz=rot(q['center'][0],q['center'][2],y);v=dict(q,position=[x-dx,0,z-dz],yaw=y);proposed.append(v)
 if not any(shape(q).intersects(o) for q in proposed for o in others):found=proposed;break
if found is None:raise RuntimeError('Server aisle overlaps equipment')
for old,new in zip(servers,found):old.update(new);moves.append(old)
for q in p['placements']:
 if q['room'] not in ['C01','N01'] or 'Central' not in q['name']:continue
 trial=dict(q,yaw=round(q['yaw']/90)*90);other=[shape(t).buffer(.25) for t in p['placements'] if t['room']==q['room'] and t!=q and t['role']!='BenchAccessory']
 if not any(shape(trial).intersects(o) for o in other):q.update(trial);moves.append(q)
p['workspaces']=[]
for q in p['placements']:
 if q['role']=='BenchAccessory':continue
 cx,cy,cz=q['center'];dx,dz=rot(cx,cz+q['size'][2]/2+.57,q['yaw']);p['workspaces'].append(dict(room=q['room'],name=q['name'],point=[q['position'][0]+dx,0,q['position'][2]+dz]))
for z in p['zones']:
 q=next(q for q in p['placements'] if q['name']==z['name']);z.update(polygon=list(shape(q).exterior.coords)[:-1],yaw=q['yaw'])
(H/'alignment.json').write_text(json.dumps(moves,indent=2));(H/'layout.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8');print('Aligned',len(moves))
