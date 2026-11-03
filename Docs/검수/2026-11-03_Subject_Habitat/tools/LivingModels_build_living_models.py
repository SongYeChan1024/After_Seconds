# 작성자 송예찬 / 2026-11-03
# [의사코드]
# 1. 실제 사람 크기의 생활·검사 소품 다섯 묶음을 흰색/강철/직물 재질로 만든다.
# 2. 바닥 중앙 피벗과 배치 앵커를 기록하고 Unity용 FBX를 분리해 내보낸다.
# 3. Blender 원본과 실제 모델 렌더를 저장하고 닫힌 메시/삼각형 수를 검사한다.
# [코딩]
import bpy, math, json, pathlib, hashlib, bmesh
from mathutils import Vector
W=pathlib.Path(__file__).parent
R=W.parents[2]
SRC=R/'SourceAssets/SubjectHabitat'
SRC.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
PALETTE={
 'HM_ClinicalWhite':([.72,.76,.77,1],.12,.48),
 'HM_BlackFrame':([.025,.035,.04,1],.65,.37),
 'HM_BrushedSteel':([.39,.45,.48,1],.85,.34),
 'HM_Linen':([.63,.70,.68,1],0,.8),
 'HM_BlueLED':([.12,.65,.85,1],.12,.32),
 'HM_FoodNeutral':([.42,.34,.20,1],0,.83),
 'HM_Screen':([.012,.032,.04,1],.05,.34),
 'HM_PaleLabel':([.72,.86,.87,1],.05,.54),
}
M={}
for n,(color,metal,rough) in PALETTE.items():
 m=bpy.data.materials.new(n);m.diffuse_color=color;m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color;bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
 if n=='HM_BlueLED':bs.inputs['Emission Color'].default_value=color;bs.inputs['Emission Strength'].default_value=.8
 M[n]=m

def mat(o,m):o.data.materials.append(M[m]);return o
def cube(n,loc,dim,m='HM_ClinicalWhite',bevel=.008):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);mat(o,m)
 if bevel:
  mod=o.modifiers.new('Soft manufactured edge','BEVEL');mod.width=min(bevel,min(dim)*.20);mod.segments=2
  bpy.ops.object.modifier_apply(modifier=mod.name)
 return o
def cyl(n,loc,radius,depth,m='HM_BrushedSteel',vertices=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc);o=bpy.context.object;o.name=n;mat(o,m)
 mod=o.modifiers.new('Rim bevel','BEVEL');mod.width=min(.004,depth*.1);mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
 return o
def uv(n,loc,scale,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=1,location=loc);o=bpy.context.object;o.name=n;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);mat(o,m)
 for p in o.data.polygons:p.use_smooth=True
 return o
def torus(n,loc,major,minor,m='HM_BrushedSteel',scale=(1,1,1),rot=(0,0,0)):
 bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=8,location=loc,major_radius=major,minor_radius=minor,rotation=rot);o=bpy.context.object;o.name=n;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);mat(o,m)
 for p in o.data.polygons:p.use_smooth=True
 return o
def tube(n,points,r=.008,m='HM_BrushedSteel'):
 c=bpy.data.curves.new(n,'CURVE');c.dimensions='3D';c.resolution_u=1;c.bevel_depth=r;c.bevel_resolution=2;c.use_fill_caps=True
 sp=c.splines.new('POLY');sp.points.add(len(points)-1)
 for p,co in zip(sp.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(n,c);bpy.context.collection.objects.link(o);mat(o,m);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');return bpy.context.object
def label(n,text,loc,size=.025,m='HM_PaleLabel'):
 c=bpy.data.curves.new(n,'FONT');c.body=text;c.size=size;c.extrude=.0004;c.align_x='LEFT';c.resolution_u=4
 o=bpy.data.objects.new(n,c);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(math.pi/2,0,0);mat(o,m)
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');return bpy.context.object
def mesh(n,verts,faces,m='HM_BrushedSteel'):
 me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);mat(o,m);return o
