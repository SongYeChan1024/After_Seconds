from pathlib import Path
import json,math
H=Path(__file__).resolve().parent;plan=json.loads((H/'plan.json').read_text(encoding='utf-8'));cat={x['name']:x for x in json.loads((H/'catalog.json').read_text())}

def fitted(name,source,target,rot=None,prefab=None):
 c=dict(cat[source]);w,h,d=c['size'];cx,cy,cz=c['center']
 if rot: w,h,d=w,d,h
 scale=min(target[0]/w,target[1]/h,target[2]/d)
 c.update(name=name,size=[w*scale,h*scale,d*scale],center=[0,h*scale/2,0],fit=target,rotation=rot or [0,0,0],asset=prefab or c['asset']);cat[name]=c
fitted('BM_ElectricalCabinet','Props_ElectricalCabinet',[1.55,2.25,.95])
fitted('BM_Centrifuge','Props_IndustrialCentrifuge',[3.5,3.4,3.6])
fitted('BM_ControlConsole','B2_ControlDeskIsland',[2.1,1.45,1.6])
fitted('BM_CoolingPump','Props_CoolingPump',[1.65,1.3,1.10],[-90,0,0],'Assets/Afrer_Seconds/05.Model/Props/B5/Props_CoolingPump_B5_Lite.prefab')
fitted('BM_HVACUnit','Props_HVACUnit',[2.7,2.2,1.45],None,'Assets/Afrer_Seconds/05.Model/Props/B2/Props_HVACUnit_B5_Lite.prefab')

program={'C01': ['BC_PumpDriveCabinet', 'BC_PumpDriveCabinet', 'BC_PumpDriveCabinet', 'BC_PlateHeatExchanger', 'BC_PlateHeatExchanger', 'BC_MaintenanceBench', 'BC_ToolTrolley', 'BM_MechanicalSparesRack', 'BC_MaintenanceBench', 'BC_ToolTrolley', 'BM_MechanicalSparesRack', 'BM_WaterFilterSkid', 'BM_SealedProcessTank', 'BM_ControlConsole', 'BM_ElectricalCabinet'], 'C03': ['BM_ElectricalCabinet', 'BM_ElectricalCabinet', 'BM_ElectricalCabinet', 'BC_PumpDriveCabinet', 'BC_PumpDriveCabinet', 'BS_ArchiveUPS', 'BM_MechanicalSparesRack'], 'C04': ['BM_ControlConsole', 'BM_ControlConsole', 'BM_ControlConsole', 'BS_ServerRack_1', 'BS_ServerRack_2', 'BS_ArchiveUPS', 'BC_ToolTrolley', 'BM_ElectricalCabinet'], 'W01': ['BM_PowerTransformer', 'BM_PowerTransformer', 'BM_PowerTransformer', 'BM_ElectricalCabinet', 'BM_ElectricalCabinet', 'BM_ElectricalCabinet', 'BM_ElectricalCabinet', 'BS_ArchiveUPS', 'BS_ArchiveUPS', 'BC_PumpDriveCabinet', 'BC_UpperValveStation', 'BC_ToolTrolley', 'BM_MechanicalSparesRack'], 'W02': ['B2_EmergencyGenerator', 'B2_EmergencyGenerator', 'B2_EmergencyGenerator', 'BM_SealedProcessTank', 'BM_SealedProcessTank', 'BC_PumpDriveCabinet', 'BC_PumpDriveCabinet', 'BM_ElectricalCabinet', 'BC_MaintenanceBench', 'BC_ToolTrolley', 'BM_MechanicalSparesRack', 'BS_ArchiveUPS'], 'W03': ['BM_MechanicalSparesRack', 'BM_MechanicalSparesRack', 'BM_MechanicalSparesRack', 'BM_MechanicalSparesRack', 'BM_MechanicalSparesRack', 'BM_MechanicalSparesRack', 'BM_MechanicalSparesRack', 'BC_MaintenanceBench', 'BC_MaintenanceBench', 'BC_ToolTrolley', 'BC_ToolTrolley', 'BC_ToolTrolley', 'BX_EquipmentCaseRack', 'SD_CylinderTrolley', 'BM_ElectricalCabinet', 'BC_UpperValveStation'], 'E01': ['BM_WaterFilterSkid', 'BM_WaterFilterSkid', 'BM_WaterFilterSkid', 'BM_SealedProcessTank', 'BM_SealedProcessTank', 'BM_CoolingPump', 'BM_CoolingPump', 'BM_CoolingPump', 'BC_PumpDriveCabinet', 'BC_PumpDriveCabinet', 'BC_UpperValveStation', 'BC_MaintenanceBench', 'BC_ToolTrolley', 'BM_MechanicalSparesRack'], 'E02': ['BM_AirFilterSkid', 'BM_AirFilterSkid', 'BM_AirFilterSkid', 'BM_AirFilterSkid', 'BM_HVACUnit', 'BM_HVACUnit', 'BM_VentilationFan', 'BM_VentilationFan', 'BM_MechanicalSparesRack', 'BM_MechanicalSparesRack', 'BC_PumpDriveCabinet', 'BC_MaintenanceBench', 'BC_ToolTrolley'], 'E03': ['BM_SealedProcessTank', 'BM_SealedProcessTank', 'BM_SealedProcessTank', 'BM_CoolingPump', 'BM_CoolingPump', 'BC_PumpDriveCabinet', 'BC_UpperValveStation', 'BM_WaterFilterSkid', 'SF_DoubleWashSink', 'OD_ClosedPPEReturn', 'OD_CleanPPEDispenser', 'BC_ToolTrolley'], 'N01': ['BM_HVACUnit', 'BM_HVACUnit', 'BM_HVACUnit', 'BM_VentilationFan', 'BM_VentilationFan', 'BM_VentilationFan', 'BM_VentilationFan', 'BM_AirFilterSkid', 'BM_AirFilterSkid', 'BM_AirFilterSkid', 'BC_PumpDriveCabinet', 'BC_PumpDriveCabinet', 'BC_PumpDriveCabinet', 'BC_MaintenanceBench', 'BC_ToolTrolley', 'BM_MechanicalSparesRack'], 'S01': ['BM_ControlConsole', 'BM_ControlConsole', 'BM_ControlConsole', 'BM_ElectricalCabinet', 'BM_ElectricalCabinet', 'BC_MaintenanceBench', 'BC_MaintenanceBench', 'BC_MaintenanceBench', 'BM_MechanicalSparesRack', 'BM_MechanicalSparesRack', 'BM_MechanicalSparesRack', 'BC_ToolTrolley', 'BC_ToolTrolley', 'BS_ServerRack_1', 'BS_ServerRack_2', 'BS_ArchiveUPS', 'SD_CylinderTrolley']}

