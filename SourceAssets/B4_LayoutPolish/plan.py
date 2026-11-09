"""Plan against actual native mesh bounds, old workspace and door routes."""
from pathlib import Path
import json,math,copy
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-09_B4_LayoutPolish'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
base=read(R/'SourceAssets/B4_ExperimentOperations/layout.json'); plan=copy.deepcopy(base)
cat={i['model']:i for i in read(H/'catalog.json')}; geom=read(H/'geometry.json');rooms={r['id']:r for r in base['rooms']}
routes=read(next(R.glob('Docs/*/2026-11-08_B4_ExperimentOperations/routes.json')))
changes=dict(rooms=base['rooms'],disable=[],moves=[],add=[])
def rot(x,z,yaw):
 a=math.radians(yaw);return x*math.cos(a)+z*math.sin(a),-x*math.sin(a)+z*math.cos(a)
def rect(pos,yaw,size,center=(0,0,0),pad=0):
 return Polygon([(pos[0]+rot(center[0]+sx*(size[0]/2+pad),center[2]+sz*(size[2]/2+pad),yaw)[0],pos[2]+rot(center[0]+sx*(size[0]/2+pad),center[2]+sz*(size[2]/2+pad),yaw)[1]) for sx,sz in [(-1,-1),(1,-1),(1,1),(-1,1)]])
objs={}; shape={}; acces={}; oldpaths={}
for code,r in rooms.items():
 objs[code]=[]
 for g in geom:
  if abs(g['p'][1]+66)>.08:continue
  x=g['p'][0]-r['x'];z=g['p'][2]+r['v']
  if math.hypot(x,z)>r['r']-.05:continue
  p=dict(g,position=[x,0,z],yaw=g['e'][1],model=Path(g['asset']).stem,room=code)
  objs[code].append(p);shape[g['id']]=rect(p['position'],p['yaw'],p['size'],p['center'])
 acces[code]=[(w['name'],Polygon(w['polygon'])) for w in base['workspaces'] if w['room']==code and 'polygon' in w]
 oldpaths[code]=[]
 for path in routes:
  if path['id'].startswith(code+'_door_0_') and int(path['id'].split('_')[-1])<len(r['doors']):
   pts=[(p[0]-r['x'],p[2]+r['v']) for p in path['points']];oldpaths[code].append(LineString(pts))
reserved={k:unary_union([p.buffer(.70,cap_style=2,join_style=2) for p in ps]) for k,ps in oldpaths.items()}
newobs={k:[] for k in rooms}
def free(poly,code,ignore=None,access=True,route=True):
 r=rooms[code]
 if not Point(0,0).buffer(r['r']-.18,quad_segs=80).covers(poly):return False
 if route and reserved[code].intersects(poly):return False
 for p in objs[code]:
  if p['id']==ignore or p['id'] in changes['disable']:continue
  if poly.intersects(shape[p['id']].buffer(.10)):return False
 if any(poly.intersects(p.buffer(.10)) for p in newobs[code]):return False
 if access and any(name!=(next((p['name'] for p in objs[code] if p['id']==ignore),'')) and poly.intersects(a) for name,a in acces[code]):return False
 return True
def place(model,code,pos,yaw,kind,collider=True,**kw):
 c=cat[model];p=dict(c,room=code,position=pos,yaw=yaw,collider=collider,name=f'B4_{code}_{kind}_{len(changes["add"])+1:03}',**kw);changes['add'].append(p)
 if collider:newobs[code].append(rect(pos,yaw,c['size'],c['center']))
 return p
def setmove(p,pos,yaw):
 r=rooms[p['room']];oldpos=p['position'];oldyaw=p['yaw'];changes['moves'].append(dict(id=p['id'],name=p['name'],worldPosition=[r['x']+pos[0],-66,-r['v']+pos[2]],yaw=yaw,before=oldpos,beforeYaw=oldyaw))
 shape[p['id']]=rect(pos,yaw,p['size'],p['center']);p['position']=pos;p['yaw']=yaw
 for q in plan['newPlacements']+plan['placements']:
  if q['name']==p['name']:q['position']=pos;q['yaw']=yaw
 for w in plan['workspaces']:
  if not w['name'].startswith(p['name']):continue
  xx,zz=rot(w['point'][0]-oldpos[0],w['point'][2]-oldpos[2],-oldyaw);xx,zz=rot(xx,zz,yaw);w['point']=[pos[0]+xx,0,pos[2]+zz]
  if 'polygon' in w:
   pts=[]
   for x,z in w['polygon']:
    xx,zz=rot(x-oldpos[0],z-oldpos[2],-oldyaw);xx,zz=rot(xx,zz,yaw);pts.append([pos[0]+xx,pos[2]+zz])
   w['polygon']=pts
def doorclear(r,a,width):
 return all(abs((a-d['angle']+180)%360-180)>math.degrees(math.asin(min(.95,(2.35+width/2)/r['r']))) for d in r['doors'])
def wallpos(r,a,y,margin):
 rad=math.sqrt(r['r']**2-(0 if r['kind']=='core' else y*y))-margin;ang=math.radians(a);return [rad*math.cos(ang),0,rad*math.sin(ang)],(270-a)%360
