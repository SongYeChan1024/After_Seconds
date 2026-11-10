from pathlib import Path
import json,math
from shapely.geometry import box
from shapely.affinity import rotate,translate
H=Path(__file__).resolve().parent;C=json.loads((H/'plan.json').read_text(encoding='utf8'))
def bounds(p):
 w,h,d=p['size'];cx,cy,cz=p['center'];x,y,z=p['position'];poly=rotate(box(cx-w/2,cz-d/2,cx+w/2,cz+d/2),-p['yaw'],origin=(0,0));return translate(poly,xoff=x,yoff=z),y+cy-h/2,y+cy+h/2
for room in C['rooms']:
 ps=[p for p in C['placements'] if p['room']==room['id']]
 for i,a in enumerate(ps):
  ba,lo,hi=bounds(a)
  for bb in ps[i+1:]:
   pb,lb,hb=bounds(bb);area=ba.intersection(pb).area
   if area>.025 and min(hi,hb)-max(lo,lb)>.05:print('OVERLAP',a['name'],bb['name'],round(area,3))
print('scaled',[(p['name'],p['relative_scale']) for p in C['placements'] if p.get('relative_scale')])
