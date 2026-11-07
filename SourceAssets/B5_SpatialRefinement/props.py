"""Manufactured details and functional equipment, preserving the earlier originals. Author 송예찬."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
plan=json.loads((H/'plan.json').read_text(encoding='utf-8'))
sources={p['model']:R/'SourceAssets/B5_RemainingDomes'/('RD_'+p['model'][3:]+'.blend') for p in plan['placements']}
sources['SF_TaskChair']=R/'SourceAssets/C02_Security/SC_TaskChair.blend';sources['SF_BriefingTable']=None
for folder,prefix in [('C02_Security','SC_'),('C02_SecurityRefine','SR_')]:
 for p in (R/'SourceAssets'/folder).glob(prefix+'*.blend'):
  if any(x in p.stem for x in ['C02_','TaskChair','WallServices','NorthAirReturn']):continue
  sources['SF_'+p.stem]=p
indices={n:i for i,n in enumerate(sorted(sources))};(H/'prop_sources.json').write_text(json.dumps({n:dict(source=str(p) if p else None,label=indices[n]) for n,p in sources.items()},indent=2),encoding='utf-8')
def bounds(o):
 vs=[o.matrix_world@Vector(p) for p in o.bound_box];v=[(-p.x,p.z,-p.y) for p in vs];return [min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]
def gauge(x,y,z):
 cyl('Gauge_Body',(x,y,z-.035),(x,y,z),.085,'Steel',32);cyl('Dial_Face',(x,y,z),(x,y,z+.003),.072,'Paper',32)
 for i in range(17):
  a=math.radians(-135+i*270/16);cyl('Dial_Tick',(x+.060*math.sin(a),y+.060*math.cos(a),z+.005),(x+.050*math.sin(a),y+.050*math.cos(a),z+.005),.0014,'Dark',6)
 cyl('Gauge_Pointer',(x,y,z+.006),(x+.035,y+.037,z+.006),.0022,'Red',6);cyl('Dial_Hub',(x,y,z+.005),(x,y,z+.012),.007,'Steel',12)
def fasteners():
 for o in list(bpy.context.scene.objects):
  if o.type!='MESH':continue
  lo,hi=bounds(o);w=hi[0]-lo[0];h=hi[1]-lo[1];d=hi[2]-lo[2]
  if o.name.startswith(('Access_Panel','Door_Face','Drawer_Face','Rack_Unit','Rear_Service_Cover')) and w>.25 and h>.12:
   for x in [lo[0]+.025,hi[0]-.025]:
    for y in [lo[1]+.025,hi[1]-.025]:
     cyl('Flush_Torx_Screw',(x,y,hi[2]+.0006),(x,y,hi[2]+.003),.005,'Steel',10);box('Screw_Drive',x,y,hi[2]+.0032,.005,.001,.001,'Dark',0)
  if o.name.startswith(('Sealed_Crate','Organiser_Bin','PPE_Dispenser','Cabinet_Body')) and w>.3:
   # Folded edging is integral, no thick cubes standing in for labels.
   for x in [lo[0]+.012,hi[0]-.012]:box('Formed_Edge_Seam',x,(lo[1]+hi[1])/2,hi[2]+.001,.004,h*.86,.003,'Steel',.001)
def prints(index):
 choices=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(('Door_Face','Drawer_Face','Access_Panel','Sealed_Crate','Organiser_Bin','PPE_Dispenser','Endboard_Inset','Cabinet_Body','Wash_Door','Display_Back','Boot_Rack_Base','Ballasted_Base','Test_Platform'))]
 count=0
 for o in choices:
  lo,hi=bounds(o);w=hi[0]-lo[0];h=hi[1]-lo[1]
  if w<.20 or h<.10:continue
  ww=min(.24,w*.55);hh=min(.095,h*.34);label((lo[0]+hi[0])/2,lo[1]+h*.28,hi[2]+.0008,ww,hh,index);count+=1
  if count>=6:break
def bed_detail(med):
 for x in [-.51,.51]:
  for z in [-.88,.88]:
   cyl('Castor_Bearing',(x-.01,.16,z),(x+.07,.16,z),.038,'Steel',16);box('Foot_Brake',x,.115,z+.08,.095,.025,.13,'Red' if med else 'Teal',.009)
  tube('Mattress_Stitch',[(x*.88,.77,-.96),(x*.88,.77,.96)],.002,'Paper')
  for z in [-.64,.64]:cyl('Rail_Pivot',(x-.025,.65,z),(x+.025,.65,z),.032,'Steel',16)
 for z in [-.68,.68]:
  tube('Hydraulic_Line',[(0,.3,z),(.25,.3,z),(.25,.50,z+.12)],.008,'Dark');cyl('Actuator_Sleeve',(0,.32,z),(0,.49,z),.073,'Dark',20)
 vs=[];nx=18;nz=12
 for j in range(nz+1):
  for i in range(nx+1):
   x=-.445+.89*i/nx;z=.10+.70*j/nz;y=.880+.010*math.sin(i*.63+j*.47)+.005*math.sin(j*1.8);vs.append((x,y,z))
 fs=[(j*(nx+1)+i,j*(nx+1)+i+1,(j+1)*(nx+1)+i+1,(j+1)*(nx+1)+i) for j in range(nz) for i in range(nx)];o=mesh('Draped_Blanket_Surface',vs,fs,'Fabric',0,True);o.modifiers.new('Textile_Thickness','SOLIDIFY').thickness=.025
 box('Patient_Remote',.43,.9,-.55,.10,.035,.19,'Coat',.013)
 for z in [-.60,-.55,-.50]:box('Remote_Key',.43,.922,z,.055,.009,.026,'Teal',.006)
 tube('Remote_Cord',[(.43,.89,-.47),(.58,.77,-.4),(.59,.47,-.3),(.40,.35,-.40)],.005,'Dark')
def desk_detail():
 for o in list(bpy.context.scene.objects):
  if o.name.startswith(('Worktop','Sealed_Top','Instrument_Tray')):
   lo,hi=bounds(o);cx=(lo[0]+hi[0])/2;z=lo[2]+.10;y=lo[1]-.055;w=min(hi[0]-lo[0]-.10,1.8)
   box('Underdesk_Cable_Channel',cx,y,z,w,.10,.12,'Dark',.012)
   for x in [cx-w*.38,cx+w*.38]:box('Cable_Entry_Grommet',x,hi[1]+.001,z,.072,.004,.060,'Rubber',.012)
   break
 for o in list(bpy.context.scene.objects):
  if o.name.startswith('Display_Back'):
   lo,hi=bounds(o);x=(lo[0]+hi[0])/2;y=lo[1]+.08;z=lo[2]-.008
   for dx in [-.045,.015]:box('USB_Data_Port',x+dx,y,z,.042,.014,.012,'Dark',.003)
   tube('Strain_Relief_Cable',[(x+.06,y,z),(x+.06,y-.10,z-.04),(x-.08,max(.65,y-.4),z-.06)],.005,'Dark')
def pump_detail():
 for x in [-.46,.46]:
  flange(x,.48,.32,.14);box('Motor_Terminal_Box',x,.71,-.19,.18,.15,.18,'Teal',.018)
  for z in [-.36,.06]:box('Elastomer_Mount',x,.20,z,.34,.04,.13,'Rubber',.012)
  gauge(x,.65,.47);tube('Impulse_Line',[(x,.61,.44),(x,.49,.44),(x,.49,.31)],.009,'Steel')
 tube('Bonding_Lead',[(-.45,.22,-.18),(-.2,.16,-.3),(.45,.22,-.18)],.006,'Indicator')
def pressure_detail():
 gauge(.05,1.7,.67);wheel(.12,.48,.91,.105)
 for y in [.35,1.15,2.2]:
  for x in [-.40,.40]:bolt(x,y,.49)
def power_detail():
 for x in [-.2,0,.2]:
  box('Moulded_Breaker',x,.54,.40,.14,.20,.075,'Dark',.012);box('Toggle_Lever',x,.55,.45,.045,.08,.027,'Coat',.008)
 for y in [.34,1.8]:
  for x in [-.4,.4]:bolt(x,y,.38)
def sink_detail(single):
 names=('Basin','Basin_Recess','Basin_Interior','Basin_Base')
 for o in list(bpy.data.objects):
  if any(o.name==n or o.name.startswith(n+'.') for n in names):bpy.data.objects.remove(o,do_unlink=True)
 xs=[0] if single else[-.46,.46];top=.84 if single else .94
 for x in xs:
  # Open concave spun bowl with a real recessed interior.
  profiles=[(.29,top),(.27,top-.01),(.24,top-.17),(.17,top-.23),(.035,top-.25)];vs=[]
  for r,y in profiles:
   for i in range(48):a=i*math.tau/48;vs.append((x+r*math.cos(a),y,r*.84*math.sin(a)))
  fs=[]
  for j in range(len(profiles)-1):
   for i in range(48):fs.append((j*48+i,j*48+(i+1)%48,(j+1)*48+(i+1)%48,(j+1)*48+i))
  o=mesh('Deep_Stainless_Bowl',vs,fs,'Steel',0,True);o.modifiers.new('Bowl_Wall','SOLIDIFY').thickness=.003
  bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.272,depth=.35,location=xyz(x,top-.1,0));cut=bpy.context.object;cut.scale.y=.84
  for body in [o for o in bpy.context.scene.objects if o.name.startswith(('Cabinet_Body','Sealed_Top','Sink_Deck'))]:
   bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Basin_Cutout','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name)
  bpy.data.objects.remove(cut,do_unlink=True)
  cyl('Drain_Outlet',(x,top-.255,0),(x,top-.248,0),.031,'Dark',24)
  tube('Bottle_Trap',[(x,top-.26,0),(x,top-.42,0),(x+.14,top-.42,0),(x+.14,top-.30,-.25)],.024,'Steel')
  cyl('Tap_Lever',(x+.06,top+.07,-.18),(x+.13,top+.07,-.18),.014,'Steel',12)
def rack_detail():
 for o in list(bpy.context.scene.objects):
  if o.name.startswith(('Folded_Shelf','Shelf','Rack_Unit')):
   lo,hi=bounds(o);y=(lo[1]+hi[1])/2
   for x in [lo[0]+.035,hi[0]-.035]:box('Folded_Gusset',x,y-.045,hi[2]-.06,.035,.08,.10,'Steel',.008)
 for o in list(bpy.context.scene.objects):
  if o.name.startswith('Sealed_Crate'):
   lo,hi=bounds(o);x=(lo[0]+hi[0])/2;y=hi[1]-.1;z=hi[2]+.012
   tube('Recessed_Case_Handle',[(x-.12,y,z),(x-.12,y+.04,z+.025),(x+.12,y+.04,z+.025),(x+.12,y,z)],.009,'Steel')
def shower_detail():
 for x in [-.48,.48]:
  for y in [.58,1.48]:
   cyl('Body_Spray_Nozzle',(x,y,-.69),(x,y,-.62),.035,'Steel',16)
   for dx in [-.012,0,.012]:cyl('Jet_Perforation',(x+dx,y,-.619),(x+dx,y,-.615),.002,'Dark',8)
 tube('Hand_Spray_Hose',[(.36,1.1,-.61),(.40,.45,-.58),(.50,.40,-.57),(.58,1.5,-.59)],.013,'Dark');box('Shower_Sensor',-.37,1.7,-.69,.13,.16,.045,'Dark',.017)
def food_detail():
 # Thin folded pans with hollow interiors rather than solid cubes.
 for x in [-.48,.48]:
  y=1.0;z=.08
  box('Tray_Base',x,y,z,.37,.015,.42,'Steel',.008)
  for xx in [x-.185,x+.185]:box('Tray_Fold',xx,y+.035,z,.012,.07,.42,'Steel',.004)
  for zz in [z-.21,z+.21]:box('Tray_Fold',x,y+.035,zz,.37,.07,.012,'Steel',.004)
def test_detail():
 for x in [-1.1,1.1]:
  for z in [-1.1,1.1]:
   for dx in [-.09,.09]:
    for dz in [-.09,.09]:cyl('Foundation_Bolt',(x+dx,.34,z+dz),(x+dx,.37,z+dz),.012,'Steel',6)
   tube('Armoured_Sensor_Conduit',[(x,.4,z),(x,3.35,z),(x,3.35,0)],.019,'Dark')
 for x in [-1.1,1.1]:
  for y in [.9,2.0]:cyl('Optical_Lens_Barrel',(x,y,.16),(x,y,.21),.065,'Steel',24);cyl('Optical_Lens',(x,y,.211),(x,y,.214),.051,'Glass',24)
def chair_detail():
 # Mechanical controls remain below the cushion and inside the existing footprint.
 tube('Seat_Adjustment_Lever',[(.20,.45,0),(.29,.45,.12)],.008,'Steel');box('Lever_Grip',.29,.45,.16,.035,.027,.09,'Dark',.01)
 cyl('Gas_Lift_Collar',(0,.23,0),(0,.32,0),.049,'Steel',20)
def briefing():
 reset();box('Conference_Surface',0,.77,0,1.8,.07,1.3,'Blue',.045)
 for x in [-.65,.65]:box('Trestle_Foot',x,.04,0,.14,.08,.95,'Steel',.02);box('Table_Column',x,.4,0,.07,.70,.07,'Steel',.015)
 b.display(0,1.07,-.32,.65,.35,11);b.monitor_stand(0,1.07,-.32,.65,.35,.82)
 for x in [-.55,.55]:box('Review_File',x,.814,.20,.31,.018,.43,'Paper',.004);b.vessel(x,.81,-.15,.04,.10,'Coat')
import os
processed=0
for n,source in sources.items():
 if os.getenv('SF_MODELS') and n not in os.getenv('SF_MODELS').split(','):continue
 processed+=1
 if source:load(source)
 else:briefing()
 key=n.replace('SF_','')
 if 'Bed' in key:bed_detail('Medical' in key)
 if any(x in key for x in ['Desk','Console','Station','Review','Cart','Table']):desk_detail()
 if key=='TwinCoolingPump':pump_detail()
 if key=='ExpansionVessel':pressure_detail()
 if key in ['ElectricalSwitchgear','ProcessControlBay']:power_detail()
 if key in ['SanitaryBasin','DoubleWashSink']:sink_detail(key=='SanitaryBasin')
 if any(x in key for x in ['Rack','Storage','Crate','Dispenser','Archive','Locker']):rack_detail()
 if key=='DeconShower':shower_detail()
 if key in ['MealPreparation','MealAssemblyIsland']:food_detail()
 if key=='TestGantry':test_detail()
 if key=='TaskChair':chair_detail()
 if key=='CompactToilet':
  tube('Flush_Supply',[(0,.28,-.28),(0,.65,-.28),(0,.65,-.39)],.018,'Steel');cyl('Flush_Valve',(0,.60,-.25),(0,.68,-.25),.041,'Steel',20)
  for x in [-.14,.14]:cyl('Seat_Hinge',(x-.03,.43,-.15),(x+.03,.43,-.15),.023,'Steel',16)
 if key in ['PlateHeatExchanger','ValveManifold']:
  for x in [-.3,.3]:gauge(x,1.15,.53);wheel(x,.68,.54,.09)
 fasteners();prints(indices[n]);save(n,'Props')
print('DETAILED',processed,'models',flush=True)
