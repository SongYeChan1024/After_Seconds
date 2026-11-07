"""Connected equipment bays and room-specific working islands. Author 송예찬."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build import *
import build
build.manifest.update(json.loads((H/'models.json').read_text(encoding='utf-8')))
def table(w=2.7,d=1.35):
 feet(w,d)
 for x in [-w/2+.10,w/2-.10]:
  for z in [-d/2+.10,d/2-.10]:box('Table_Leg',x,.44,z,.055,.65,.055,'Steel',.009)
 box('Lower_Shelf',0,.26,0,w-.13,.035,d-.13,'Steel',.007);box('Worktop',0,.90,0,w,.065,d,'Coat',.022)
def receiving():
 table()
 for j in range(2):
  for i in range(4):
   x=-.98+i*.54;z=-.33+j*.62;box('Receiving_Tote',x,1.04,z,.48,.21,.50,'Teal',.016);box('Tote_Rim',x,1.15,z,.50,.025,.52,'Steel',.005)
   for k in range(3):box('Sealed_Linen_Pack',x,1.18+k*.041,z,.42,.038,.44,'Paper',.012)
 box('Scanner_Base',1.04,1.0,.39,.18,.11,.16,'Dark',.013);tube('Scanner_Stand',[(1.04,1.03,.39),(1.04,1.30,.39),(.95,1.38,.39)],.021,'Dark');display(.75,1.45,-.47,.62,.38,8);box('Terminal_Stand',.75,1.15,-.55,.045,.48,.05,'Steel',.009)
def meal_island():
 table(3.1,1.4)
 for x in [-1.1,-.4,.4,1.1]:
  box('Serving_Tray',x,.95,0,.56,.035,.58,'Steel',.012)
  for z in [-.14,.14]:box('Compartment',x,.978,z,.48,.018,.22,'Coat',.016)
  cyl('Cup',(x,1.0,.43),(x,1.10,.43),.055,'Coat',24)
 for x in [-1.45,1.45]:cyl('OverShelf_Post',(x,.94,-.57),(x,1.70,-.57),.022,'Steel',16)
 box('Over_Shelf',0,1.66,-.47,3.05,.04,.45,'Steel',.012)
 for x in [-1.1,-.7,-.3,.1,.5,.9]:vessel(x,1.69,-.47,.10,.22,'Coat')
def transfer_desk():
 table(2.4,1.1);display(-.65,1.32,-.29,.70,.42,1);monitor_stand(-.65,1.32,-.29,.70,.42,.933);keyboard(-.65,.96,.20);phone(.75,.935,.16)
 for x in [.0,.28,.56]:box('Clip_Record',x,.94,-.1,.24,.006,.34,'Paper',.001);box('Document_Clip',x,.946,-.23,.11,.006,.02,'Steel',.001)
def decon_bench():
 for x in [-1.15,1.15]:box('Bench_Support',x,.22,0,.13,.44,.69,'Steel',.014)
 for i in range(7):box('Clean_Seat_Slat',0,.45,-.31+i*.103,2.6,.055,.078,'Coat',.013)
 box('Zone_Divider',0,.14,0,2.65,.20,.03,'Teal',.007)
 for x in [-.95,-.48,0,.48,.95]:box('Shoe_Cubby',x,.16,0,.42,.02,.60,'Steel',.004)
def instrumentpanel():
 feet(2.0,.60);box('Process_Control_Body',0,1.25,0,2,2.22,.52,'Coat',.024)
 for x,k in [(-.52,5),(.52,7)]:
  display(x,1.64,.29,.80,.48,k);box('Panel_Lid_Seam',x,.79,.275,.91,.69,.022,'Dark',.006);box('Panel_Lid',x,.79,.296,.87,.65,.023,'Steel',.009)
  for dx in [-.29,.29]:
   cyl('Control_Knob',(x+dx,1.18,.29),(x+dx,1.18,.34),.042,'Dark',20);cyl('Status_Lamp',(x+dx,1.04,.29),(x+dx,1.04,.32),.020,'Indicator',16)
 for x in [-.8,-.4,0,.4,.8]:cyl('Gland',(x,.10,-.17),(x,.19,-.17),.035,'Dark',16)
def manifolds():
 for x in [-1.2,1.2]:box('Manifold_Frame',x,1.28,-.20,.07,2.56,.07,'Steel',.01)
 for y in [.35,1.55,2.4]:box('Frame_Crossbar',0,y,-.20,2.48,.06,.06,'Steel',.009)
 for y in [.75,1.80]:
  cyl('Header',(-1.35,y,0),(1.35,y,0),.10,'Steel',32)
  for x in [-1,-.5,0,.5,1]:
   cyl('Valve_Branch',(x,y,0),(x,y+.32,0),.040,'Steel',20);cyl('Valve_Body',(x,y+.15,0),(x,y+.26,0),.075,'Teal',24);cyl('Valve_Stem',(x,y+.20,0),(x,y+.20,.13),.017,'Steel',12)
   # Machined wheel, spokes and mounted pressure gauge.
   pts=[(x+.10*math.cos(a*math.tau/24),y+.20+.10*math.sin(a*math.tau/24),.15) for a in range(25)];tube('Valve_Wheel',pts,.011,'Teal')
   for a in [0,math.pi/2]:cyl('Wheel_Spoke',(x-.09*math.cos(a),y+.20-.09*math.sin(a),.15),(x+.09*math.cos(a),y+.20+.09*math.sin(a),.15),.008,'Steel',8)
   cyl('Gauge_Back',(x,y+.40,0),(x,y+.40,.045),.065,'Steel',24);cyl('Gauge_Face',(x,y+.40,.046),(x,y+.40,.049),.055,'Paper',24);tube('Gauge_Needle',[(x,y+.40,.052),(x+.025,y+.43,.052)],.003,'Dark')
def filterbank():
 box('Filter_Plinth',0,.09,0,2.45,.18,.72,'Dark',.018)
 for i in range(3):
  x=(i-1)*.79;box('Filter_Case',x,1.16,0,.76,2.12,.66,'Coat',.022);box('Filter_Seal',x,1.2,.344,.65,1.85,.025,'Dark',.009)
  for j in range(25):box('Pleated_Filter',x-.28+j*.0233,1.2,.365,.011,1.69,.030,'Fabric',.002)
  for y in [.30,2.05]:box('Retaining_Clip',x,y,.39,.50,.06,.035,'Steel',.005)
def gasstation():
 box('Cylinder_Base',0,.06,0,1.4,.12,.72,'Steel',.02)
 for x in [-.40,.40]:
  cyl('Cylinder',(x,.13,0),(x,1.75,0),.23,'Teal',48);cyl('Shoulder',(x,1.73,0),(x,1.86,0),.17,'Steel',32);cyl('Bottle_Valve',(x,1.85,0),(x,2.03,0),.035,'Steel',20);tube('Regulator_Line',[(x,1.95,0),(x,2.12,.2),(0,2.12,.2)],.015,'Steel')
  for y in [.55,1.4]:tube('Cylinder_Retainer',[(x-.24,y,-.1),(x-.24,y,.20),(x+.24,y,.20),(x+.24,y,-.10)],.016,'Steel')
 box('Wall_Rack',0,1.12,-.31,1.38,2.12,.05,'Coat',.014)
def evidence():
 shelf(1.7,2.05,.75)
 for j,y in enumerate([.18,.65,1.12,1.59]):
  for i in range(3):
   x=(i-1)*.54;box('Archived_Case',x,y+.17,0,.48,.33,.62,'Dark',.024);box('Case_Lid',x,y+.34,0,.50,.032,.64,'Steel',.008);box('Security_Seal',x-.16,y+.23,.324,.025,.18,.002,'Hazard',0);pull(x,y+.15,.325,.19)
def wallbay():
 cabinet(2.35,.84,.60,'drawers');box('Installed_Backpanel',0,1.60,-.28,2.35,1.45,.06,'Coat',.015)
 for x in [-.82,.82]:box('Upper_Storage',x,1.75,-.06,.67,.99,.40,'Steel',.016);box('Upper_Door',x,1.75,.153,.62,.92,.027,'Coat',.009);pull(x,1.7,.177,.18)
 display(0,1.72,-.23,.65,.43,17)
 for x in [-.72,-.36,0,.36,.72]:vessel(x,.88,.09,.065,.23,'Coat')
for name,fn in {'ReceivingIsland':receiving,'MealAssemblyIsland':meal_island,'TransferNurseDesk':transfer_desk,'DeconChangeBench':decon_bench,'ProcessControlBay':instrumentpanel,'ValveManifold':manifolds,'FilterBank':filterbank,'MedicalGasStation':gasstation,'ArchiveCaseRack':evidence,'ServiceWorkBay':wallbay}.items():reset();fn();export(name)
# Connected cooling risers from each floor plant to the upper distribution ring.
data=json.loads((H/'plan.json').read_text(encoding='utf-8'));reset();rad=10
for p in data['placements']:
 if p['room']!='C03' or not any(k in p['model'] for k in ['Pump','Vessel','Exchanger']):continue
 x,y,z=p['position'];out=Vector((x,0,z)).normalized();side=Vector((out.z,0,-out.x));back=Vector((x,0,z))+out*.48
 for shift,mat in [(-.12,'Teal'),(.12,'Steel')]:
  p0=back+side*shift;p0.y=1.05;p1=out*8.95+side*shift;p1.y=1.05;p2=out*8.95+side*shift;p2.y=3.8;tube('Equipment_Header_Connection',[tuple(p0),tuple(p1),tuple(p2)],.075,mat)
  for yy in [1.3,2.5,3.5]:cyl('Riser_Clamp',tuple(out*8.95+side*shift+Vector((0,yy,0))),tuple(out*math.sqrt(100-yy*yy)+side*shift+Vector((0,yy,0))),.025,'Steel',12)
export('C03_ProcessConnections',True)
reset()
for xx in [-1.76,1.76]:
 for zz in [-3.08,3.08]:
  box('Structural_Column',xx,8,zz,.12,16,.12,'Steel',.006);box('Column_Base',xx,.04,zz,.28,.08,.28,'Steel',.008)
  for yy in range(2,17,2):box('Landing_Bracket',xx,yy-.12,zz,.24,.22,.22,'Steel',.006)
for x,z in [(0,4.55),(-4.55,0),(0,-4.55)]:
 cyl('Riser_Pipe',(x,.18,z),(x,18.6,z),.065,'Steel',20)
 for y in [.5,2.9,6.9,10.9,14.9,18.2]:
  out=Vector((x,0,z)).normalized();cyl('Wall_Support',(x,y,z),(out.x*4.99,y,out.z*4.99),.036,'Steel',12);cyl('Pipe_Collar',(x,y-.035,z),(x,y+.035,z),.083,'Steel',16)
for y in [3.65,7.65,11.65,15.65,18.6]:tube('Shaft_Ring',[(4.93*math.cos(i*math.tau/96),y,4.93*math.sin(i*math.tau/96)) for i in range(97)],.035,'Steel')
export('VB_Services',True)
reset()
for x,z in [(2.6,0),(0,-2.6),(-2.6,0),(0,2.6)]:
 box('Lamp_Housing',x,3.31,z,.82,.13,.24,'Steel',.012);box('Diffuser',x,3.232,z,.72,.025,.17,'Lamp',.008);cyl('Suspension',(x,3.38,z),(x,3.65,z),.02,'Steel',12);out=Vector((x,0,z)).normalized();cyl('Wall_Arm',(x,3.65,z),(out.x*4.99,3.65,out.z*4.99),.035,'Steel',12)
export('VL_Lighting',True)
print('COMPLETE DETAIL',flush=True)
