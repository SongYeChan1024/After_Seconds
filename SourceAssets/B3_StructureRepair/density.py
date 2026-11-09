from pathlib import Path
import json,math,copy,collections
import numpy as np
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union
from shapely import contains_xy
H=Path(__file__).resolve().parent;R=H.parents[1]
p=json.loads((H/'layout_route.json').read_text(encoding='utf-8'))
cat={c['name']:c for f in [R/'SourceAssets/B3_FullFloor/catalog.json',H/'catalog.json'] for c in json.loads(f.read_text())}
def rot(x,z,yaw):
 a=math.radians(yaw);return (x*math.cos(a)+z*math.sin(a),-x*math.sin(a)+z*math.cos(a))
def body(q):
 x,y,z=q['position'];w,h,d=q['size'];cx,cy,cz=q['center']
 return Polygon([(x+rot(cx+xx,cz+zz,q['yaw'])[0],z+rot(cx+xx,cz+zz,q['yaw'])[1]) for xx,zz in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]])
def front(q):
 dx,dz=rot(q['center'][0],q['center'][2]+q['size'][2]/2+.67,q['yaw']);return (q['position'][0]+dx,q['position'][2]+dz)
def make(room,model,x,z,yaw,n):
 c=cat[model];dx,dz=rot(c['center'][0],c['center'][2],yaw)
 return dict(room=room,name=f'B3_{room}_Dense_{model.split("_",1)[-1]}_{n:02}',model=model,asset=c['asset'],position=[x-dx,0,z-dz],yaw=yaw,size=c['size'],center=c['center'],meshCollider=model=='OD_PipedDeconShower',role='Storage' if any(t in model for t in ['Rack','Freezer','Cabinet','Pallet','Island']) else 'Equipment')
def repeated(n,prefix='BS_SampleRack_'):return [prefix+str(i%3+1) for i in range(n)]
program={
 'C01':repeated(12)+['BR_B3_SampleDrawerIsland']*3+['BR_B3_LoadedTransferCart']*3+repeated(3,'BR_B3_SamplePallet_'),
 'C02':['BS_DeepFreezer']*5+['BS_ColdCabinet']*3+['BR_B3_LoadedTransferCart']*2+['B3_CryogenicDewar']*2,
 'C03':['OD_CleanPPEDispenser','OD_ClosedPPEReturn','BR_B3_SterileTrayRack','BR_B3_LoadedTransferCart']*2,
 'C04':['BR_B3_SterileTrayRack']*6+['BX_EquipmentWashStation']*2+['SF_MedicalSterilizer']*2+['BR_B3_LoadedTransferCart']*3,
 'C05':['BS_AccessionBench','BS_PackingBench','BR_B3_SampleDrawerIsland','BS_ColdCabinet']*2+['BR_B3_LoadedTransferCart']*3,
 'W01':repeated(10)+repeated(5,'BR_B3_SamplePallet_')+['BR_B3_LoadedTransferCart']*3,
 'W02':['BS_DeepFreezer','BS_ColdCabinet']*6+['BR_B3_SampleDrawerIsland']*2+['BR_B3_LoadedTransferCart']*2+['B3_CryogenicDewar']*2,
 'W03':['BS_SealedWasteStation']*3+repeated(4,'BR_B3_SamplePallet_')+['BR_B3_LoadedTransferCart']*3,
 'E01':['LB_SignalAnalysisBench','LB_ElectronicsBench','BS_AccessionBench']+['BO_SensorStorage','BS_ColdCabinet']*2+['BR_B3_LoadedTransferCart']*2,
 'E02':['BS_ServerRack_1','BS_ServerRack_2']*6+['BS_ArchiveUPS']*2+['BS_FilterBank']*2+['BR_B3_LoadedTransferCart']*2,
 'E03':repeated(8)+repeated(3,'BR_B3_SamplePallet_')+['BR_B3_LoadedTransferCart']*2+['OD_CleanPPEDispenser']*2,
 'N01':['BS_AccessionBench']*2+['BS_PackingBench']*2+repeated(6,'BR_B3_SamplePallet_')+['BR_B3_LoadedTransferCart']*4+['OD_PalletTruck'],
 'S01':['BR_B3_SterileTrayRack']*5+['SF_MedicalSterilizer']*4+['BX_EquipmentWashStation']*2+['BS_PackingBench']*2+['BR_B3_LoadedTransferCart']*3}
