"""Operationally readable B5 equipment; editable manufactured parts. Author 송예찬."""
import sys,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *

def extras():
 for n,c in [('Carton',(.48,.39,.25,1)),('Powder',(.10,.18,.23,1)),('Polymer',(.47,.57,.56,1)),('Tag',(.65,.74,.72,1)),('LensGreen',(.08,.65,.29,1)),('LensAmber',(.72,.35,.035,1)),('LensOff',(.055,.09,.08,1))]+[('Screen_'+n,(.12,.34,.36,1)) for n in ['Test','Food','Issue','Decon','Lift','Power','Stock']]:
  m=bpy.data.materials.get('OD_'+n) or bpy.data.materials.new('OD_'+n);m.diffuse_color=c;m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=c;b.mats[n]=m

def new():reset();extras()
def source(n,folder='B5_SpatialRefinement'):load(R/'SourceAssets'/folder/(n+'.blend'));extras()
def remove(*names):
 for o in list(bpy.context.scene.objects):
  if any(o.name==n or o.name.startswith(n+'.') for n in names):bpy.data.objects.remove(o,do_unlink=True)
def group(fn,x=0,z=0,yaw=0,y=0):
 before=set(bpy.data.objects);fn();transform(set(bpy.data.objects)-before,x,z,yaw,y)
def ellipsoid(n,x,y,z,w,h,d,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=xyz(x,y,z));o=bpy.context.object;o.name=n;o.scale=(w/2,d/2,h/2);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(b.mats[mat]);
 for p in o.data.polygons:p.use_smooth=True
 return o
