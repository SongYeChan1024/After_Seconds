"""B2 manufactured service decks and functional process islands. 송예찬."""
import sys,json,math,ast,os
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(R/'SourceAssets/B2_FullFloor'))
from common import *
H=Path(__file__).resolve().parent;b.H=H;b.manifest=json.loads((H/'models.json').read_text()) if os.environ.get('BN_ONLY') and (H/'models.json').exists() else {}
C=json.loads((H/'layout.json').read_text(encoding='utf8'));rooms={r['id']:r for r in C['rooms']}
source=ast.parse((R/'SourceAssets/B2_DetailMezzanine/build.py').read_text(encoding='utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='bulkbox'],type_ignores=[]),'<bulkbox>','exec'))
routes=[];only=os.environ.get('BN_ONLY','')
def save(name,category='Environment',lod=True):
 b.OUT=b.A/category/'B2';b.raw_export('BN_'+name);b.manifest['BN_'+name]['category']=category
 if lod:
  ob=bpy.context.object;m=ob.modifiers.new('DistanceSimplification','DECIMATE');m.ratio=.35;m.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=m.name);ob.name='BN_'+name+'_LOD1'
  bpy.ops.export_scene.fbx(filepath=str(b.OUT/(ob.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE')
  b.manifest[ob.name]={'triangles':len(ob.data.polygons),'category':category,'asset':str(b.OUT/(ob.name+'.fbx')),'distance_only':True}
 (H/'models.json').write_text(json.dumps(b.manifest,indent=2),encoding='utf8')
def begin():
 global CV,CF
 reset();CV=[];CF=[]
def collisionbox(x,y,z,w,h,d):bulkbox(CV,CF,x,y,z,w,h,d)
def end(name):
 save(name);reset();mesh('ContinuousWalkingAndGuardCollision',CV,CF,'Dark',0);save(name+'_Collision',lod=False)
def prism(vs,fs,a,c,width,thick=.065):
 a=Vector(a);c=Vector(c);di=c-a;di.y=0;di.normalize();rr=Vector((di.z,0,-di.x));k=len(vs)
 for p in [a,c]:
  for dy in [0,-thick]:
   for sign in [-1,1]:vs.append(tuple(p+rr*sign*width/2+Vector((0,dy,0))))
 fs.extend([tuple(k+j for j in f) for f in [(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3),(0,1,3,2),(4,6,7,5)]])
def guard_segment(a,c,side,width):
 a=Vector(a);c=Vector(c);di=c-a;di.y=0;di.normalize();rr=Vector((di.z,0,-di.x));aa=a+rr*side*(width/2+.035);cc=c+rr*side*(width/2+.035)
 for h,r in [(.95,.025),(.47,.017)]:cyl('SteelHandrail',tuple(aa+Vector((0,h,0))),tuple(cc+Vector((0,h,0))),r,'Steel',10)
 # Thin full guard collider provides an intentional fall boundary.
 k=len(CV)
 for p in [aa,cc]:
  for y in [0,.97]:
   for sg in [-1,1]:CV.append(tuple(p+rr*sg*.017+Vector((0,y,0))))
 CF.extend([tuple(k+j for j in f) for f in [(0,4,6,2),(1,3,7,5),(2,6,7,3),(0,1,5,4),(0,2,3,1),(4,5,7,6)]])
def walkway(name,pts,width=1.5,stairs=False,gap=None):
 ps=[Vector(p) for p in pts];gv=[];gf=[];sv=[];sf=[];hv=[];hf=[]
 for idx,(a,c) in enumerate(zip(ps,ps[1:])):
  di=c-a;flat=Vector((di.x,0,di.z));L=flat.length;direction=flat.normalized();rr=Vector((direction.z,0,-direction.x))
  prism(CV,CF,a,c,width+.02)
  steps=max(1,math.ceil(abs(di.y)/.18)) if stairs and abs(di.y)>.03 else max(1,math.ceil(L/.6))
  for i in range(steps):
   p=a.lerp(c,(i+.5)/steps);length=L/steps
   if stairs and abs(di.y)>.03:
    y=a.y+di.y*(i+1)/steps
    origin=Vector((p.x,y,p.z));prism(sv,sf,origin-direction*length*.5,origin+direction*length*.5,width,.06)
    # Perforated non-slip nosing with small hazard edge.
    q=origin-direction*(length*.5-.018)
    for xx in [-width*.36,0,width*.36]:
     p2=q+rr*xx;old=set(bpy.context.scene.objects);box('StairNosing',0,0,0,width*.25,.012,.035,'Hazard',.002);transform(set(bpy.context.scene.objects)-old,p2.x,p2.y+.004,p2.z,math.degrees(math.atan2(direction.x,direction.z)))
   else:
    for j in range(max(2,int(width/.075))):
     x=-width*.5+.035+j*.075;aa=a.lerp(c,i/steps)+rr*x;cc=a.lerp(c,(i+1)/steps)+rr*x
     prism(gv,gf,aa,cc,.009,.045)
    for dd in [.08+j*.18 for j in range(max(1,int(length/.18)))]:
     q=a+direction*(i*length+dd);q.y=p.y-.018;prism(gv,gf,q-rr*(width*.5-.02),q+rr*(width*.5-.02),.009,.015)
  # Outer channel stringers, bolted railing shoes.
  for side in [-1,1]:
   aa=a+rr*side*(width/2+.025);cc=c+rr*side*(width/2+.025)
   prism(sv,sf,aa-Vector((0,.065,0)),cc-Vector((0,.065,0)),.075,.16)
   if gap is None or not gap((a+c)*.5,side):
    guard_segment(a,c,side,width)
    if idx%2==0 or len(ps)<4:
     cyl('GuardPost',tuple(aa),tuple(aa+Vector((0,.95,0))),.022,'Steel',10)
     box('RailingShoe',aa.x,aa.y+.012,aa.z,.11,.024,.11,'Steel',.003)
  if idx%2==0:
   p=(a+c)*.5;prism(sv,sf,p-rr*(width*.5),p+rr*(width*.5),.075,.15)
 if gv:
  ob=mesh(name+'_OpenSteelGrating',gv,gf,'Steel',.0006)
  for m in ob.modifiers:
   if m.type=='BEVEL':m.segments=1
 mesh(name+'_StringersAndTreads',sv,sf,'Steel',.003)
 routes.append({'name':name,'points':[[p.x,p.y,p.z] for p in ps],'width':width})
def columns(rad):
 for angle in [45,135,225,315]:
  a=math.radians(angle);x=rad*math.cos(a);z=rad*math.sin(a)
  box('ColumnWeb',x,1.75,z,.07,3.50,.23,'Steel',.006)
  for dz in [-.14,.14]:box('ColumnFlange',x,1.75,z+dz,.24,3.50,.05,'Steel',.006)
  for y in [.045,3.42]:
   box('ColumnBasePlate',x,y,z,.39,.09,.43,'Steel',.01)
   for dx in [-.14,.14]:
    for dz in [-.16,.16]:cyl('AnchorBolt',(x+dx,y+.04,z+dz),(x+dx,y+.08,z+dz),.019,'Steel',6)
  collisionbox(x,1.75,z,.26,3.50,.33)
def pts_at(ps,d):return at(ps,d)[0]
for t in C['tunnels']:
 code=t['id'];ps=[Vector((p[0],0,-p[1])) for p in t['path']];L=sum((c-a).length for a,c in zip(ps,ps[1:]));a=t['a'] in C['ends'][code];bb=t['b'] in C['ends'][code]
 t['length']=L;t['connectedA']=a;t['connectedB']=bb
 start=0 if a else 1.6;finish=L if bb else L-1.6
 def height(d):return 2.42*max(0,min(1,1 if a else (d-1.6)/3.9,1 if bb else (L-1.6-d)/3.9))
 ds=sorted(set([start,finish]+([] if a else [5.5])+([] if bb else [L-5.5])+[start+(finish-start)*i/math.ceil((finish-start)/.6) for i in range(math.ceil((finish-start)/.6)+1)]))
 if only and only!=code:continue
 begin();walkway(code+'_ConnectedUpper',[(pts_at(ps,d)+Vector((0,height(d),0))) for d in ds],stairs=True)
 # Existing crossbeams are replaced together with the old route.
 for d in [start+.6+i*3 for i in range(math.ceil((finish-start)/3))]:
  if height(d)<2.4 or d>finish:continue
  p,di=at(ps,d);rr=Vector((di.z,0,-di.x));vs=[];fs=[];prism(vs,fs,p-rr*2.12+Vector((0,2.26,0)),p+rr*2.12+Vector((0,2.26,0)),.11,.15);mesh('WallSupportedBeam',vs,fs,'Steel',.004)
 end(code+'_UpperWalk');print('ROUTE',code,flush=True)
 # Selected ends retain the existing downfeed branch; a tee continues the upper header into the dome.
 begin()
 for is_start,connected in [(True,a),(False,bb)]:
  if not connected:continue
  ds2=[5.5*(i/18) if is_start else L-5.5+5.5*(i/18) for i in range(19)]
  for side,y,r,mat in [(-1.30,2.95,.15,'Steel'),(1.30,2.90,.12,'PipeRed')]:
   pp=[]
   for d in ds2:
    p,di=at(ps,d);pp.append(tuple(p+Vector((di.z,0,-di.x))*side+Vector((0,y,0))))
   tube('ContinuingProcessHeader',pp,r,mat)
   p,di=at(ps,0 if is_start else L);rr=Vector((di.z,0,-di.x));q=p+rr*side+Vector((0,y,0));inside=di*(-1 if is_start else 1)
   tube('DomeSupplyRiser',[tuple(q),tuple(q+inside*1.6),tuple(q+inside*2.0+Vector((0,2.5,0)))],r,mat)
 save(code+'_HeaderContinuation',lod=True)
for id,rad in C['decks'].items():
 if only and only!=id:continue
 r=rooms[id];doors=[d for d in r['doors'] if id in C['ends'].get(d['id'].split('-')[1],[])]
 openings=[math.atan2(d['z'],d['x']) for d in doors]
 topz=math.sqrt(rad*rad-2.2**2);inner=math.atan2(math.sqrt((rad-.8)**2-2.2**2),-2.2)
 def gap(p,side):
  # CCW path right is outward. Gaps only where an actual stair/bridge meets it.
  angle=math.atan2(p.z,p.x);angs=openings if side==1 else [inner]
  return any(abs(math.atan2(math.sin(angle-a),math.cos(angle-a)))*rad<(1.20 if side==-1 else 1.05) for a in angs)
 begin();walkway(id+'_RingDeck',[(rad*math.cos(math.tau*i/64),3.6,rad*math.sin(math.tau*i/64)) for i in range(65)],1.6,gap=gap)
 columns(rad)
 # Twenty steps form a usable route from the lower equipment floor.
 walkway(id+'_InternalStair',[(-2.2,0,-3.0),(-2.2,3.6,2.6)],1.5,True)
 walkway(id+'_StairLanding',[(-2.2,3.6,2.6),(-2.2,3.6,topz)],1.5,gap=lambda p,side: p.z>topz-.85)
 for d in doors:
  length=math.hypot(d['x'],d['z']);ux,uz=d['x']/length,d['z']/length
  walkway(id+'_'+d['id'].split('-')[1]+'_PortalStair',[(d['x'],2.42,d['z']),(ux*(rad+.80),3.6,uz*(rad+.80)),(ux*rad,3.6,uz*rad)],1.5,True,gap=lambda p,side:math.hypot(p.x,p.z)<rad+.81)
 end(id+'_ServiceDeck');print('DOME',id,flush=True)
if not only or only=='C02':
 begin();walkway('C02_T01_PortalStair',[(6.662,2.42,7.725),(5.95,3.6,5.6),(5.85,3.6,5.30)],1.5,True);end('C02_Connector')
 # Rebuild only the existing guard with an explicit opening in its rear rail.
 begin()
 for x in [-6.2,6.2]:
  box('ValveStationServicePad',x,3.603,3.3,2.18,.006,1.6,'Plate',.001)
  for z in [2.54,4.06]:box('PadEdge',x,3.610,z,2.17,.008,.035,'Hazard',.001)
  for sign in [-1,1]:rail((x+sign*.75,-1.9),(x+sign*1.1,-1.9))
 for a,c in [((-7.3,-1.9),(-7.3,5.6)),((7.3,-1.9),(7.3,5.6)),((-7.3,5.6),(4.95,5.6)),((6.85,5.6),(7.3,5.6)),((-5.1,-1.9),(-5.1,3.4)),((5.1,-1.9),(5.1,3.4)),((-5.1,3.4),(5.1,3.4))]:rail(a,c)
 save('C02_OpenedGuards',lod=True)
if not only or only=='props':
 # A real pressure reservoir: dished shoulders, bands, sight glass, flanged feed and manway.
 reset()
 cyl('PressureVessel',(0,.46,0),(0,4.22,0),.71,'Steel',64)
 for y in [.48,1.5,2.8,4.18]:
  cyl('WeldBand',(0,y-.024,0),(0,y+.024,0),.726,'Steel',64)
 for y in [.36,4.34]:
  for j in range(7):
   yy=y+(.10 if y>2 else -.10)*(j/6);radius=.71*math.sqrt(max(.1,1-(j/7)**2));cyl('DishedEnd',(0,yy-.025,0),(0,yy+.025,0),radius,'Steel',48)
 for x in [-.51,.51]:
  for z in [-.51,.51]:
   box('VesselLeg',x,.24,z,.12,.48,.12,'Steel',.014);box('FootPlate',x,.045,z,.26,.09,.26,'Steel',.008)
 tube('FeedRiser',[(0,4.45,0),(0,4.65,0),(.65,4.65,0)],.13,'Steel');flange(.5,4.65,0,.13,'x')
 tube('ReturnOutlet',[(0,.75,0),(0,.75,.82),(0,1.15,.82)],.10,'PipeRed');valve(0,.75,.65,.10)
 cyl('Manway',(0,2.35,.61),(0,2.35,.80),.23,'Steel',48);flange(0,2.35,.81,.18)
 for y in [1.25,3.75]:cyl('SightGlassTap',(-.5,y,.5),(-.5,y,.73),.035,'Steel',12)
 cyl('LevelTube',(-.5,1.25,.73),(-.5,3.75,.73),.027,'Dark',16)
 for j in range(20):box('LevelMark',-.43,1.35+j*.12,.75,.09,.008,.018,'Paper',.001)
 gauge(.35,1.6,.75);save('SurgeReservoir','Props')
 reset()
 box('AirPlenumCase',0,2.35,0,2.1,4.55,1.9,'Plate',.045)
 for y in [.13,1.55,3.0,4.55]:box('BoltedSectionFlange',0,y,0,2.23,.11,2.05,'Steel',.012)
 for x in [-.95,.95]:
  box('RolledEdgeFrame',x,2.35,.99,.09,4.45,.07,'Steel',.008)
  for y in [.25,1.5,3,4.4]:cyl('PanelBolt',(x,y,1.02),(x,y,1.06),.021,'Steel',6)
 for y in [.85,2.2,3.65]:
  box('AccessSeal',0,y,1.01,1.7,1.15,.055,'Rubber',.023);box('AccessPanel',0,y,1.047,1.62,1.08,.035,'Plate',.018)
  tube('PullHandle',[(.56,y-.14,1.08),(.56,y-.14,1.15),(.56,y+.14,1.15),(.56,y+.14,1.08)],.02,'Steel')
  for x in [-.68,.68]:
   for dy in [-.42,.42]:cyl('PanelLatch',(x,y+dy,1.07),(x,y+dy,1.1),.035,'Steel',6)
 for x in [-.7,.7]:
  cyl('UpperDuct',(x,4.5,0),(x,4.85,0),.34,'Steel',40);flange(x,4.7,0,.27,'y')
 gauge(-.45,2.35,1.10);save('AirPlenum','Props')
 reset()
 box('DayTank',0,1.25,0,2,1.8,1.35,'Plate',.12)
 for x in [-.83,.83]:
  box('TankSkid',x,.2,0,.18,.4,1.65,'Steel',.015)
  for z in [-.68,.68]:box('AnchorFoot',x,.055,z,.3,.11,.3,'Steel',.008)
 for z in [-.65,.65]:box('TankRim',0,1.35,z,2.10,.16,.065,'Steel',.01)
 cyl('InspectionHatch',(0,2.15,0),(0,2.28,0),.3,'Steel',40);flange(0,2.22,0,.24,'y')
 tube('FuelFeed',[(-.7,2.1,0),(-.7,2.8,0),(.4,2.8,0),(.4,2.8,.65)],.075,'Steel');flange(.4,2.8,.58,.075)
 gauge(.25,1.5,.73);valve(-.5,.75,.7,.075);save('DayTank','Props')
 reset()
 for x in [-.63,.63]:box('ManifoldUpright',x,1,0,.065,2,.065,'Steel',.006);box('AnchorFoot',x,.04,0,.25,.08,.45,'Steel',.008)
 for y in [.5,1.65]:
  tube('DistributionHeader',[(-.65,y,0),(.65,y,0)],.065,'Steel')
  flange(0,y,0,.065,'x')
 for x in [-.42,0,.42]:
  tube('MeteredBranch',[(x,.5,0),(x,.5,.18),(x,1.65,.18),(x,1.65,0)],.035,'PipeRed')
  gauge(x,1.35,.22);valve(x,.78,.18,.035)
 save('ServiceManifold','Props')
 reset()
 for x in [-.60,.60]:box('SkidRail',x,.06,0,.1,.12,.80,'Steel',.012)
 box('MotorBase',0,.16,0,1.4,.15,.72,'Steel',.012)
 cyl('SpareMotor',(-.48,.55,0),(.43,.55,0),.30,'Steel',40)
 for x in [-.40+i*.065 for i in range(12)]:cyl('CoolingFin',(x-.012,.55,0),(x+.012,.55,0),.34,'Steel',32)
 cyl('DriveShaft',(.42,.55,0),(.68,.55,0),.07,'Steel',24)
 box('TerminalBox',0,.86,0,.35,.18,.30,'Dark',.018)
 for z in [-.29,.29]:tube('LiftingEye',[(-.2,.80,z),(-.2,.94,z),(0,.94,z),(0,.8,z)],.022,'Steel')
 save('MotorSpares','Props')
 # Purposeful overhead pipe racks within selected domes, attached to pressure equipment.
 for id,rad in C['decks'].items():
  reset()
  for z,y,mat in [(-.6,6.05,'Steel'),(.6,6.05,'PipeRed')]:
   tube('OverheadDistribution',[(-3.4,y,z),(3.4,y,z)],.13,mat)
   for x in [-2.8,0,2.8]:flange(x,y,z,.13,'x')
  height={'E01':4.65,'E02':4.85,'W02':2.8}[id]
  tube('EquipmentConnection',[(2.15,height,0),(2.15,5.6,0),(2.15,6.05,-.6)],.10,'Steel')
  for x in [-3,0,3]:
   box('TrapezeSupport',x,5.80,0,.10,.10,1.8,'Steel',.008)
   for z in [-.8,.8]:
    roof=math.sqrt(rooms[id]['r']**2-x*x-z*z)-.16
    cyl('SuspensionRod',(x,5.8,z),(x,roof,z),.022,'Steel',12);box('RoofPlate',x,roof,z,.30,.07,.30,'Steel',.006)
  save(id+'_OverheadPlant')
if only and (H/'routes.json').exists():
 oldroutes=json.loads((H/'routes.json').read_text());names={r['name'] for r in routes};routes=[r for r in oldroutes if r['name'] not in names]+routes
(H/'routes.json').write_text(json.dumps(routes,indent=2),encoding='utf8');(H/'layout.json').write_text(json.dumps(C,ensure_ascii=False,indent=2),encoding='utf8')
print('BN_BUILD_READY',flush=True)
