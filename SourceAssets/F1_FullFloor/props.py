import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
def legs(w,d,h):
 for x in [-w/2,w/2]:
  for z in [-d/2,d/2]:box('Leg',(x,h/2,z),(.065,h,.065),'Steel',.006)
def pallet(y=0):
 for x in [-.52,0,.52]:box('PalletRunner',(x,y+.075,0),(.12,.15,1),'Wood',.004)
 for z in [-.44,-.22,0,.22,.44]:box('PalletBoard',(0,y+.19,z),(1.25,.08,.17),'Wood',.003)
def drum(x,y,z):
 cyl('Drum',(x,y+.46,z),.29,.9,'Rust',verts=24)
 for h in [.08,.25,.67,.87]:cyl('Rim',(x,y+h,z),.302,.025,'Steel',verts=24)
 cyl('Lid',(x,y+.917,z),.278,.018,'Green',verts=24);cyl('Bung',(x+.15,y+.94,z),.035,.02,'Steel')
def wheel(x,y,z,r=.28,w=.16):
 cyl('Tyre',(x,y,z),r,w,'Rubber','x',24);cyl('WheelHub',(x,y,z),r*.53,w+.012,'Steel','x')
def railing(x0,x1,z,y):
 for x in [x0,x1]:beam('Post',(x,y,z),(x,y+1,z),.045)
 for h in [.5,1]:beam('Rail',(x0,y+h,z),(x1,y+h,z),.04)

reset()
box('MachineFoot',(0,.16,0),(3.3,.32,2.65),'Dark',.06)
for x in [-1.25,1.25]:box('PressColumn',(x,2,0),(.48,3.8,1.7),'Green',.045);box('Guide',(x*.64,2.0,.35),(.12,2.4,.12),'Steel',.01)
box('Crown',(0,3.8,0),(3.4,.65,1.9),'Green',.06);box('Platen',(0,1.05,.2),(2.35,.25,1.85),'Steel',.025);box('Die',(0,1.27,.2),(1.15,.18,.85),'Dark',.02);box('Ram',(0,2.45,.15),(2.0,.45,1.45),'Steel',.03);cyl('HydraulicRam',(0,3.05,.15),.22,.9,'Steel',verts=24)
box('ControlPod',(1.75,1.28,1),(.48,.65,.3),'Coat',.025)
for x in [1.62,1.85]:cyl('ControlButton',(x,1.28,1.17),.055,.035,'Red' if x<1.7 else 'Indicator','z')
box('WarningPlate',(0,3.78,.966),(1.5,.28,.014),'Hazard',.003);text('PressMark','PRESS / 04',(0,3.78,.982),.17,'Dark')
for x in [-.98,.98]:beam('Guard',(x,.5,1.25),(x,2,1.25),.055,'Hazard')
for x in [-1.25,1.25]:
 for z in [-.8,.8]:cyl('Anchor',(x,.345,z),.075,.035,'Steel',verts=8)
save('Press')

for name,length in [('ConveyorLong',5.4),('ConveyorShort',3.2)]:
 reset();legs(length-.35,1.05,.78)
 for z in [-.58,.58]:box('SideBeam',(0,.82,z),(length,.18,.12),'Green');box('EdgeRail',(0,1.02,z),(length,.045,.045),'Steel',.004)
 for i in range(int(length/.19)):
  x=-length/2+.11+i*.19;cyl('Roller',(x,.87,0),.065,1.03,'Steel','z',16)
 box('DriveMotor',(-length/2+.4,.49,-.78),(.65,.32,.28),'Green',.03)
 for x in [-length/2+.35,length/2-.35]:box('CrossBrace',(x,.36,0),(.07,.08,1.15),'Steel')
 save(name)

reset();box('Chassis',(0,.6,0),(1.28,.55,2.15),'Hazard',.09);box('Counterweight',(0,.85,-.85),(1.42,.75,.52),'Green',.08)
for x in [-.7,.7]:
 for z in [-.72,.72]:wheel(x,.31,z,.31,.22)
