"""실험동 C01 아치 접합 양개 포켓 도어. 작성자: 송예찬."""
from pathlib import Path
import math,json
import bpy,bmesh
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[1]
lib=R/'SourceAssets/B5_Sector01/build_details.py'
e={'__file__':str(lib),'__name__':'door_library'};exec(compile(lib.read_text('utf-8').split('# Structural ribs')[0],str(lib),'exec'),e)
e['reset']();box=e['box'];mesh=e['mesh'];cyl=e['cyl'];xyz=e['xyz'];mats=e['mats']
for key,c,metal,rough in [('Accent',(.035,.23,.25,1),.35,.35),('Glass',(.27,.52,.58,.24),.1,.1),('Status',(.12,.55,.50,1),.1,.3)]:
 m=bpy.data.materials.new('CDR_'+key);m.diffuse_color=c;m.use_nodes=True;bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=c;bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;mats[key]=m
groups={}
def assign(group):
 for o in bpy.context.scene.objects:
  if o.type=='MESH' and o.name not in groups:groups[o.name]=group
def profile(n,points,z0,z1,mat='Coat',bev=.004):
 vs=[(x,y,z) for z in (z0,z1) for x,y in points];k=len(points)
 return mesh(n,vs,[tuple(range(k-1,-1,-1)),tuple(range(k,2*k))]+[(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)],mat,bev)
def crown(x):return 2.84+.81*math.sqrt(max(0,1-(x/2.60)**2))
# Two separate face skins and a roof leave a real slot for the sliding leaves.
outer=[(2.6-5.2*i/64,crown(2.6-5.2*i/64)) for i in range(65)]
outline=[(-2.6,0),(-1.2,0),(-1.2,2.79),(1.2,2.79),(1.2,0),(2.6,0)]+outer
for face in [-1,1]:
 z=face*.22
 profile('Bulkhead_Face_'+str(face),outline,z-.03,z+.03,'Coat',.009)
 # Side pocket service panels, backing, kickplates and concealed fixings.
 for side in [-1,1]:
  x=side*1.91
  box('Pocket_Panel_Gasket',x,1.45,face*.253,1.19,2.70,.006,'Dark',.002)
  box('Pocket_Access_Panel',x,1.45,face*.264,1.15,2.66,.022,'Coat',.008)
  box('Pocket_Kickplate',x,.20,face*.279,1.11,.27,.008,'Steel',.003)
  box('Pocket_Accent',x,1.05,face*.280,1.11,.035,.009,'Accent',.002)
  for y in [.18,2.70]:
   for dx in [-.49,.49]:cyl('Captive_Screw',(x+dx,y,face*.278),(x+dx,y,face*.284),.011,'Steel',8)
  for zz in [-.148,.148]:box('Pocket_Guide_Rail',side*1.91,.055,zz,1.32,.055,.025,'Steel',.003)
  box('Jamb_Face',side*1.242,1.397,face*.254,.084,2.794,.065,'Steel',.005)
  box('Jamb_Brush_Seal',side*1.215,1.397,face*.121,.03,2.78,.024,'Dark',.002)
 # Header service cover and a recessed proximity sensor; no runtime behavior.
 hz=-.254 if face<0 else .704
 box('Header_Gasket',0,2.99,hz,2.76,.255,.008,'Dark',.003)
 box('Header_Service_Cover',0,2.99,hz+face*.016,2.72,.215,.026,'Steel',.007)
 for x in [-1.25,1.25]:cyl('Header_Screw',(x,2.99,hz+face*.031),(x,2.99,hz+face*.037),.013,'Steel',8)
 box('Sensor_Housing',0,2.93,hz+face*.046,.30,.075,.05,'Dark',.012)
 box('Sensor_Lens',0,2.93,hz+face*.074,.17,.032,.009,'Glass',.004)
 box('Status_Light',0,3.13,hz+face*.006,.48,.018,.009,'Status',.003)
 # Fine relief seam following the crown, not a large rectangular lintel.
 for i in range(60):
  a=-2.52+5.04*i/60;b=-2.52+5.04*(i+1)/60
  e['tube']('Crown_Edge_Trim',[(a,crown(a)-.055,face*.25),(b,crown(b)-.055,face*.25)],.009,'Steel')
