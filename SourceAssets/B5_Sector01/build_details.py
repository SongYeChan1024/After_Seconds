import bpy,bmesh,math,json,sys
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[1];A=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model'
OUT=A/'Environment/B5';manifest={}
def reset():
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;bpy.context.scene.unit_settings.system='METRIC'
 global mats;mats={}
 for n,c,metal,rough in [('Coat',(.62,.70,.74,1),.05,.48),('Steel',(.29,.34,.38,1),.92,.32),('Dark',(.028,.041,.05,1),.1,.68),('Lamp',(.72,.82,.88,1),0,.35),('Floor',(.22,.28,.32,1),.04,.7),('Linen',(.6,.65,.67,1),0,.92),('Paper',(.69,.72,.70,1),0,.8),('Screen',(.025,.10,.12,1),.05,.45),('Mirror',(.7,.76,.78,1),1,.08)]:
  m=bpy.data.materials.new('S1_'+n);m.use_nodes=True;m.diffuse_color=c;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=c;bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;mats[n]=m
def xyz(x,y,z):return (-x,-z,y)
def mesh(n,vs,fs,mat='Steel',bev=.003,smooth=False):
 me=bpy.data.meshes.new(n);me.from_pydata([xyz(*v) for v in vs],[],fs);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);me.materials.append(mats[mat]);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 for p in me.polygons:p.use_smooth=smooth
 if bev:
  b=o.modifiers.new('Manufactured_Edge_Bevel','BEVEL');b.width=bev;b.segments=3;b.limit_method='ANGLE';b.angle_limit=.45;b.harden_normals=True
  w=o.modifiers.new('Weighted_Normal','WEIGHTED_NORMAL');w.keep_sharp=True
 o['bevel_width_m']=bev;return o
def box(n,x,y,z,w,h,d,mat='Steel',bev=.004):
 v=[(x+dx*w/2,y+dy*h/2,z+dz*d/2) for dx,dy,dz in [(-1,-1,-1),(1,-1,-1),(1,-1,1),(-1,-1,1),(-1,1,-1),(1,1,-1),(1,1,1),(-1,1,1)]]
 return mesh(n,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,min(bev,min(w,h,d)*.22))
def cyl(n,a,b,r,mat='Steel',verts=20):
 aa,bb=Vector(xyz(*a)),Vector(xyz(*b));v=bb-aa;bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=v.length,location=(aa+bb)/2);o=bpy.context.object;o.name=n;o.rotation_euler=v.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);o.data.materials.append(mats[mat]);be=o.modifiers.new('Edge_Bevel','BEVEL');be.width=min(.002,r*.15);be.segments=2;o['bevel_width_m']=be.width;return o
def tube(n,points,r=.015,mat='Steel',sides=8):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=r;cu.bevel_resolution=2
 sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
 for p,v in zip(sp.points,points):p.co=(*xyz(*v),1)
 o=bpy.data.objects.new(n,cu);bpy.context.collection.objects.link(o);o.data.materials.append(mats[mat]);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);o['bevel_width_m']=r;return o
