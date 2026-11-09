"""B4 laboratory identity and first-person detail pass. Author Song Ye Chan."""
import sys,math,json,bpy
from pathlib import Path
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H))
from common import *

def bench(w=2.4,d=.85):c.tabletop(w,d);pedestal(-w/2+.37,.55,min(.65,d-.1))
def probe(x,y,z):
 cyl('Probe_Grip',(x,y,z-.09),(x,y,z+.05),.012,'Dark',20);cyl('Probe_Tip',(x,y,z+.05),(x,y,z+.09),.004,'Steel',12)
def breadboard_station(w=2.4,metrology=False):
 reset();bench(w,1.45 if metrology else .86);z=-.04;optical(-.28,.95,z,1.25,.72 if metrology else .54);stage(-.30,1.00,z)
 for x in [-.80,.24]:box('Optical_Bridge_Column',x,1.27,z-.22,.045,.57,.06,'Dark',.005)
 box('Optical_Bridge',-.28,1.56,z-.22,1.09,.075,.10,'Dark',.006);sensor(-.28,1.40,z-.18)
 cyl('Calibration_Coupon',(-.30,1.105,z),(-.30,1.145,z),.06,'Steel',32)
 instrument(w/2-.36,.93,-.09,.54,.29,.40,43)
 cable('Optical_Signal',[(-.28,1.44,z-.26),(-.34,1.56,z-.28),(.30,1.56,z-.28),(.39,1.00,-.30),(w/2-.35,1.00,-.30)],.003)
 paper(-w/2+.29,.919,.16,.21,.26,2);label(-.28,1.56,z-.164,.24,.045,6)
 if metrology:
  enclosure(-.28,.99,-.04,1.35,.72,.85);tray(.63,.93,.46,.50,.26);probe(.60,.95,.46)
 save('LB_MetrologyIsland' if metrology else 'LB_OpticalCalibrationBench')
breadboard_station(2.5,True);breadboard_station()

reset();bench(2.1,.86)
instrument(-.55,.93,-.10,.66,.32,.45,44);instrument(.24,.93,-.15,.56,.26,.36,46)
box('ESD_Mat',.15,.919,.20,1.12,.006,.36,'Teal',.004)
box('Device_Under_Test',.10,.96,.19,.31,.07,.18,'Dark',.006)
for i in range(5):port(-.02+i*.055,.96,.284,.007)
for i in range(2):
 x=-.39+i*.085;cable('BNC_Test_Lead',[(x,1.00,.143),(x,1.00,.27),(-.30+i*.08,.93,.32),(-.03+i*.08,.93,.30),(-.03+i*.08,.96,.29)],.0025)
probe(.55,.935,.22);paper(.86,.919,.16,.20,.29,5);label(.10,1.00,.284,.23,.035,13)
save('LB_ElectronicsBench')

reset();bench(2.1,.86);optical(-.40,.95,-.02,.93,.62);enclosure(-.40,.99,-.04,.96,.70,.68)
for x in [-.68,-.12]:cyl('Actuator_Guide',(x,1.00,-.12),(x,1.56,-.12),.017,'Steel',20)
box('Actuator_Bridge',-.40,1.55,-.12,.65,.10,.20,'Dark',.008);cyl('Actuator_Body',(-.40,1.24,-.12),(-.40,1.55,-.12),.068,'Coat',24);cyl('Piston',(-.40,1.08,-.12),(-.40,1.24,-.12),.023,'Steel',20)
box('Test_Fixture',-.40,1.045,-.12,.23,.07,.21,'Steel',.008);instrument(.57,.93,-.12,.58,.35,.42,45)
c.emergency(.89,1.00,.15);label(-.40,1.56,.307,.34,.055,8);paper(.48,.919,.27,.25,.22,5)
cable('Pressure_Line',[(-.40,1.42,-.20),(-.24,1.46,-.30),(.16,1.18,-.32),(.46,1.09,-.34)],.005,'Rubber')
save('LB_TestChamberBench')

reset();bench(2.65,.86);instrument(-.74,.93,-.13,.73,.33,.42,46);instrument(.12,.93,-.17,.61,.26,.36,49)
optical(.86,.95,-.01,.55,.49);stage(.84,1.00,-.02);sensor(.85,1.20,-.18)
box('Probe_Pedestal',.85,1.10,-.24,.06,.22,.06,'Dark',.006)
for i in range(3):cable('Signal_Input',[(-.51+i*.07,1.00,.10),(-.45+i*.07,.93,.22),(.20+i*.05,.93,.25),(.52,1.02,.13),(.73,1.12,.06)],.0024)
paper(-.80,.919,.26,.30,.23,4);label(.85,1.23,-.086,.10,.035,13);save('LB_SignalAnalysisBench')

