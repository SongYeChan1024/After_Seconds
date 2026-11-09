"""B4 repair assemblies; metres, front +Z. Author Song Ye Chan."""
import sys, math, json, importlib.util, os
from pathlib import Path
import bpy
H=Path(__file__).resolve().parent; R=H.parents[1]
spec=importlib.util.spec_from_file_location('ops',R/'SourceAssets/B4_ExperimentOperations/common.py'); c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
b=c.b;b.H=H;b.OUT=b.A/'Props/B4';b.manifest=json.loads((H/'models.json').read_text()) if (H/'models.json').exists() else {}
box=c.box;cyl=c.cyl;tube=c.tube
def reset():
 c.reset()
 for k in ['Coat','Steel','Red','Paper','Dark']:
  m=b.mats[k];m.name='BP_'+k
def save(n):
 if os.environ.get('POLISH_ONLY') and n!=os.environ['POLISH_ONLY']:return
 b.raw_export('BP_'+n)
 (H/'models.json').write_text(json.dumps(b.manifest,indent=2),encoding='utf8')
def bolt(x,y,z):cyl('Captive_Hex',(x,y,z),(x,y,z+.012),.012,'Steel',6)
def ring(n,x,y,z,rad,axis='z',th=.008,mat='Steel',count=40):
 pts=[]
 for i in range(count+1):
  a=math.tau*i/count
  pts.append((x+rad*math.cos(a),y+rad*math.sin(a),z) if axis=='z' else (x+rad*math.cos(a),y,z+rad*math.sin(a)))
 tube(n,pts,th,mat)
def mount(rad,x,y,face,width=.10,height=.12):
 # Wall is spherical except the cylindrical 5m stair core. Integral blocks
 # terminate 12mm into wall lining, closing the real curved wall contact.
 wall=math.sqrt(rad*rad-x*x-(0 if rad==5 else y*y))-.035
 z=face-wall
 box('Curved_Wall_Anchor',x,y,(z-.025)/2,width,height,-z+.025,'Steel',.004)
 box('Anchor_Plate',x,y,z+.012,width+.06,height+.05,.036,'Steel',.004)
 bolt(x,y,.01)
