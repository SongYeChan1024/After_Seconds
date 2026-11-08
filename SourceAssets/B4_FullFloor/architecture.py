import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
plan=json.loads((H/'plan.json').read_text(encoding='utf-8'));rooms={r['id']:r for r in plan['rooms']};ts=plan['tunnels']
for r in plan['rooms']:
 if r['id']=='C01':continue
 code=r['id'];rad=r['r'];core=r['kind']=='core';local=[]
 for t in ts:
  if code not in [t['a'],t['b']]:continue
  q=dict(t);q['p']=[t['p'][0]-r['x'],t['p'][1]-r['v']];q['q']=[t['q'][0]-r['x'],t['q'][1]-r['v']];local.append(q)
 reset();shell_mats()
 if core:
  o=cyl('Shaft_Outer',(0,-.20,0),(0,20.5,0),5.22,'Coat',96);cut(o,cyl('Shaft_Interior',(0,-.5,0),(0,20.25,0),5.0,'Dark',96))
 else:
  o=env['sphere']('Dome_Outer',0,0,rad+.22);o.data.materials.append(b.mats['Coat']);cut(o,env['sphere']('Dome_Interior',0,0,rad));cut(o,env['box']('BaseCut',0,-rad,0,rad*3,rad*2,rad*3,'Shell',0))
 for t in local:cut(o,env['sweep']('DoorCut',t,extend=4))
 for p in o.data.polygons:p.use_smooth=True
 o.data.set_sharp_from_angle(angle=math.radians(20));be=o.modifiers.new('Manufactured_Rim','BEVEL');be.width=.008;be.segments=2;be.limit_method='ANGLE'
 save(code+'_Shell')
 reset();shell_mats();floor=cyl('Floor',(0,-.24,0),(0,0,0),rad-.005,'Floor',128)
 if code=='C02':
  t=next(t for t in local if t['id']=='B4-T02');cut(floor,env['sweep']('Existing_T02_Floor_Clearance',dict(t,h=3.4),extend=0))
 save(code+'_Floor')
 reset()
 def clear(a,y):return y>=3.65 or all(abs((a-d['angle']+180)%360-180)>math.degrees(math.asin(min(.95,2.65/rad))) for d in r['doors'])
 if not core:
  for i in range(36):
   a=i*10+5
   for lo,hi in [(0.03,1.3),(1.32,2.64),(2.66,3.65),(3.67,rad*.68),(rad*.68+.02,rad*.86),(rad*.86+.02,rad-.08)]:
    if hi<=lo or hi>=rad or not clear(a,lo):continue
    sphere_patch('Wall_Panel',math.radians(i*10+.08),math.radians((i+1)*10-.08),math.asin(lo/rad),math.asin(hi/rad),rad-.045,rad-.025,'Coat',2,3)
  for a in range(0,360,45):sphere_patch('Continuous_Rib',math.radians(a-.45),math.radians(a+.45),.004 if clear(a,0) else math.asin(3.7/rad),1.50,rad-.16,rad-.055,'Steel',1,26)
  for y in [3.78,rad*.79]:
   p=math.asin(y/rad);sphere_patch('Structural_Ring',0,math.tau,p-.005,p+.005,rad-.15,rad-.06,'Steel',96,1)
 else:
  for y in [3.7,7.8,12.0,16.2,19.7]:ringtube('Shaft_Structural_Ring',4.9,y,0,360,.04)
  for a in range(0,360,15):
   t=math.radians(a);cyl('Shaft_Panel_Seam',(4.96*math.cos(t),3.65,4.96*math.sin(t)),(4.96*math.cos(t),20.1,4.96*math.sin(t)),.006,'Dark',6)
 for i in range(72):
  if clear(i*5+2.5,0):sector('Sealed_Skirting',rad-.15,rad+.12,-.01,.13,i*5,(i+1)*5,'Steel',2,.002)
 save(code+'_Lining')
 reset()
 y=3.9 if core else 3.75;rr=4.86 if core else math.sqrt(rad*rad-y*y)-.18
 for h in [y,y+.16]:ringtube('Service_Conduit',rr,h,0,360,.021)
 for a in range(15,360,60):
  if not clear(a,2):continue
  t=math.radians(a);rr2=4.84 if core else math.sqrt(rad*rad-2.5**2)-.22;x,z=rr2*math.cos(t),rr2*math.sin(t)
  old=set(bpy.context.scene.objects);vent(0,2.48,0,.72,.25);box('Vent_Backing',0,2.48,-.045,.78,.29,.09,'Dark',.01);transform(set(bpy.context.scene.objects)-old,x,0,z,270-a)
  tube('Conduit_Drop',[(rr*math.cos(t),y,rr*math.sin(t)),(x,2.68,z),(x,2.56,z)],.018,'Steel')
 save(code+'_Services');print('ROOM COMPLETE',code,flush=True)

