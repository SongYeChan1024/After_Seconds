"""Dome panels and continuous services, corridor finish. Author 송예찬."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build import *
import build
build.manifest.update(json.loads((H/'models.json').read_text(encoding='utf-8')))
data=json.loads((H/'plan.json').read_text(encoding='utf-8'));manifest={}
def allowed(a,room,margin=0):
 return all(abs((a-d['angle']+180)%360-180)>math.degrees(math.asin(min(1,(2.65+margin)/room['r']))) for d in room['doors'])
for code in [k for k in data['construction'] if k not in ['VB','VL']]:
 room=data['rooms'][code];rad=room['r'];reset();bands=[.012,.17,.34,.52,.74,.98,1.23,1.48,1.565]
 for sector in range(36):
  a=sector*10+5
  for j in range(len(bands)-1):
   if rad*math.sin(bands[j])<3.55 and not allowed(a,room,.65):continue
   sphere_patch('Dome_Panel',math.radians(sector*10+.10),math.radians((sector+1)*10-.10),bands[j]+.001,bands[j+1]-.001,rad-.038,rad-.018,'Coat',4,3)
 for a in range(0,360,45):
  start=.008 if allowed(a,room,.45) else math.asin(min(1,3.60/rad))
  sphere_patch('Continuous_Structural_Rib',math.radians(a-.38),math.radians(a+.38),start,1.46,rad-.13,rad-.06,'Steel',2,32)
 for height in [3.65,rad*.88]:
  phi=math.asin(height/rad);sphere_patch('Horizontal_Ring',0,math.tau,phi-.007,phi+.007,rad-.13,rad-.06,'Steel',144,2)
 export(code+'_Architecture',True)
 reset();cyl('Epoxy_Floor',(0,-.006,0),(0,.008,0),rad-.12,'Floor',160)
 # Flush perimeter cove; metal access hatches stay outside the main circulation area.
 for a in range(0,360,45):
  if not allowed(a,room,.75):continue
  t=math.radians(a);x,z=(rad-1.1)*math.cos(t),(rad-1.1)*math.sin(t);box('Service_Hatch',x,.015,z,.55,.012,.55,'Steel',.008);box('Recessed_Pull',x,.023,z+.19,.17,.002,.025,'Dark',0)
 export(code+'_Floor',True)
 reset()
 # Conduits are continuous at a height above every door; supported from the spherical wall.
 height=3.80;ringrad=math.sqrt(rad*rad-height*height)-.18
 for off,mat in [(-.065,'Teal'),(.065,'Steel')]:
  pts=[(ringrad*math.cos(i*math.tau/96),height+off,ringrad*math.sin(i*math.tau/96)) for i in range(97)];tube('Supply_Return_Ring',pts,.032,mat)
 for a in range(0,360,30):
  t=math.radians(a);x,z=ringrad*math.cos(t),ringrad*math.sin(t);outer=math.sqrt(rad*rad-height*height)
  cyl('Conduit_Wall_Bracket',(x,height,z),(outer*math.cos(t),height,outer*math.sin(t)),.022,'Steel',12)
  if not allowed(a,room,.65):continue
  lower=math.sqrt(rad*rad-2.55**2)-.12;pt=(lower*math.cos(t),2.55,lower*math.sin(t));tube('Branch_Conduit',[(x,height,z),(x,2.75,z),pt],.023,'Steel')
  # Wall-mounted ventilation grilles with closed plenum and edge depth.
  objs=set(bpy.context.scene.objects);vent(0,2.58,0,.65,.24);box('Vent_Plenum',0,2.58,-.04,.69,.28,.10,'Dark',.01)
  yaw=math.atan2(-pt[0],-pt[2]);m=Matrix.Translation(Vector(xyz(pt[0],0,pt[2])))@Matrix.Rotation(-yaw,4,'Z')
  for o in set(bpy.context.scene.objects)-objs:o.matrix_world=m@o.matrix_world
 export(code+'_Services',True)
 # Preserve global manifest as build.export stores in its defining module.
import build
(H/'architecture_models.json').write_text(json.dumps(build.manifest,indent=2),encoding='utf-8')
# Corridor geometry: one seamless authored model per tunnel, same dimensional family as T02.
for tun in data['tunnels'][2:]:
 code=tun['id'].replace('B5-','');L=math.dist(tun['p'],tun['q']);reset();count=math.ceil((L-1.2)/2.2)
 # Import the existing arc-panel function only; never run its older scene application.
 tree=ast.parse((R/'SourceAssets/T02_StairA/build.py').read_text(encoding='utf-8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='curved'],type_ignores=[]),'arc','exec'))
 for i in range(count):
  z0=.6+i*(L-1.2)/count+.008;z1=.6+(i+1)*(L-1.2)/count-.008
  for j in range(6):curved('Arch_Panel',z0,z1,j*math.pi/6+.003,(j+1)*math.pi/6-.003)
  for s in [-1,1]:
   box('Lower_Panel',s*2.062,.72,(z0+z1)/2,.036,1.12,z1-z0,'Coat',.005);box('Cart_Rail',s*1.98,.94,(z0+z1)/2,.12,.105,z1-z0-.035,'Steel',.012);box('Rubber_Edge',s*1.915,.94,(z0+z1)/2,.018,.06,z1-z0-.09,'Dark',.006);box('Kick',s*2.035,.12,(z0+z1)/2,.044,.19,z1-z0,'Steel',.004)
 box('Resin_Floor',0,.003,L/2,4.04,.014,L-.6,'Floor',.002)
 for s in [-1,1]:
  box('Drain_Back',s*1.84,.012,L/2,.10,.008,L-.9,'Dark',.001)
  for z in [i*.22+.6 for i in range(int((L-1.2)/.22))]:box('Drain_Grate',s*1.84,.018,z,.10,.011,.035,'Steel',.001)
 for x in [.70,.81,.92,1.03]:cyl('Cable',(x,3.1,.65),(x,3.1,L-.65),.026,'Dark',12)
 for z in [1+i*3 for i in range(math.ceil((L-2)/3))]:
  box('Tray_Rung',.87,3.04,z,.55,.035,.10,'Steel',.005)
  for x in [.6,1.15]:cyl('Tray_Hanger',(x,3.04,z),(x,1.3+math.sqrt(2.09**2-x*x),z),.012,'Steel',12)
 # One real service box per corridor, ventilation repeated for the tunnel length.
 box('Backed_Control_Enclosure',1.94,1.54,L*.45,.20,.82,.64,'Steel',.016);box('Control_Gasket',1.828,1.54,L*.45,.02,.76,.58,'Dark',.006);box('Control_Cover',1.809,1.54,L*.45,.025,.73,.55,'Coat',.009)
 for y in [1.25,1.82]:
  for z in [L*.45-.20,L*.45+.20]:cyl('Captive_Screw',(1.795,y,z),(1.782,y,z),.011,'Steel',8)
 for z in [L*.2,L*.8]:
  box('Vent_Plenum',-1.93,1.95,z,.13,.40,.72,'Dark',.012)
  for j in range(7):box('Vent_Louver',-1.85,1.81+j*.047,z,.045,.021,.62,'Steel',.005)
 export(code+'_Finish',True)
(H/'architecture_models.json').write_text(json.dumps(build.manifest,indent=2),encoding='utf-8')
print('COMPLETE ARCHITECTURE',len(build.manifest),flush=True)
