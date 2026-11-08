"""B4 observation instruments and fittings. Author: 송예찬."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *

def desk(kind):
 reset()
 box('Rounded_Instrument_Top',0,.81,0,2.15,.07,.92,'Coat',.025)
 box('Operator_Edge',0,.782,.46,2.06,.035,.028,'Rubber',.01)
 for x in [-.9,.9]:
  box('Desk_Foot',x,.055,0,.25,.09,.80,'Steel',.022)
  box('Box_Section_Leg',x,.43,-.12,.11,.69,.13,'Steel',.012)
 box('Rear_Cable_Raceway',0,.64,-.36,1.86,.16,.16,'Steel',.012)
 for x,k in [(-.48,kind),(.48,2 if kind==1 else 4)]:
  display(x,1.25,-.19,.79,.46,k);monitor_stand(x,1.25,-.19,.79,.46,.845)
 keyboard(-.22,.865,.21)
 box('Mouse_Pad',.48,.851,.22,.25,.005,.23,'Rubber',.008)
 box('Mouse',.47,.872,.22,.062,.036,.107,'Dark',.022)
 # Discrete physical acquisition controls, with guarded emergency stop.
 box('Acquisition_Control_Base',-.79,.885,.22,.25,.08,.26,'Dark',.014)
 for i in range(3):cyl('Encoder',(-.86+i*.07,.926,.20),(-.86+i*.07,.946,.20),.021,'Steel',24)
 cyl('Safety_Collar',(-.79,.927,.28),(-.79,.95,.28),.031,'Hazard',24)
 cyl('Stop_Button',(-.79,.95,.28),(-.79,.975,.28),.022,'Red',24)
 box('Acquisition_PC',.65,.42,-.13,.28,.52,.48,'Dark',.014);vent(.65,.46,.118,.22,.27)
 for y in [.27,.63]:box('PC_Trim',.65,y,.12,.23,.014,.018,'Steel',.003)
 tube('Floor_Cable_Drop',[(.7,.64,-.38),(.7,.2,-.38),(.7,.025,-.49),(.85,.025,-.6)],.017,'Dark')
 save('ObservationConsole' if kind==1 else 'TrialControlConsole','Props')

desk(1);desk(3)

reset();cabinet(1.85,.85,.72,'drawers')
box('Preparation_Top',0,.895,0,1.93,.065,.79,'Steel',.014)
box('Raised_Backlip',0,1.00,-.39,1.91,.22,.025,'Coat',.005)
box('AntiStatic_Mat',-.34,.931,.05,.95,.006,.53,'Rubber',.008)
# Fitted sensor case, recessed foam pockets and six identifiable optical tags.
box('Open_Sensor_Case',-.30,.98,.03,.75,.09,.38,'Dark',.015)
box('Foam_Insert',-.30,1.025,.03,.70,.014,.33,'Rubber',.007)
for i in range(6):
 x=-.59+(i%3)*.28;z=-.065+(i//3)*.16
 cyl('Sensor_Recess',(x,1.03,z),(x,1.035,z),.048,'Steel',24)
 cyl('Optical_Tag',(x,1.036,z),(x,1.060,z),.034,'Paper',24)
 cyl('IR_Reflector',(x,1.061,z),(x,1.068,z),.020,'Lens',24)
box('Case_Lid',-.30,1.21,-.19,.75,.37,.035,'Dark',.014)
box('Lid_Foam',-.30,1.21,-.166,.68,.31,.011,'Rubber',.005)
for x in [-.60,0]:cyl('Case_Hinge',(x-.025,1.03,-.19),(x+.025,1.03,-.19),.013,'Steel',12)
display(.61,1.17,-.07,.32,.20,5)
box('Sensor_Docking_Base',.61,.96,-.09,.40,.09,.28,'Coat',.012)
for x in [.52,.61,.70]:cyl('Dock_Socket',(x,1.007,.01),(x,1.012,.01),.018,'Dark',16)
save('SensorPreparationBench','Props')

reset()
# Enclosed data acquisition rack: backing, perforated doors, actual modular trays.
feet(.70,.78)
box('Rack_Back',0,1.15,-.37,.70,2.05,.035,'Dark',.012)
for x in [-.34,.34]:box('Rack_Side',x,1.15,0,.04,2.05,.78,'Steel',.012)
for y in [.18,2.17]:box('Rack_Frame',0,y,0,.71,.06,.80,'Steel',.01)
for j in range(9):
 y=.32+j*.18;box('Rack_Unit',0,y,0,.60,.15,.70,'Dark',.007)
 box('Anodized_Faceplate',0,y,.365,.62,.145,.025,'Steel',.004)
 for x in [-.27,.27]:
  for yy in [y-.05,y+.05]:bolt(x,yy,.38)
 for k in range(6):box('Cooling_Slot',-.19+k*.04,y,.38,.024,.065,.004,'Dark',0)
 for k in range(3):box('Channel_LED',.15+k*.035,y+.03,.382,.012,.008,.006,'Indicator',.001)
 box('Service_Port',.18,y-.025,.383,.10,.035,.008,'Dark',.002)
display(0,2.015,.385,.47,.12,5)
for z in [-.25,.1]:tube('Rack_Handle',[(-.36,1.1,z),(-.40,1.1,z),(-.40,1.35,z),(-.36,1.35,z)],.012,'Steel')
save('AcquisitionRack','Props')

reset();cabinet(1.30,1.9,.58)
for side in [-1,1]:print_panel('Inventory_Label',side*.32,1.3,.323,.21,.09)
save('SensorStorage','Props')

reset();trolley(.82,.58)
box('Sync_Instrument',0,.87,0,.66,.26,.43,'Coat',.018)
display(-.11,.88,.23,.33,.17,5)
for y in [.83,.94]:
 for x in [.16,.24]:cyl('BNC_Socket',(x,y,.219),(x,y,.246),.019,'Steel',16);cyl('BNC_Core',(x,y,.247),(x,y,.250),.009,'Dark',12)
box('Instrument_Rack_Ears',0,.87,.205,.78,.29,.025,'Steel',.005)
# The ears are behind the front controls; all ports stay clear of the monitor.
box('Lower_PowerUnit',0,.38,0,.56,.27,.39,'Dark',.012);vent(0,.39,.203,.42,.15)
tube('Instrument_Coil',[(.26,.84,.25),(.36,.75,.30),(.37,.45,.32),(.27,.35,.25),(.23,.39,.22)],.008,'Dark')
save('SynchronizationCart','Props')

reset()
box('Ceiling_Anchor',0,.025,0,.22,.05,.22,'Steel',.012)
box('Drop_Arm',0,-.18,0,.055,.36,.055,'Steel',.006)
cyl('Tilt_Axis',(-.11,-.36,0),(.11,-.36,0),.052,'Steel',24)
box('Optical_Tracking_Head',0,-.40,.075,.29,.15,.24,'Coat',.025)
for x in [-.085,.085]:
 cyl('Camera_Barrel',(x,-.40,.195),(x,-.40,.252),.039,'Dark',32)
 cyl('Lens_Rim',(x,-.40,.246),(x,-.40,.263),.035,'Steel',32)
 cyl('Optical_Lens',(x,-.40,.264),(x,-.40,.268),.028,'Lens',32)
box('Tracking_Status',0,-.40,.198,.018,.012,.008,'Indicator',.002)
tube('Camera_Data_Lead',[(0,-.42,-.05),(.08,-.32,-.12),(.06,-.13,-.08),(0,.01,-.08)],.007,'Dark')
save('OpticalTrackingCamera','Props')

reset()
box('Calibration_Base',0,.035,0,.55,.07,.50,'Steel',.025)
cyl('Height_Adjust_Column',(0,.07,0),(0,1.35,0),.028,'Steel',20)
cyl('Column_Clamp',(0,.73,0),(0,.84,0),.039,'Dark',20)
box('Target_Back',0,1.4,0,.62,.62,.035,'Coat',.012)
for i in range(7):
 for j in range(7):box('Calibration_Check',-.24+i*.08,1.16+j*.08,.021,.08,.08,.005,'Paper' if (i+j)%2==0 else 'Dark',0)
save('CalibrationTarget','Props')

reset()
# Sealed industrial observation-layer lighting, downward local Y.
box('Fixture_Back',0,.027,0,1.20,.054,.30,'Steel',.018)
box('Gasket',0,-.008,0,1.15,.017,.26,'Rubber',.008)
box('Prismatic_Diffuser',0,-.025,0,1.10,.025,.22,'Lamp',.008)
for x in [-.57,.57]:
 box('EndCap',x,-.013,0,.055,.04,.30,'Coat',.009)
 for z in [-.10,.10]:cyl('Lens_Fastener',(x,-.039,z),(x,-.044,z),.009,'Steel',8)
box('Cable_Gland',.62,.025,0,.055,.045,.06,'Dark',.009)
save('SealedTaskLight')

reset()
# One portal kit per 4.2 m vault; the closed infill is a separate model.
arc('Continuous_Portal_Frame',2.115,.095,.24,0,math.pi,1.3)
for x in [-2.067,2.067]:
 box('Portal_Jamb',x,.65,0,.095,1.30,.24,'Steel',.008)
 box('Jamb_Foot',x,.055,0,.20,.11,.33,'Steel',.009)
 for y in [.28,1.05]:box('Frame_Service_Plate',x,y,.127,.075,.14,.018,'Dark',.003)
box('Threshold',0,.018,0,4.16,.036,.34,'Steel',.006)
save('VaultPortal')
reset()
vs=[(-2.015,0,-.10),(2.015,0,-.10),(2.015,1.3,-.10)]
vs += [(2.015*math.cos(math.pi*i/48),1.3+2.015*math.sin(math.pi*i/48),-.10) for i in range(1,49)]
front=list(vs);vs += [(x,y,z+.12) for x,y,z in front];n=len(front)
fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
mesh('Closed_Vault_Door',vs,fs,'Coat',.01)
box('Meeting_Seal',0,1.65,.027,.020,3.28,.012,'Dark',.002)
for x in [-.95,.95]:
 box('Door_Recess',x,1.15,.028,1.65,1.85,.01,'Dark',.006)
 box('Door_Armor',x,1.15,.04,1.59,1.79,.025,'Steel',.01)
 pull(x,1.15,.057,.23)
box('Interlock_Status',1.65,1.6,.06,.05,.09,.012,'Indicator',.003)
save('ClosedVaultDoor')
reset()
box('Wall_Anchor_Plate',0,0,0,.22,.19,.028,'Steel',.009)
for x in [-.078,.078]:
 for y in [-.060,.060]:bolt(x,y,.017)
cyl('Camera_Support_Stem',(0,0,.02),(0,0,.35),.024,'Steel',20)
box('Camera_Anchor_Saddle',0,-.015,.35,.20,.035,.17,'Steel',.008)
save('TrackingCameraSupport','Props')
print('PROPS COMPLETE',flush=True)
