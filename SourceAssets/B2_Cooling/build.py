import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
d=json.loads((H/'source_design.json').read_text(encoding='utf-8'));f=next(f for f in d['floors'] if f['id']=='B2');r=next(r for r in f['rooms'] if r['id']=='C02');rad=11
local=[];doors=[]
for t in f['tunnels']:
 if 'C02' not in [t['a'],t['b']]:continue
 q=dict(t);q['p']=[t['p'][0]-19,t['p'][1]-1];q['q']=[t['q'][0]-19,t['q'][1]-1];local.append(q)
 p=q['p'] if t['a']=='C02' else q['q'];doors.append({'id':t['id'].split('-')[1],'angle':math.degrees(math.atan2(-p[1],p[0]))})
(H/'doors.json').write_text(json.dumps(doors,indent=2))
reset();shell_mats();o=env['sphere']('DomeOuter',0,0,11.22);o.data.materials.append(b.mats['Coat']);cut(o,env['sphere']('DomeInner',0,0,11));cut(o,env['box']('Below',0,-11,0,33,22,33,'Shell',0))
for t in local:cut(o,env['sweep']('DoorOpening',t,extend=4))
for p in o.data.polygons:p.use_smooth=True
o.data.set_sharp_from_angle(angle=.35);m=o.modifiers.new('EdgeBevel','BEVEL');m.width=.008;m.segments=3;m.limit_method='ANGLE';o['bevel_width_m']=.008
save('C02_Shell')
reset();cyl('Foundation',(0,-.24,0),(0,0,0),10.995,'Floor',128);save('C02_Floor')
reset()
def clear(a,y):return y>=3.68 or all(abs((a-k['angle']+180)%360-180)>math.degrees(math.asin(2.7/11)) for k in doors)
for i in range(48):
 a=i*7.5+3.75
 for lo,hi in [(.03,1.3),(1.32,2.64),(2.66,3.66),(3.69,7.4),(7.42,9.45),(9.47,10.95)]:
  if clear(a,lo):sphere_patch('LinerPanel',math.radians(i*7.5+.08),math.radians((i+1)*7.5-.08),math.asin(lo/11),math.asin(hi/11),10.945,10.975,'Coat',2,4)
for a in range(0,360,30):sphere_patch('ArchRib',math.radians(a-.5),math.radians(a+.5),.004 if clear(a,0) else math.asin(3.72/11),1.50,10.78,10.93,'Steel',1,32)
for y in [3.82,8.6]:
 p=math.asin(y/11);sphere_patch('CircumferentialBeam',0,math.tau,p-.008,p+.008,10.78,10.9,'Steel',128,1)
for i in range(72):
 if clear(i*5+2.5,0):sector('CovedSkirt',10.82,11.01,-.01,.16,i*5,(i+1)*5,'Steel',2,.004)
save('C02_Lining')
reset()
for y in [3.92,4.08]:ringtube('PerimeterConduit',10.12,y,0,360,.025,'Steel')
for a in [20,90,150,220,300]:
 if not clear(a,2):continue
 old=set(bpy.context.scene.objects);vent(0,2.5,0,.85,.32);box('VentFrame',0,2.5,-.04,.91,.38,.09,'Dark',.012);transform(set(bpy.context.scene.objects)-old,10.55*math.cos(math.radians(a)),0,10.55*math.sin(math.radians(a)),270-a)
save('C02_Services')
# Structural steel is separate from the genuinely open grating.
reset()
for x in [-7.22,-5.18,5.18,7.22]:
 for z in [-1.68,2.05,5.48]:
  box('ColumnWeb',x,1.70,z,.065,3.4,.21,'Steel',.005)
  for zz in [z-.12,z+.12]:box('ColumnFlange',x,1.70,zz,.24,3.4,.035,'Steel',.004)
  box('ColumnBase',x,.035,z,.4,.07,.42,'Steel',.009)
  for dx in [-.14,.14]:
   for dz in [-.15,.15]:cyl('AnchorBolt',(x+dx,.07,z+dz),(x+dx,.115,z+dz),.018,'Steel',6)
  box('ColumnHead',x,3.32,z,.32,.045,.36,'Steel',.006)
  box('GussetPlate',x,3.1,z+.145,.29,.30,.022,'Steel',.005)
  for yy in [3.02,3.17]:bolt(x-.075,yy,z+.16);bolt(x+.075,yy,z+.16)
 # stringers carry walkway
 for yy,h,w in [(3.32,.24,.045),(3.20,.03,.18),(3.44,.03,.18)]:box('DeckLongBeam',x,yy,1.84,w,h,7.52,'Steel',.004)
