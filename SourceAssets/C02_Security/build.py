"""C02 engineered architectural/operations assets. Author: 송예찬."""
import ast,bpy,bmesh,math,json,os
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[1];A=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model';manifest={}
tree=ast.parse((R/'SourceAssets/CircularDressing/build_environment.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
ex=ast.unparse(next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='export'))
ex=ex.replace('obj.name = name','obj.name = name\n    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)').replace('for p in o.data.polygons:',"if o.get('display_uv'): continue\n        for p in o.data.polygons:")
exec(ex);raw_export=export
def export(name,environment=False):
 if os.environ.get('C02_MODELS') and name not in os.environ['C02_MODELS'].split(','):return
 global OUT;OUT=A/('Environment' if environment else 'Props')/'B5';raw_export(name);manifest[name]['category']='Environment' if environment else 'Props'
def reset():
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;bpy.context.scene.unit_settings.system='METRIC';global mats;mats={}
 for n,col,met,rough in [('Coat',(.65,.71,.72,1),.12,.48),('Steel',(.36,.43,.47,1),.8,.34),('Dark',(.026,.040,.05,1),.15,.52),('Rubber',(.016,.022,.025,1),0,.73),('Teal',(.08,.24,.26,1),.4,.4),('Fabric',(.14,.19,.22,1),0,.9),('Glass',(.08,.18,.20,.18),.15,.16),('Indicator',(.19,.67,.48,1),.1,.3),('Paper',(.74,.76,.70,1),0,.88),('Lamp',(.75,.85,.88,1),0,.2),('Floor',(.23,.28,.30,1),.02,.68)]+[(f'Display_{i:02}',(.15,.35,.40,1),.05,.2) for i in range(1,11)]:
  m=bpy.data.materials.new('SC_'+n);m.diffuse_color=col;m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=col;p.inputs['Metallic'].default_value=met;p.inputs['Roughness'].default_value=rough;mats[n]=m
def tube(name,pts,r,mat='Dark'):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=r;cu.bevel_resolution=2;cu.use_fill_caps=True;s=cu.splines.new('POLY');s.points.add(len(pts)-1)
 for p,v in zip(s.points,pts):p.co=(*xyz(*v),1)
 ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);cu.materials.append(mats[mat]);bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False);return ob
def display(x,y,z,w,h,kind):
 # Recessed optical face, separate shell seam, machined perimeter and rear service cover.
 box('Display_Back',x,y,z-.042,w+.065,h+.065,.114,'Dark',.018)
 box('Rear_Service_Cover',x,y,z-.104,w*.83,h*.77,.025,'Coat',.012)
 box('Display_Recess',x,y,z+.020,w+.025,h+.025,.020,'Rubber',.004)
 for xx in [x-w/2-.019,x+w/2+.019]:box('Anodized_Bezel_Side',xx,y,z+.030,.025,h+.065,.039,'Steel',.005)
 for yy in [y-h/2-.021,y+h/2+.021]:box('Anodized_Bezel_Rail',x,yy,z+.030,w+.025,.023,.039,'Steel',.004)
 for xx in [x-w/2-.006,x+w/2+.006]:box('Optical_Gasket',xx,y,z+.030,.007,h,.009,'Dark',0)
 for yy in [y-h/2-.006,y+h/2+.006]:box('Optical_Gasket',x,yy,z+.030,w,.007,.009,'Dark',0)
 ob=mesh('LCD_Optical_Surface',[(x-w/2,y-h/2,z+.032),(x+w/2,y-h/2,z+.032),(x+w/2,y+h/2,z+.032),(x-w/2,y+h/2,z+.032)],[(0,3,2,1)],f'Display_{kind:02}',0)
 if ob.data.polygons[0].normal.y>0:ob.data.flip_normals()
 uv=ob.data.uv_layers.new(name='UVMap');coords=[(1,0),(0,0),(0,1),(1,1)]
 for p in ob.data.polygons:
  for li in p.loop_indices:uv.data[li].uv=coords[ob.data.loops[li].vertex_index]
 ob['display_uv']=True
 box('Power_Indicator',x+w*.4,y-h*.5-.021,z+.052,.014,.004,.004,'Indicator',0)
 # Tiny integrated rack LCDs do not get the desktop VESA/IO hardware.
 if h>.25:
  for i in range(12):box('Rear_Exhaust_Slot',x+(i-5.5)*w*.052,y+h*.26,z-.119,w*.025,h*.08,.005,'Dark',0)
  for xx in [x-w*.35,x+w*.35]:
   for yy in [y-h*.27,y+h*.27]:
    cyl('Captive_Back_Screw',(xx,yy,z-.116),(xx,yy,z-.123),.006,'Steel',8)
    box('Screw_Head_Slot',xx,yy,z-.124,.007,.0015,.001,'Dark',0)
  box('IO_Recess',x,y-h*.28,z-.121,w*.43,h*.12,.011,'Dark',.004)
  for j in range(3):
   xx=x+(j-1)*w*.12;box('IO_Socket_Surround',xx,y-h*.28,z-.130,w*.085,h*.065,.012,'Steel',.002)
   box('IO_Socket_Interior',xx,y-h*.28,z-.138,w*.064,h*.038,.003,'Rubber',0)
  for j in range(4):cyl('OSD_Key',(x-w*.31+j*.025,y-h*.5-.020,z+.050),(x-w*.31+j*.025,y-h*.5-.020,z+.054),.005,'Dark',10)
  box('VESA_Plate',x,y,z-.135,min(w*.25,.22),min(h*.4,.20),.028,'Steel',.006)