def hollow_round(n,loc,outer,inner,height,m='HM_BrushedSteel',bottom=.004):
 # Closed wall/bottom vessel: no invisible top disk, visible open interior.
 N=32;verts=[]
 for r,z in [(outer,0),(outer,height),(inner,height),(inner,bottom)]:
  verts.extend([(loc[0]+r*math.cos(i*2*math.pi/N),loc[1]+r*math.sin(i*2*math.pi/N),loc[2]+z) for i in range(N)])
 verts.append((loc[0],loc[1],loc[2]));verts.append((loc[0],loc[1],loc[2]+bottom));faces=[]
 for ring in range(3):
  for i in range(N):j=(i+1)%N;faces.append((ring*N+i,ring*N+j,(ring+1)*N+j,(ring+1)*N+i))
 for i in range(N):j=(i+1)%N;faces.extend([(4*N,j,i),(4*N+1,3*N+i,3*N+j)])
 return mesh(n,verts,faces,m)
def sink_bowl(n,centre):
 N=32;verts=[]
 loops=[(.29,.22,.96),(.245,.18,.96),(.12,.075,.835),(.12,.075,.82),(.29,.22,.82)]
 for rx,ry,z in loops:
  for i in range(N):
   a=i*2*math.pi/N;ca,sa=math.cos(a),math.sin(a);verts.append((centre[0]+rx*math.copysign(abs(ca)**.5,ca),centre[1]+ry*math.copysign(abs(sa)**.5,sa),z))
 faces=[]
 for k in [0,1,3]:
  for i in range(N):j=(i+1)%N;faces.append((k*N+i,k*N+j,(k+1)*N+j,(k+1)*N+i))
 for i in range(N):j=(i+1)%N;faces.append((4*N+i,4*N+j,j,i))
 faces.append(tuple(2*N+i for i in range(N-1,-1,-1)))
 faces.append(tuple(3*N+i for i in range(N)))
 return mesh(n,verts,faces,'HM_BrushedSteel')
def arc_screen():
 N=48;v=[]
 for rx,ry,z in [(.76,.46,.50),(.76,.46,1.40),(.735,.435,.50),(.735,.435,1.40)]:
  v += [(rx*math.cos(i*math.pi/N),.30+ry*math.sin(i*math.pi/N),z) for i in range(N+1)]
 count=N+1;f=[]
 for i in range(N):
  j=i+1;f.extend([(i,j,count+j,count+i),(2*count+i,3*count+i,3*count+j,2*count+j),(count+i,count+j,3*count+j,3*count+i),(i,2*count+i,2*count+j,j)])
 f.extend([(0,count,3*count,2*count),(N,2*count+N,3*count+N,count+N)])
 return mesh('Hygiene_PrivacyScreen',v,f,'HM_ClinicalWhite')

groups={};anchors={}
def start():return set(bpy.data.objects)
def collect(name,before,keep=()):
 obs=[o for o in bpy.data.objects if o not in before and o.type=='MESH'];main=[o for o in obs if o.name not in keep]
 for group,n in [(main,name+'_Body')]+[([o],o.name) for o in obs if o.name in keep]:
  if not group:continue
  bpy.ops.object.select_all(action='DESELECT')
  for o in group:o.select_set(True)
  bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();group[0].name=n
 groups[name]=[o for o in bpy.data.objects if o not in before and o.type=='MESH']
 return groups[name]

b=start()
cube('Desk_Worktop',(0,.10,.735),(1.1,.55,.055))
cube('Desk_BlackEdge',(0,.10,.702),(1.08,.53,.018),'HM_BlackFrame',.003)
cube('Desk_RearPanel',(0,.34,.39),(1.02,.025,.60),'HM_ClinicalWhite',.003)
for x in [-.46,.46]:
 cube('Desk_FixedLeg',(x,.23,.35),(.055,.15,.70),'HM_BlackFrame')
 cube('Desk_FloorPlate',(x,.22,.015),(.18,.24,.03),'HM_BrushedSteel')