for z in [3.43,5.53]:
 for yy,h,dpt in [(3.32,.24,.045),(3.2,.03,.18),(3.44,.03,.18)]:box('NorthBeam',0,yy,z,14.6,h,dpt,'Steel',.004)
for x in [-6.2,6.2]:
 for z in [-1.7,-.4,.9,2.2,3.5,5.45]:box('CrossBearer',x,3.42,z,2.2,.16,.08,'Steel',.004)
 for z in [-1.68,2.05]:cyl('DiagonalKneeBrace',(x-.98,2.65,z),(x+.98,3.30,z),.035,'Steel',12)
for x in [-3.6,0,3.6]:box('NorthJoist',x,3.42,4.5,.08,.16,2.2,'Steel',.005)
save('MezzanineStructure')
reset()
def grate(x,z,w,depth):
 # 50 mm bearing bar spacing, 140 mm transverse ties, real visual apertures.
 count=round(w/.05)
 for i in range(count+1):box('BearingBar',x-w/2+w*i/count,3.565,z,.009,.07,depth,'Steel',.0014)
 for j in range(round(depth/.14)+1):box('CrossTie',x,3.585,z-depth/2+j*depth/round(depth/.14),w,.023,.010,'Steel',.0015)
 for xx in [x-w/2,x+w/2]:box('GratingEdge',xx,3.57,z,.022,.06,depth,'Steel',.003)
 for zz in [z-depth/2,z+depth/2]:box('GratingBand',x,3.57,zz,w,.06,.022,'Steel',.003)
grate(0,4.5,14.6,2.2)
for x in [-6.2,6.2]:grate(x,.75,2.2,5.3)
save('MezzanineGrating')
reset()
for x in [-6.2,6.2]:
 box('OpaqueServicePad',x,3.603,3.3,2.18,.006,1.6,'Plate',.001)
 for z in [2.54,4.06]:box('PadEdge',x,3.610,z,2.17,.008,.035,'Hazard',.001)
for a,c in [((-7.3,-1.9),(-7.3,5.6)),((7.3,-1.9),(7.3,5.6)),((-7.3,5.6),(7.3,5.6)),((-5.1,-1.9),(-5.1,3.4)),((5.1,-1.9),(5.1,3.4)),((-5.1,3.4),(5.1,3.4))]:rail(a,c)
# short landing returns leave 1.4m stair openings
for x in [-6.2,6.2]:
 for sign in [-1,1]:rail((x+sign*.75,-1.9),(x+sign*1.1,-1.9))
save('MezzanineGuards')
reset()
for x in [-6.2,6.2]:
 for i in range(20):
  y=(i+1)*.18;z=-7.5+(i+.5)*.28
  box('FoldedTread',x,y-.025,z,1.4,.05,.28,'Steel',.004)
  box('RiserLip',x,y-.075,z-.12,1.4,.10,.035,'Steel',.003)
  box('AntiSlipNose',x,y+.004,z-.11,1.37,.008,.035,'Hazard',.0015)
  for j in range(4):box('GripGroove',x,y+.002,z-.07+j*.05,1.30,.004,.008,'Dark',.001)
 for xx in [x-.76,x+.76]:
  old=set(bpy.context.scene.objects);ob=box('StairStringer',0,0,0,.09,.25,math.hypot(3.6,5.6),'Steel',.006)
  # oriented beam directly in Blender coordinates
  aa=Vector(xyz(xx,-.08,-7.5));bb=Vector(xyz(xx,3.52,-1.9));ob.location=(aa+bb)/2;ob.rotation_euler=(bb-aa).to_track_quat('Y','Z').to_euler()
  for i in [0,5,10,15,20]:
   y=i*.18;z=-7.5+i*.28;cyl('StairPost',(xx,y,z),(xx,y+1.08,z),.025,'Steel',12)
  for yy,th in [(1.08,.032),(.55,.018)]:cyl('StairHandrail',(xx,yy,-7.5),(xx,3.6+yy,-1.9),th,'Steel',16)
