"""Purpose-specific accessory meshes; base assets and placements are preserved."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mesh import *
reports=[]
def save(m):reports.append(m.export())
def motor(m,x,y,z,r=.16,length=.42):
 m.beam((x,y,z-length/2),(x,y,z+length/2),r,'Green',24)
 for i in range(12):
  a=i*math.tau/12;xx=x+math.cos(a)*r;yy=y+math.sin(a)*r;m.beam((xx,yy,z-length*.4),(xx,yy,z+length*.4),r*.075,'Steel',4)
 for zz in [z-length/2,z+length/2]:
  m.ring((x,y,zz),r*.93,.012,'Steel')
  for i in range(6):
   a=i*math.tau/6;m.bolt((x+math.cos(a)*r*.78,y+math.sin(a)*r*.78,zz+.015),.012)
 m.box((x+r*.6,y+r*.6,z),(.13,.10,.15),'Green')
def pallet(m,y=0):
 for z in [-.44,-.22,0,.22,.44]:
  for x in [-.52,0,.52]:
   for dx in [-.025,.025]:m.bolt((x+dx,y+.232,z),.0055,'y')

m=Model('FD_Press')
for x in [-1.25,1.25]:
 for y in [.52,3.48]:
  m.box((x,y,.866),(.42,.27,.018),'Steel')
  for dx in [-.14,.14]:
   for dy in [-.075,.075]:m.bolt((x+dx,y+dy,.878),.026)
 for y in [1.5,2.1,2.8]:m.box((x-.25 if x>0 else x+.25,y,.4),(.04,.12,.25),'Steel')
for x in [-.8,.8]:
 for y in [1.5,2.7]:m.beam((x,y-.065,.35),(x,y+.065,.35),.095,'Steel',16)
for z in [-.48,.48]:
 m.tube([(.19,3.3,.15),( .5,3.45,.15),(1.43,3.42,.15),(1.52,3.12,.35),(1.53,1.65,.6),(1.47,.62,z)],.027,'Rubber',10)
 for y in [1.1,1.9,2.8]:m.box((1.53,y,.61),(.09,.045,.07),'Steel')
motor(m,-1.1,.62,-.75,.19,.6);m.gauge((.95,3.84,.99),.11);m.label((-.82,3.81,.991),.38,.13)
for x in [-.75,-.25,.25,.75]:
 m.box((x,1.18,.85),(.055,.012,.38),'Dark');m.bolt((x,1.182,.99),.021,'y')
for x in [1.57,1.93]:
 for y in [1.03,1.53]:m.bolt((x,y,1.16),.012)
m.ring((1.85,1.28,1.19),.064,.011,'Hazard');m.label((1.74,1.46,1.158),.23,.055)
m.tube([(1.75,.95,1),(1.7,.68,.99),(1.5,.42,.82),(1.3,.38,.4)],.019,'Rubber');save(m)
for name,length in [('ConveyorLong',5.4),('ConveyorShort',3.2)]:
 m=Model('FD_'+name)
 for sign in [-1,1]:
  for i in range(int(length/.38)):
   x=-length/2+.2+i*.38;m.box((x,.83,sign*.674),(.10,.12,.012),'Steel');m.bolt((x,.84,sign*.685),.014,sign=sign)
  for x in [-length/2+.15,length/2-.15]:
   m.box((x,.79,sign*.68),(.24,.19,.018),'Corrosion');m.bolt((x,.84,sign*.70),.024,sign=sign);m.beam((x-.12,.72,sign*.68),(x+.12,.72,sign*.68),.015,'Steel',6)
 motor(m,-length/2+.4,.49,-.82,.14,.29)
 m.box((-length/2+.27,.63,-.71),(.4,.38,.08),'Green');m.label((-length/2+.27,.66,-.66),.22,.055)
 m.tube([(-length/2+.6,.49,-.78),(-length/2+.8,.38,-.62),(-length/2+.85,.25,-.51),(-length/2+.8,.07,-.50)],.014,'Rubber');save(m)
m=Model('FD_Forklift')
for x in [-.7,.7]:
 for z in [-.72,.72]:
  for i in range(20):
   a=i*math.tau/20;d=.309;m.beam((x-.09,.31+math.cos(a)*d,z+math.sin(a)*d),(x+.09,.31+math.cos(a+.08)*d,z+math.sin(a+.08)*d),.014,'Rubber',4)
  for i in range(6):
   a=i*math.tau/6;m.bolt((x+(.113 if x>0 else -.113),.31+math.cos(a)*.11,z+math.sin(a)*.11),.015,'x',1 if x>0 else -1)
for x in [-.43,.43]:
 for i in range(30):
  y=.5+i*.083;m.box((x,y,1.225),(.035,.061,.013),'Steel');m.box((x,y+.026,1.24),(.05,.015,.016),'Dark')
 m.tube([(x,.55,1.03),(x+.08,1,1.03),(x+.10,2.9,1.03),(x+.02,3.05,1.03),(x-.04,2.85,1.03),(x-.04,.75,1.03)],.016,'Rubber')
 m.box((x,1.97,.62),(.19,.14,.07),'Dark');m.box((x,1.97,.663),(.15,.095,.012),'Paper')
for i in range(8):m.box((-.48+i*.138,.88,-1.119),(.055,.4,.009),'Dark')
for x in [-.15,.15]:m.box((x,.91,.46),(.12,.045,.18),'Rubber')
for x in [.36,.45]:m.beam((x,.91,.1),(x,1.36,.28),.014,'Steel');m.beam((x,1.33,.28),(x,1.40,.28),.028,'Dark')
m.label((0,1.81,1.217),.3,.1);m.box((0,1.405,-.414),(.035,.5,.018),'Dark');save(m)
m=Model('FD_PartsRack')
for x in [-1.05,1.05]:
 for z in [-.442,.442]:
  for y in [.22+i*.12 for i in range(19)]:m.box((x,y,z),(.019,.043,.003),'Dark')
  for y in [.11,.86,1.61,2.36]:m.bolt((x,y,z+.004),.015)
for row in range(3):
 y=.17+row*.75
 for x in [-.69,-.03,.63]:
  m.box((x,y+.19,.328),(.18,.065,.006),'Dark');m.box((x,y+.19,.338),(.12,.02,.015),'Steel');m.label((x,y+.325,.329),.24,.055)
  m.box((x,y+.39,0),(.025,.008,.64),'Paper')
for y in [.12,.87,1.62,2.37]:m.box((0,y+.027,.437),(2.15,.04,.02),'Steel')
save(m)
for name,levels in [('CrateLoad_A',2),('CrateLoad_B',3),('PalletStack',0)]:
 m=Model('FD_'+name)
 if not levels:
  for i in range(4):pallet(m,i*.235)
 else:
  pallet(m)
  for row in range(levels):
   for x in [-.3,.3]:
    for z in [-.23,.23]:
     y=.235+row*.41;m.box((x,y+.2,z+.211),(.008,.39,.002),'Dark');m.label((x+.08,y+.26,z+.214),.19,.07)
     for dx in [-.275,.275]:m.box((x+dx,y+.2,z+.213),(.008,.38,.004),'Paper')
  for x in [-.43,.43]:m.box((x,.63,.466),(.065,.1,.016),'Steel');m.bolt((x,.63,.478),.009)
 save(m)
m=Model('FD_DrumGroup')
for x,z in [(-.34,0),(.34,.06),(0,-.58)]:
 m.ring((x,.92,z),.275,.009,'Steel','y');m.ring((x+.15,.948,z),.034,.006,'Steel','y');m.beam((x-.10,.92,z-.1),(x-.10,.942,z-.1),.019,'Steel',8)
 m.label((x,.51,z+.293),.18,.11)
 for y in [.25,.67]:m.ring((x,y,z),.308,.006,'Steel','y')
save(m)
m=Model('FD_CableReel')
for side in [-1,1]:
 x=side*.511
 for off in [-.48,-.24,0,.24,.48]:
  half=math.sqrt(.70**2-off**2);m.box((x,.73+off,0),(.003,.007,half*2),'Dark')
 for i in range(8):
  a=i*math.tau/8;m.bolt((x,.73+.5*math.cos(a),.5*math.sin(a)),.024,'x',side)
 m.ring((x+side*.008,.73,0),.17,.014,'Steel','x')
m.tube([(.29,.73,.55),(.38,.42,.54),(.38,.12,.65),(.21,.035,.85),(-.22,.03,.86),(-.48,.03,.65)],.018,'Rubber');save(m)
for name,w,h,d,rows in [('Switchgear',1.4,2.3,.65,1),('FileCabinet',.62,1.35,.6,4),('Locker',.72,1.9,.52,1),('KitchenCounter',1.7,.9,.65,2)]:
 m=Model('FD_'+name);front=d/2+.034
 for y in [.18,h-.18]:
  m.box((-w/2+.065,y,front),(.085,.16,.025),'Steel')
  for dy in [-.05,.05]:m.bolt((-w/2+.065,y+dy,front+.02),.01)
 for i in range(rows):
  y=(i+.5)*h/rows;m.label((-.13,y+.06,front+.008),min(.18,w*.3),.055)
  m.beam((w*.3,y,front),(w*.3,y,front+.025),.023,'Steel',12);m.box((w*.3,y,front+.027),(.004,.026,.002),'Dark')
 for x in [-w/2+.025,w/2-.025]:m.box((x,h/2,front-.013),(.008,h-.05,.009),'Dark')
 if name=='Switchgear':
  for x in [-.4,0,.4]:
   for i in range(6):m.box((x-.065+i*.026,1.96,front+.041),(.005,.07,.004),'Paper')
   m.beam((x-.05,1.92,front+.047),(x+.03,1.98,front+.047),.003,'Hazard',4)
  m.label((0,.37,front+.008),.38,.13)
  for x in [-.45,-.15,.15,.45]:m.tube([(x,0,-.12),(x,.2,-.12),(x,.24,-.32)],.025,'Rubber')
 if name=='KitchenCounter':
  for x in [-.242,.242]:m.box((x,h+.066,0),(.018,.017,.36),'Steel')
  for z in [-.18,.18]:m.box((0,h+.066,z),(.5,.017,.017),'Steel')
  m.ring((.07,h+.068,.02),.035,.005,'Steel','y')
  for i in range(5):m.box((.07,h+.07,-.002+i*.011),(.045,.003,.003),'Steel')
  m.ring((.45,h+.3,0),.085,.012,'Steel','y');m.tube([(.53,h+.25,0),(.63,h+.24,0),(.63,h+.10,0),(.53,h+.08,0)],.015,'Dark')
 save(m)
m=Model('FD_ScrapBin')
for x in [-.55,.55]:
 m.box((x,.65,.511),(.11,.22,.018),'Steel');m.tube([(x-.07,.73,.53),(x-.07,.65,.59),(x+.07,.65,.59),(x+.07,.73,.53)],.014,'Steel')
 for y in [.38,.79]:m.bolt((x,y,.511),.018)
for y in [.28,.83]:m.box((0,y,.508),(1.35,.024,.024),'Corrosion')
save(m)
m=Model('FD_ShippingCage')
for x in [-1,1]:
 for y in [.15,1.15,2.25]:m.box((x,y,.991),(.14,.13,.017),'Steel');m.bolt((x,y,1.005),.018)
m.beam((-1,.1,-.97),(1,2.25,-.97),.018,'Steel');m.beam((1,.1,-.97),(-1,2.25,-.97),.018,'Steel');save(m)
for name in ['PalletJack','HandTruck']:
 m=Model('FD_'+name)
 if name=='PalletJack':
  for x in [-.25,.25]:
   m.bolt((x,.26,.81),.018,'y');m.bolt((x,.26,.94),.018,'y');m.box((x,.247,.43),(.13,.005,.47),'Steel')
  m.beam((0,.42,-.35),(0,.72,-.35),.041,'Steel',16);m.ring((0,.53,-.35),.053,.01,'Steel','y');m.label((0,.48,-.145),.22,.07)
  m.tube([(.13,.49,-.35),(.22,.58,-.4),(.20,.72,-.50)],.013,'Rubber')
 else:
  for x in [-.24,.24]:
   for y in [.45,.75,1.05]:m.bolt((x,y,-.089),.012)
   m.beam((x,1.08,-.12),(x,1.29,-.12),.035,'Rubber',12)
  for x in [-.2,-.1,0,.1,.2]:m.box((x,.071,.20),(.018,.005,.36),'Steel')
 save(m)
m=Model('FD_Bench')
for x in [-.65,.65]:
 for z in [-.16,.16]:m.bolt((x,.495,z),.014,'y')
 for y in [.65,.9]:m.bolt((x,y,-.162),.014)
for x in [-.6,0,.6]:m.box((x,.782,-.164),(.004,.45,.002),'Dark')
save(m)
m=Model('FD_OfficeChair')
for x in [-.265,.265]:
 m.bolt((x,.48,0),.018,'x',1 if x>0 else -1);m.tube([(x,.46,.11),(x,.4,.14),(x*1.2,.4,.14)],.014,'Steel')
m.box((.30,.4,.14),(.12,.028,.06),'Dark')
for x in [-.19,.19]:
 for y in [.65,1.04]:m.bolt((x,y,-.255),.012,sign=-1)
save(m)
m=Model('FD_Desk')
m.box((0,.62,-.29),(1.12,.045,.16),'Steel')
for x in [-.48,.48]:m.box((x,.7,-.29),(.04,.15,.04),'Steel')
for x in [-.35,-.12,.16]:m.tube([(x,.79,-.26),(x,.66,-.29),(x+.12,.63,-.28),(.49,.63,-.27),(.58,.40,-.28),(.58,.03,-.3)],.006,'Rubber',6)
m.box((.38,.655,-.28),(.3,.035,.085),'Paper')
for x in [.29,.38,.47]:m.box((x,.677,-.28),(.035,.003,.026),'Dark')
save(m)
m=Model('FD_MotorBench')
for x in [-.68,-.34,0,.34,.68]:
 for y in [1.12,1.29,1.46,1.58]:m.box((x,y,-.364),(.014,.014,.003),'Dark')
for x in [-.85,.85]:
 for y in [.22,.8]:m.bolt((x,y,.41),.016)
for x in [-.78,-.46]:
 for z in [.02,.18]:m.bolt((x,1.052,z),.012,'y')
m.box((-.71,1.14,.105),(.009,.11,.20),'Dark');m.box((-.52,1.14,.105),(.009,.11,.20),'Dark')
m.tube([(.72,1.0,-.27),(.86,.85,-.29),(.87,.52,-.3),(.68,.35,-.28),(.45,.35,-.29)],.011,'Rubber');save(m)
m=Model('FD_ToolCart')
for y in [.29,.43,.57,.71]:m.label((-.20,y,.322),.12,.045)
for x in [-.32,.32]:
 for z in [-.23,.23]:m.bolt((x+.052,.09,z),.015,'x')
for x in [-.30,-.05]:m.box((x,.949,.118),(.022,.05,.015),'Steel')
m.beam((.2,.91,.06),(.2,.94,.06),.064,'Steel',16);m.bolt((.2,1.068,.06),.013,'y');save(m)
m=Model('FD_InspectionCounter')
for y in [.33,.57,.81]:m.box((-.5,y,.348),(.42,.006,.006),'Dark');m.label((-.58,y+.08,.35),.14,.04)
for x in [-.7,-.3]:m.bolt((x,.91,.35),.012)
for z in [-.25,.05]:m.box((.4,1.04,z),(.45,.02,.009),'Steel')
save(m)
(H/'props.json').write_text(json.dumps(reports,indent=2));print('PROPS_READY',len(reports))
