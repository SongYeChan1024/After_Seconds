"""Scoped wall openings and material-specific roof failure. Song Yechan V0.01."""
from pathlib import Path
import sys,os,math,json,random
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(Path(os.environ['LOCALAPPDATA'])/'Temp/AfterSeconds_20261113/deps'))
sys.path.insert(0,str(H.parent/'F1_RoofLiftWilderness'))
from meshlib import Model
from shapely.geometry import Polygon,LineString,Point,box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
OUT=Path(os.environ['LOCALAPPDATA'])/'Temp/AfterSeconds_WindowRoofDamage_20261113/candidate'
site=json.loads((H.parent/'F1_AbandonedCamouflage/site.json').read_text(encoding='utf8'))
original=json.loads((H.parent/'F1_FullFloor/plan.json').read_text(encoding='utf8'))
rng=random.Random(131103);reports=[];window_stats=[]

def polygons(g):
 if g.geom_type=='Polygon':return [g]
 return [q for q in getattr(g,'geoms',[]) if q.geom_type=='Polygon']

def wall(m,q):
 start=len(m.v);a,b=q['a'],q['b'];length=math.dist(a,b);h={'C01':9,'C02':7.3}.get(q['room'],q['h']);th=q['th']
 has=q['window'] or (q['room'].startswith('T') and length>5)
 old=0;area=0;count=0
 if has and length>2.8:
  old=(length-1.1)*(h-(1.65 if h>6 else 1.15)-.65)
  if h>6:sill=2.8 if h>8 else 2.4;wh=3.15 if h>8 else 2.75;spacing=4;ww=3.1
  elif q['room'].startswith('C'):sill=1.25;wh=1.65;spacing=3.5;ww=2.3
  elif q['room'].startswith('T'):sill=1.65;wh=1.1;spacing=3.4;ww=2
  else:sill=1.9;wh=1.4;spacing=3.4;ww=2.1
  count=max(1,round(length/spacing));cell=length/count;ww=min(ww,cell-.85)
  m.box((0,sill/2,0),(length,sill,th),'Plaster');m.box((0,(h+sill+wh)/2,0),(length,h-sill-wh,th),'Plaster')
  ends=[-length/2]
  windows=[]
  for i in range(count):
   cx=-length/2+(i+.5)*cell;windows.append((cx-ww/2,cx+ww/2))
  left=-length/2
  for l,r in windows:
   m.box(((left+l)/2,sill+wh/2,0),(l-left,wh,th),'Plaster');left=r
   m.box(((l+r)/2,sill-.045,0),(ww+.22,.09,th+.22),'Concrete')
   # A recessed metal frame, with a small number of meaningful glazing divisions.
   for x in [l,l+ww/2,r]:m.box((x,sill+wh/2,0),(.048,wh,.075),'Corrosion')
   for y in [sill,sill+wh/2,sill+wh]:m.box(((l+r)/2,y,0),(ww,.045,.075),'Corrosion')
   for col in range(2):
    for row in range(2):
     x=l+col*ww/2+.03;y=sill+row*wh/2+.03;w=ww/2-.06;hh=wh/2-.06;v=rng.random()
     if v<.42:m.box((x+w/2,y+hh/2,0),(w,hh,.008),'Glass')
     elif v<.78:
      pts=[(x,y,0),(x+w*.86,y,0),(x+w*.7,y+hh*.16,0),(x+w*.51,y+hh*.11,0),(x+w*.18,y+hh*.7,0),(x,y+hh*.82,0)]
      m.add(pts,[tuple(range(len(pts)))],'Glass')
   area+=ww*wh
  m.box(((left+length/2)/2,sill+wh/2,0),(length/2-left,wh,th),'Plaster')
 else:m.box((0,h/2,0),(length,h,th),'Plaster')
 for side in [-1,1]:
  for i in range(max(1,int(length/3))):
   xx=-length/2+(i+.5)*length/max(1,int(length/3));hh=rng.uniform(.08,.2)
   m.box((xx,hh/2,side*(th/2+.04)),(rng.uniform(.55,1.4),hh,.08),'Concrete')
 dx,dz=(b[0]-a[0])/length,(b[1]-a[1])/length;cx,cz=(a[0]+b[0])/2,(a[1]+b[1])/2
 for i in range(start,len(m.v)):
  x,y,z=m.v[i];m.v[i]=(cx+x*dx-z*dz,y,cz+x*dz+z*dx)
 window_stats.append(dict(name=q['name'],room=q['room'],wallArea=length*h,beforeOpeningArea=old,afterOpeningArea=area,windows=count))

