"""Abandoned camouflage factory: altered shell, broken glazing, roof damage and derelict process structures."""
import sys,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
p=json.loads((H/'site.json').read_text(encoding='utf8'));rng=random.Random(120612)

def panel(n,pts,th,mat):
 k=len(pts);vs=pts+[(x,y-th,z) for x,y,z in pts];fs=[tuple(range(k)),tuple(range(2*k-1,k-1,-1))]+[(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)];return mesh(n,vs,fs,mat)

def wall(q):
 a,b=q['a'],q['b'];length=math.dist(a,b);yaw=-math.degrees(math.atan2(b[1]-a[1],b[0]-a[0]));x,z=(a[0]+b[0])/2,(a[1]+b[1])/2;h={'C01':9,'C02':7.3}.get(q['room'],q['h']);th=q['th'];start=set(bpy.context.scene.objects)
 window=q['window'] or (q['room'].startswith('T') and length>5)
 if window and length>2.8:
  sill=1.65 if h>6 else 1.15;wh=h-sill-.65;w=length-1.1
  box('SpalledLowerWall',(0,sill/2,0),(length,sill,th),'Plaster',0);box('WeatheredLintel',(0,h-.325,0),(length,.65,th),'Plaster',0)
  for side in [-1,1]:box('BrickEndPier',(side*(length/2-.275),sill+wh/2,0),(.55,wh,th),'Plaster',0)
  cols=max(2,round(w/.72));rows=max(2,round(wh/.65));cw=w/cols;rh=wh/rows
  for i in range(cols+1):box('RustedMullion',(-w/2+i*cw,sill+wh/2,0),(.042,wh+.06,th+.02),'Corrosion',0)
  for j in range(rows+1):box('RustedTransom',(0,sill+j*rh,0),(w-.044,.035,th+.025),'Corrosion',0)
  for i in range(cols):
   for j in range(rows):
    xx=-w/2+i*cw+.027;yy=sill+j*rh+.025;cw2=cw-.055;rh2=rh-.05;v=rng.random()
    if v<.15:box('DustyRemainingPane',(xx+cw2/2,yy+rh2/2,0),(cw2,rh2,.009),'Glass',0)
    elif v<.48:
     # Broken triangular edge, not an opaque rectangle over the opening.
     pts=[(xx,yy,0),(xx+cw2*rng.uniform(.4,.85),yy,0),(xx+cw2*.13,yy+rh2*rng.uniform(.35,.9),0)]
     mesh('GlassShard',pts,[(0,1,2)],'Glass')
  for zz in [-1,1]:box('ChippedWindowSill',(0,sill-.035,zz*(th/2+.045)),(length-.7,.10,.13),'Concrete',0)
 else:box('WeatheredMasonry',(0,h/2,0),(length,h,th),'Plaster',0)
 # Irregular exposed foundations remain clear of the wall surface, avoiding coplanar paint overlays.
 for side in [-1,1]:
  for i in range(max(1,int(length/3))):
   xx=-length/2+(i+.5)*length/max(1,int(length/3));ww=rng.uniform(.55,1.8);hh=rng.uniform(.08,.23)
   box('CrumblingFooting',(xx,hh/2,side*(th/2+.055)),(ww,hh,.10),'Concrete',0,yaw=rng.uniform(-3,3))
 turn(set(bpy.context.scene.objects)-start,x,0,z,yaw)

reset();vs=[];fs=[]
for tri in p['floorTriangles']:
 k=len(vs);vs.extend((x,0,z) for x,z in tri);fs.append((k+2,k+1,k))
mesh('InteriorFloor',vs,fs,'Concrete');save('InteriorFloor','Environment',False)

for r in p['rooms']+p['tunnels']:
 id=r['id'];reset()
 for q in p['walls']:
  if q['room']==id:wall(q)
 if 'doors' in r:
  x,z,w,d=[r[k] for k in ['x','z','w','d']];h={'C01':9,'C02':7.3}.get(id,r['h'])
  for door in r['doors']:
   dx,_,dz=door['point'];vertical=abs(abs(dx-x)-w/2)<.05
   if h>3.4:box('PortalHeader',(dx,(h+3.4)/2,dz),(.24,h-3.4,4.6) if vertical else (4.6,h-3.4,.24),'Plaster',0)
 save(id+'_Walls','Environment',False)

