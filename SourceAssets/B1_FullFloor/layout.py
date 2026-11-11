from pathlib import Path
import sys,json,math
H=Path(__file__).resolve().parent;R=H.parents[1];sys.path.insert(0,str(R/'Unity/After_Seconds_Build_V0.01/Temp/ZFightingReview/deps'))
from shapely.geometry import Polygon,LineString,Point
from shapely.affinity import rotate,translate
plan=json.loads((H/'plan.json').read_text(encoding='utf8'));cat={c['name']:c for c in json.loads((H/'catalog.json').read_text())};cat.update(json.loads((H/'models_props.json').read_text()))
program={
'C01':['BO_TrialControlConsole']*2+['BO_AcquisitionRack','BO_SynchronizationCart','SF_MedicalGasStation','BO_SensorStorage']*1+['SF_WaitingBench']*2+['SF_TestControlConsole'],
'C02':['LB_SensorPrepBench','SD_CentrifugeBench','SF_DoubleWashSink','BS_ColdCabinet','SF_PPEDispenser','CP_ReagentShelf','SF_MedicalSterilizer','LP_SampleTrolley'],
'C03':['SF_ArchiveCaseRack']*5+['BL_ResearchDesk']*2+['BS_ArchiveUPS','SF_SC_IncidentReview','SF_TaskChair']*1,
'C04':['SF_MedicalBed']*2+['SF_VitalCart','SF_UltrasoundCart','SF_PrivacyCurtain','SF_MedicationCabinet','SF_MedicalGasStation','SF_DoubleWashSink','SF_PPEDispenser','SF_ExaminationLight'],
'C05':['BO_ObservationConsole']*2+['BO_AcquisitionRack','LB_SignalAnalysisBench','BO_SensorStorage','SF_TaskChair']*1,
'W01':['BL_ResearchDesk']*6+['SF_TaskChair']*6+['SF_SC_RecordArchive']*2+['SF_WaitingBench'],
'W02':['BL_ServingCounter','SF_MealPreparation','SF_ColdStorage','SF_TrayDishwasher','SF_DoubleWashSink','SF_SupplyRack','BL_LoungeSofa','SF_LinenReturnCart'],
'W03':['SF_PersonalLocker']*8+['BL_SanitaryCubicle']*2+['BL_ShowerCubicle']*2+['BL_LaundryMachine']*2+['SF_LinenRack','SF_BootDryingRack','SF_LinenReturnCart','SF_SanitaryBasin']*1,
'E01':['SF_SC_VideoWall','SF_SC_OperatorDesk_A','SF_SC_OperatorDesk_B','SF_SC_RadioDutyStation','SF_SC_NetworkRack','SF_SC_UPSRack','SF_SC_RecordArchive']+['SF_TaskChair']*3,
'E02':['SF_ArchiveCaseRack']*4+['BL_ResearchDesk','SF_SC_NetworkRack','SF_TaskChair','SF_SR_EvidenceCabinet','BL_LoungeSofa'],
'E03':['SF_PersonalLocker']*4+['BL_SanitaryCubicle','BL_ShowerCubicle','BL_LaundryMachine','SF_SanitaryBasin','SF_SC_GearLockers','SF_SR_ShiftEquipment','SF_SC_RadioDutyStation','BL_LoungeSofa','SF_BootDryingRack'],
'N01':['BO_TrialControlConsole']*2+['LB_ElectrodePrepBench','BO_AcquisitionRack','BO_SynchronizationCart','BO_SensorStorage','LB_SignalAnalysisBench','SF_WaitingBench'],
'S01':['BS_ServerRack_1','BS_ServerRack_2']*4+['BS_ArchiveUPS']*2+['BL_ResearchDesk','SF_SC_IncidentReview','SF_TaskChair','BS_FilterBank','SF_ArchiveCaseRack']}
placements=[];work=[];blocks={r['id']:[] for r in plan['rooms']};serial={r['id']:0 for r in plan['rooms']}
def turn(x,z,a):t=math.radians(a);return x*math.cos(t)+z*math.sin(t),-x*math.sin(t)+z*math.cos(t)
def rect(w,d,x,z,yaw):return translate(rotate(Polygon([(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]),-yaw,origin=(0,0)),xoff=x,yoff=z)
def add(room,n,x,z,yaw=0,role='Equipment',y=0,apron=.8):
 c=cat[n];w,h,d=c['size'];cx,cy,cz=c['center'];ox,oz=turn(cx,cz,yaw);serial[room]+=1;name=f'B1_{room}_{n.split("_",1)[1]}_{serial[room]:02}'
 # All source meshes are floor-based; preserve original pivot and rotate their measured bounds.
 p=dict(room=room,name=name,model=n,asset=c['asset'],position=[x-ox,y-(cy-h/2),z-oz],yaw=yaw,size=c['size'],center=c['center'],role=role,meshCollider=n in ['BL_SanitaryCubicle','BL_ShowerCubicle'])
 placements.append(p)
 if role!='Accessory':
  poly=rect(w,d,x,z,yaw);blocks[room].append(poly.buffer(.12));dx,dz=turn(0,d/2+apron/2,yaw);blocks[room].append(rect(w,apron,x+dx,z+dz,yaw));dx,dz=turn(0,d/2+.6,yaw);work.append(dict(room=room,name=name,point=[x+dx,0,z+dz]))
 return p
add('C01','BL_TrialTargetRail',0,-4.5);add('C01','BL_PredictiveSensorFrame',0,1.8);add('N01','BL_TrialTargetRail',-3,-2,20);add('N01','BL_PredictiveSensorFrame',3,-2,-20)
add('W01','SF_BriefingTable',0,0,0)
for x in [-4,0,4]:add('W02','BL_DiningSet',x,1.0,0,apron=.3)
for room,xs in [('W03',[-4.5,-1.8,1.8,4.5]),('E03',[-4,-1.3])]:
 for x in xs:
  for z in [-3.0,3.0]:add(room,'BL_StaffBunk',x,z,0,apron=.25)
failed=[]
for r in plan['rooms']:
 code=r['id'];rad=r['r']
 if code not in program:continue
 # Door approaches and a circulation hub remain clear. Paths are design constraints,
 # actual capsule routes are verified after Unity colliders are in place.
 paths=[LineString([(0,0),(d['x'],d['z'])]).buffer(.97,cap_style=2) for d in r['doors']]
 for i,n in enumerate(program[code]):
  if n not in cat:failed.append([code,n,'missing']);continue
  c=cat[n];w,h,d=c['size'];limit=math.sqrt(rad*rad-min(h,4)**2)-.35;found=None
  for step in range(36):
   radius=limit-d/2-.25-step*.18
   if radius<.3:break
   options=[]
   for ai in range(180):
    angle=ai*2;th=math.radians(angle);x,z=radius*math.cos(th),radius*math.sin(th);yaw=270-angle;poly=rect(w,d,x,z,yaw);dx,dz=turn(0,d/2+.45,yaw);ap=rect(w,.9,x+dx,z+dz,yaw)
    if not Point(0,0).buffer(limit,resolution=96).covers(poly):continue
    if any(poly.intersects(p) for p in paths):continue
    if any(poly.buffer(.18).intersects(p) or ap.intersects(p) for p in blocks[code]):continue
    options.append((radius+math.cos(th*3+i)*.05,x,z,yaw))
   if options:found=max(options);break
  if found is None:failed.append([code,n,'space']);continue
  _,x,z,yaw=found;add(code,n,x,z,yaw)
# Small purpose-specific items are supported by existing flat work surfaces.
for p in list(placements):
 if p['model']=='BL_ResearchDesk':
  dx,dz=turn(.56,.09,p['yaw']);add(p['room'],'BL_HandheldRecorder',p['position'][0]+dx,p['position'][2]+dz,p['yaw'],role='Accessory',y=.855)
 if p['model'] in ['LB_SensorPrepBench','LB_ElectrodePrepBench']:
  # Place tray on a clear end of a worktop; height is reviewed in the close-up pass.
  dx,dz=turn(.60,.25,p['yaw']);add(p['room'],'BL_ExperimentCartridges',p['position'][0]+dx,p['position'][2]+dz,p['yaw'],role='Accessory',y=.93)
plan['placements']=placements;plan['workspaces']=work;plan['unplaced']=failed
(H/'layout.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(count=len(placements),perRoom={r['id']:sum(p['room']==r['id'] for p in placements) for r in plan['rooms']},unplaced=failed)))
if failed:raise RuntimeError('Placement failures require adjustment')