for room in site['rooms']+site['tunnels']:
 m=Model('AE_'+room['id']+'_Walls')
 for q in site['walls']:
  if q['room']==room['id']:wall(m,q)
 if 'doors' in room:
  x,z,w,d=[room[k] for k in ['x','z','w','d']];h={'C01':9,'C02':7.3}.get(room['id'],room['h'])
  for door in room['doors']:
   dx,_,dz=door['point'];vertical=abs(abs(dx-x)-w/2)<.05
   if h>3.4:m.box((dx,(h+3.4)/2,dz),(.24,h-3.4,4.6) if vertical else (4.6,h-3.4,.24),'Plaster')
 reports.append(m.export(OUT))

def irregular(cx,cz,rx,rz,n=48):
 # Several scales of fracture; unlike a uniformly toothed circular cut.
 phase=rng.uniform(0,6);pts=[]
 for i in range(n):
  t=i*math.tau/n;k=1+.13*math.sin(t*3+phase)+.09*math.sin(t*7+phase)+rng.uniform(-.05,.05)
  pts.append((cx+rx*k*math.cos(t),cz+rz*k*math.sin(t)))
 return Polygon(pts).buffer(0)

def profile(z):
 t=(z/.24)%1
 return .045*max(0,min(1,(t-.16)/.16,(.84-t)/.16))

def corrugated(m,surface,height):
 # Real folded cross-section, including a thin underside; ridges run down the slope.
 minx,minz,maxx,maxz=surface.bounds
 breaks=sorted(set([minz,maxz]+[i*.24+t*.24 for i in range(math.floor(minz/.24)-1,math.ceil(maxz/.24)+1) for t in [0,.16,.32,.68,.84,1] if minz<i*.24+t*.24<maxz]))
 for a,b in zip(breaks,breaks[1:]):
  section=surface.intersection(box(minx-1,a,maxx+1,b))
  for poly in polygons(section):
   if poly.area<.0001:continue
   for tri in constrained_delaunay_triangles(poly).geoms:
    pts=[(x,height(x,z)+profile(z),z) for x,z in list(tri.exterior.coords)[:3]]
    m.add(pts+[(x,y-.006,z) for x,y,z in pts],[(0,1,2),(5,4,3)],'Corrosion')
 # Thin oxidised torn cross section; not a thick concrete-like rim.
 for p in polygons(surface):
  for ring in [p.exterior,*p.interiors]:
   pts=list(ring.coords)
   for a,b in zip(pts,pts[1:]):
    m.add([(a[0],height(*a)+profile(a[1]),a[1]),(b[0],height(*b)+profile(b[1]),b[1]),(b[0],height(*b)+profile(b[1])-.006,b[1]),(a[0],height(*a)+profile(a[1])-.006,a[1])],[(0,1,2,3)],'RoofEdgeRust')

