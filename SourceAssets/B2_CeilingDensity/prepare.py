"""B2 art-only revision. Keep SurfaceRefinement as immutable input."""
from pathlib import Path
import json,copy
H=Path(__file__).resolve().parent; R=H.parents[1]
C=json.loads((R/'SourceAssets/B2_SurfaceRefinement/plan.json').read_text(encoding='utf8'))
baseline=copy.deepcopy(C['placements']); changes=[]
def rows(room,model=None,group=None):
 return [p for p in C['placements'] if p['room']==room and (not model or p['model']==model) and (not group or p['group']==group)]
def scale(ps,f):
 for p in ps:
  p['relative_scale']=f;p['size']=[v*f for v in p['size']];p['center']=[v*f for v in p['center']]
def positions(ps,coords):
 for p,(x,z) in zip(ps,coords):p['position'][0]=x;p['position'][2]=z
scale(rows('C02','BM_CoolingPump'),2)
positions(rows('C02',group='PumpTrainA'),[(-2.2,-4.2),(-2.2,-.6),(-2.2,3)])
positions(rows('C02',group='PumpTrainB'),[(2.4,-2.4),(2.4,1.2)])
scale(rows('C02','BC_PlateHeatExchanger'),1.5)
positions(rows('C02','BC_PlateHeatExchanger'),[(-1.55,6.1),(1.55,6.1)])
for p in rows('C02','BC_PlateHeatExchanger'):p['yaw']=90 if p['position'][0]<0 else 270
positions(rows('C02','BN_SurgeReservoir'),[(3.8,3.9)])
positions(rows('C02',group='PartsStaging'),[(-5.3,-6),(-6.8,-6)])
positions(rows('C02','BR_PartsCradle'),[(-5.3,-6)])
for p in rows('C02','BN_MotorSpares')+rows('C02','BR_PartsCradle'):p['yaw']=180
positions(rows('C02',group='SupplyHeader'),[(-4.2,6.8)])
positions(rows('C02',group='ReturnHeader'),[(5.6,5.8)])
for p in rows('C02',group='ReturnHeader'):p['yaw']=270
scale(rows('C01','BM_Centrifuge'),1.5)
scale(rows('C01','BC_PlateHeatExchanger'),1.5)
positions(rows('C01','BC_PlateHeatExchanger'),[(-3,-4.3),(3,-4.3)])
scale(rows('C01','BM_WaterFilterSkid'),1.2)
positions(rows('C01','BM_WaterFilterSkid'),[(-3,4.6),(3,4.6)])
positions(rows('C01',group='FeedHeader'),[(-2,7.1),(2,7.1)])
positions(rows('C01','BN_MotorSpares'),[(-6.1,.8),(6.1,.8)])
for p in rows('C01','BN_MotorSpares'):p['yaw']=270 if p['position'][0]<0 else 90
scale(rows('W01','BM_PowerTransformer'),1.35)
for p in rows('W01','BM_PowerTransformer'):p['position'][2]=.5 if p['position'][2]<3 else 4.1
for p in rows('W01','BM_PowerTransformer'):
 if p['position'][2]>3:p['yaw']=180
for p in rows('W01',group='Isolation'):p['position'][2]=-1.8;p['yaw']=180
scale(rows('W02','B2_EmergencyGenerator'),1.5)
positions(rows('W02','B2_EmergencyGenerator'),[(-2.7,-3.3),(-2.7,-.1),(-2.7,3.1)])
positions(rows('W02',group='FuelDistribution'),[(-6.3,-3.3),(-6.3,-.1),(-6.3,3.1)])
scale(rows('E01','BM_CoolingPump'),1.5)
positions(rows('E01','BM_CoolingPump'),[(1.1,-2.2),(1.1,.8),(3.4,.8)])
positions(rows('E01','BN_SurgeReservoir'),[(-.6,3.1)])
positions(rows('E01',group='PumpRemoval'),[(3.6,-2)])
scale(rows('E03','BM_CoolingPump'),1.5)
positions(rows('E03','BM_CoolingPump'),[(-2,-5),(1,-5)])
scale(rows('N01','BM_HVACUnit'),1.5)
def add(room,model,group,x,z,yaw=0):
 src=copy.deepcopy(next(p for p in baseline if p['model']==model));src.update(room=room,group=group,position=[x,0,z],yaw=yaw,name=f'B2_{room}_CD_{group}_{len(C["placements"])+1:03d}')
 C['placements'].append(src)
