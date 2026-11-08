import sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *

reset();tabletop(1.8,.82)
box('Intake_Pedestal',-.62,.41,-.02,.45,.71,.64,'Coat',.018)
for y in [.29,.53]:box('Issue_Drawer',-.62,y,.31,.39,.20,.025,'Steel',.007);pull(-.62,y+.05,.33,.20)
screen(-.28,1.23,-.14,.70,.39,23,True,.915);keyboard(-.35,.95,.20)
box('Wristband_Scanner',.50,1.04,.12,.22,.23,.32,'Coat',.025);box('Scanner_Window',.50,1.08,.287,.14,.07,.008,'Lens',.004)
for i in range(4):box('Wristband_Tray',.30+i*.12,.94,-.16,.08,.04,.22,'Paper',.004)
buttons(.68,1.00,.29,1);label(.54,1.16,.289,.15,.04);save('SubjectCheckIn')

reset()
for x in [-.59,.59]:
 box('Bench_Seat',x,.49,0,.72,.13,.62,'Coat',.045);box('Bench_Back',x,.93,-.27,.72,.70,.13,'Coat',.045);box('Bench_Support',x,.25,0,.12,.45,.45,'Steel',.01)
 for xx in [x-.40,x+.40]:tube('Rounded_Armrest',[(xx,.49,.19),(xx,.72,.19),(xx,.74,-.22),(xx,.49,-.22)],.027,'Steel')
box('Bench_Spine',0,.30,0,2.0,.10,.10,'Steel',.012)
for x in [-.72,.72]:box('Anchored_Foot',x,.035,0,.4,.07,.72,'Steel',.012)
save('EscortBench')

reset();cabinet(.82,1.05,.66);screen(0,1.47,-.03,.67,.40,24,True,1.08)
box('Duty_Control_Deck',0,1.1,.25,.85,.08,.3,'Coat',.018);buttons(-.15,1.09,.41,3);emergency(.30,1.25,.35)
tube('Handset',[(.30,1.43,.1),(.31,1.65,.1),(.42,1.65,.1),(.42,1.43,.1)],.025,'Dark');tube('Comms_Lead',[(.35,1.43,.1),(.46,1.32,.16),(.46,1.12,.16),(.33,1.06,.2)],.006)
label(0,.68,.36,.44,.13,42);save('GuardControlPost')

reset();glass_panel(0,-1.20,3.4,2.55)
for side in [-1,1]:
 old=set(bpy.context.scene.objects);glass_panel(0,0,2.4,2.55);transform(set(bpy.context.scene.objects)-old,side*1.70,0,0,90)
box('Booth_Service_Header',0,2.50,0,3.50,.15,2.50,'Steel',.015)
box('Booth_Desk',0,.90,-.57,3.15,.07,.88,'Coat',.02)
for x in [-1.3,1.3]:box('Booth_Desk_Leg',x,.44,-.65,.08,.85,.55,'Steel',.008)
for x,k in [(-.72,25),(.72,26)]:screen(x,1.35,-.73,.83,.47,k,True,.94);keyboard(x,.96,-.30)
for x in [-.82,.82]:box('Booth_Ceiling_LED',x,2.40,-.15,.80,.06,.13,'Lamp',.01)
save('ObservationBooth')

reset()
for side in [-1,1]:glass_panel(side*1.37,0,1.25,2.5)
for x in [-.70,.70]:box('Gate_Stile',x,1.25,0,.09,2.5,.15,'Steel',.009)
box('Open_Gate_Header',0,2.49,0,4.05,.12,.18,'Steel',.012)
box('Gate_Access_Housing',.84,1.30,.12,.23,.38,.12,'Dark',.014);screen(.84,1.35,.19,.15,.15,24);buttons(.84,1.19,.19,1)
save('ScreenedEntry')

reset();box('Fitting_Base',0,.04,0,1.15,.08,.85,'Steel',.018)
for x in [-.43,.43]:box('Accessory_Column',x,1.10,-.15,.06,2.15,.08,'Steel',.008)
box('Fitting_Crossbar',0,2.13,-.15,1.05,.08,.12,'Steel',.008)
for x in [-.22,.22]:
 tube('Harness_Support',[(x,1.95,-.14),(x,1.83,0),(x,1.1,0)],.012,'Steel');box('Soft_Sensor_Harness',x,1.48,.02,.26,.56,.06,'Fabric',.025)
 for y in [1.27,1.48,1.69]:cyl('Body_Tracking_Tag',(x,y,.053),(x,y,.074),.033,'Paper',20)
