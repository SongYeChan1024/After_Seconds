"""Approved B2 operations layout, room-local Unity X/Y/Z. Author: Song Yechan."""
import json,math,hashlib
from pathlib import Path
from shapely.geometry import Point,LineString,Polygon,box
from shapely.ops import unary_union,triangulate
from shapely import affinity
H=Path(__file__).resolve().parent;R=H.parents[1]
old=json.loads((R/'SourceAssets/B2_FullFloor/layout.json').read_text(encoding='utf8'))
bn=json.loads((R/'SourceAssets/B2_DomeNetwork/layout.json').read_text(encoding='utf8'))
catalog={}
for p in old['placements']+bn['placements']:
 catalog.setdefault(p['model'],dict(source=p['name'],size=p['size'],center=p['center'],asset=p.get('asset','')))
rooms={r['id']:r for r in old['rooms'] if r['kind']=='cavern'}
plan=dict(version='0.01',author='송예찬',rooms=list(rooms.values()),catalog=catalog,placements=[],decks={},services={},routes=[])
aliases=dict(pump='BM_CoolingPump',drive='BC_PumpDriveCabinet',heat='BC_PlateHeatExchanger',bench='BC_MaintenanceBench',cart='BC_ToolTrolley',rack='BM_MechanicalSparesRack',filter='BM_WaterFilterSkid',tank='BM_SealedProcessTank',console='BM_ControlConsole',ups='BS_ArchiveUPS',server='BS_ServerRack_1',server2='BS_ServerRack_2',power='BM_PowerTransformer',valve='BC_UpperValveStation',generator='B2_EmergencyGenerator',case='BX_EquipmentCaseRack',cylinder='SD_CylinderTrolley',air='BM_AirFilterSkid',hvac='BM_HVACUnit',fan='BM_VentilationFan',sink='SF_DoubleWashSink',returnbin='OD_ClosedPPEReturn',ppe='OD_CleanPPEDispenser',centrifuge='BM_Centrifuge',surge='BN_SurgeReservoir',plenum='BN_AirPlenum',fuel='BN_DayTank',manifold='BN_ServiceManifold',motor='BN_MotorSpares')
def put(room,group,kind,x,z,yaw=0,y=0):
 model=aliases[kind]; i=1+sum(p['room']==room for p in plan['placements'])
 p=dict(name=f'B2_{room}_Ops_{group}_{i:02}',room=room,group=group,model=model,position=[x,y,z],yaw=yaw,**catalog[model]);plan['placements'].append(p);return p
def row(room,group,kind,points,yaw=0):
 for x,z in points:put(room,group,kind,x,z,yaw)
