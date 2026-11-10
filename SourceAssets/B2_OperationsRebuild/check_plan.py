import json,math
from pathlib import Path
from shapely.geometry import Point,LineString,box,Polygon
from shapely import affinity
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;p=json.loads((H/'plan.json').read_text(encoding='utf8'))
im=Image.new('RGB',(1600,1250),'#131c26');d=ImageDraw.Draw(im);f=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
issues=[]
for index,r in enumerate(p['rooms']):
 ox=200+(index%4)*400;oy=210+(index//4)*410;s=14
 def screen(q):return(ox+q[0]*s,oy-q[1]*s)
 rad=r['r'];d.ellipse((ox-rad*s,oy-rad*s,ox+rad*s,oy+rad*s),outline='#9aafbe',width=2);d.text((ox-170,oy-190),r['id']+' operations layout',font=f,fill='white')
 shapes=[]
 for a in [a for a in p['placements'] if a['room']==r['id'] and a['position'][1]<.5]:
  w,h,dep=a['size'];cx,_,cz=a['center'];x,y,z=a['position']
  poly=affinity.translate(affinity.rotate(box(cx-w/2,cz-dep/2,cx+w/2,cz+dep/2),-a['yaw'],origin=(0,0)),x,z)
  d.polygon([screen(q) for q in poly.exterior.coords],fill='#4c7182',outline='#a5d7e8');d.text(screen((x-.3,z)),a['model'].split('_')[-1][:3],font=f,fill='#e1e7d6')
  for name,b in shapes:
   if poly.intersection(b).area>.07:issues.append((r['id'],'prop-overlap',name,a['name'],round(poly.intersection(b).area,2)))
  shapes.append((a['name'],poly))
 if r['id'] in p['decks']:
  de=p['decks'][r['id']];d.line([screen(q) for q in de['outline']],fill='#e9ae51',width=2)
  for st in de['stairs']+de['links']:
   pts=[(q[0],q[2]) for q in st];d.line([screen(q) for q in pts],fill='#ffca7b',width=5)
   footprint=LineString(pts).buffer(.8,cap_style=2)
   for name,b in shapes:
    if footprint.intersection(b).area>.07:issues.append((r['id'],'stair-overlap',name,round(footprint.intersection(b).area,2)))
 for a in r['doors']:
  q=screen((a['x'],a['z']));d.ellipse((q[0]-5,q[1]-5,q[0]+5,q[1]+5),fill='#73dc89');d.text(q,a['id'][3:],font=f,fill='#73dc89')
im.save(H/'layout_preview.png')
(H/'offline_issues.json').write_text(json.dumps(dict(projection_only=True,note='Upper stair projections may overlap low equipment; Unity 3D route and face access tests are authoritative.',items=issues),indent=2))
print('issues',len(issues));print(*issues,sep='\n')
