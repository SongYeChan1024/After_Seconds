"""Each output is attached to its existing fixed/moving owner. No motion code."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mesh import *
reports=[]
def save(m,parent):q=m.export();q['parent']=parent;reports.append(q)
m=Model('FD_LiftCar')
for x in [-1.10,0,1.10]:
 m.box((x,1.72,1.638),(1.07,2.85,.015),'Green')
 for dx in [-.49,.49]:
  for y in [.34,1.4,3.04]:m.bolt((x+dx,y,1.625),.012,sign=-1)
for x in [-1.69,1.69]:
 m.box((x,.26,0),(.018,.30,3.1),'Steel')
 for z in [-1.3,0,1.3]:
  for y in [.17,.35]:m.bolt((x+(.015 if x<0 else -.015),y,z),.01,'x',1 if x<0 else -1)
for x in [-1.4,-.7,0,.7,1.4]:m.box((x,1.05,1.61),(.055,.1,.09),'Steel')
m.box((0,.26,1.622),(3.25,.30,.02),'Steel')
for i in range(17):
 for j in range(16):
  x=-1.44+i*.18;z=-1.35+j*.18;sgn=1 if (i+j)%2==0 else -1;m.beam((x-.027,.079,z-.025*sgn),(x+.027,.079,z+.025*sgn),.004,'Steel',4)
m.box((0,3.216,.9),(.95,.018,.43),'Dark')
for x in [-.48,.48]:m.box((x,3.20,.9),(.022,.018,.46),'Steel')
for z in [.67,1.13]:m.box((0,3.20,z),(.97,.018,.022),'Steel')
for i in range(15):m.box((-.43+i*.061,3.201,.9),(.018,.012,.40),'Steel')
for x in [-.48,.48]:
 for z in [.67,1.13]:m.bolt((x,3.19,z),.012,'y',-1)
# Control panel authored facing +Z then mounted on inner right wall facing -X.
start=len(m.v);m.box((0,1.48,0),(.32,.97,.048),'Steel');m.box((0,1.77,.028),(.23,.13,.018),'Dark')
m.text('1F',(0,1.77,.04),.068,'Paper')
for x,y,label in [(-.075,1.52,'1F'),(.075,1.52,'B1'),(-.075,1.32,'< >'),(.075,1.32,'> <')]:
 m.beam((x,y,.026),(x,y,.042),.038,'Steel',20);m.ring((x,y,.045),.026,.003,'Dark',n=20);m.text(label,(x,y,.047),.025,'Dark')
m.beam((0,1.09,.026),(0,1.09,.052),.043,'Red',20);m.text('STOP',(0,1.19,.031),.024,'Dark')
for x in [-.135,.135]:
 for y in [1.04,1.91]:m.bolt((x,y,.028),.008)
for i in range(start,len(m.v)):
 x,y,z=m.v[i];m.v[i]=(1.67-z,y+.15,x-.87)
# Plain capacity plate on rear, no light/signalling behavior.
start=len(m.v);m.box((0,2.52,0),(.72,.22,.012),'Dark');m.text('SERVICE LIFT',(0,2.56,.008),.055);m.text('MAX. LOAD  1500 kg',(0,2.48,.008),.032)
for i in range(start,len(m.v)):
 x,y,z=m.v[i];m.v[i]=(-x,y,1.61-z)
for x in [-1.62,1.62]:
 for z in [-1.3,1.3]:
  m.box((x,3.51,z),(.24,.15,.25),'Steel')
  for xx in [-.065,.065]:m.bolt((x+xx,3.595,z),.019,'y')
 for y in [.35,2.9]:
  # Existing shoes already reach x +/-1.86; supplementary brackets stop before guide rails.
  m.box((x+(.22 if x>0 else -.22),y,-.08),(.08,.29,.23),'Corrosion')
  for zz in [-.15,.0]:m.bolt((x+(.27 if x>0 else -.27),y,zz),.014,'x',1 if x>0 else -1)
for z in [-.18,-.06,.06,.18]:
 m.ring((0,3.72,z),.038,.008,'Steel','y',20);m.bolt((0,3.75,z),.025,'y')
save(m,'Car')
for side in ['Left','Right']:
 m=Model('FD_LiftDoor'+side)
 for x in [-.57,.57]:
  for y in [.22,.65,2.55,2.79]:m.bolt((x,y,-.071),.011,sign=-1)
 for x in [-.42,.42]:
  m.box((x,2.98,.02),(.12,.22,.05),'Steel');m.beam((x,3.03,-.035),(x,3.03,.08),.067,'Rubber',20);m.bolt((x,3.03,-.05),.015,sign=-1)
 x=.64 if side=='Left' else -.64;m.box((x,1.48,-.047),(.025,2.78,.016),'Rubber')
 for i in range(5):m.box((-.4+i*.2,.16,-.042),(.11,.12,.008),'Steel')
 save(m,'Car/Door'+side)
m=Model('FD_LiftHoist')
# Parent is MachineBedMotorBrake, retaining its +0.75m offset.
for i in range(18):
 a=i*math.tau/18;x=-1.2+math.cos(a)*.375;y=4.8+math.sin(a)*.375;m.beam((x,y,-1.85),(x,y,-1.0),.019,'Steel',4)
for z in [-1.91,-.93]:
 m.ring((-1.2,4.8,z),.33,.016,'Steel')
 for i in range(8):
  a=i*math.tau/8;m.bolt((-1.2+.29*math.cos(a),4.8+.29*math.sin(a),z),.025,sign=-1 if z<-1 else 1)
for x in [-1.95,-.45]:
 for z in [-1.83,-1.04]:m.bolt((x,4.38,z),.032,'y')
m.box((-.82,5.05,-1.4),(.23,.2,.3),'Green')
for z in [-1.5,-1.3]:m.bolt((-.82,5.16,z),.013,'y')
m.tube([(-.70,5.02,-1.4),(-.56,4.98,-1.4),(-.5,4.59,-1.4),(-.40,4.53,-1.3),(-.05,4.53,-1.2)],.022,'Rubber',10)
m.box((0,4.49,-1.2),(.25,.16,.22),'Dark')
# Brake caliper and spring on fixed machine; rotating disc belongs to sheave below.
for z in [-.98,-.78]:m.box((-.77,4.94,z),(.24,.38,.12),'Steel')
m.beam((-.8,4.9,-1.03),(-.8,4.9,-.71),.025,'Steel',12)
for i in range(9):m.ring((-.8,4.9,-1.03+i*.018),.043,.007,'Steel',n=16)
m.box((-1.2,4.8,-1.932),(.33,.18,.012),'Dark')
start=len(m.v);m.text('M-01  11 kW',(-1.2,4.8,0),.037)
for i in range(start,len(m.v)):
 x,y,z=m.v[i];m.v[i]=(x,y,-1.942-z)
save(m,'FixedShaft/MachineBedMotorBrake')
m=Model('FD_LiftSheave')
for z in [-.27,.27]:
 m.ring((0,0,z),.27,.018,'Steel',n=32)
 for i in range(8):
  a=i*math.tau/8;m.bolt((math.cos(a)*.25,math.sin(a)*.25,z),.027,sign=-1 if z<0 else 1)
m.ring((0,0,-.34),.52,.045,'Steel',n=40);save(m,'Sheave')
m=Model('FD_LiftGuides')
for x,z in [(-1.94,-.6),(1.94,-.6),(-2.4,-1.26),(-2.4,.06)]:
 for y in range(-18,6,3):
  for dx in [-.075,.075]:m.bolt((x+dx,y,z-.055),.019,sign=-1)
 for y in range(-17,5,3):
  m.box((x,y,z+.065),(.13,.4,.025),'Steel')
  for dy in [-.13,.13]:m.bolt((x,y+dy,z+.086),.017)
for x in [-1,1]:
 for i in range(12):m.ring((x,-18.62+i*.038,-.6),.13,.018,'Steel','y',24)
for z in [-2.5,-2.68]:m.box((0,.106,z),(2.7,.012,.021),'Dark')
for x in [-1.35,1.35]:
 for y in [.25,1.65,3.15]:m.bolt((x,y,-2.965),.021,sign=-1)
# Recessed wiring conduit, firmly attached to shaft outside the car envelope.
m.tube([(2.49,-17.8,1.6),(2.49,5.8,1.6),(2.49,6.35,.8)],.026,'Steel',8)
m.box((2.49,6.35,.8),(.09,.32,.30),'Dark')
for y in range(-17,7,2):m.box((2.49,y,1.6),(.07,.06,.12),'Corrosion')
save(m,'FixedShaft')
m=Model('FD_LiftCounterweight')
for z in [-.56,.56]:
 for y in [.15,1.4,2.65]:m.bolt((.13,y,z),.023,'x')
 m.box((0,1.4,z),(.27,2.44,.022),'Steel')
for z in [-.18,-.06,.06,.18]:m.bolt((0,2.91,z),.025,'y')
save(m,'Counterweight')
(H/'lift.json').write_text(json.dumps(reports,indent=2));print('LIFT_READY',len(reports))