def folded_remnants(m,holes,height,low=False):
 total=0
 for p in polygons(holes):
  coords=list(p.exterior.coords);step=max(3,int(len(coords)/8))
  for i in range(1,len(coords)-2,step):
   ax,az=coords[i];bx,bz=coords[i+2];dx,dz=p.centroid.x-(ax+bx)/2,p.centroid.y-(az+bz)/2;ln=math.hypot(dx,dz);dx/=ln;dz/=ln
   edge=math.dist((ax,az),(bx,bz));width=min(edge,.9 if low else 1.35)
   if width<.22:continue
   cx,cz=(ax+bx)/2,(az+bz)/2;tx,tz=(bx-ax)/edge,(bz-az)/edge
   reach=rng.uniform(.38,.85) if low else rng.uniform(.7,1.65);lift=rng.uniform(.25,.62) if low else rng.uniform(.55,1.3)
   if total%3==1:lift*=-.75
   nu,nv=10,12;vs=[]
   ends=[rng.uniform(.75,1.0) for k in range(nu+1)]
   for j in range(nv+1):
    t=j/nv
    for k in range(nu+1):
     u=(k/nu-.5)*width;v=t*reach*ends[k]
     # A supported root, crease and a rolled free edge; plate remains attached.
     horizontal=v*(1-.32*t*t);xx=cx+tx*u+dx*(horizontal-.18);zz=cz+tz*u+dz*(horizontal-.18)
     yy=height(xx,zz)+profile(zz)+lift*(.18*t+1.15*t*t-.33*t*t*t)+.035*math.sin(t*math.pi)*math.sin(k*1.7)
     vs.append((xx,yy,zz))
   fs=[]
   for j in range(nv):
    for k in range(nu):
     a=j*(nu+1)+k;fs.append((a,a+1,a+nu+2,a+nu+1))
   n=len(vs);boundary=list(range(nu+1))+[j*(nu+1)+nu for j in range(1,nv+1)]+[nv*(nu+1)+k for k in range(nu-1,-1,-1)]+[j*(nu+1) for j in range(nv-1,0,-1)]
   sides=[(a,b,b+n,a+n) for a,b in zip(boundary,boundary[1:]+boundary[:1])]
   m.add(vs+[(x,y-.006,z) for x,y,z in vs],fs+[tuple(n+i for i in reversed(f)) for f in fs]+sides,'Corrosion')
   # Creased raw edge and occasional narrow tear, scaled in centimetres.
   edgepts=vs[-nu-1:];m.tube(edgepts,.004,'RoofRawSteel',4)
   total+=1
 return total

def metal(m,outer,holes,height,low=False,ridge=None):
 surface=outer.difference(holes)
 if ridge is not None:
  minx,minz,maxx,maxz=outer.bounds
  for side in [box(minx-1,minz-1,ridge,maxz+1),box(ridge,minz-1,maxx+1,maxz+1)]:corrugated(m,surface.intersection(side),height)
 else:corrugated(m,surface,height)
 minx,minz,maxx,maxz=outer.bounds
 # Narrow overlapping sheet seams repeat at panel width, distinct from corrugation.
 for iz in range(1,math.ceil((maxz-minz)/1.2)):
  zz=minz+iz*1.2;line=LineString([(minx,zz),(maxx,zz)]).intersection(surface)
  for l in ([line] if line.geom_type=='LineString' else getattr(line,'geoms',[])):
   if l.geom_type!='LineString' or l.length<.08:continue
   coords=list(l.coords)
   if ridge is not None and coords[0][0]<ridge<coords[-1][0]:coords.insert(1,(ridge,zz))
   m.tube([(xx,height(xx,z)+profile(z)+.008,z) for xx,z in coords],.009,'RoofRawSteel',5)
 # Purlin channels continue under torn sheets; each exposed support carries bolt heads.
 for ix in range(math.ceil((maxx-minx)/2.7)+1):
  xx=minx+ix*2.7;line=LineString([(xx,minz),(xx,maxz)]).intersection(outer)
  for l in ([line] if line.geom_type=='LineString' else getattr(line,'geoms',[])):
   if l.geom_type!='LineString' or l.length<.05:continue
   a,b=l.coords[0],l.coords[-1];y=height(xx,(a[1]+b[1])/2)-.085
   m.box((xx,y,(a[1]+b[1])/2),(.055,.13,l.length),'Corrosion')
   for yy in [y-.065,y+.065]:m.box((xx+.035,yy,(a[1]+b[1])/2),(.12,.014,l.length),'Corrosion')
   z=a[1]+.24
   while z<b[1]:
    if surface.contains(Point(xx,z)):m.beam((xx,height(xx,z)+profile(z),z),(xx,height(xx,z)+profile(z)+.012,z),.014,'RoofRawSteel',6)
    z+=.72
 return folded_remnants(m,holes,height,low)

def pebble(m,p,r,mat):
 x,y,z=p;v=[(x+r,y,z),(x-r,y,z),(x,y+r*.6,z),(x,y-r*.6,z),(x,y,z+r*.8),(x,y,z-r*.8)]
 m.add(v,[(0,2,4),(4,2,1),(1,2,5),(5,2,0),(0,4,3),(4,1,3),(1,5,3),(5,0,3)],mat)