def export(name,props=False,collide=True):
 objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];bevelled=sum(bool(o.get('bevel_width_m',0)) for o in objs)
 for o in objs:
  if not o.data.uv_layers:o.data.uv_layers.new(name='UVMap')
  for p in o.data.polygons:
   axes=[i for i in range(3) if i!=max(range(3),key=lambda j:abs(p.normal[j]))]
   for li in p.loop_indices:
    c=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;o.data.uv_layers.active.data[li].uv=(c[axes[0]]*.7,c[axes[1]]*.7)
 bpy.ops.wm.save_as_mainfile(filepath=str(H/(name+'.blend')))
 dep=bpy.context.evaluated_depsgraph_get();out=[]
 for o in objs:
  me=bpy.data.meshes.new_from_object(o.evaluated_get(dep),depsgraph=dep);n=bpy.data.objects.new(o.name,me);bpy.context.collection.objects.link(n);n.matrix_world=o.matrix_world.copy();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();out.append(n)
 bpy.ops.object.select_all(action='DESELECT')
 for o in out:o.select_set(True)
 bpy.context.view_layer.objects.active=out[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
 # Normalize the assembled object's origin without moving its vertices.
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 folder=A/('Props/B5' if props else 'Environment/B5');folder.mkdir(parents=True,exist_ok=True)
 bpy.ops.export_scene.fbx(filepath=str(folder/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE',use_custom_props=True)
 manifest[name]=dict(asset=str(folder/(name+'.fbx')).replace(str(R/'Unity/After_Seconds_Build_V0.01')+'\\',''),parts=len(objs),beveled_parts=bevelled,triangles=len(o.data.polygons),props=props,collide=collide)
 print('EXPORTED',name,len(o.data.polygons),flush=True)

# Structural ribs follow the actual 10 m hemisphere; exclude both entrance sectors.
reset()
for deg in [30,60,150,180,210,240,270,300,330]:
 a=math.radians(deg);ca,sa=math.cos(a),math.sin(a)
 for seg in range(8):
  lo=math.radians(seg*10.7+.08);hi=math.radians((seg+1)*10.7-.08);vs=[]
  for tangent in [-.09,.09]:
   for radius in [9.82,9.96]:
    for j in range(9):
     p=lo+(hi-lo)*j/8;rr=radius*math.cos(p);vs.append((ca*rr-sa*tangent,radius*math.sin(p),sa*rr+ca*tangent))
  k=9;fs=[]
  for j in range(8):fs.extend([(j,j+1,k+j+1,k+j),(2*k+j,3*k+j,3*k+j+1,2*k+j+1),(j,2*k+j,2*k+j+1,j+1),(k+j,k+j+1,3*k+j+1,3*k+j)])
  fs.extend([(0,k,3*k,2*k),(k-1,3*k-1,4*k-1,2*k-1)]);mesh('Segmented_Rib',vs,fs,'Coat',.006,True)
  # Fasteners on the inner face at the joint.
  p=hi-.025;rr=9.805*math.cos(p);yy=9.805*math.sin(p)
  cyl('Joint_Bolt',(ca*rr,yy,sa*rr),(ca*(rr-.012),yy-.012,sa*(rr-.012)),.023,'Steel',6)
 box('Rib_Base',ca*9.84,.06,sa*9.84,.32,.12,.32,'Steel',.01)
export('S1_VaultRibs')

reset()
for deg in range(5,360,10):
 # Portal opening arcs: east around +5 deg, north around +104 deg in Unity Z.
 if min(abs((deg-5+180)%360-180),abs((deg-104+180)%360-180))<15:continue
 # World local z is north, so doorway angles are 5 and104 degrees.
 lo=math.radians(deg-4.9);hi=math.radians(deg+4.9);vs=[];nx=8;ny=4
 for depth in [0,.024]:
  for j in range(ny+1):
   y=.025+1.25*j/ny;rad=math.sqrt(100-y*y)-.034-depth
   for i in range(nx+1):a=lo+(hi-lo)*i/nx;vs.append((rad*math.cos(a),y,rad*math.sin(a)))
 N=(nx+1)*(ny+1);fs=[]
 for j in range(ny):
  for i in range(nx):k=j*(nx+1)+i;fs.extend([(k,k+1,k+nx+2,k+nx+1),(N+k,N+k+nx+1,N+k+nx+2,N+k+1)])
 per=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,ny+1)]+[ny*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1) for j in range(ny-1,0,-1)]
 for a,b in zip(per,per[1:]+per[:1]):fs.append((a,b,N+b,N+a))
 mesh('Curved_Cove',vs,fs,'Coat',.003,True)
export('S1_CoveRing')

reset();cyl('FloorFinish',(0,-.012,0),(0,.006,0),9.96,'Floor',192)
# Flush sealed control joints give the room scale without raised trip strips.
for offset in range(-8,9,2):
 half=math.sqrt(9.94**2-offset**2)
 box('FloorControlJoint',offset,.0085,0,.006,.001,half*2,'Dark',0)
 box('FloorControlJoint',0,.0085,offset,half*2,.001,.006,'Dark',0)
export('S1_FloorFinish',collide=False)