for t in ts:
 if t['id']=='B4-T02':continue
 code=t['id'].split('-')[1];p,q=t['p'],t['q'];dx,dv=q[0]-p[0],q[1]-p[1];L=math.hypot(dx,dv);yaw=math.degrees(math.atan2(dx,-dv))
 reset();shell_mats();o=env['sweep']('Tunnel_Vault',t,pad=.18);cut(o,env['sweep']('Interior',t,extend=.4))
 for rid in [t['a'],t['b']]:
  r=rooms[rid]
  c=env['sphere']('Dome_Clearance',r['x'],r['v'],r['r']) if r['kind']!='core' else cyl('Core_Clearance',(r['x'],-1,-r['v']),(r['x'],5,-r['v']),r['r'],'Dark',96)
  cut(o,c)
 floor=env['floorbar'](t)
 for rid in [t['a'],t['b']]:
  r=rooms[rid];cut(floor,cyl('Floor_Seam_Cut',(r['x'],-1,-r['v']),(r['x'],1,-r['v']),r['r']-.005,'Dark',128))
 save(code+'_Shell')
 reset()
 # Local corridor finish, wall bumpers, cable services, drainage. Kept behind passage width.
 for side in [-1,1]:
  x=side*2.02
  box('Wall_Bumper',x,.8,L/2,.065,.12,max(.2,L-1.6),'Steel',.012)
  box('Floor_Drain',side*1.91,.006,L/2,.10,.012,max(.2,L-1.6),'Dark',.003)
  for z in [i*1.8+.9 for i in range(int(L/1.8))]:
   for j in range(4):box('Drain_Grating',side*1.91,.014,z+j*.12,.09,.005,.026,'Steel',.002)
 for x in [-.55,.55]:cyl('Overhead_Conduit',(x,3.24,.45),(x,3.24,L-.45),.026,'Steel',12)
 for z in [i*3.0+.8 for i in range(int(L/3))]:
  cyl('Cable_Hanger',(-.61,3.26,z),(.61,3.26,z),.014,'Steel',12)
 for z in [L*.28,L*.72]:
  old=set(bpy.context.scene.objects);vent(0,1.8,0,.62,.27);transform(set(bpy.context.scene.objects)-old,2.01,0,z,270)
 save(code+'_Finish');print('TUNNEL COMPLETE',code,flush=True)