def physiology(acquisition=False):
 reset();w,d=(.94,.65) if acquisition else (.59,.50);c.cartbase(w,d)
 for x in [-w/2+.045,w/2-.045]:box('Cart_Column',x,.70,-d/2+.055,.035,1.02,.045,'Steel',.004)
 for y in [.48,.94]:box('Instrument_Shelf',0,y,0,w,.035,d,'Steel',.006)
 instrument(0,.97,-.015,w-.05,.26,d-.04,49 if acquisition else 47)
 instrument(0,.50,-.02,w-.08,.22,d-.05,46 if acquisition else 47)
 if acquisition:
  for i in range(5):port(-.30+i*.14,.59,d/2+.01,.012)
  c.screen(0,1.43,-.16,.63,.30,49);box('Screen_Mast',0,1.24,-.22,.045,.40,.045,'Steel',.006)
 else:
  box('Headbox_Dock',0,1.35,-.19,.43,.23,.09,'Coat',.01);label(0,1.39,-.142,.35,.08,1)
  for i in range(4):port(-.13+i*.086,1.28,-.14,.009)
 for i in range(3):
  x=-.16+i*.14;cable('Stored_Lead',[(x,1.27,-.11),(x+.02,1.22,.04),(x+.035,.81,.10),(x-.03,.75,.08),(x-.05,1.0,.07)],.0025)
  box('Probe_Dock',x-.05,.99,.07,.034,.05,.028,'Coat',.004)
 box('Battery_Module',0,.32,0,w*.66,.15,d*.66,'Dark',.009);label(0,.33,d*.335,w*.46,.07,5)
 save('LB_AcquisitionCart' if acquisition else 'LB_PhysiologyCart')
physiology();physiology(True)

reset();c.tabletop(2.3,.85);pedestal(-.81,.52,.64)
box('Prep_Work_Mat',0,.919,.02,2.13,.006,.72,'Teal',.006)
box('Service_Backboard',0,1.28,-.35,2.10,.70,.045,'Coat',.01)
instrument(-.67,.93,-.16,.67,.32,.33,47);label(-.67,1.47,-.32,.49,.11,4)
# Clean consumables: small sealed foil sleeves with corner heat seals.
tray(-.15,.933,-.02,.37,.44)
for i in range(3):
 x=-.25+i*.10;box('Sealed_Electrode_Pouch',x,.95,-.11+i*.055,.09,.006,.14,'Paper',.003)
 for zz in [-.17+i*.055,-.05+i*.055]:box('Pouch_Seal',x,.954,zz,.084,.001,.008,'Mark',.0005)
 cyl('Electrode_In_Pouch',(x,.955,-.11+i*.055),(x,.957,-.11+i*.055),.025,'Fabric',24)
# A fitted channel panel with individual ports, cable guides and keyed lead connectors.
box('Isolated_Headbox',.41,1.31,-.30,.45,.25,.07,'Dark',.01);label(.41,1.36,-.262,.39,.07,1)
for i in range(4):
 x=.26+i*.10;port(x,1.25,-.26,.009);box('Cable_Comb',x,1.17,-.28,.025,.035,.032,'Coat',.003)
 cable('Patient_Lead',[(x,1.25,-.24),(x,1.14,-.20),(x+.015,1.0,-.10),(x+.035,.96,.12),(x-.025,.96,.18)],.0018)
 cyl('Pad_Foam',(x-.025,.95,.18),(x-.025,.955,.18),.026,'Paper',24);cyl('Gel_Contact',(x-.025,.956,.18),(x-.025,.958,.18),.016,'Fabric',24);cyl('Snap_Connector',(x-.025,.959,.18),(x-.025,.966,.18),.007,'Steel',16)