def monitor_stand(x,y,z,w,h,top=.8225):
 # Pivot sits behind the VESA plate; the arm is physically connected to the desk foot.
 box('Monitor_Base',x,top+.022,z-.08,.34,.032,.26,'Steel',.014)
 box('Base_Rubber_Foot',x,top+.003,z-.08,.30,.006,.22,'Rubber',0)
 box('Monitor_Lift_Column',x,(top+.035+y-.08)/2,z-.18,.052,y-.08-top-.035,.052,'Steel',.012)
 cyl('Tilt_Hinge',(x-.065,y-.07,z-.18),(x+.065,y-.07,z-.18),.040,'Dark',16)
 for xx in [x-.071,x+.071]:cyl('Hinge_Cap',(xx-.004,y-.07,z-.18),(xx+.004,y-.07,z-.18),.024,'Steel',12)
 box('VESA_Arm_Link',x,y-.035,z-.158,.07,.14,.045,'Steel',.009)
 tube('Display_Power_Lead',[(x-w*.12,y-h*.28,z-.143),(x-w*.12,y-h*.28-.065,z-.19),(x-.04,.98,z-.215),(x-.04,top+.065,z-.215),(x-.012,top+.012,z-.12),(x-.012,.72,z-.12)],.006)
 tube('Display_Data_Lead',[(x,y-h*.28,z-.143),(x+.04,y-h*.28-.06,z-.20),(x+.04,.94,z-.215),(x+.04,top+.065,z-.215),(x+.012,top+.012,z-.12),(x+.012,.72,z-.12)],.005,'Teal')
 for yy in [.91,1.0]:box('Cable_Management_Clip',x,yy,z-.225,.11,.016,.024,'Dark',.003)
 cyl('Cable_Desk_Gland',(x,top,z-.12),(x,top+.006,z-.12),.028,'Dark',20)
def pull(x,y,z,w=.20):
 for xx in [x-w/2,x+w/2]:cyl('Grip_Stand',(xx,y,z),(xx,y,z+.035),.008,'Steel',10)
 cyl('Pull',(x-w/2,y,z+.035),(x+w/2,y,z+.035),.011,'Steel',12)
def keyboard(x,y,z):
 box('Keyboard_Chassis',x,y,z,.46,.028,.16,'Dark',.012)
 for j in range(4):
  for i in range(12):box('Keycap',x-.209+i*.038,y+.018,z-.054+j*.034,.027,.010,.023,'Coat',.002)
 box('Spacebar',x,y+.02,z+.071,.19,.009,.018,'Coat',.002)
