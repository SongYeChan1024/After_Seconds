import json,math,random,copy
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
old=json.loads((R/'SourceAssets/B2_FullFloor/layout.json').read_text(encoding='utf8'))
rooms={r['id']:r for r in old['rooms']}
config={'version':'0.01','rooms':old['rooms'],'ends':{'T01':['C02'],'T11':['W02'],'T12':['W02'],'T14':['E01'],'T15':['E01','E02'],'T16':['E02']},'decks':{'E01':4.4,'E02':4.8,'W02':4.8},'tunnels':[],'placements':[]}
for t in old['tunnels']:
 t=copy.deepcopy(t);t['id']=t['id'].split('-')[1]
 if t['id'] in config['ends']:config['tunnels'].append(t)
# Retain native fit/bounds metadata when reusing existing art.
templates={p['model']:p for p in old['placements']}
catalog={p['name']:p for p in json.loads((R/'SourceAssets/B2_FullFloor/catalog.json').read_text(encoding='utf8'))}
for key in ['BC_ToolTrolley','BC_MaintenanceBench','BC_PlateHeatExchanger','BC_UpperValveStation','BM_MechanicalSparesRack']:
 if key not in templates and key in catalog:
  templates[key]={'model':key,**catalog[key],'fit':None}
def add(room,model,x,z,yaw=0):
 p=copy.deepcopy(templates[model]);p.update(room=room,model=model,name=f'B2_{room}_Dense_{len(config["placements"])+1:03d}_{model[3:]}',position=[x,0,z],yaw=yaw)
 config['placements'].append(p);return p
for name,size in [('BN_SurgeReservoir',[1.8,4.75,1.8]),('BN_AirPlenum',[2.25,4.85,2.15]),('BN_DayTank',[2.25,3.0,1.65]),('BN_ServiceManifold',[1.45,2.05,.72]),('BN_MotorSpares',[1.4,.95,.85])]:
 templates[name]={'model':name,'asset':'Assets/Afrer_Seconds/05.Model/Props/B2/'+name+'.fbx','size':size,'center':[0,size[1]/2,0],'fit':None}
for room,model in [('E01','BN_SurgeReservoir'),('E02','BN_AirPlenum'),('W02','BN_DayTank')]:add(room,model,2.15,0)
# Broad-phase circular clearances protect existing footprints, fronts and door spokes.
def radius(p):return math.hypot(p['size'][0],p['size'][2])*.5
def distance_segment(x,z,a,c):
 dx=c[0]-a[0];dz=c[1]-a[1];d=dx*dx+dz*dz;t=max(0,min(1,((x-a[0])*dx+(z-a[1])*dz)/d)) if d else 0
 return math.hypot(x-a[0]-dx*t,z-a[1]-dz*t)
def okay(room,p,x,z):
 rr=radius(p);r=rooms[room]
 if math.hypot(x,z)+rr>r['r']-1.65:return False
 # Continuous centre crossing and radial approaches to every doorway.
 if math.hypot(x,z)<1.5+rr:return False
 if any(distance_segment(x,z,(0,0),(d['x'],d['z']))<.90+rr for d in r['doors']):return False
 if room in config['decks']:
  if distance_segment(x,z,(-2.2,-3.1),(-2.2,4.5))<.95+rr:return False
  for a in [45,135,225,315]:
   rad=config['decks'][room];cx=rad*math.cos(math.radians(a));cz=rad*math.sin(math.radians(a))
   if math.hypot(x-cx,z-cz)<rr+.38:return False
  # No tall reused equipment beneath the ring deck.
  if p['size'][1]>3.05 and abs(math.hypot(x,z)-config['decks'][room])<rr+1:return False
 for q in old['placements']+config['placements']:
  if q['room']!=room:continue
  qx,qz=q['position'][0],q['position'][2];qr=radius(q)
  if math.hypot(x-qx,z-qz)<rr+qr+.65:return False
  angle=math.radians(q['yaw']);gx=qx+math.sin(angle)*(q['size'][2]*.5+.6);gz=qz+math.cos(angle)*(q['size'][2]*.5+.6)
  if math.hypot(x-gx,z-gz)<rr+.65:return False
 return True
roles={
 'C01':['BC_PumpDriveCabinet','BN_ServiceManifold','BM_WaterFilterSkid','BN_MotorSpares','BC_ToolTrolley'],
 'C03':['BN_MotorSpares','BC_ToolTrolley'],
 'C04':['BN_ServiceManifold','BN_MotorSpares','BC_ToolTrolley'],
 'W01':['BM_PowerTransformer','BC_PumpDriveCabinet','BN_ServiceManifold','BN_MotorSpares'],
 'W02':['BN_ServiceManifold','BN_MotorSpares','BC_ToolTrolley'],
 'W03':['BM_MechanicalSparesRack','BC_MaintenanceBench','BN_MotorSpares','BC_ToolTrolley'],
 'E01':['BM_WaterFilterSkid','BN_ServiceManifold','BN_MotorSpares','BC_ToolTrolley'],
 'E02':['BM_AirFilterSkid','BN_ServiceManifold','BN_MotorSpares','BC_ToolTrolley'],
 'E03':['BM_SealedProcessTank','BM_WaterFilterSkid','BN_ServiceManifold','BN_MotorSpares'],
 'N01':['BM_VentilationFan','BM_AirFilterSkid','BN_ServiceManifold','BN_MotorSpares'],
 'S01':['BC_MaintenanceBench','BM_MechanicalSparesRack','BN_ServiceManifold','BN_MotorSpares']}
rng=random.Random(11010)
for room,models in roles.items():
 for i in range(12 if rooms[room]['r']>=8 else 4):
  model=models[i%len(models)]
  if model not in templates:continue
  candidates=[]
  for _ in range(1800):
   ang=rng.random()*math.tau;rr=rng.uniform(2.4,rooms[room]['r']-2);x=round(math.cos(ang)*rr,2);z=round(math.sin(ang)*rr,2)
   if okay(room,templates[model],x,z):candidates.append((x,z))
  if candidates:
   x,z=min(candidates,key=lambda p:math.hypot(*p));yaw=round(math.degrees(math.atan2(-x,-z))/15)*15
   add(room,model,x,z,yaw)
(H/'layout.json').write_text(json.dumps(config,ensure_ascii=False,indent=2),encoding='utf8')
print('PLACEMENTS',len(config['placements']),{r:sum(p['room']==r for p in config['placements']) for r in roles})