def turn(x,z,yaw):
 a=math.radians(yaw);return x*math.cos(a)+z*math.sin(a),-x*math.sin(a)+z*math.cos(a)
def corners(w,d,cx=0,cz=0,yaw=0):return [(cx+turn(x,z,yaw)[0],cz+turn(x,z,yaw)[1]) for x,z in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]]
def sat(a,b,margin=.25):
 for poly in [a,b]:
  for i in range(4):
   x,z=poly[(i+1)%4][0]-poly[i][0],poly[(i+1)%4][1]-poly[i][1];l=math.hypot(x,z);nx,nz=-z/l,x/l;aa=[x*nx+z*nz for x,z in a];bb=[x*nx+z*nz for x,z in b]
   if max(aa)+margin<min(bb) or max(bb)+margin<min(aa):return False
 return True
placements=[];zones=[];fail=[]
for r in plan['rooms']:
 code=r['id']
 if code not in program:continue
 paths=[];blocks=[corners(4.6,4.6)] if code=='C01' else []
 for d in r['doors']:
  paths.append(corners(1.85,math.hypot(d['x'],d['z'])+1,d['x']/2,d['z']/2,math.degrees(math.atan2(d['x'],d['z']))))
 for i,n in enumerate(program[code]):
  c=cat[n];w,h,d=c['size'];cx,cy,cz=c['center'];limit=math.sqrt(r['r']**2-min(h,3.5)**2)-.24;found=None
  # Match wall bays first; keep a front working apron clear of later placements.
  for step in range(24):
   radius=r['r']-d/2-.63-step*.20
   if radius<1.4:continue
   choices=[]
   for ai in range(180):
    a=(ai*2+i*7)%360;theta=math.radians(a);x,z=radius*math.cos(theta),radius*math.sin(theta);yaw=270-a;poly=corners(w,d,x,z,yaw)
    ax,az=turn(0,(d+.90)/2,yaw);apron=corners(w,.90,x+ax,z+az,yaw)
    if max(math.hypot(px,pz) for px,pz in poly)>limit:continue
    if sat(poly,corners(2.0,2.0),.1) or any(sat(poly,p,.20) for p in paths) or any(sat(poly,p,.45) for p in blocks):continue
    if any(sat(apron,p,.1) for p in blocks):continue
    score=min(abs((a-q['angle']+180)%360-180) for q in r['doors'])*.05+radius+math.sin(theta*2+i)*.08
    choices.append((score,x,z,yaw,poly,apron))
   if choices:found=max(choices);break
  if found is None:fail.append([code,n]);continue
  _,x,z,yaw,poly,apron=found;blocks.extend([poly,apron]);ox,oz=turn(cx,cz,yaw)
  name=f'B2_{code}_{n.split("_",1)[1]}_{i+1:02}'
  placements.append(dict(room=code,name=name,model=n,asset=c['asset'],position=[x-ox,0,z-oz],yaw=yaw,size=c['size'],center=c['center'],meshCollider=n in ['OD_PipedDeconShower'],role='Storage' if 'Rack' in n else 'Equipment',fit=c.get('fit'),rotation=c.get('rotation')))
  zones.append(dict(room=code,name=name,center=[x,z],size=[w,d],yaw=yaw,polygon=poly))
c=cat['BM_Centrifuge'];placements.append(dict(room='C01',name='B2_C01_IndustrialCentrifuge_01',model=c['name'],asset=c['asset'],position=[0,0,0],yaw=0,size=c['size'],center=c['center'],meshCollider=False,role='CentralProcess',fit=c['fit'],rotation=c['rotation']))
plan['placements']=placements;plan['zones']=zones;plan['unplaced']=fail
(H/'layout.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'placements':len(placements),'perRoom':{r['id']:sum(p['room']==r['id'] for p in placements) for r in plan['rooms']},'unplaced':fail},indent=2))
if fail:raise RuntimeError('Unplaced equipment: revise layout before build')
