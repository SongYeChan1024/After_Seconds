import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
def prop(n):save(n,'Props',True)
def chair(x,z,yaw=0):
 old=set(bpy.context.scene.objects)
 box('Seat',0,.46,0,.45,.075,.45,'Fabric',.025);box('Back',0,.78,-.205,.44,.52,.065,'Fabric',.02)
 for xx in [-.19,.19]:
  for zz in [-.18,.18]:cyl('ChairLeg',(xx,.015,zz),(xx,.43,zz),.017,'Steel',12)
 transform(set(bpy.context.scene.objects)-old,x,0,z,yaw)
reset()
for x in [-.50,.50]:
 for z in [-1.08,1.08]:box('BunkPost',x,1.17,z,.045,2.34,.045,'Steel',.006)
for y in [.40,1.54]:
 box('BedFrame',0,y,0,1.05,.09,2.2,'Steel',.01);box('Mattress',0,y+.105,0,.98,.15,2.07,'Paper',.04);box('Blanket',0,y+.189,.27,.95,.028,1.46,'Fabric',.012);box('Pillow',0,y+.245,-.72,.65,.13,.35,'Paper',.055)
 for z in [-1.08,1.08]:box('BedEnd',0,y+.27,z,1.04,.40,.035,'Coat',.008)
for x in [-.50,.50]:cyl('UpperSafetyRail',(x,1.97,-1.05),(x,1.97,.48),.019,'Steel',12)
for z in [.51,.95]:cyl('LadderRail',(.58,.04,z),(.58,2.03,z),.022,'Steel',12)
for y in [.28,.56,.84,1.12,1.4,1.68]:cyl('LadderRung',(.58,y,.51),(.58,y,.95),.018,'Steel',12)
box('PersonalBox',0,.14,.35,.74,.25,.60,'Warm',.014);pull(0,.14,.66,.22)
prop('StaffBunk')
reset();box('Worktop',0,.79,0,1.65,.065,.78,'Warm',.018)
for x in [-.69,.69]:
 for z in [-.29,.29]:box('DeskLeg',x,.38,z,.045,.76,.045,'Steel',.004)
box('Modesty',0,.55,-.31,1.4,.36,.028,'Coat',.006);display(-.22,1.16,-.19,.59,.34,1);monitor_stand(-.22,1.16,-.19,.59,.34,.823);keyboard(-.22,.845,.18)
box('MousePad',.20,.825,.18,.23,.006,.24,'Dark',.001);box('Mouse',.20,.847,.18,.062,.037,.10,'Coat',.016)
box('PC',.57,.34,-.04,.25,.59,.40,'Dark',.013);vent(.57,.42,.17,.18,.24)
box('Notebook',.52,.832,.05,.27,.016,.33,'Paper',.003)
cyl('Pen',(.40,.846,-.04),(.40,.846,.15),.006,'Teal',10)
cyl('Cup',(.54,.825,.28),(.54,.93,.28),.038,'Coat',24)
prop('ResearchDesk')
reset();box('DiningTop',0,.76,0,1.8,.065,.88,'Warm',.02)
for x in [-.72,.72]:
 for z in [-.30,.30]:box('TableLeg',x,.37,z,.05,.74,.05,'Steel',.004)
for x in [-.5,.5]:
 for z in [-.83,.83]:chair(x,z,0 if z<0 else 180)
for x in [-.50,.50]:
 for z in [-.20,.20]:
  box('Tray',x,.804,z,.38,.018,.27,'Steel',.009);cyl('Plate',(x,.815,z),(x,.83,z),.095,'Paper',32);cyl('Cup',(x+.23,.795,z),(x+.23,.895,z),.033,'Coat',24)
prop('DiningSet')
reset();box('SofaBase',0,.23,0,2,.34,.85,'Warm',.04);box('Backrest',0,.68,-.37,1.95,.62,.20,'Fabric',.05)
for x in [-.92,.92]:box('Armrest',x,.52,0,.20,.36,.85,'Fabric',.04)
for x in [-.56,0,.56]:box('Cushion',x,.46,.04,.53,.18,.64,'Fabric',.055)
for x in [-.78,.78]:
 for z in [-.28,.28]:box('SofaFoot',x,.04,z,.055,.08,.055,'Steel',.006)
prop('LoungeSofa')
reset();cabinet(2.7,.88,.85,'doors','Coat');box('ServingCounter',0,.94,0,2.78,.07,.91,'Steel',.014)
for x in [-.85,0,.85]:
 box('FoodWell',x,.985,0,.68,.02,.56,'Dark',.012);box('ServingPan',x,1.01,0,.60,.055,.48,'Steel',.014)
 for z in [-.16,0,.16]:box('CoveredMeal',x,1.048,z,.48,.025,.12,'Warm',.01)
