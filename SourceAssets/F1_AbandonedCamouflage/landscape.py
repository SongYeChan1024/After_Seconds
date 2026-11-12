"""Chunked foliage, terrain-conforming paving, abandonment debris and rusting perimeter."""
import sys,random,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
p=json.loads((H/'site.json').read_text(encoding='utf8'));rng=random.Random(112616)
if (H/'models_environment.json').exists():manifest.update(json.loads((H/'models_environment.json').read_text()))

def height(x,z):
 d=max(abs(x)/80,abs(z)/62);outer=max(0,min(1,(d-.83)/1.2));waves=math.sin(x*.041+z*.016)*2+math.sin(z*.055-x*.02)*1.4+math.cos(x*.073+z*.032)*1.1
 hills=(4.8+waves)*outer**1.5;ground=-.18+math.sin(x*.16)*math.cos(z*.11)*.10+math.sin(x*.31+z*.24)*.025;ditch=-.48*math.exp(-((z+45)/4)**2)*math.exp(-((x+20)/60)**2)
 roadz=-28-.035*(-51-x);rw=math.exp(-((z-roadz)/5.5)**4)*max(0,min(1,(-x-42)/12));road=-.12-max(0,min(1,(-x-60)/140))*.8+math.sin(x*.17)*.045
 return (ground+hills+ditch)*(1-rw)+road*rw

def chunkmesh(name,vs,fs,mat):
 if vs:mesh(name,vs,fs,mat)

def blade(vs,fs,x,y,z,h,angle,width):
 dx,dz=math.cos(angle),math.sin(angle);wx,wz=-dz*width,dx*width;k=len(vs)
 vs.extend([(x-wx,y,z-wz),(x+wx,y,z+wz),(x+dx*h*.12+wx*.6,y+h*.5,z+dz*h*.12+wz*.6),(x+dx*h*.12-wx*.6,y+h*.5,z+dz*h*.12-wz*.6),(x+dx*h*.38,y+h,z+dz*h*.38)])
 fs.extend([(k,k+1,k+2,k+3),(k+3,k+2,k+4)])

def leaf(vs,fs,x,y,z,s,angle):
 k=len(vs);dx,dz=math.cos(angle)*s,math.sin(angle)*s;wx,wz=-dz*.5,dx*.5
 vs.extend([(x-dx,y,z-dz),(x+wx,y+s*.2,z+wz),(x+dx,y+.03,z+dz),(x-wx,y+s*.2,z-wz)]);fs.append((k,k+1,k+2,k+3))

