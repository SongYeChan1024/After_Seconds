"""Sanitary fixture and equipment port connections. Author 송예찬."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build import *
import build
build.manifest.update(json.loads((H/'models.json').read_text(encoding='utf-8')))
reset()
box('WC_Foundation',0,.035,0,.45,.07,.62,'Steel',.025);box('Toilet_Pedestal',0,.19,-.03,.29,.29,.32,'Steel',.048)
vs=[];fs=[];profile=[(.13,.16),(.23,.32),(.24,.40),(.205,.415),(.18,.32),(.08,.24)]
for radius,y in profile:
 for i in range(64):a=i*math.tau/64;vs.append((radius*math.cos(a),y,.08+radius*1.25*math.sin(a)))
for j in range(len(profile)-1):
 for i in range(64):fs.append((j*64+i,j*64+(i+1)%64,(j+1)*64+(i+1)%64,(j+1)*64+i))
fs.append(tuple(range(5*64,6*64)));mesh('Hollow_Stainless_Bowl',vs,fs,'Steel',.002,True)
for ring in [(.218,.431),(.218,.451)]:
 radius,y=ring;tube('Rounded_Seat_Ring',[(radius*math.cos(i*math.tau/64),y,.08+radius*1.25*math.sin(i*math.tau/64)) for i in range(65)],.017,'Coat')
box('Flush_Cistern',0,.58,-.25,.43,.38,.17,'Steel',.023);cyl('Flush_Key',(0,.59,-.155),(0,.59,-.145),.034,'Coat',24)
for x in [-.13,.13]:cyl('Seat_Hinge',(x-.04,.44,-.14),(x+.04,.44,-.14),.022,'Steel',16)
tube('Flush_Connection',[(0,.47,-.26),(0,.30,-.26),(0,.30,-.12)],.035,'Steel');export('CompactToilet')
data=json.loads((H/'plan.json').read_text(encoding='utf-8'));reset()
for p in data['placements']:
 if p['room']!='C03' or not any(k in p['model'] for k in ['Pump','Vessel','Exchanger']):continue
 x,_,z=p['position'];yaw=math.radians(p['yaw']);c,s=math.cos(yaw),math.sin(yaw);out=Vector((x,0,z)).normalized();side=Vector((out.z,0,-out.x))
 def world(v):xx,yy,zz=v;return Vector((x+c*xx+s*zz,yy,z-s*xx+c*zz))
 if 'Pump' in p['model']:ports=[(-.46,1.10,.24),(.46,1.10,.24)];width=.95
 elif 'Vessel' in p['model']:ports=[(.45,.40,.87),(0,2.55,0)];width=.84
 else:ports=[(-.7,1.52,.68),(.7,.52,.68)];width=1.02
 for j,pt in enumerate(ports):
  yy=pt[1];sgn=-1 if j==0 else 1;p0=world(pt);p1=world((sgn*width,yy,pt[2]));p2=world((sgn*width,yy,-.78));p3=out*8.97+side*(sgn*.15);p3.y=yy;p4=p3.copy();p4.y=3.8;tube('Connected_Process_Pipe',[tuple(p0),tuple(p1),tuple(p2),tuple(p3),tuple(p4)],.065,'Teal' if j==0 else 'Steel')
  direction=(p1-p0).normalized()
  if (p1-p0).length>.06:cyl('Equipment_Flange',tuple(p0+direction*.035),tuple(p0+direction*.07),.105,'Steel',24)
  for y in [1.3,2.6,3.5]:cyl('Riser_Saddle',tuple(Vector((p3.x,y,p3.z))),tuple(out*math.sqrt(100-y*y)+side*(sgn*.15)+Vector((0,y,0))),.025,'Steel',12)
export('C03_ProcessConnections',True)
print('COMPLETE FINISH',flush=True)
