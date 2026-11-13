"""Supply connections, removed machinery anchors and material-specific roof fall."""
import sys,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mesh import *
rng=random.Random(131114);reports=[];placements=[]
def save(m,kind):
 q=m.export();q['kind']=kind;reports.append(q)
def trench(m,a,b,width=.29):
 a,b=Vector(a),Vector(b);length=(b-a).length;u=(b-a).normalized();n=Vector((-u.z,0,u.x));c=(a+b)/2
 # A flush closed cover, with visible supporting edge and cross slats.
 for side in [-1,1]:m.beam(a+n*width/2,b+n*width/2,.009,'Corrosion',4)
 if abs(u.x)>.9:m.box(c,(length,.014,width),'Dark')
 else:m.box(c,(width,.014,length),'Dark')
 for i in range(int(length/.10)+1):
  p=a+u*(i*length/max(1,int(length/.10)));m.beam(p-n*(width*.45)+Vector((0,.009,0)),p+n*(width*.45)+Vector((0,.009,0)),.008,'Steel',4)
 for i in range(int(length/.9)+1):
  p=a+u*(i*length/max(1,int(length/.9)))
  for side in [-1,1]:m.bolt(p+n*(width*.40)+Vector((0,.014,0)),.007,'y')
m=Model('ES_C01_Utilities');trench(m,(-17.8,.01,3.15),(-1.3,.01,3.15));trench(m,(-1.3,.01,3.15),(-1.3,.01,7))
for socket,end in [((-17.1,.62,1.25),(-17.6,.022,3.15)),((-11.3,.49,1.22),(-11.7,.022,3.15)),((-1.3,.22,6.8),(-1.3,.022,6.5))]:
 x,y,z=socket;ex,ey,ez=end
 m.box((x,y,z),(.15,.16,.13),'Dark');m.bolt((x-.047,y+.043,z+.071),.009);m.bolt((x+.047,y-.043,z+.071),.009)
 pts=[(x,y,z+.06),(x,y-.05,z+.14),(x+.04,max(.04,y*.35),z+.28),(ex,.031,ez-.3),end];m.tube(pts,.022,'Rubber',8)
 m.beam((x,y,z+.058),(x,y,z+.13),.035,'Steel',12)
 for p in [pts[2],pts[-1]]:m.ring(p,.027,.004,'Steel','y',12)
# Press base hold-downs: do not move the existing press.
for x in [-17.35,-14.65]:
 for z in [.96,3.03]:m.box((x,.024,z),(.18,.035,.15),'Steel');m.bolt((x,.045,z),.026,'y')
save(m,'utilities')
m=Model('ES_FloorAnchors')
for cx,cz,rx,rz in [(-18.5,-10,1.02,.66),(31,-9.4,.68,.88)]:
 for sx in [-1,1]:
  for sz in [-1,1]:
   x,z=cx+sx*rx,cz+sz*rz;m.beam((x,.004,z),(x,.025,z),.025,'RoofEdgeRust',8);m.ring((x,.007,z),.04,.006,'Steel','y',12)
   # Exposed aggregate chips at the cut-off bolts.
   for j in range(7):
    a=rng.random()*math.tau;r=rng.uniform(.035,.09);xx,zz=x+math.cos(a)*r,z+math.sin(a)*r;rr=rng.uniform(.007,.021)
    m.bent([(xx-rr,.006,zz-rr),(xx+rr,.009,zz-rr*.4),(xx+rr*.2,.006,zz+rr)],.004,'RoofAggregate')
save(m,'anchors')
def transform(m,start,c,yaw):
 ca,sa=math.cos(yaw),math.sin(yaw)
 for i in range(start,len(m.v)):
  x,y,z=m.v[i];m.v[i]=(c[0]+x*ca-z*sa,y+c[1],c[2]+x*sa+z*ca)