chunks=collections.defaultdict(list)
for item in p['grass']:chunks[(int(item[0]//18),int(item[2]//18))].append(item)
for key,items in sorted(chunks.items()):
 reset();surfaces=[([],[]) for i in range(3)]
 for x,y,z,size,t in items:
  vs,fs=surfaces[t]
  for j in range(11):
   a=rng.uniform(0,math.tau);rad=rng.uniform(0,size*.18);blade(vs,fs,x+math.cos(a)*rad,y-.025,z+math.sin(a)*rad,size*rng.uniform(.5,1.2),a,rng.uniform(.012,.027))
 for (vs,fs),mat in zip(surfaces,['Leaf','DryLeaf','DeepLeaf']):chunkmesh('WeedBlades',vs,fs,mat)
 save('Grass_%s_%s'%key,'Environment',True)

# Shrubs are grouped by broad site quadrant; discrete branching rather than tree-shaped solid blobs.
groups=collections.defaultdict(list)
for item in p['bushes']:groups[(int(item[0]//36),int(item[2]//36))].append(item)
for key,items in sorted(groups.items()):
 reset();vv=[];ff=[]
 for x,y,z,s,t in items:
  for j in range(4):
   angle=rng.uniform(0,math.tau);end=(x+math.cos(angle)*s*.45,y+s*rng.uniform(.8,1.35),z+math.sin(angle)*s*.45)
   beam('DryShrubStem',(x,y,z),end,.018*s,'Bark',False)
   for k in range(20):
    yy=rng.uniform(.3,1.0);xx=x+(end[0]-x)*yy+rng.uniform(-.35,.35)*s;zz=z+(end[2]-z)*yy+rng.uniform(-.35,.35)*s;leaf(vv,ff,xx,y+yy*s,zz,.06*s,rng.uniform(0,math.tau))
 chunkmesh('ShrubLeaves',vv,ff,'Leaf');save('Shrubs_%s_%s'%key,'Environment',True)

# Ivy appears in interrupted vertical patches, never as an opaque green wall.
reset();vv=[];ff=[]
for q in p['walls']:
 if q['room'].startswith('T') or rng.random()<.48:continue
 a,b=q['a'],q['b'];length=math.dist(a,b)
 if length<2:continue
 dx,dz=(b[0]-a[0])/length,(b[1]-a[1])/length
 for side in [-1,1]:
  for vine in range(max(1,int(length/6))):
   tt=rng.uniform(.15,.85);x=a[0]+(b[0]-a[0])*tt-dz*side*(q['th']/2+.08);z=a[1]+(b[1]-a[1])*tt+dx*side*(q['th']/2+.08);h=rng.uniform(1.1,3.7)
   for j in range(int(h/.14)):
    yy=j*.14;xx=x+math.sin(j*.8)*.10;zz=z+math.cos(j*.7)*.08
    for k in [-1,0,1]:
     angle=rng.uniform(0,math.tau);s=rng.uniform(.06,.14);ii=len(vv);cx=xx+dx*k*.15;cz=zz+dz*k*.15
     vv.extend([(cx-dx*s,yy,cz-dz*s),(cx,yy+s*.65,cz),(cx+dx*s,yy,cz+dz*s),(cx,yy-s*.45,cz)]);ff.append((ii,ii+1,ii+2,ii+3))
chunkmesh('ClimbingIvy',vv,ff,'DeepLeaf');save('WallIvy','Environment',True)

def rock(vs,fs,x,y,z,sx,sy,sz):
 k=len(vs);a=rng.uniform(0,math.tau);ca,sa=math.cos(a),math.sin(a)
 for yy in [0,sy]:
  for xx,zz in [(-.5,-.5),(.5,-.5),(.5,.5),(-.5,.5)]:
   xx*=sx*rng.uniform(.8,1.1);zz*=sz*rng.uniform(.8,1.1);vs.append((x+xx*ca+zz*sa,y+yy*rng.uniform(.85,1.15),z-xx*sa+zz*ca))
 fs.extend([tuple(k+i for i in f) for f in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])

for r in p['rooms']:
 reset();con=([],[]);brick=([],[]);leaves=([],[])
 walls=[q for q in p['walls'] if q['room']==r['id']]
 for q in walls:
  a,b=q['a'],q['b'];length=math.dist(a,b)
  if length<2:continue
  for pile in range(max(1,int(length/3.5))):
   t=(pile+.5)/max(1,int(length/3.5));x=a[0]+(b[0]-a[0])*t;z=a[1]+(b[1]-a[1])*t;vx=r['x']-x;vz=r['z']-z;ll=math.hypot(vx,vz);x+=vx/ll*.45;z+=vz/ll*.45
   for j in range(9):
    v,f=con if j%3 else brick;rock(v,f,x+rng.uniform(-.5,.5),.018,z+rng.uniform(-.45,.45),rng.uniform(.07,.28),rng.uniform(.025,.12),rng.uniform(.07,.28))
   for j in range(14):leaf(leaves[0],leaves[1],x+rng.uniform(-.8,.8),.016,z+rng.uniform(-.8,.8),rng.uniform(.025,.07),rng.uniform(0,math.tau))
 for (v,f),mat in [(con,'Concrete'),(brick,'Brick'),(leaves,'DryLeaf')]:chunkmesh('ScatteredSpalls',v,f,mat)
 # A few fallen roof sheets and fragments lie by perimeter, away from doors and central travel.
 if r['id']=='C01':
  box('FallenRoofSheet',(-1.1,.13,-8.5),(1.6,.055,2.4),'Corrosion',0,yaw=-17)
  beam('FallenBrokenBeam',(-24.4,.15,-12.3),(-20.7,.17,-12.6),.14,'Corrosion')
 if r['id']=='C04':
  for i in range(5):box('DisplacedOldFiles',(-17.1+i*.22,.03,30.9+rng.uniform(-.35,.35)),(.22,.04,.30),'Paper',0,yaw=rng.uniform(-60,60))
 save(r['id']+'_Debris','Environment',True)

# Road slabs leave soil/weed cracks. The near road is level enough for controller traversal.
reset()
for x,z,w,d in [(-54,-30.7,3,1.6),(-58,-25.6,2.6,2.0),(-61.5,-30.7,3.7,2.3),(-66,-26.5,2.4,2.6),(-70.2,-30.4,2.8,2.4),(-75,-25.5,2.1,1.9),(-82,-29.5,3.5,2.8),(-89,-27,2.4,2.7),(-48,-32,2.4,2.2),(-53,-24,2.1,2.0),(-41,-34.8,3.6,2.7)]:
 y=height(x,z);box('SunkenApronSlab',(x,y+.014,z),(w,.06,d),'Concrete',0,yaw=rng.uniform(-5,5))
save('BrokenApron','Environment',False)

reset();v=[];f=[]
for x,z,rx,rz in [(-57,-30,2,.8),(-71,-26.8,2.8,.6),(-86,-30,3,1),(-39,-43,3,1.3),(3,12.5,2,.8),(31,8,2,1)]:
 # Fan follows terrain at every vertex; no water sheet clipping through a flat landscape cube.
 k=len(v);v.append((x,height(x,z)+.035,z));n=15
 for i in range(n):
  a=i*math.tau/n;xx=x+math.cos(a)*rx*rng.uniform(.75,1.05);zz=z+math.sin(a)*rz*rng.uniform(.75,1.05);v.append((xx,height(xx,zz)+.035,zz))
 for i in range(n):f.append((k,k+1+(i+1)%n,k+1+i))
mesh('RainPuddles',v,f,'Water');save('RainPuddles','Environment',False)

reset()
def fence(a,b):
 ll=math.dist(a,b);n=max(1,round(ll/3));dx,dz=(b[0]-a[0])/ll,(b[1]-a[1])/ll
 for i in range(n+1):
  x,z=a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n;y=height(x,z);lean=rng.uniform(-.14,.14)
  beam('LeaningFencePost',(x,y,z),(x+lean,y+2.25,z),.06,'Corrosion')
 for i in range(n):
  t=i/n;t1=(i+1)/n;x,z=a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t;xx,zz=a[0]+(b[0]-a[0])*t1,a[1]+(b[1]-a[1])*t1;y=height(x,z);yy=height(xx,zz)
  if rng.random()<.12:continue
  for hh in [.35,1.15,2.08]:beam('FenceWire',(x,y+hh,z),(xx,yy+hh,zz),.015,'Corrosion')
  for j in range(8):
   tt=(j+.3)/8;px,pz=x+(xx-x)*tt,z+(zz-z)*tt;py=y+(yy-y)*tt
   beam('DiamondWire',(px,py+.18,pz),(px+dx*.38,py+1.1,pz+dz*.38),.009,'Corrosion');beam('DiamondWire',(px+dx*.38,py+1.1,pz+dz*.38),(px,py+2.07,pz),.009,'Corrosion')
for a,b in [((-69,-48),(61,-48)),((61,-48),(61,61)),((61,61),(-69,61)),((-69,61),(-69,-23)),((-69,-33),(-69,-48))]:fence(a,b)
# The dilapidated gate leaves the complete road opening unblocked.
for z,sgn in [(-33,-1),(-23,1)]:
 x=-69;y=height(x,z);box('GateMasonryPier',(x,y+1.55,z),(.7,3.1,.7),'Plaster',0)
 end=(-65,y,z+sgn*2.7)
 for hh in [.25,2.3]:beam('OpenRustedGate',(x,y+hh,z),(end[0],end[1]+hh,end[2]),.08,'Corrosion')
 for i in range(1,9):
  t=i/9;xx=x+(end[0]-x)*t;zz=z+(end[2]-z)*t;beam('GateBars',(xx,y+.25,zz),(xx,y+2.3,zz),.035,'Corrosion')
save('PerimeterFence','Environment',False)

reset()
for x,z,h in [(-78,9,6.4),(-56,48,5),(-58,-43,4.5),(42,53,7),(65,-12,5.7),(75,30,5),(-98,-7,6),(14,-57,5.8)]:
 y=height(x,z);beam('DeadTreeTrunk',(x,y,z),(x+.25,y+h,z-.1),.20,'Bark',False)
 for i in range(7):
  a=i*2.39;hh=y+h*(.35+i*.075);end=(x+math.cos(a)*h*.30,hh+h*.22,z+math.sin(a)*h*.30);beam('DeadTreeBranch',(x+.15,hh,z),end,.07,'Bark',False)
  for s in [-1,1]:beam('DeadTwig',end,(end[0]+s*.6,end[1]+.5,end[2]+.3),.025,'Bark',False)
save('DeadTrees','Environment',True)
print('Landscape complete',len(manifest),flush=True)
