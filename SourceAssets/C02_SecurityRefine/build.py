"""C02 supporting equipment; editable Blender originals. Author: 송예찬."""
import ast,bpy,bmesh,math,json,os
from pathlib import Path
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;R=H.parents[1]
base=(R/'SourceAssets/C02_Security/build.py').read_text(encoding='utf-8')
exec(compile(base.split("\nfor k in ['A','B']:desk(k)")[0],'C02_helpers','exec'))
base_reset=reset
def reset():
 base_reset();m=bpy.data.materials.new('SC_EquipmentPrint');m.diffuse_color=(.08,.13,.15,1);mats['EquipmentPrint']=m
def label(textrow,x,y,z,w,h):
 ob=mesh('Equipment_Identification',[(x-w/2,y-h/2,z),(x+w/2,y-h/2,z),(x+w/2,y+h/2,z),(x-w/2,y+h/2,z)],[(0,3,2,1)],'EquipmentPrint',0)
 if ob.data.polygons[0].normal.y>0:ob.data.flip_normals()
 uv=ob.data.uv_layers.new(name='UVMap');v1=1-textrow/8;v0=v1-1/8;coords=[(1,v0),(0,v0),(0,v1),(1,v1)]
 for p in ob.data.polygons:
  for li in p.loop_indices:uv.data[li].uv=coords[ob.data.loops[li].vertex_index]
 ob['display_uv']=True
def grill(x,y,z,w,h,count=9):
 box('Vent_Recess',x,y,z,w,h,.045,'Dark',.008)
 for xx in [x-w/2,x+w/2]:box('Vent_Frame',xx,y,z+.03,.025,h+.04,.05,'Steel',.005)
 for yy in [y-h/2,y+h/2]:box('Vent_Frame',x,yy,z+.03,w,.025,.05,'Steel',.005)
 for j in range(count):box('Vent_Louver',x,y-h*.43+j*h*.86/(count-1),z+.043,w-.03,h*.040,.057,'Coat',.004)
 for xx in [x-w/2+.035,x+w/2-.035]:
  for yy in [y-h/2+.035,y+h/2-.035]:bolt(xx,yy,z+.063)
def headset(x,y,z):
 pts=[(x+math.cos(math.radians(a))*.13,y+math.sin(math.radians(a))*.17,z) for a in range(0,181,9)]
 tube('Headset_Spring',pts,.012,'Steel');tube('Headband_Pad',pts[3:-3],.021,'Rubber')
 for xx in [x-.13,x+.13]:
  box('Ear_Cup',xx,y-.025,z,.068,.14,.085,'Dark',.023);box('Ear_Cushion',xx,y-.025,z+.045,.055,.12,.028,'Rubber',.012)
 tube('Headset_Mic',[(x-.15,y-.05,z),(x-.11,y-.14,z+.06),(x-.03,y-.14,z+.12)],.006,'Steel')
 box('Mic_Foam',x-.025,y-.14,z+.12,.06,.025,.026,'Rubber',.011)
 # A visible coiled lead and socket, not a floating loose wire.
 pts=[(x+.13+.018*math.cos(i*.8),y-.10-i*.004,z+.018*math.sin(i*.8)) for i in range(50)]
 tube('Coiled_Lead',pts,.004,'Dark')
def anchor(x,y,z):
 back=math.hypot(5.23,3.76)-math.sqrt(6.965**2-y*y-x*x)-.025
 box('Wall_Bracket',x,y,(back+.08)/2,.12,.15,.08-back,'Steel',.009);bolt(x,y,.09)

# Distinct AV service station, northwest of the main operator wall.
reset()
box('AV_Cabinet',0,1.02,0,.98,2.04,.62,'Coat',.025);box('AV_Plinth',0,.05,.02,1.02,.10,.68,'Dark',.018)
for xx in [-.435,.435]:box('Rack_Rail',xx,1.04,.326,.033,1.86,.035,'Steel',.005)
label(0,0,1.91,.342,.78,.098)
for row in range(3):
 yy=1.63-row*.23;box('Encoder_Module',0,yy,.33,.82,.19,.035,'Dark',.008)
 for j in range(6):
  xx=-.31+j*.12;cyl('BNC_Socket',(xx,yy+.025,.354),(xx,yy+.025,.377),.017,'Steel',12);cyl('Signal_Core',(xx,yy+.025,.378),(xx,yy+.025,.384),.007,'Dark',10)
 for j in range(4):box('Module_LED',-.31+j*.04,yy-.057,.354,.012,.006,.006,'Indicator',0)
 pull(.29,yy-.05,.36,.11)