reset()
box('Wall_Plate',0,0,-.055,.26,.34,.04,'Steel',.006)
for y in [-.12,.12]:cyl('WallBolt',(0,y,-.025),(0,y,-.008),.018,'Steel',6)
box('Bracket',0,.02,.38,.065,.09,.85,'Steel',.008)
box('Housing',0,0,.82,1.25,.16,.24,'Coat',.012)
box('Diffuser',0,-.095,.82,1.11,.035,.18,'Lamp',.01)
for x in [-.54,.54]:box('End_Seal',x,-.08,.82,.025,.03,.19,'Dark',.003)
export('S1_WallTaskLight')

reset()
box('PrivacyPanel',0,.82,0,1.38,1.55,.065,'Coat',.018)
for x in [-.66,.66]:
 cyl('Upright',(x,.06,0),(x,1.65,0),.025,'Steel')
 box('Foot',x,.026,0,.14,.052,.24,'Steel',.012)
for y in [.1,1.55]:box('Trim',0,y,.041,1.27,.025,.018,'Steel',.003)
box('ReturnPanel',-.67,.81,-.38,.065,1.53,.76,'Coat',.018)
export('S1_PrivacyScreen')

reset()
# An integrated utility tower, with parts designed for a narrow institutional bay.
box('LockerBody',0,.84,0,.58,1.65,.48,'Steel',.012)
for y,h in [(.52,.9),(1.35,.7)]:
 box('DoorSeal',0,y,.249,.535,h,.015,'Dark',.004);box('Door',0,y,.263,.52,h-.025,.022,'Coat',.007)
 cyl('Pull',(.195,y-.09,.30),(.195,y+.09,.30),.012)
for i in range(5):box('VentSlot',0,.17+i*.028,.277,.28,.008,.004,'Dark',.001)
for x in [-.22,.22]:
 for z in [-.17,.17]:cyl('LevelFoot',(x,0,z),(x,.09,z),.033,'Dark')
export('S1_PersonalLocker',props=True)

reset()
# Meal/reading surface accessories, assembled around the local tabletop origin.
box('NotebookPages',-.14,.021,0,.21,.026,.15,'Paper',.004)
for y in [.005,.038]:box('NotebookCover',-.14,y,0,.22,.006,.16,'Dark',.003)
box('Pencil',-.035,.008,.15,.008,.008,.17,'Coat',.002)
cyl('WaterBottleBody',(.17,.015,0),(.17,.16,0),.035,'Steel',24);cyl('WaterBottleCap',(.17,.16,0),(.17,.18,0),.029,'Dark',24)
box('MealTray',0,.012,-.23,.39,.024,.24,'Steel',.008)
for x in [-.185,.185]:box('TrayLip',x,.035,-.23,.014,.035,.23,'Steel',.004)
for z in [-.34,-.12]:box('TrayLip',0,.035,z,.38,.035,.014,'Steel',.004)
cyl('CupBody',(.11,.025,-.23),(.11,.115,-.23),.032,'Coat',24);cyl('CupInside',(.11,.114,-.23),(.11,.116,-.23),.026,'Dark',24)
export('S1_TabletopKit',props=True,collide=False)

reset()
for i in range(3):box('FoldedTowel',0,.02+i*.027,0,.27,.038,.19,'Linen',.016)
box('SoapBottle',.21,.07,0,.07,.13,.055,'Coat',.012);cyl('Pump',(.21,.14,0),(.21,.17,0),.012,'Steel');box('PumpNozzle',.23,.17,0,.065,.012,.014,'Dark',.003)
cyl('TissueRoll',(-.22,.065,0),(-.22,.065,.1),.052,'Paper',32);cyl('RollCore',(-.22,.065,.101),(-.22,.065,.103),.015,'Dark',20)
export('S1_HygieneKit',props=True,collide=False)

reset()
for x,z in [(-.085,.01),(.075,-.025)]:
 box('SlipperSole',x,.015,z,.095,.028,.24,'Dark',.015);box('SlipperUpper',x,.045,z+.03,.10,.06,.115,'Linen',.02)