# Replace all 12 standalone safety panels by genuine wall-mounted assemblies.
for code,items in objs.items():
 r=rooms[code]
 for p in items:
  if p['model']!='BX_SafetyEquipment':continue
  changes['disable'].append(p['id']);model='BP_WallSafety_R'+str(r['r']);c=cat[model];cands=[]
  for a in range(0,360,2):
   if not doorclear(r,a,1.4):continue
   pos,yaw=wallpos(r,a,2.13,.20);poly=rect(pos,yaw,[1.34,2.1,.44],[0,1.19,.21])
   if not free(poly,code,access=False,route=False):continue
   # Clear operating approach directly in front of the door.
   fx,fz=rot(0,1.15,yaw);ap=[pos[0]+fx,0,pos[2]+fz]
   if not free(rect(ap,yaw,[1.0,1,.65]),code,access=False,route=False):continue
   dist=min(math.hypot(ap[0]-d['x'],ap[2]-d['z']) for d in r['doors'])
   cands.append((dist+.12*math.dist(pos,p['position']),pos,yaw,ap))
  if not cands:
   scores=[];swaps=[]
   for a in range(0,360,4):
    if not doorclear(r,a,1.4):continue
    pos,yaw=wallpos(r,a,2.13,.20);fx,fz=rot(0,1.15,yaw);ap=[pos[0]+fx,0,pos[2]+fz]
    poly=rect(pos,yaw,[1.34,2.1,.44],[0,1.19,.21]).union(rect(ap,yaw,[1,1,.65]))
    hits=[q for q in items if q['id'] not in changes['disable'] and poly.intersects(shape[q['id']].buffer(.1))]
    scores.append((len(hits),a,[q['name'] for q in hits]))
    if len(hits)!=1:continue
    q=hits[0]
    if q['lights'] or q['size'][0]>1.8 or q['size'][2]>1.1 or q['model'].endswith('Chair'):continue
    for dyaw in [p['yaw'],0,90,180,270]:
     target=p['position']; qp=rect(target,dyaw,q['size'],q['center'])
     if poly.intersects(qp.buffer(.1)) or not free(qp,code,ignore=q['id'],access=False,route=False):continue
     swaps.append((math.dist(target,q['position']),a,q,target,dyaw,pos,yaw,ap))
   if not swaps:
    print('WALL_BLOCKERS',code,sorted(scores)[:8]);raise RuntimeError('No safe wall position '+code)
   _,_,q,target,dyaw,pos,yaw,ap=sorted(swaps,key=lambda t:t[0])[0]
   setmove(q,target,dyaw);cands.append((0,pos,yaw,ap))
  _,pos,yaw,ap=min(cands);q=place(model,code,pos,yaw,'WallSafety');q['size']=[1.34,1.82,.44];q['center']=[0,1.19,.21]
  plan['workspaces']=[w for w in plan['workspaces'] if w['name']!=p['name']];plan['workspaces'].append(dict(name=q['name'],room=code,point=ap))
# Bring loose carts into coherent equipment bays instead of a loose ring.
cart_models={'BX_SmallSupplyCart','BX_MobileAcquisitionCart','BX_EmergencyCart','BX_TargetRecoveryTrolley'}
station_models={'BX_ProtocolTable','BX_DualReviewStation','BX_OperatorIsland','BX_InstrumentServiceBay','BX_ElectrodePrepBench','BX_SubjectCheckIn','BF_AnalysisBench','BF_SensorWorkbench','BF_ResearchDesk','BO_SensorPreparationBench'}
for code,items in objs.items():
 if rooms[code]['kind']=='core':continue
 stations=[p for p in items if p['model'] in station_models]
 for p in items:
  if p['model'] not in cart_models:continue
  candidates=[]
  for s in stations:
   for side in [-1,1]:
    for dz in [-.20,.15,.45]:
     xx,zz=rot(side*(s['size'][0]/2+p['size'][0]/2+.30),dz,s['yaw']);pos=[s['position'][0]+xx,0,s['position'][2]+zz];poly=rect(pos,s['yaw'],p['size'],p['center'])
     if not free(poly,code,ignore=p['id']):continue
     fx,fz=rot(0,p['size'][2]/2+.48,s['yaw']);ap=[pos[0]+fx,0,pos[2]+fz]
     if not free(rect(ap,s['yaw'],[.65,1,.50]),code,ignore=p['id'],access=False,route=False):continue
     candidates.append((math.dist(pos,p['position']),pos,s['yaw']))
  if candidates:
   _,pos,yaw=min(candidates);setmove(p,pos,yaw)
# Move tall loose service cabinets back toward a proper wall equipment row.
for code,items in objs.items():
 r=rooms[code]
 for p in items:
  if p['model'] not in {'BX_UtilityServiceSpine','BX_CleanReturnCabinet'} or math.hypot(p['position'][0],p['position'][2])>r['r']*.80:continue
  cands=[]
  for a in range(0,360,3):
   if not doorclear(r,a,p['size'][0]):continue
   pos,yaw=wallpos(r,a,p['size'][1],p['size'][2]/2+.30)
   if free(rect(pos,yaw,p['size'],p['center']),code,ignore=p['id']):cands.append((math.dist(pos,p['position']),pos,yaw))
  if cands:_,pos,yaw=min(cands);setmove(p,pos,yaw)