for j in range(4):
 xx=-.31+j*.12;tube('AV_Patch_Cable',[(xx,1.655,.384),(xx,1.52,.45),(xx+.12,1.49,.45),(xx+.12,1.425,.384)],.007,'Teal')
box('Service_Drawer',0,.75,.329,.82,.30,.032,'Teal',.008);pull(0,.80,.352,.28)
grill(0,.30,.35,.77,.35,7)
box('Foldout_Test_Shelf',0,.99,.50,.85,.035,.36,'Steel',.012)
for xx in [-.34,.34]:tube('Shelf_Brace',[(xx,.78,.33),(xx,.96,.62),(xx,.96,.35)],.012,'Steel')
box('Diagnostic_Handset',-.20,1.027,.53,.17,.055,.24,'Dark',.014)
box('Diagnostic_Screen',-.20,1.057,.50,.11,.004,.12,'Teal',0)
for j in range(3):box('Meter_Button',-.245+j*.045,1.061,.615,.022,.008,.022,'Coat',.002)
export('SR_AVServiceRack')

# Credential/key issue point at the western wall: glazed keys, scan shelf, locked returns.
reset()
box('Key_Station_Lower',0,.43,0,.98,.86,.42,'Coat',.024)
for xx in [-.473,.473]:box('Key_Case_Side',xx,1.45,0,.035,1.20,.42,'Coat',.010)
box('Key_Case_Back',0,1.45,-.20,.94,1.20,.035,'Coat',.008)
box('Key_Case_Top',0,2.035,0,.98,.05,.42,'Coat',.010)
box('Opaque_Key_Backboard',0,1.42,.12,.85,.99,.045,'Dark',.008)
for row in range(3):
 for col in range(4):
  xx=(col-1.5)*.19;yy=1.12+row*.28
  cyl('Key_Hook',(xx,yy+.07,.15),(xx,yy+.07,.20),.009,'Steel',12)
  cyl('Key_Ring',(xx,yy+.04,.19),(xx,yy+.04,.20),.022,'Steel',16)
  box('Asset_Tag',xx,yy-.012,.205,.068,.088,.009,'Teal' if col%2 else 'Paper',.003)
  box('Key_Blade',xx+.022,yy-.08,.21,.017,.069,.008,'Steel',.002)
for xx in [-.45,.45]:box('Glass_Door_Rail',xx,1.43,.24,.036,1.14,.045,'Steel',.006)
for yy in [.88,1.98]:box('Glass_Door_Rail',0,yy,.24,.90,.035,.045,'Steel',.006)
box('Key_Glazing',0,1.43,.236,.86,1.05,.006,'Glass',0);pull(.39,1.40,.266,.07)
label(1,0,2.02,.226,.83,.078)
box('Credential_Shelf',0,.87,.30,1.04,.035,.36,'Steel',.011)
box('Card_Scanner',.25,.916,.34,.19,.065,.21,'Dark',.013);box('Scan_Window',.25,.951,.34,.13,.006,.13,'Teal',0)
box('Return_Hatch',0,.51,.228,.86,.61,.035,'Dark',.008);box('Badge_Return_Slot',0,.68,.249,.42,.045,.012,'Rubber',.004);pull(0,.30,.252,.24);label(2,0,.52,.249,.66,.083)
export('SR_CredentialStation')

# Sealed evidence storage: visible backed interior and physical crates behind glass.
reset();box('Evidence_Plinth',0,.065,0,1.29,.13,.65,'Dark',.018)
for xx in [-.61,.61]:box('Evidence_Case_Side',xx,1.02,0,.035,1.90,.58,'Coat',.010)
box('Evidence_Back',0,1.02,-.28,1.22,1.90,.035,'Dark',.007)
box('Evidence_Header',0,1.97,.02,1.27,.14,.62,'Coat',.016);label(3,0,1.97,.337,1.06,.132)
for yy in [.19,.73,1.27,1.82]:box('Storage_Shelf',0,yy,.01,1.19,.027,.54,'Steel',.006)
for row in range(3):
 for col in range(2):
  xx=(col-.5)*.57;yy=.37+row*.54
  box('Sealed_Transport_Case',xx,yy,.045,.50,.32,.40,'Teal' if row==1 else 'Dark',.022)
  box('Case_Lid',xx,yy+.17,.045,.515,.032,.415,'Coat',.008)
  for ax in [-.17,.17]:box('Case_Latch',xx+ax,yy+.10,.256,.041,.075,.026,'Steel',.006)
  pull(xx,yy-.01,.254,.18);label(4,xx,yy+.075,.268,.28,.035)