for rad in [5,6,7,8,9,10,12]:
 reset(); face=math.sqrt(rad*rad-(0 if rad==5 else 2.13**2))-.20
 box('Folded_Mount_Rail',0,1.19,.027,1.34,1.82,.054,'Steel',.009)
 for x in [-.58,.58]:
  for y in [.40,1.97]:mount(rad,x,y,face)
 # Hose cabinet has a folded return frame, recessed door, hinges and handle.
 box('Cabinet_Body',.25,1.25,.18,.76,1.18,.25,'Red',.018)
 box('Door_Gasket',.25,1.25,.311,.70,1.12,.018,'Rubber',.004)
 box('Recessed_Door',.25,1.25,.333,.66,1.08,.028,'Coat',.009)
 for x in [-.055,.555]:box('Door_Return',x,1.25,.354,.025,1.04,.035,'Steel',.003)
 for y in [.74,1.76]:box('Door_Return',.25,y,.354,.63,.025,.035,'Steel',.003)
 box('Inspection_Window',.25,1.35,.351,.48,.48,.012,'Dark',.003)
 for rr in [.17,.14,.11,.08]:ring('Reeled_Hose',.25,1.35,.368,rr,th=.012,mat='Warm')
 cyl('Reel_Spindle',(.25,1.35,.36),(.25,1.35,.40),.055,'Steel',20)
 for y in [.89,1.60]:cyl('Door_Hinge',(-.105,y-.05,.34),(-.105,y+.05,.34),.018,'Steel',12)
 tube('Pull_Handle',[(.50,1.10,.36),(.50,1.10,.41),(.50,1.32,.41),(.50,1.32,.36)],.012,'Steel')
 c.label(.25,.91,.353,.45,.11,42)
 # Extinguisher is strapped to a wall saddle, with rounded shoulders, gauge,
 # pin, handle, hose and nozzle. No floor plinth / no freestanding screen.
 x=-.47
 cyl('Pressure_Vessel',(x,.53,.235),(x,1.16,.235),.125,'Red',32)
 for yy,rr in [(.50,.095),(.515,.116),(1.17,.116),(1.19,.09),(1.21,.055)]:cyl('Rounded_Shoulder',(x,yy-.014,.235),(x,yy+.014,.235),rr,'Red',32)
 cyl('Valve_Body',(x,1.21,.235),(x,1.30,.235),.035,'Steel',16)
 box('Valve_Lever',x+.025,1.31,.235,.19,.025,.048,'Steel',.007)
 box('Trigger_Grip',x+.03,1.28,.235,.19,.018,.045,'Dark',.004)
 cyl('Gauge_Bezel',(x,1.235,.268),(x,1.235,.31),.043,'Steel',28)
 cyl('Gauge_Dial',(x,1.235,.31),(x,1.235,.313),.034,'Paper',28)
 tube('Gauge_Needle',[(x-.018,1.22,.315),(x+.016,1.25,.315)],.002,'Dark')
 ring('Safety_Pin',x-.09,1.29,.235,.032,th=.003)
 tube('Pressure_Hose',[(x+.02,1.265,.235),(x+.15,1.26,.24),(x+.18,1.16,.25),(x+.18,.73,.26),(x+.14,.68,.28)],.014,'Dark')
 cyl('Hose_Nozzle',(x+.14,.68,.28),(x+.12,.58,.28),.024,'Dark',16)
 for yy in [.64,1.04]:
  box('Wall_Saddle',x,yy,.11,.24,.06,.18,'Steel',.009)
  ring('Retaining_Strap',x,yy,.235,.132,axis='y',th=.009)
 box('Lower_Cradle',x,.48,.23,.27,.035,.28,'Steel',.007)
 c.label(x,.83,.362,.15,.15,42)
 save('WallSafety_R'+str(rad))
 # Overhead service section gives the upper wall a functional second layer.
 reset();face=math.sqrt(rad*rad-(0 if rad==5 else 3.30**2))-.22
 box('Power_Distribution',-.45,2.91,.08,.56,.64,.16,'Coat',.012)
 box('Panel_Gasket',-.45,2.91,.166,.50,.58,.018,'Dark',.003)
 box('Panel_Lid',-.45,2.91,.182,.47,.55,.018,'Steel',.005)
 c.label(-.45,3.05,.194,.29,.055,41)
 for y in [2.69,3.12]:bolt(-.62,y,.195);bolt(-.28,y,.195)
 for x in [-.65,.65]:mount(rad,x,2.74,face);mount(rad,x,3.18,face)
 for y in [2.56,2.48]:
  tube('Formed_Service_Conduit',[(-1.05,y,.04),(.65,y,.04),(.81,y+.16,.04),(.81,3.18,.04)],.022,'Steel')
  for x in [-.90,0,.55]:box('Conduit_Strap',x,y,.045,.045,.09,.07,'Steel',.004)
 box('Data_Patch_Box',.18,2.96,.09,.40,.33,.18,'Coat',.008)
 for i in range(4):
  xx=.06+i*.075;box('Data_Port',xx,2.96,.187,.05,.06,.018,'Dark',.003)
  tube('Patch_Cable',[(xx,2.95,.21),(xx,2.70,.24),(xx+.25,2.66,.20),(xx+.25,3.20,.07)],.006,'Dark')
 save('WallServices_R'+str(rad))
