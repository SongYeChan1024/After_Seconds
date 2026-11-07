"""Direct destination legs plus preserved C01/C02/VA routes. Author 송예찬."""
import json,math,heapq
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;R=H.parents[1];plan=json.loads((H/'plan.json').read_text(encoding='utf-8'));grids=json.loads((H/'grids.json').read_text(encoding='utf-8'));old=json.loads((R/'SourceAssets/T02_StairA/plan.json').read_text(encoding='utf-8'));routes=list(old['routes']);labels=[]
# Arrival green reaches the stair foot; departure colours begin in the portal lobby.
# This leaves space for the newly connected W01 and N01 arrival branches.
for r in routes:
 if r['id'] in ['C01_FromVA','C02_FromVA']:
  idx=next(i for i,p in enumerate(r['points']) if math.hypot(p[0]+44,p[1]-28)>4.05)
  r['points']=r['points'][idx:]
palette={'C01':('실험동','#39C8E3'),'C02':('보안관제동','#4F8CFF'),'C03':('냉각설비동','#E9AD49'),'C04':('유틸리티동','#C27FFF'),'VA':('계단 A','#70D692'),'VB':('계단 B','#A5D656'),'VL':('화물승강기','#E4D090'),'W01':('제1격리생활동','#E9A28B'),'W02':('제2격리생활동','#B5B8ED'),'W03':('의료검사동','#F18CA9'),'E01':('물자보급동','#B8C977'),'E02':('급식지원동','#F0CE5A'),'E03':('제염동','#D492CE'),'N01':('중앙관제동','#8BAECC'),'S01':('폐쇄시험동','#CE8C62')}
def dense(ps,step=.09):
 out=[]
 for a,b in zip(ps,ps[1:]):
  a,b=np.array(a),np.array(b);n=max(1,math.ceil(np.linalg.norm(b-a)/step));out.extend((a+(b-a)*i/n).tolist() for i in range(n))
 return out+[list(ps[-1])]
reserved={c:{} for c in grids}
def reserve(route):
 for room,g in grids.items():
  pts=[p for p in route['points'] if abs(p[0]-g['cx'])<(g['half']+3)*g['step'] and abs(p[1]-g['cz'])<(g['half']+3)*g['step']]
  for x,z in pts:
   ix=round((x-g['cx'])/g['step'])+g['half'];iz=round((z-g['cz'])/g['step'])+g['half']
   for dx in range(-3,4):
    for dz in range(-3,4):
     xx,zz=ix+dx,iz+dz
     if not(0<=xx<g['size'] and 0<=zz<g['size']):continue
     if math.hypot(g['cx']+(xx-g['half'])*g['step']-x,g['cz']+(zz-g['half'])*g['step']-z)<.28:reserved[room].setdefault((xx,zz),set()).add(route['code'])
for r in routes:reserve(r)
def path(room,start,end,code,departure=False):
 g=grids[room];n=g['size'];step=g['step']
 def world(p):return[g['cx']+(p[0]-g['half'])*step,g['cz']+(p[1]-g['half'])*step]
 def ok(p):return 0<=p[0]<n and 0<=p[1]<n and g['flags'][p[1]*n+p[0]]=='1' and not(reserved[room].get(p,set())-{code})
 def nearest(pt):
  p=(round((pt[0]-g['cx'])/step)+g['half'],round((pt[1]-g['cz'])/step)+g['half']);cand=[(math.dist(world((p[0]+dx,p[1]+dz)),pt),(p[0]+dx,p[1]+dz)) for dx in range(-11,12) for dz in range(-11,12) if ok((p[0]+dx,p[1]+dz))]
  if not cand:raise RuntimeError(('No endpoint',room,code,pt))
  return min(cand)[1]
 a,b=nearest(start),nearest(end);todo=[(0,a)];cost={a:0};prev={};found=False
 while todo:
  _,p=heapq.heappop(todo)
  if p==b:found=True;break
  for dx,dz in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
   q=(p[0]+dx,p[1]+dz)
   if not ok(q) or (dx and dz and (not ok((p[0]+dx,p[1])) or not ok((p[0],p[1]+dz)))):continue
   val=cost[p]+math.hypot(dx,dz)
   if val<cost.get(q,1e9):cost[q]=val;prev[q]=p;heapq.heappush(todo,(val+math.dist(q,b),q))
 if not found and departure:
  # A departure stencil may start in the same clear lobby component as its portal.
  # It never bridges across a differently coloured arrival line.
  reachable={b};todo2=[b]
  while todo2:
   pp=todo2.pop()
   for dx,dz in [(1,0),(-1,0),(0,1),(0,-1)]:
    qq=(pp[0]+dx,pp[1]+dz)
    if ok(qq) and qq not in reachable:reachable.add(qq);todo2.append(qq)
  best=min(reachable,key=lambda p:math.dist(world(p),start))
  return path(room,world(best),end,code)
 if not found:raise RuntimeError(('No route',room,code,a,b))
 ps=[b]
 while ps[-1]!=a:ps.append(prev[ps[-1]])
 ps=ps[::-1]
 # Preserve generous clear-cell margins while removing grid zigzags.
 simple=[ps[0]];i=0
 while i<len(ps)-1:
  k=i+1
  for j in range(i+2,len(ps)):
   seg=dense([world(ps[i]),world(ps[j])],step*.30)
   if all(ok((round((q[0]-g['cx'])/step)+g['half'],round((q[1]-g['cz'])/step)+g['half'])) for q in seg):k=j
   else:break
  simple.append(ps[k]);i=k
 return[world(p) for p in simple]