export('S1_Slippers',props=True,collide=False)
reset()
box('PersonalBox',0,.11,0,.4,.2,.3,'Coat',.015);box('LidGasket',0,.206,0,.405,.012,.305,'Dark',.003);box('Lid',0,.224,0,.42,.026,.32,'Coat',.01)
for x in [-.17,.17]:box('Catch',x,.19,.167,.034,.065,.015,'Steel',.003)
cyl('Handle',(-.06,.12,.17),(.06,.12,.17),.012,'Dark')
export('S1_PersonalBox',props=True)

reset()
box('MirrorFrame',0,.30,0,.44,.64,.05,'Steel',.015);box('Mirror',0,.30,.028,.39,.59,.008,'Mirror',.007)
export('S1_Mirror')
reset()
box('CallHousing',0,.13,0,.18,.26,.07,'Coat',.015);cyl('CallButton',(0,.12,.034),(0,.12,.05),.038,'Dark',24);box('CallStatus',0,.22,.039,.05,.008,.008,'Lamp',.002)
for i in range(4):box('SpeakerSlot',0,.055+i*.012,.038,.09,.004,.005,'Dark',.001)
export('S1_CallPanel')
reset()
cyl('ClockRim',(0,.18,0),(0,.18,.06),.18,'Steel',64);cyl('ClockFace',(0,.18,.06),(0,.18,.066),.16,'Paper',64)
for i in range(12):
 a=i*math.pi/6;cyl('ClockMark',(math.sin(a)*.135,.18+math.cos(a)*.135,.067),(math.sin(a)*.15,.18+math.cos(a)*.15,.067),.003,'Dark',6)
cyl('HourHand',(0,.18,.07),(-.065,.21,.07),.004,'Dark',6);cyl('MinuteHand',(0,.18,.072),(.085,.26,.072),.003,'Dark',6)
export('S1_Clock')
reset()
box('RecordBoard',0,.18,0,.25,.36,.025,'Steel',.006);box('RecordPaper',0,.18,.015,.21,.30,.004,'Paper',.001)
box('Clip',0,.33,.026,.075,.026,.018,'Steel',.004)
for y in [.1,.13,.16,.19,.22,.25]:box('WrittenLine',-.01,y,.019,.15,.002,.002,'Dark',.0003)
export('S1_RecordBoard')
reset()
box('PanelMount',0,.15,0,.25,.33,.03,'Steel',.007);box('IDPlate',0,.15,.019,.21,.29,.012,'Coat',.004)
# Embossed geometric specimen ID, without explanatory room signage.
font=bpy.data.curves.new('Specimen_ID','FONT');font.body='S-03';font.size=.06;font.extrude=.0006;font.align_x='CENTER';o=bpy.data.objects.new('Specimen_ID',font);bpy.context.collection.objects.link(o);o.location=xyz(0,.17,.028);o.rotation_euler=(math.pi/2,0,math.pi);o.scale.x=-1;o.data.materials.append(mats['Dark']);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
for i in range(17):box('Barcode',-.07+i*.008,.07,.028,.003,.04,.002,'Dark',.0003)
export('S1_SpecimenPlate')

reset()
# Service pipe assembly for the medical apparatus: overhead, clear of circulation.
tube('SignalConduit',[(0,0,0),(0,2.6,0),(.15,2.85,0),(.6,2.85,0)],.035,'Steel')
box('AnchoredBase',0,.028,0,.24,.055,.24,'Steel',.007)
for x in [-.085,.085]:
 for z in [-.085,.085]:cyl('AnchorBolt',(x,.055,z),(x,.073,z),.012,'Steel',6)
cyl('CameraMountCollar',(.52,2.82,0),(.52,2.9,0),.065,'Steel',24)
for y in [.3,1.9,2.55]:
 box('PipeClamp',0,y,-.025,.12,.07,.08,'Steel',.004)
 box('Mount',0,y,-.085,.18,.12,.03,'Coat',.006)
export('S1_ServiceRiser')