reset();rise=17/8;steps=13;tread=.27;half=steps*tread/2
for flight in range(8):
 direction=1 if flight%2==0 else -1;x=-.96 if flight%2==0 else .96;z0=-half*direction;y0=flight*rise
 for i in range(steps):
  y=y0+(i+1)*rise/steps;z=z0+direction*(i+.5)*tread
  box('Folded_Stair_Tread',x,y-.045,z,1.5,.09,tread,'Steel',.005);box('Closed_Riser',x,y-rise/steps/2,z-direction*(tread/2-.015),1.49,rise/steps,.03,'Coat',.003);box('AntiSlip_Nose',x,y+.003,z-direction*.105,1.43,.006,.035,'Mark',.001)
 for xx in [x-.78,x+.78]:
  cyl('Stair_Stringer',(xx,y0-.07,z0),(xx,y0+rise-.07,-z0),.065,'Steel',12)
  for i in [0,3,6,9,13]:
   y=y0+i*rise/steps;z=z0+direction*i*tread;cyl('Rail_Post',(xx,y,z),(xx,y+1.06,z),.024,'Steel',12)
  for yy,th in [(1.06,.03),(.54,.017)]:cyl('Continuous_Handrail',(xx,y0+yy,z0),(xx,y0+rise+yy,-z0),th,'Steel',16)
 y=y0+rise;z=-z0+direction*.70;box('Full_Landing',0,y-.08,z,3.44,.16,1.40,'Steel',.008);box('Landing_Surface',0,y+.002,z,3.32,.004,1.28,'Floor',.001)
 for xx in ([-1.74,-.90,.90,1.74] if flight==7 else [-1.74,0,1.74]):cyl('Landing_Post',(xx,y,z+direction*.67),(xx,y+1.08,z+direction*.67),.025,'Steel',12)
 for yy,th in [(1.08,.032),(.54,.018)]:
  if flight==7:
   for a,bx in [(-1.74,-.9),(.9,1.74)]:cyl('Landing_Backrail',(a,y+yy,z+direction*.67),(bx,y+yy,z+direction*.67),th,'Steel',16)
  else:cyl('Landing_Backrail',(-1.74,y+yy,z+direction*.67),(1.74,y+yy,z+direction*.67),th,'Steel',16)
  for xx in [-1.74,1.74]:cyl('Landing_Siderail',(xx,y+yy,-z0),(xx,y+yy,z+direction*.67),th,'Steel',16)
for x in [-1.78,1.78]:
 for z in [-3.12,3.12]:box('Structural_Column',x,8.5,z,.14,17,.14,'Steel',.008)
box('Upper_Door_Bridge',0,16.92,-3.83,1.8,.16,1.4,'Steel',.008)
box('Upper_Door_Walkway',0,17.002,-3.83,1.68,.004,1.34,'Floor',.001)
for x in [-.9,.9]:
 for z in [-3.13,-4.48]:cyl('Upper_Bridge_Post',(x,17,z),(x,18.08,z),.025,'Steel',12)
 for y,th in [(18.08,.032),(17.54,.018)]:cyl('Upper_Bridge_Handrail',(x,y,-3.13),(x,y,-4.48),th,'Steel',16)
save('VerticalStairs')
reset()
# Cargo lift cabin at B4 level: enclosed back, bumpers, recessed floor, door headers.
box('Lift_Platform',0,.035,-1.25,3.70,.07,3.5,'Steel',.012)
box('Lift_Back',0,1.9,-2.98,3.74,3.8,.12,'Coat',.012)
for x in [-1.84,1.84]:
 box('Lift_Side',x,1.9,-1.25,.10,3.8,3.5,'Coat',.01)
 for z in [-2.8,-2.1,-1.4,-.7,.1]:box('Wall_Crash_Rib',x-(.055 if x>0 else -.055),1.3,z,.065,1.9,.10,'Steel',.008)
 for y in [.5,1.05]:box('Impact_Bumper',x-(.1 if x>0 else -.1),y,-1.25,.08,.09,3.1,'Rubber',.008)
 box('Lift_Door_Jamb',x,2.0,.48,.22,4.0,.28,'Steel',.012)
box('Lift_Roof',0,3.78,-1.25,3.70,.12,3.5,'Steel',.012);box('Roller_Header',0,3.87,.48,3.80,.30,.40,'Steel',.015)
for x in [-1.91,1.91]:
 box('Guide_Rail',x,10,-2.7,.11,20,.12,'Steel',.005)
 for y in [1,3.5,6,8.5,11,13.5,16,18.5]:box('Rail_Bracket',x,y,-2.85,.25,.12,.30,'Steel',.008)
for i in range(18):box('Threshold_Groove',-.85+i*.1,.075,.51,.045,.01,.32,'Dark',.001)
box('Call_Panel',2.13,1.3,.57,.22,.55,.08,'Dark',.01);display(2.13,1.43,.62,.14,.15,22)
for y in [1.13,1.24]:cyl('Call_Button',(2.13,y,.62),(2.13,y,.638),.035,'Steel',24)
save('CargoLift')
print('ARCHITECTURE DONE',flush=True)
