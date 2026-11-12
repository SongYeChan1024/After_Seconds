"""13 compact architectural insert meshes, using existing B1 materials."""
from pathlib import Path
import sys,json,math
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parent/'B1_FullFloor'))
import common as c
c.H=H
from common import *
p=json.loads((H/'layout.json').read_text(encoding='utf8'));inter=p['interior']
colliders={};lifedetails=[]
def block(name,x,y,z,w,h,d,mat='Coat',bevel=.006):
 box(name,x,y,z,w,h,d,mat,bevel)
def part(w):
 ax,az=w['a'];bx,bz=w['b'];dx=bx-ax;dz=bz-az;length=math.hypot(dx,dz);yaw=math.degrees(math.atan2(-dz,dx));h=w['h'];th=w['th'];name=w['name']
 old=set(bpy.context.scene.objects)
 # Continuous slab and shallow, separated applied trims. No coplanar overlays.
 if w.get('glazed'):
  block(name+'_LowerPanel',0,.56,0,length,1.12,th,w['mat'],.007)
  block(name+'_UpperPanel',0,(h+2.42)/2,0,length,h-2.42,th,w['mat'],.007)
  # Glazed strip gives a view into occupied offices while remaining a physical wall.
  block(name+'_Glazing',0,1.77,0,length-.08,1.27,.012,'Glass',.001)
  for xx in [-length/2+.025,length/2-.025]:block(name+'_WindowPost',xx,1.77,0,.045,1.3,th+.018,'Steel',.003)
  for yy in [1.145,2.395]:block(name+'_WindowRail',0,yy,0,length-.06,.028,th+.018,'Steel',.002)
 else:block(name+'_Panel',0,h/2,0,length,h,th,w['mat'],.007)
 for side in [-1,1]:
  z=side*(th/2+.009)
  block(name+'_Skirt',0,.075,z,length-.024,.13,.012,'Steel',.002)
  if h>2:
   block(name+'_ChairRail',0,.92,z,length-.025,.035,.012,'Warm',.002)
   n=max(1,math.ceil(length/1.25))
   for k in range(1,n):
    if w.get('glazed'):
     block(name+'_Joint',-length/2+k*length/n,.56,z,.012,1.07,.008,'Steel',.001)
    else:block(name+'_Joint',-length/2+k*length/n,h/2,z,.012,h-.05,.008,'Steel',.001)
 block(name+'_Cap',0,h+.014,0,length+.01,.023,th+.03,'Steel',.003)
 transform(set(bpy.context.scene.objects)-old,(ax+bx)/2,0,(az+bz)/2,yaw)
 colliders.setdefault(w['room'],[]).append(dict(name=name,position=[(ax+bx)/2,h/2,(az+bz)/2],size=[length,h,th],yaw=yaw))
def ceiling(q):
 x0,z0,x1,z1=q['bounds'];y=q['y'];n=q['name'];w=x1-x0;d=z1-z0
 # Open peripheral slot and longitudinal ceiling rafts preserve original dome silhouette.
 panels=max(1,math.ceil(w/2.1));pitch=w/panels
 for i in range(panels):
  x=x0+(i+.5)*pitch
  block(n+'_AcousticRaft',x,y,(z0+z1)/2,pitch-.09,.085,d-.12,'Coat',.009)
  colliders.setdefault(q['room'],[]).append(dict(name=n+'_Ceiling',position=[x,y,(z0+z1)/2],size=[pitch-.09,.085,d-.12],yaw=0))
  for z in [z0+.04,z1-.04]:block(n+'_Beam',x,y+.10,z,pitch-.04,.10,.07,'Steel',.004)
 # Four visibly grounded supports, inset from adjacent walls to avoid coincident faces.
 for x in [x0+.10,x1-.10]:
  for z in [z0+.12,z1-.12]:
   block(n+'_Post',x,(y-.065)/2,z,.065,y-.065,.065,'Steel',.004)
   colliders.setdefault(q['room'],[]).append(dict(name=n+'_Post',position=[x,(y-.065)/2,z],size=[.065,y-.065,.065],yaw=0))
 # A little acoustic underside detail, kept above standing clearance.
 for z in [z0+.36,z1-.36]:block(n+'_EdgeInlay',(x0+x1)/2,y-.05,z,w-.35,.014,.035,'Warm',.002)
def details(room):
 # Human use is visible at useful surfaces, not as corridor clutter.
 if room in ['W03','E03']:
  beds=[q for q in p['placements'] if q['room']==room and q['model']=='BL_StaffBunk']
  for i,q in enumerate(beds):
   x,y,z=q['position'];xx=x-.28
   block('BedReadingShelf',xx,.96,z-1.05,.36,.045,.20,'Warm',.008)
   block('PersonalBook',xx,.995,z-1.05,.23,.018,.15,'Teal' if i%2 else 'Fabric',.002)
   for zz in [-.08,.08]:block('FoldedTowel',x+.10,.623,z+.53+zz,.36,.035,.14,'Paper',.006)
 if room=='W02':
  block('CoffeeTable',-7.0,.46,4.6,1.25,.065,.63,'Warm',.015)
  for xx in [-.5,.5]:
   for zz in [-.22,.22]:block('CoffeeLeg',-7+xx,.215,4.6+zz,.045,.43,.045,'Steel',.004)
  colliders.setdefault(room,[]).append(dict(name='CoffeeTable',position=[-7,.26,4.6],size=[1.25,.52,.63],yaw=0))
  for i in range(3):block('SharedMagazine',-7+i*.07,.505+i*.009,4.6,.26,.008,.33,'Teal' if i%2 else 'Paper',.002)
 if room=='C02':
  # A slim counter makes record handover distinguishable from another office desk.
  block('IntakeShelf',2.04,.94,-1.5,.48,.065,.72,'Warm',.008)
  for z in [-1.65,-1.37]:
   block('IntakeDocument',2.0,.989,z,.29,.02,.23,'Paper',.002)
for r in p['rooms']:
 room=r['id']
 if r['kind']=='core':continue
 reset()
 for w in inter['walls']:
  if w['room']==room:part(w)
 for q in inter['ceilings']:
  if q['room']==room:ceiling(q)
 details(room)
 save('RI_'+room+'_Interior','Environment',False)
(H/'structural_colliders.json').write_text(json.dumps(colliders,indent=2),encoding='utf8')
print('INTERIOR MODELS COMPLETE',flush=True)
