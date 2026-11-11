import sys,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
plan=json.loads((H/'plan.json').read_text(encoding='utf8'));rooms={r['id']:r for r in plan['rooms']}
for r in plan['rooms']:
 code=r['id'];rad=r['r'];core=r['kind']=='core';local=[]
 for t in plan['tunnels']:
  if code in [t['a'],t['b']]:
   q=copy.deepcopy(t);q['path']=[[p[0]-r['x'],p[1]-r['v']] for p in t['path']];local.append(q)
 reset()
 if core:o=cyl('Shaft',(0,-.2,0),(0,22,0),rad+.22,'Coat',128);cut(o,cyl('Void',(0,-.4,0),(0,21.8,0),rad,'Coat',128))
 else:
  o=sphere('Dome',0,0,rad+.22);o.data.materials.append(b.mats['Coat']);cut(o,sphere('Interior',0,0,rad));cut(o,box('BaseCut',0,-rad,0,rad*3,rad*2,rad*3,'Dark',0))
 for t in local:cut(o,sweep('Opening',t,extend=4))
 for p in o.data.polygons:p.use_smooth=True
 o.data.set_sharp_from_angle(angle=math.radians(25));save(code+'_Shell')
 reset();cyl('SeamlessFloor',(0,-.24,0),(0,0,0),rad-.005,'Floor',128)
 # Remove cylinder bevel at the floor rim: tunnel and floor meet at exactly y=0.
 for o in bpy.context.scene.objects:o.modifiers.clear()
 save(code+'_Floor')
 reset()
 def clear(a,y=0):return y>3.7 or all(abs((a-d['angle']+180)%360-180)>math.degrees(math.asin(min(.95,2.85/rad)))+3 for d in r['doors'])
 if not core:
  for i in range(48):
   a=i*7.5+3.75
   for lo,hi in [(.04,1.28),(1.31,2.60),(2.63,3.68),(3.72,rad*.72),(rad*.72+.03,rad*.89)]:
    if lo>=hi or not clear(a,lo):continue
    sphere_patch('IvoryLiner',math.radians(i*7.5+.10),math.radians((i+1)*7.5-.10),math.asin(lo/rad),math.asin(hi/rad),rad-.08,rad-.06,'Coat',3,4)
  for a in range(0,360,45):sphere_patch('Rib',math.radians(a-.35),math.radians(a+.35),.008 if clear(a) else math.asin(3.85/rad),1.48,rad-.18,rad-.105,'Steel',1,30)
  for y in [3.88,rad*.80]:
   phi=math.asin(y/rad);sphere_patch('Ring',0,math.tau,phi-.004,phi+.004,rad-.205,rad-.185,'Steel',128,1)
 else:
  for y in [3.8,7.7,11.6,15.5,19.4]:ringtube('ShaftRing',4.88,y,0,360,.035)
 for i in range(72):
  if clear(i*5+2.5):sector('CovedSkirt',rad-.19,rad-.11,.015,.13,i*5+.08,(i+1)*5-.08,'Steel',3,.002)
 save(code+'_Lining')
 reset();y=4.10;rr=4.82 if core else math.sqrt(rad*rad-y*y)-.26
 for yy in [y,y+.13]:ringtube('Conduit',rr,yy,0,360,.017)
 for a in range(15,360,60):
  if not clear(a):continue
  th=math.radians(a);rr2=4.78 if core else math.sqrt(rad*rad-2.5**2)-.30;old=set(bpy.context.scene.objects);vent(0,2.5,0,.75,.26);box('VentBack',0,2.5,-.05,.82,.32,.09,'Dark',.006);transform(set(bpy.context.scene.objects)-old,rr2*math.cos(th),0,rr2*math.sin(th),270-a)
 save(code+'_Services')
for t in plan['tunnels']:
 reset();o=sweep('Vault',t,.18);cut(o,sweep('Void',t,extend=.3))
 for rid in [t['a'],t['b']]:
  r=rooms[rid];cut(o,sphere('EndCut',r['x'],r['v'],r['r']+.22) if r['kind']!='core' else cyl('EndCut',(r['x'],-1,-r['v']),(r['x'],5,-r['v']),r['r']+.22,'Dark',128))
 fl=floorbar(t)
 for rid in [t['a'],t['b']]:
  r=rooms[rid];cut(fl,cyl('FloorCut',(r['x'],-1,-r['v']),(r['x'],1,-r['v']),r['r']-.005,'Dark',128))
 save(t['id'].split('-')[1]+'_Shell')
reset();rise=1.8;steps=12;tread=.27;half=steps*tread/2
for flight in range(10):
 direction=1 if flight%2==0 else -1;x=-.96 if direction==1 else .96;z0=-half*direction;y0=flight*rise
 for i in range(steps):
  y=y0+(i+1)*.15;z=z0+direction*(i+.5)*tread;box('Tread',x,y-.04,z,1.5,.08,tread,'Steel',.003);box('Riser',x,y-.115,z-direction*(tread/2-.012),1.49,.07,.024,'Coat',.002);box('Nosing',x,y+.003,z-direction*.105,1.43,.006,.035,'Mark',.001)
 for xx in [x-.78,x+.78]:
  cyl('Stringer',(xx,y0-.08,z0),(xx,y0+rise-.08,-z0),.055,'Steel',12)
  for i in [0,3,6,9,12]:cyl('RailPost',(xx,y0+i*.15,z0+direction*i*tread),(xx,y0+i*.15+1.06,z0+direction*i*tread),.023,'Steel',12)
  for yy,th in [(1.06,.028),(.54,.016)]:cyl('Handrail',(xx,y0+yy,z0),(xx,y0+rise+yy,-z0),th,'Steel',16)
 y=y0+rise;z=-z0+direction*.70;box('Landing',0,y-.08,z,3.44,.16,1.40,'Steel',.006)
 for xx in [-1.74,1.74]:cyl('LandingPost',(xx,y,z+direction*.65),(xx,y+1.07,z+direction*.65),.023,'Steel',12)
 for yy,th in [(1.07,.028),(.54,.016)]:
  if flight<9:cyl('BackRail',(-1.74,y+yy,z+direction*.65),(1.74,y+yy,z+direction*.65),th,'Steel',16)
  else:
   for a,bb in [(-1.74,-.90),(.90,1.74)]:cyl('BackRail',(a,y+yy,z+direction*.65),(bb,y+yy,z+direction*.65),th,'Steel',16)
  for xx in [-1.74,1.74]:cyl('SideRail',(xx,y+yy,-z0),(xx,y+yy,z+direction*.65),th,'Steel',16)
for x in [-1.78,1.78]:
 for z in [-3.04,3.04]:box('Column',x,9,z,.12,18,.12,'Steel',.006)
box('ArrivalLanding',0,17.92,-3.70,1.8,.16,1.4,'Steel',.006)
for x in [-.90,.90]:
 for z in [-3,-4.39]:cyl('BridgePost',(x,18,z),(x,19.08,z),.023,'Steel',12)
 for y in [18.54,19.08]:cyl('BridgeRail',(x,y,-3),(x,y,-4.39),.025,'Steel',16)
save('Stairs18m')
print('B1 ARCHITECTURE COMPLETE',flush=True)