def tag(x,y,z,w,h,i):
 o=mesh('Flush_Identification_Print',[(x-w/2,y-h/2,z),(x+w/2,y-h/2,z),(x+w/2,y+h/2,z),(x-w/2,y+h/2,z)],[(0,3,2,1)],'Tag',0)
 if o.data.polygons[0].normal.y>0:o.data.flip_normals()
 uv=o.data.uv_layers.new(name='UVMap');u=i%4/4;v=1-(i//4+1)/8;coords=[(u+.249,v+.001),(u+.001,v+.001),(u+.001,v+.124),(u+.249,v+.124)]
 for p in o.data.polygons:
  for li in p.loop_indices:uv.data[li].uv=coords[o.data.loops[li].vertex_index]
 o['display_uv']=True
def screen(x,y,z,w,h,kind):
 b.mats['Display_01']=b.mats['Screen_'+kind]
 before=set(bpy.data.objects);b.display(x,y,z,w,h,1)
 for o in set(bpy.data.objects)-before:
  if o.name.startswith('LCD_Optical_Surface'):o.data.materials[0]=b.mats['Screen_'+kind]
def lamp(x,y,z,colour='LensGreen',radius=.023):
 cyl('Lamp_Panel_Gasket',(x,y,z),(x,y,z+.006),radius*1.43,'Rubber',32)
 cyl('Lamp_Knurled_Bezel',(x,y,z+.005),(x,y,z+.017),radius*1.27,'Steel',32)
 cyl('Lens_Recess',(x,y,z+.017),(x,y,z+.019),radius*1.04,'Dark',32)
 ellipsoid('Convex_Pilot_Lens',x,y,z+.020,radius*1.92,radius*1.92,.021,colour)
 for i in range(12):
  a=i*math.tau/12;cyl('Bezel_Grip',(x+radius*1.23*math.cos(a),y+radius*1.23*math.sin(a),z+.008),(x+radius*1.23*math.cos(a),y+radius*1.23*math.sin(a),z+.014),.0018,'Steel',6)
def screws(w,h,z,cy):
 for x in [-w/2+.025,w/2-.025]:
  for y in [cy-h/2+.025,cy+h/2-.025]:bolt(x,y,z)
def carton(x,y,z,w=.47,h=.32,d=.49,i=13):
 box('Corrugated_Carton',x,y+h/2,z,w,h,d,'Carton',.007)
 box('Fold_Seam',x,y+h+.0008,z,.002,.001,d-.012,'Dark',0)
 box('Paper_Sealing_Tape',x,y+h+.0016,z,.048,.001,d+.001,'Paper',0)
 box('Tape_Fold',x,y+h-.042,z+d/2+.001,.048,.084,.001,'Paper',0);tag(x-w*.15,y+h*.52,z+d/2+.0018,w*.5,h*.40,i)
def tote(x,y,z,w=.50,h=.33,d=.50,i=15):
 box('Moulded_Stacking_Tote',x,y+h/2,z,w,h,d,'Polymer',.022)
 box('Reinforced_Lid_Lip',x,y+h-.012,z,w+.012,.034,d+.012,'Powder',.008)
 for xx in [x-w*.32,x+w*.32]:
  box('Moulded_Rib',xx,y+h*.47,z+d/2+.009,.018,h*.66,.020,'Polymer',.004)
 box('Recessed_Handhold',x,y+h*.78,z+d/2+.011,w*.33,.037,.006,'Dark',.008);tag(x,y+h*.39,z+d/2+.013,w*.36,h*.31,i)
def pallet(x=0,z=0):
 for xx in [-.48,0,.48]:box('Pallet_Runner',x+xx,.065,z,.14,.13,.98,'Powder',.008)
 for zz in [-.42,0,.42]:box('Pallet_Deck',x,.145,z+zz,1.2,.035,.25,'Polymer',.006)
def rack(kind):
 new();w=1.85;d=.82;h=2.85
 for x in [-w/2,w/2]:
  for z in [-d/2,d/2]:
   box('Perforated_Upright',x,h/2,z,.064,h,.064,'Powder',.006);box('Anchor_Plate',x,.018,z,.16,.036,.16,'Steel',.006)
   for y in [i*.13+.19 for i in range(20)]:box('Beam_Hook_Slot',x,y,z+.033,.013,.031,.002,'Dark',.001)
   for dx in [-.052,.052]:cyl('Rack_Floor_Anchor',(x+dx,.035,z),(x+dx,.049,z),.011,'Steel',6)
  tube('Frame_Diagonal',[(x,.18,-d/2),(x,1.45,d/2),(x,2.68,-d/2)],.012,'Steel')
 for level,y in enumerate([.19,.86,1.53,2.20]):
  box('Folded_Deck',0,y,0,w,.035,d,'Steel',.005)
  for z in [-d/2,d/2]:box('Load_Beam',0,y-.042,z,w,.10,.055,'WarmAccent',.007)
  tag(-.59,y-.044,d/2+.029,.42,.075,13+kind)
  for j in range(3):
   x=(j-1)*.59
   if kind==0:
    carton(x,y+.02,0,.53,.40 if level%2 else .49,.65,13)
   elif kind==1:tote(x,y+.02,.01,.51,.36,.64,14)
   elif kind==2:
    if j<2:
     cyl('Sealed_Consumable_Drum',(x,y+.03,0),(x,y+.52,0),.22,'Polymer',32)
     for yy in [y+.07,y+.48]:cyl('Drum_Impact_Ring',(x,yy-.012,0),(x,yy+.012,0),.231,'Powder',32)
     cyl('Tamper_Cap',(x+.06,y+.52,.06),(x+.06,y+.55,.06),.04,'Steel',20);tag(x,y+.30,.222,.23,.1,15)
    else:carton(x,y+.02,0,.47,.35,.60,15)
   else:
    box('Rugged_Instrument_Case',x,y+.24,0,.51,.42,.65,'Dark',.025)
    for xx in [x-.19,x+.19]:box('Case_Clasp',xx,y+.32,.337,.045,.10,.025,'Steel',.006)
    b.pull(x,y+.29,.34,.18);tag(x,y+.16,.328,.21,.085,16)
 for x in [-.92,.92]:box('Column_Impact_Guard',x,.24,.46,.13,.45,.12,'Hazard',.02)
 save('OD_WarehouseRack_'+str(kind),'Props')
def palletload(kind):
 new();pallet()
 for j in range(3):
  for x in [-.28,.28]:carton(x,.165+j*.32,0,.53,.31,.79,16) if kind==0 else tote(x,.165+j*.32,0,.53,.31,.80,15)
 for x in [-.42,.42]:
  box('Cargo_Strap',x,.69,.407,.025,1.06,.003,'Dark',.001);box('Cargo_Strap',x,.69,-.407,.025,1.06,.003,'Dark',.001);box('Cargo_Strap',x,1.128,0,.025,.004,.82,'Dark',.001)
 save('OD_PalletLoad_'+str(kind),'Props')
def palletjack():
 new()
 for x in [-.25,.25]:
  box('Tapered_Fork',x,.095,.25,.17,.10,1.24,'Hazard',.022)
  cyl('Load_Roller',(x-.074,.060,.70),(x+.074,.060,.70),.055,'Dark',20)
 box('Fork_Crosshead',0,.20,-.42,.70,.25,.30,'Hazard',.025)
 for x in [-.13,.13]:cyl('Steering_Wheel',(x-.04,.11,-.54),(x+.04,.11,-.54),.10,'Rubber',24)
 cyl('Hydraulic_Jack',(0,.12,-.44),(0,.49,-.44),.076,'Steel',24);tube('Tiller_Arm',[(0,.4,-.48),(0,.87,-.77),(0,1.12,-.89)],.029,'Steel')
 tube('Tiller_Loop',[(-.19,1.1,-.89),(-.19,1.27,-.89),(.19,1.27,-.89),(.19,1.1,-.89),(-.19,1.1,-.89)],.023,'Dark');tag(0,.27,-.258,.34,.10,18)
 save('OD_PalletTruck','Props')
def receiving():
 new();b.cabinet(2.0,.9,.95,'drawers',mat='Powder');box('Receiving_Worktop',0,.94,0,2.06,.045,1.0,'Steel',.014);box('Parcel_Scale',-.1,.99,0,.73,.06,.67,'Dark',.01);carton(-.1,1.02,0,.51,.32,.48,17)
 screen(.73,1.37,-.29,.50,.30,'Stock');cyl('Terminal_Stand',(.73,.96,-.35),(.73,1.21,-.35),.023,'Steel',16)
 box('Thermal_Label_Printer',-.82,1.07,.04,.28,.21,.30,'Dark',.018);box('Printer_Output_Slot',-.82,1.08,.195,.20,.014,.008,'Rubber',.003);tag(-.82,1.03,.20,.17,.055,17)
 box('Scanner_Cradle',.24,.97,.20,.13,.05,.18,'Powder',.008);tube('Scanner_Grip',[(.24,.99,.20),(.24,1.11,.17)],.025,'Dark');box('Barcode_Scanner_Head',.24,1.13,.17,.12,.055,.08,'Polymer',.012);box('Scanner_Window',.24,1.13,.214,.085,.025,.003,'Red',.002)
 tube('Scanner_Cord',[(.24,1.,.20),(.47,.94,.30),(.56,.76,.32),(.56,.66,.30),(.65,.66,.15)],.005,'Dark');save('OD_ReceivingInspection','Props')
def dummy():
 source('SF_TestGantry');remove('Inactive_Target')
 def body():
  for x in [-.16,.16]:
   box('Instrumented_Foot',x,.43,.06,.17,.12,.33,'Powder',.035);cyl('Ankle_Loadcell',(x,.46,0),(x,.56,0),.046,'Steel',24)
   ellipsoid('Calibrated_Shin',x,.77,0,.15,.43,.17,'Polymer');ellipsoid('Knee_Encoder',x,1.0,0,.12,.12,.13,'Dark');ellipsoid('Calibrated_Thigh',x,1.23,0,.20,.42,.21,'Polymer')
   cyl('Foot_Clamp',(x-.10,.39,.04),(x+.10,.39,.04),.023,'Steel',16)
  box('Pelvis_Sensor_Frame',0,1.46,0,.43,.24,.25,'Powder',.045);ellipsoid('Torso_Instrument_Shell',0,1.76,0,.52,.47,.29,'Polymer')
  cyl('Neck_Loadcell',(0,1.98,0),(0,2.08,0),.055,'Steel',24);ellipsoid('Instrumented_Head',0,2.20,0,.23,.30,.23,'Polymer');box('Face_Reference_Plate',0,2.20,.108,.15,.15,.024,'Dark',.029)
  for side in [-1,1]:
   ellipsoid('Shoulder_Joint',side*.29,1.92,0,.14,.14,.14,'Dark');ellipsoid('Upper_Arm',side*.36,1.73,0,.14,.35,.15,'Polymer');ellipsoid('Elbow_Encoder',side*.39,1.54,0,.11,.11,.12,'Steel');ellipsoid('Forearm',side*.42,1.36,.015,.12,.30,.13,'Polymer');box('Hand_Test_Block',side*.43,1.16,.02,.10,.13,.13,'Powder',.027)
  for x,y in [(0,2.24),(-.18,1.88),(.18,1.88),(0,1.64),(-.16,1.18),(.16,1.18),(-.16,.74),(.16,.74)]:
   cyl('Optical_Marker_Socket',(x,y,.14),(x,y,.158),.024,'Dark',20);ellipsoid('Reflective_Tracking_Marker',x,y,.164,.026,.026,.017,'Lamp')
  tag(0,1.72,.148,.24,.075,1);tube('Surrogate_Data_Harness',[(0,1.72,-.16),(0,1.05,-.21),(.3,.60,-.30),(.65,.39,-.45),(1.06,.39,-.55),(1.06,1.10,-.55)],.014,'Dark')
 group(body,yaw=180)
 for x in [-.72,.72]:
  box('Fixture_Support',x,.52,0,.11,.34,.16,'Steel',.012);tube('Quick_Release_Fixture',[(x,.68,0),(x,.68,.5),(x*.4,.68,.5)],.017,'Steel')
 for z in [-.78,-.52,-.26,0,.26,.52,.78]:box('Reference_Grid',0,.354,z,1.46,.001,.007,'Paper',0)
 for x in [-.78,-.52,-.26,0,.26,.52,.78]:box('Reference_Grid',x,.354,0,.007,.001,1.46,'Paper',0)
 group(lambda:tag(0,.12,1.203,1.05,.12,0),yaw=180);save('OD_InstrumentedTestRig','Props')
def testconsole():
 source('SF_TestControlConsole')
 for o in bpy.context.scene.objects:
  if o.name.startswith('LCD_Optical_Surface'):o.data.materials[0]=b.mats['Screen_Test']
 tag(.52,.30,.369,.51,.07,0);save('OD_ExchangeControl','Props')
def mealtray(x,y,z):
 box('Sealed_Meal_Tray',x,y+.026,z,.32,.052,.23,'Dark',.018);box('Heat_Sealed_Foil_Lid',x,y+.054,z,.328,.003,.238,'Steel',.009)
 # Printed paper sleeve lies flush over foil, with folded front flap.
 box('Meal_Paper_Sleeve',x,y+.057,z,.11,.001,.241,'Paper',.001);tag(x,y+.030,z+.121,.10,.033,3)
def mealcheck():
 new();b.cabinet(2.35,.90,.88,'drawers',mat='Steel');box('Hygienic_Worktop',0,.938,0,2.42,.045,.94,'Steel',.016)
 for x in [-.8,-.40,0]:
  for z in [-.19,.16]:mealtray(x,.963,z)
 box('Checkweigher_Base',.77,.99,0,.62,.055,.57,'Dark',.014);box('Weighing_Pan',.77,1.028,0,.52,.021,.45,'Steel',.008);mealtray(.77,1.04,0)
 screen(.72,1.37,-.34,.46,.27,'Food');cyl('Scale_Display_Stem',(.72,.96,-.39),(.72,1.22,-.39),.022,'Steel',16);tag(.72,.30,.484,.55,.07,3)
 save('OD_SealedMealInspection','Props')
def regen():
 new();b.cabinet(1.7,2.20,.91,mat='Steel');remove('Door_Face','Door_Gasket','Hinge','Vent_Recess','Louver','Pull','Grip_Stand')
 for x in [-.41,.41]:
  box('Insulated_Door_Gasket',x,1.16,.47,.79,1.87,.035,'Rubber',.022);box('Regeneration_Door',x,1.16,.5,.74,1.82,.05,'Powder',.024)
  box('Recessed_Vision_Frame',x,1.44,.535,.49,.63,.027,'Steel',.02);box('Dark_Inspection_Window',x,1.44,.553,.44,.58,.006,'Glass',.012)
  b.pull(x+.26,1.15,.54,.055)
  for y in [.39,1.92]:box('Heavy_Door_Hinge',x-.32,y,.54,.055,.13,.05,'Steel',.009)
  tag(x,.48,.527,.48,.12,5);lamp(x+.25,1.85,.532)
 screen(0,2.05,.51,.52,.15,'Food');b.vent(0,.29,.54,1.30,.18);box('Exhaust_Collar',0,2.27,-.2,.55,.14,.4,'Steel',.009)
 save('OD_MealRegenerationCabinet','Props')
def mealtrolley():
 new();b.trolley(1.12,.76)
 for x in [-.53,.53]:box('Rack_Side_Protection',x,.77,0,.035,1.10,.70,'Steel',.008)
 for j in range(7):
  y=.29+j*.15;box('Removable_Tray',0,y,0,1.02,.022,.70,'Steel',.006)
  for x in [-.30,.06,.36]:mealtray(x,y+.016,0)
 box('Cart_Dust_Cover',0,1.37,0,1.13,.04,.78,'Polymer',.016);tag(0,1.25,.37,.55,.12,18);save('OD_SealedMealCart','Props')
def issue():
 new();b.cabinet(2.1,2.2,.70,mat='Powder');remove('Door_Face','Door_Gasket','Hinge','Vent_Recess','Louver','Pull','Grip_Stand')
 for row,y in enumerate([.48,.96,1.44]):
  for col,x in enumerate([-.66,0,.66]):
   box('Lockable_Cassette_Gasket',x,y,.367,.61,.44,.018,'Dark',.008);box('Security_Cassette_Face',x,y,.384,.57,.40,.025,'Polymer',.012);b.pull(x,y+.08,.409,.17);tag(x,y-.075,.398,.38,.10,6 if row<2 else 7)
   cyl('Quarter_Turn_Lock',(x+.20,y+.11,.398),(x+.20,y+.11,.414),.018,'Steel',20);box('Lock_Keyway',x+.20,y+.11,.416,.002,.015,.001,'Dark',0)
 screen(-.37,1.94,.38,.61,.29,'Issue');box('Badge_Reader',.42,1.94,.39,.23,.26,.06,'Dark',.016);lamp(.42,1.86,.427,'LensAmber',.012);tag(.42,2.01,.423,.17,.09,7)
 save('OD_ControlledNutritionBank','Props')
def sealedcase():
 new();b.trolley(.94,.66)
 for x in [-.23,.23]:
  tote(x,.24,0,.41,.28,.52,7);box('Case_Tamper_Seal',x+.12,.47,.27,.018,.11,.002,'Red',.001)
 for x in [-.32,-.11,.11,.32]:
  vs=[];fs=[];nx=12;ny=16
  for side in [-1,1]:
   for j in range(ny+1):
    for i in range(nx+1):
     u=i/nx;v=j/ny;depth=.004+.022*min(1,min(u,1-u)*6)*min(1,min(v,1-v)*6);vs.append((x-.085+.17*u,.78+.285*v,side*depth))
  stride=(nx+1)*(ny+1)
  for side in range(2):
   for j in range(ny):
    for i in range(nx):
     a=side*stride+j*(nx+1)+i;fs.append((a,a+1,a+nx+2,a+nx+1))
  border=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,ny+1)]+[ny*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1) for j in range(ny-1,0,-1)]
  for a,c in zip(border,border[1:]+border[:1]):fs.append((a,c,c+stride,a+stride))
  mesh('Flexible_Sealed_Nutrition_Pouch',vs,fs,'Polymer',0,True)
  box('Pouch_Upper_Heatseal',x,1.07,0,.17,.012,.011,'Paper',.003);box('Pouch_Lower_Heatseal',x,.779,0,.17,.012,.011,'Paper',.003)
  cyl('Capped_Delivery_Port',(x,.74,0),(x,.78,0),.015,'Steel',16);cyl('Tamper_Port_Cover',(x,.73,0),(x,.76,0),.021,'Powder',16);tag(x,.93,.0268,.11,.07,6)
 for x in [-.44,.44]:box('Pouch_Tray_Side',x,.84,0,.018,.20,.55,'Steel',.005)
 box('Opened_Transit_Case_Lid',0,1.02,-.29,.88,.48,.024,'Powder',.012)
 box('Inventory_Header_Rail',0,.55,.328,.85,.13,.015,'Powder',.005);cyl('Transit_Lid_Hinge',(-.38,.77,-.29),(.38,.77,-.29),.019,'Steel',16);tag(0,.54,.337,.5,.11,6);save('OD_NutritionTransferCart','Props')
