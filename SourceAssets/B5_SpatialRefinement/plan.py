"""Room-in-room spatial layout. Unity metres. Author 송예찬."""
from pathlib import Path
import json,math
H=Path(__file__).resolve().parent;R=H.parents[1];old=json.loads((R/'SourceAssets/B5_RemainingDomes/plan.json').read_text(encoding='utf-8'));rooms=old['rooms'];props=[];structures=[];lights=[]
def prop(room,model,x,z,yaw=0,y=0):
 p=dict(id=f'{room}_SF_{len(props):03}_{model}',room=room,model='SF_'+model,position=[x,y,z],yaw=yaw);props.append(p);return p
def struct(room,kind,x,z,w,d,yaw=0,**kw):structures.append(dict(room=room,kind=kind,x=x,z=z,w=w,d=d,yaw=yaw,**kw))
def local(room,model,cx,cz,yaw,x,z,rot=0):
 a=math.radians(yaw);return prop(room,model,cx+math.cos(a)*x+math.sin(a)*z,cz-math.sin(a)*x+math.cos(a)*z,yaw+rot)
def rim(room,model,angle,inset=1.25):
 r=rooms[room];a=math.radians(angle);dist=r['r']-inset
 # Move to the nearest clear wall segment; retain generous portal clearance.
 for delta in [0,10,-10,20,-20,30,-30,40,-40,60,-60]:
  test=a+math.radians(delta)
  if all(abs((math.degrees(test)-q['angle']+180)%360-180)>math.degrees(math.asin(min(.95,3.15/r['r']))) for q in r['doors']):a=test;break
 return prop(room,model,dist*math.cos(a),dist*math.sin(a),-90-math.degrees(a))
for room,cx,cz in [('W01',3.3,3.75),('W02',3.5,4.3)]:
 for x,z in [(-cx,-cz),(cx,-cz),(-cx,cz),(cx,cz)]:
  yaw=180 if z>0 else 0;struct(room,'living_suite',x,z,4.2,3.8,yaw)
  for model,xx,zz in [('LivingBed',-1.03,-.3),('LivingDesk',.72,-1.43),('PersonalLocker',1.25,-.60),('SanitaryBasin',1.05,.15),('CompactToilet',1.05,1.0)]:local(room,model,x,z,yaw,xx,zz)
 prop(room,'TransferNurseDesk' if room=='W01' else 'IsolationNurseStation',0,0,180)
 for model,angle in [('LinenRack',0),('LinenReturnCart',180),('WaitingBench',90),('MealTransportCart',270)]:rim(room,model,angle,1.3)
 struct(room,'nurse_canopy',0,0,3.1,2.0)
# Two proper examination suites and a separate waiting/triage zone.
for x in [-3.05,3.05]:
 struct('W03','exam_suite',x,2.4,4.25,3.9,180)
 for model,xx,zz,rot in [('MedicalBed',-.5,.05,0),('VitalCart',1.3,-.95,0),('ExaminationLight',-1.45,-.90,0),('PrivacyCurtain',1.7,.95,90),('MedicalGasStation',-.45,-1.48,0)]:local('W03',model,x,2.4,180,xx,zz,rot)
prop('W03','TransferNurseDesk',0,-3.2,180);prop('W03','UltrasoundCart',2.8,-2.4,180)
for model,a in [('MedicationCabinet',90),('MedicalSterilizer',110),('LinenRack',200),('WaitingBench',230),('WaitingBench',310)]:rim('W03',model,a,1.45)
struct('W03','triage_screen',0,-3.2,3.3,1.9,180)
# Central cooling machinery on four engineered beds, enclosed control booth behind.
for x in [-2.55,2.55]:
 for z in [-2.15,1.65]:
  prop('C03','TwinCoolingPump' if z<0 else 'PlateHeatExchanger',x,z,180 if x<0 else 0,y=.07)
  struct('C03','machine_plinth',x,z,2.25,1.65)
for x in [-5.35,5.35]:prop('C03','ExpansionVessel',x,2.8,180)
for x in [-4.9,4.9]:prop('C03','ValveManifold',x,-2.4,90 if x<0 else 270)
struct('C03','control_booth',0,5.6,4.8,2.7,180);prop('C03','ProcessControlBay',0,6.0,180)
for m,a in [('AirHandlingUnit',150),('FilterBank',210),('MaintenanceBench',275),('ElectricalSwitchgear',325)]:rim('C03',m,a,1.5)
struct('C03','process_headers',0,0,6.2,5.9)
# Utility: fenced power train and a clear service aisle to air plant.
for m,x,z,y in [('ElectricalSwitchgear',-2.9,1.7,90),('ElectricalSwitchgear',-2.9,-.3,90),('AirHandlingUnit',2.5,1.8,270),('ProcessControlBay',2.8,-1.1,270),('MaintenanceBench',0,-3.6,0)]:prop('C04',m,x,z,y)
struct('C04','power_screen',-1.65,.7,.12,4.8);struct('C04','service_canopy',.4,.7,6.3,4.5)
# Goods receiving has parallel rack aisles and an inspection counter.
for x in [-2.5,2.5]:
 for z in [-.7,1.2,3.1]:prop('E01','SupplyRack',x,z,90 if x<0 else 270)
