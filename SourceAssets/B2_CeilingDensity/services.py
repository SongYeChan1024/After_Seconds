"""Beveled, open-grating partial decks and connected services, not game code."""
import sys,json,math,ast,os
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(R/'SourceAssets/B2_FullFloor'))
from common import *
H=Path(__file__).resolve().parent;R=H.parents[1]
os.environ['BO_PHASE']='services'
H=Path(__file__).resolve().parent;b.H=H;b.manifest=json.loads((H/'models.json').read_text()) if (H/'models.json').exists() else {}
C=json.loads((H/'plan.json').read_text(encoding='utf8'))
tree=ast.parse((R/'SourceAssets/B2_DetailMezzanine/build.py').read_text(encoding='utf8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='bulkbox'],type_ignores=[]),'bulkbox','exec'))
def save(n,lod=True):
 b.OUT=b.A/'Environment/B2';b.raw_export('CD_'+n);b.manifest['CD_'+n]['category']='Environment'
 if lod:
  ob=bpy.context.object;m=ob.modifiers.new('DistanceSimplification','DECIMATE');m.ratio=.38;m.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=m.name);ob.name='CD_'+n+'_Far'
  bpy.ops.export_scene.fbx(filepath=str(b.OUT/(ob.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE')
  b.manifest[ob.name]={'triangles':len(ob.data.polygons),'category':'Environment','distance_only':True}
 (H/'models.json').write_text(json.dumps(b.manifest,indent=2),encoding='utf8')
def prism(vs,fs,a,c,width,thick=.06):
 a=Vector(a);c=Vector(c);di=c-a;di.y=0;di.normalize();rr=Vector((di.z,0,-di.x));k=len(vs)
 for p in [a,c]:
  for dy in [0,-thick]:
   for sg in [-1,1]:vs.append(tuple(p+rr*sg*width/2+Vector((0,dy,0))))
 fs.extend([tuple(k+j for j in f) for f in [(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3),(0,1,3,2),(4,6,7,5)]])
def linebox(n,a,c,width,height,mat='Steel',bev=.003):
 vs=[];fs=[];prism(vs,fs,a,c,width,height);return mesh(n,vs,fs,mat,bev)
def rail(a,c,cv,cf):
 a=Vector(a);c=Vector(c);length=(c-a).length
 for h,rr in [(.98,.026),(.49,.018)]:cyl('SafetyRail',tuple(a+Vector((0,h,0))),tuple(c+Vector((0,h,0))),rr,'Steel',12)
 linebox('ToeBoard',a+Vector((0,.14,0)),c+Vector((0,.14,0)),.028,.14)
 prism(cv,cf,a+Vector((0,1.02,0)),c+Vector((0,1.02,0)),.06,1.02)
 for i in range(math.ceil(length/1.35)+1):
  q=a.lerp(c,i/max(1,math.ceil(length/1.35)));cyl('RailingPost',tuple(q),tuple(q+Vector((0,1.01,0))),.026,'Steel',10)
  box('BoltedShoe',q.x,q.y+.016,q.z,.14,.032,.14,'Steel',.003)
  for dx in [-.045,.045]:
   for dz in [-.045,.045]:cyl('ShoeBolt',(q.x+dx,q.y+.035,q.z+dz),(q.x+dx,q.y+.047,q.z+dz),.011,'Steel',6)
def column(x,z,cv,cf):
 box('ColumnWeb',x,1.72,z,.065,3.44,.23,'Steel',.004)
 for dz in [-.14,.14]:box('ColumnFlange',x,1.72,z+dz,.25,3.44,.045,'Steel',.004)
 box('AnchorPlate',x,.045,z,.38,.09,.43,'Steel',.007)
 for dx in [-.13,.13]:
  for dz in [-.16,.16]:cyl('AnchorBolt',(x+dx,.09,z+dz),(x+dx,.14,z+dz),.02,'Steel',6)
 bulkbox(cv,cf,x,1.72,z,.26,3.44,.33)
for room,de in C['decks'].items():
 if os.environ.get('BO_PHASE')=='services':continue
 if os.environ.get('BO_SKIP')==room:continue
 reset();cv=[];cf=[];gv=[];gf=[]
 for aa,bb,axis in de['bars']:
  prism(gv,gf,(aa[0],3.6,aa[1]),(bb[0],3.6,bb[1]),.009 if axis==0 else .012,.045 if axis==0 else .020)
 ob=mesh('OpenBearingGrating',gv,gf,'Steel',.0008)
 for m in ob.modifiers:
  if m.type=='BEVEL':m.segments=1
 for tri in de['triangles']:
  k=len(cv);cv.extend([(x,y,z) for y in [3.60,3.54] for x,z in tri]);cf.extend([tuple(k+j for j in f) for f in [(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)]])
 for aa,bb in de['rails']:
  a=(aa[0],3.6,aa[1]);c=(bb[0],3.6,bb[1]);rail(a,c,cv,cf);linebox('EdgeChannel',(aa[0],3.51,aa[1]),(bb[0],3.51,bb[1]),.07,.16)
 # Longitudinal steel members under the open grid.
 for path,w in de['paths']:
  for aa,bb in zip(path,path[1:]):
   linebox('DeckSpine',(aa[0],3.49,aa[1]),(bb[0],3.49,bb[1]),.12,.22)
 # Internal stairs and portal height transitions have continuous walking slopes.
 for st in de['stairs']+de['links']:
  for aa,bb in zip(st,st[1:]):
   a=Vector(aa);c=Vector(bb);di=c-a;flat=Vector((di.x,0,di.z));ln=flat.length;direction=flat.normalized();right=Vector((direction.z,0,-direction.x));width=1.55
   prism(cv,cf,a,c,width)
   steps=max(1,math.ceil(abs(di.y)/.18));sv=[];sf=[]
   for i in range(steps):
    mid=a.lerp(c,(i+.5)/steps);mid.y=a.y+di.y*(i+1)/steps
    prism(sv,sf,mid-direction*ln/steps/2,mid+direction*ln/steps/2,width,.055)
    q=mid-direction*(ln/steps/2-.025);linebox('AntiSlipNosing',q-right*.73+Vector((0,.006,0)),q+right*.73+Vector((0,.006,0)),.045,.009,'Hazard',.001)
   mesh('BoltedStairTreads',sv,sf,'Steel',.003)
   for sign in ([-1,1] if abs(di.y)>.1 else []):
    aa=a+right*(width/2+.035)*sign;bb=c+right*(width/2+.035)*sign;rail(aa,bb,cv,cf);linebox('StairStringer',aa-Vector((0,.09,0)),bb-Vector((0,.09,0)),.09,.24)
 # Supports placed on deck outer edges, away from centre aisle and door mouths.
 supports={'C02':[(-6.15,4.8),(-2.3,8.12),(2.7,7.86),(7.8,2.6)],'E02':[(-4.0,1.3),(-4,-2.2)],'W02':[(3.42,-2.3),(3.42,1.2),(-.1,4.96)],'E01':[(-3.96,-3.34),(-.968,-5.016),(2.2,-4.576)]}[room]
 for x,z in supports:column(x,z,cv,cf)
 save(room+'_OperationsDeck');reset();mesh('WalkingAndGuardCollision',cv,cf,'Dark',0);save(room+'_OperationsDeck_Collision',False)
 print('DECK',room,flush=True)

# Manufacturable distribution: no decorative disconnected piping across a walkway.
for room,services in C['services'].items():
 if os.environ.get('CD_SERVICE_ROOM') and room!=os.environ['CD_SERVICE_ROOM']:continue
 if os.environ.get('BO_PHASE')=='decks':continue
 reset();kind=services['kind'];props=[p for p in C['placements'] if p['room']==room]
 def pipe(pts,r=.08,mat='Pipe'):
  tube('ProcessPipe',pts,r,mat)
  for p in [pts[0],pts[-1]]:flange(*p,r=r,axis='y')
 def tray(a,c):
  # Open ladder cable tray, with edge folds and short transverse rungs.
  a=Vector(a);c=Vector(c);di=(c-a).normalized();rr=Vector((di.z,0,-di.x));ln=(c-a).length
  for sign in [-1,1]:linebox('CableTrayFold',a+rr*.25*sign,c+rr*.25*sign,.025,.14,'Steel',.002)
  for i in range(math.ceil(ln/.28)+1):
   q=a.lerp(c,i/max(1,math.ceil(ln/.28)));linebox('CableTrayRung',q-rr*.25,q+rr*.25,.035,.035,'Steel',.002)
  for side in [-.13,0,.13]:tube('HeavyCable',[tuple(a+rr*side),tuple(c+rr*side)],.024,'Rubber')
 if kind in ['cooling','separation','water','waste','fuel']:
  # Connection headers stay with their process equipment; no low cross-room pipes.
  plant=[p for p in props if p['model'] in ['BM_CoolingPump','BM_SealedProcessTank','BM_WaterFilterSkid','BC_PlateHeatExchanger','BM_Centrifuge','B2_EmergencyGenerator']]
  for p in plant:
   x,y,z=p['position'];w,h,dep=p['size'];a=math.radians(p['yaw']);side=Vector((math.cos(a),0,-math.sin(a)));back=Vector((-math.sin(a),0,-math.cos(a)))
   port=Vector((x,max(.42,min(1.6,h*.65)),z))+back*(dep*.45)
   room_radius=next(q['r'] for q in C['rooms'] if q['id']==room);roof_margin=math.sqrt(max(.1,room_radius**2-(port.x+back.x*.22)**2-(port.z+back.z*.22)**2))-.48;top=port+Vector((0,min(5.6,roof_margin)-port.y,0));xx={'C02':2.5,'C01':3,'W02':3,'E01':2.5,'E03':2}[room]*(1 if x>=0 else -1)
   feed=(xx,5.6,max(-4,min(4.5,top.z)))
   pipe([tuple(port),tuple(Vector((x,port.y+.22,z))+back*(dep*.24)),tuple(Vector((x,top.y,z))+back*(dep*.24)),feed],.14 if p.get('relative_scale',1)>=1.5 else .085,'PipeRed' if kind=='fuel' else 'Pipe')
   old=set(bpy.context.scene.objects);box('EquipmentPlinth',0,.045,0,w+.15,.09,dep+.12,'Dark',.012);transform(set(bpy.context.scene.objects)-old,x,0,z,p['yaw'])
  # Two longitudinal ceiling headers feed two trains; curves and flanges remain visible.
  for sign in [-1,1]:
   x={'C02':2.5,'C01':3,'W02':3,'E01':2.5,'E03':2}[room]*sign
   pipe([(x,5.6,-4),(x,5.6,4.5)],.15,'PipeRed' if sign==1 else 'Pipe')
   for z in [-3,0,3]:
    box('PipeSaddle',x,5.83,z,.40,.08,.12,'Steel',.004)
    cyl('HangerRod',(x,5.85,z),(x,6.5,z),.018,'Steel',10)
  if room=='C02':
   # Valves adjacent to the rear deck, operated from 3.6m level.
   for x in [-1.7,.4,2.5]:
    pipe([(x,5.6,4.5),(x,5.6,6.25),(x,4.35,6.25)],.1);valve(x,4.35,6.25);gauge(x+.26,4.75,6.25)
  if room=='E03':
   for x in [-2,.5,3]:
    box('WetCatchTray',x,.025,-2.6,2.2,.05,2.6,'Steel',.008)
    for zz in [-3.82,-1.38]:box('ContainmentLip',x,.07,zz,2.2,.10,.07,'Dark',.005)
 elif kind=='air':
  # Flanged rectangular ducts aligned to the filter/fan rows, with visible access lids.
  xs=[2] if room=='E02' else [-3,3]
  for x in xs:
   for z in [-3,-1,1,3,5]:
    box('VentDuct',x,5.4,z,1.25,1.05,1.94,'Pipe',.018)
    for zz in [z-.98,z+.98]:
     box('DuctFlangeTop',x,5.95,zz,1.40,.07,.08,'Steel',.004);box('DuctFlangeBottom',x,4.85,zz,1.40,.07,.08,'Steel',.004)
     for xx in [x-.67,x+.67]:box('DuctFlangeSide',xx,5.4,zz,.07,1.1,.08,'Steel',.004)
    box('DamperInspectionLid',x-.645,5.4,z,.045,.55,.72,'Dark',.012)
    for dz in [-.23,.23]:box('AccessLatch',x-.68,5.4,z+dz,.045,.18,.035,'Steel',.003)
  for p in props:
   if p['model'] not in ['BM_AirFilterSkid','BM_VentilationFan','BM_HVACUnit']:continue
   x,y,z=p['position'];bottom=p['size'][1]-.02;box('EquipmentDuctRiser',x,(4.90+bottom)/2,z,.75,4.90-bottom,.65,'Pipe',.012)
   if room=='N01' and abs(x)<.1:box('CentreFilterReturnDuct',1.5,5.4,z,3,1.05,.75,'Pipe',.012)
   if room=='N01' and abs(x)>4:
    target_x=3 if x>0 else -3;box('HVACConnectionDuct',(x+target_x)/2,5.4,z,abs(x-target_x),1.05,.75,'Pipe',.012)
   if room=='E02' and x>3:box('FanBranchDuct',(x+2)/2,5.4,z,x-2,1.05,.65,'Pipe',.012)
 elif kind in ['power','control','diagnostics']:
  points={'C03':[(-3.2,3.8,-2),(-3.2,3.8,2.8),(2.4,3.8,2.8)],'C04':[(-3,3.4,-4.6),(3.6,3.4,-4.6)],'W01':[(-3,4.3,-4.9),(3,4.3,-4.9),(3,4.3,4.6)],'S01':[(-3,4.2,-6),(3,4.2,-6)]}[room]
  for a,c in zip(points,points[1:]):tray(a,c)
  # Cable drops terminate at the rear of cabinets, away from operating faces.
  for p in props:
   if p['model'] not in ['BC_PumpDriveCabinet','BS_ServerRack_1','BS_ServerRack_2']:continue
   x,y,z=p['position'];a=math.radians(p['yaw']);bx=x-math.sin(a)*.40;bz=z-math.cos(a)*.40
   tube('RearCableDrop',[(bx,1.8,bz),(bx,3.3,bz),(bx+.12,3.5,bz)],.035,'Rubber')
 else:
  # Parts bay wheel stops, recessed low footprint cart pockets, no fake wall barriers.
  for p in props:
   if p['group'] not in ['Receiving','Dispatch','Repair']:continue
   x,y,z=p['position'];w=p['size'][0]
   for side in [-1,1]:box('BayCornerPlate',x+side*(w/2+.12),.008,z-.55,.16,.012,.38,'Hazard',.002)
 # Continue the existing seven tunnel header ends into the new process header.
 if room in C['decks']:
  network=json.loads((R/'SourceAssets/B2_DomeNetwork/layout.json').read_text(encoding='utf8'))
  rr=next(r for r in C['rooms'] if r['id']==room);origin=Vector((rr['x'],0,-rr['v']))
  for t in network['tunnels']:
   if room not in network['ends'][t['id']]:continue
   ps=[Vector((p[0],0,-p[1])) for p in t['path']];start=t['a']==room;di=(ps[1]-ps[0]).normalized() if start else (ps[-1]-ps[-2]).normalized();p=ps[0] if start else ps[-1];inside=di*(-1 if start else 1);right=Vector((di.z,0,-di.x))
   for side,y,rad,mat in [(-1.30,2.95,.15,'Pipe'),(1.30,2.90,.12,'PipeRed')]:
    a=p+right*side+inside*2+Vector((0,y+2.5,0))-origin
    x=(2 if room=='E02' else 3 if room=='W02' else 2.5)*(1 if a.x>=0 else -1)
    target=(x,5.6,max(-4,min(4.5,a.z)))
    lift=min(6.0,math.sqrt(max(.1,rr['r']**2-a.x*a.x-a.z*a.z))-.36);tube('TunnelToProcessHeader',[tuple(a),(a.x,lift,a.z),(x,lift,target[2]),target],rad,mat)
 if not any(o.type=='MESH' for o in bpy.context.scene.objects):continue
 save(room+'_OperationsServices');print('SERVICES',room,flush=True)