# C02: two pump trains with an accessible centre aisle; controls remain dry.
row('C02','PumpTrainA','pump',[(-2.5,-2),(-2.5,0),(-2.5,2)],90)
row('C02','PumpTrainB','pump',[(2.3,-1),(2.3,1)],270)
row('C02','HeatExchange','heat',[(-.9,5),(1.1,5)],180)
put('C02','Accumulator','surge',3.8,3.1,180)
row('C02','DryControl','drive',[(7.6,-1.5),(7.6,0),(7.6,1.5)],270)
put('C02','Maintenance','bench',-5.7,-4.4)
put('C02','PartsStaging','motor',1,-5.5)
put('C02','PartsStaging','cart',-1,-6.2)
put('C02','Maintenance','rack',-7.9,-3.8,90)
put('C02','SupplyHeader','manifold',-.8,7.9,180)
put('C02','ReturnHeader','manifold',2,7.9,180)
# C01: actual two-train process, five doors remain joined by the outer route.
row('C01','SeparationTrain','centrifuge',[(-3,0),(3,0)])
row('C01','FeedTreatment','filter',[(-3,4),(3,4)],180)
row('C01','DischargeCooling','heat',[(-3,-3.6),(3,-3.6)])
row('C01','ProcessControl','drive',[(-5.5,-3.7),(5.5,-3.7)])
row('C01','FeedHeader','manifold',[(-3,6.4),(3,6.4)],180)
row('C01','MotorRemoval','motor',[(-5.4,1.8),(5.4,1.8)],90)
row('C01','Maintenance','bench',[(-3,-7),(3,-7)])
row('C01','Parts','rack',[(-6,-5.8),(6,4.2)],90)
row('C01','CartBay','cart',[(-1.5,-7),(1.5,-7)])
put('C01','Handover','console',-7.5,2.8,90)
# C03: U-shaped switchgear facing a shared inspection aisle, no wet equipment.
row('C03','Switchboard','drive',[(-2.8,-1.8),(-2.8,-.3),(-2.8,1.2)],90)
row('C03','Switchboard','drive',[(-1.1,3),(0.4,3),(1.9,3)],180)
put('C03','BackupPower','ups',-3.6,2.8,90)
put('C03','TestEquipment','bench',.8,-.8)
put('C03','MeterCart','cart',-1.6,-3.4)
# C04: operation consoles, rear service lane and handover side station.
row('C04','Operations','console',[(-1.8,-.8),(0,-.8),(1.8,-.8)])
row('C04','RearRackRow','server',[(-2.8,-4.6),(-1.6,-4.6),(-.4,-4.6)],0)
row('C04','RearRackRow','server2',[(.8,-4.6),(2,-4.6)],0)
put('C04','Backup','ups',3.5,-3.8)
put('C04','Handover','bench',-4.4,-1.6,90)
put('C04','ServiceCart','cart',-4.8,-3.3,90)
put('C04','Distribution','drive',4.4,2,270)
# W01: two transformer banks, front isolation panels, dry cable distribution.
row('W01','TransformerBank','power',[(-2.6,1.8),(2.6,1.8),(-2.6,4.6),(2.6,4.6)])
row('W01','Isolation','drive',[(-2.6,-1.1),(2.6,-1.1)])
row('W01','Switchgear','drive',[(-3,-4.9),(-1.5,-4.9),(0,-4.9),(1.5,-4.9),(3,-4.9)])
row('W01','BatteryBackup','ups',[(-5.6,.4),(5.6,3)],90)
put('W01','TestBay','bench',0,6.3,180)
put('W01','MeterCart','cart',5.2,-3.4,270)
# W02: two parallel generator trains, fuel day tank at their rear.
row('W02','GeneratorTrain','generator',[(-3,-2.6),(-3,.1),(-3,2.8)])
row('W02','FuelDistribution','manifold',[(-5.5,-2.6),(-5.5,.1),(-5.5,2.8)],90)
put('W02','DayTank','fuel',-2.4,6,180)
row('W02','Control','drive',[(1,-5.6),(2.5,-5.6)])
put('W02','Backup','ups',-.5,-7.2)
put('W02','Maintenance','bench',-2.4,-6.4)
put('W02','ToolBay','cart',-4.6,-5.2)
row('W02','ServiceSpares','motor',[(.2,4.7),(-5,4.8)])
put('W02','Consumables','rack',0,6.7,180)
# W03: receiving left, storage rows, repair rear, dispatch right; wide middle aisle.
row('W03','PartsA','rack',[(-3,-2),(-3,.2),(-3,2.4)],90)
row('W03','PartsB','rack',[(2,-2),(2,.2),(2,2.4)],270)
row('W03','Repair','bench',[(-2.5,-5.3),(0,-5.7),(2.5,-5.3)])
for x in [-2.5,2.5]:put('W03','RepairMotors','motor',x+.3,-5.18,y=.985)
put('W03','Receiving','case',-5.4,1.8,90)
put('W03','Receiving','cart',-5.6,-.3,90)
row('W03','Dispatch','cart',[(4.7,-.2),(4.7,-1.5)],270)
put('W03','HeavyParts','rack',0,5.5,180)
put('W03','WeldingBay','cylinder',-5.2,-3.7)
put('W03','ServicePower','drive',4.7,4.5,230)
# E01: eccentric accumulator, boost train and treatment line. No all-room ring.
put('E01','Accumulator','surge',0,2.3)
row('E01','Treatment','filter',[(-3.8,2),(-3.8,4.5)],90)
row('E01','BoostTrain','pump',[(1.4,-2),(1.4,-.4),(3.4,-.4)],270)
row('E01','DryControls','drive',[(-2.6,-4.4),(-1,-4.4)])
put('E01','WaterHeader','manifold',-.5,5.6,180)
put('E01','WaterHeader','valve',-2,6,180)
put('E01','Maintenance','bench',-5.3,.1,90)
put('E01','SpareSeals','cart',-.5,-6.7)
put('E01','PumpRemoval','motor',3.3,-2.2,180)
# E02: west filter-change face, east motor aisle, overhead damper service.
row('E02','FilterBank','air',[(2,-2.8),(2,0),(2,2.8)],270)
row('E02','FanDrive','fan',[(5.5,-2.8),(5.5,0),(5.5,2.8)],270)
put('E02','Plenum','plenum',2,5.7,90)
put('E02','CleanFilters','rack',-2.3,5.4,180)
put('E02','SealedReturns','returnbin',-2.4,-4.4)
put('E02','PressureReadings','drive',-5.8,.4,90)
put('E02','ServiceBench','bench',-.3,-6.8)
put('E02','FilterCart','cart',-4.7,-3,90)
put('E02','MotorSpares','motor',4.5,-5.3)
# E03: wet process trains and dry records/controls on opposite sides.
row('E03','SealedWaste','tank',[(-2,-2.6),(.5,-2.6),(3,-2.6)])
row('E03','TransferPumps','pump',[(-2,-4.8),(1,-4.8)],180)
put('E03','Treatment','filter',4.9,.2,270)
row('E03','DryControls','drive',[(-2.8,3),(-1.3,3)],180)
put('E03','DryRecords','console',.5,4.6,180)
put('E03','Decontamination','sink',-4.8,-2.8,90)
put('E03','SealedReturns','returnbin',2.9,1)
put('E03','PPE','ppe',-4.7,2.8,90)
put('E03','WetHeader','manifold',4,-4.4)
put('E03','ServiceCart','cart',-3.4,4.6,180)
# N01: longitudinal fan banks with motor withdrawal lanes, overhead ducts.
row('N01','FanBankA','fan',[(-3,-2.5),(-3,.2),(-3,2.9)],90)
row('N01','FanBankB','fan',[(3,-2.5),(3,.2),(3,2.9)],270)
row('N01','IntakeFilters','air',[(-3,6),(0,6),(3,6)],180)
row('N01','DriveControls','drive',[(-3,-6),(3,-6)])
row('N01','ServiceSpares','motor',[(-6,.2),(6,.2)])
row('N01','ServiceBenches','bench',[(-6,3.4),(6,3.4)],90)
row('N01','DuctEquipment','hvac',[(-6,-3.2),(6,-3.2)],90)
put('N01','ToolBay','cart',0,8.2,180)
# S01: working test benches with incoming/outgoing repair bays, distinct from storage.
row('S01','DiagnosticBench','bench',[(-3,0),(-3,-2.8),(3,0),(3,-2.8)])
for x,z in [(-3,0),(-3,-2.8),(3,0),(3,-2.8)]:put('S01','TestMotors','motor',x+.3,z+.12,y=.985)
row('S01','StatusStation','console',[(-1.8,5),(0,5),(1.8,5)],180)
row('S01','TestPower','drive',[(-3,-6),(3,-6)])
row('S01','Tools','rack',[(-6,0),(6,0)],90)
row('S01','IncomingRepair','cart',[(-5,4),(-3.5,4)])
row('S01','ReleasedRepair','cart',[(5,3),(6.4,3)])
put('S01','Recording','server',-1.8,-7)
put('S01','Recording','server2',-.6,-7)
put('S01','Backup','ups',1.2,-7)
put('S01','ServiceGas','cylinder',6,-3.5)