prop('E01','ReceivingIsland',0,-3.55,180)
for m,a in [('ColdStorage',90),('SealedSupplyCrates',145),('LinenRack',190),('LinenReturnCart',235),('MealTransportCart',320),('ArchiveCaseRack',30)]:rim('E01',m,a,1.2)
struct('E01','receiving_canopy',0,-3.55,4.1,2.7);struct('E01','storage_gantry',0,1.2,6.4,6.3)
# Food prep is an island, separate dirty return bay and glazed cold/clean back area.
prop('E02','MealAssemblyIsland',0,.2,0);prop('E02','MealPreparation',-3.4,2.7,90);prop('E02','DoubleWashSink',3.4,-.7,270);prop('E02','TrayDishwasher',3.4,1.3,270)
for x in [-1.3,1.3]:prop('E02','ColdStorage',x,5.2,180)
prop('E02','MealTransportCart',-3.5,-2.6,90);prop('E02','MealTransportCart',-.6,-3.4,0)
for m,a in [('SupplyRack',155),('SupplyRack',200),('LinenReturnCart',320),('SealedSupplyCrates',35)]:rim('E02',m,a,1.5)
struct('E02','kitchen_extract',0,.2,3.9,3.4);struct('E02','wash_partition',2.15,.1,.12,5.4);struct('E02','cold_partition',0,4.25,5.7,.12)
# Decontamination: opposing wet bays and clean/dirty partitions with central openings.
for z in [-2.3,2.3]:
 struct('E03','decon_partition',0,z,9.1,.12)
for x in [-3.35,3.35]:
 prop('E03','DeconShower',x,0,90 if x<0 else 270)
 struct('E03','wet_canopy',x,0,2.5,2.8)
prop('E03','DeconChangeBench',0,4.0,0);prop('E03','DeconChangeBench',0,-4.0,0)
for m,a in [('PPEDispenser',75),('PersonalLocker',105),('BootDryingRack',145),('LinenReturnCart',255),('SanitaryBasin',285)]:rim('E03',m,a,1.3)
# Central control: six seated operators inside a glazed control suite, servers outside.
struct('N01','command_suite',0,2.2,9.6,9.0)
prop('N01','CentralVideoWall',0,6.0,180)
for z in [3.85,.55]:
 for x in [-2.6,0,2.6]:prop('N01','CentralOperatorDesk',x,z,180);prop('N01','TaskChair',x,z-1.05,0)
for x in [-6.5,6.5]:
 for z in [-.1,1.5,3.1]:prop('N01','DataRecorderRack',x,z,90 if x<0 else 270)
prop('N01','BriefingTable',0,-4.4,0)
for x,z,y in [(-1.5,-4.4,90),(1.5,-4.4,270),(0,-5.55,0)]:prop('N01','TaskChair',x,z,y)
for m,a in [('ArchiveCaseRack',145),('MaintenanceBench',210),('ArchiveCaseRack',330)]:rim('N01',m,a,1.4)
# Closed-test central enclosure has a clear entrance and side observation booth.
struct('S01','test_cell',0,1.0,5.5,5.2)
prop('S01','TestGantry',0,1.1,0);prop('S01','MedicalBed',3.9,-3.2,0)
struct('S01','observation_booth',-5.2,.5,2.7,4.2,180);prop('S01','TestControlConsole',-5.2,1.0,180)
for m,a in [('ElectricalSwitchgear',55),('DataRecorderRack',100),('ArchiveCaseRack',135),('MedicalSterilizer',230),('SupplyRack',280),('VitalCart',315)]:rim('S01',m,a,1.4)
# Existing security equipment remains useful, but moves into operational subrooms.
struct('C02','security_suite',0,3.5,6.25,4.0)
struct('C02','review_booth',-2.1,-2.7,3.4,2.6,15)
struct('C02','server_baffle',3.65,3.4,.1,3.7)
for room in ['VA','VB','VL']:struct(room,'core_detail',0,0,10,10)
out=dict(author='송예찬',scope='C01 protected; 11 other domes + 3 cores',rooms=rooms,tunnels=old['tunnels'],placements=props,structures=structures,lightPolicy='local fixtures only, existing lights preserved')
(H/'plan.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(len(props),'props',len(structures),'structures',len(set(p['model'] for p in props)),'model types')
