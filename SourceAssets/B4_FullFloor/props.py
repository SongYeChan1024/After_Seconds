import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
def bench_top(w=2.4):
 for x in [-w/2+.16,w/2-.16]:
  box('Bench_Frame',x,.44,0,.085,.78,.65,'Steel',.008);box('Level_Foot',x,.045,0,.18,.08,.75,'Steel',.014)
 box('Sealed_Worktop',0,.86,0,w,.07,.88,'Coat',.022);box('Cable_Raceway',0,.63,-.34,w-.2,.14,.16,'Steel',.012)
def instrument(x,kind):
 box('Instrument_Shell',x,1.10,-.04,.72,.40,.55,'Coat',.025);display(x-.09,1.10,.25,.40,.24,kind)
 for y in [1.03,1.17]:
  cyl('Encoder',(x+.22,y,.248),(x+.22,y,.285),.026,'Steel',24)
 vent(x,1.12,-.323,.5,.18)
 for i in range(3):cyl('BNC_Socket',(x-.20+i*.12,.955,.25),(x-.20+i*.12,.955,.28),.017,'Steel',16)
 tube('Coiled_Test_Lead',[(x+.1,.955,.28),(x+.3,.9,.30),(x+.35,.9,.05),(x+.1,.90,.02)],.007,'Dark')

reset();bench_top();instrument(-.56,7)
box('AntiStatic_Mat',.54,.901,.05,.85,.008,.60,'Rubber',.008)
for i in range(5):
 x=.25+i*.14;box('Probe_Dock',x,.93,-.13,.09,.05,.17,'Dark',.006);cyl('Probe',(x,.96,-.15),(x,1.10,-.15),.016,'Steel',16)
box('Sensor_Foam_Tray',.56,.94,.19,.68,.06,.20,'Dark',.01)
for i in range(4):cyl('Optical_Tag',(.32+i*.16,.97,.19),(.32+i*.16,1,.19),.038,'Paper',24)
save('SensorWorkbench','Props')
reset();bench_top(2.65);instrument(-.72,8)
box('Analyzer_Base',.57,1.03,-.05,.96,.28,.64,'Coat',.032)
cyl('Sealed_Optic_Chamber',(.57,1.17,-.10),(.57,1.45,-.10),.235,'Steel',48);cyl('Chamber_Lid',(.57,1.45,-.1),(.57,1.49,-.1),.245,'Dark',48)
for i in range(8):
 a=i*math.tau/8;cyl('Lid_Captive_Bolt',(.57+.20*math.cos(a),1.49,-.10+.20*math.sin(a)),(.57+.20*math.cos(a),1.51,-.10+.20*math.sin(a)),.014,'Steel',8)
for i in range(4):
 x=.25+i*.20;cyl('Sample_Cup',(x,1.18,.19),(x,1.27,.19),.035,'Steel',24);cyl('Cap',(x,1.27,.19),(x,1.29,.19),.038,'Dark',24)
display(.57,1.08,.283,.39,.14,8);save('AnalysisBench','Props')

reset()
box('Throwing_Lane',0,.018,0,2.15,.036,5.4,'Floor',.01)
for x in [-1.04,1.04]:
 box('Lane_Edge',x,.04,0,.045,.08,5.4,'Steel',.008)
 for z in [-2.55,-1.0,.55]:
  box('Screen_Post',x,1.14,z,.06,2.2,.06,'Steel',.008)
 box('Impact_Side_Glass',x,1.2,-1.0,.022,1.9,3.1,'Glass',.005)
box('Impact_Backstop',0,1.17,-2.55,2.10,2.30,.22,'Steel',.022)
for x in [-.52,0,.52]:
 box('Target_Isolation_Pad',x,1.2,-2.40,.46,.66,.08,'Rubber',.015)
 cyl('Instrumented_Target',(x,1.2,-2.35),(x,1.2,-2.31),.18,'Coat',48)
 cyl('Bullseye',(x,1.2,-2.308),(x,1.2,-2.30),.045,'Mark',32)