def phone(x,y,z):
 box('Secure_Telephone',x,y+.028,z,.17,.056,.23,'Dark',.015)
 for i in range(3):
  for j in range(3):box('Dial_Key',x-.04+i*.04,y+.061,z-.01+j*.04,.021,.010,.021,'Coat',.003)
 tube('Handset',[(x-.075,y+.09,z-.07),(x-.07,y+.14,z-.08),(x+.07,y+.14,z-.08),(x+.075,y+.09,z-.07)],.025,'Rubber')
 tube('Phone_Cable',[(x-.08,y+.08,z-.08),(x-.14,y+.01,z-.08),(x-.14,y+.01,z+.10)],.006,'Dark')
def desk(kind):
 reset();box('Worktop',0,.785,0,1.95,.075,.86,'Coat',.025);box('Soft_Edge',0,.762,.437,1.89,.035,.025,'Rubber',.009)
 for x in [-.83,.83]:
  box('Desk_Pedestal',x,.39,-.10,.22,.69,.53,'Steel',.025);box('Desk_Foot',x,.055,.02,.29,.10,.79,'Dark',.025)
 box('UnderDesk_PC',.58,.40,-.16,.29,.53,.44,'Dark',.018)
 for j in range(8):box('PC_Vent',.58,.25+j*.037,.064,.23,.012,.008,'Steel',.001)
 for x,k in [(-.45,7 if kind=='A' else 8),(.45,8 if kind=='A' else 6)]:
  display(x,1.24,-.16,.71,.44,k);monitor_stand(x,1.24,-.16,.71,.44)
 keyboard(-.22,.835,.20);box('Mouse_Pad',.33,.827,.23,.22,.006,.23,'Rubber',.006);box('Optical_Mouse',.33,.850,.23,.064,.040,.103,'Dark',.021);phone(.74,.829,.25)
 # Push-to-talk / access keypad with tactile buttons and a recessed reader.
 box('Access_Keypad',-.72,.851,.22,.16,.045,.21,'Teal',.012)
 for j in range(3):
  for i in range(3):box('Access_Key',-.766+i*.046,.878,.19+j*.039,.028,.011,.025,'Dark',.003)
 box('Credential_Slot',-.72,.877,.147,.12,.004,.017,'Dark',0)
 for xx in [-.66,-.08]:cyl('Desk_Cable_Grommet',(xx,.823,-.33),(xx,.830,-.33),.029,'Dark',20)
 box('Desk_Cable_Basket',0,.70,-.27,1.55,.10,.20,'Dark',.012)
 for i in range(12):box('Basket_Vent',-.69+i*.125,.70,-.164,.064,.05,.003,'Steel',0)
 cyl('Seat_Power_Gland',(-.82,.13,-.25),(-.82,.20,-.25),.023,'Dark',12)
 export('SC_OperatorDesk_'+kind)
for k in ['A','B']:desk(k)
reset()
for x in [-1.42,0,1.42]:
 box('Wall_Cabinet_Base',x,.43,-.035,1.39,.83,.67,'Dark',.018);box('Cabinet_Front',x,.44,.315,1.32,.73,.035,'Coat',.012);pull(x,.71,.340,.27)
 for yy in [.15,.19,.23]:box('Base_Vent',x,yy,.342,1.12,.015,.008,'Dark',.002)
 cyl('VideoWall_Support',(x,.75,-.16),(x,3.25,-.16),.048,'Steel',16)
for row in range(2):
 for col in range(3):
  xx=(col-1)*1.42;yy=1.49+row*.90;display(xx,yy,.05,1.33,.82,1+row*3+col)
  box('Screen_VESA_Carriage',xx,yy,-.155,.24,.20,.13,'Steel',.009)
  tube('Screen_Data_Pigtail',[(xx-.15,yy-.23,-.09),(xx-.15,yy-.34,-.24),(xx+.10,yy-.36,-.27),(xx+.10,.97,-.27)],.008)