add('S01','BC_PumpDriveCabinet','CalibrationPower',-6,-4.2,90)
add('S01','BM_MechanicalSparesRack','ServiceParts',6,-5.8,270)
add('S01','BM_MechanicalSparesRack','ServiceParts',-4.3,6.2,180)
add('S01','BC_PumpDriveCabinet','CalibrationPower',3.6,6.1,180)
add('E03','BM_SealedProcessTank','Equalization',4.6,2.8,270)
# Narrow spares cabinet in the dry side, separate from wet-pump access.
add('E03','BM_MechanicalSparesRack','FilterSpares',-1.7,5.7,180)
C['reference_images']=[p.relative_to(R).as_posix() for p in sorted((R/'Docs/Reference/B2').glob('*.jpg'))]
C['art_revision']='Dense connected plant, roof services, dark red light; no B2 floor guidance.'
for p in C['placements']:
 old=next((x for x in baseline if x['name']==p['name']),None)
 if old!=p:changes.append({'name':p['name'],'before':old,'after':p})
(H/'changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf8')
(H/'plan.json').write_text(json.dumps(C,ensure_ascii=False,indent=2),encoding='utf8')
# Rebuild only distribution, using a new namespace. Original decks remain untouched.
s=(R/'SourceAssets/B2_OperationsRebuild/build.py').read_text(encoding='utf8')
s=s.replace("from common import *","from common import *\nH=Path(__file__).resolve().parent;R=H.parents[1]\nos.environ['BO_PHASE']='services'")
s=s.replace("'BO_'","'CD_'").replace("'_LOD1'","'_Far'")
# Rotation-aware plinth dimensions: old template assumed all equipment faced +Z.
s=s.replace("box('EquipmentPlinth',x,.045,z,w+.15,.09,dep+.12,'Dark',.012)","old=set(bpy.context.scene.objects);box('EquipmentPlinth',0,.045,0,w+.15,.09,dep+.12,'Dark',.012);transform(set(bpy.context.scene.objects)-old,x,0,z,p['yaw'])")
s=s.replace("pipe([tuple(port),tuple(port+back*.22),tuple(top+back*.22),feed],.085,", "pipe([tuple(port),tuple(port+back*.22),tuple(top+back*.22),feed],.14 if p.get('relative_scale',1)>=1.5 else .085,")
s=s.replace("top=port+Vector((0,5.6-port.y,0));", "room_radius=next(q['r'] for q in C['rooms'] if q['id']==room);roof_margin=math.sqrt(max(.1,room_radius**2-(port.x+back.x*.22)**2-(port.z+back.z*.22)**2))-.48;top=port+Vector((0,min(5.6,roof_margin)-port.y,0));")
s=s.replace("tuple(port+back*.22),tuple(top+back*.22)","tuple(Vector((x,port.y+.22,z))+back*(dep*.24)),tuple(Vector((x,top.y,z))+back*(dep*.24))")
s=s.replace("'C03':[(-3.2,3.8,-2),(-3.2,3.8,3.4),(2.4,3.8,3.4)]","'C03':[(-3.2,3.8,-2),(-3.2,3.8,2.8),(2.4,3.8,2.8)]")
s=s.replace("tube('TunnelToProcessHeader',[tuple(a),(a.x,6.0,a.z),(x,6.0,target[2]),target]", "lift=min(6.0,math.sqrt(max(.1,rr['r']**2-a.x*a.x-a.z*a.z))-.36);tube('TunnelToProcessHeader',[tuple(a),(a.x,lift,a.z),(x,lift,target[2]),target]")
s=s.replace("for room,services in C['services'].items():", "for room,services in C['services'].items():\n if os.environ.get('CD_SERVICE_ROOM') and room!=os.environ['CD_SERVICE_ROOM']:continue")
s=s.replace("['BM_AirFilterSkid','BM_VentilationFan']:continue", "['BM_AirFilterSkid','BM_VentilationFan','BM_HVACUnit']:continue")
s=s.replace("if room=='E02' and x>3:", "if room=='N01' and abs(x)<.1:box('CentreFilterReturnDuct',1.5,5.4,z,3,1.05,.75,'Pipe',.012)\n   if room=='N01' and abs(x)>4:\n    target_x=3 if x>0 else -3;box('HVACConnectionDuct',(x+target_x)/2,5.4,z,abs(x-target_x),1.05,.75,'Pipe',.012)\n   if room=='E02' and x>3:")
# The three waste tanks retain their original positions and catch trays.
(H/'services.py').write_text(s,encoding='utf8')
print('placements',len(C['placements']),'modified/new',len(changes),'scaled',sum('relative_scale' in p for p in C['placements']))