box('Release_Toeline',0,.042,1.6,1.85,.008,.06,'Mark',.002)
for z in [-2,-1,0,1]:box('Range_Index',-.85,.041,z,.18,.006,.025,'Mark',0)
display(0,2.08,-2.39,.75,.20,9);save('ThrowLane','Props')

reset()
for z in [-2.25,0,2.25]:
 for x in [-1.12,1.12]:
  box('Gantry_Foot',x,.045,z,.42,.09,.50,'Steel',.014);box('Extruded_Optical_Rail',x,1.45,z,.11,2.85,.12,'Steel',.012)
  box('IR_Tracker',x-(.10 if x>0 else -.10),1.85,z,.15,.14,.20,'Coat',.018)
  cyl('Tracker_Lens',(x,1.85,z+.10),(x,1.85,z+.13),.034,'Lens',24)
 box('Overhead_Calibration_Beam',0,2.85,z,2.35,.13,.15,'Steel',.014)
 for x in [-.65,0,.65]:box('Beam_Marker',x,2.77,z,.075,.02,.10,'Paper',.002)
for x in [-1.14,1.14]:box('Floor_Tracking_Rail',x,.022,0,.045,.044,5.2,'Steel',.005)
save('TrajectoryGantry','Props')

reset()
box('Booth_Back',0,1.3,-.95,2.10,2.6,.14,'Steel',.018)
for x in [-1.02,1.02]:box('Acoustic_Wing',x,1.2,-.12,.12,2.4,1.8,'Dark',.018)
for i in range(12):
 x=(i%4-1.5)*.35;y=.95+(i//4)*.35
 cyl('Stimulus_Bezel',(x,y,-.865),(x,y,-.82),.09,'Steel',32);cyl('Stimulus_Lens',(x,y,-.815),(x,y,-.805),.069,'Indicator' if i in [2,6,9] else 'Dark',32)
box('Response_Tray',0,.84,.03,1.65,.10,.48,'Coat',.025)
for x in [-.48,.48]:cyl('Response_Pad',(x,.90,.03),(x,.93,.03),.12,'Steel',36)
display(0,2.2,-.861,.95,.23,10);save('ReactionBooth','Props')

reset()
box('Diagnostics_Platform',0,.05,0,1.6,.10,2.3,'Steel',.018)
for x in [-.77,.77]:box('Sensor_Column',x,1.18,-.55,.11,2.3,.18,'Coat',.018)
box('Sensor_Crossbar',0,2.30,-.55,1.65,.15,.25,'Steel',.018)
box('Seat_Pedestal',0,.32,0,.48,.50,.6,'Steel',.025);box('Diagnostic_Seat',0,.64,.10,.70,.13,.78,'Fabric',.055);box('Backrest',0,1.10,-.30,.70,.88,.15,'Fabric',.055);box('Head_Support',0,1.67,-.29,.38,.30,.16,'Fabric',.055)
for x in [-.46,.46]:box('Arm_Support',x,.88,.05,.17,.12,.62,'Coat',.03)
for x in [-.50,.50]:cyl('Stereo_Sensor',(x,2.17,-.40),(x,2.17,-.34),.05,'Lens',32)
display(.77,1.45,-.415,.25,.32,11);save('DiagnosticChair','Props')

reset();feet(1.25,.67)
box('Archive_Back',0,1.17,-.31,1.25,2.10,.04,'Steel',.01)
for x in [-.62,.62]:box('Archive_Side',x,1.17,0,.04,2.10,.67,'Steel',.01)
for j in range(6):
 y=.24+j*.34;box('Archive_Shelf',0,y,0,1.25,.035,.67,'Steel',.006)
 for i in range(7):
  x=-.51+i*.17;box('Sealed_Record_Cartridge',x,y+.15,.02,.14,.27,.52,'Coat',.008);box('Flush_ID_Strip',x,y+.19,.285,.11,.055,.0015,'Paper',.0002);pull(x,y+.09,.29,.07)
box('Archive_Header',0,2.25,0,1.25,.12,.68,'Steel',.01);save('RecordRack','Props')

reset();bench_top(2.1);display(0,1.34,-.15,1.25,.58,12);monitor_stand(0,1.34,-.15,1.25,.58,.895);keyboard(0,.93,.22)
for i in range(4):box('Bound_Protocol_Book',-.80+i*.055,1.04,-.08,.045,.28,.24,'Dark' if i%2 else 'Coat',.004)
box('Document_Tray',.76,.93,.10,.34,.06,.46,'Steel',.008)
for i in range(4):box('Record_Sheet',.76,.965+i*.002,.10,.30,.001,.40,'Paper',.0002)
save('ResearchDesk','Props')

reset();box('VideoWall_Back',0,1.65,0,4.65,2.7,.25,'Steel',.025)
for i in range(4):display((-1 if i%2==0 else 1)*1.13,1.1+(i//2)*1.15,.15,2.10,1.04,13+i)
for x in [-1.75,1.75]:box('DisplayWall_Foot',x,.09,0,.65,.18,.90,'Steel',.025)
save('InterpretationWall','Props')
reset();box('ControlWall_Back',0,1.9,0,6.2,3.35,.32,'Steel',.025)
for i in range(6):display((i%3-1)*2.0,1.15+(i//3)*1.35,.18,1.88,1.18,13+i)
for x in [-2.4,0,2.4]:box('ControlWall_Foot',x,.09,0,.70,.18,1.0,'Steel',.02)
save('IntegratedControlWall','Props')

reset();w=4.7;d=4.5
box('Shield_Rear',0,1.55,-d/2,w,3.1,.28,'Steel',.025)
for x in [-w/2,w/2]:
 box('Shield_Side',x,1.55,0,.28,3.1,d,'Steel',.025)
 for z in [-1.8,-.9,0,.9,1.8]:box('Shield_Stiffener',x-(.18 if x>0 else -.18),1.55,z,.10,2.9,.12,'Dark',.01)
# Front left 2.1m doorway; observation window on the right.
box('Shield_Header',0,2.95,2.12,w,.30,.28,'Steel',.02)
box('Window_Sill',1.20,.55,2.12,2.15,1.10,.25,'Steel',.018);box('Observation_Glass',1.20,1.90,2.12,1.97,1.55,.045,'Glass',.008)
for x in [.15,2.25]:box('Window_Frame',x,1.99,2.12,.12,1.88,.28,'Steel',.012)
for y in [1.15,2.81]:box('Window_Rail',1.20,y,2.12,2.15,.10,.28,'Steel',.01)
box('Test_Anvil',0,.41,-.90,.90,.82,.90,'Steel',.035)
cyl('Load_Cell',(0,.83,-.9),(0,.91,-.9),.28,'Dark',40)
for i in range(4):
 a=i*math.pi/2;cyl('Test_Bolt',(.22*math.cos(a),.91,-.9+.22*math.sin(a)),(.22*math.cos(a),.95,-.9+.22*math.sin(a)),.022,'Steel',8)
display(0,1.9,-2.10,1.30,.65,19);save('ShieldTestCell','Props')

reset()
box('Divider_Base',0,.07,0,2.65,.14,.30,'Steel',.015);box('Divider_Lower',0,.60,0,2.65,1.1,.10,'Coat',.014)
for x in [-1.3,1.3]:box('Divider_Post',x,1.25,0,.07,2.50,.13,'Steel',.008)
box('Divider_UpperGlass',0,1.76,0,2.54,1.23,.022,'Glass',.004);box('Divider_Header',0,2.43,0,2.65,.08,.13,'Steel',.009)
save('GlazedDivider','Props')
reset();cabinet(1.25,1.85,.68);display(0,1.52,.387,.40,.22,20)
box('Transfer_Recess',0,.94,.385,.75,.47,.025,'Dark',.008);box('Transfer_Hatch',0,.94,.407,.67,.40,.04,'Steel',.015);pull(0,.94,.432,.26)
save('CustodyTransferHatch','Props')
print('PROPS DONE',flush=True)