for xx in [-.61,0,.61]:box('Front_Frame',xx,1.02,.316,.035,1.86,.045,'Steel',.006)
for xx in [-.302,.302]:box('Storage_Glass',xx,1.02,.310,.56,1.77,.006,'Glass',0)
pull(.055,1.03,.345,.075);cyl('Cabinet_Lock',(.055,.88,.342),(.055,.88,.355),.019,'Dark',12)
export('SR_EvidenceCabinet')

# Shallow wall station above the southwest service strip, clear of the route.
reset();box('Equipment_Backboard',0,1.63,0,1.53,1.16,.065,'Dark',.016)
for xx in [-.67,.67]:
 for yy in [1.14,2.10]:anchor(xx,yy,-.085)
for xx in [-.43,.04]:
 box('Headset_Hook',xx,1.91,.10,.045,.06,.16,'Steel',.007);headset(xx,1.73,.18)
label(5,0,2.13,.037,1.36,.17)
box('Equipment_Tray',0,1.07,.18,1.59,.045,.45,'Steel',.012)
for xx in [-.76,.76]:box('Tray_End',xx,1.13,.18,.025,.10,.43,'Steel',.005)
for i in range(3):
 xx=.36+i*.12;box('Spare_Battery_Cradle',xx,1.12,.19,.10,.05,.19,'Dark',.009);box('Spare_Battery',xx,1.22,.19,.074,.18,.11,'Teal',.012);box('Charge_Contact',xx,1.32,.19,.042,.006,.06,'Steel',0);box('Charge_LED',xx,1.15,.29,.014,.008,.004,'Indicator',0)
export('SR_ShiftEquipment')

# A manufactured three-module HVAC return bank above the video wall, without new lights.
reset()
box('Air_Plenum',0,3.39,5.43,3.34,.53,.30,'Coat',.024)
for xx in [-1.08,0,1.08]:
 front=[(xx+dx*.29,3.39+dy*.18,5.54) for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 back=[(x,y,math.sqrt(6.98**2-x*x-y*y)) for x,y,z in front]
 mesh('Return_Duct_To_Dome',front+back,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'Steel',.006)
# Faces toward the center, so build grilles locally then rotate the entire assembly 180 degrees about its center.
parts=set(bpy.context.scene.objects)
for xx in [-1.08,0,1.08]:grill(xx,3.39,5.61,.98,.39,8)
label(6,0,3.67,5.59,1.3,.10)
for ob in set(bpy.context.scene.objects)-parts:
 center=Vector(xyz(0,3.39,5.43));ob.matrix_world=Matrix.Translation(center)@Matrix.Rotation(math.pi,4,'Z')@Matrix.Translation(-center)@ob.matrix_world
export('SR_NorthAirReturn',True)

# Wall service rails with supports and explicitly routed drops to the equipment.
reset()
for start,end in [(183,240),(305,335)]:
 for y in [2.38,2.49]:
  pts=[(6.43*math.cos(math.radians(a)),y,6.43*math.sin(math.radians(a))) for a in range(start,end+1,2)]
  tube('Wall_Service_Conduit',pts,.022,'Steel')
 for a in range(start+2,end,12):
  t=math.radians(a);x,z=6.43*math.cos(t),6.43*math.sin(t)
  tube('Conduit_Wall_Support',[(x,2.33,z),(x,2.55,z),(x*1.009,2.55,z*1.009)],.014,'Dark')
for x,z,height in [(-5.95,-.30,2.05),(-5.12,-1.65,1.8),(-5.23,-3.76,2.12),(4.3,-4.37,1.97),(4.5,-2.8,1.84)]:
 r=math.hypot(x,z);drop=min(r*1.035,6.43)/r;tube('Equipment_Service_Drop',[(x*6.43/r,2.38,z*6.43/r),(x*drop,2.38,z*drop),(x*drop,height,z*drop)],.017,'Dark')
export('SR_WallServices',True)
if os.environ.get('C02_MODELS'):
 previous=json.loads((H/'model_manifest.json').read_text(encoding='utf-8'));previous.update(manifest);manifest=previous
(H/'model_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
