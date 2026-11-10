"""Manufactured roof pipe circuits and maintenance frames; metres, beveled edges."""
import sys,json,math,os
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(R/'SourceAssets/B2_FullFloor'))
from common import *
H=Path(__file__).resolve().parent;R=H.parents[1];b.H=H;b.OUT=b.A/'Environment/B2'
b.manifest=json.loads((H/'models.json').read_text()) if (H/'models.json').exists() else {}
C=json.loads((H/'plan.json').read_text(encoding='utf8'))
def save(n):
 b.OUT=b.A/'Environment/B2';b.raw_export('CD_'+n);b.manifest['CD_'+n]['category']='Environment'
 ob=bpy.context.object;m=ob.modifiers.new('DistanceSimplification','DECIMATE');m.ratio=.36;m.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=m.name);ob.name='CD_'+n+'_Far'
 bpy.ops.export_scene.fbx(filepath=str(b.OUT/(ob.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE')
 b.manifest[ob.name]={'triangles':len(ob.data.polygons),'category':'Environment','distance_only':True}
 (H/'models.json').write_text(json.dumps(b.manifest,indent=2),encoding='utf8')
def swept(n,pts,r,mat='Pipe',sides=16):
 pts=[Vector(p) for p in pts];vs=[];fs=[]
 for i,p in enumerate(pts):
  tangent=(pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized();basis=Vector((1,0,0)) if abs(tangent.x)<.8 else Vector((0,0,1));a=tangent.cross(basis).normalized();bb=tangent.cross(a).normalized()
  for j in range(sides):vs.append(tuple(p+r*(math.cos(math.tau*j/sides)*a+math.sin(math.tau*j/sides)*bb)))
 for i in range(len(pts)-1):
  for j in range(sides):k=i*sides+j;kk=i*sides+(j+1)%sides;fs.append((k,kk,kk+sides,k+sides))
 fs.extend([tuple(range(sides-1,-1,-1)),tuple(range((len(pts)-1)*sides,len(pts)*sides))])
 ob=mesh(n,vs,fs,mat,0)
 for f in ob.data.polygons:f.use_smooth=len(f.vertices)==4
 return ob
def anchor(x,y,z,r):
 top=math.sqrt(max(.1,r*r-x*x-z*z))-.12
 cyl('ThreadedHanger',(x,y,z),(x,top,z),.018,'Steel',10)
 box('RoofAnchor',x,top,z,.20,.045,.20,'Steel',.004)
 for dx in [-.062,.062]:cyl('AnchorNut',(x+dx,top-.04,z),(x+dx,top,z),.012,'Steel',6)
def angled_flange(x,y,z,radius,tangent):
 old=set(bpy.context.scene.objects);flange(0,0,0,r=radius,axis='z')
 direction=Vector(xyz(*tangent)).normalized();rot=Vector((0,-1,0)).rotation_difference(direction).to_matrix().to_4x4()
 mat=Matrix.Translation(Vector(xyz(x,y,z)))@rot
 for ob in set(bpy.context.scene.objects)-old:ob.matrix_world=mat@ob.matrix_world
def tray(x,y,z0,z1):
 for dx in [-.25,.25]:box('TrayEdge',x+dx,y,(z0+z1)/2,.032,.14,z1-z0,'Steel',.003)
 for i in range(math.ceil((z1-z0)/.32)+1):
  z=z0+(z1-z0)*i/max(1,math.ceil((z1-z0)/.32));box('TrayRung',x,y-.04,z,.52,.035,.04,'Steel',.002)
 for dx in [-.14,-.07,0,.07,.14]:swept('PowerCable',[(x+dx,y+.02,z0),(x+dx,y+.02,z1)],.024,'Rubber',8)
def ibeam(x,y,z,length,axis='z',height=.24,width=.18):
 dims=(width,height,length) if axis=='z' else (length,height,width)
 box('BeamWeb',x,y,z,.035 if axis=='z' else length,height,length if axis=='z' else .035,'Steel',.003)
 for sign in [-1,1]:box('BeamFlange',x,y+sign*(height/2-.018),z,dims[0],.036,dims[2],'Steel',.004)
def column(x,z,h):
 box('ColumnWeb',x,h/2,z,.055,h,.20,'Steel',.004)
 for dz in [-.12,.12]:box('ColumnFlange',x,h/2,z+dz,.22,h,.04,'Steel',.004)
 box('Baseplate',x,.04,z,.38,.08,.40,'Steel',.008)
 for dx in [-.13,.13]:
  for dz in [-.14,.14]:cyl('AnchorBolt',(x+dx,.08,z+dz),(x+dx,.14,z+dz),.018,'Steel',6)
def ceiling(room):
 reset();rid=room['id'];r=room['r'];wet=C['services'][rid]['kind'] in ['cooling','separation','water','waste','fuel'];air=C['services'][rid]['kind']=='air'
 extent=r*(.51 if rid in C['decks'] else .62);xx=r*.24;rad=.30 if wet else .34 if air else .14
 def roof(x,z,clear=.8):return math.sqrt(max(.1,r*r-x*x-z*z))-clear
 # Four main lengths, larger pipes on wet/air circuits, plus small instrument lines.
 for side in [-1,1]:
  for j,(radius,mat) in enumerate([(rad,'Pipe'),(.09,'PipeRed'),(.045,'Pipe')]):
   x=side*xx+side*j*(rad+.13);pts=[(x,roof(x,-extent+2*extent*i/32),-extent+2*extent*i/32) for i in range(33)]
   swept('InsulatedMain' if j==0 else 'InstrumentService',pts,radius,mat,24 if j==0 else 12)
   for z in [-extent*.72,0,extent*.72]:angled_flange(x,roof(x,z),z,radius,(0,-z/math.sqrt(r*r-x*x-z*z),1))
   # Continuous return cross-header joins the matching main on the opposite side.
   if side==1:
    for z in [-extent,extent]:
     cross=[(-x+2*x*i/24,roof(-x+2*x*i/24,z),z) for i in range(25)]
     swept('CircuitCrossHeader',cross,radius,mat,20 if j==0 else 12)
  # Roof-anchored cross channels and clamps. Never free-floating supports.
  for z in [-extent*.75,-extent*.25,extent*.25,extent*.75]:
   y=roof(side*xx,z)-rad-.14;box('PipeCarrier',side*(xx+.30),y,z,1.8,.10,.13,'Steel',.004)
   for j,radius in enumerate([rad,.09,.045]):
    x=side*xx+side*j*(rad+.13);bottom=roof(x,z)-radius
    if bottom>y+.075:box('SaddleStem',x,(bottom+y+.05)/2,z,.065,bottom-y-.05,.085,'Steel',.003)
   for x in [side*(xx-.5),side*(xx+1.1)]:anchor(x,y,z,r)
 # Cable tray longitudinal route, below the crown and clear of floor activities.
 tx=-.09*r;ty=roof(tx,extent*.85)-.42;tray(tx,ty,-extent*.85,extent*.85)
 for z in [-extent*.7,0,extent*.7]:
  for dx in [-.28,.28]:anchor(tx+dx,ty-.08,z,r)
 # Structural ribs/services at intermediate elevations visibly tie plant to roof.
 if wet:
  hx={'C01':3,'C02':2.5,'W02':3,'E01':2.5,'E03':2}[rid]
  for side in [-1,1]:
   x=side*xx;z=0;top=roof(x,z)
   tube('HeaderRiser',[(side*hx,5.6,z),(x,5.6,z),(x,top,z)],.15,'Pipe')
   flange(side*hx,5.6,z,.15,'y');flange(x,top-.4,z,.15,'y')
 elif air:
  for side in [-1,1]:
   x=side*xx;z=0;top=roof(x,z)
   lowerx=2 if rid=='E02' else side*3
   tube('VentilationRiser',[(lowerx,5.4,z),(x,5.4,z),(x,top,z)],.32,'Pipe')
   for y in [5.9,top-.4]:flange(x,y,z,.32,'y')
 else:
  lower={'C03':(-3.2,3.8,0),'C04':(0,3.4,-4.6),'W01':(0,4.3,-4.9),'S01':(0,4.2,-6),'W03':(0,3.3,0)}[rid]
  for k in range(4):tube('TrayFeeder',[(tx+k*.04,ty,0),(tx+k*.04,ty-.25,0),(lower[0]+k*.04,lower[1],lower[2])],.022,'Rubber')
 save(rid+'_CeilingServices')
for room in C['rooms']:
 if os.environ.get('CD_ROOM') and os.environ['CD_ROOM']!=room['id']:continue
 ceiling(room)
if not os.environ.get('CD_ROOM'):
 reset()
 # Two framed motor work bays, centre aisle unobstructed; hoists stay above head height.
 for x in [-3,3]:
  for xx in [x-1.25,x+1.25]:
   for z in [-3.75,1.1]:column(xx,z,3.55)
   ibeam(xx,3.55,-1.325,5.08)
  for z in [-3.75,1.1]:ibeam(x,3.55,z,2.7,'x')
  ibeam(x,3.47,-1.325,4.85)
  for z in [-2.8,0]:
   box('HoistTrolley',x,3.3,z,.40,.22,.34,'Dark',.018)
   cyl('ChainMotor',(x-.26,3.2,z),(x+.26,3.2,z),.14,'Coat',20)
   for dx in [-.065,.065]:swept('HoistChain',[(x+dx,3.15,z),(x+dx,2.45,z)],.014,'Dark',8)
   tube('LiftingHook',[(x-.065,2.45,z),(x-.065,2.3,z),(x+.08,2.3,z),(x+.11,2.40,z)],.025,'Steel')
  tray(x,3.84,-3.75,1.1)
  for xx in [x-1.25,x+1.25]:tube('FramePowerConduit',[(xx,.25,-3.75),(xx,3.8,-3.75),(x,3.8,-3.75)],.025,'Dark')
 save('S01_MaintenanceGantry')
 reset()
 for x in [-3.5,4.35]:
  for z in [-3.95,-1.2]:column(x,z,3.95)
  ibeam(x,3.95,-2.575,3.0)
 for z in [-3.95,-1.2]:ibeam(.425,3.95,z,8.05,'x')
 # Tank-top vent collector with short individual branches and bolted isolation points.
 for x in [-2,.5,3]:
  tube('TankVentBranch',[(x,2.75,-2.6),(x,4.30,-2.6),(x,4.30,-3.95)],.13,'Pipe')
  flange(x,3.25,-2.6,.13,'y')
 tube('WasteVentCollector',[(-3.3,4.3,-3.95),(3.5,4.3,-3.95),(3.5,5.6,-3.95),(2,5.6,-3.95)],.20,'Pipe')
 for x in [-2,.5,3]:box('VentPipeSaddle',x,4.05,-3.95,.30,.14,.32,'Steel',.006)
 save('E03_WetProcessGantry')