add=[];moves=[];unplaced=[];summary=[]
for r in p['rooms']:
 rid=r['id'];rad=r['r']
 if rid not in program:continue
 existing=[q for q in p['placements'] if q['room']==rid and q['role']!='BenchAccessory']
 if rid=='C01':
  q=next(q for q in existing if q['name']=='B3_C01_SampleTrolley_10');old=copy.deepcopy(q);q.update(position=[7.1,0,4.7],yaw=0);moves.append(dict(name=q['name'],old=old,new=copy.deepcopy(q)))
 doorZones=unary_union([LineString([(d['x'],d['z']),(d['x']*(rad-3.2)/(rad-.8),d['z']*(rad-3.2)/(rad-.8))]).buffer(1.28,cap_style=2) for d in r['doors']])
 def legal(q,placed,margin=.34):
  b=body(q);limit=math.sqrt(rad*rad-min(q['size'][1],3.5)**2)-.22
  if any(math.hypot(x,z)>limit for x,z in b.exterior.coords):return False
  if b.intersects(doorZones):return False
  f=Point(front(q));apron=f.buffer(.48)
  for other in placed:
   ob=body(other)
   bayGap=.12 if ('ServerRack' in q['model'] and 'ServerRack' in other['model']) or ('SampleRack' in q['model'] and 'SampleRack' in other['model']) else margin
   if b.distance(ob)<bayGap or apron.intersects(ob.buffer(.12)) or b.intersects(Point(front(other)).buffer(.48)):return False
  return True
 # Reposition only the objects obstructing the revised T08 entry.
 if rid in ['C03','C04']:
  bad=[q for q in existing if body(q).intersects(doorZones)]
  for q in bad:
   others=[a for a in existing if a is not q];choices=[]
   for angle in range(0,360,4):
    for rr in [rad-.9,rad-1.3,rad-1.8,rad-2.4,rad-3.1]:
     x,z=rr*math.cos(math.radians(angle)),rr*math.sin(math.radians(angle));c=make(rid,q['model'],x,z,270-angle,0)
     if legal(c,others):choices.append((math.dist([x,z],[q['position'][0],q['position'][2]]),c))
   if not choices:raise RuntimeError(('Cannot clear revised door',q['name']))
   c=min(choices,key=lambda x:x[0])[1];old=copy.deepcopy(q);q.update(position=c['position'],yaw=c['yaw']);moves.append(dict(name=q['name'],old=old,new=copy.deepcopy(q)))
   for child in p['placements']:
    if child['name'].startswith(q['name']+'_') and child['role']=='BenchAccessory':
     dx,dz=rot(child['position'][0]-old['position'][0],child['position'][2]-old['position'][2],-old['yaw']);dx,dz=rot(dx,dz,q['yaw']);oldc=copy.deepcopy(child);child['position'][0]=q['position'][0]+dx;child['position'][2]=q['position'][2]+dz;child['yaw']+=q['yaw']-old['yaw'];moves.append(dict(name=child['name'],old=oldc,new=copy.deepcopy(child)))
 # Re-align existing central furniture as part of coherent rows, not separate rotated islands.
 def row_candidates(model):
  if rid=='C01' and 'SampleRack' in model:return [(x,z,0 if z<0 else 180) for z in [-5.2,-2.3,2.3,5.2] for x in [-4.5,-1.5,1.5,4.5]]
  if rid in ['W01','E03'] and 'SampleRack' in model:return [(x,z,0 if z<=0 else 180) for z in [-3.0,0,3.0] for x in [-3.0,0,3.0]]
  if rid=='N01':
   if model=='BS_AccessionBench':return [(-4.4,z,90) for z in [-3,0,3]]
   if model=='BS_PackingBench':return [(0,z,270) for z in [-3,0,3]]
   if 'SamplePallet' in model:return [(x,z,90) for z in [-3,0,3] for x in [3.2,5.2]]
   if 'Cart' in model or 'Truck' in model:return [(x,z,0 if z<0 else 180) for z in [-5.2,5.2] for x in [-4.4,0,4.4]]
  return []
 central=[q for q in existing if '_Central' in q['name'] and row_candidates(q['model'])]
 fixed=[q for q in existing if q not in central]
 for q in central:
  options=[]
  for x,z,yaw in row_candidates(q['model']):
   c=make(rid,q['model'],x,z,yaw,0)
   if legal(c,fixed):options.append((math.dist([x,z],[q['position'][0],q['position'][2]]),c))
  if options:
   old=copy.deepcopy(q);c=min(options,key=lambda x:x[0])[1];q.update(position=c['position'],yaw=c['yaw']);moves.append(dict(name=q['name'],old=old,new=copy.deepcopy(q)))
  fixed.append(q)
 placed=list(existing);roomadd=[]
 # A grid keeps rows aligned; wider storage units use 3m bays and cold/server units use smaller bays.
 for n,model in enumerate(program[rid]):
  candidates=[]
  if row_candidates(model):candidates=row_candidates(model)
  elif rid=='E02' and 'ServerRack' in model:
   for x in [-5.2,-1.8]:
    for z in [-2.55,-1.53,-.51,.51,1.53,2.55]:candidates.append((x,z,90 if x< -3 else 270))
  else:
   width=cat[model]['size'][0];sx=3.0 if width>2.5 else 2.35 if width>1.6 else 1.4
   depth=cat[model]['size'][2];sz=max(2.4,depth+1.35)
   for zi in range(-4,5):
    for xi in range(-5,6):
     x=xi*sx+(sx*.5 if zi%2 else 0);z=zi*sz
     if abs(x)<.75 and abs(z)<1.1:continue
     if math.hypot(x,z)>rad-1.4:continue
     candidates.append((x,z,0 if z<=0 else 180))
   # Ninety degree alternatives fit service bays without random rotation.
   candidates+= [(z,x,90 if z<=0 else 270) for x,z,yaw in list(candidates)]
  valid=[]
  for x,z,yaw in candidates:
   q=make(rid,model,x,z,yaw,n+1)
   if legal(q,placed):
    near=min((body(q).distance(body(a)) for a in roomadd),default=2)
    score=abs(math.hypot(x,z)-rad*.43)+near*.7
    valid.append((score,q))
  if not valid:unplaced.append([rid,model]);continue
  q=min(valid,key=lambda a:a[0])[1];placed.append(q);roomadd.append(q)
 add+=roomadd
 summary.append(dict(room=rid,before=len(existing),added=len(roomadd),beforeArea=round(unary_union([body(q) for q in existing]).area,2),afterArea=round(unary_union([body(q) for q in placed]).area,2),roomArea=round(math.pi*rad*rad,2)))
