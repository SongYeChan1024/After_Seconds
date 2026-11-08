from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,math,collections
H=Path(__file__).resolve().parent;p=json.loads((H/'layout.json').read_text(encoding='utf8'));grids=json.loads((H/'nav_grid.json').read_text());im=Image.new('RGB',(1600,1600),'#172029');d=ImageDraw.Draw(im)
def rot(x,z,a):a=math.radians(a);return x*math.cos(a)+z*math.sin(a),-x*math.sin(a)+z*math.cos(a)
for ii,g in enumerate(grids):
 r=next(r for r in p['rooms'] if r['id']==g['room']);ox=400+ii%2*800;oy=400+ii//2*800;scale=340/r['r'];n=g['n'];valid=set(g['valid']);door=r['doors'][0]
 def pos(i):return (-g['radius']+i%n*g['cell'],-g['radius']+i//n*g['cell'])
 start=min(valid,key=lambda i:(pos(i)[0]-door['x'])**2+(pos(i)[1]-door['z'])**2);seen={start};q=collections.deque([start])
 while q:
  a=q.popleft()
  for b in [a-1,a+1,a-n,a+n]:
   if b in valid and b not in seen:seen.add(b);q.append(b)
 for i in valid:
  x,z=pos(i);x=ox+x*scale;z=oy-z*scale;sz=g['cell']*scale/2;d.rectangle((x-sz,z-sz,x+sz,z+sz),fill='#345a55' if i in seen else '#62464e')
 for idx,a in enumerate([a for a in p['newPlacements'] if a['room']==g['room']],1):
  x,_,z=a['position'];w,_,dep=a['size'];cx,_,cz=a['center'];pts=[]
  for u,v in [(-w/2,-dep/2),(w/2,-dep/2),(w/2,dep/2),(-w/2,dep/2)]:
   u,v=rot(u+cx,v+cz,a['yaw']);pts.append((ox+(x+u)*scale,oy-(z+v)*scale))
  d.polygon(pts,outline='#ccd2bd',width=2);d.text((ox+x*scale-6,oy-z*scale-10),str(idx),font_size=22,fill='white')
  x,_,z=a['access'];d.ellipse((ox+x*scale-4,oy-z*scale-4,ox+x*scale+4,oy-z*scale+4),fill='#ffdc7f')
 for idx,door in enumerate(r['doors']):d.text((ox+door['x']*scale-15,oy-door['z']*scale-8),'D'+str(idx),font_size=22,fill='#efaf82')
 d.text((ox-350,oy-370),g['room'],font_size=30,fill='white')
 print(g['room'],'accessible',len(seen),'of',len(valid))
im.save(H/'nav_grid.png')