for r in p['rooms']:
 id=r['id'];x,z,w,d=[r[k] for k in ['x','z','w','d']];h={'C01':9,'C02':7.3}.get(id,r['h']);reset()
 if id in ['C01','C02']:
  rise=2.35 if id=='C01' else 1.8
  for zz in [z-d/2+.3,z-d/4,z,z+d/4,z+d/2-.3]:
   for xx in [x-w/2+.25,x+w/2-.25]:
    box('RustedColumn',(xx,h/2,zz),(.15,h,.34),'Corrosion',0)
    for side in [-1,1]:box('ColumnFlange',(xx+side*.13,h/2,zz),(.055,h,.35),'Corrosion',0)
   beam('BottomChord',(x-w/2,h,zz),(x+w/2,h,zz),.15,'Corrosion')
   beam('RafterWest',(x-w/2,h,zz),(x,h+rise,zz),.16,'Corrosion');beam('RafterEast',(x,h+rise,zz),(x+w/2,h,zz),.16,'Corrosion')
   for j in range(12):
    a=x-w/2+j*w/12;b=a+w/12;yy=h+rise*(1-abs((a+b)/2-x)/(w/2));beam('ZigZagTruss',(a,h,zz),((a+b)/2,yy,zz),.06,'Corrosion');beam('ZigZagTruss',((a+b)/2,yy,zz),(b,h,zz),.06,'Corrosion')
  for xx in [-.38,-.18,0,.18,.38]:beam('Purlin',(x+xx*w,h+rise*(1-abs(xx)*2),z-d/2),(x+xx*w,h+rise*(1-abs(xx)*2),z+d/2),.1,'Corrosion')
  # Dark disconnected lamp shells, cables sagging below the truss.
  for xx in [-w*.25,w*.25]:
   for zz in [-d*.28,0,d*.28]:
    beam('DeadPendantCable',(x+xx,h-.1,z+zz),(x+xx+.13,h-1.1,z+zz+.05),.018,'Dark',False)
    bpy.ops.mesh.primitive_cone_add(vertices=20,radius1=.31,radius2=.09,depth=.22,location=xyz(x+xx+.13,h-1.22,z+zz+.05));finish(bpy.context.object,'UnpoweredLamp','Corrosion')
  save(id+'_Frames','Environment',False);reset()
  nx=12 if id=='C01' else 10;nz=10 if id=='C01' else 8;dx=w/nx;dz=d/nz
  for i in range(nx):
   for j in range(nz):
    # A broad collapsed bay and broken central ridge expose sky and truss.
    if (id=='C01' and i>=8 and j<4) or (id=='C02' and i<3 and j>4) or (i in [nx//2-1,nx//2] and j%3!=0) or rng.random()<.09:continue
    x0=x-w/2+i*dx;x1=x0+dx-.025;z0=z-d/2+j*dz;z1=z0+dz-.025
    y0=h+rise*(1-abs(x0-x)/(w/2))+.13;y1=h+rise*(1-abs(x1-x)/(w/2))+.13
    panel('CorrodedRoofSheet',[(x0,y0,z0),(x1,y1,z0),(x1,y1,z1),(x0,y0,z1)],.035,'Corrosion')
    for k in range(1,5):
     xx=x0+(x1-x0)*k/5;yy=h+rise*(1-abs(xx-x)/(w/2))+.155;beam('Corrugation',(xx,yy,z0),(xx,yy,z1),.035,'Corrosion')
  for zz in [z-d/2,z+d/2]:
   mesh('AgedGable',[(x-w/2,h,zz),(x+w/2,h,zz),(x,h+rise,zz)],[(0,1,2)],'Plaster')
 else:
  # Damaged low annex roofs, intact small concealed access cores.
  n=4;dx=w/n;dz=d/n
  for i in range(n):
   for j in range(n):
    if id.startswith('C') and ((i==0 and j==2) or (i==2 and j==1)):continue
    box('SpalledRoof',(x-w/2+(i+.5)*dx,h+.09,z-d/2+(j+.5)*dz),(dx-.02,.18,dz-.02),'Concrete',0)
  for xx in [x-w/2,x+w/2]:box('RoofKerb',(xx,h+.28,z),(.14,.25,d),'Concrete',0)
 save(id+'_Roof','Environment',False)

# The original hall roofs are replaced by slotted, damaged light-admitting covers.
old=json.loads((H/'before_layout.json').read_text(encoding='utf8'))
orig=json.loads((H.parent/'F1_FullFloor/plan.json').read_text(encoding='utf8'))
for t in p['tunnels']:
 reset()
 for q in orig['corridorRoofs']:
  if q['room']!=t['id']:continue
  pts=q['points'];cx=sum(a for a,b in pts)/len(pts);cz=sum(b for a,b in pts)/len(pts)
  # Two perimeter strips and exposed beams; a continuous skylight keeps these former service links legible.
  for i in range(len(pts)):
   a,b=pts[i],pts[(i+1)%len(pts)];beam('RustRoofEdge',(a[0],3.5,a[1]),(b[0],3.5,b[1]),.10,'Corrosion')
  shrink=[(cx+(a-cx)*.50,cz+(b-cz)*.50) for a,b in pts]
  for i in range(len(pts)):
   j=(i+1)%len(pts);panel('BrokenHallCover',[(pts[i][0],3.56,pts[i][1]),(pts[j][0],3.56,pts[j][1]),(shrink[j][0],3.56,shrink[j][1]),(shrink[i][0],3.56,shrink[i][1])],.04,'Corrosion')
 save(t['id']+'_Roof','Environment',False)

# Walkable former maintenance deck on the west side of production.
reset();box('CatwalkDeck',(-24.65,3.4,3.7),(1.25,.13,15.4),'Corrosion',0)
for z in [-3.9,-1,2,5,8,11.3]:
 for x in [-25.27,-24.03]:beam('RailingPost',(x,3.47,z),(x,4.45,z),.045,'Corrosion')
 beam('DeckBracket',(-25.8,2.65,z),(-24.05,3.31,z),.075,'Corrosion')
for x in [-25.27,-24.03]:
 for y in [3.94,4.45]:beam('CatwalkRail',(x,y,-3.9),(x,y,11.35),.045,'Corrosion')
for i in range(20):box('StairTread',(-24.65,(i+1)*.17-.04,-10.1+(i+.5)*.31),(1.25,.08,.30),'Corrosion',0)
for x in [-25.24,-24.06]:
 beam('StairStringer',(x,.04,-10.1),(x,3.34,-3.9),.11,'Corrosion')
 beam('StairHandrail',(x,1.05,-10.1),(x,4.45,-3.9),.045,'Corrosion')
 for i in range(0,21,4):beam('StairPost',(x,i*.17,-10.1+i*.31),(x,i*.17+1.05,-10.1+i*.31),.04,'Corrosion')
for z in [-10,-4,4,10]:
 beam('DisconnectedServicePipe',(-25.55,.25,z),(-25.55,7.4,z),.19,'Corrosion',False)
for y in [5,5.5,6.0]:beam('HighPipe',(-25.55,y,-12.9),(-25.55,y,12.9),.2,'Corrosion',False)
save('C01_CatwalkPipes','Environment',False)

# A disused stack, silos and a partial adjacent industrial shell anchor the exterior silhouette.
reset();cx,cz=-31,9
cyl('BrickStack',(cx,10,cz),1.25,20,'Plaster',verts=28);cyl('StackRim',(cx,20.03,cz),1.38,.24,'Corrosion',verts=28)
cyl('StackDarkMouth',(cx,20.16,cz),1.13,.015,'Dark',verts=28)
box('StackPlinth',(cx,.75,cz),(3.4,1.5,3.4),'Concrete',0)
for y in [2,5,8,11,14,17,19]:
 bpy.ops.mesh.primitive_torus_add(major_segments=28,minor_segments=6,location=xyz(cx,y,cz),major_radius=1.28,minor_radius=.045);finish(bpy.context.object,'StackBand','Corrosion')
for x in [cx-.28,cx+.28]:beam('StackLadder',(x,.5,cz-1.34),(x,19.7,cz-1.34),.035,'Corrosion')
for i in range(62):beam('LadderRung',(cx-.28,.7+i*.30,cz-1.34),(cx+.28,.7+i*.30,cz-1.34),.024,'Corrosion')
for x,z in [(9,22),(16,24)]:
 cyl('RustedSilo',(x,5,z),2.1,7,'Corrosion',verts=24)
 bpy.ops.mesh.primitive_cone_add(vertices=24,radius1=.38,radius2=2.1,depth=2.4,location=xyz(x,.9,z));finish(bpy.context.object,'Hopper','Corrosion')
 for xx in [-1.6,1.6]:
  for zz in [-1.6,1.6]:beam('SiloLeg',(x+xx,-.1,z+zz),(x+xx,5,z+zz),.14,'Corrosion')
 cyl('TopLid',(x,8.58,z),2.17,.15,'Corrosion',verts=24)
 for y in [3,5,7]:
  bpy.ops.mesh.primitive_torus_add(major_segments=24,minor_segments=6,location=xyz(x,y,z),major_radius=2.12,minor_radius=.045);finish(bpy.context.object,'SiloHoop','Rust')
beam('ProcessDuct',(9,7,22),(9,7,4),.46,'Corrosion',False);beam('ProcessDuct',(9,7,4),(1.7,7,4),.46,'Corrosion',False)
# A derelict annex beyond the main route: exposed columns, broken roof bays and open window frames.
for x in [-26,-18,-10,-2]:
 for z in [42,54]:box('AnnexColumn',(x,3.6,z),(.45,7.2,.45),'Plaster',0)
 beam('AnnexCrossbeam',(x,7.2,42),(x,8.8,48),.16,'Corrosion');beam('AnnexCrossbeam',(x,8.8,48),(x,7.2,54),.16,'Corrosion')
for z in [42,54]:
 box('AnnexLowWall',(-14,1,z),(24,2,.3),'Plaster',0)
 beam('AnnexLintel',(-26,7.1,z),(-2,7.1,z),.24,'Corrosion')
 for x in range(-25,-2):
  beam('AnnexMullion',(x,2,z),(x,7,z),.045,'Corrosion')
 for y in [3,4,5,6]:beam('AnnexTransom',(-26,y,z),(-2,y,z),.045,'Corrosion')
for x0,x1 in [(-26,-18),(-10,-2)]:panel('AnnexRoof',[(x0,7.3,42),(x1,7.3,42),(x1,8.9,48),(x0,8.9,48)],.04,'Corrosion')
save('ExteriorProcessRuins','Environment',False)
print('Abandoned shell complete',len(manifest),flush=True)
