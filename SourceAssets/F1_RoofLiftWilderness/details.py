"""송예찬 / V0.01. Separate static and movable modelling only."""
import sys,os,math,json,random
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from meshlib import Model
OUT=Path(os.environ['LOCALAPPDATA'])/'Temp/AfterSeconds_20261113/candidate'
reports=[]
def save(m):reports.append(m.export(OUT))

# All shaft coordinates relative to (44,0,29), entrance toward -Z.
m=Model('FW_LiftShaft')
for x in [-2.7,2.7]:m.box((x,-6,0),(.3,26.4,6.4),'Concrete')
m.box((0,-6,3.05),(5.1,26.4,.3),'Concrete')
m.box((0,-19.1,0),(5.1,.3,5.8),'Concrete')
m.box((0,-7.6,-3.05),(5.1,14.4,.3),'Concrete')
m.box((0,-18.5,-3.05),(5.1,1,.3),'Concrete')
for x in [-1.98,1.98]:m.box((x,-16.4,-3.05),(1.14,3.2,.3),'Concrete')
for x in [-1.98,1.98]:m.box((x,1.6,-3.05),(1.14,3.2,.3),'Concrete')
m.box((0,3.55,-3.05),(5.1,.7,.3),'Concrete')
m.box((0,7.05,0),(5.7,.3,6.4),'Concrete')
for x in [-2.5,2.5]:
 for z in [-2.8,2.8]:m.box((x,-6,z),(.16,26.1,.16),'Corrosion')
for y in [-18,-12,-6,0,3.9,6.9]:
 for x in [-2.5,2.5]:m.box((x,y,0),(.16,.2,5.6),'Corrosion')
 m.box((0,y,2.8),(5,.2,.16),'Corrosion')
# Narrow steel maintenance grille reveals the machine above landing doors.
for x in [i*.3 for i in range(-8,9)]:m.box((x,5.4,-3.05),(.026,2.9,.035),'Steel')
for y in [4.05,5.4,6.85]:m.box((0,y,-3.05),(5,.04,.05),'Steel')
save(m)
m=Model('FW_LiftGuides')
for x,z in [(-1.94,-.6),(1.94,-.6),(-2.4,-1.26),(-2.4,.06)]:
 m.box((x,-7,z),(.065,24,.09),'Steel')
 for y in range(-18,6,3):m.box((x,y,z+.13),(.23,.14,.35),'Corrosion')
for x in [-1,1]:
 m.box((x,-18.8,-.6),(.5,.25,.5),'Corrosion')
 m.beam((x,-18.65,-.6),(x,-18.1,-.6),.12,'Steel',16)
save(m)
m=Model('FW_LiftLanding')
m.box((0,.01,-2.82),(3.6,.16,1.06),'Steel')
for x in [-1.43,1.43]:m.box((x,1.65,-2.8),(.22,3.3,.3),'Corrosion')
m.box((0,3.25,-2.8),(3.08,.3,.3),'Corrosion')
for x in [-1.28,1.28]:m.box((x,1.55,-2.98),(.06,3.02,.08),'Hazard')
m.box((1.85,1.15,-3.25),(.25,.38,.08),'Dark');m.beam((1.85,1.14,-3.3),(1.85,1.14,-3.35),.052,'Steel',16)
save(m)
# Car pivot at its floor, coordinates relative to car centre.
m=Model('FW_LiftCar')
m.box((0,0,0),(3.6,.15,3.5),'Steel');m.box((0,3.3,0),(3.7,.14,3.6),'Steel')
for x in [-1.75,1.75]:m.box((x,1.63,0),(.10,3.18,3.45),'Green')
m.box((0,1.63,1.70),(3.4,3.18,.1),'Green')
for x in [-1.62,1.62]:
 for z in [-1.59,1.59]:m.box((x,1.63,z),(.12,3.2,.12),'Corrosion')
 m.box((x,3.52,0),(.13,.4,3.45),'Corrosion')
 for y in [.35,2.9]:m.beam((x,y,-.08),(x+(.24 if x>0 else -.24),y,-.08),.11,'Steel',16)
m.box((0,3.65,0),(3.5,.18,.28),'Corrosion')
for z in [-.18,-.06,.06,.18]:m.beam((0,3.65,z),(0,3.79,z),.045,'Steel',12)
m.box((0,1.05,1.55),(3.15,.045,.06),'Steel')
for x in [-1.55,1.55]:m.box((x,1.05,0),(.05,.045,3.1),'Steel')
for z in [-1.64,-1.51]:m.box((0,.082,z),(3.3,.012,.035),'Dark')
m.box((0,3.19,.25),(1.1,.05,.14),'Paper')
save(m)
for side in ['Left','Right']:
 m=Model('FW_LiftDoor'+side)
 m.box((0,1.49,0),(1.31,2.86,.07),'Steel')
 for x in [-.56,.56]:m.box((x,1.49,-.05),(.035,2.86,.035),'Corrosion')
 for y in [.25,2.65]:m.box((0,y,-.055),(1.15,.035,.035),'Corrosion')
 m.box((.52 if side=='Left' else -.52,1.4,-.07),(.035,.3,.04),'Dark');save(m)
