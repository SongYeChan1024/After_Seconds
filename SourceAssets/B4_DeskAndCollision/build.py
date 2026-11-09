"""Protocol workstation detail. Author Song Ye Chan. Unity metres; front +Z."""
import sys,json,importlib.util,math
from pathlib import Path
import bpy
H=Path(__file__).resolve().parent;R=H.parents[1]
s=importlib.util.spec_from_file_location('desk_common',R/'SourceAssets/B4_ExperimentOperations/common.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
b=c.b;b.H=H;b.OUT=b.A/'Props/B4';b.manifest={};box=c.box;cyl=c.cyl;tube=c.tube
c.reset();c.tabletop(2.8,1.35)
# Screen, mount and routed leads occupy the rear centre only.
c.screen(0,1.28,-.37,.72,.37,40)
box('Monitor_Foot',0,.936,-.45,.32,.042,.25,'Steel',.012)
box('Monitor_Rubber_Pad',0,.918,-.45,.29,.006,.22,'Rubber',.001)
box('Monitor_Mast',0,1.083,-.56,.06,.29,.07,'Steel',.008)
cyl('Tilt_Pivot',(-.055,1.24,-.55),(.055,1.24,-.55),.035,'Dark',16)
box('VESA_Mount_Link',0,1.255,-.516,.07,.09,.06,'Steel',.006)
# Compact desktop PC with service seams, ventilation, I/O and feet.
x=-.65;z=-.39
box('Compact_PC_Chassis',x,1.026,z,.34,.20,.37,'Dark',.012)
box('PC_Front_Panel',x,1.026,z+.19,.326,.18,.018,'Coat',.006)
for xx in [x-.115,x+.115]:
 for zz in [z-.12,z+.12]:box('PC_Rubber_Foot',xx,.920,zz,.045,.01,.045,'Rubber',.002)
box('Service_Seam',x,1.124,z,.32,.003,.35,'Steel',.0005)
for i in range(10):box('PC_Front_Intake',x-.13+i*.018,1.015,z+.202,.007,.066,.003,'Dark',.001)
for i in range(8):box('PC_Rear_Exhaust',x-.12+i*.034,1.06,z-.188,.017,.056,.003,'Steel',.001)
cyl('Power_Button',(x+.115,1.069,z+.203),(x+.115,1.069,z+.209),.014,'Steel',16)
box('Power_LED',x+.115,1.04,z+.210,.006,.006,.002,'Indicator',.001)
for y in [1.005,.976]:box('USB_Surround',x+.112,y,z+.202,.035,.016,.006,'Steel',.001);box('USB_Socket',x+.112,y,z+.206,.027,.009,.004,'Dark',.0005)
for xx in [x-.115,x+.115]:
 for y in [.962,1.09]:cyl('Case_Fastener',(xx,y,z+.20),(xx,y,z+.204),.005,'Steel',8)
# Rear I/O is authored with matching cable plugs in input_devices.py.
# Detail pass: realistic keyboard, right-hand mouse, smooth wired connections.
sp=importlib.util.spec_from_file_location('input_devices',H/'input_devices.py');devices=importlib.util.module_from_spec(sp);sp.loader.exec_module(devices);devices.build(c,H)
# Separate left and right paper zones. No paper can reach the screen/stand.
paper_bounds=[]
for j,(x,z,a) in enumerate([(-.93,.21,-6),(.89,.16,5)]):
 before=set(bpy.context.scene.objects)
 box('Protocol_Folder',x,.926,z,.44,.020,.54,'Dark',.006)
 for i in range(4):box('Thin_Protocol_Sheet',x+.003*i,.937+i*.0014,z-.004*i,.40,.001,.50,'Paper',.0002)
 for i in range(10):box('Printed_Record_Row',x-.025,.943,z-.19+i*.033,.30-(i%3)*.035,.0008,.003,'Steel',.0001)
 box('Document_Header',x,.943,z-.222,.32,.001,.014,'Mark',.0002)
 box('Binder_Clip',x,.948,z-.246,.07,.012,.025,'Steel',.002)
 # Rotate as a group around each folder centre, preserving placement.
 from mathutils import Matrix,Vector
 m=Matrix.Translation(Vector(b.xyz(x,0,z)))@Matrix.Rotation(-math.radians(a),4,'Z')@Matrix.Translation(-Vector(b.xyz(x,0,z)))
 for o in set(bpy.context.scene.objects)-before:o.matrix_world=m@o.matrix_world
 paper_bounds.append(dict(x=x,z=z,rotation=a))
cyl('Pen',(.58,.926,.14),(.58,.926,.31),.004,'Steel',12)
box('Document_Inbox',.98,.947,-.43,.44,.064,.30,'Steel',.006)
box('Inbox_Dark_Base',.98,.981,-.43,.40,.004,.27,'Dark',.001)
for xx in [.765,1.195]:box('Inbox_Rim',xx,.994,-.43,.01,.06,.30,'Steel',.002)
for i in range(5):box('Queued_Sheet',.98+i*.002,.986+i*.0014,-.43,.37,.001,.24,'Paper',.0002)
b.raw_export('PD_ProtocolTable')
(H/'models.json').write_text(json.dumps(b.manifest,indent=2),encoding='utf8')
(H/'paper_layout.json').write_text(json.dumps(paper_bounds,indent=2),encoding='utf8')