box('Fitting_Tray',0,.85,.15,.96,.04,.48,'Coat',.012)
for x in [-.3,0,.3]:case(x,.88,.15,.24,.11,.23)
label(0,2.13,-.08,.55,.06);save('SensorFittingStand')

reset();box('Measurement_Base',0,.04,0,2.8,.08,2.8,'Steel',.018);box('Force_Plate',0,.084,0,2.55,.008,2.55,'Floor',.002)
for i in range(-4,5):
 box('Measurement_Grid',i*.28,.09,0,.008,.004,2.5,'Mark',0);box('Measurement_Grid',0,.09,i*.28,2.5,.004,.008,'Mark',0)
for x in [-1.32,1.32]:
 box('Sensor_Pylon',x,1.45,-.95,.10,2.85,.15,'Steel',.012)
 for y in [1.2,2.35]:cyl('Precision_Optics',(x,y,-.84),(x,y,-.77),.05,'Lens',24)
box('Precision_Header',0,2.86,-.95,2.75,.12,.18,'Steel',.014)
screen(0,2.68,-.82,.65,.18,27);save('PrecisionPlatform')

reset()
for x in [-1.10,0,1.10]:
 box('Adjustable_Target_Base',x,.06,0,.65,.12,.90,'Steel',.02);box('Vertical_Track',x,1.25,-.08,.14,2.35,.16,'Steel',.012)
 for y in [.6,1.0,1.4,1.8,2.2]:box('Height_Index',x+.082,y,-.06,.008,.02,.08,'Paper',0)
 y=1.3+(.35 if x<0 else -.15 if x>0 else .05);box('Sliding_Carriage',x,y,.07,.32,.38,.16,'Dark',.015)
 cyl('Replaceable_Target',(x,y,.15),(x,y,.27),.30,'Coat',40);cyl('Target_Sensor',(x,y,.271),(x,y,.278),.085,'Mark',28)
 knob(x+.19,y,.1,.035);tube('Target_Cable',[(x,y,-.13),(x+.12,y-.25,-.2),(x+.12,.15,-.2),(x,.12,0)],.009)
save('AdaptiveTargetArray')

reset();box('Resistance_Base',0,.06,0,2.25,.12,2.60,'Steel',.022)
for x in [-.91,.91]:
 box('Load_Rig_Column',x,1.48,-.88,.13,2.88,.15,'Steel',.012)
 cyl('Pulley_Axle',(x-.12,2.65,-.82),(x+.12,2.65,-.82),.13,'Dark',32)
 tube('Tension_Cable',[(x,1.0,-.90),(x,2.70,-.90),(x,2.70,-.65),(x,1.48,.7)],.009,'Steel')
 cyl('Hand_Grip',(x-.12,1.47,.70),(x+.12,1.47,.70),.025,'Rubber',20)
 for i in range(10):box('Load_Stack',x,.22+i*.065,-.93,.40,.052,.42,'Dark',.009)
 box('Stack_Guard',x,.67,-.65,.47,1.0,.025,'Glass',.004)
box('Rig_Overhead_Beam',0,2.85,-.88,2.0,.16,.20,'Steel',.012);screen(0,1.45,-.70,.67,.40,28)
emergency(0,1.0,-.66);box('Subject_Stance_Mat',0,.128,.42,1.5,.012,1.15,'Rubber',.01)
save('LoadResistanceRig')

reset();box('Pursuit_Track_Base',0,.035,0,3.8,.07,1.0,'Steel',.02)
for x in [-1.65,1.65]:box('Pursuit_Support',x,1.25,-.15,.13,2.45,.2,'Steel',.012)
for y in [1.1,2.2]:
 box('Linear_Target_Rail',0,y,-.1,3.55,.075,.12,'Steel',.009)
 for i in range(12):box('Encoder_Scale',-1.55+i*.28,y+.055,-.03,.025,.007,.04,'Paper',0)
 x=-.7 if y<2 else .85;box('Servo_Carriage',x,y,.035,.24,.24,.2,'Coat',.015);cyl('Optical_Pursuit_Target',(x,y,.15),(x,y,.19),.18,'Mark',32)
