"""Replace only western exterior foliage chunks; retain the factory wall ivy."""
import sys,collections,numpy as np
from pathlib import Path
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H))
import models
from models import *
site=json.loads((H.parent/'F1_AbandonedCamouflage/site.json').read_text(encoding='utf8'))
terrain=np.fromfile(Path(os.environ['LOCALAPPDATA'])/'Temp/AfterSeconds_WildernessDetail_20261113/AE_OvergrownFactoryTerrain.raw',dtype='<f4').reshape((513,513))
def ground(x,z):
 u=(x+192)/384*512;v=(z+160)/320*512;i=int(u);j=int(v);a=u-i;b=v-j
 return float((terrain[j,i]*(1-a)*(1-b)+terrain[j,i+1]*a*(1-b)+terrain[j+1,i]*(1-a)*b+terrain[j+1,i+1]*a*b)*28-6)
reports=[];rng=random.Random(1783)
chunks=collections.defaultdict(list)
for item in site['grass']:
 key=(int(item[0]//18),int(item[2]//18))
 if key[0]<=-4:chunks[key].append(item)
for key,items in sorted(chunks.items()):
 m=Model('WD_ApproachGrass_%s_%s'%key)
 for x,_,z,size,t in items:
  y=ground(x,z)-.025
  for j in range(rng.randint(16,25)):
   a=rng.random()*math.tau;r=rng.uniform(.01,.12);xx,zz=x+math.cos(a)*r,z+math.sin(a)*r
   blade(m,rng,(xx,ground(xx,zz)-.025,zz),size*rng.uniform(.42,.9),rng.uniform(.004,.012),a,rng.uniform(.1,.3),rng.choice(['Straw','Faded','Sage']))
  if t!=1:
   for j in range(2):seedstalk(m,rng,(x,y,z),size*rng.uniform(.7,1.05),rng.random()*math.tau)
 q=m.export('Grass');q['target']='AE_Grass_%s_%s'%key;q['plants']=len(items);reports.append(q)
groups=collections.defaultdict(list)
for item in site['bushes']:
 key=(int(item[0]//36),int(item[2]//36))
 if key[0]<=-3:groups[key].append(item)
for key,items in sorted(groups.items()):
 m=Model('WD_ApproachShrubs_%s_%s'%key)
 for x,_,z,size,t in items:
  y=ground(x,z)-.035
  for k in range(6):
   a=rng.random()*math.tau;dx,dz=math.cos(a),math.sin(a);h=size*rng.uniform(.43,.72);end=Vector((x+dx*.42*size,y+h,z+dz*.42*size));base=Vector((x,y,z));mid=base.lerp(end,.55)+Vector((0,h*.13,0));m.beam(base,mid,.014*size,'Twig',6);m.beam(mid,end,.006*size,'Twig',5)
   for j in range(5):
    start=base.lerp(end,.4+j*.11);angle=a+rng.uniform(-1.6,1.6);tip=start+Vector((math.cos(angle)*size*.16,h*.16,math.sin(angle)*size*.16));m.beam(start,tip,.0035*size,'Twig',5)
    for leaf in range(3):
     c=start.lerp(tip,.3+leaf*.3);side=Vector((math.cos(angle+1.2)*.017*size,0,math.sin(angle+1.2)*.017*size));top=c+Vector((dx*.025*size,.035*size,dz*.025*size));m.add([tuple(c-side),tuple(c+side),tuple(top)],[(0,1,2)],rng.choice(['Faded','Sage','Straw']))
 q=m.export('Shrub');q['target']='AE_Shrubs_%s_%s'%key;q['plants']=len(items);reports.append(q)
(H/'approach_models.json').write_text(json.dumps(reports,indent=2),encoding='utf8');print('APPROACH_MODELS_READY',len(reports),sum(q['plants'] for q in reports))
