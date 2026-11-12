import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
p=json.loads((H/'plan.json').read_text(encoding='utf8'))
def slab(n,points,y,th=.14,mat='Coat'):
 vs=[(x,yy,z) for yy in [y-th,y] for x,z in points];k=len(points);fs=[tuple(range(k-1,-1,-1)),tuple(range(k,2*k))]+[(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)];return mesh(n,vs,fs,mat)
def wallsegment(q):
 a,b=q['a'],q['b'];dx=b[0]-a[0];dz=b[1]-a[1];length=math.hypot(dx,dz);yaw=-math.degrees(math.atan2(dz,dx));x=(a[0]+b[0])/2;z=(a[1]+b[1])/2;h=q['h'];th=q['th'];start=set(bpy.context.scene.objects)
 if q['window']:
  sill=3 if q['room']=='C01' else 2.45 if q['room']=='C02' else 1.25;wh=1.5 if h>5 else 1.2
  box('LowerMasonry',(0,sill/2,0),(length,sill,th),'Coat',0);box('HeaderWall',(0,(sill+wh+h)/2,0),(length,h-sill-wh,th),'Coat',0)
  for xx in [-length/2+.4,length/2-.4]:box('WindowEndPier',(xx,sill+wh/2,0),(.8,wh,th),'Coat',0)
  w=length-.8
  for yy in [sill+.025,sill+wh-.025]:box('WindowRail',(0,yy,0),(w,.06,th+.08),'Steel',.002)
  count=max(2,round(w/1.25))
  for i in range(count+1):box('Mullion',(-w/2+i*w/count,sill+wh/2,0),(.05,wh,th+.025),'Steel',.001)
  # Transparent panes occupy the opening, separate from all opaque wall planes.
  for i in range(count):box('WindowGlass',(-w/2+(i+.5)*w/count,sill+wh/2,0),(w/count-.055,wh-.07,.012),'Glass',0)
 else:box('Masonry',(0,h/2,0),(length,h,th),'Coat',0)
 # Lower faded paint, wall base, service pipe remain outside the masonry faces.
 for zz in [-th/2-.007,th/2+.007]:
  box('PaintDado',(0,.52,zz),(length,1.04,.008),'Green',0);box('Skirting',(0,.08,zz*1.08),(length,.16,.025),'Dark',0)
 turn(set(bpy.context.scene.objects)-start,x,0,z,yaw)

reset()
# Constrained triangles exactly tile the floor union; no overlapping corridor/room floor plates.
vv=[];ff=[]
for tri in p['floorTriangles']:
 k=len(vv);vv.extend((x,0,z) for x,z in tri);ff.append((k+2,k+1,k))