# Small mobile apparatus and return storage supplement existing work groups.
for code,items in objs.items():
 r=rooms[code]
 if r['kind']=='core':continue
 for model in ['BP_ReturnRack','BP_InstrumentTrolley']:
  c=cat[model];candidates=[]
  for s in items:
   if s['model'] not in station_models|{'BX_ConsumableWall','BX_EquipmentCaseRack','BX_CalibrationRack'}:continue
   for side in [-1,1]:
    for z in [0,-.25,.25]:
     xx,zz=rot(side*(s['size'][0]/2+c['size'][0]/2+.28),z,s['yaw']);pos=[s['position'][0]+xx,0,s['position'][2]+zz];poly=rect(pos,s['yaw'],c['size'],c['center'])
     if not free(poly,code):continue
     if any(math.hypot(x,z)>math.sqrt(r['r']**2-c['size'][1]**2)-.08 for x,z in poly.exterior.coords):continue
     fx,fz=rot(0,c['size'][2]/2+.65,s['yaw']);ap=[pos[0]+fx,0,pos[2]+fz]
     if not free(rect(ap,s['yaw'],[.8,1,.6]),code,access=False,route=False):continue
     candidates.append((abs(math.hypot(pos[0],pos[2])-r['r']*.65),pos,s['yaw'],ap))
  if candidates:
   _,pos,yaw,ap=min(candidates);p=place(model,code,pos,yaw,model[3:]);plan['workspaces'].append(dict(name=p['name'],room=code,point=ap))
# A second layer of service installations follows empty wall sectors.
for code,r in rooms.items():
 if r['kind']=='core':continue
 n=0
 for a in range(15,360,30):
  if not doorclear(r,a,2.2):continue
  # Avoid ribs at 45-degree intervals; no work-face/door obstruction at 2.5m.
  if abs((a+22.5)%45-22.5)<5:a+=8
  pos,yaw=wallpos(r,a,3.30,.22)
  place('BP_WallServices_R'+str(r['r']),code,pos,yaw,'WallServices',False);n+=1
  if n>=4:break
# Purposeful, compact desktop detailing on proven empty front corner patches.
kitindex=0
for code,items in objs.items():
 for p in items:
  model=p['model']; y=None;z=.25;xs=[]
  if model in {'BF_AnalysisBench','BF_SensorWorkbench'}:y=.901;xs=[-p['size'][0]/2+.23];z=.24
  elif model=='BF_ResearchDesk':y=.915;xs=[p['size'][0]/2-.24];z=.18
  elif model in {'BX_ProtocolTable','BX_OperatorIsland'}:y=.944;xs=[p['size'][0]/2-.25];z=.18
  elif model=='BX_DualReviewStation':y=.944;xs=[p['size'][0]/2-.25];z=.20
  elif model=='BX_ObservationBooth':y=.94;xs=[1.29];z=-.46
  if y is None:continue
  for x in xs:
   model='BP_BenchKit_'+str(kitindex%3+1);kitindex+=1
   place(model,code,[x,y,z],0,'BenchDetail',False,parentId=p['id'])
(H/'changes.json').write_text(json.dumps(changes,indent=2),encoding='utf8')
(H/'layout.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8')
# Review-only plot. It does not create in-game arrows or route lines.
W=1800;im=Image.new('RGB',(W,1500),'#152029');d=ImageDraw.Draw(im)
for index,(code,r) in enumerate(rooms.items()):
 col=index%4;row=index//4;cx=col*450+225;cy=row*375+195;s=145/r['r']
 def xy(p):return cx+p[0]*s,cy-p[1]*s
 d.text((col*450+18,row*375+12),code+' / WALL + WORK BAYS',fill='#eeeeee')
 d.ellipse((cx-r['r']*s,cy-r['r']*s,cx+r['r']*s,cy+r['r']*s),outline='#91a4ad',width=2)
 for route in oldpaths[code]:d.line([xy(p) for p in route.coords],fill='#3a6871',width=max(1,int(1.4*s)))
 for p in objs[code]:
  if p['id'] in changes['disable']:continue
  d.polygon([xy(q) for q in shape[p['id']].exterior.coords],fill='#687480',outline='#adb8bf')
 for p in changes['add']:
  if p['room']!=code or not p['collider']:continue
  poly=rect(p['position'],p['yaw'],p['size'],p['center']);d.polygon([xy(q) for q in poly.exterior.coords],fill='#ca7252',outline='#ffc6a3')
im.save(O/'layout_review.png')
print(json.dumps({'moved':len(changes['moves']),'replaced':len(changes['disable']),'new':len(changes['add']),'by_room':{k:sum(p['room']==k for p in changes['add']) for k in rooms}},indent=2))