def dirtyreturn():
 new();b.wheels(1.35,.72)
 for x in [-.34,.34]:
  box('Sealed_PPE_Return_Body',x,.64,0,.61,.89,.67,'Powder',.035);box('Lid_Seal',x,1.09,0,.63,.022,.68,'Rubber',.012);box('Hinged_Return_Lid',x,1.12,0,.65,.045,.71,'Steel',.018);tube('Hands_Free_Pedal',[(x-.12,.18,.31),(x-.12,.14,.45),(x+.12,.14,.45),(x+.12,.18,.31)],.014,'Steel');tag(x,.74,.338,.44,.15,8)
  box('Bag_Retaining_Collar',x,1.065,0,.59,.05,.62,'Polymer',.018)
 tube('Push_Rail',[(-.64,.84,-.37),(-.64,1.14,-.37),(.64,1.14,-.37),(.64,.84,-.37)],.022,'Steel');save('OD_ClosedPPEReturn','Props')
def bagseal():
 new();b.cabinet(1.25,.87,.62,'drawers',mat='Steel');box('Film_Roll_Base',0,.96,-.1,.86,.13,.30,'Powder',.012);cyl('Bag_Film_Roll',(-.36,1.09,-.13),(.36,1.09,-.13),.115,'Paper',32)
 box('Impulse_Seal_Base',0,.965,.18,.80,.075,.18,'Dark',.012);box('Hinged_Seal_Bar',0,1.035,.18,.76,.04,.085,'Steel',.008);b.pull(0,1.04,.23,.25);tag(0,.67,.334,.61,.13,9);lamp(.47,1.0,.24,'LensAmber',.014);save('OD_ContaminatedBagSealer','Props')
