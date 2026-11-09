from pathlib import Path
import json,math,collections
import numpy as np
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union
from shapely import contains_xy
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-09_B3_StructureRepair'
p=json.loads((H/'layout_after.json').read_text(encoding='utf-8'))
def rot(x,z,yaw):
 a=math.radians(yaw);return x*math.cos(a)+z*math.sin(a),-x*math.sin(a)+z*math.cos(a)
def body(q):
 x,y,z=q['position'];w,h,d=q['size'];cx,cy,cz=q['center']
 return Polygon([(x+rot(cx+xx,cz+zz,q['yaw'])[0],z+rot(cx+xx,cz+zz,q['yaw'])[1]) for xx,zz in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]])
reports=[]
for r in p['rooms']:
 rid=r['id'];rad=r['r']
 if r['kind']=='core':continue
 qs=[q for q in p['placements'] if q['room']==rid and q['role']!='BenchAccessory'];ob=unary_union([body(q).buffer(.36) for q in qs])
 coords=np.arange(-rad,rad+.01,.28);xx,zz=np.meshgrid(coords,coords);valid=(xx*xx+zz*zz<(rad-.38)**2)&~contains_xy(ob,xx,zz);n=len(coords)
 def nearest(x,z):
  distance=np.where(valid,(xx-x)**2+(zz-z)**2,np.inf);j=int(np.argmin(distance));return (j//n,j%n),float(math.sqrt(distance.flat[j]))
 d=r['doors'][0];start,_=nearest(d['x'],d['z']);seen={start};queue=collections.deque([start])
 while queue:
  y,x=queue.popleft()
  for yy,xxx in [(y+1,x),(y-1,x),(y,x+1),(y,x-1)]:
   if 0<=yy<n and 0<=xxx<n and valid[yy,xxx] and (yy,xxx) not in seen:seen.add((yy,xxx));queue.append((yy,xxx))
 bad=[]
 for d in r['doors']:
  k,dist=nearest(d['x'],d['z'])
  if k not in seen or dist>1:bad.append(dict(name=d['id'],distance=dist,unreachable=k not in seen))
 for q in p['workspaces']:
  if q['room']!=rid:continue
  k,dist=nearest(q['point'][0],q['point'][2])
  if k not in seen or dist>.50:bad.append(dict(name=q['name'],distance=dist,unreachable=k not in seen))
 reports.append(dict(room=rid,placements=len(qs),failed=bad))
 im=Image.new('RGB',(900,900),'#f5f4ef');draw=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16);scale=370/rad
 def pt(x,z):return (450+x*scale,450-z*scale)
 draw.ellipse([pt(-rad,rad),pt(rad,-rad)],outline='#334f61',width=3)
 for q in qs:
  color='#526f80' if '_Dense_' in q['name'] else '#a2b5bb';draw.polygon([pt(x,z) for x,z in body(q).exterior.coords],fill=color,outline='#263c48')
 for d in r['doors']:
  x,z=d['x'],d['z'];draw.line([pt(x*1.06,z*1.06),pt(x*.78,z*.78)],fill='#d29034',width=8);draw.text(pt(x*1.15,z*1.15),d['id'].split('-')[-1],fill='black',font=font)
 draw.text((25,20),rid+' - proposed storage / processing layout',fill='black',font=font);draw.text((25,45),'Dark: added equipment   Light: existing equipment',fill='black',font=font);im.save(O/(rid+'_layout_after.png'))
(H/'density_route_check.json').write_text(json.dumps(reports,indent=2))
print(json.dumps(reports,indent=2));print('FAILED',sum(len(r['failed']) for r in reports))
