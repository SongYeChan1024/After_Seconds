"""Additional bench structure; reuses the approved B4 construction language."""
import sys,importlib.util,json,math
from pathlib import Path
import bpy
H=Path(__file__).resolve().parent;R=H.parents[1]
spec=importlib.util.spec_from_file_location('ops',R/'SourceAssets/B4_ExperimentOperations/common.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
b=c.b;b.H=H;b.OUT=b.A/'Props/B4';b.manifest=json.loads((H/'models.json').read_text())
box=c.box;cyl=c.cyl;tube=c.tube
def reset():
 c.reset()
 for k in ['Coat','Steel','Red','Paper','Dark']:b.mats[k].name='BP_'+k
def save(n):
 b.raw_export('BP_'+n);(H/'models.json').write_text(json.dumps(b.manifest,indent=2),encoding='utf8')
reset()
# Two-sided service island with readable physical separations and open legs.
for x in [-1.10,1.10]:
 for z in [-.55,.55]:
  box('Square_Tube_Leg',x,.45,z,.07,.82,.07,'Steel',.007);cyl('Threaded_Leveling_Foot',(x,.025,z),(x,.10,z),.06,'Dark',16)
box('Worktop_Core',0,.88,0,2.50,.075,1.45,'Coat',.018)
for z in [-.715,.715]:box('Steel_Edge_Return',0,.866,z,2.46,.035,.025,'Steel',.004)
for x in [-.84,.84]:
 box('Drawer_Housing',x,.48,0,.49,.70,1.12,'Coat',.012)
 for side in [-1,1]:
  old=set(bpy.context.scene.objects)
  for y in [.27,.48,.69]:
   box('Drawer_Shadow_Gap',x,y,.57,.44,.184,.016,'Dark',.002);box('Drawer_Front',x,y,.584,.41,.16,.016,'Coat',.004);c.pull(x,y+.035,.60,.23)
  if side<0:b.transform(set(bpy.context.scene.objects)-old,0,0,0,180)
for side in [-1,1]:
 old=set(bpy.context.scene.objects)
 box('AntiStatic_Surface',0,.923,.37,1.45,.008,.53,'Rubber',.004)
 box('Bench_Meter',-.42,1.05,.22,.50,.24,.35,'Coat',.018);c.screen(-.47,1.06,.40,.28,.12,33);c.knob(-.24,1.05,.40,.022)
 for i in range(4):cyl('Calibration_Socket',(.10+i*.13,.95,.29),(.10+i*.13,1.02,.29),.03,'Steel',16)
 tube('Coiled_Instrument_Lead',[(.18,.96,.4),(.4,.96,.5),(.59,.96,.38),(.51,.96,.24)],.007,'Dark')
 if side<0:b.transform(set(bpy.context.scene.objects)-old,0,0,0,180)
for x in [-1.06,1.06]:box('Overhead_Service_Upright',x,1.51,0,.055,1.20,.055,'Steel',.006)
box('Service_Header',0,2.08,0,2.17,.10,.24,'Steel',.01)
for side in [-1,1]:
 for x in [-.65,0,.65]:
  box('Outlet_Plate',x,1.94,side*.05,.20,.15,.035,'Coat',.007)
  for dx in [-.04,.04]:cyl('Recessed_Outlet',(x+dx,1.94,side*.07),(x+dx,1.94,side*.081),.019,'Dark',16)
for x in [-1.06,1.06]:tube('Protected_Power_Run',[(x,2.1,.06),(x,1.0,.06),(x,.15,.06),(x-.12,.10,.06)],.015,'Dark')
save('CalibrationIsland')
reset()
# Addon fits below an existing worktop, leaving the front knee opening free.
box('Drawer_Pedestal',0,.39,0,.45,.67,.52,'Coat',.014)
for y in [.18,.39,.60]:
 box('Drawer_Seam',0,y,.268,.405,.18,.016,'Dark',.002);box('Drawer_Front',0,y,.28,.38,.16,.018,'Coat',.004);c.pull(0,y+.03,.297,.20)
 c.label(-.10,y-.025,.29,.10,.025,41)
for x in [-.17,.17]:
 for z in [-.19,.19]:cyl('Leveling_Foot',(x,.015,z),(x,.08,z),.035,'Dark',12)
box('Side_Service_Panel',.231,.39,0,.012,.38,.36,'Steel',.004)
for y in [.25,.53]:
 for z in [-.13,.13]:cyl('Panel_Fixing',(.235,y,z),(.246,y,z),.008,'Steel',6)
save('BenchPedestal')