for yy in [1.49,2.39]:box('VideoWall_Crossrail',0,yy,-.24,4.25,.085,.075,'Steel',.012)
box('VideoWall_Header',0,2.99,-.04,4.28,.10,.15,'Steel',.018)
for z in [-.26,-.20]:tube('VideoWall_PowerBus',[(-2,.48,z),(-2,1.0,z),(2,1.0,z),(2,.48,z)],.017)
export('SC_VideoWall')
reset()
cyl('Chair_Column',(0,.12,0),(0,.46,0),.055,'Steel',20)
for a in range(5):
 t=a*math.tau/5;x,z=math.cos(t)*.30,math.sin(t)*.30;tube('Castor_Spider',[(0,.17,0),(x*.6,.13,z*.6),(x,.085,z)],.022,'Steel');cyl('Wheel',(x-.032,.052,z),(x+.032,.052,z),.049,'Rubber',16)
box('Padded_Seat',0,.47,.025,.51,.095,.49,'Fabric',.040);box('Backrest',0,.83,-.20,.48,.59,.095,'Fabric',.042)
for x in [-.29,.29]:tube('Arm_Support',[(x*.7,.41,-.08),(x,.61,-.08),(x,.68,.12)],.018,'Steel');box('Arm_Pad',x,.70,.05,.075,.045,.34,'Rubber',.021)
box('Lumbar_Support',0,.72,-.14,.37,.17,.04,'Dark',.019);export('SC_TaskChair')
for kind in ['Recorder','Network','UPS']:
 reset();w=.76;h=1.20 if kind=='UPS' else 2.2;d=.80
 box('Rack_Plinth',0,.055,0,w+.04,.11,d+.04,'Dark',.018)
 for x in [-w/2,w/2]:box('Rack_Side',x,h/2,0,.028,h,d,'Coat',.010)
 box('Solid_Back',0,h/2,-d/2,w,h,.025,'Dark',.006);box('Rack_Top',0,h,0,w,.03,d,'Steel',.006)
 for x in [-.33,.33]:box('Mount_Rail',x,h/2,.34,.031,h-.08,.035,'Steel',.005)
 if kind=='Recorder':
  for row in range(8):
   y=.22+row*.225;box('Recorder_Unit',0,y,.18,.65,.198,.39,'Dark',.010)
   for col in range(3):
    x=(col-1)*.205;box('Drive_Caddy',x,y,.387,.188,.157,.022,'Steel',.006);pull(x,y,.4,.11);box('Drive_Status',x+.07,y+.051,.422,.012,.010,.006,'Indicator',.002)
  display(0,2.04,.385,.39,.10,8)
 elif kind=='Network':
  for row in range(7):
   y=.22+row*.27;box('Switch_Unit',0,y,.16,.65,.18,.43,'Dark',.009)
   for col in range(10):
    x=-.27+col*.06;box('RJ45_Recess',x,y+.02,.383,.035,.028,.012,'Steel',.003);box('RJ45_Port',x,y+.02,.391,.027,.020,.006,'Rubber',.002)
   if row%2==0:
    for col in range(5):
     x=-.24+col*.12;tube('Patch_Lead',[(x,y+.02,.405),(x,y-.065,.45),(x+.035,y-.11,.44),(x+.035,y-.19,.407)],.007,'Teal')
  display(0,2.05,.385,.4,.11,10)
 else:
  for y in [.25,.55,.85]:box('Battery_Drawer',0,y,.36,.64,.26,.045,'Steel',.010);pull(0,y,.389,.24)
  display(0,1.07,.385,.37,.12,10)
 if kind!='UPS':
  for x in [-.35,.35]:box('Door_Frame',x,h/2,.43,.034,h,.035,'Steel',.006)
  for y in [.03,h-.03]:box('Door_Frame',0,y,.43,.70,.034,.035,'Steel',.006)
  box('Door_Glass',0,h/2,.427,.654,h-.12,.006,'Glass',.001);pull(.29,h*.52,.45,.09)
 export('SC_'+kind+'Rack')