def deck(room,paths,stairs,links):
 """Union floor polygons; boundary rails are removed at actual stair mouths."""
 parts=[LineString(p).buffer(w/2,cap_style=3,join_style=2) for p,w in paths]
 footprint=unary_union(parts).buffer(0)
 assert footprint.geom_type=='Polygon',room
 # Finish each rise at the deck boundary, then cross a level landing. Avoid a
 # half-metre lip where a sloped portal stair used to continue under the deck.
 landing_footprints=[footprint]
 for st in stairs+links:
  for a,b in zip(st,st[1:]):
   if abs(a[1]-3.6)<.01 and abs(b[1]-3.6)<.01:landing_footprints.append(LineString([(a[0],a[2]),(b[0],b[2])]).buffer(.775,cap_style=2))
 all_landings=unary_union(landing_footprints)
 for collection in [stairs,links]:
  for si,st in enumerate(collection):
   corrected=[st[0]]
   for a,b in zip(st,st[1:]):
    line=LineString([(a[0],a[2]),(b[0],b[2])])
    if b[1]>a[1]+.1 and all_landings.intersects(line):
     intersection=line.intersection(all_landings);coords=[]
     for segment in getattr(intersection,'geoms',[intersection]):
      if hasattr(segment,'coords'):coords.extend(segment.coords)
     ds=sorted(line.project(Point(q)) for q in coords)
     if ds and ds[0]>0.1 and ds[0]<line.length-.03:
      q=line.interpolate(max(.01,ds[0]-.04));corrected.append([q.x,b[1],q.y])
    corrected.append(b)
   collection[si]=corrected
 rail=footprint.boundary
 for s in stairs+links:
  # Last point is on the deck; cut the boundary around that mouth only.
  rail=rail.difference(LineString([(q[0],q[2]) for q in s]).buffer(.94,cap_style=3,join_style=2))
 rails=[]
 for ln in getattr(rail,'geoms',[rail]):
  coords=list(ln.coords)
  for a,b in zip(coords,coords[1:]):
   if math.dist(a,b)>.08:rails.append([list(a),list(b)])
 triangles=[list(t.exterior.coords)[:3] for t in triangulate(footprint) if footprint.covers(t)]
 bars=[]
 for axis,spacing in [(0,.10),(1,.32)]:
  for i in range(-140,141):
   d=i*spacing;line=LineString([(d,-20),(d,20)] if axis==0 else [(-20,d),(20,d)])
   for seg in getattr(line.intersection(footprint),'geoms',[line.intersection(footprint)]):
    if seg.geom_type=='LineString' and seg.length>.025:bars.append([list(seg.coords[0]),list(seg.coords[-1]),axis])
 plan['decks'][room]=dict(paths=paths,stairs=stairs,links=links,outline=list(footprint.exterior.coords),triangles=triangles,bars=bars,rails=rails)
 for i,(path,w) in enumerate(paths):plan['routes'].append(dict(name=f'{room}_Upper_{i}',room=room,height=1.8,points=[[x,3.6,z] for x,z in path]))
 for i,s in enumerate(stairs+links):plan['routes'].append(dict(name=f'{room}_Stair_{i}',room=room,height=1.2 if i>=len(stairs) else 1.8,points=s))