save('MezzanineStairs')
reset()
# Continuous closed cooling loop; ends terminate at actual equipment sockets.
for s in [-1,1]:
 x=s*2.5
 tube('TankReturn',[(x,2.33,0),(x,2.80,0),(x,2.95,.35),(x,2.95,5.85),(x,3.05,6.15),(s*3.0,3.05,6.15)],.13,'Steel')
 for z in [.65,3.0,5.45]:flange(x,2.95,z,.13)
 tube('PumpDischarge',[(s*3,.77,-3.5),(s*3,.77,-2.7),(s*2.5,.77,-2.25),(s*2.5,.77,-.62)],.10,'Steel')
 valve(s*2.5,.77,-1.45,.10)
 old=set(bpy.context.scene.objects);gauge(0,0,0);transform(set(bpy.context.scene.objects)-old,s*2.5,1.36,-1.20,180)
 tube('PumpFeed',[(s*3,.45,-3.55),(s*4.25,.45,-3.55),(s*4.55,.72,-3.55),(s*4.55,2.58,-3.55),(s*4.55,2.85,-3.28),(s*4.55,2.85,5.85),(s*4.25,2.95,6.15),(s*3,2.95,6.15)],.095,'Steel')
 for z in [-1.9,.8,3.2]:
  xx=s*4.55;box('PipeSupportFoot',xx,.035,z,.36,.07,.4,'Steel',.008);cyl('PipeSupport',(xx,.07,z),(xx,2.75,z),.045,'Steel',12);box('PipeSaddle',xx,2.74,z,.24,.05,.18,'Steel',.005)
 box('TankPlinth',x,.06,0,1.68,.12,1.75,'Plate',.016)
 box('PumpSkid',s*3,.055,-3.5,1.9,.11,1.18,'Steel',.014)
 for dx in [-.80,.80]:
  for dz in [-.44,.44]:cyl('SkidAnchor',(s*3+dx,.11,-3.5+dz),(s*3+dx,.15,-3.5+dz),.02,'Steel',6)
for y in [2.95,3.2]:
 tube('RearHeader',[(-4.2,y,6.15),(4.2,y,6.15)],.12,'Steel')
 for x in [-3,0,3]:flange(x,y,6.15,.12,'x')
for x in [-4.2,0,4.2]:
 box('HeaderAnchor',x,2.96,6.35,.22,.55,.06,'Steel',.006);cyl('HeaderStandoff',(x,2.97,6.15),(x,2.97,6.36),.035,'Steel',12)
 for y in [.04,3.15]:box('HeaderSupportPlate',x,y,6.40,.34,.06,.32,'Steel',.006)
 box('HeaderSupportUpright',x,1.58,6.4,.09,3.1,.09,'Steel',.006)
for s in [-1,1]:
 for i,z in enumerate([2.93,3.25,3.57]):
  y=2.68+i*.14
  tube('UpperStationFeed',[(s*4.15,y,6.15),(s*6.64,y,6.15),(s*6.64,y,z),(s*6.64,3.98,z)],.032,'Steel')
  cyl('DeckPenetrationSeal',(s*6.64,3.60,z),(s*6.64,3.63,z),.062,'Rubber',20)
for s in [-1,1]:
 for y,targetY in [(2.95,1.35),(3.2,.62)]:
  tube('ExchangerConnection',[(s*1.4,y,6.15),(s*.38,y,6.15),(s*.38,targetY,6.15),(s*.38,targetY,6.40)],.075,'Steel');flange(s*.38,targetY,6.38,.075)
save('CoolingPipework')
reset()
# Walkway and machinery floor detailing, sealed drains, variable maintenance boundaries.
for x in [-4.1,4.1]:
 box('DrainChannel',x,.006,-.9,.18,.012,5.8,'Dark',.002)
 for i in range(66):box('DrainRung',x,.014,-3.7+i*.086,.16,.015,.025,'Steel',.002)
for x in [-3,3]:
 for s in [-1,1]:box('SkidPerimeter',x+s*1.1,.009,-3.5,.055,.016,1.52,'Hazard',.001)
 for z in [-4.26,-2.74]:box('SkidBoundary',x,.009,z,2.2,.016,.055,'Hazard',.001)
for z in [-6,-3,0,3,6]:
 box('FloorExpansionJoint',0,.003,z,math.sqrt(11**2-z*z)*2-.3,.006,.012,'Dark',.001)
save('FloorDetails')