reset()
box('ServiceBackboard',0,1.2,0,1.34,2.35,.06,'Coat',.012)
for x in [-.58,.58]:
 box('Post',x,1.12,-.06,.065,2.24,.08,'Steel',.006)
 box('BasePlate',x,.025,0,.22,.05,.30,'Steel',.008)
 for z in [-.10,.10]:cyl('AnchorBolt',(x,.05,z),(x,.067,z),.012,'Steel',6)
export('S1_ServiceBackboard')
reset()
box('ShelfTop',0,.94,0,.58,.035,.38,'Steel',.008)
for x in [-.24,.24]:
 for z in [-.14,.14]:
  cyl('ShelfLeg',(x,.025,z),(x,.92,z),.018,'Steel')
  cyl('RubberFoot',(x,0,z),(x,.045,z),.023,'Dark')
for z in [-.14,.14]:cyl('CrossBrace',(-.24,.2,z),(.24,.2,z),.013,'Steel')
export('S1_HygieneShelf',props=True)

reset()
box('Worktop',0,.745,0,1.2,.045,.62,'Coat',.012)
box('TopUnderEdge',0,.714,0,1.15,.018,.57,'Dark',.005)
for x in [-.53,.53]:
 for z in [-.24,.24]:
  box('DeskLeg',x,.35,z,.035,.70,.035,'Steel',.005)
  box('DeskFoot',x,.012,z,.05,.024,.05,'Dark',.007)
box('RearBrace',0,.40,-.26,1.1,.055,.035,'Steel',.005)
box('ModestyPanel',0,.56,-.275,1.08,.28,.025,'Coat',.006)
box('DrawerCase',-.37,.59,.025,.32,.24,.49,'Steel',.008)
for y in [.545,.655]:
 box('DrawerSeal',-.37,y,.278,.30,.10,.012,'Dark',.003)
 box('DrawerFace',-.37,y,.289,.285,.087,.016,'Coat',.006)
 cyl('DrawerPull',(-.43,y,.31),(-.31,y,.31),.008,'Steel')
cyl('StoolSeat',(0,.425,.73),(0,.465,.73),.18,'Coat',40)
for x in [-.12,.12]:
 for z in [.61,.85]:
  cyl('StoolLeg',(x,.015,z),(x,.425,z),.016,'Steel')
  cyl('StoolFoot',(x,0,z),(x,.025,z),.022,'Dark')
export('S1_LivingDesk',props=True)

reset()
# Spherical collars cover the coplanar tunnel/dome junction seam at C01 only.
design=json.loads((R/'Docs/도면/Decision/원형공동/facility_layout.json').read_text('utf-8'))
floor=next(f for f in design['floors'] if f['id']=='B5')
for t in floor['tunnels']:
 if t['id'] not in ['B5-T01','B5-T03']:continue
 p=Vector((t['p'][0]+15,0,-t['p'][1]+10));q=Vector((t['q'][0]+15,0,-t['q'][1]+10));fw=(q-p).normalized();right=Vector((fw.z,0,-fw.x))
 vs=[];count=65;spring=t['h']-t['w']/2
 for sphere_r in [9.92,9.97]:
  for profile_r in [t['w']/2-.018,t['w']/2+.28]:
   for i in range(count):
    a=math.pi*i/(count-1);cross=profile_r*math.cos(a);y=spring+profile_r*math.sin(a);u=p+right*cross;d=u.dot(fw);along=-d+math.sqrt(max(0,d*d+sphere_r*sphere_r-y*y-u.length_squared));pt=u+fw*along;vs.append((pt.x,y,pt.z))
 fs=[];k=count
 for i in range(k-1):fs.extend([(i,i+1,k+i+1,k+i),(2*k+i,3*k+i,3*k+i+1,2*k+i+1),(i,2*k+i,2*k+i+1,i+1),(k+i,k+i+1,3*k+i+1,3*k+i)])
 fs.extend([(0,k,3*k,2*k),(k-1,3*k-1,4*k-1,2*k-1)])
 mesh(t['id']+'_C01_Collar',vs,fs,'Coat',.004,True)
export('S1_PortalCollars')

(H/'detail_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('DETAILS_DONE',len(manifest),sum(x['triangles'] for x in manifest.values()),flush=True)