def bootwash():
 new();box('Bootwash_Sump',0,.11,0,1.05,.22,1.25,'Steel',.04)
 for x in [-.28,.28]:
  for z in [i*.10-.40 for i in range(9)]:cyl('Rotary_Sole_Brush',(x-.18,.24,z),(x+.18,.24,z),.048,'Dark',16)
 for x in [-.50,.50]:tube('Safety_Handrail',[(x,.20,-.48),(x,1.10,-.48),(x,1.10,.48),(x,.20,.48)],.024,'Steel')
 box('Brush_Motor_Cover',0,.38,-.54,.77,.32,.23,'Powder',.03);tag(0,.39,-.416,.49,.10,10);tube('Drain_Connection',[(.41,.14,-.53),(.41,.14,-.78)],.035,'Steel');save('OD_BootSoleWasher','Props')
def cleanppe():
 new();b.cabinet(1.80,2.10,.53,mat='Polymer');remove('Door_Face','Door_Gasket','Hinge','Vent_Recess','Louver','Pull','Grip_Stand')
 for y in [.50,1.05,1.60]:
  for x in [-.60,0,.60]:
   case=box('Individual_PPE_Cassette',x,y,.29,.53,.48,.065,'Powder',.016)
   cut=box('Window_Cutter',x,y+.065,.30,.36,.22,.14,'Dark',0);bpy.context.view_layer.objects.active=case;mod=case.modifiers.new('Recessed_Window_Opening','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
   box('Pack_Inspection_Window',x,y+.065,.328,.36,.22,.003,'Window',.003)
   box('Folded_Protective_Pack',x,y+.06,.306,.29,.16,.014,'Paper',.007);tag(x,y+.065,.314,.24,.08,11)
   box('Dispensing_Slot',x,y-.135,.33,.39,.055,.018,'Rubber',.008);box('Visible_Sealed_Pack_Edge',x,y-.14,.35,.29,.017,.035,'Paper',.004)
 tag(0,1.99,.29,1.15,.12,11);save('OD_CleanPPEDispenser','Props')
def aircheck():
 new();box('Check_Station_Foot',0,.045,0,.68,.09,.60,'Steel',.022);box('Check_Station_Column',0,.90,-.05,.26,1.68,.26,'Powder',.022);screen(0,1.50,.12,.46,.29,'Decon')
 for x in [-.26,.26]:
  tube('Hand_Check_Cradle',[(x,.93,-.03),(x,1.10,.18),(x,1.10,.36)],.022,'Steel');box('Sensor_Handplate',x,1.10,.27,.18,.045,.24,'Dark',.024)
 box('Shoe_Check_Plate',0,.10,.25,.59,.045,.30,'Dark',.012);tag(0,.83,.086,.22,.09,12);lamp(0,1.78,.10,'LensGreen');save('OD_DeconExitCheck','Props')
def shower():
 source('SF_DeconShower');box('Water_Service_Column',.56,1.32,-.66,.22,1.15,.12,'Powder',.018);screen(.56,1.61,-.588,.13,.18,'Decon')
 for y in [1.27,1.39]:lamp(.56,y,-.585,'LensGreen' if y>1.3 else 'LensOff',.018)
 tube('Waste_Water_Outlet',[(.5,.06,-.64),(.5,.06,-.83),(.5,.015,-.83)],.037,'Steel');tube('Connected_Overhead_Water_Feed',[(.36,2.25,-.68),(.36,3.46,-.68)],.022,'Steel')
 cyl('Drain_Floor_Collar',(.5,.008,-.83),(.5,.025,-.83),.065,'Steel',24);tag(-.25,1.40,-.708,.49,.13,10);save('OD_PipedDeconShower','Props')
def power():
 source('SF_ElectricalSwitchgear');remove('Indicator_Lamp')
 for col,x in enumerate([.19,.39]):
  for row,y in enumerate([1.16,1.38,1.60]):lamp(x,y,.36,'LensGreen' if (col,row) in [(0,2),(1,1)] else 'LensAmber' if row==0 and col==0 else 'LensOff')
 for o in bpy.context.scene.objects:
  if o.name.startswith('LCD_Optical_Surface'):o.data.materials[0]=b.mats['Screen_Power']
 tag(.29,1.76,.368,.35,.075,22);tag(0,1.02,.368,.52,.085,25)
 for x in [.19,.39]:
  for row,y in enumerate([1.16,1.38,1.60]):tag(x,y-.063,.368,.14,.032,22+row)
 for x in [-.49,.49]:box('Door_Earth_Bond_Tag',x,.23,.36,.06,.06,.009,'Hazard',.006)
 save('OD_ElectricalSwitchgear','Props')
def process():
 source('SF_ProcessControlBay');remove('Status_Lamp','Moulded_Breaker','Toggle_Lever')
 for o in list(bpy.context.scene.objects):
  if o.name.startswith('Fastener'):
   vv=[o.matrix_world@Vector(v) for v in o.bound_box];yy=sum(v.z for v in vv)/8
   if abs(yy-1.8)<.02:bpy.data.objects.remove(o,do_unlink=True)
 for j,x in enumerate([-.81,-.23,.23,.81]):
  lamp(x,1.04,.309,'LensGreen' if j in [0,2] else 'LensOff',.020);tag(x,.96,.309,.18,.047,23 if j%2==0 else 24)
  cyl('Selector_Gasket',(x,1.18,.261),(x,1.18,.292),.054,'Rubber',32);box('Selector_Position_Mark',x,1.195,.342,.004,.025,.003,'Paper',.001)
 box('Recessed_DIN_Control_Plate',0,.32,.276,.94,.22,.028,'Steel',.008)
 for x in [-.25,0,.25]:
  box('Moulded_Breaker',x,.31,.309,.17,.16,.060,'Dark',.009);box('Toggle_Lever',x,.30,.346,.045,.065,.022,'Polymer',.006);tag(x,.385,.340,.13,.028,25)
 save('OD_ProcessControlBay','Props')
def lift():
 source('RD_VL_Hoist','B5_RemainingDomes')
 remove('Closed_Lift_Leaf','Door_Impact_Plate','Call_Station','Call_Key')
 # Retire every component of the earlier overlapping LCD, not only its screen surface.
 for o in list(bpy.context.scene.objects):
  vs=[o.matrix_world@Vector(p) for p in o.bound_box];cx=sum(v.x for v in vs)/8;cy=sum(v.z for v in vs)/8;cz=-sum(v.y for v in vs)/8
  if 2.88<cy<3.30 and abs(cx)<.43 and cz<-1.71:bpy.data.objects.remove(o,do_unlink=True)
 def landing(y):
  # Local front is +Z; rotate to face the actual lower landing at -Z.
  for x in [-.69,.69]:
   box('Freight_Door_Structural_Leaf',x,1.42,1.66,1.355,2.69,.105,'Powder',.014)
   for xx in [x-.52,x+.52]:box('Door_Pressed_Stiffener',xx,1.42,1.728,.095,2.47,.033,'Steel',.008)
   for yy in [.35,1.09,2.40]:box('Leaf_Cross_Rib',x,yy,1.725,1.16,.085,.035,'Steel',.009)
   box('Replaceable_Kick_Plate',x,.58,1.75,1.13,.46,.025,'Steel',.008)
   for row in range(5):
    for col in range(13):
     xx=x-.50+col*.082;yy=.40+row*.073;dy=.012 if (row+col)%2 else -.012;cyl('Chequer_Plate_Lug',(xx-.018,yy-dy,1.765),(xx+.018,yy+dy,1.765),.003,'Steel',8)
   tag(x,1.79,1.715,.71,.17,19 if x<0 else 20)
  box('Centre_Door_Seal',0,1.42,1.719,.014,2.65,.021,'Rubber',.005)
  for xx in [-1.50,1.50]:
   box('Impact_Buffer_Anchor',xx,.65,1.80,.19,1.12,.14,'Steel',.018);box('Replaceable_Rubber_Buffer',xx,.65,1.89,.12,1.0,.06,'Rubber',.022)
   for yy in [.25,1.06]:bolt(xx,yy,1.925)
  for z in [1.75,1.82,1.89]:box('Machined_Door_Sill_Track',0,.075,z,2.8,.025,.022,'Steel',.004)
  screen(0,3.08,1.77,.90,.25,'Lift');box('Call_Plate_StandOff',1.57,1.40,1.85,.16,.43,.23,'Powder',.012);box('Lift_Call_Face',1.57,1.40,1.98,.23,.59,.045,'Steel',.014)
  for yy in [1.36,1.55]:lamp(1.57,yy,2.005,'LensGreen' if yy>1.4 else 'LensOff',.033)
  tag(1.57,1.18,2.004,.18,.08,21)
 group(lambda:landing(0),yaw=180)
 # The upper landing receives the same manufactured door detail, at its existing height.
 group(lambda:landing(0),yaw=180,y=16)
 for y in [3.6,7.4,11.2]:
  box('Hoist_Service_Hatch',0,y,-1.699,1.62,.95,.035,'Powder',.018)
  for x in [-.68,.68]:
   for yy in [y-.35,y+.35]:cyl('Hatch_Captive_Bolt',(x,yy,-1.72),(x,yy,-1.735),.014,'Steel',6)
 save('OD_VL_FreightHoist','Environment')

def workflowfloor():
 new()
 for x,z,i in [(-3.1,-3.25,8),(-2.7,3.7,11),(3.2,-4.65,10)]:
  w=1.20;d=.30;o=mesh('Floor_Process_Print',[(x-w/2,.013,z-d/2),(x+w/2,.013,z-d/2),(x+w/2,.013,z+d/2),(x-w/2,.013,z+d/2)],[(0,3,2,1)],'Tag',0)
  if o.data.polygons[0].normal.z<0:o.data.flip_normals()
  uv=o.data.uv_layers.new(name='UVMap');u=i%4/4;v=1-(i//4+1)/8;coords=[(u+.249,v+.001),(u+.001,v+.001),(u+.001,v+.124),(u+.249,v+.124)]
  for p in o.data.polygons:
   for li in p.loop_indices:uv.data[li].uv=coords[o.data.loops[li].vertex_index]
  o['display_uv']=True
 save('OD_E03_WorkflowFloor','Environment')
builders={**{'WarehouseRack_'+str(i):(lambda i=i:rack(i)) for i in range(4)},**{'PalletLoad_'+str(i):(lambda i=i:palletload(i)) for i in range(2)},'PalletTruck':palletjack,'ReceivingInspection':receiving,'InstrumentedTestRig':dummy,'ExchangeControl':testconsole,'SealedMealInspection':mealcheck,'MealRegenerationCabinet':regen,'SealedMealCart':mealtrolley,'ControlledNutritionBank':issue,'NutritionTransferCart':sealedcase,'ClosedPPEReturn':dirtyreturn,'ContaminatedBagSealer':bagseal,'BootSoleWasher':bootwash,'CleanPPEDispenser':cleanppe,'DeconExitCheck':aircheck,'PipedDeconShower':shower,'ElectricalSwitchgear':power,'ProcessControlBay':process,'VL_FreightHoist':lift,'E03_WorkflowFloor':workflowfloor}
for name,fn in builders.items():
 if os.getenv('OD_ONLY') and name not in os.environ['OD_ONLY'].split(','):continue
 if not os.getenv('OD_ONLY') and 'OD_'+name in b.manifest:continue
 print('BUILD',name,flush=True);fn()
print('OPERATIONAL BUILD COMPLETE',flush=True)
