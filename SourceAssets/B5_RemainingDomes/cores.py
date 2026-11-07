"""VB/VL vertical shafts. Static art only. Author 송예찬."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build import *
import build
build.manifest.update(json.loads((H/'models.json').read_text(encoding='utf-8')))
data=json.loads((H/'plan.json').read_text(encoding='utf-8'))
def cylinder_obj(name,r,y0,y1):
 bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=r,depth=y1-y0,location=xyz(0,(y0+y1)/2,0));o=bpy.context.object;o.name=name;return o
def difference(obj,cut):
 bpy.context.view_layer.objects.active=obj;mod=obj.modifiers.new('True_Opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
for code in ['VB','VL']:
 reset();r=data['rooms'][code];shell=cylinder_obj('Shaft',5.22,-.08,19.4);shell.data.materials.append(build.mats['Coat']);difference(shell,cylinder_obj('Void',4.98,-.5,19.1))
 for t in data['tunnels']:
  if code not in (t['a'],t['b']):continue
  other=data['rooms'][t['b'] if t['a']==code else t['a']];f=Vector((other['x']-r['x'],0,-other['v']+r['v'])).normalized();right=Vector((f.z,0,-f.x));prof=[(-2.1,-.3),(2.1,-.3)]+[(2.1*math.cos(i*math.pi/32),1.3+2.1*math.sin(i*math.pi/32)) for i in range(33)];vs=[]
  for dist in [0,7]:
   for x,y in prof:vs.append(tuple(f*dist+right*x+Vector((0,y,0))))
  n=len(prof);fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];difference(shell,mesh('PortalCut',vs,fs,'Dark',0))
 be=shell.modifiers.new('Portal_Edge','BEVEL');be.width=.01;be.segments=3;export(code+'_Shaft',True)
reset()
for x in [-1.53,1.53]:
 for z in [-1.66,1.66]:
  box('Hoist_Steel_Column',x,9.1,z,.16,18.2,.16,'Steel',.012);box('Foundation_Plate',x,.055,z,.34,.11,.34,'Steel',.01)
  for dx in [-.11,.11]:
   for dz in [-.11,.11]:cyl('Anchor_Bolt',(x+dx,.11,z+dz),(x+dx,.15,z+dz),.015,'Steel',8)
for y in [.18,3.2,6.4,9.6,12.8,16.2,18.2]:
 for x in [-1.53,1.53]:box('Horizontal_Girt',x,y,0,.16,.16,3.45,'Steel',.01)
 for z in [-1.66,1.66]:box('Cross_Girt',0,y,z,3.2,.16,.16,'Steel',.01)
# Solid service sides backed by rails; the static cabin is visibly enclosed, not a hollow door.
for x in [-1.46,1.46]:
 box('Hoist_Side_Panel',x,9.10,0,.045,18.0,3.15,'Coat',.008);cyl('Guide_Rail',(x-.05*(1 if x>0 else -1),.1,0),(x-.05*(1 if x>0 else -1),18.1,0),.045,'Steel',16)
box('Hoist_Back',0,9.1,1.60,2.89,18.0,.06,'Coat',.008)
for y in [1.42,17.42]:
 for x in [-1.46,1.46]:box('Lift_Jamb',x,y,-1.68,.15,2.84,.18,'Steel',.012)
 box('Lift_Header',0,y+1.42,-1.68,3.08,.18,.18,'Steel',.014)
 for x in [-.69,.69]:
  box('Closed_Lift_Leaf',x,y,-1.64,1.36,2.69,.075,'Coat',.016);box('Door_Impact_Plate',x,y-.7,-1.685,1.25,.62,.025,'Steel',.009)
 box('Flush_Threshold',0,y-1.38,-1.68,2.76,.035,.40,'Steel',.006)
 for x in [-1.58,1.58]:
  box('Call_Station',x,y,-1.77,.19,.42,.075,'Dark',.011);cyl('Call_Key',(x,y-.06,-1.82),(x,y-.06,-1.84),.027,'Indicator',16)
before_display=set(bpy.data.objects)
display(0,3.08,-1.79,.62,.24,18)
# The lift entry faces -Z, while the shared display constructor faces +Z.
display_pivot=Vector(xyz(0,3.08,-1.79))
display_turn=Matrix.Translation(display_pivot)@Matrix.Rotation(math.pi,4,'Z')@Matrix.Translation(-display_pivot)
for obj in set(bpy.data.objects)-before_display:obj.matrix_world=display_turn@obj.matrix_world
box('Hoist_Closure',0,9.46,-1.65,2.90,12.95,.06,'Coat',.008)
box('Cabin_Floor',0,.04,0,2.78,.08,3.10,'Steel',.012);box('Cabin_Ceiling',0,2.78,0,2.78,.08,3.10,'Coat',.012)
box('Upper_Landing',0,15.92,-2.48,3.08,.16,1.35,'Steel',.01)
for x in [-1.56,1.56]:
 for z in [-1.83,-3.1]:cyl('Upper_Guard_Post',(x,16,z),(x,17.08,z),.025,'Steel',16)
 cyl('Upper_Handrail',(x,17.08,-1.83),(x,17.08,-3.1),.032,'Steel',16)
export('VL_Hoist',True)
reset();cyl('Core_Resin',(0,-.006,0),(0,.01,0),4.94,'Floor',160)
for i in range(12):
 x=-1.35+i*.24;box('Lift_Loading_Stripe',x,.017,-2.15,.11,.006,.42,'Hazard',.001)
export('VL_Floor',True)
print('COMPLETE CORES',flush=True)
