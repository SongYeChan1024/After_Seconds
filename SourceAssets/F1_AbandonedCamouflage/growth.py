"""Concentrated encroachment at wall bases and damaged roofs; clear travel axes."""
import sys,random,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
rng=random.Random(1811);manifest.update(json.loads((H/'models_environment.json').read_text()))
# Use only pure mesh helpers, not the earlier generator's execution section.
src=(H/'landscape.py').read_text();exec(src[src.index('def height'):src.index('chunks=collections')])
patches=[(-28,-7,2.2,5),(-28,1,2,4),(-29,18,4,2),(-21,17,3,1.1),(-21,29,1.2,3),(-37,-17,3,1.2),(-39,-31,1.2,3),(-48,-21,4,1.3),(-53,-34,5,1.5),(-63,-21,4,1.3),(-73,-34,6,2),(-81,-23,5,1.6),(-38,34,4,2),(-31,42,3,5),(-10,38,6,2),(5,17,2,3),(19,18,2,3),(34,8,3,3),(36,-9,1.5,6),(53,25,2,5),(52,-29,2,4),(-53,24,2,5),(54,-41,4,2)]
for idx,(x,z,rx,rz) in enumerate(patches):
 reset();v=[];f=[];lv=[];lf=[]
 for j in range(int(rx*rz*13)):
  angle=rng.uniform(0,math.tau);rad=math.sqrt(rng.random());xx=x+math.cos(angle)*rx*rad;zz=z+math.sin(angle)*rz*rad;y=height(xx,zz);h=rng.uniform(.45,1.05)
  for k in range(5):blade(v,f,xx+rng.uniform(-.07,.07),y-.015,zz+rng.uniform(-.07,.07),h*rng.uniform(.6,1),rng.uniform(0,math.tau),.025)
  if j%4==0:
   for k in range(6):leaf(lv,lf,xx+rng.uniform(-.25,.25),y+rng.uniform(.2,.7),zz+rng.uniform(-.25,.25),rng.uniform(.09,.19),rng.uniform(0,math.tau))
 mesh('DenseNettlePatch',v,f,'Leaf');mesh('BroadLeafWeeds',lv,lf,'DeepLeaf');save('Encroachment_%02d'%idx,'Environment',True)

# Young trees rooted outside the factory, with individually readable leaves and open branches.
for group,points in enumerate([[(-56,40,5.5),(-64,36,6.7),(-72,19,5),(-63,-43,4.5)],[(-25,60,6.1),(0,57,5.6),(21,48,6.7),(36,59,5.4)],[(58,9,6.7),(69,0,5.5),(59,-34,6.3),(45,-50,5.4)]]):
 reset();v=[];f=[]
 for x,z,h in points:
  y=height(x,z);beam('ColonisingBirch',(x,y,z),(x+.3,y+h,z-.2),.18,'Bark',False)
  for j in range(9):
   a=j*2.399;yy=y+h*(.35+j*.065);cx=x+math.cos(a)*h*.25;cz=z+math.sin(a)*h*.25;cy=yy+h*.15
   beam('TreeBranch',(x+.15,yy,z),(cx,cy,cz),.055,'Bark',False)
   for k in range(100):
    xx=cx+rng.uniform(-.9,.9);zz=cz+rng.uniform(-.9,.9);yh=cy+rng.uniform(-.6,.6);leaf(v,f,xx,yh,zz,rng.uniform(.10,.18),rng.uniform(0,math.tau))
 mesh('Leaves',v,f,'Leaf');save('ColonisingTrees_%d'%group,'Environment',True)

# Local patches below missing roof sheets, with leaf litter and fallen roof fragments.
for id,x,z,rx,rz in [('C01',-.3,-9.0,.75,2.1),('C02',15.2,.4,.65,.9),('C04',-17.6,30.5,.65,.8),('C03',-24.2,-20.3,.65,.55)]:
 reset();v=[];f=[];lv=[];lf=[]
 for j in range(90):
  xx=x+rng.uniform(-rx,rx);zz=z+rng.uniform(-rz,rz)
  for k in range(4):blade(v,f,xx,.02,zz,rng.uniform(.15,.55),rng.uniform(0,math.tau),.018)
  for k in range(3):leaf(lv,lf,xx+rng.uniform(-.5,.5),.018,zz+rng.uniform(-.5,.5),rng.uniform(.04,.12),rng.uniform(0,math.tau))
 mesh('GrowthUnderRoofDamage',v,f,'Leaf');mesh('DeadLeaves',lv,lf,'DryLeaf');save(id+'_IndoorGrowth','Environment',True)

# Debris silhouettes are intentional piles, in addition to scattered small surface spalls.
for id,x,z in [('C01',.1,-10.4),('C02',15.5,.1),('C04',-18,30.3),('C03',-23.8,-20.3)]:
 reset()
 for j in range(12):
  xx=x+rng.uniform(-.6,.6);zz=z+rng.uniform(-.5,.5);o=box('CollapsedPlasterChunk',(xx,rng.uniform(.04,.18),zz),(rng.uniform(.12,.4),rng.uniform(.07,.18),rng.uniform(.12,.4)),'Concrete',0,yaw=rng.uniform(-90,90));o.rotation_euler.x=rng.uniform(-.2,.2)
 for j in range(3):
  xx=x+rng.uniform(-.5,.5);zz=z+rng.uniform(-.4,.4);beam('BrokenTimber',(xx,.05,zz),(xx+rng.uniform(-.9,.9),.07,zz+1.1),.07,'Wood')
 if id=='C01':
  beam('FallenRafter',(-.8,.18,-12.7),(.5,.38,-8.7),.16,'Corrosion');beam('FallenRafterDiagonal',(-.8,.18,-12.7),(.5,1.1,-10.7),.07,'Corrosion');beam('BrokenRoofWeb',(.5,1.1,-10.7),(.5,.38,-8.7),.07,'Corrosion')
 save(id+'_CollapsePile','Environment',True)
print('Encroachment complete',len(manifest),flush=True)
