from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[1]
source=(R/'SourceAssets/B3_FullFloor/layout.py').read_text(encoding='utf8')
start=source.index('def racks');end=source.index('def turn')
program={
'C01':['BC_PumpDriveCabinet']*3+['BC_PlateHeatExchanger']*2+['BC_MaintenanceBench','BC_ToolTrolley','BM_MechanicalSparesRack']*2+['BM_WaterFilterSkid','BM_SealedProcessTank','BM_ControlConsole','BM_ElectricalCabinet'],
'C03':['BM_ElectricalCabinet']*3+['BC_PumpDriveCabinet']*2+['BS_ArchiveUPS','BM_MechanicalSparesRack'],
'C04':['BM_ControlConsole']*3+['BS_ServerRack_1','BS_ServerRack_2','BS_ArchiveUPS','BC_ToolTrolley','BM_ElectricalCabinet'],
'W01':['BM_PowerTransformer']*3+['BM_ElectricalCabinet']*4+['BS_ArchiveUPS']*2+['BC_PumpDriveCabinet','BC_UpperValveStation','BC_ToolTrolley','BM_MechanicalSparesRack'],
'W02':['B2_EmergencyGenerator']*3+['BM_SealedProcessTank']*2+['BC_PumpDriveCabinet']*2+['BM_ElectricalCabinet','BC_MaintenanceBench','BC_ToolTrolley','BM_MechanicalSparesRack','BS_ArchiveUPS'],
'W03':['BM_MechanicalSparesRack']*7+['BC_MaintenanceBench']*2+['BC_ToolTrolley']*3+['BX_EquipmentCaseRack','SD_CylinderTrolley','BM_ElectricalCabinet','BC_UpperValveStation'],
'E01':['BM_WaterFilterSkid']*3+['BM_SealedProcessTank']*2+['BM_CoolingPump']*3+['BC_PumpDriveCabinet']*2+['BC_UpperValveStation','BC_MaintenanceBench','BC_ToolTrolley','BM_MechanicalSparesRack'],
'E02':['BM_AirFilterSkid']*4+['BM_HVACUnit']*2+['BM_VentilationFan']*2+['BM_MechanicalSparesRack']*2+['BC_PumpDriveCabinet','BC_MaintenanceBench','BC_ToolTrolley'],
'E03':['BM_SealedProcessTank']*3+['BM_CoolingPump']*2+['BC_PumpDriveCabinet','BC_UpperValveStation','BM_WaterFilterSkid','SF_DoubleWashSink','OD_ClosedPPEReturn','OD_CleanPPEDispenser','BC_ToolTrolley'],
'N01':['BM_HVACUnit']*3+['BM_VentilationFan']*4+['BM_AirFilterSkid']*3+['BC_PumpDriveCabinet']*3+['BC_MaintenanceBench','BC_ToolTrolley','BM_MechanicalSparesRack'],
'S01':['BM_ControlConsole']*3+['BM_ElectricalCabinet']*2+['BC_MaintenanceBench']*3+['BM_MechanicalSparesRack']*3+['BC_ToolTrolley']*2+['BS_ServerRack_1','BS_ServerRack_2','BS_ArchiveUPS','SD_CylinderTrolley']}
setup='''
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
'''
source=source[:start]+setup+'\nprogram='+repr(program)+'\n\n'+source[end:]
source=source.replace("paths=[];blocks=[]","paths=[];blocks=[corners(4.6,4.6)] if code=='C01' else []")
source=source.replace("name=f'B3_","name=f'B2_")
source=source.replace("role='Storage' if 'Rack' in n else 'Equipment'","role='Storage' if 'Rack' in n else 'Equipment',fit=c.get('fit'),rotation=c.get('rotation')")
source=source[:source.index(' # Two sealed carriers')]+source[source.index("plan['placements']="):]
source=source.replace("plan['placements']=placements",'''c=cat['BM_Centrifuge'];placements.append(dict(room='C01',name='B2_C01_IndustrialCentrifuge_01',model=c['name'],asset=c['asset'],position=[0,0,0],yaw=0,size=c['size'],center=c['center'],meshCollider=False,role='CentralProcess',fit=c['fit'],rotation=c['rotation']))
plan['placements']=placements''')
(H/'layout.py').write_text(source,encoding='utf8')
exec(compile(source,str(H/'layout.py'),'exec'),{'__file__':str(H/'layout.py')})