box('Stepper_EndDrive',1.82,1.55,-.15,.22,.46,.34,'Dark',.02);screen(-1.52,.65,.12,.38,.23,29)
save('PursuitTrack')

reset();box('Stimulus_Wall',0,1.35,0,3.5,2.6,.30,'Dark',.025)
for i in range(15):
 x=(i%5-2)*.60;y=.65+(i//5)*.65;cyl('Stimulus_Bezel',(x,y,.15),(x,y,.19),.17,'Steel',24);cyl('Stimulus_Response_Surface',(x,y,.195),(x,y,.207),.14,'Indicator' if i in [2,5,13] else 'Rubber',28)
screen(0,2.4,.17,.85,.21,30)
for x in [-1.3,1.3]:box('Wall_Anchor_Foot',x,.06,.05,.48,.12,.78,'Steel',.015)
save('StimulusWall')

reset();tabletop(3.4,1.35)
for x,k in [(-.80,31),(.80,32)]:screen(x,1.32,-.28,1.08,.55,k,True,.915);keyboard(x,.95,.23)
for x in [-1.38,1.38]:
 box('Control_Wedge',x,1.01,.17,.35,.19,.42,'Steel',.018);knob(x,1.04,.39,.03);buttons(x,.96,.39,3)
emergency(1.38,1.17,.38);box('Instrument_Computer',-1.30,.48,-.17,.36,.62,.64,'Dark',.016);vent(-1.30,.49,.16,.25,.38)
save('OperatorIsland')

reset();cabinet(.88,2.05,.75)
for j in range(5):
 y=.40+j*.31;box('Rack_Instrument',0,y,.395,.78,.26,.06,'Steel',.01);screen(-.15,y,.435,.34,.14,33);knob(.25,y,.43)
 for x in [-.36,.36]:pull(x,y,.43,.045)
box('Rack_Patchbay',0,1.92,.407,.77,.12,.05,'Dark',.005)
for x in [-.3,-.2,-.1,0,.1,.2,.3]:cyl('BNC_Input',(x,1.92,.44),(x,1.92,.47),.019,'Steel',16)
save('CalibrationRack')

reset();box('Timing_Base',0,.05,0,.6,.10,.65,'Steel',.014);box('Timing_Column',0,1.20,0,.12,2.3,.13,'Steel',.01)
for y in [.75,1.28,1.81]:screen(0,y,.09,.43,.28,34)
for y in [.51,1.04,1.57]:buttons(0,y,.09,3)
tube('Clock_Link',[(0,.22,-.08),(.16,.18,-.08),(.16,.15,.10),(.25,.15,.18)],.009);save('TimingReferenceTower')

reset();cartbase();box('Cart_Instrument_Cabinet',0,.62,0,.76,.72,.55,'Coat',.018);box('Cart_Top',0,1.0,0,.90,.06,.66,'Steel',.014)
screen(0,1.40,-.10,.63,.37,35,True,1.04);keyboard(0,1.06,.20)
for y in [.45,.67]:box('Acquisition_Unit',0,y,.295,.65,.16,.04,'Dark',.006);screen(-.12,y,.32,.27,.09,34);knob(.23,y,.32,.018)
for side in [-1,1]:tube('Cart_Handle',[(side*.42,.9,-.2),(side*.48,1.1,-.2),(side*.48,1.1,.2),(side*.42,.9,.2)],.022,'Steel')
save('MobileAcquisitionCart')

reset();hollow_cabinet(1.65,1.95,.70)
# Recessed open storage cells with solid backing and actual test articles.
box('Cabinet_Interior',0,1.13,-.29,1.48,1.43,.03,'Dark',.005)
for j in range(4):
 y=.45+j*.36;box('Article_Tray',0,y,.02,1.43,.025,.57,'Steel',.005)
 for i in range(5):
  x=-.56+i*.28
  if j%2==0:
   cyl('Instrumented_Test_Disc',(x,y+.12,.18),(x,y+.12,.27),.10,'Coat',24);cyl('Disc_ID',(x,y+.12,.272),(x,y+.12,.274),.044,'Mark',20)
  else:box('Calibrated_Projectile',x,y+.11,.18,.17,.19,.15,'Coat',.035)
label(0,1.91,.38,.65,.07,41);save('ProjectileCabinet')

reset();cartbase(1.15,.78)
for y in [.31,.73]:
 box('Recovery_Tray',0,y,0,1.07,.055,.70,'Steel',.014)
 for x in [-.34,0,.34]:case(x,y+.033,0,.30,.22,.52)
tube('Trolley_Pushbar',[(-.52,.26,-.32),(-.52,1.02,-.32),(.52,1.02,-.32),(.52,.26,-.32)],.026,'Steel')
save('TargetRecoveryTrolley')

reset()
for x in [-.77,.77]:box('Case_Rack_Post',x,1.12,0,.06,2.23,.77,'Steel',.008)
box('Rack_Back',0,1.12,-.36,1.6,2.23,.035,'Steel',.006)
for j in range(4):
 y=.16+j*.52;box('Case_Shelf',0,y,0,1.6,.035,.78,'Steel',.006)
 for i in range(2):case((i-.5)*.76,y+.02,.02,.69,.36,.64)
save('EquipmentCaseRack')

reset();tabletop(2.3,.85);box('Electrode_Prep_Mat',0,.921,.03,1.75,.008,.62,'Rubber',.008)
for x in [-.8,-.4,0,.4,.8]:
 box('Recessed_Sensor_Tray',x,.95,.12,.30,.05,.32,'Steel',.008)
 for j in range(3):cyl('Electrode',(x-.08+j*.08,.982,.12),(x-.08+j*.08,.997,.12),.025,'Paper',20)
box('Preparation_Backboard',0,1.28,-.35,2.1,.70,.06,'Coat',.01)
screen(-.56,1.30,-.30,.72,.35,36)
for x in [.18,.42,.66]:
 tube('Sensor_Lead',[(x,1.48,-.29),(x+.06,1.22,-.25),(x,.99,-.12),(x-.05,.97,.12)],.006);box('Lead_Connector',x-.05,.98,.12,.035,.035,.08,'Steel',.004)
save('ElectrodePrepBench')

reset();box('Recliner_Base',0,.15,0,.78,.30,1.58,'Steel',.035);box('Treatment_Seat',0,.62,.10,.83,.16,.77,'Fabric',.055)
o=box('Reclined_Back',0,1.04,-.48,.83,.93,.16,'Fabric',.055);o.rotation_euler.x=math.radians(-18)
box('Padded_Headrest',0,1.46,-.64,.40,.26,.18,'Fabric',.04);box('Foot_Rest',0,.45,.77,.76,.10,.63,'Fabric',.03)
for x in [-.54,.54]:box('Arm_Support',x,.82,.05,.15,.12,.86,'Coat',.025)
cyl('Hydraulic_Piston',(0,.29,-.16),(0,.55,-.16),.11,'Steel',24);buttons(.55,.83,.51,2);save('RecoveryRecliner')

reset();cartbase(.85,.68);box('Emergency_Cabinet',0,.61,0,.76,.71,.59,'Coat',.02)
for j in range(4):box('Treatment_Drawer',0,.36+j*.17,.309,.68,.14,.022,'Steel',.006);pull(0,.36+j*.17,.329,.27)
box('Cart_Worktop',0,1.0,0,.89,.06,.72,'Steel',.014);screen(0,1.35,-.12,.60,.33,37,True,1.04)
cyl('Medical_Cylinder',(.55,.24,-.1),(.55,1.02,-.1),.115,'Steel',28);cyl('Cylinder_Neck',(.55,1.02,-.1),(.55,1.13,-.1),.035,'Steel',16);tube('Supply_Hose',[(.55,1.13,-.1),(.7,1.05,.1),(.67,.35,.12),(.43,.3,.12)],.012)
save('EmergencyCart')

reset();box('Service_Base',0,.04,0,2.7,.08,.55,'Steel',.012);box('Service_Enclosure',0,1.15,-.06,2.6,2.2,.34,'Coat',.016)
for x in [-.85,0,.85]:
 box('Service_Access',x,.72,.123,.74,1.18,.02,'Steel',.007);pull(x,.95,.14,.19)
 for y in [1.55,1.85]:
  box('Recessed_Patch',x,y,.14,.64,.18,.035,'Dark',.005)
  for j in range(4):cyl('Quick_Connect',(x-.21+j*.14,y,.162),(x-.21+j*.14,y,.19),.028,'Steel',16)
 label(x,2.10,.12,.50,.07,41)
save('UtilityServiceSpine')

reset();tabletop(2.5,1.05)
for x,k in [(-.61,38),(.61,39)]:screen(x,1.40,-.20,1.06,.59,k,True,.915)
keyboard(-.26,.95,.29);box('Jog_Wheel_Deck',.75,.98,.26,.32,.12,.32,'Steel',.018);cyl('Review_Jog_Wheel',(.75,1.05,.26),(.75,1.09,.26),.10,'Dark',28)
for x in [-1.05,1.05]:case(x,.92,-.04,.24,.15,.31)
save('DualReviewStation')

reset();tabletop(2.8,1.35)
for x,z in [(-.9,.2),(0,-.23),(.85,.2)]:
 box('Protocol_Folder',x,.929,z,.48,.025,.61,'Dark',.008)
 for i in range(3):box('Thin_Protocol_Sheet',x,.945+i*.0015,z,.44,.001,.57,'Paper',.0003)
box('Review_Table_Bracket',0,1.08,-.5,.12,.32,.10,'Steel',.008);screen(0,1.25,-.46,.72,.37,40)
save('ProtocolTable')

reset();cabinet(1.65,.88,.80)
# Four-sided basin, bottom, drainage and curved tap; no solid block filling the bowl.
for x in [-.76,.76]:box('Basin_Side',x,.97,0,.10,.20,.74,'Steel',.018)
for z in [-.34,.34]:box('Basin_Rim',0,.97,z,1.5,.20,.08,'Steel',.015)
box('Basin_Bottom',0,.88,0,1.45,.035,.64,'Steel',.01);cyl('Drain',(0,.90,0),(0,.904,0),.08,'Dark',24)
tube('Gooseneck_Tap',[(-.40,1,-.30),(-.40,1.40,-.30),(-.40,1.48,-.10),(-.40,1.38,.08)],.025,'Steel')
for x in [-.61,-.18]:knob(x,1.12,-.24,.03)
box('Drying_Backboard',0,1.50,-.37,1.62,.72,.06,'Coat',.01)
for x in [.15,.35,.55]:cyl('Drying_Peg',(x,1.55,-.32),(x,1.68,-.16),.013,'Steel',12)
save('EquipmentWashStation')

reset();hollow_cabinet(1.4,2.10,.65)
for y in [.81,1.16,1.51]:box('Clean_Return_Shelf',0,y,.01,1.31,.025,.58,'Steel',.005)
for x in [-.66,0,.66]:box('Clean_Window_Frame',x,1.29,.345,.045,1.46,.045,'Steel',.005)
for y in [.59,2.0]:box('Window_Horizontal_Frame',0,y,.345,1.35,.045,.045,'Steel',.005)
for x in [-.34,.34]:
 box('Clean_Return_Window',x,1.29,.355,.60,1.37,.025,'Glass',.004)
 for y in [.84,1.19,1.54]:case(x,y,.03,.43,.21,.46)
 pull(x*.16,1.15,.38,.07)
label(0,1.97,.36,.85,.09,42);save('CleanReturnCabinet')

reset();cabinet(2.65,.90,.65)
for i in range(5):
 x=(i-2)*.50;box('Drawer_Front',x,.49,.35,.46,.62,.035,'Coat',.008);pull(x,.71,.373,.20)
box('Upper_Storage_Back',0,1.63,-.27,2.65,1.45,.05,'Steel',.008)
for y in [1.04,1.57,2.10]:
 box('Supply_Shelf',0,y,0,2.65,.035,.62,'Steel',.008)
 for x in [-1,-.5,0,.5,1]:
  box('Sealed_Consumable_Box',x,y+.18,.03,.41,.32,.43,'Coat',.012);label(x,y+.21,.247,.27,.09,41)
save('ConsumableWall')

reset();box('Access_Console_Base',0,.05,0,.60,.10,.65,'Steel',.016);box('Interlock_Column',0,.82,-.08,.24,1.52,.25,'Coat',.018)
screen(0,1.47,.10,.40,.27,24);emergency(0,1.08,.11);buttons(0,.82,.11,2)
for y,mat in [(1.84,'Red'),(1.94,'Hazard'),(2.04,'Indicator')]:cyl('Status_Tower',(0,y,-.07),(0,y+.08,-.07),.045,mat,20)
save('TrialInterlock')

reset();cabinet(1.4,1.65,.9)
for x in [-.38,.38]:
 vent(x,.68,.48,.48,.72);screen(x,1.36,.48,.35,.20,28);knob(x,1.08,.48,.035)
for x in [-.52,.52]:tube('Protected_Power_Lead',[(x,.25,-.47),(x,.15,-.66),(x+.13,.1,-.66),(x+.17,.1,-.30)],.025,'Dark')
label(0,1.59,.48,.8,.07,42);save('ShieldPowerPack')

reset();box('Safety_Back',0,1.1,0,1.4,2.2,.13,'Coat',.016)
cyl('Extinguisher',(-.38,.30,.22),(-.38,1.17,.22),.13,'Red',24);cyl('Extinguisher_Valve',(-.38,1.17,.22),(-.38,1.29,.22),.035,'Steel',12);tube('Extinguisher_Hose',[(-.38,1.24,.22),(-.18,1.12,.28),(-.18,.55,.3)],.015)
box('Emergency_Kit',.29,1.18,.21,.59,.76,.29,'Steel',.022);pull(.29,1.18,.36,.20);label(.29,1.42,.362,.42,.12,42)
box('Safety_Foot',0,.04,0,1.5,.08,.55,'Steel',.012);save('SafetyEquipment')

reset();box('Acoustic_Frame',0,1.25,0,3.0,2.50,.18,'Steel',.015)
for j in range(6):
 for i in range(10):box('Absorption_Tile',(i-4.5)*.285,.16+j*.39,.12,.27,.36,.10,'Rubber',.02)
for x in [-1.15,1.15]:box('Acoustic_Foot',x,.045,0,.3,.09,.75,'Steel',.012)
save('AcousticPartition')

reset();tabletop(2.6,.90);screen(-.78,1.28,-.16,.70,.38,33,True,.915)
box('Device_Service_Cradle',.45,1.02,.04,1.14,.21,.58,'Steel',.025)
for x in [.10,.45,.80]:
 cyl('Open_Optics_Module',(x,1.14,.05),(x,1.27,.05),.095,'Steel',28);cyl('Optic_Glass',(x,1.273,.05),(x,1.28,.05),.079,'Lens',28)
box('Tool_Pegboard',.35,1.48,-.36,1.60,1.03,.06,'Dark',.01)
for x in [-.2,0,.2,.4,.6,.8,1]:cyl('Tool_Handle',(x,1.42,-.30),(x,1.64,-.30),.017,'Rubber',12);cyl('Tool_Shaft',(x,1.64,-.30),(x,1.82,-.30),.007,'Steel',10)
save('InstrumentServiceBay')

reset();cartbase(.72,.62)
for y in [.32,.70,1.08]:
 box('Supply_Cart_Tray',0,y,0,.70,.04,.62,'Steel',.012)
 for x in [-.18,.18]:case(x,y+.03,0,.29,.17,.43)
for x in [-.32,.32]:box('Tray_Column',x,.66,-.25,.04,.95,.04,'Steel',.006)
save('SmallSupplyCart')

reset();box('Reel_Base',0,.045,0,.65,.09,.7,'Steel',.012)
for x in [-.24,.24]:
 box('Reel_Support',x,.43,0,.06,.77,.14,'Steel',.01);cyl('Reel_Flange',(x-.02,.55,0),(x+.02,.55,0),.31,'Coat',36)
cyl('Cable_Drum',(-.20,.55,0),(.20,.55,0),.24,'Rubber',40)
for x in [-.17,-.1,-.03,.04,.11,.18]:
 pts=[(x,.55+.244*math.cos(a*math.tau/48),.244*math.sin(a*math.tau/48)) for a in range(49)];tube('Cable_Winding',pts,.012,'Dark')
tube('Reel_Handle',[(-.3,.8,0),(-.3,.93,0),(.3,.93,0),(.3,.8,0)],.02,'Steel');save('RollingCableReel')
print('OPERATIONS MODELS COMPLETE',flush=True)