def concrete(m,outer,holes,height):
 # Independent concentric fracture rings: sound face, shallow spall, coarse core, underside.
 top_holes=[];bottom_holes=[];ringdata=[]
 for p in polygons(holes):
  coarse=list(p.exterior.coords);q=[]
  for a,b in zip(coarse,coarse[1:]):
   for j in range(3):q.append((a[0]+(b[0]-a[0])*j/3,a[1]+(b[1]-a[1])*j/3))
  cx,cz=p.centroid.coords[0];rings=[[],[],[],[]]
  for x,z in q:
   dx,dz=x-cx,z-cz;ln=math.hypot(dx,dz);dx/=ln;dz/=ln
   spread=rng.uniform(.12,.32)
   rings[0].append((x+dx*spread,height,z+dz*spread))
   rings[1].append((x+dx*rng.uniform(.05,.18),height-rng.uniform(.025,.075),z+dz*rng.uniform(.05,.18)))
   rings[2].append((x+dx*rng.uniform(-.08,.06),height-rng.uniform(.10,.15),z+dz*rng.uniform(-.08,.06)))
   rings[3].append((x+dx*rng.uniform(.1,.32),height-.22,z+dz*rng.uniform(.1,.32)))
  top_holes.append(Polygon([(x,z) for x,y,z in rings[0]]));bottom_holes.append(Polygon([(x,z) for x,y,z in rings[3]]));ringdata.append(rings)
 for holes2,y in [(top_holes,height),(bottom_holes,height-.22)]:
  surface=outer.difference(unary_union(holes2))
  for poly in polygons(surface):
   for tri in constrained_delaunay_triangles(poly).geoms:
    m.add([(x,y,z) for x,z in list(tri.exterior.coords)[:3]],[(0,1,2)],'Concrete')
 coords=list(outer.exterior.coords)
 for a,b in zip(coords,coords[1:]):m.add([(a[0],height,a[1]),(b[0],height,b[1]),(b[0],height-.22,b[1]),(a[0],height-.22,a[1])],[(0,1,2,3)],'Concrete')
 for rings in ringdata:
  n=len(rings[0])
  for layer in range(3):
   for i in range(n):
    j=(i+1)%n;pts=[rings[layer][i],rings[layer][j],rings[layer+1][j],rings[layer+1][i]]
    m.add(pts,[(0,1,2),(0,2,3)],'RoofFracture' if layer!=0 or i%4==0 else 'Concrete')
    if layer==1:
     for k in range(3):
      t=rng.random();v=.25+k*.25;p=tuple((pts[0][a]*(1-t)+pts[1][a]*t)*(1-v)+(pts[3][a]*(1-t)+pts[2][a]*t)*v for a in range(3))
      cx=sum(p[0] for p in rings[0])/n;cz=sum(p[2] for p in rings[0])/n;dx,dz=cx-p[0],cz-p[2];ln=math.hypot(dx,dz)
      pebble(m,(p[0]+dx/ln*.025,p[1],p[2]+dz/ln*.025),rng.uniform(.018,.037),'RoofAggregate')
  # Short branching cracks extend into the sound face, following local fracture directions.
  for i in range(0,n,18):
   x,y,z=rings[0][i];cx=sum(p[0] for p in rings[0])/n;cz=sum(p[2] for p in rings[0])/n;dx,dz=x-cx,z-cz;ln=math.hypot(dx,dz);dx/=ln;dz/=ln
   pts=[(x,y+.002,z),(x+dx*.2-dz*.08,y+.002,z+dz*.2+dx*.08),(x+dx*.5,y+.002,z+dz*.5),(x+dx*.75-dz*.06,y+.002,z+dz*.75+dx*.06)]
   m.tube(pts,.005,'Dark',4)
   m.tube([(xx,yy-.224,zz) for xx,yy,zz in pts],.004,'Dark',4)
 # Rebar follows a reinforcement grid, anchored within solid concrete at each end.
 for p in polygons(holes):
  minx,minz,maxx,maxz=p.bounds
  for axis in [0,1]:
   lo,hi=(minx,maxx) if axis==0 else (minz,maxz)
   for k in range(math.ceil((hi-lo)/.42)):
    c=lo+k*.42
    line=LineString([(c,minz-1),(c,maxz+1)]) if axis==0 else LineString([(minx-1,c),(maxx+1,c)])
    clipped=line.intersection(p)
    for l in ([clipped] if clipped.geom_type=='LineString' else getattr(clipped,'geoms',[])):
     if l.geom_type!='LineString' or l.length<.25:continue
     a,b=l.coords[0],l.coords[-1];dx,dz=(b[0]-a[0])/l.length,(b[1]-a[1])/l.length
     for side,(xx,zz),sign in [(0,a,1),(1,b,-1)]:
      reach=min(l.length*.43,rng.uniform(.45,1.25));dip=rng.uniform(.06,.26)
      pts=[(xx-dx*.22*sign,height-.12,zz-dz*.22*sign),(xx+dx*reach*.55*sign,height-.12,zz+dz*reach*.55*sign),(xx+dx*reach*sign,height-.12-dip,zz+dz*reach*sign)]
      m.tube(pts,.012,'RoofEdgeRust',8)
      for t in range(1,int(reach/.10)):
       u=t*.10;px,pz=xx+dx*u*sign,zz+dz*u*sign;py=height-.12-max(0,(u/reach-.55)/.45)*dip
       m.beam((px-dx*.0025,py,pz-dz*.0025),(px+dx*.0025,py,pz+dz*.0025),.014,'RoofEdgeRust',8)