for x in [-.59,.59]:
 for z in [-.55,.58]:beam('OverheadGuardPost',(x,.75,z),(x,2.25,z),.06,'Dark')
box('OverheadGuard',(0,2.28,0),(1.4,.1,1.55),'Green',.03)
box('Seat',(0,1.11,-.23),(.65,.13,.6),'Rubber',.06);box('SeatBack',(0,1.43,-.48),(.65,.6,.12),'Rubber',.06)
beam('SteeringColumn',(0,.94,.5),(0,1.48,.42),.07,'Steel');cyl('SteeringWheel',(0,1.5,.42),.22,.03,'Dark','y',24)
for x in [-.53,.53]:box('Mast',(x,1.65,1.12),(.14,3.15,.17),'Steel');box('Carriage',(x,.65,1.25),(.19,.95,.14),'Dark');box('Fork',(x,.13,1.95),(.15,.07,1.65),'Steel',.015)
for y in [.35,1.05,2.5,3.1]:box('MastCross',(0,y,1.12),(1.15,.1,.12),'Steel')
cyl('LiftPiston',(0,1.7,1.08),.065,2.6,'Steel');text('TruckNumber','12',(0,.88,-1.125),.26,'Paper',180);save('Forklift')

reset()
for x in [-1.05,1.05]:
 for z in [-.4,.4]:box('RackUpright',(x,1.25,z),(.075,2.5,.075),'Green',.004)
for y in [.12,.87,1.62,2.37]:
 box('Shelf',(0,y,0),(2.18,.065,.86),'Steel',.004)
 for z in [-.45,.45]:box('ShelfBeam',(0,y-.06,z),(2.2,.13,.06),'Rust',.004)
for i in range(3):
 for j in range(3):
  x=-.69+j*.66;y=.17+i*.75;box('PartsBox',(x,y+.19,0),(.55,.38,.65),'Wood' if(i+j)%2 else 'Coat',.012);box('Label',(x,y+.22,.33),(.22,.08,.008),'Paper',.001)
beam('RearBrace',(-1,0,-.42),(1,2.5,-.42),.025,'Steel');save('PartsRack')

for name,variant in [('CrateLoad_A',0),('CrateLoad_B',1)]:
 reset();pallet()
 for level in range(2 if variant==0 else 3):
  for x in [-.3,.3]:
   for z in [-.23,.23]:
    y=.235+level*.41;box('ShippingCarton',(x,y+.2,z),(.56,.4,.42),'Wood' if level%2==0 else 'Coat',.008);box('PackingTape',(x,y+.405,z),(.055,.004,.43),'Paper',0)
 for x in [-.43,.43]:box('Strapping',(x,.65+variant*.2,.459),(.025,.83+variant*.4,.006),'Dark',0)
 save(name)
reset()
for i in range(4):pallet(i*.235)
save('PalletStack')

reset()
for x in [-.25,.25]:box('Fork',(x,.15,.45),(.18,.19,1.25),'Hazard',.03);wheel(x,.1,1,.095,.1)
box('HydraulicUnit',(0,.35,-.35),(.55,.52,.4),'Green',.03);cyl('Pump',(0,.7,-.35),.06,.5,'Steel');beam('HandleStem',(0,.55,-.35),(0,1.25,-.65),.055,'Dark')
for x in [-.23,.23]:beam('Handle',(x,1.05,-.6),(x,1.4,-.65),.04,'Dark')
beam('HandleCross',(-.23,1.4,-.65),(.23,1.4,-.65),.04,'Dark');save('PalletJack')

reset()
for x in [-.24,.24]:beam('Frame',(x,.1,0),(x,1.3,-.12),.045,'Green');wheel(x,.18,-.04,.18,.11)
for y in [.25,.6,.95,1.3]:beam('FrameBar',(-.24,y,-y*.09),(.24,y,-y*.09),.04,'Green')
box('ToePlate',(0,.04,.2),(.54,.06,.44),'Steel');save('HandTruck')