p['placements']+=add
# New desktop kits only on bare front-left portions of drawer islands and sterilizer tops.
accessories=[]
for q in add:
 if q['model'] not in ['BR_B3_SampleDrawerIsland']:continue
 c=cat['BR_B3_SealingKit'];dx,dz=rot(.6,.37,q['yaw'])
 accessories.append(dict(room=q['room'],name=q['name']+'_SealingKit',model=c['name'],asset=c['asset'],position=[q['position'][0]+dx,1.557,q['position'][2]+dz],yaw=q['yaw'],size=c['size'],center=c['center'],meshCollider=False,role='BenchAccessory'))
p['placements']+=accessories
p['workspaces']=[dict(room=q['room'],name=q['name'],point=[front(q)[0],0,front(q)[1]]) for q in p['placements'] if q['role']!='BenchAccessory']
p['zones']=[dict(room=q['room'],name=q['name'],polygon=list(body(q).exterior.coords),center=list(body(q).centroid.coords)[0],size=[q['size'][0],q['size'][2]],yaw=q['yaw']) for q in p['placements'] if q['role']!='BenchAccessory']
(H/'layout_after.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
(H/'density_delta.json').write_text(json.dumps(dict(additions=add+accessories,moves=moves,summary=summary,unplaced=unplaced),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(added=len(add),accessories=len(accessories),moved=len(moves),total=len(p['placements']),summary=summary,unplaced=len(unplaced)),indent=2))
