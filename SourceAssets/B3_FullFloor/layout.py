from pathlib import Path
import json,math
H=Path(__file__).resolve().parent;plan=json.loads((H/'plan.json').read_text(encoding='utf-8'));cat={x['name']:x for x in json.loads((H/'catalog.json').read_text())}
def racks(n):return ['BS_SampleRack_'+str(i%3+1) for i in range(n)]
program={
'C01':racks(8)+['LP_SampleTrolley']*3+['BS_AccessionBench','BS_PackingBench','B3_CryogenicDewar'],
'C02':['BS_DeepFreezer']*3+['BS_ColdCabinet']*2+['BO_SensorStorage','B3_CryogenicDewar','BS_ArchiveUPS'],
'C03':['BS_SealedWasteStation','OD_ClosedPPEReturn','OD_CleanPPEDispenser','SF_DeconChangeBench','BS_ColdCabinet'],
'C04':['OD_PipedDeconShower','SF_MedicalSterilizer']*1+['SF_DoubleWashSink','OD_ClosedPPEReturn','OD_CleanPPEDispenser','SD_CylinderTrolley','BS_PackingBench'],
'C05':['SD_CentrifugeBench']*2+['LB_SensorPrepBench','BS_PackingBench','BS_ColdCabinet','BO_SensorStorage','LP_SampleTrolley','B3_CryogenicDewar'],
'W01':racks(7)+['BS_AccessionBench','BS_PackingBench','LP_SampleTrolley','B3_CryogenicDewar'],
'W02':['BS_DeepFreezer']*4+['BS_ColdCabinet']*2+['BS_ArchiveUPS','B3_CryogenicDewar']*2+['LP_SampleTrolley'],
'W03':['BS_SealedWasteStation']*2+['OD_ClosedPPEReturn','BS_ColdCabinet','BS_PackingBench','SF_MedicalSterilizer','BO_SensorStorage'],
'E01':['LB_SignalAnalysisBench']*2+['LB_ElectronicsBench','LB_AcquisitionCart','BS_ColdCabinet','BS_AccessionBench','BO_SensorStorage','LP_SampleTrolley'],
'E02':['BS_ServerRack_1','BS_ServerRack_2']*4+['BS_ArchiveUPS']*2+['BS_FilterBank','SD_MaintenanceStation','BS_AccessionBench'],
'E03':racks(6)+['BS_PackingBench','LP_SampleTrolley','OD_CleanPPEDispenser','BO_SensorStorage'],
'N01':['BS_AccessionBench']*3+['BS_PackingBench']*2+racks(2)+['LP_SampleTrolley']*2+['BS_ColdCabinet','B3_CryogenicDewar'],
'S01':['SF_MedicalSterilizer']*3+['SF_DoubleWashSink']*2+['BS_PackingBench']*2+['OD_CleanPPEDispenser','BS_SealedWasteStation','LP_SampleTrolley']}
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
 paths=[];blocks=[]
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
  name=f'B3_{code}_{n.split("_",1)[1]}_{i+1:02}'
  placements.append(dict(room=code,name=name,model=n,asset=c['asset'],position=[x-ox,0,z-oz],yaw=yaw,size=c['size'],center=c['center'],meshCollider=n in ['OD_PipedDeconShower'],role='Storage' if 'Rack' in n else 'Equipment'))
  zones.append(dict(room=code,name=name,center=[x,z],size=[w,d],yaw=yaw,polygon=poly))
 # Two sealed carriers on selected receiving/prep surfaces, placed clear of instrument bodies.
 for q in [p for p in placements if p['room']==code and p['model']=='BS_PackingBench']:
  c=cat['B3_SealedSampleCarrier'];dx,dz=turn(.12,-.285,q['yaw']);placements.append(dict(room=code,name=q['name']+'_SealedCarrier',model=c['name'],asset=c['asset'],position=[q['position'][0]+dx,.958,q['position'][2]+dz],yaw=q['yaw']+17,size=c['size'],center=c['center'],meshCollider=False,role='BenchAccessory'))
plan['placements']=placements;plan['zones']=zones;plan['unplaced']=fail
(H/'layout.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'placements':len(placements),'perRoom':{r['id']:sum(p['room']==r['id'] for p in placements) for r in plan['rooms']},'unplaced':fail},indent=2))
if fail:raise RuntimeError('Unplaced equipment: revise layout before build')