profile('Crown_Solid_Infill',[(-2.6,2.81),(2.6,2.81)]+outer,-.19,.70,'Coat',.006)
for side in [-1,1]:box('Pocket_End',side*2.57,1.405,0,.06,2.81,.38,'Steel',.006)
# A continuous arched cuff reaches beyond the spherical junction into the tunnel.
def arch(r):return [(-r,0)]+[(r*math.cos(math.pi-math.pi*i/64),1.3+r*math.sin(math.pi-math.pi*i/64)) for i in range(65)]+[(r,0)]
inner=arch(2.08);outer_ring=arch(2.22);vs=[];k=len(inner)
for z in [.29,1.0]:vs.extend([(x,y,z) for x,y in inner+outer_ring])
fs=[]
for i in range(k-1):
 fs.extend([(i,i+1,2*k+i+1,2*k+i),(k+i,3*k+i,3*k+i+1,k+i+1),(i,k+i,k+i+1,i+1),(2*k+i,2*k+i+1,3*k+i+1,3*k+i)])
fs.extend([(0,2*k,3*k,k),(k-1,2*k-1,4*k-1,3*k-1)])
mesh('Arched_Tunnel_Return',vs,fs,'Steel',.004,True)
box('Flush_Threshold',0,.009,0,2.4,.018,.58,'Steel',.003)
assign('Frame')
for side,label in [(-1,'Left'),(1,'Right')]:
 x=side*.607
 shell=box('Leaf_Shell',x,1.4065,0,1.204,2.767,.104,'Coat',.008)
 cutter=box('Window_Cut',x,1.93,0,.28,.73,.5,'Dark',0)
 bpy.context.view_layer.objects.active=shell;mod=shell.modifiers.new('Observation_Window','BOOLEAN');mod.object=cutter;mod.operation='DIFFERENCE';mod.solver='EXACT';bpy.ops.object.modifier_move_up(modifier=mod.name);bpy.ops.object.modifier_move_up(modifier=mod.name);bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
 box('Observation_Glass',x,1.93,0,.278,.728,.009,'Glass',.003)
 for face in [-1,1]:
  for dx in [-.153,.153]:box('Window_Vertical_Trim',x+dx,1.93,face*.052,.026,.77,.022,'Steel',.004)
  for dy in [-.378,.378]:box('Window_Horizontal_Trim',x,1.93+dy,face*.052,.28,.026,.022,'Steel',.004)
  box('Leaf_Kickplate',x,.21,face*.055,1.12,.31,.009,'Steel',.004)
  box('Leaf_Accent',x,1.05,face*.055,1.17,.035,.008,'Accent',.002)
  box('Leaf_Grip_Recess',side*.18,1.25,face*.054,.058,.22,.006,'Dark',.009)
  box('Leaf_Grip_Insert',side*.18,1.25,face*.058,.025,.17,.006,'Steel',.006)
 box('Meeting_Seal',side*.004,1.4045,0,.008,2.771,.112,'Dark',.0015)
 assign('Leaf_'+label)
# Preserve editable bevel sources; export only evaluated, joined functional groups.
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 if not o.data.uv_layers:o.data.uv_layers.new(name='UVMap')
 for p in o.data.polygons:
  axes=[i for i in range(3) if i!=max(range(3),key=lambda j:abs(p.normal[j]))]
  for li in p.loop_indices:
   c=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;o.data.uv_layers.active.data[li].uv=(c[axes[0]],c[axes[1]])
bpy.ops.wm.save_as_mainfile(filepath=str(H/'CDR_ClinicalPortal.blend'))
sources=list(bpy.context.scene.objects);dep=bpy.context.evaluated_depsgraph_get();out=[];stats=[]
for group in ['Frame','Leaf_Left','Leaf_Right']:
 parts=[]
 for o in sources:
  if o.type!='MESH' or groups[o.name]!=group:continue
  me=bpy.data.meshes.new_from_object(o.evaluated_get(dep),depsgraph=dep);n=bpy.data.objects.new('Export',me);bpy.context.collection.objects.link(n);n.matrix_world=o.matrix_world.copy();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<5e-9];bmesh.ops.delete(bm,geom=bad,context='FACES');bm.to_mesh(me);bm.free();parts.append(n)
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name='CDR_'+group;bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');out.append(o);stats.append(dict(group=group,triangles=len(o.data.polygons)))
bpy.ops.object.select_all(action='DESELECT')
for o in out:o.select_set(True)
output=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/B5/CDR_ClinicalPortal.fbx'
bpy.ops.export_scene.fbx(filepath=str(output),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE',use_custom_props=True)
(H/'geometry.json').write_text(json.dumps(dict(author='송예찬',clear_width=2.4,clear_height=2.79,crown_height=3.65,leaf_travel=1.235,tunnel_width=4.2,tunnel_height=3.4,groups=stats),ensure_ascii=False,indent=2),encoding='utf-8')
print('EXPORTED',stats)
