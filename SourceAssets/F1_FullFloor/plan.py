"""Factory plan derived from the current 1F decision graph. Unity world X/Z metres."""
from pathlib import Path
import sys,json,math
H=Path(__file__).resolve().parent;R=H.parents[1];U=R/'Unity/After_Seconds_Build_V0.01'
sys.path.insert(0,str(U/'Temp/ZFightingReview/deps'))
from shapely.geometry import Polygon,LineString,box,Point
from shapely.ops import unary_union,triangulate
from shapely import constrained_delaunay_triangles
source=json.loads(next((R/'Docs').glob('**/Decision/*/facility_layout.json')).read_text(encoding='utf8'))
floor=next(f for f in source['floors'] if f['id']=='1F')
sizes={'C01':(28,28,6.7),'C02':(20,20,5.6),'C03':(14,14,3.8),'C04':(14,14,3.8),'VA':(10,10,4.2),'VB':(10,10,4.2),'VL':(10,10,4.6)}
rooms=[];polys={}
for q in floor['rooms']:
 if q['id']=='OUT':continue
 id=q['id'];x=q['x'];z=-q['v'];w,d,h=sizes[id];bounds=[x-w/2,z-d/2,x+w/2,z+d/2];polys[id]=box(*bounds)
 rooms.append(dict(id=id,name=q['name'],x=x,z=z,w=w,d=d,h=h,bounds=bounds,kind=q['kind'],doors=[]))
paths=[('T01','VB','C02',[(44,-28),(37,-28),(28,-21),(24,-8)]),('T02','C02','C01',[(24,-8),(-12,0)]),('T03','C01','C03',[(-12,0),(-18,-16),(-30,-16),(-30,-26)]),('T04','C03','OUT',[(-30,-26),(-51,-28)]),('T05','VL','C02',[(44,28),(44,18),(24,8),(24,-8)]),('T06','VA','C04',[(-44,28),(-12,25)]),('T07','C04','C01',[(-12,25),(-12,0)])]
hallpolys=[];tunnels=[]
for id,a,b,points in paths:
 line=LineString(points);shape=line.buffer(2.1,cap_style=2,join_style=2);hallpolys.append(shape);tunnels.append(dict(id=id,a=a,b=b,path=points,w=4.2,h=3.4))
 for rid in [a,b]:
  if rid=='OUT':continue
  q=next(q for q in rooms if q['id']==rid);hit=line.intersection(polys[rid].boundary)
  pts=[hit] if hit.geom_type=='Point' else list(hit.geoms)
  for pt in pts:q['doors'].append(dict(id=id,point=[pt.x,0,pt.y]))
hallunion=unary_union(hallpolys);roomunion=unary_union(list(polys.values()));yard=box(-68,-39,-48,-17)
whole=unary_union([roomunion,hallunion,yard]);assert whole.geom_type=='Polygon'
walls=[];roofpolys=[]
def lines(g):
 if g.geom_type=='LineString':yield g
 elif hasattr(g,'geoms'):
  for x in g.geoms:yield from lines(x)
for q in rooms:
 id=q['id'];poly=polys[id];coords=list(poly.exterior.coords)
 for i in range(4):
  cut=LineString(coords[i:i+2]).difference(hallunion.buffer(.025))
  for j,seg in enumerate(lines(cut)):
   a,b=seg.coords[0],seg.coords[-1]
   if seg.length<.10:continue
   walls.append(dict(name=f'{id}_Wall_{i}_{j}',room=id,a=a,b=b,h=q['h'],th=.24,window=seg.length>4.3 and id.startswith('C')))
for t,poly in zip(tunnels,hallpolys):
 outside=poly.difference(roomunion).difference(yard)
 parts=[outside] if outside.geom_type=='Polygon' else list(outside.geoms)
 for k,p in enumerate(parts):
  if p.area<.1:continue
  roofpolys.append(dict(room=t['id'],points=list(p.exterior.coords)[:-1],h=3.4))
  coords=list(p.exterior.coords)
  for i,(a,b) in enumerate(zip(coords,coords[1:])):
   mid=Point((a[0]+b[0])/2,(a[1]+b[1])/2)
   if roomunion.buffer(.04).contains(mid) or yard.buffer(.04).contains(mid):continue
   walls.append(dict(name=f'{t["id"]}_Wall_{k}_{i}',room=t['id'],a=a,b=b,h=3.4,th=.18,window=False))
placements=[]
def add(room,model,x,z,yaw=0,y=0,access=True,scale=1):
 r=next((q for q in rooms if q['id']==room),dict(x=-58,z=-28));i=sum(p['room']==room for p in placements)+1
 placements.append(dict(name=f'F1_{room}_{model}_{i:02}',room=room,model=model,position=[r['x']+x,y,r['z']+z],yaw=yaw,access=access,scale=scale))