def fallen_sheet(m,c,w,d,yaw):
 start=len(m.v);nx=max(8,int(w/.035));nz=8;vs=[]
 edge=[rng.uniform(-.07,.07) for i in range(nx+1)]
 for j in range(nz+1):
  for i in range(nx+1):
   x=-w/2+w*i/nx;z=-d/2+d*j/nz+edge[i]*(1 if j==0 else -.3 if j==nz else 0)
   fold=max(0,x-w*.15)*.45+max(0,-z-d*.16)*.15;yy=.030+math.sin(x*math.tau/.15)*.020+fold
   vs.append((x,yy,z))
 fs=[(j*(nx+1)+i,j*(nx+1)+i+1,(j+1)*(nx+1)+i+1,(j+1)*(nx+1)+i) for j in range(nz) for i in range(nx)]
 m.add(vs,fs,'Corrosion')
 for j in [0,nz]:m.tube([vs[j*(nx+1)+i] for i in range(nx+1)],.003,'RoofEdgeRust',5)
 for x in [-w*.28,w*.28]:m.bolt((x,.053,-d*.20),.009,'y')
 transform(m,start,c,yaw)
def shard(m,x,z,size,height,material):
 sides=rng.randint(4,6);phase=rng.random()*math.tau;points=[]
 for j in range(sides):
  a=phase+j*math.tau/sides;r=size*rng.uniform(.65,1);points.append((x+math.cos(a)*r,.008+height*rng.uniform(.8,1),z+math.sin(a)*r*.7))
 m.bent(points,max(.005,height),material)
clusters=[('C01',-3.2,-6.25,'metal'),('C01',-19.55,-1.12,'metal'),('C02',29.6,-12.6,'metal'),('C02',18.6,-8.8,'metal'),('C03',-34.48,-24.46,'concrete'),('C03',-28.32,-27.68,'concrete'),('C04',-16.48,26.54,'concrete'),('C04',-10.32,23.32,'concrete')]
for room in ['C01','C02','C03','C04']:
 m=Model('ES_'+room+'_RoofFall')
 for _,cx,cz,kind in [q for q in clusters if q[0]==room]:
  placements.append(dict(room=room,center=[cx,cz],material=kind))
  if kind=='metal':
   fallen_sheet(m,(cx,0,cz),1.05,1.55,rng.uniform(-1,1));fallen_sheet(m,(cx+.65,.01,cz+.36),.50,.73,rng.uniform(-2,2))
   # Short twisted channel from the roof support, next to the metal skin.
   m.tube([(cx-.6,.04,cz+.5),(cx-.15,.06,cz+.78),(cx+.4,.12,cz+.84)],.025,'RoofEdgeRust',6)
  else:
   for i in range(13):shard(m,cx+rng.uniform(-.85,.85),cz+rng.uniform(-.85,.85),rng.uniform(.08,.29),rng.uniform(.025,.12),'FallenConcrete')
   m.tube([(cx-.4,.032,cz),(cx,.06,cz+.2),(cx+.5,.10,cz+.18)],.009,'RoofEdgeRust',8)
  for i in range(75):
   a=rng.random()*math.tau;r=(rng.random()**.65)*1.6;x,z=cx+math.cos(a)*r,cz+math.sin(a)*r
   shard(m,x,z,rng.uniform(.012,.06)*(1-r/2.2),rng.uniform(.004,.018),'RoofAggregate' if kind=='concrete' else rng.choice(['RoofEdgeRust','Dust','Gravel']))
 save(m,'roofFall')
m=Model('ES_RoofSprouts')
for room,cx,cz,kind in clusters:
 for i in range(9):
  angle=rng.random()*math.tau;r=rng.uniform(.55,1.35);x,z=cx+math.cos(angle)*r,cz+math.sin(angle)*r
  for j in range(rng.randint(4,8)):
   a=rng.random()*math.tau;h=rng.uniform(.045,.17);w=rng.uniform(.003,.008);lean=rng.uniform(.04,.13);dx,dz=math.cos(a),math.sin(a)
   vs=[(x-dz*w,.009,z+dx*w),(x+dz*w,.009,z-dx*w),(x+dx*lean*.3+dz*w*.45,h*.65,z+dz*lean*.3-dx*w*.45),(x+dx*lean*.3-dz*w*.45,h*.65,z+dz*lean*.3+dx*w*.45),(x+dx*lean,h,z+dz*lean)]
   m.add(vs,[(0,1,2,3),(3,2,4)],rng.choice(['DeepLeaf','DryLeaf','DryLeaf']))
save(m,'roofFall')
(H/'models.json').write_text(json.dumps(reports,indent=2));(H/'fall_sites.json').write_text(json.dumps(placements,indent=2));print('STORY_MODELS_READY',len(reports),sum(q['triangles'][0] for q in reports))
