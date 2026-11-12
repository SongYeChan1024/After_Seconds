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
