import json,math
import numpy as np
from pathlib import Path
from shapely.geometry import Point,LineString
from shapely.ops import unary_union
H=Path(__file__).resolve().parent;d=json.loads((H/'plan.json').read_text(encoding='utf8'));rs={r['id']:r for r in d['rooms']}
adjust={'B2-T01':{'VL':110},'B2-T07':{'C03':-20,'VL':180},'B2-T19':{'VL':250},'B2-T08':{'VB':200},'B2-T20':{'VB':130}}
for t in d['tunnels']:
 if t['id'] not in adjust:continue
 a,b=rs[t['a']],rs[t['b']];angles=[];pts=[]
 for r,o in [(a,b),(b,a)]:
  angle=adjust[t['id']].get(r['id'],math.degrees(math.atan2(o['v']-r['v'],o['x']-r['x'])));v=np.array([math.cos(math.radians(angle)),math.sin(math.radians(angle))]);angles.append(v);pts.append(np.array([r['x'],r['v']])+v*(r['r']-.8))
 p,q=pts;u,v=angles;control=min(9,float(np.linalg.norm(q-p))*.32);c1=p+u*control;c2=q+v*control;n=max(24,math.ceil(np.linalg.norm(q-p)/.6));path=[]
 for i in range(n+1):
  x=i/n;pt=(1-x)**3*p+3*(1-x)**2*x*c1+3*(1-x)*x*x*c2+x**3*q;path.append(pt.tolist())
 t.update(path=path,p=path[0],q=path[-1],length=sum(math.dist(x,y) for x,y in zip(path,path[1:])),routing='Curved entry clearance')
for r in d['rooms']:
 r['doors']=[]
 for t in d['tunnels']:
  if r['id'] not in [t['a'],t['b']]:continue
  p=t['p'] if t['a']==r['id'] else t['q'];r['doors'].append(dict(id=t['id'],x=p[0]-r['x'],z=r['v']-p[1],angle=math.degrees(math.atan2(r['v']-p[1],p[0]-r['x']))))
union=unary_union([Point(r['x'],r['v']).buffer(r['r']+.25) for r in d['rooms']]);bad=[]
for i,t in enumerate(d['tunnels']):
 for u in d['tunnels'][i+1:]:
  over=LineString(t['path']).buffer(2.72).intersection(LineString(u['path']).buffer(2.72)).difference(union)
  if over.area>.025:bad.append({'a':t['id'],'b':u['id'],'area':over.area})
d['tunnelClearance']={'outerBuffer':2.72,'conflicts':bad,'revised':list(adjust)}
(H/'plan.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8');print('Remaining overlaps',bad)
assert not bad
from PIL import Image,ImageDraw,ImageFont
im=Image.new('RGB',(1600,1200),'#121b22');pen=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/consolab.ttf',20);small=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',15)
def xy(x,v):return 800+x*5.3,590+v*5.3
for t in d['tunnels']:
 pen.line([xy(*p) for p in t['path']],fill='#b57863' if t['id'] in adjust else '#647d87',width=28)
for r in d['rooms']:
 x,y=xy(r['x'],r['v']);rr=r['r']*5.3;pen.ellipse((x-rr,y-rr,x+rr,y+rr),fill='#33444e',outline='#9bb7c0',width=2);pen.text((x,y),r['id'],font=font,fill='white',anchor='mm')
for t in d['tunnels']:
 ps=t['path'];p=ps[len(ps)//2] if len(ps)>2 else [(ps[0][0]+ps[-1][0])/2,(ps[0][1]+ps[-1][1])/2];pen.text(xy(*p),t['id'].split('-')[1],font=small,fill='#f6e2ce',anchor='mm')
pen.text((55,40),'B2 MACHINERY / 12 CAVERNS + 3 CORES + 21 PIPE TUNNELS',font=font,fill='white');pen.text((55,1110),'COPPER: CURVED ENTRY CLEARANCE / INNER DIAMETER 5.0 m / CROWN 3.85 m',font=font,fill='#cfa48b');im.save(H/'connection_plan.png')