tray(.45,.934,.12,.50,.38)
# Separate used-lead return tray, opened sleeve, swab and handled inspection tools.
tray(.92,.934,.05,.29,.54);label(.92,.953,.328,.23,.040,3)
cable('Removed_Lead',[(.83,.955,-.12),(.99,.955,-.11),(1.01,.955,.05),(.87,.955,.10),(.84,.955,-.01),(.97,.957,-.04)],.002)
cyl('Returned_Connector',(.97,.96,-.07),(.97,.96,-.03),.009,'Steel',16)
for i in range(2):box('Opened_Peel_Pack',.88+i*.09,.954,.22,.07,.004,.09,'Paper',.002)
cyl('Swab_Stick',(-.35,.931,.19),(-.35,.931,.34),.002,'Steel',12);cyl('Swab_Tip',(-.35,.932,.16),(-.35,.932,.20),.006,'Paper',16)
paper(-.79,.925,.20,.29,.31,1);cyl('Fine_Marker',(-.54,.932,.13),(-.54,.932,.31),.004,'Dark',16)
for x in [.15,.19]:cyl('Forceps_Arm',(x,.933,.20),(x+.006,.935,.35),.003,'Steel',12)
label(-.15,1.47,-.32,.40,.10,2);save('LB_ElectrodePrepBench')

reset();bench(1.8,1.3);tray(-.48,.933,.12,.66,.50)
for i in range(3):sensor(-.66+i*.18,1.00,.10)
optical(.33,.95,-.12,.65,.48);stage(.33,1.00,-.12);instrument(-.42,.93,-.39,.67,.24,.31,44)
paper(.37,.919,.39,.33,.30,2);cable('Spare_Probe_Lead',[(.10,.93,.08),(.23,.93,.18),(.58,.93,.15),(.61,.94,-.06),(.45,.99,-.12)],.003)
save('LB_SensorPrepBench')

reset();c.hollow_cabinet(.88,2.04,.82)
for j in range(6):
 y=.28+j*.27;instrument(0,y,-.015,.80,.235,.70,[49,44,46][j%3])
 for x in [-.40,.40]:box('Rack_Ear',x,y+.11,.35,.025,.23,.025,'Steel',.002)
label(0,1.97,.418,.55,.065,10)
for j in range(3):cable('Rack_Patch',[(.24,.60+j*.27,.38),(.35,.55+j*.27,.42),(.36,.40+j*.27,.42),(.25,.33+j*.27,.38)],.003)
save('LB_DAQRack')

reset();box('Force_Plate_Base',0,.07,0,2.76,.14,2.76,'Steel',.018)
for x in [-.64,.64]:
 box('Isolated_Force_Plate',x,.153,0,1.18,.026,2.28,'Dark',.006)
 for zz in [-.93,.93]:
  for xx in [x-.46,x+.46]:cyl('Load_Cell',(xx,.10,zz),(xx,.139,zz),.06,'Coat',20)
 for zz in [-1.0,1.0]:box('Stance_Reference',x,.168,zz,.32,.002,.025,'Mark',.0004)
for x in [-1.29,1.29]:
 for z in [-1.28,1.28]:
  box('Tracking_Mast',x,1.45,z,.075,2.87,.075,'Dark',.007)
  for y in [.60,1.50,2.35]:sensor(x,y,z+.07)
  for y in [.4,.8,1.2,1.6,2.0,2.4]:box('Mast_Reference',x,y,z+.039,.026,.012,.002,'Mark',.0003)
 box('Overhead_Side_Rail',x,2.88,0,.08,.07,2.65,'Steel',.006)
box('Overhead_Rear_Rail',0,2.88,-1.28,2.65,.07,.08,'Steel',.006)
instrument(.85,.18,-1.09,.57,.24,.32,48);label(0,.18,1.36,.54,.08,9)
save('LB_PrecisionPlatform')

reset()
for x in [-1.23,1.23]:box('Target_Foot',x,.04,0,.40,.08,.86,'Steel',.009);box('Target_Upright',x,1.23,-.22,.075,2.38,.10,'Steel',.007)
for y in [.38,1.15,2.30]:box('Target_Crossbeam',0,y,-.22,2.54,.085,.10,'Steel',.006)
for x,y in [(-.84,1.77),(0,1.20),(.84,1.77)]:
 cyl('Load_Cell_Body',(x,y,-.23),(x,y,-.06),.08,'Coat',24);cyl('Impact_Damper',(x,y,-.06),(x,y,.06),.10,'Rubber',24)
 box('Replaceable_Target',x,y,.095,.64,.64,.065,'Coat',.014);box('Impact_Insert',x,y,.132,.50,.50,.007,'Rubber',.008)
 for xx in [x-.28,x+.28]:
  for yy in [y-.28,y+.28]:screw(xx,yy,.131)
 for i in range(3):
  r=.06+i*.065;cable('Target_Ring',[(x+r*math.cos(t*math.pi/16),y+r*math.sin(t*math.pi/16),.137) for t in range(33)],.0012,'Mark')
 cable('Load_Signal',[(x,y,-.25),(x,1.1,-.31),(x,.48,-.31),(0,.48,-.31)],.003)