for t in plan['tunnels'][2:]:
 p=np.array([t['p'][0],-t['p'][1]]);q=np.array([t['q'][0],-t['q'][1]]);f=(q-p)/np.linalg.norm(q-p);right=np.array([f[1],-f[0]])
 for direction in ([-1,1] if t['a'].startswith('V') else [1,-1]):
  a,b=(t['a'],t['b']) if direction==1 else (t['b'],t['a']);s,e=(p,q) if direction==1 else(q,p);forward=f*direction;side=right*direction;start=s-forward*3.3+side*.26;end=e+forward*3.3+side*.26
  if b in ['VA','VB']:end=np.array(plan['rooms'][b]['position'])[np.array([0,2])]+np.array([-.96,-2.55])
  if a in ['VA','VB']:start=s-forward*1.65+side*.26
  if b=='VL':end=np.array([44,25.35])
  if a=='VL':start=s-forward*1.65+side*.26
  first=path(a,start,s-forward*.55+side*.26,b,True);last=path(b,e+forward*.55+side*.26,end,b)
  points=dense(first+[list(s+side*.26),list(e+side*.26)]+last);route=dict(id=t['id']+'_'+a+'_to_'+b,code=b,width=.10,points=points,departure=a,arrival=b);routes.append(route);reserve(route)
  for dist in [2.8,float(np.linalg.norm(e-s))-2.8]:labels.append(dict(id=t['id']+'_'+b+'_'+str(round(dist,1)),code=b,position=list(s+forward*dist+side*1.12),forward=list(forward),width=.62,length=1.5))
out=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/B5/Textures';out.mkdir(exist_ok=True)
for code,(name,col) in palette.items():
 im=Image.new('RGBA',(768,1792));d=ImageDraw.Draw(im);ink=col+'FF';d.polygon([(384,90),(555,300),(450,300),(450,470),(318,470),(318,300),(213,300)],fill=ink)
 for text,y,size in [('SECTOR '+code[0] if not code.startswith('V') else 'VERTICAL',550,60),(code,740,236),(name,1130,90),('B5 / DESTINATION',1510,51)]:
  font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',size);bb=d.textbbox((0,0),text,font=font);d.text(((768-bb[2]+bb[0])/2-bb[0],y-bb[1]),text,font=font,fill=ink)
 im.save(out/f'RD_Floor_{code}.png')
legends=[]
for code,(name,col) in palette.items():
 g=grids[code];adj=[t['b'] if t['a']==code else t['a'] for t in plan['tunnels'] if code in (t['a'],t['b'])]
 if code=='C01':adj.append('VA')
 if code=='VA':adj.append('C01')
 w,h=1.5,1.15
 if code in ['VB','VL']:w,h=1.0,.80
 if code in ['C01','C02','VA']:
  saved=old[{'C01':'labLegend','C02':'legend','VA':'coreLegend'}[code]];pos=saved['position'];w,h=saved['width'],saved['length'];forward=saved.get('forward',[0,1])
 else:
  candidates=[]
  for iz in range(8,g['size']-8):
   for ix in range(8,g['size']-8):
    valid=True
    hz=math.ceil((h/2+.06)/g['step']);hx=math.ceil((w/2+.06)/g['step'])
    for dz in range(-hz,hz+1):
     for dx in range(-hx,hx+1):
      pt=(ix+dx,iz+dz)
      if g['flags'][pt[1]*g['size']+pt[0]]!='1' or reserved[code].get(pt):valid=False;break
     if not valid:break
    if valid:
     x,z=g['cx']+(ix-g['half'])*g['step'],g['cz']+(iz-g['half'])*g['step'];candidates.append((math.hypot(x-g['cx'],z-g['cz']+1.8),[x,z]))
  if not candidates:raise RuntimeError(('Legend space',code))
  pos=min(candidates)[1];forward=[0,1]
 legends.append(dict(code=code,position=pos,width=w,length=h,forward=forward,adjacent=adj))
 im=Image.new('RGBA',(1400,1000));d=ImageDraw.Draw(im);f=lambda s:ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',s);d.text((35,25),code+'  '+name,font=f(83),fill=col+'FF');d.line((35,155,1360,155),fill=col+'FF',width=7)
 for j,dest in enumerate(adj):
  yy=200+j*150;cc=palette[dest][1]+'FF';d.rectangle((50,yy+15,140,yy+70),fill=cc);d.text((185,yy),dest+'  '+palette[dest][0]+(' / 경유 C02' if (code,dest) in [('C01','VA'),('VA','C01')] else ''),font=f(58),fill=cc)
 d.text((35,915),'B5   /   DESTINATION COLOUR GUIDE',font=f(36),fill=(203,216,216,255));im.save(out/f'RD_Legend_{code}.png')
result=dict(author='송예찬',scope='All 19 corridors. Direct neighbouring destinations; retained C01/C02/VA through routes.',destinations={k:dict(name=v[0],color=v[1],sector=k[0] if not k.startswith('V') else 'CORE',pattern='circle' if k=='C01' else 'double' if k.startswith('V') else 'square') for k,v in palette.items()},routes=routes,labels=labels,legends=legends)
(H/'guidance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print('Guidance',len(routes),'routes',len(labels),'floor destination labels')
