"""C01 observation dome and representative approach. Author 송예찬."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import common as b
from common import *
plan=json.loads((H/'plan.json').read_text(encoding='utf-8'))
doors=[]
for t in plan['tunnels']:
 p=t['p'] if t['a']=='C01' else t['q'];a=math.degrees(math.atan2(-p[1],p[0]));doors.append(a)

# Closed, thick hemisphere with exact vaulted openings.
tree=ast.parse((R/'SourceAssets/CircularFacility/build_geometry.py').read_text(encoding='utf-8'))
env={'bpy':bpy,'bmesh':bmesh,'math':math,'Vector':Vector}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'shell_helpers','exec'),env)
reset();env['mats']={'Shell':b.mats['Coat'],'Floor':b.mats['Floor'],'Steel':b.mats['Steel']}
o=env['sphere']('Dome_Outer',0,0,12.22);cut=env['sphere']('Dome_Interior',0,0,12);env['boolean'](o,cut);bpy.data.objects.remove(cut,do_unlink=True)
o.data.materials.append(b.mats['Coat'])
bottom=env['box']('Lower_Cut',0,-12,0,40,24,40,'Shell',0);env['boolean'](o,bottom);bpy.data.objects.remove(bottom,do_unlink=True)
for t in plan['tunnels']:
 cut=env['sweep']('Portal_Cut',t,extend=4);env['boolean'](o,cut);bpy.data.objects.remove(cut,do_unlink=True)
for p in o.data.polygons:p.use_smooth=True
o.data.set_sharp_from_angle(angle=math.radians(20))
mod=o.modifiers.new('Portal_Edge_Bevel','BEVEL');mod.width=.012;mod.segments=2;mod.limit_method='ANGLE'
wn=o.modifiers.new('Portal_Weighted_Normals','WEIGHTED_NORMAL');wn.keep_sharp=True
save('C01_Shell')

reset();cyl('Seamless_Resin_Floor',(0,-.24,0),(0,.0,0),11.99,'Floor',160);save('C01_Floor')

def clear(a,y):
 if y>=3.6:return True
 return all(abs((a-d+180)%360-180)>math.degrees(math.asin(2.7/12)) for d in doors)
reset()
for i in range(48):
 a=i*7.5+3.75
 for lo,hi in [(0.02,1.2),(1.22,2.4),(2.42,3.62),(3.64,5.0),(5.02,6.5),(6.52,8.0),(8.02,9.4),(9.42,10.5),(10.52,11.4),(11.42,11.96)]:
  if not clear(a,lo):continue
  sphere_patch('Dome_Panel',math.radians(i*7.5+.08),math.radians((i+1)*7.5-.08),math.asin(lo/12),math.asin(hi/12),11.965,11.985,'Coat',3,3)
for i in range(8):
 a=i*45;lo=.004 if clear(a,0) else math.asin(3.65/12)
 sphere_patch('Continuous_Rib',math.radians(a-.34),math.radians(a+.34),lo,1.50,11.82,11.94,'Steel',2,40)
for y in [3.70,9.5]:
 phi=math.asin(y/12);sphere_patch('Structural_Ring',0,math.tau,phi-.004,phi+.004,11.82,11.94,'Steel',160,2)
save('C01_PanelsRibs')

reset()
for i in range(32):
 a0=50+i*2.5;a1=a0+2.5
 sector('Deck_Tray',7.2,10.6,2.31,2.49,a0+.015,a1-.015,'Steel',2,.004)
 sector('NonSlip_Deck',7.23,10.57,2.49,2.50,a0+.025,a1-.025,'Floor',2,.002)
for rr in [7.35,10.45]:
 sector('Curved_LoadBearing_Beam',rr-.08,rr+.08,2.04,2.32,50,130,'Steel',64,.009)
for deg in [52,65,80,100,115,128]:
 a=math.radians(deg);x,z=10.35*math.cos(a),10.35*math.sin(a)
 box('Column_Base',x,.055,z,.35,.11,.35,'Steel',.012);box('Structural_Column',x,1.15,z,.15,2.1,.15,'Steel',.01)
 for dx in [-.12,.12]:
  for dz in [-.12,.12]:cyl('Anchor_Bolt',(x+dx,.11,z+dz),(x+dx,.13,z+dz),.017,'Steel',6)
 cyl('Radial_Joist',(7.25*math.cos(a),2.26,7.25*math.sin(a)),(10.5*math.cos(a),2.26,10.5*math.sin(a)),.075,'Steel',12)
# Two full landings physically meet the uppermost stair tread.
# Cut stair wells so the slanted deck edge cannot obstruct headroom.
for sx in [-5.8,5.8]:
 cut=box('Stairwell_Cut',sx,2.4,4.90,1.72,1.0,4.30,'Steel',0)
 for ob in list(bpy.context.scene.objects):
  if ob!=cut and ob.type=='MESH':env['boolean'](ob,cut)
 bpy.data.objects.remove(cut,do_unlink=True)
for sx in [-5.8,5.8]:box('Stair_Landing',sx,2.40,7.70,1.64,.20,1.50,'Steel',.008);box('Landing_Finish',sx,2.495,7.70,1.60,.01,1.46,'Floor',.003)
save('C01_DeckStructure')

reset()
for r in [7.21,10.57]:
 for i in range(17):
  a=math.radians(50+i*5);x,z=r*math.cos(a),r*math.sin(a)
  cyl('Guard_Post',(x,2.5,z),(x,3.60,z),.026,'Steel',16);box('Post_Base',x,2.52,z,.13,.04,.13,'Steel',.006)
 ringtube('Continuous_Handrail',r,3.60,50,130,.032)
 ringtube('Toe_Rail',r,2.62,50,130,.018)
 for i in range(16):
  sector('Laminated_Observation_Glass',r-.008,r+.008,2.69,3.48,50+i*5+.30,55+i*5-.30,'Glass',4,.002)
  for deg in [51+i*5,54+i*5]:
   a=math.radians(deg);box('Glass_Clamp',r*math.cos(a),2.85,r*math.sin(a),.055,.10,.045,'Steel',.005)
# Landings are open at the stairs, guarded on their exposed outer sides.
for sx in [-5.8,5.8]:
 sign=1 if sx>0 else -1;x=sx+sign*.84
 for z in [7.05,8.35]:cyl('Landing_Post',(x,2.5,z),(x,3.6,z),.026,'Steel',16)
 cyl('Landing_Handrail',(x,3.6,7.05),(x,3.6,8.35),.032,'Steel',16)
save('C01_DeckGuards')

reset()
for sx in [-5.8,5.8]:
 for i in range(15):
  h=(i+1)/6;z=2.8+i*.28
  box('Folded_Tread',sx,h-.035,z+.14,1.6,.07,.28,'Steel',.006)
  box('Closed_Riser',sx,h-1/12,z+.018,1.59,1/6,.036,'Steel',.003)
  box('AntiSlip_Nose',sx,h+.002,z+.035,1.50,.004,.045,'Rubber',.001)
  for x in [sx-.73,sx+.73]:box('Step_Edge',x,h+.003,z+.04,.065,.006,.07,'Mark',.001)
 for x in [sx-.81,sx+.81]:
  cyl('Stair_Stringer',(x,.06,2.77),(x,2.32,7.02),.085,'Steel',8)
  for i in [0,5,10,14]:
   h=(i+1)/6;z=2.8+i*.28+.14;cyl('Stair_Rail_Post',(x,h,z),(x,h+1.05,z),.024,'Steel',16)
  cyl('Continuous_Stair_Handrail',(x,1.05,2.74),(x,3.55,7.05),.032,'Steel',16)
  cyl('Mid_Rail',(x,.60,2.74),(x,3.10,7.05),.019,'Steel',12)
save('C01_Stairs')

reset()
for y in [3.85,4.02]:
 r=math.sqrt(144-y*y)-.21;ringtube('Perimeter_Service_Conduit',r,y,0,360,.032)
for a in range(0,360,30):
 t=math.radians(a);r=math.sqrt(144-3.9**2)-.18;x,z=r*math.cos(t),r*math.sin(t)
 cyl('Service_Hanger',(x,3.8,z),(x,4.1,z),.016,'Steel',12)
 if not clear(a,2):continue
 r0=math.sqrt(144-2.5**2)-.16;x0,z0=r0*math.cos(t),r0*math.sin(t)
 tube('Wall_Conduit',[(x,3.85,z),(x,2.65,z),(x0,2.5,z0)],.020,'Steel')
 new=set(bpy.context.scene.objects);vent(0,2.45,0,.8,.28);box('Vent_Closed_Plenum',0,2.45,-.05,.85,.32,.12,'Dark',.01)
 transform(set(bpy.context.scene.objects)-new,x0,0,z0,180-a+90)
save('C01_Services')

reset()
for r in [2.55,2.60]:sector('Flush_Calibration_Ring',r,r+.018,.002,.004,0,360,'Mark',128,0)
for i in range(72):
 a=math.radians(i*5);rr=2.48;length=.15 if i%6==0 else .065
 p=(rr*math.cos(a),.004,rr*math.sin(a));q=((rr-length)*math.cos(a),.004,(rr-length)*math.sin(a));cyl('Angular_Measure_Tick',p,q,.004,'Mark',6)
for x in [-.18,.18]:box('Subject_Foot_Position',x,.004,0,.12,.006,.32,'Mark',.004)
for x,z in [(-2.2,0),(2.2,0),(0,-2.2),(0,2.2)]:cyl('Flush_Registration_Disc',(x,.002,z),(x,.005,z),.075,'Steel',24)
save('C01_MeasurementFloor')

# Build full T02 approach vault/floor. Future C02 side stays closed in this representative scene.
t=next(t for t in plan['tunnels'] if t['id']=='B4-T02');start=Vector((t['p'][0],0,-t['p'][1]));end=Vector((t['q'][0],0,-t['q'][1]));L=(end-start).length
reset();env['mats']={'Shell':b.mats['Coat'],'Floor':b.mats['Floor'],'Steel':b.mats['Steel']}
outer=env['sweep']('T02_Vault',t,pad=.18,mat='Shell');inner=env['sweep']('T02_Clearance',t,extend=.4);env['boolean'](outer,inner);bpy.data.objects.remove(inner,do_unlink=True)
roomcut=env['sphere']('Dome_Clearance',0,0,12);env['boolean'](outer,roomcut);bpy.data.objects.remove(roomcut,do_unlink=True);env['floorbar'](t)
save('T02_ApproachShell')
reset()
for i in range(360):
 a=i+.5
 if all(abs((a-d+180)%360-180)>10.8 for d in doors):sector('Sealed_Wall_Base',11.87,12.16,-.015,.14,i,i+1,'Steel',1,.002)
save('C01_Skirting')
print('ARCHITECTURE COMPLETE',flush=True)
