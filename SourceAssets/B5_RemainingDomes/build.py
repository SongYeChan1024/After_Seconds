"""Purpose-built B5 furnishings. Metres, front +Z. Author 송예찬."""
import ast,bpy,bmesh,math,json,os
from pathlib import Path
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;R=H.parents[1];A=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model';manifest={}
for source in ['CircularDressing/build_environment.py','C02_Security/build.py']:
 tree=ast.parse((R/'SourceAssets'/source).read_text(encoding='utf-8'))
 funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name not in ['reset','export','desk']]
 exec(compile(ast.Module(body=funcs,type_ignores=[]),'helpers','exec'))
tree=ast.parse((R/'SourceAssets/CircularDressing/build_environment.py').read_text(encoding='utf-8'))
ex=ast.unparse(next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='export')).replace('obj.name = name','obj.name = name\n    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)').replace('for p in o.data.polygons:',"if o.get('display_uv'): continue\n        for p in o.data.polygons:")
exec(ex);raw_export=export
def export(name,env=False):
 global OUT;OUT=A/('Environment' if env else 'Props')/'B5';raw_export('RD_'+name);manifest['RD_'+name]['category']='Environment' if env else 'Props'
 (H/'models.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
def reset():
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;bpy.context.scene.unit_settings.system='METRIC';global mats;mats={}
 for n,c,metal,rough in [('Coat',(.65,.71,.72,1),.12,.48),('Steel',(.36,.43,.47,1),.8,.34),('Dark',(.026,.040,.05,1),.15,.52),('Rubber',(.016,.022,.025,1),0,.73),('Teal',(.08,.24,.26,1),.4,.4),('Fabric',(.38,.46,.47,1),0,.9),('Glass',(.08,.18,.20,.18),.15,.16),('Indicator',(.19,.67,.48,1),.1,.3),('Paper',(.74,.76,.70,1),0,.88),('Lamp',(.75,.85,.88,1),0,.2),('Floor',(.23,.28,.30,1),.02,.68),('Warm',(.55,.45,.29,1),.1,.58),('Red',(.47,.13,.10,1),.05,.6),('Hazard',(.77,.62,.21,1),.05,.6)]+[(f'Display_{i:02}',(.15,.35,.40,1),.05,.2) for i in range(1,19)]:
  m=bpy.data.materials.new('RD_'+n);m.diffuse_color=c;m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=c;p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;mats[n]=m
def wheels(w,d):
 for x in [-w/2+.08,w/2-.08]:
  for z in [-d/2+.08,d/2-.08]:
   cyl('Swivel',(x,.12,z),(x,.20,z),.024,'Steel',12);box('Castor_Fork',x,.09,z,.09,.10,.035,'Steel',.006);cyl('Tyre',(x-.045,.07,z),(x+.045,.07,z),.062,'Rubber',20);cyl('Axle',(x-.05,.07,z),(x+.05,.07,z),.014,'Steel',12)
def feet(w,d):
 for x in [-w/2+.09,w/2-.09]:
  for z in [-d/2+.09,d/2-.09]:
   cyl('Adjustable_Foot',(x,.025,z),(x,.18,z),.021,'Steel',12);cyl('Foot_Pad',(x,.012,z),(x,.037,z),.04,'Rubber',16)
def vent(x,y,z,w=.5,h=.23):
 box('Vent_Recess',x,y,z,w,h,.015,'Dark',.004)
 for j in range(6):box('Louver',x,y-h*.39+j*h*.155,z+.013,w-.03,.014,.027,'Steel',.003)
def cabinet(w=1.2,h=1.7,d=.65,style='doors',mat='Coat'):
 feet(w,d);box('Cabinet_Body',0,(h+.16)/2,0,w,h-.16,d,mat,.022);box('Toe_Recess',0,.13,.02,w-.08,.13,d-.06,'Dark',.008)
 box('Sealed_Top',0,h+.012,0,w+.025,.04,d+.035,'Steel',.009)
 if style=='drawers':
  for i in range(5):
   yy=.30+i*(h-.29)/5;box('Drawer_Gasket',0,yy,d/2+.006,w-.06,(h-.3)/5-.012,.022,'Dark',.005);box('Drawer_Face',0,yy,d/2+.025,w-.09,(h-.3)/5-.034,.027,mat,.007);pull(0,yy,d/2+.043,.25)
 else:
  for side in [-1,1]:
   x=side*w*.248;box('Door_Gasket',x,(h+.19)/2,d/2+.007,w*.49,h-.19,.022,'Dark',.009);box('Door_Face',x,(h+.20)/2,d/2+.027,w*.475,h-.24,.028,mat,.012);pull(side*.07,h*.55,d/2+.048,.065)
   for yy in [.32,h-.16]:box('Hinge',side*(w/2-.055),yy,d/2+.045,.042,.095,.027,'Steel',.006)
   vent(x,h-.25,d/2+.044,w*.33,.16)
def shelf(w=1.6,h=2.05,d=.58):
 for x in [-w/2,w/2]:
  for z in [-d/2,d/2]:box('Upright',x,h/2,z,.038,h,.038,'Steel',.006)
 for y in [.16,.63,1.10,1.57,2.04]:box('Folded_Shelf',0,y,0,w,.035,d,'Coat',.006);box('Shelf_Label_Rail',0,y+.025,d/2+.004,w,.035,.018,'Teal',.003)
 box('Back_Panel',0,h/2,-d/2-.018,w,h,.025,'Coat',.006)
def vessel(x,y,z,r=.12,h=.32,mat='Coat'):
 cyl('Container',(x,y+.02,z),(x,y+h-.04,z),r,mat,24);cyl('Shoulder',(x,y+h-.05,z),(x,y+h-.02,z),r*.9,mat,24);cyl('Cap',(x,y+h-.02,z),(x,y+h+.015,z),r*.69,'Teal',24)
 for i in range(12):
  a=i*math.tau/12;cyl('Cap_Grip',(x+r*.69*math.cos(a),y+h-.018,z+r*.69*math.sin(a)),(x+r*.69*math.cos(a),y+h+.01,z+r*.69*math.sin(a)),.003,'Teal',6)
def trolley(w=1,d=.6):
 wheels(w,d)
 for y in [.21,.72]:box('Cart_Shelf',0,y,0,w,.035,d,'Steel',.009)
 for x in [-w/2+.04,w/2-.04]:
  for z in [-d/2+.04,d/2-.04]:cyl('Cart_Post',(x,.18,z),(x,.96,z),.018,'Steel',12)
 for x in [-w/2+.04,w/2-.04]:tube('Push_Handle',[(x,.72,-d/2+.04),(x,1.,-d/2+.04),(x,1.,d/2-.04),(x,.72,d/2-.04)],.019,'Steel')
def bed(med=False):
 wheels(1.02,2.12);box('Bed_Underframe',0,.28,0,.91,.14,1.98,'Steel',.018)
 for z in [-.68,.68]:cyl('Lift_Column',(0,.29,z),(0,.55,z),.065,'Steel',20)
 box('Bed_Deck',0,.56,0,1.02,.10,2.12,'Coat',.035);box('Mattress_Piped_Edge',0,.64,0,.97,.08,2.03,'Dark',.03);box('Mattress',0,.73,0,.95,.14,2.01,'Fabric',.055)
 box('Pillow',0,.84,-.71,.70,.13,.39,'Paper',.058)
 for z in [-1.07,1.07]:box('Moulded_Endboard',0,.83,z,1.03,.58,.075,'Coat',.03);box('Endboard_Inset',0,.90,z+(.043 if z>0 else -.043),.75,.22,.012,'Teal',.025)
 box('Folded_Blanket',0,.831,.45,.89,.045,.7,'Teal' if med else 'Warm',.018)
 for side in [-1,1]:
  tube('Folding_SideRail',[(side*.53,.66,-.64),(side*.53,.99,-.64),(side*.53,.99,.64),(side*.53,.66,.64)],.021,'Steel')
  for z in [-.35,0,.35]:cyl('Guard_Rung',(side*.53,.66,z),(side*.53,.97,z),.015,'Steel',12)
 if med:
  tube('IV_Pole',[(.58,.24,-.78),(.58,1.96,-.78),(.40,1.96,-.78)],.016,'Steel');vessel(.40,1.54,-.78,.045,.25,'Glass');tube('IV_Tube',[(.40,1.55,-.78),(.39,1.18,-.72),(.31,.92,-.30)],.003,'Dark')
def monitor_cart(kind):
 wheels(.55,.55);box('Ballasted_Base',0,.19,0,.50,.08,.50,'Coat',.018);cyl('Lift_Pole',(0,.22,0),(0,1.22,0),.035,'Steel',20);box('Instrument_Tray',0,1.07,.08,.56,.04,.40,'Steel',.009);display(0,1.43,0,.56,.36,kind);box('Display_Attachment',0,1.28,-.13,.06,.28,.08,'Steel',.009)
 tube('Sensor_Cable',[(.2,1.28,-.12),(.25,.85,-.1),(.19,.73,-.12),(.15,1.04,.12)],.008,'Dark');box('Probe_Basket',0,.65,0,.35,.22,.25,'Teal',.01)
def apply_subset(name,fn):
 if os.environ.get('RD_ONLY') and name not in os.environ['RD_ONLY'].split(','):return
 reset();fn();export(name)
def living_desk():
 box('Worktop',0,.75,0,1.20,.06,.58,'Coat',.025)
 for x in [-.50,.50]:box('Cantilever',x,.37,-.05,.06,.69,.40,'Steel',.012)
 box('Paper_Journal',-.18,.786,.10,.24,.013,.29,'Paper',.003);box('Notebook_Binding',-.303,.787,.10,.012,.016,.29,'Dark',.002)
 vessel(.35,.785,.10,.041,.10,'Coat');box('Reading_Base',-.43,.80,-.17,.18,.025,.15,'Steel',.008);tube('Reading_Arm',[(-.43,.81,-.17),(-.43,1.21,-.17),(-.27,1.28,-.17)],.012,'Steel');box('Reading_Shade',-.24,1.27,-.17,.25,.055,.12,'Coat',.018);box('Reading_Diffuser',-.24,1.238,-.17,.21,.005,.09,'Lamp',.001)
def sanitary():
 cabinet(.77,.78,.50);cyl('Basin',(0,.79,0),(0,.83,0),.30,'Steel',48);cyl('Basin_Recess',(0,.826,0),(0,.832,0),.25,'Dark',48);cyl('Basin_Interior',(0,.833,0),(0,.836,0),.20,'Steel',48);tube('Faucet',[(0,.80,-.19),(0,1.08,-.19),(0,1.08,0),(0,1.03,0)],.016,'Steel');box('Splash_Back',0,1.09,-.28,.77,.58,.035,'Coat',.012);box('Mirror_Rim',0,1.55,-.265,.62,.57,.035,'Steel',.015);box('Mirror',0,1.55,-.244,.58,.53,.003,'Glass',0)
def cell_screen():
 for x in [-1.72,1.72]:
  box('Alcove_Side',x,1.20,-.30,.055,2.4,2.86,'Coat',.012)
  box('Side_Inset',x+(.031 if x<0 else -.031),1.32,-.40,.012,1.64,2.44,'Warm',.006)
 box('Service_Back',0,1.2,-1.75,3.49,2.4,.065,'Coat',.014);box('Head_Rail',0,1.03,-1.70,3.24,.16,.035,'Steel',.006)
 for x in [-1.74,1.74]:box('Front_Edge_Trim',x,1.2,1.15,.075,2.4,.09,'Steel',.009)
 box('Alcove_Header',0,2.4,-.3,3.55,.10,2.96,'Coat',.014)
 # Header is an open rectangular frame, not a low opaque ceiling.
 o=bpy.data.objects.get('Alcove_Header');bpy.data.objects.remove(o,do_unlink=True)
 for x in [-1.73,1.73]:box('Top_SideRail',x,2.40,-.30,.09,.11,2.98,'Steel',.01)
 box('Back_Exhaust',0,2.15,-1.70,1.2,.28,.10,'Dark',.012);vent(0,2.15,-1.64,1.12,.22)
 box('Call_Intercom',1.42,1.39,-1.68,.20,.35,.08,'Steel',.012);cyl('Call_Key',(1.42,1.30,-1.63),(1.42,1.30,-1.61),.031,'Indicator',20)
def linen():
 shelf()
 for j,y in enumerate([.18,.65,1.12,1.59]):
  for i in range(3):
   x=(i-1)*.48
   for k in range(3):box('Folded_Linen',x,y+.045+k*.072,0,.41,.068,.48,'Paper' if j%2==0 else 'Fabric',.020)
def hampers():
 trolley(.85,.65)
 for x,mat in [(-.21,'Fabric'),(.21,'Teal')]:
  box('Wash_Bag',x,.49,0,.38,.55,.52,mat,.055);box('Bag_Cuff',x,.77,0,.40,.07,.54,mat,.016);box('Closed_Lid',x,.81,0,.42,.035,.57,'Coat',.016);pull(x,.82,.29,.12)
def supply():
 shelf()
 for j,y in enumerate([.18,.65,1.12,1.59]):
  for i in range(4):
   x=(i-1.5)*.37;box('Organiser_Bin',x,y+.12,0,.32,.23,.46,'Teal' if j%2 else 'Coat',.018);box('Bin_Recess',x,y+.16,.24,.18,.06,.003,'Paper',0)
   for k in range(3):box('Sterile_Pack',x-.09+k*.09,y+.25,-.02,.075,.10,.30,'Paper',.006)
def passcart():
 trolley(1.2,.70)
 for j in range(5):
  y=.33+j*.14;box('Food_Tray',0,y,0,1.05,.025,.61,'Steel',.007)
  if j<4:
   for x in [-.32,.32]:box('Meal_Cover',x,y+.048,0,.46,.07,.47,'Coat',.025)
def privacy():
 for x in [-.8,.8]:
  box('Stabiliser',x,.045,0,.14,.09,.7,'Steel',.015);cyl('Curtain_Post',(x,.09,0),(x,2.10,0),.022,'Steel',16)
 cyl('Curtain_Rail',(-.8,2.1,0),(.8,2.1,0),.022,'Steel',16)
 vs=[];fs=[]
 for y in [.25,1.98]:
  for i in range(65):vs.append((-.76+1.52*i/64,y,.045*math.sin(i*math.pi/4)))
 for i in range(64):fs.append((i,i+1,66+i,65+i))
 ob=mesh('Pleated_Privacy_Fabric',vs,fs,'Fabric',0,True);sol=ob.modifiers.new('Textile_Thickness','SOLIDIFY');sol.thickness=.004
 for i in range(9):cyl('Curtain_Hanger',(-.75+i*.1875,1.97,0),(-.75+i*.1875,2.1,0),.006,'Steel',8)
def examlight():
 box('Lamp_Base',0,.08,0,.60,.16,.60,'Coat',.04);cyl('Upright',(0,.16,0),(0,1.6,0),.036,'Steel',16);tube('Articulated_Arm',[(0,1.55,0),(.1,1.95,0),(.62,2.13,0)],.033,'Coat');cyl('Lamp_Disc',(.62,2.06,0),(.62,2.14,0),.23,'Coat',40)
 for i in range(6):a=i*math.tau/6;cyl('Optical_Lens',(.62+.13*math.cos(a),2.045,.13*math.sin(a)),(.62+.13*math.cos(a),2.065,.13*math.sin(a)),.05,'Lamp',16)
def sterilizer():
 cabinet(1.1,.8,.66,'drawers');box('Sterilizer_Shell',0,1.10,0,1.0,.56,.61,'Coat',.035);box('Thermal_Gasket',-.17,1.10,.317,.55,.46,.025,'Rubber',.022);box('Autoclave_Door',-.17,1.10,.337,.49,.40,.035,'Steel',.025);pull(-.17,1.1,.36,.24);display(.32,1.21,.32,.20,.14,4);cyl('Dial',(.32,1.02,.33),(.32,1.02,.36),.045,'Dark',24)
def pump():
 box('Pump_Skid',0,.07,0,1.7,.14,1.12,'Steel',.02)
 for x in [-.46,.46]:
  cyl('Motor',(x,.48,-.36),(x,.48,.08),.20,'Teal',32)
  for i in range(12):a=i*math.tau/12;cyl('Cooling_Fin',(x+.20*math.cos(a),.48+.20*math.sin(a),-.34),(x+.20*math.cos(a),.48+.20*math.sin(a),.06),.014,'Steel',8)
  cyl('Pump_Volute',(x,.48,.08),(x,.48,.31),.23,'Steel',32);cyl('Discharge',(x,.48,.24),(x,.97,.24),.07,'Steel',20)
  for y in [.78,.84]:cyl('Flange',(x,y-.015,.24),(x,y+.015,.24),.13,'Steel',24)
  box('Motor_Foot',x,.22,-.10,.40,.17,.51,'Steel',.015)
 tube('Discharge_Header',[(-.46,.97,.24),(-.46,1.1,.24),(.46,1.1,.24),(.46,.97,.24)],.065,'Steel')
def tank():
 feet(1.35,1.35);cyl('Pressure_Vessel',(0,.20,0),(0,2.35,0),.61,'Steel',64)
 for y in [.35,1.15,2.20]:cyl('Tank_Band',(0,y-.035,0),(0,y+.035,0),.63,'Teal',64)
 cyl('Dished_Lid',(0,2.34,0),(0,2.43,0),.55,'Steel',48);cyl('Inspection_Neck',(0,2.42,0),(0,2.55,0),.23,'Steel',32)
 for i in range(8):a=i*math.tau/8;cyl('Lid_Bolt',(.48*math.cos(a),2.42,.48*math.sin(a)),(.48*math.cos(a),2.46,.48*math.sin(a)),.018,'Dark',6)
 tube('Sight_Gauge',[(-.30,.48,.60),(-.30,1.95,.60)],.026,'Glass');tube('Outlet',[(0,.40,.50),(0,.40,.87),(.45,.40,.87)],.065,'Steel');display(.20,1.54,.605,.27,.19,5)
def exchanger():
 box('Skid',0,.09,0,1.9,.18,.95,'Steel',.02)
 for x in [-.7,.7]:box('End_Frame',x,1.03,0,.11,1.85,.84,'Teal',.025)
 for x in [i*.055-.58 for i in range(22)]:box('Heat_Exchange_Plate',x,1.06,0,.026,1.52,.72,'Steel',.006)
 for y in [.36,1.72]:
  for z in [-.38,.38]:cyl('Tie_Rod',(-.83,y,z),(.83,y,z),.023,'Steel',12)
 for x in [-.7,.7]:
  for y in [.52,1.52]:cyl('Process_Nozzle',(x,y,.38),(x,y,.68),.085,'Steel',24);cyl('Process_Flange',(x,y,.64),(x,y,.69),.14,'Steel',24)
def electrical():
 cabinet(1.25,2.2,.65,mat='Dark');display(-.22,1.60,.36,.49,.30,6)
 for x in [.19,.39]:
  for y in [1.16,1.38,1.60]:cyl('Indicator_Lamp',(x,y,.36),(x,y,.385),.025,'Indicator',16)
 cyl('Isolator',(0,.80,.36),(0,.80,.40),.08,'Hazard',24);box('Isolator_Handle',0,.8,.43,.035,.16,.07,'Red',.012)
def ahu():
 box('AHU_Base',0,.12,0,2.2,.24,1.1,'Steel',.02);box('AHU_Housing',0,1.05,0,2.1,1.70,1.0,'Coat',.03)
 for x in [-.70,0,.70]:
  box('Service_Gasket',x,1.06,.51,.67,1.57,.025,'Dark',.008);box('Access_Panel',x,1.06,.534,.63,1.53,.026,'Coat',.01);pull(x+.21,1.03,.55,.05)
  for y in [.42,1.68]:bolt(x-.24,y,.553)
 for x in [-.68,.68]:vent(x,1.55,.555,.48,.30)
 display(0,1.45,.56,.40,.26,7);box('Duct_Collar',0,1.96,0,1.40,.15,.77,'Steel',.01);box('Duct',0,2.16,0,1.30,.28,.70,'Coat',.012)
def toolbench():
 cabinet(1.65,.88,.67,'drawers');box('Backboard',0,1.47,-.31,1.65,1.12,.05,'Steel',.012)
 for i in range(6):
  x=-.65+i*.25;cyl('Hanging_Tool',(x,1.25,-.27),(x,1.7,-.27),.013,'Steel',10);box('Tool_Handle',x,1.30,-.25,.034,.17,.04,'Teal',.011)
 box('Bench_Vise',.48,1.0,.12,.30,.20,.25,'Dark',.022);cyl('Vise_LeadScrew',(.48,1.03,.12),(.48,1.03,.38),.018,'Steel',16)
def crates():
 box('Pallet',0,.10,0,1.4,.20,.90,'Dark',.018)
 for x in [-.46,0,.46]:box('Pallet_Runner',x,.035,0,.18,.07,.89,'Steel',.01)
 for j in range(2):
  for x in [-.35,.35]:
   y=.42+j*.44;box('Sealed_Crate',x,y,0,.66,.42,.82,'Coat',.028);box('Crate_Lid',x,y+.206,0,.68,.04,.84,'Steel',.009)
   for dx in [-.24,.24]:box('Shipping_Clasp',x+dx,y+.12,.428,.06,.14,.025,'Steel',.006)
   box('Recessed_Handhold',x,y,.424,.26,.07,.013,'Dark',.014);box('Inventory_Print',x,y-.10,.425,.24,.062,.001,'Paper',0)
def fridge():
 cabinet(1.45,2.12,.82,mat='Steel');display(.39,1.85,.47,.23,.13,9)
 for x in [-.36,.36]:
  for y in [.55,1.5]:cyl('Coldroom_Handle_Mount',(x,y,.47),(x,y,.54),.016,'Steel',12)
  cyl('Coldroom_Handle',(x,.55,.54),(x,1.5,.54),.023,'Steel',16)
def sink():
 feet(1.8,.75);box('Sink_Deck',0,.9,0,1.8,.08,.75,'Steel',.012);box('Shelf',0,.25,0,1.65,.035,.65,'Steel',.006)
 for x in [-.46,.46]:
  box('Basin_Recess',x,.943,0,.67,.008,.53,'Dark',.025);box('Basin_Base',x,.948,0,.56,.003,.43,'Steel',.03);tube('Gooseneck',[(x,.94,-.29),(x,1.28,-.29),(x,1.31,.02),(x,1.23,.02)],.018,'Steel');cyl('Drain',(x,.95,0),(x,.952,0),.037,'Dark',24)
 box('Splashguard',0,1.13,-.38,1.80,.40,.035,'Steel',.008)
def mealprep():
 cabinet(1.8,.87,.75,'drawers',mat='Steel')
 for x in [-.57,0,.57]:box('Serving_Well',x,.91,0,.50,.015,.60,'Dark',.012);box('Lidded_Gastronorm',x,.94,0,.46,.045,.56,'Steel',.013);pull(x,.97,.27,.17)
 for x in [-.85,.85]:cyl('Hygiene_Shield_Post',(x,.91,-.32),(x,1.50,-.32),.02,'Steel',16)
 box('Hygiene_Shield',0,1.30,-.31,1.70,.38,.006,'Glass',.001)
def dishwasher():
 cabinet(1.2,.86,.76,mat='Steel');box('Wash_Chamber',0,1.23,0,1.12,.68,.70,'Steel',.02);box('Wash_Door',0,1.24,.36,1.04,.56,.027,'Coat',.012);pull(0,1.47,.39,.55);display(.31,1.65,.35,.26,.14,10);box('Control_Riser',0,1.64,-.22,1.11,.18,.24,'Dark',.01)
def shower():
 box('Shower_Tray',0,.04,0,1.48,.08,1.50,'Steel',.018)
 for i in range(19):box('Drain_Grate',-.65+i*.072,.088,0,.035,.015,1.31,'Steel',.002)
 for x in [-.72,.72]:box('Shower_Side',x,1.2,0,.035,2.40,1.48,'Coat',.01)
 box('Shower_Back',0,1.2,-.73,1.48,2.4,.035,'Coat',.01);tube('Water_Riser',[(.36,.25,-.68),(.36,2.25,-.68),(0,2.25,-.20)],.022,'Steel');cyl('Shower_Head',(0,2.20,-.20),(0,2.25,-.20),.16,'Steel',32)
 for y in [.95,1.12]:cyl('Mixer_Control',(0,y,-.70),(0,y,-.62),.045,'Steel',24)
 tube('Grab_Rail',[(-.45,.90,-.65),(-.45,1.45,-.65)],.022,'Steel')
def ppe():
 shelf(1.8,2.05,.62)
 for j,y in enumerate([.18,.65,1.12,1.59]):
  for i in range(4):
   x=(i-1.5)*.42;box('PPE_Dispenser',x,y+.14,0,.36,.27,.50,'Coat',.015);box('Dispense_Slot',x,y+.10,.257,.24,.065,.008,'Dark',.008)
   if j==2:box('Folded_Mask',x,y+.10,.28,.18,.018,.07,'Fabric',.006)
def boots():
 box('Boot_Rack_Base',0,.06,0,1.45,.12,.58,'Steel',.02)
 for i in range(6):
  x=-.6+i*.24;cyl('Drying_Pipe',(x,.12,-.10),(x,.86,-.10),.018,'Steel',12);box('Boot_Sole',x,.20,.06,.18,.08,.36,'Rubber',.027);box('Boot_Upper',x,.38,-.04,.16,.40,.20,'Teal',.045)
 box('Air_Manifold',0,.15,-.25,1.40,.15,.13,'Steel',.012)
def chamber():
 box('Test_Platform',0,.12,0,2.4,.24,2.4,'Dark',.035);cyl('Test_Dais',(0,.24,0),(0,.35,0),.95,'Steel',64)
 for x in [-1.1,1.1]:
  for z in [-1.1,1.1]:box('Test_Column',x,1.8,z,.16,3.4,.16,'Steel',.02);box('Anchored_Base',x,.29,z,.30,.10,.30,'Steel',.01)
 for x in [-1.1,1.1]:box('Gantry',x,3.46,0,.20,.18,2.40,'Coat',.02)
 for z in [-1.1,1.1]:box('Gantry',0,3.46,z,2.40,.18,.20,'Coat',.02)
 for y in [.9,2.0]:
  for x in [-1.1,1.1]:tube('Sensor_Rail',[(x,y,-1.1),(x,y,1.1)],.024,'Steel');box('Optical_Receiver',x,y,0,.20,.22,.32,'Dark',.018)
 box('Inactive_Target',0,1.33,0,.60,1.8,.25,'Coat',.09)
def test_console():
 cabinet(1.65,.83,.65,'drawers',mat='Dark');display(-.30,1.25,-.05,.75,.46,16);monitor_stand(-.3,1.25,-.05,.75,.46,.86);keyboard(-.3,.89,.22)
 for x in [.29,.49,.69]:cyl('Experiment_Knob',(x,.90,.20),(x,.94,.20),.032,'Steel',20)
 box('Key_Enable_Recess',.48,.88,-.04,.34,.02,.20,'Rubber',.006);cyl('Stop_Button',(.48,.90,-.04),(.48,.96,-.04),.05,'Red',24)
def control_desk():
 cabinet(2.2,.78,.82,'drawers',mat='Dark')
 for x,k in [(-.53,11),(.53,12)]:display(x,1.24,-.16,.88,.51,k);monitor_stand(x,1.24,-.16,.88,.51,.81)
 keyboard(-.30,.84,.22);phone(.72,.82,.16);box('Trackball',.32,.85,.23,.18,.08,.19,'Teal',.024)
def bigwall():
 cabinet(4.8,.80,.75,mat='Dark')
 for x,channels in [(-1.60,(11,6)),(0,(12,7)),(1.60,(15,17))]:
  cyl('Display_Upright',(x,.70,-.24),(x,3.17,-.24),.045,'Steel',16)
  for y,k in zip([1.44,2.44],channels):display(x,y,.02,1.51,.90,k);box('VESA_Mount',x,y,-.19,.30,.30,.16,'Steel',.01)
def recorder():
 cabinet(.85,2.2,.75,mat='Dark')
 for j in range(9):
  y=.32+j*.19;box('Rack_Unit',0,y,.405,.72,.16,.04,'Steel',.009)
  for x in [-.25,0,.25]:box('Drive_Caddy',x,y,.43,.21,.12,.028,'Dark',.004);box('Drive_LED',x+.06,y+.03,.447,.025,.006,.002,'Indicator',0)
 display(0,2.06,.43,.52,.13,15)
def bench():
 for x in [-.70,.70]:box('Bench_Leg',x,.22,0,.09,.39,.47,'Steel',.014)
 box('Seat',0,.45,0,1.75,.10,.56,'Fabric',.045);box('Back',0,.84,-.23,1.75,.65,.10,'Fabric',.044)
def isolationbench():
 cabinet(1.4,.84,.65,'drawers');display(-.32,1.22,-.10,.66,.41,1);monitor_stand(-.32,1.22,-.10,.66,.41,.87);keyboard(-.25,.9,.20);vessel(.45,.87,.03,.075,.28,'Coat')
builders={'LivingBed':lambda:bed(False),'MedicalBed':lambda:bed(True),'LivingDesk':living_desk,'SanitaryBasin':sanitary,'LivingAlcove':cell_screen,'LinenRack':linen,'LinenReturnCart':hampers,'SupplyRack':supply,'MealTransportCart':passcart,'PrivacyCurtain':privacy,'ExaminationLight':examlight,'MedicalSterilizer':sterilizer,'VitalCart':lambda:monitor_cart(2),'UltrasoundCart':lambda:monitor_cart(3),'MedicationCabinet':lambda:cabinet(1.25,1.85,.62,'drawers'),'PersonalLocker':lambda:cabinet(.68,1.8,.55,mat='Warm'),'TwinCoolingPump':pump,'ExpansionVessel':tank,'PlateHeatExchanger':exchanger,'ElectricalSwitchgear':electrical,'AirHandlingUnit':ahu,'MaintenanceBench':toolbench,'SealedSupplyCrates':crates,'ColdStorage':fridge,'DoubleWashSink':sink,'MealPreparation':mealprep,'TrayDishwasher':dishwasher,'DeconShower':shower,'PPEDispenser':ppe,'BootDryingRack':boots,'TestGantry':chamber,'TestControlConsole':test_console,'CentralOperatorDesk':control_desk,'CentralVideoWall':bigwall,'DataRecorderRack':recorder,'WaitingBench':bench,'IsolationNurseStation':isolationbench}
if __name__=='__main__':
 for name,fn in builders.items():apply_subset(name,fn)
 print('COMPLETE',len(manifest),flush=True)