reset();cyl('CableCore',(0,.73,0),.53,.85,'Dark','x',40)
for x in [-.46,.46]:
 cyl('WoodFlange',(x,.73,0),.73,.09,'Wood','x',40);cyl('AxleEnd',(x*1.12,.73,0),.14,.02,'Dark','x')
 for i in range(8):
  a=i*math.tau/8;cyl('Fastener',(x*1.13,.73+.48*math.cos(a),.48*math.sin(a)),.03,.025,'Steel','x',8)
for x in [-.37+i*.065 for i in range(12)]:cyl('CableCoil',(x,.73,0),.551,.035,'Rubber','x',40)
save('CableReel')
reset();drum(-.34,0,0);drum(.34,0,.06);drum(0,0,-.58);save('DrumGroup')
reset();box('BinBase',(0,.15,0),(1.4,.2,1.0),'Green');
for x in [-.68,.68]:box('BinSide',(x,.55,0),(.08,.8,1),'Green')
for z in [-.46,.46]:box('BinSide',(0,.55,z),(1.3,.8,.08),'Green')
for i in range(8):box('Scrap',((i%3-.8)*.32,.55+(i%2)*.1,(i//3-1)*.23),(.65,.07,.24),'Rust',.006,yaw=i*37)
save('ScrapBin')

reset();box('CageBase',(0,.08,0),(2.1,.16,2),'Steel')
for x in [-1,1]:
 for z in [-.95,.95]:box('Corner',(x,1.15,z),(.07,2.3,.07),'Steel',.005)
for y in [.5,1,1.5,2,2.3]:
 for x in [-1,1]:beam('MeshBar',(x,y,-.95),(x,y,.95),.012,'Steel')
 beam('MeshBar',(-1,y,-.95),(1,y,-.95),.012,'Steel')
for i in range(11):
 z=-.95+i*.19
 for x in [-1,1]:beam('MeshBar',(x,.1,z),(x,2.3,z),.012,'Steel')
 beam('MeshBar',(-1+i*.2,.1,-.95),(-1+i*.2,2.3,-.95),.012,'Steel')
for x in [-.55,.55]:box('Carton',(x,.5,-.25),(.75,.8,1),'Wood')
save('ShippingCage')

reset();legs(2.6,.88,.75);box('ScannerBelt',(0,.77,0),(3,.16,.95),'Dark')
for x in [-.7,.7]:box('TunnelSide',(x,1.15,0),(.25,.95,1.3),'Coat',.04)
box('TunnelTop',(0,1.65,0),(1.65,.22,1.3),'Coat',.04)
for z in [-.67,.67]:
 for i in range(8):box('LeadCurtain',(-.48+i*.136,1.24,z),(.122,.65,.025),'Rubber',.003)
box('ControlTray',(.97,1.05,.56),(.4,.14,.4),'Green');cyl('Stop',(1.08,1.14,.56),.04,.03,'Red');save('Scanner')
reset();legs(1.5,.65,.92);box('Counter',(0,.94,0),(1.7,.1,.82),'Wood');box('DrawerUnit',(-.5,.48,0),(.5,.8,.68),'Green');box('ReadingTray',(.4,1.015,-.1),(.45,.04,.32),'Steel');save('InspectionCounter')

for name in ['FileCabinet','Locker','RadioCabinet','Switchgear','KitchenCounter']:
 reset();w,h,d={'FileCabinet':(.62,1.35,.6),'Locker':(.72,1.9,.52),'RadioCabinet':(1.1,1.75,.5),'Switchgear':(1.4,2.3,.65),'KitchenCounter':(1.7,.9,.65)}[name]
 box('Housing',(0,h/2,0),(w,h,d),'Green' if name!='KitchenCounter' else 'Coat',.024)
 count=4 if name=='FileCabinet' else 2 if name in ['RadioCabinet','KitchenCounter'] else 1
 for i in range(count):
  hh=(h-.12)/count;y=.06+hh*(i+.5);box('Door',(0,y,d/2+.016),(w-.06,hh-.035,.025),'Coat' if name=='FileCabinet' else 'Green',.006);box('Pull',(.16,y+.05,d/2+.05),(.12,.022,.035),'Steel',.006)
  if name in ['Locker','Switchgear']:
   for j in range(7):box('Vent',(0,y+.25+j*.04,d/2+.032),(w*.6,.014,.006),'Dark',0)
 if name=='RadioCabinet':
  for x in [-.3,0,.3]:box('ChargingRadio',(x,h+.12,0),(.13,.24,.11),'Dark');beam('Antenna',(x-.04,h+.24,0),(x-.04,h+.43,0),.012,'Dark')
 if name=='KitchenCounter':
  box('Worktop',(0,h+.025,0),(w+.04,.05,d+.04),'Steel');cyl('Kettle',(.45,h+.16,0),.1,.27,'Coat');box('Sink',(0,h+.055,0),(.48,.015,.35),'Dark');beam('Tap',(0,h,-.22),(0,h+.3,-.22),.028);beam('TapHead',(0,h+.3,-.22),(0,h+.3,-.05),.028)
 if name=='Switchgear':
  for x in [-.4,0,.4]:box('Meter',(x,h-.35,d/2+.05),(.22,.18,.04),'Dark');cyl('Switch',(x,1.2,d/2+.07),.06,.055,'Red' if x<0 else 'Steel','z')
 save(name)

reset();legs(1.5,.42,.42);box('Seat',(0,.45,0),(1.7,.08,.5),'Wood');box('Back',(0,.78,-.2),(1.7,.5,.06),'Wood');save('Bench')
reset();box('KeyBoard',(0,1.6,0),(1.15,.72,.055),'Green');
for i in range(8):
 x=(i%4-1.5)*.23;y=1.65-(i//4)*.25;beam('KeyHook',(x,y,.03),(x,y,.08),.012);cyl('KeyRing',(x,y-.04,.085),.025,.008,'Steel','z',12);box('Key',(x,y-.09,.085),(.016,.07,.01),'Steel',.001);box('Tag',(x+.035,y-.08,.09),(.04,.06,.006),'Paper',.001)
text('Label','KEY REGISTER',(0,1.86,.032),.075);save('KeyBoard')
reset();box('Board',(0,1.55,0),(1.3,.85,.07),'Wood');
for i in range(4):
 x=(i%2-.5)*.52;y=1.55+(i//2-.5)*.32;box('Notice',(x,y,.04),(.43,.26,.008),'Paper',.001);text('Print','SHIFT A' if i==0 else 'NOTICE',(x,y+.05,.047),.043,'Dark');
 for j in range(3):box('TextRule',(x,y-.01-j*.035,.047),(.3,.006,.002),'Dark',0)
save('NoticeBoard')
reset();box('Mount',(0,.8,-.12),(.4,1.6,.1),'Dark');cyl('Extinguisher',(0,.62,0),.12,.5,'Red');cyl('Neck',(0,.92,0),.045,.1,'Steel');box('Handle',(0,1,0),(.17,.03,.04),'Dark');beam('Hose',(.12,.92,0),(.17,.45,0),.025,'Dark');box('Sign',(0,1.4,-.055),(.33,.25,.025),'Red');text('Fire','FIRE',(0,1.4,-.036),.085);save('SafetyStation')

reset();bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=1);o=bpy.context.object;o.scale=(.14,.18,.1);o.location=xyz(0,.075,0);finish(o,'Shell','Hazard');cyl('Brim',(0,.012,0),.19,.018,'Hazard',verts=32);box('TopRidge',(0,.16,0),(.025,.022,.23),'Hazard',.009);save('HardHat')
reset();box('Radio',(0,.12,0),(.12,.24,.065),'Dark',.018);beam('Antenna',(-.038,.23,0),(-.038,.43,0),.012,'Rubber');box('LCD',(0,.17,.035),(.082,.045,.005),'Indicator',.003)
for i in range(5):box('SpeakerGrille',(0,.06+i*.012,.035),(.08,.004,.003),'Steel',0)
for x in [-.03,.03]:box('Button',(x,.115,.039),(.019,.014,.006),'Coat',.002)
save('HandRadio')
reset();box('Folder',(0,.012,0),(.25,.024,.32),'Green',.002);box('Paper',(0,.027,.005),(.23,.006,.29),'Paper',.001)
for i in range(8):box('RecordLine',(0,.031,-.1+i*.026),(.18,.001,.002),'Dark',0)
box('Clip',(0,.037,-.135),(.06,.01,.025),'Steel',.002);save('ShippingRecord')

reset();box('Door',(0,1.45,0),(2.1,2.9,.12),'Green',.02)
for x in [-1.1,1.1]:box('Frame',(x,1.5,0),(.12,3,.2),'Steel')
box('Lintel',(0,3,0),(2.3,.14,.2),'Steel');box('DoorSeam',(0,1.45,.066),(.009,2.8,.006),'Dark',0)
for x in [-.45,.45]:box('PanicBar',(x,1.05,.12),(.75,.055,.06),'Steel')
box('VisionPanel',(0,2.2,.067),(.7,.33,.008),'Dark');text('DoorLabel','STAIR / B1',(0,2.65,.075),.13);save('ArrivalFireDoor')
reset();box('CabinFloor',(0,.0375,0),(3.7,.075,3.5),'Steel');box('BackWall',(0,1.8,-1.72),(3.7,3.45,.1),'Green');
for x in [-1.8,1.8]:box('SideWall',(x,1.8,0),(.1,3.45,3.5),'Green');beam('Handrail',(x*.95,1,-1.5),(x*.95,1,1.4),.05,'Steel');box('GateTrack',(x,1.8,1.75),(.12,3.6,.12),'Steel')
box('CabinCeiling',(0,3.58,0),(3.7,.12,3.5),'Steel');box('Header',(0,3.38,1.75),(3.7,.26,.15),'Hazard');box('CallPanel',(1.69,1.4,1.55),(.1,.4,.2),'Steel');save('LiftCabin',lod=False)
reset();box('BarrierBody',(0,.55,0),(.28,1.1,.3),'Hazard');cyl('Base',(0,.04,0),.22,.08,'Steel');save('BarrierPedestal')
reset();box('GatePedestal',(0,.58,0),(.42,1.16,.45),'Hazard');beam('RaisedGate',(0,.95,0),(.8,3.5,0),.12,'Paper');box('Pivot',(0,1,0),(.5,.25,.55),'Dark');save('GateBarrier')
reset();cyl('Bollard',(0,.5,0),.13,1,'Hazard');cyl('BollardBand',(0,.75,0),.134,.12,'Dark');cyl('Base',(0,.035,0),.23,.07,'Steel');save('GuardBollard')
reset();cyl('GasLift',(0,.28,0),.04,.4,'Steel');box('Seat',(0,.48,0),(.52,.12,.5),'Fabric',.04);box('Back',(0,.84,-.21),(.5,.58,.08),'Fabric',.04)
for x in [-.3,.3]:beam('ArmSupport',(x,.45,-.12),(x,.7,-.12),.035,'Steel');box('Armrest',(x,.72,0),(.07,.045,.35),'Dark',.02)
for i in range(5):
 a=i*math.tau/5;x=.32*math.cos(a);z=.32*math.sin(a);beam('ChairStar',(0,.15,0),(x,.10,z),.045,'Steel');cyl('Caster',(x,.06,z),.06,.055,'Rubber','x',12)
save('OfficeChair')