def portal(room,tid,landing):
 d=next(d for d in rooms[room]['doors'] if d['id']=='B2-'+tid)
 return [[d['x'],2.42,d['z']],[landing[0],3.6,landing[1]]]
deck('C02', [([[-5.4,2.7],[-5.4,5.6],[-2.4,7.4],[2,7.4],[5.2,4.8],[7,2.4],[5.4,-1.3]],1.65)],
 [[[-5.4,0,-2.7],[-5.4,3.6,2.7]],[[5.4,0,-6.7],[5.4,3.6,-1.3]]], [portal('C02','T01',[5.2,4.8])])
deck('E02',[([[-3.2,-4],[-3.2,4]],1.7),([[-3.2,2.6],[-.5,2.6]],1.6)],
 [[[-.5,0,-3],[-.5,3.6,2.6]]],[portal('E02','T15',[-3.2,4]),portal('E02','T16',[-3.2,-4])])
deck('W02',[([[2.6,-4.2],[2.6,3.5],[-.4,4.2]],1.7)],
 [[[.2,0,-2.8],[.2,3.6,2.8],[2.6,3.6,2.8]]], [portal('W02','T11',[2.6,3.5]),portal('W02','T12',[2.6,-4.2])])
e14=next(d for d in rooms['E01']['doors'] if d['id']=='B2-T14');ang14=math.degrees(math.atan2(e14['z'],e14['x']))
arc=[[4.4*math.cos(math.radians(a)),4.4*math.sin(math.radians(a))] for a in [ang14]+list(range(-150,16,15))]
e15=next(d for d in rooms['E01']['doors'] if d['id']=='B2-T15');ang15=math.atan2(e15['z'],e15['x'])
deck('E01',[(arc,1.65)],
 [[[1,0,5.6],[arc[-1][0],3.6,arc[-1][1]]]],[portal('E01','T14',arc[0]),portal('E01','T15',[4.4*math.cos(ang15),4.4*math.sin(ang15)])])

for p in plan['placements']:
 if p['group'] in ['RepairMotors','TestMotors']:
  p['scale']=.65;p['size']=[v*.65 for v in p['size']];p['center']=[v*.65 for v in p['center']]
 if p['group']=='DiagnosticBench' or p['room']=='W03' and p['group']=='Repair' and p['position'][0]!=0:p['visual_variant']='BO_MotorServiceBench'
# Dimensioned pipe/duct/cable infrastructure will be authored to these actual placements.
for id in rooms:plan['services'][id]=dict(kind={'C02':'cooling','C01':'separation','W01':'power','W02':'fuel','E01':'water','E02':'air','E03':'waste','N01':'air','C03':'power','C04':'control','W03':'repair','S01':'diagnostics'}[id])

# Preserve gameplay sources/other scenes as hashes, including user's in-progress work.
protected={}
asset=R/'Unity/After_Seconds_Build_V0.01/Assets'
for p in asset.rglob('*'):
 if p.is_file() and (p.suffix in ['.cs','.controller','.inputactions'] or p.suffix=='.unity' and p.name!='Level_B2_Circular.unity'):
  protected[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
if not (H/'protected_before.json').exists():(H/'protected_before.json').write_text(json.dumps(protected,indent=2),encoding='utf8')
(H/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8')
print('placements',len(plan['placements']),'domes',len(rooms),'decks',len(plan['decks']))