for x in [-1.25,1.25]:cyl('ShieldPost',(x,.98,-.30),(x,1.57,-.30),.022,'Steel',16)
box('SneezeShield',0,1.55,-.10,2.62,.025,.62,'Glass',.004)
prop('ServingCounter')
reset();cabinet(.70,.86,.69,'doors','Coat')
cyl('DoorOuter',(0,.46,.365),(0,.46,.40),.258,'Steel',48);cyl('DoorSeal',(0,.46,.405),(0,.46,.43),.217,'Rubber',48);cyl('DrumWindow',(0,.46,.433),(0,.46,.442),.19,'Lens',48)
display(-.06,.77,.397,.26,.075,2);cyl('CycleDial',(.23,.77,.40),(.23,.77,.44),.043,'Steel',24)
prop('LaundryMachine')
reset()
for x in [-.70,.70]:box('CubicleWall',x,1.1,0,.045,2.2,1.55,'Coat',.006)
box('BackWall',0,1.1,-.75,1.43,2.2,.045,'Coat',.006);box('Door',-.31,1.05,.75,.72,2.1,.035,'Coat',.007);pull(-.10,1.05,.78,.045)
box('Cistern',0,.73,-.50,.40,.55,.22,'Paper',.04);box('BowlPedestal',0,.25,-.18,.31,.45,.44,'Paper',.05);box('ClosedToiletSeat',0,.48,-.15,.42,.06,.59,'Paper',.05)
prop('SanitaryCubicle')
reset()
for x in [-.67,.67]:box('ShowerSide',x,1.1,0,.045,2.2,1.4,'Coat',.006)
box('ShowerBack',0,1.1,-.67,1.36,2.2,.045,'Coat',.006);box('ShowerTray',0,.035,0,1.28,.07,1.32,'Paper',.018);box('Drain',.3,.074,-.30,.14,.008,.14,'Steel',.001)
cyl('ShowerRiser',(.2,.95,-.61),(.2,2,-.61),.017,'Steel',16);cyl('ShowerArm',(.2,2,-.61),(.2,2,-.27),.017,'Steel',16);cyl('ShowerHead',(.2,1.98,-.25),(.2,2,-.25),.09,'Steel',32)
cyl('CurtainRod',(-.64,2.12,.57),(.64,2.12,.57),.018,'Steel',16)
for i in range(11):box('CurtainFold',-.6+i*.06,1.23,.56+(i%2)*.018,.063,1.69,.018,'Fabric',.006)
prop('ShowerCubicle')
reset();box('TargetBase',0,.075,0,2.9,.15,1.3,'Steel',.02)
for x in [-1.27,1.27]:box('TargetUpright',x,1.65,-.32,.11,3.3,.11,'Steel',.01)
for y in [.70,1.6,2.6]:
 cyl('TargetRail',(-1.3,y,-.30),(1.3,y,-.30),.035,'Steel',24)
 for i,x in enumerate([-.78,0,.78]):
  xx=x+(.14 if y==1.6 else 0);cyl('TargetDisc',(xx,y,-.22),(xx,y,-.13),.23,'Coat',48);cyl('TargetRing',(xx,y,-.128),(xx,y,-.12),.16,'Dark',48);cyl('TargetCenter',(xx,y,-.117),(xx,y,-.11),.065,'Warm',32)
box('TimingHeader',0,3.12,-.28,2.42,.37,.18,'Dark',.015);display(0,3.12,-.17,1.8,.23,3)
prop('TrialTargetRail')
reset();box('InstrumentBase',0,.07,0,2.0,.14,2.0,'Steel',.018)
for x in [-.88,.88]:
 for z in [-.88,.88]:
  box('Tower',x,1.38,z,.10,2.76,.10,'Coat',.009)
  for y in [1.0,1.85,2.55]:
   cyl('Sensor', (x,y,z),(x*.91,y,z*.91),.075,'Dark',24);cyl('Lens',(x*.9,y,z*.9),(x*.88,y,z*.88),.055,'Lens',24)
for x in [-.88,.88]:cyl('OverheadLink',(x,2.76,-.88),(x,2.76,.88),.04,'Steel',24)
for z in [-.88,.88]:cyl('OverheadLink',(-.88,2.76,z),(.88,2.76,z),.04,'Steel',24)
box('StandingPad',0,.155,0,.76,.03,.90,'Rubber',.014)
prop('PredictiveSensorFrame')
reset();box('CartridgeTray',0,.025,0,.42,.05,.30,'Steel',.008)
for i in range(4):
 x=-.145+i*.097;cyl('Cartridge',(x,.05,0),(x,.19,0),.032,'Coat',24);cyl('CartridgeCap',(x,.19,0),(x,.212,0),.036,'Teal',24)
prop('ExperimentCartridges')
reset();box('Recorder',0,.028,0,.10,.056,.19,'Dark',.009);box('RecorderScreen',0,.059,-.03,.069,.006,.068,'Lens',.002)
for x in [-.026,0,.026]:cyl('Key',(x,.058,.048),(x,.064,.048),.008,'Coat',12)
for i in range(6):box('SpeakerSlot',-.031+i*.012,.058,-.075,.004,.005,.025,'Steel',.001)
prop('HandheldRecorder')
print('B1 PROPS COMPLETE',flush=True)
