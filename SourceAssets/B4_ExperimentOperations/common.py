"""B4 experiment operations art, Unity metres/front +Z. 작성자 송예찬."""
import sys,importlib.util,json,math,bpy
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[1]
spec=importlib.util.spec_from_file_location('operations_helpers',R/'SourceAssets/B4_Observation/common.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
b.H=H;b.manifest=json.loads((H/'models.json').read_text()) if (H/'models.json').exists() else {}
box=b.box;cyl=b.cyl;mesh=b.mesh;tube=b.tube;display=b.display;stand=b.monitor_stand;keyboard=b.keyboard;pull=b.pull;vent=b.vent;feet=b.feet;cabinet=b.cabinet;transform=b.transform
def reset():
 b.reset()
 for i in range(23,43):
  m=bpy.data.materials.new(f'BX_Display_{i:02}');m.diffuse_color=(.11,.16,.18,1);b.mats[f'Display_{i:02}']=m
def save(name):
 import os
 if os.environ.get('BX_ONLY') and name not in os.environ['BX_ONLY'].split(','):return
 b.OUT=b.A/'Props/B4';b.raw_export('BX_'+name);b.manifest['BX_'+name]['category']='Props'
 (H/'models.json').write_text(json.dumps(b.manifest,indent=2),encoding='utf8')
def screen(x,y,z,w=.68,h=.39,k=23,desktop=False,top=.9):
 display(x,y,z,w,h,k)
 if desktop:stand(x,y,z,w,h,top)
def label(x,y,z,w=.24,h=.07,k=41):return b.print_panel('Flush_Equipment_ID',x,y,z,w,h,k)
def knob(x,y,z,r=.023):
 cyl('Encoder_Recess',(x,y,z),(x,y,z+.007),r*1.26,'Dark',20);cyl('Knurled_Control',(x,y,z+.008),(x,y,z+.034),r,'Steel',20);box('Index_Mark',x,y+r*.55,z+.035,.005,r*.38,.002,'Paper',.0005)
def buttons(x,y,z,n=3):
 for i in range(n):
  xx=x+(i-(n-1)/2)*.075;cyl('Button_Bezel',(xx,y,z),(xx,y,z+.012),.024,'Steel',16);cyl('Button_Cap',(xx,y,z+.012),(xx,y,z+.021),.017,'Indicator' if i==0 else 'Dark',16)
def emergency(x,y,z):
 box('Emergency_Backplate',x,y,z,.15,.15,.025,'Hazard',.012);cyl('Stop_Bezel',(x,y,z+.02),(x,y,z+.04),.045,'Dark',20);cyl('Emergency_Stop',(x,y,z+.04),(x,y,z+.07),.035,'Red',20)
def tabletop(w=2.2,d=.8,y=.88):
 for x in [-w/2+.16,w/2-.16]:
  box('Leg_Frame',x,(y-.07)/2,0,.07,y-.15,d*.72,'Steel',.008);box('Level_Foot',x,.045,0,.18,.09,d*.91,'Dark',.012)
 box('Sealed_Top',0,y,0,w,.07,d,'Coat',.022);box('Service_Raceway',0,y-.19,-d*.36,w-.25,.12,.11,'Steel',.008)
def wheel(x,z,y=.09):
 cyl('Swivel_Stem',(x,y,z),(x,y+.12,z),.018,'Steel',12);box('Caster_Fork',x,y+.025,z,.075,.09,.09,'Steel',.009);cyl('Rubber_Wheel',(x-.045,y,z),(x+.045,y,z),.065,'Rubber',20);cyl('Axle',(x-.05,y,z),(x+.05,y,z),.021,'Steel',12)
def cartbase(w=.85,d=.62):
 for x in [-w/2+.08,w/2-.08]:
  for z in [-d/2+.08,d/2-.08]:wheel(x,z)
 box('Cart_Base',0,.22,0,w,.08,d,'Steel',.014)
def glass_panel(x,z,w=2.6,h=2.5,y=0):
 for xx in [x-w/2,x+w/2]:box('Glazing_Post',xx,y+h/2,z,.075,h,.10,'Steel',.009)
 for yy in [y+.1,y+h-.05]:box('Glazing_Rail',x,yy,z,w,.08,.12,'Steel',.008)
 box('Laminated_Glass',x,y+h/2,z,w-.09,h-.16,.024,'Glass',.003);box('Lower_Protection',x,y+.36,z,w-.08,.49,.07,'Coat',.01)
def case(x,y,z,w=.5,h=.28,d=.4):
 box('Protective_Case',x,y+h/2,z,w,h,d,'Dark',.028);box('Lid_Seam',x,y+h*.72,z,w+.006,.014,d+.006,'Steel',.003)
 for xx in [x-w*.33,x+w*.33]:
  box('Case_Latch',xx,y+h*.68,z+d/2+.006,.055,.075,.018,'Steel',.007)
 pull(x,y+h*.42,z+d/2+.012,min(.18,w*.4));label(x,y+h*.84,z+d/2+.006,min(w*.5,.27),.042)
def hollow_cabinet(w,h,d):
 feet(w,d)
 for x in [-w/2+.025,w/2-.025]:box('Cabinet_Side',x,(h+.16)/2,0,.05,h-.16,d,'Coat',.01)
 for y in [.19,h]:box('Cabinet_Shell_Rail',0,y,0,w,.05,d,'Steel',.01)
 box('Cabinet_Inner_Back',0,(h+.16)/2,-d/2+.025,w-.08,h-.16,.05,'Steel',.008)
def vial(x,y,z,r=.026,h=.16):
 cyl('Vial_Base',(x,y,z),(x,y+.018,z),r,'Steel',20);cyl('Vial_Body',(x,y+.018,z),(x,y+h-.03,z),r,'Glass',24);cyl('Sealed_Cap',(x,y+h-.03,z),(x,y+h,z),r*1.08,'Dark',24)
 # a thin wrap label, not a protruding cube
 b.sector('Wrapped_Label',r+.001,r+.0018,y+.035,y+.095,18,162,'Paper',12,.0002)
