"""Distinct functional interiors; retained dome shells. Author 송예찬."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
plan=json.loads((H/'plan.json').read_text(encoding='utf-8'));fixtures=[]
def wall(x,z,length,yaw=0,height=2.85,glass=True,mat='Accent'):
 before=set(bpy.data.objects)
 box('Partition_Kick',0,.09,0,length,.18,.14,'Steel',.012);box('Service_Wainscot',0,.48,0,length,.65,.105,mat,.012)
 if glass:box('Safety_Glass',0,(.82+height-.18)/2,0,length-.10,height-1.0,.014,'Window',.003)
 else:box('Acoustic_Panel',0,(.82+height-.18)/2,0,length-.10,height-1.0,.085,'Coat',.012)
 for y in [.80,height-.10]:box('Partition_Transom',0,y,0,length,.09,.12,'Steel',.009)
 n=max(1,math.ceil(length/1.25))
 for i in range(n+1):
  xx=-length/2+length*i/n;box('Partition_Mullion',xx,height/2,0,.055,height,.12,'Steel',.007)
  for yy in [.18,height-.25]:bolt(xx,yy,.067)
  box('Window_Gasket',xx-.037,(height+.80)/2,0,.012,height-.95,.022,'Gasket',.003)
 transform(set(bpy.data.objects)-before,x,z,yaw)
def doorway(z,w,opening,height=2.85,glass=True,mat='Accent'):
 for side in [-1,1]:
  seg=(w-opening)/2
  if seg>.05:wall(side*(opening/2+seg/2),z,seg,glass=glass,mat=mat,height=height)
  box('Entry_Portal_Jamb',side*(opening/2+.025),height/2,z,.10,height,.19,'Steel',.018)
 box('Entry_Portal_Header',0,height-.04,z,opening+.20,.14,.20,'Steel',.018)
 for side in [-1,1]:box('Edge_Impact_Strip',side*(opening/2+.01),.75,z+.11,.035,1.30,.04,'Rubber',.008)
def ceiling(w,d,h=3.0,solid=False):
 for x in [-w/2,w/2]:box('Canopy_Perimeter',x,h,0,.16,.18,d,'Steel',.012)
 for z in [-d/2,d/2]:box('Canopy_Crossbeam',0,h,z,w,.18,.16,'Steel',.012)
 for x in [-w*.34,0,w*.34]:
  box('Acoustic_Ceiling_Baffle',x,h+.12,0,.07,.30,d-.18,'Coat',.008)
 if solid:
  for x in [-w*.25,w*.25]:box('Ceiling_Deck',x,h+.03,0,w*.47,.045,d-.16,'Coat',.007)
 for z in [-d*.28,d*.28]:
  box('Recessed_Worklight',0,h-.13,z,w*.62,.09,.14,'Dark',.015);box('Worklight_Diffuser',0,h-.18,z,w*.58,.012,.10,'Lamp',.004)
def suite(w,d,kind):
 living=kind=='living_suite';h=2.75 if living else 2.95;mat='WarmAccent' if living else 'Accent'
 wall(0,-d/2,w,glass=not living,height=h,mat=mat)
 for x in [-w/2,w/2]:wall(x,0,d,90,glass=not living,height=h,mat=mat)
 doorway(d/2,w,1.25 if living else 2.9 if kind=='review_booth' else 2.1,h,glass=True,mat=mat);ceiling(w,d,h+.12,solid=living)
 if living:
  wall(1.28,1.6,1.25,height=1.60,glass=False,mat='Coat')
  box('Bed_Service_Rail',-1.05,1.08,-d/2+.13,1.65,.14,.11,'Steel',.01)
  for x in [-1.65,-1.3]:box('Power_Outlet',x,1.08,-d/2+.20,.12,.10,.025,'Dark',.007)
  b.vent(0,2.4,-d/2+.08,1.2,.24)
def overhead(kind,w,d):
 ceiling(w,d,3.25,solid=False)
 if kind in ['kitchen_extract','wet_canopy']:
  box('Extract_Hood',0,3.50,0,w*.80,.32,d*.76,'Steel',.045)
  for x in [-w*.20,w*.20]:b.vent(x,3.50,d*.39,w*.32,.20)
  box('Duct_Riser',0,4.15,0,.65,1.05,.55,'Coat',.018)
 else:
  for x in [-w/2,w/2]:
   for z in [-d/2,d/2]:box('Gantry_Column',x,1.6,z,.13,3.2,.13,'Steel',.014);box('Baseplate',x,.05,z,.28,.10,.28,'Steel',.012)
def special(s):
 kind=s['kind'];w=s['w'];d=s['d']
 if kind.endswith('_suite') or kind in ['control_booth','observation_booth','review_booth']:
  if kind=='command_suite':
   for x in [-w/2,w/2]:wall(x,.20,d-.4,90,height=3.3)
   wall(0,d/2,w,height=3.3,glass=False,mat='Blue');doorway(-d/2,w,3.2,3.3,glass=True,mat='Blue');ceiling(w,d,3.45)
  elif kind=='security_suite':
   for x in [-w/2,w/2]:wall(x,0,d,90,mat='Blue')
   doorway(-d/2,w,2.3,mat='Blue');ceiling(w,d,3.0)
  else:suite(w,d,kind)
 elif kind in ['nurse_canopy','service_canopy','receiving_canopy','storage_gantry','kitchen_extract','wet_canopy']:overhead(kind,w,d)
 elif kind=='machine_plinth':
  box('Equipment_Bed',0,.035,0,w,.07,d,'Steel',.02)
  for x in [-w/2+.12,w/2-.12]:
   for z in [-d/2+.12,d/2-.12]:cyl('Anchor_Head',(x,.07,z),(x,.09,z),.023,'Steel',6)
 elif kind=='process_headers':
  for x in [-2.55,2.55]:
   sign=1 if x>0 else -1
   tube('Pump_Discharge_Connection',[(x,1.17,-2.15+.24*sign),(x,3.5,-2.15+.24*sign)],.065,'Steel')
   # Connect to all four actual heat-exchanger flange ends, keeping the side aisle clear.
   for dx in [-.7,.7]:
    for y in [.59,1.59]:
     yy=3.5 if dx<0 else 3.85
     xx=x+dx*sign;zz=1.65+.69*sign
     tube('Exchanger_Flow_Return',[(xx,y,zz),(xx,y,zz+.26*sign),(xx,yy,zz+.26*sign),(x,yy,zz+.26*sign),(x,yy,3.8)],.065,'Steel')
   tube('Primary_Flow',[(x,3.5,-3.4),(x,3.5,4.0)],.10,'Teal')
   for z in [-2.5,0,2.5]:cyl('Header_Support',(x,3.6,z),(x,4.3,z),.018,'Steel',12)
  tube('Supply_Crossover',[(-2.55,3.5,3.8),(-2.55,3.9,3.8),(2.55,3.9,3.8),(2.55,3.5,3.8)],.1,'Steel')
 elif kind in ['power_screen','wash_partition','server_baffle']:wall(0,0,d,90,glass=kind!='power_screen',height=2.6,mat='Blue' if kind=='server_baffle' else 'Accent')
 elif kind in ['cold_partition','decon_partition']:doorway(0,w,2.7,3.0,glass=True,mat='Accent')
 elif kind=='triage_screen':
  for x in [-w/2,w/2]:wall(x,0,d,90,height=1.6,glass=False)
  ceiling(w,d,3.0)
 elif kind=='test_cell':
  for x in [-w/2,w/2]:wall(x,0,d,90,height=3.5,mat='Blue')
  wall(0,d/2,w,height=3.5,mat='Blue');doorway(-d/2,w,2.1,3.5,mat='Blue');ceiling(w,d,3.62)
  for x in [-1.8,1.8]:
   tube('Cell_Sensor_Conduit',[(x,.5,d/2-.1),(x,3.25,d/2-.1),(x,3.25,-d/2+.1)],.025,'Steel');box('Interlock_Housing',x,1.2,-d/2-.12,.22,.42,.1,'Dark',.014);label(x,1.25,-d/2-.178,.16,.16,55)
def core(room):
 r=plan['rooms'][room]
 for y in [3.9,7.9,11.9,15.9,18.7]:
  tube('Shaft_Service_Ring',[(4.83*math.cos(i*math.tau/96),y,4.83*math.sin(i*math.tau/96)) for i in range(97)],.055,'Steel')
 for a in range(0,360,30):
  if any(abs((a-q['angle']+180)%360-180)<36 for q in r['doors']):continue
  t=math.radians(a);before=set(bpy.data.objects)
  wall(0,0,.74,height=3.4,glass=False,mat='Accent')
  b.vent(0,2.68,.10,.57,.35);label(0,1.5,.071,.28,.20,56)
  transform(set(bpy.data.objects)-before,4.78*math.cos(t),4.78*math.sin(t),-90-a)
 if room in ['VA','VB']:
  for x in [-1.76,1.76]:
   for z in [-3.08,3.08]:
    for y in [0.12,2.12,4.12,6.12,8.12,10.12,12.12,14.12,16.12]:
     box('Column_Joint_Collar',x,y,z,.19,.16,.19,'Steel',.009)
     for xx in [-.06,.06]:bolt(x+xx,y,z+.104)
 else:
  for x in [-1.5,1.5]:
   box('Door_Guide_Cover',x,1.4,-1.82,.10,2.7,.10,'Steel',.012)
   for y in [.2,.8,1.4,2.0,2.6]:bolt(x,y,-1.88)
  for x in [-.7,.7]:
   box('Landing_Track',x,.025,-1.95,1.3,.045,.14,'Steel',.009)
   for i in range(12):box('Track_Groove',x-.58+i*.105,.049,-1.95,.015,.004,.12,'Dark',.001)
  box('Service_Cabinet',2.2,1.0,0,.45,1.8,.75,'Coat',.02);b.vent(2.2,1.5,.39,.30,.25);label(2.2,1.05,.391,.24,.24,57)
import os
for room in [r for r in plan['rooms'] if r!='C01' and (not os.getenv('SF_ROOMS') or r in os.getenv('SF_ROOMS').split(','))]:
 reset()
 for s in [q for q in plan['structures'] if q['room']==room]:
  before=set(bpy.data.objects)
  if s['kind']=='core_detail':core(room)
  else:special(s)
  transform(set(bpy.data.objects)-before,s['x'],s['z'],s['yaw'])
  if s['kind'] in ['living_suite','exam_suite','control_booth','observation_booth','command_suite','security_suite','receiving_canopy','kitchen_extract','nurse_canopy','wet_canopy','service_canopy','review_booth']:
   h=2.87 if s['kind']=='living_suite' else 3.45 if s['kind']=='command_suite' else 3.0 if s['kind']=='security_suite' else 3.25 if s['kind'].endswith('canopy') or s['kind']=='kitchen_extract' else 3.07
   a=math.radians(s['yaw'])
   for z in [-s['d']*.28,s['d']*.28]:fixtures.append(dict(room=room,position=[s['x']+math.sin(a)*z,h-.22,s['z']+math.cos(a)*z],intensity=1.15,range=4.4))
 save('SF_'+room+'_Interior')
(H/'fixtures.json').write_text(json.dumps(fixtures,indent=2),encoding='utf-8')