cube('Desk_Drawer',(.28,.08,.61),(.36,.43,.16),'HM_ClinicalWhite')
cube('Desk_DrawerHandle',(.28,-.145,.63),(.20,.015,.015),'HM_BlackFrame',.002)
stool=[]
stool.append(cyl('LivingDesk_FixedStool',(0,-.46,.44),.19,.045,'HM_BlackFrame'))
stool.append(cyl('StoolStem',(0,-.46,.22),.027,.42));stool.append(cyl('StoolBoltedBase',(0,-.46,.015),.145,.03))
for x,y in [(-.08,-.52),(.08,-.52),(0,-.37)]:cyl('StoolAnchorBolt',(x,y,.032),.012,.01,'HM_BlackFrame',12)
# Keep a fixed seat mesh separate for later authored posing.
bpy.ops.object.select_all(action='DESELECT')
for o in stool:o.select_set(True)
bpy.context.view_layer.objects.active=stool[0];bpy.ops.object.join();stool[0].name='LivingDesk_FixedStool'
collect('LivingDesk',b,('LivingDesk_FixedStool',));anchors['LivingDesk']={'MealSurface':[0,.10,.766],'SeatTop':[0,-.46,.465]}

b=start()
cube('MealTray_Base',(0,0,.009),(.45,.30,.018),'HM_BrushedSteel',.015)
for x in [-.218,.218]:cube('Tray_Rim',(x,0,.019),(.012,.30,.024),'HM_BrushedSteel',.004)
for y in [-.143,.143]:cube('Tray_Rim',(0,y,.019),(.45,.012,.024),'HM_BrushedSteel',.004)
hollow_round('Meal_Bowl',(-.075,.01,.023),.082,.075,.052,'HM_ClinicalWhite',.006)
uv('Meal_Porridge',(-.075,.01,.044),(.071,.071,.011),'HM_FoodNeutral')
hollow_round('Meal_Cup',(.13,.065,.022),.035,.030,.09,'HM_BrushedSteel',.004)
torus('Cup_Handle',(.17,.065,.068),.024,.004,'HM_BrushedSteel',rot=(math.pi/2,0,0))
cube('Vitamin_Packet',(.115,-.085,.028),(.074,.055,.01),'HM_ClinicalWhite',.003)
cube('Packet_Stripe',(.115,-.085,.034),(.067,.014,.002),'HM_BlueLED',.0003)
cube('Spoon_Handle',(.033,-.03,.03),(.013,.155,.006),'HM_BrushedSteel',.002)
uv('Spoon_Bowl',(.033,.062,.034),(.022,.029,.004),'HM_BrushedSteel')
collect('MealTraySet',b);anchors['MealTraySet']={}

b=start()
uv('Bed_Pillow',(0,.59,.067),(.31,.215,.067),'HM_Linen')
cube('FoldedBlanket',(0,-.39,.055),(.67,.50,.11),'HM_Linen',.035)
for y,z in [(-.60,.076),(-.62,.05),(-.18,.085)]:
 tube('Blanket_Fold',[(-.31,y,z),(0,y-.005,z+.004),(.31,y,z)],.003,'HM_BlackFrame')
collect('BedLinen',b);anchors['BedLinen']={}

b=start()
arc_screen()
for x in [-.748,.748]:
 cyl('Screen_Post',(x,.30,.705),.015,1.41,'HM_BlackFrame',16)
 cyl('Screen_BoltFoot',(x,.30,.02),.055,.04,'HM_BrushedSteel')