mesh('ContinuousFloor',vv,ff,'Floor');save('GroundFloor','Environment',False)
for room in p['rooms']:
 id=room['id'];x,z,w,d,h=[room[k] for k in ['x','z','w','d','h']];reset()
 for q in p['walls']:
  if q['room']==id:wallsegment(q)
 # Portal headers close the space above each 3.4m opening, without blocking the route.
 for door in room['doors']:
  dx,_,dz=door['point'];vertical=abs(abs(dx-x)-w/2)<.05;span=4.6
  if h>3.4:box('PortalHeader',(dx,(h+3.4)/2,dz),(.24,h-3.4,span) if vertical else (span,h-3.4,.24),'Coat',0)
 save(id+'_Walls','Environment',False)
 reset()
 # Steel columns and pitched trusses read as a former production building.
 for xx in [-w/2+.2,w/2-.2]:
  for zz in [-d/2+.2,0,d/2-.2]:
   box('ColumnWeb',(x+xx,h/2,z+zz),(.1,h,.3),'Steel',.002)
   for side in [-.16,.16]:box('ColumnFlange',(x+xx+side,h/2,z+zz),(.045,h,.32),'Steel',.002)
 if id in ['C01','C02']:
  rise=1.8;count=5 if id=='C01' else 4
  for i in range(count):
   zz=z-d/2+.3+i*(d-.6)/(count-1);a=(x-w/2,h,zz);b=(x,h+rise,zz);c=(x+w/2,h,zz);beam('TrussChord',a,c,.14);beam('Rafter',a,b,.16);beam('Rafter',b,c,.16)
   for j in range(8):
    xx=x-w/2+j*w/8;xx2=xx+w/8;yy=h+rise*(1-abs(xx2-x)/(w/2));beam('TrussWeb',(xx,h,zz),(xx2,yy,zz),.065)
  for xx in [-w*.32,0,w*.32]:beam('Purlin',(x+xx,h+rise*(1-abs(xx)/(w/2)),z-d/2),(x+xx,h+rise*(1-abs(xx)/(w/2)),z+d/2),.12)
 else:
  for zz in [-d*.25,d*.25]:beam('RoofBeam',(x-w/2,h-.15,z+zz),(x+w/2,h-.15,z+zz),.12)
 # High services keep walking routes and working surfaces clear.
 for zz in [-d/2+.35,d/2-.35]:
  beam('CableTray',(x-w/2+.4,h-.5,z+zz),(x+w/2-.4,h-.5,z+zz),.08,'Dark')
 if id=='C04':
  box('OfficeBreakPartition',(x+1.6,1.2,z+4.4),(.14,2.4,5),'Green',.008);box('PartitionUpperGlass',(x+1.6,2.9,z+4.4),(.025,1,5),'Glass',0)
 save(id+'_Frames','Environment',False)
 reset()
 if id in ['C01','C02']:
  # Two closed sloped roof panels; geometry thickness points downward.
  rise=1.8
  for side in [-1,1]:
   pts=[(x,h+rise,z-d/2-.35),(x+side*(w/2+.35),h-.04,z-d/2-.35),(x+side*(w/2+.35),h-.04,z+d/2+.35),(x,h+rise,z+d/2+.35)]
   vs=pts+[(xx,yy-.14,zz) for xx,yy,zz in pts];mesh('RoofPanel',vs,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'Green')
  for zz in [-d/2,d/2]:mesh('Gable',[(x-w/2,h,z+zz),(x+w/2,h,z+zz),(x,h+rise,z+zz)],[(0,1,2)],'Coat')
 else:slab('FlatRoof',[(x-w/2-.2,z-d/2-.2),(x+w/2+.2,z-d/2-.2),(x+w/2+.2,z+d/2+.2),(x-w/2-.2,z+d/2+.2)],h+.15,.15,'Green')
 save(id+'_Roof','Environment',False)

for t in p['tunnels']:
 id=t['id'];reset()
 for q in p['walls']:
  if q['room']==id:wallsegment(q)
 save(id+'_Walls','Environment',False)
 reset()
 for q in p['corridorRoofs']:
  if q['room']==id:slab('ServiceHallRoof',q['points'],q['h']+.15,.15,'Green')
 save(id+'_Roof','Environment',False)

reset()
# Low boundary with open sight lines; gateway and road continue west, away from the facility.
for zz in [-39,-17]:
 for x in range(-68,-47,4):
  box('FencePost',(x,1.3,zz),(.07,2.6,.07),'Steel',.004)
 for y in [.4,1.3,2.4]:beam('FenceRail',(-68,y,zz),(-48,y,zz),.028,'Steel')
 for x in range(81):beam('FenceWire',(-68+x*.25,.1,zz),(-68+x*.25,2.5,zz),.009,'Steel')
box('ExteriorRoad',(-84,-.08,-28),(32,.16,11),'Floor',0)
for zz in [-33.4,-22.6]:box('RoadEdge',(-84,.005,zz),(32,.008,.12),'Paper',0)
for x in range(-97,-69,5):box('RoadDash',(x,.005,-28),(2.6,.008,.1),'Hazard',0)
# Background parcels are outside the accessible yard; no new mandatory route or puzzle.
for x,z,w,d,h in [(-30,48,24,14,5),(62,0,16,22,7),(-11,-49,30,11,6)]:
 box('AdjacentFactory',(x,h/2,z),(w,h,d),'Coat',0);box('FactoryRoof',(x,h+.12,z),(w+.5,.24,d+.5),'Green',0)
 for i in range(1,int(w/2)):
  for side in [-1,1]:box('BackgroundWindow',(x-w/2+i*2,3,z+side*(d/2+.006)),(1.4,1,.008),'Dark',0)
save('Yard','Environment',False)

reset()
# Painted work-cell corners and traffic guidance, raised 8mm to avoid depth fighting.
for room in p['rooms']:
 if room['id'] not in ['C01','C02']:continue
 x,z=room['x'],room['z']
 for xx in [-2.5,2.5]:
  for zz in [-4.7,4.7]:box('WorkCellStripe',(x+xx,.008,z+zz),(.10,.004,1.4),'Hazard',0)
 for xx in [-7,7]:box('TrafficLane',(x+xx,.008,z),( .08,.004,room['d']-3),'Paper',0)
save('FloorMarkings','Environment',False)