reset()
box('Radio_Cabinet',0,.46,-.06,1.40,.88,.55,'Coat',.025);box('Worktop',0,.925,0,1.46,.05,.68,'Steel',.016)
for x in [-.35,.35]:box('Cabinet_Door',x,.47,.229,.665,.78,.025,'Dark',.012);pull(x,.74,.25,.24)
for i in range(5):
 x=(i-2)*.24;box('Charge_Cradle',x,.97,-.02,.19,.06,.19,'Dark',.012);box('Handheld_Radio',x,1.105,-.025,.10,.23,.062,'Dark',.018);box('Radio_Screen',x,1.135,.012,.064,.047,.006,'Teal',.003);cyl('Antenna',(x-.025,1.21,-.025),(x-.025,1.40,-.025),.006,'Rubber',10)
 for j in range(4):box('Speaker_Slot',x,1.04+j*.014,.010,.064,.006,.006,'Steel',.001)
box('Dispatch_Panel',0,1.62,-.25,1.30,.43,.10,'Dark',.018);display(-.24,1.63,-.186,.63,.31,6)
for i in range(3):cyl('Channel_Selector',(.23+i*.135,1.57,-.19),(.23+i*.135,1.57,-.15),.035,'Steel',16)
tube('Microphone_Arm',[(.58,.97,.15),(.58,1.19,.13),(.46,1.34,.13)],.009,'Dark');cyl('Microphone',(.46,1.34,.13),(.44,1.38,.13),.023,'Dark',16)
export('SC_RadioDutyStation')
reset()
for x in [-.38,.38]:
 box('Locker_Case',x,1.05,-.03,.73,2.10,.58,'Coat',.024);box('Locker_Door',x,1.08,.274,.67,2.00,.028,'Teal',.016);pull(x+.19,1.03,.299,.075)
 for y in [.24,.28,.32,1.78,1.82,1.86]:box('Locker_Vent',x,y,.294,.40,.018,.010,'Dark',.002)
 box('Number_Label',x,1.62,.295,.11,.045,.001,'Paper',0);cyl('Keyhole',(x+.19,.91,.300),(x+.19,.91,.306),.009,'Dark',12)
box('Locker_Plinth',0,.055,0,1.54,.11,.68,'Dark',.018);export('SC_GearLockers')
reset()
box('Archive_Case',0,.91,0,1.24,1.82,.55,'Coat',.022)
for row in range(5):
 y=.23+row*.31
 for x in [-.30,.30]:
  box('Sealed_RecordDrawer',x,y,.287,.57,.28,.028,'Dark',.009);pull(x,y,.313,.21);box('Index_Window',x,y+.086,.305,.16,.036,.003,'Paper',0)
box('Archive_Top',0,1.84,0,1.27,.05,.59,'Steel',.011);export('SC_RecordArchive')
reset()
box('Review_Worktop',0,.785,0,1.75,.06,.76,'Coat',.025)
for x in [-.72,.72]:box('Review_Leg',x,.39,-.02,.10,.74,.56,'Steel',.022)
display(-.35,1.17,-.17,.72,.45,9);monitor_stand(-.35,1.17,-.17,.72,.45,.815);keyboard(-.35,.833,.20)
box('Review_Cable_Channel',-.35,.72,-.27,.52,.10,.19,'Dark',.009)
box('Evidence_Tray',.45,.835,.06,.54,.05,.41,'Dark',.016)
for i in range(3):box('Flat_RecordEnvelope',.39+i*.026,.864+i*.001,.06,.37,.0008,.27,'Paper',0)
box('Card_Reader',.67,.86,.27,.12,.06,.17,'Teal',.012);box('Read_Slot',.67,.887,.30,.074,.008,.10,'Dark',.002);phone(.62,.825,-.20);export('SC_IncidentReview')
# Architectural shell bands follow the existing 7 m sphere and leave all three portal sectors open.
def sphere_patch(name,a0,a1,p0,p1,r0,r1,mat,na=6,np=4):
 vs=[]
 for r in [r0,r1]:
  for j in range(np+1):
   phi=p0+(p1-p0)*j/np
   for i in range(na+1):a=a0+(a1-a0)*i/na;vs.append((r*math.cos(phi)*math.cos(a),r*math.sin(phi),r*math.cos(phi)*math.sin(a)))
 n=(na+1)*(np+1);fs=[]
 for j in range(np):
  for i in range(na):k=j*(na+1)+i;fs.extend([(k,k+1,k+na+2,k+na+1),(n+k,n+k+na+1,n+k+na+2,n+k+1)])
 per=list(range(na+1))+[j*(na+1)+na for j in range(1,np+1)]+[np*(na+1)+i for i in range(na-1,-1,-1)]+[j*(na+1) for j in range(np-1,0,-1)]
 for a,b in zip(per,per[1:]+per[:1]):fs.append((a,b,n+b,n+a))
 return mesh(name,vs,fs,mat,.0018 if p1<1.4 else 0,True)