sink_bowl('Hygiene_Sink',(-.40,.23))
cube('Sink_Cabinet',(-.40,.23,.52),(.53,.40,.62),'HM_ClinicalWhite',.015)
cube('Sink_ToeKick',(-.40,.23,.10),(.45,.32,.20),'HM_BlackFrame',.01)
cube('Sink_DoorSeam',(-.40,.024,.52),(.004,.002,.53),'HM_BlackFrame',.0002)
tube('Sink_Faucet',[(-.40,.39,.97),(-.40,.39,1.13),(-.40,.26,1.13),(-.40,.22,1.08)],.014)
cyl('Sink_Drain',(-.40,.23,.838),.022,.004,'HM_BlackFrame',24)
cyl('Toilet_Pedestal',(.34,-.045,.20),.145,.40,'HM_BrushedSteel')
hollow_round('Toilet_Bowl',(.34,-.055,.29),.235,.19,.13,'HM_BrushedSteel',.018)
torus('Toilet_Seat',(.34,-.055,.43),.213,.021,'HM_BlackFrame',scale=(1,1.28,1))
cube('Toilet_Cistern',(.34,.30,.65),(.42,.17,.46),'HM_BrushedSteel',.027)
cyl('Toilet_Flush',(.34,.3,.891),.022,.014,'HM_BlackFrame',16)
torus('Towel_Loop',(-.71,.11,.92),.045,.006,'HM_BlackFrame',rot=(math.pi/2,0,0))
cube('HandTowel',(-.71,.065,.77),(.13,.015,.25),'HM_Linen',.007)
collect('HygieneStation',b);anchors['HygieneStation']={}

b=start()
cube('Monitor_BoltedBase',(0,.02,.025),(.40,.38,.05),'HM_BlackFrame',.02)
cyl('Monitor_Stem',(0,.07,.72),.025,1.40)
cube('Monitor_Body',(0,.01,1.34),(.54,.095,.36),'HM_ClinicalWhite',.025)
cube('Monitor_Screen',(0,-.041,1.35),(.46,.008,.27),'HM_Screen',.01)
for z in [1.26,1.31,1.36,1.41]:cube('Monitor_Grid',(0,-.047,z),(.41,.001,.001),'HM_PaleLabel',0)
for x in [-.18,-.09,0,.09,.18]:cube('Monitor_Grid',(x,-.047,1.35),(.001,.001,.19),'HM_PaleLabel',0)
pulse=[(-.20,-.051,1.335),(-.14,-.051,1.335),(-.12,-.051,1.35),(-.10,-.051,1.32),(-.08,-.051,1.40),(-.06,-.051,1.29),(-.04,-.051,1.335),(.02,-.051,1.335),(.06,-.051,1.348),(.10,-.051,1.335),(.20,-.051,1.335)]
tube('Monitor_Trace',pulse,.0018,'HM_BlueLED')
label('Monitor_Label','S-03   07:30',(-.205,-.053,1.438),.021)
cube('Monitor_ControlStrip',(0,-.052,1.19),(.42,.012,.035),'HM_BlackFrame',.004)
for x in [-.17,-.12,-.07]:
 button=cyl('Monitor_Button',(x,-.064,1.19),.006,.006,'HM_BlueLED',12);button.rotation_euler=(math.pi/2,0,0)
cube('Monitor_SupplyShelf',(0,.02,.93),(.40,.31,.025),'HM_ClinicalWhite',.012)
cube('Monitor_ArmBand',(.08,.005,.972),(.19,.12,.05),'HM_Linen',.02)
for x in [-.08,-.035]:
 tube('Monitor_ElectrodeLead',[(x,.04,1.10),(x-.03,-.05,.96),(x-.06,-.09,.86),(x-.02,-.09,.76)],.003,'HM_BlackFrame')
cube('Monitor_LeadHook',(-.18,.055,1.07),(.025,.08,.025),'HM_BrushedSteel',.006)
collect('TestMonitorStand',b);anchors['TestMonitorStand']={}

def bounds(obs):
 ps=[o.matrix_world@Vector(c) for o in obs for c in o.bound_box]
 return [min(v[i] for v in ps) for i in range(3)],[max(v[i] for v in ps) for i in range(3)]