instrument(0,.13,0,.72,.25,.43,48);save('LB_AdaptiveTargetArray')

reset()
for z in [-2.46,0,2.46]:
 for x in [-1.25,1.25]:
  box('Gate_Foot',x,.045,z,.16,.09,.27,'Steel',.007);box('Optical_Gate_Post',x,1.45,z,.07,2.9,.08,'Dark',.006)
  for y in [.60,1.20,1.80,2.40]:sensor(x,y,z+.06)
 box('Gate_Overhead',0,2.87,z,2.57,.075,.09,'Steel',.005)
 label(0,2.87,z+.05,.31,.05,6)
for x in [-1.28,1.28]:box('Protected_Base_Raceway',x,.10,0,.06,.09,5.14,'Coat',.007)
instrument(-.95,.16,-2.16,.46,.23,.32,50);save('LB_TrajectoryGantry')

reset()
for x in [-1.02,1.02]:
 box('Rig_Base_Rail',x,.065,0,.22,.13,2.54,'Steel',.012);box('Rig_Column',x,1.50,-.65,.13,2.85,.15,'Steel',.009)
 for z in [-1.06,1.06]:cyl('Level_Bolt',(x,.09,z),(x,.17,z),.027,'Dark',16)
box('Actuator_Crosshead',0,2.82,-.65,2.17,.18,.30,'Coat',.015)
for x in [-.72,.72]:cyl('Precision_Guide',(x,.27,-.65),(x,2.73,-.65),.028,'Steel',24)
box('Load_Carriage',0,1.67,-.65,1.64,.14,.25,'Dark',.010);cyl('Hydraulic_Actuator',(0,2.04,-.65),(0,2.73,-.65),.13,'Coat',32);cyl('Piston_Rod',(0,1.75,-.65),(0,2.04,-.65),.045,'Steel',24);cyl('Load_Cell',(0,1.49,-.65),(0,1.66,-.65),.09,'Steel',24)
box('Grip_Attachment',0,1.40,-.50,.65,.10,.14,'Dark',.015);box('Stance_Platform',0,.07,.45,1.65,.14,1.60,'Dark',.012)
for x in [-1.0,1.0]:box('Side_Shield',x,1.16,-.19,.009,1.74,1.40,'Glass',.001)
instrument(.62,.20,-1.01,.68,.30,.41,45);c.emergency(-1.02,1.1,.55);label(0,2.82,-.493,.57,.09,14)
cable('Hydraulic_Service',[(.12,2.50,-.72),(.43,2.63,-.84),(.88,2.3,-.86),(.88,.53,-.86),(.62,.40,-1.1)],.013,'Rubber')
save('LB_LoadResistanceRig')

# The approved workstation geometry/handedness stays; only fake line writing is replaced.
bpy.ops.wm.open_mainfile(filepath=str(R/'SourceAssets/B4_DeskAndCollision/PD_ProtocolTable.blend'));c.reset if False else None
b.mats={m.name.replace('B4O_','').replace('BX_',''):m for m in bpy.data.materials};materials()
for o in list(bpy.context.scene.objects):
 if o.name.startswith(('Printed_Record_Row','Document_Header')):bpy.data.objects.remove(o,do_unlink=True)
for j,(x,z,a) in enumerate([(-.93,.21,-6),(.89,.16,5)]):
 before=set(bpy.context.scene.objects);paper(x,.944,z,.40,.50,4 if j==0 else 3)
 m=Matrix.Translation(Vector(b.xyz(x,0,z)))@Matrix.Rotation(-math.radians(a),4,'Z')@Matrix.Translation(-Vector(b.xyz(x,0,z)))
 for o in set(bpy.context.scene.objects)-before:o.matrix_world=m@o.matrix_world
paper(.988,.993,-.43,.37,.24,5);save('LB_RecordWorkstation',False)

bpy.ops.wm.open_mainfile(filepath=str(R/'SourceAssets/B4_LayoutPolish/BP_BenchKit_3.blend'))
b.mats={m.name.replace('B4O_','').replace('BP_',''):m for m in bpy.data.materials};materials()
for o in list(bpy.context.scene.objects):
 if o.name.startswith('Printed_Protocol_Row'):bpy.data.objects.remove(o,do_unlink=True)
paper(.009,.034,-.015,.24,.30,1);save('LB_RecordKit',False)
print('LAB_MODELS_COMPLETE',len(manifest),flush=True)