m=Model('FW_LiftCounterweight')
for z in [-.56,.56]:m.box((0,1.4,z),(.22,2.8,.13),'Corrosion')
for y in [.06,2.74]:m.box((0,y,0),(.30,.12,1.25),'Corrosion')
for i in range(11):m.box((0,.25+i*.225,0),(.3,.19,1.02),'Concrete')
for z in [-.18,-.06,.06,.18]:m.beam((0,2.8,z),(0,2.96,z),.04,'Steel',12)
save(m)
m=Model('FW_LiftSheave')
for z in [-.24,-.12,0,.12,.24]:m.torus((0,0,z),1.2,.035,'Corrosion')
for z in [-.23,.23]:
 m.torus((0,0,z),.98,.035,'Steel')
 for i in range(8):
  a=i*math.tau/8;m.beam((.18*math.cos(a),.18*math.sin(a),z),(.99*math.cos(a),.99*math.sin(a),z),.055,'Steel')
m.beam((0,0,-.36),(0,0,.36),.20,'Steel',24);save(m)
m=Model('FW_LiftHoist')
for z in [-1.2,1.2]:m.box((-1.2,4.3,z),(2.6,.22,.2),'Corrosion')
for z in [-1.05,-.15]:m.box((-1.2,4.56,z),(.5,.7,.24),'Steel')
m.beam((-1.2,4.8,-1.9),(-1.2,4.8,-.9),.37,'Green',24)
for z in [-1.8,-1.65,-1.5,-1.35]:m.torus((-1.2,4.8,z),.37,.025,'Corrosion')
m.box((-1.2,4.3,-1.45),(1,.13,1.25),'Steel');m.box((-.77,4.9,-.75),(.25,.28,.3),'Corrosion');save(m)
m=Model('FW_LiftRopeArc')
for z in [-.18,-.06,.06,.18]:m.tube([(1.2*math.cos(i*math.pi/48),1.2*math.sin(i*math.pi/48),z) for i in range(49)],.012,'Steel',8)
save(m)
m=Model('FW_LiftRopeDrop')
for z in [-.18,-.06,.06,.18]:m.beam((0,0,z),(0,-1,z),.012,'Steel',8)
save(m)

m=Model('FW_VBDoorFrame')
for x in [-1.04,1.04]:m.box((x,1.42,0),(.14,2.84,.22),'Corrosion')
m.box((0,2.79,0),(2.22,.14,.22),'Corrosion');m.box((0,-.04,0),(2.2,.08,.26),'Steel');save(m)
for side in ['Left','Right']:
 m=Model('FW_VBDoor'+side);sign=1 if side=='Left' else -1
 m.box((sign*.49,1.35,0),(.98,2.7,.075),'Green')
 for y in [.20,2.5]:m.box((sign*.49,y,-.05),(.82,.035,.025),'Steel')
 m.box((sign*.49,1.1,-.09),(.75,.06,.06),'Steel')
 for y in [.35,1.35,2.35]:m.beam((0,y-.09,0),(0,y+.09,0),.055,'Steel',12)
 save(m)
m=Model('FW_VBShaft')
for x in [-2.12,2.12]:m.box((x,-9,.1),(.24,18,6.6),'Concrete')
m.box((0,-9,3.35),(4,.18*100,.24),'Concrete');m.box((0,-9,-3.3),(4,18,.24),'Concrete')
m.box((0,-18.15,0),(4,.3,6.5),'Concrete')
for x in [-2.02,2.02]:
 for z in [-2.85,-1.5,0,1.5,3.2]:m.beam((x,0,z),(x,1.05,z),.035,'Corrosion')
 for y in [.55,1.05]:m.beam((x,y,-2.85),(x,y,3.2),.035,'Corrosion')
for x in [-2,-1,0,1,2]:m.beam((x,0,3.2),(x,1.05,3.2),.035,'Corrosion')
for y in [.55,1.05]:m.beam((-2,y,3.2),(2,y,3.2),.035,'Corrosion')
save(m)
random.seed(1311)
m=Model('FW_DryGrass')
for j in range(32):
 x,z=random.uniform(-1.4,1.4),random.uniform(-1.4,1.4);h=random.uniform(.18,.65)
 for a in [0,1.8]:
  dx,dz=.03*math.cos(a),.03*math.sin(a);m.add([(x-dx,0,z-dz),(x+dx,0,z+dz),(x+.18,h*.7,z+.06),(x+.22,h,z+.08)],[(0,1,2),(0,2,3)],'DryLeaf')
save(m)
m=Model('FW_DryShrub')
for j in range(18):
 a=random.random()*math.tau;h=random.uniform(.35,1.15);end=(math.cos(a)*.75,h,math.sin(a)*.75)
 m.beam((0,0,0),end,.016,'Wood',5)
 for k in [.55,.8]:m.beam(tuple(v*k for v in end),(end[0]+random.uniform(-.22,.22),h+.2,end[2]+random.uniform(-.2,.2)),.009,'Wood',5)
save(m)
m=Model('FW_WildernessRock');v=[(math.cos(i*math.tau/7)*random.uniform(.7,1.3),0,math.sin(i*math.tau/7)*random.uniform(.7,1.3)) for i in range(7)]+[(math.cos(i*math.tau/7)*.6,random.uniform(.45,.85),math.sin(i*math.tau/7)*.6) for i in range(7)]+[(0,.95,0)]
m.add(v,[tuple(range(6,-1,-1))]+[(i,(i+1)%7,(i+1)%7+7,i+7) for i in range(7)]+[(i+7,(i+1)%7+7,14) for i in range(7)],'Concrete');save(m)
(HERE/'detail_models.json').write_text(json.dumps(reports,indent=2))
print('DETAILS_READY',len(reports))