manifest=[]
for name,obs in groups.items():
 for o in obs:
  bm=bmesh.new();bm.from_mesh(o.data)
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=0.0000002)
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 lo,hi=bounds(obs);offset=Vector(((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,lo[2]))
 for o in obs:o.location-=offset
 root=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(root)
 for o in obs:o.parent=root
 for n,point in anchors[name].items():
  a=bpy.data.objects.new('HM_'+n,None);bpy.context.collection.objects.link(a);a.location=Vector(point)-offset;a.parent=root
 f=bpy.data.objects.new('HM_FrontMarker',None);bpy.context.collection.objects.link(f);f.location=Vector((0,-.7,0))-offset;f.parent=root
 bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
 for o in root.children:o.select_set(True)
 bpy.context.view_layer.objects.active=root
 target=W/(name+'.fbx')
 bpy.ops.export_scene.fbx(filepath=str(target),use_selection=True,object_types={'MESH','EMPTY'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',global_scale=1,axis_forward='-Z',axis_up='Y',bake_anim=False,use_mesh_modifiers=True,mesh_smooth_type='OFF',add_leaf_bones=False,path_mode='AUTO')
 audits=[]
 for o in obs:
  me=o.data;bm=bmesh.new();bm.from_mesh(me);audits.append({'mesh':o.name,'triangles':sum(len(p.vertices)-2 for p in me.polygons),'boundaryEdges':sum(e.is_boundary for e in bm.edges),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'zeroAreaFaces':sum(p.calc_area()<1e-12 for p in bm.faces)});bm.free()
 lo,hi=bounds(obs)
 entry={'name':name,'fbx':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'pivot':'bottom-center','frontMarker':f.name,'frontBlender':[0,-1,0],'blenderBoundsMin':lo,'blenderBoundsMax':hi,'unitySizeXYZ':[hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]],'triangles':sum(x['triangles'] for x in audits),'meshAudit':audits,'anchorsBlender':{n:list(Vector(v)-offset) for n,v in anchors[name].items()},'materials':{n:{'baseColor':c,'metallic':mt,'smoothness':1-rr,'emission':.8 if n=='HM_BlueLED' else 0} for n,(c,mt,rr) in PALETTE.items()},'visualOnly':True,'note':'Disconnected manufactured pieces have intentional joint intersections; closed surfaces and area audited. No Collider or runtime behavior.'}
 manifest.append(entry)
(W/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(SRC/'SubjectHabitat.blend'))

# Studio render of each real mesh, with only render helpers added after saving sources.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=720;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.world.color=(.12,.12,.12)
scene.view_settings.view_transform='AgX'
floor=cube('Review_Ground',(0,0,-.015),(200,200,.025),'HM_BlackFrame',0)
floor.data.materials.clear();fm=bpy.data.materials.new('ReviewGround');fm.diffuse_color=(.15,.17,.19,1);floor.data.materials.append(fm)
for pos,power,size in [((3,-4,5),450,4),((-3,-1,3),280,3),((0,3,4),400,3)]:
 bpy.ops.object.light_add(type='AREA',location=pos);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector((0,0,.6))-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO'
for entry in manifest:
 name=entry['name'];obs=groups[name]
 for n,oo in groups.items():
  for o in oo:o.hide_render=(n!=name)
 lo,hi=bounds(obs);centre=Vector(((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,(lo[2]+hi[2])/2));size=max(hi[i]-lo[i] for i in range(3));cam.data.ortho_scale=size*1.6;cam.location=centre+Vector((2.2,-3,2))*size;cam.rotation_euler=(centre-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(W/(name+'_preview.png'));bpy.ops.render.render(write_still=True)
print(json.dumps([{'name':x['name'],'triangles':x['triangles'],'size':x['unitySizeXYZ'],'boundary':sum(a['boundaryEdges'] for a in x['meshAudit'])} for x in manifest],indent=2))
# [주석] 배치와 충돌 연결은 저장 씬의 담당자가 수행한다. 이 스크립트는 원본·파생 FBX·검수 렌더만 만든다.