for room in site['rooms']:
 key=room['id']
 if not key.startswith('C'):continue
 x,z,w,d=[room[k] for k in ['x','z','w','d']];outer=box(x-w/2,z-d/2,x+w/2,z+d/2);m=Model('AE_'+key+'_Roof')
 if key in ['C01','C02']:
  h,rise=(9,2.35) if key=='C01' else (7.3,1.8)
  height=lambda xx,zz:h+rise*(1-abs(xx-x)/(w/2))+.13
  specs=[(x+w*.28,z-d*.23,w*.23,d*.26),(x-.5,z+d*.22,w*.085,d*.16),(x-w*.27,z-d*.04,w*.09,d*.11),(x+w*.17,z+d*.40,w*.12,d*.12)]
  holes=unary_union([irregular(*q,32) for q in specs]).intersection(outer);folds=metal(m,outer,holes,height,ridge=x)
  for zz in [z-d/2,z+d/2]:m.add([(x-w/2,h,zz),(x+w/2,h,zz),(x,h+rise,zz)],[(0,1,2)],'Plaster')
 else:
  holes=unary_union([irregular(x-w*.32,z+d*.11,w*.16,d*.17),irregular(x+w*.12,z-d*.12,w*.155,d*.15)]).intersection(outer)
  concrete(m,outer,holes,room['h']+.18);folds=0
  for xx in [x-w/2,x+w/2]:m.box((xx,room['h']+.28,z),(.14,.25,d),'Concrete')
 report=m.export(OUT);report.update(openingArea=holes.area,roofArea=outer.area,foldedSheets=folds);reports.append(report)

for tunnel in site['tunnels']:
 m=Model('AE_'+tunnel['id']+'_Roof');opening=0;area=0;folds=0
 for q in original['corridorRoofs']:
  if q['room']!=tunnel['id']:continue
  outer=Polygon(q['points']);cx,cz=outer.centroid.coords[0]
  # Irregular longitudinal loss, with attached metal and visible support instead of a clean slot.
  points=[];coords=list(outer.exterior.coords)
  for a,b in zip(coords,coords[1:]):
   n=max(2,round(math.dist(a,b)/.8))
   for i in range(n):
    t=i/n;xx=a[0]+(b[0]-a[0])*t;zz=a[1]+(b[1]-a[1])*t;k=rng.uniform(.42,.59);points.append((cx+(xx-cx)*k,cz+(zz-cz)*k))
  holes=Polygon(points).buffer(0).intersection(outer.buffer(-.2));folds+=metal(m,outer,holes,lambda x,z:3.56,True);area+=outer.area;opening+=holes.area
 report=m.export(OUT);report.update(openingArea=opening,roofArea=area,foldedSheets=folds);reports.append(report)

(H/'models.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
stats=dict(walls=window_stats,totalWallArea=sum(q['wallArea'] for q in window_stats),beforeOpeningArea=sum(q['beforeOpeningArea'] for q in window_stats),afterOpeningArea=sum(q['afterOpeningArea'] for q in window_stats))
(H/'windows.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
print('MODELS',len(reports),'TRIANGLES',sum(q['triangles'] for q in reports),'WINDOWS',stats['beforeOpeningArea'],stats['afterOpeningArea'],flush=True)