# Each factory cell has working clearance, a readable approach, and a second way around it.
for args in [('Press',-4,2,0),('ConveyorLong',3,2,0),('ConveyorShort',6,-4,90),('Forklift',7,-8,-25),('CableReel',-8,-7,20),('CableReel',-5.5,-7,-15),('PartsRack',-10,7,90),('PartsRack',-10,3,90),('PartsRack',-5,11,180),('PartsRack',0,11,180),('MotorBench',7,10,180),('Switchgear',11,7,-90),('Switchgear',11,4,-90),('CrateLoad_A',-10,-1,0),('CrateLoad_B',-10,-4,90),('DrumGroup',3,-9,0),('ScrapBin',10,-11,0),('ToolCart',-7,5,-90)]:add('C01',*args)
for x,z in [(-11,10),(10,11),(-10,-10),(9,-1)]:add('C01','SafetyStation',x,z,0,access=False)
for args in [('CrateLoad_A',-6,-5,0),('CrateLoad_B',-6,-1,0),('CrateLoad_A',-6,3,90),('PalletStack',-2,-6,0),('PalletStack',5,-4,0),('PalletJack',-.5,-2,25),('HandTruck',5,1,-10),('ShippingDesk',-5,7,180),('PartsRack',0,7,180),('ShippingCage',6,5,0),('DrumGroup',6,-7,0),('SafetyStation',-8,6,90),('ScrapBin',-8,-7,0)]:add('C02',*args)
# Office left side / break room right side; leave a direct cross-building passage.
for args in [('OfficeDesk_A',-4,3.8,180),('OfficeDesk_B',-1,3.8,180),('OfficeDesk_C',-4,-3.7,0),('FileCabinet',-5.8,.8,90),('FileCabinet',-5.8,-.6,90),('Locker',4.8,-5.7,0),('Locker',3.2,-5.7,0),('BreakTable',3.7,3.3,0),('KitchenCounter',5.9,.4,-90),('NoticeBoard',2.6,6.72,180),('SafetyStation',-6.65,-4.8,90)]:add('C04',*args)
# Gate duty is off the through route; open pedestrian lanes flank the inspection desk.
for args in [('SecurityDesk',-1,3.7,180),('Scanner',3,0,0),('RadioCabinet',5.9,3.9,-90),('KeyBoard',-3,6.72,180),('FileCabinet',-5.8,4,90),('InspectionCounter',-3.7,-3.3,0),('Bench',3.7,-5.7,0),('SafetyStation',5.7,-5.8,0),('BarrierPedestal',-3.2,.2,0),('BarrierPedestal',-5.6,.2,0)]:add('C03',*args)
for id in ['VA','VB']:
 add(id,'ArrivalFireDoor',0,-4.72,0,access=False);add(id,'NoticeBoard',3.9,4.72,180,access=False);add(id,'SafetyStation',-4.65,2,90,access=False)
add('VL','LiftCabin',0,-1.25,0,access=False);add('VL','SafetyStation',-4.6,2.6,90,access=False)
for args in [('GateBarrier',5,0,90),('GuardBollard',5,-2.7,0),('GuardBollard',5,2.7,0),('DrumGroup',-6,8,0),('CableReel',-5,-8,0)]:add('OUT',*args,access=False)
# Small handled items have their own inspectable shapes and discrete placements.
for room,x,z in [('C01',7,9.8),('C02',-5.5,6.9),('C04',-4,3.7),('C03',-1.5,3.6)]:add(room,'HardHat',x,z,y=.91 if room=='C01' else .825,access=False)
for room,x,z in [('C02',-4.5,6.8),('C03',-.5,3.5),('C04',-1.3,3.6)]:add(room,'HandRadio',x,z,y=.825,access=False)
for room,x,z in [('C01',-7,5),('C02',1,6.9),('C04',-4.5,-3.5),('C03',-4,-3.2)]:add(room,'ShippingRecord',x,z,y=.92 if room=='C01' else .83,access=False)
floortri=[]
for tri in constrained_delaunay_triangles(whole).geoms:
 assert tri.difference(whole).area<1e-7
 floortri.append(list(tri.exterior.coords)[:3])
assert abs(sum(Polygon(t).area for t in floortri)-whole.area)<.001
arrivals=[dict(id='VA',position=[-44,0,24.2],yaw=0),dict(id='VB',position=[44,0,-31.8],yaw=0),dict(id='VL',position=[44,.075,26.8],yaw=0)]
plan=dict(version='V0.01',source='Decision/facility_layout.json 1F',rooms=rooms,tunnels=tunnels,walls=walls,corridorRoofs=roofpolys,floorOutline=list(whole.exterior.coords)[:-1],floorTriangles=floortri,placements=placements,arrivals=arrivals,yard=[-68,-39,-48,-17],out=[-51,0,-28],notes='Final surface floor. Graph and room centres retained; factory rectilinear envelopes and portal-safe corridor bends. Runtime transition/AI/ending not implemented.')
(H/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8')
print({'rooms':len(rooms),'links':len(tunnels),'placements':len(placements),'floorArea':round(whole.area,2),'walls':len(walls)},flush=True)