for variant in range(3):
 reset()
 # Small surface kits fit into free bench ends, all bases at y=0.
 if variant==0:
  box('Instrument_Case',0,.075,0,.34,.15,.27,'Coat',.015)
  box('Lid_Seam',0,.115,0,.35,.008,.28,'Dark',.002)
  for x in [-.11,.11]:box('Case_Latch',x,.09,.145,.035,.055,.020,'Steel',.003)
  tube('Folding_Handle',[(-.07,.15,-.02),(-.07,.20,-.02),(.07,.20,-.02),(.07,.15,-.02)],.008,'Dark')
  for x in [-.13,.13]:
   for z in [-.09,.09]:box('Case_Foot',x,.01,z,.035,.02,.035,'Rubber',.003)
  c.label(0,.073,.151,.21,.045,41)
 elif variant==1:
  box('Parts_Tray',0,.017,0,.38,.034,.28,'Steel',.006)
  for x in [-.18,.18]:box('Raised_Tray_Rim',x,.035,0,.014,.05,.28,'Steel',.003)
  for z in [-.13,.13]:box('Raised_Tray_Rim',0,.035,z,.36,.05,.014,'Steel',.003)
  for i in range(3):
   x=-.11+i*.11;cyl('Sensor_Pod',(x,.04,-.02),(x,.085,-.02),.037,'Coat',20);cyl('Optical_Lens',(x,.085,-.02),(x,.09,-.02),.022,'Lens',20)
  tube('Probe_Lead',[(-.1,.05,.08),(.09,.05,.08),(.14,.06,.03),(.10,.06,-.07)],.004,'Dark')
 else:
  box('Clipboard',0,.012,0,.27,.024,.34,'Dark',.004)
  for i in range(4):box('Protocol_Paper',.003*i,.027+i*.0015,-.005*i,.24,.001,.30,'Paper',0)
  for i in range(7):box('Printed_Protocol_Row',-.015,.034,-.10+i*.026,.17-(i%3)*.025,.001,.005,'Mark',0)
  box('Binder_Clip',0,.037,-.15,.08,.02,.035,'Steel',.003)
  cyl('Pen',(.10,.043,-.1),(.10,.043,.09),.005,'Steel',12)
 save('BenchKit_'+str(variant+1))
reset();c.cartbase(1.16,.70)
for y in [.29,.64,.96]:
 box('Shelf_Tray',0,y,0,1.1,.04,.68,'Steel',.007)
 for z in [-.32,.32]:box('Folded_Tray_Rim',0,y+.035,z,1.08,.06,.025,'Steel',.004)
for x in [-.51,.51]:tube('Frame_And_Push_Handle',[(x,.18,-.27),(x,1.16,-.27),(x,1.16,.27),(x,.18,.27)],.022,'Steel')
for x in [-.30,.25]:c.case(x,.33,0,.44,.23,.49)
box('Signal_Analyzer',0,1.08,-.05,.65,.20,.40,'Coat',.014);c.screen(-.12,1.08,.156,.27,.11,33);c.knob(.22,1.08,.16,.022)
for x in [-.3,0,.3]:cyl('Cable_Spool',(x,.69,0),(x,.84,0),.105,'Dark',24)
tube('Test_Lead',[(-.25,1.01,.2),(-.42,1.0,.22),(-.45,.80,.25),(-.3,.76,.2)],.009,'Dark')
save('InstrumentTrolley')
reset()
# Open instrument-return rack: staggered labelled cases, spare sensors and cables.
for x in [-.68,.68]:
 for z in [-.27,.27]:box('Rack_Post',x,1.15,z,.045,2.28,.045,'Steel',.004);box('Adjustable_Foot',x,.035,z,.11,.07,.11,'Dark',.006)
for y in [.18,.69,1.20,1.71,2.22]:
 box('Reinforced_Shelf',0,y,0,1.40,.045,.64,'Steel',.007)
 box('Label_Front_Rail',0,y+.025,.32,1.4,.07,.025,'Coat',.003)
 c.label(-.45,y+.025,.335,.26,.04,41)
for yy in [.22,.73,1.24]:
 for x,w in [(-.40,.42),(.18,.60)]:c.case(x,yy,-.01,w,.28,.45)
for x in [-.44,0,.40]:
 cyl('Spare_Sensor_Housing',(x,1.75,0),(x,1.90,0),.11,'Coat',24);cyl('Sensor_Lens',(x,1.90,0),(x,1.91,0),.055,'Lens',24)
save('ReturnRack')
print('POLISH_MODELS',len(b.manifest),sum(m['triangles'] for m in b.manifest.values()))