doors=[-75.9637,155.556,3.0128]
def portal(a):return any(abs((a-b+180)%360-180)<28 for b in doors)
reset();bands=[.016,.18,.36,.58,.85,1.12,1.38,1.565]
for sector in range(24):
 for j in range(len(bands)-1):
  a=sector*15+7.5
  if j<3 and portal(a):continue
  sphere_patch('Dome_Panel',math.radians(sector*15+.09),math.radians((sector+1)*15-.09),bands[j]+.001,bands[j+1]-.001,6.963,6.983,'Coat')
for a in [30,90,150,210,270,330]:sphere_patch('Continuous_Meridian',math.radians(a-.48),math.radians(a+.48),.58 if portal(a) else .007,1.38,6.855,6.945,'Steel',2,40)
for phi in [.58,1.38]:sphere_patch('Structural_Ring',0,math.tau,phi-.008,phi+.008,6.85,6.94,'Steel',128,2)
export('SC_C02_Architecture',True)
reset();cyl('Epoxy_Disc',(0,-.004,0),(0,.009,0),6.86,'Floor',160)
box('Operator_FloorInset',0,.011,4.1,4.9,.003,3.1,'Dark',0)
for x in [-2.47,2.47]:box('Inset_Edge',x,.014,4.1,.035,.003,3.1,'Steel',0)
for z in [2.54,5.66]:box('Inset_Edge',0,.014,z,4.97,.003,.035,'Steel',0)
for x,z in [(3.7,3.2),(-4.7,-1.3),(-2.4,-3.0)]:
 box('Service_Hatch',x,.014,z,.62,.010,.62,'Steel',.008);box('Flush_Pull',x,.021,z+.20,.17,.003,.025,'Dark',0)
export('SC_C02_Floor',True)
reset()
for a in [0,90,180,270]:
 angle=math.radians(a);x,z=3.64*math.cos(angle),3.64*math.sin(angle)
 box('Suspended_Luminaire',x,3.37,z,1.50,.13,.32,'Steel',.023);box('Diffuser',x,3.288,z,1.39,.035,.265,'Lamp',.012)
 for dx in [-.59,.59]:cyl('Suspension_Rod',(x+dx,3.43,z),(x+dx,math.sqrt(6.94**2-(x+dx)**2-z*z),z),.016,'Steel',12)
for yy in [2.55,2.67]:
 pts=[(math.cos(math.radians(a))*6.42,yy,math.sin(math.radians(a))*6.42) for a in range(30,134,2)];tube('North_ServiceBus',pts,.025,'Dark')
for x,z in [(3.45,4.75),(4.55,3.8),(0,5.4)]:
 r=math.hypot(x,z);tube('Rack_PowerDrop',[(x*6.42/r,2.67,z*6.42/r),(x,2.67,z),(x,2.25,z),(x,.10,z)],.027,'Dark')
export('SC_C02_OverheadServices',True)
if os.environ.get('C02_MODELS'):
 previous=json.loads((H/'model_manifest.json').read_text(encoding='utf-8'));previous.update(manifest);manifest=previous
(H/'model_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
