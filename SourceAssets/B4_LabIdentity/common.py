"""Beveled manufactured parts, readable graphics, nonblocking physical proxies."""
import bpy,bmesh,math,json,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;R=H.parents[1]
s=importlib.util.spec_from_file_location('lab_ops',R/'SourceAssets/B4_ExperimentOperations/common.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
b=c.b;box=c.box;cyl=c.cyl;mesh=c.mesh
OUT=b.A/'Props/B4';manifest={}
def materials():
 for k in ['Coat','Steel']:
  if k in b.mats:b.mats[k].name='LB_'+k
 for k in [f'Display_{i:02d}' for i in range(43,51)]+[f'Record_{i:02d}' for i in range(1,7)]+['Labels']:
  m=bpy.data.materials.new('LB_'+k);m.diffuse_color=(.55,.58,.56,1);b.mats[k]=m
def reset():c.reset();materials()
def printed(name,vs,uv,mat):
 o=mesh(name,vs,[(0,3,2,1)],mat,0)
 if o.data.polygons[0].normal.z<0 and all(abs(v[1]-vs[0][1])<1e-7 for v in vs):o.data.flip_normals()
 layer=o.data.uv_layers.new(name='UVMap')
 for p in o.data.polygons:
  for li in p.loop_indices:layer.data[li].uv=uv[o.data.loops[li].vertex_index]
 o['display_uv']=True;o['visual_only']=True;return o
def paper(x,y,z,w=.21,d=.297,kind=1):
 box('Paper_Sheet',x,y-.0007,z,w,.001,d,'Paper',.00015)
 return printed('Readable_Record',[(x-w/2,y,z-d/2),(x+w/2,y,z-d/2),(x+w/2,y,z+d/2),(x-w/2,y,z+d/2)],[(1,1),(0,1),(0,0),(1,0)],f'Record_{kind:02d}')
def label(x,y,z,w=.18,h=.09,k=7):
 o=b.print_panel('Technical_Label',x,y,z,w,h,43);o.data.materials[0]=b.mats['Labels'];u=(k%4)/4;v=1-(k//4+1)/4
 for p in o.data.polygons:
  for li in p.loop_indices:
   q=o.data.uv_layers.active.data[li].uv.copy();o.data.uv_layers.active.data[li].uv=(u+q.x/4,v+q.y/4)
 o['visual_only']=True;return o
def cable(name,pts,r=.0025,mat='Dark'):
 curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.resolution_u=10;curve.bevel_depth=r;curve.bevel_resolution=2;s=curve.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
 ps=[Vector(b.xyz(*p)) for p in pts]
 for i,(pt,p) in enumerate(zip(s.bezier_points,ps)):
  pt.co=p;prev=ps[max(0,i-1)];nxt=ps[min(len(ps)-1,i+1)];t=(nxt-prev).normalized();pt.handle_left_type='FREE';pt.handle_right_type='FREE'
  for side,q in [('left',prev),('right',nxt)]:
   h=p+t*(1 if side=='right' else -1)*(q-p).length/3
   h=Vector([max(min(p[j],q[j]),min(max(p[j],q[j]),h[j])) for j in range(3)]);setattr(pt,'handle_'+side,h)
 o=bpy.data.objects.new(name,curve);bpy.context.collection.objects.link(o);curve.materials.append(b.mats[mat]);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');o=bpy.context.object;o['visual_only']=True;return o
def screw(x,y,z):
 cyl('Captive_Screw',(x,y,z),(x,y,z+.003),.004,'Steel',10);box('Screw_Slot',x,y,z+.0035,.005,.0012,.0006,'Dark',0)
def port(x,y,z,r=.009):
 cyl('BNC_Lock_Ring',(x,y,z),(x,y,z+.012),r,'Steel',16);cyl('Insulated_Socket',(x,y,z+.012),(x,y,z+.013),r*.65,'Dark',16);cyl('Contact_Pin',(x,y,z+.013),(x,y,z+.014),r*.18,'Steel',8)
def instrument(x,y,z,w=.5,h=.22,d=.30,k=46):
 box('Instrument_Chassis',x,y+h/2,z,w,h,d,'Coat',.009);box('Inset_Front',x,y+h/2,z+d/2+.003,w-.025,h-.025,.009,'Dark',.004)
 c.screen(x-w*.12,y+h*.58,z+d/2+.012,w*.53,h*.62,k)
 c.knob(x+w*.33,y+h*.64,z+d/2+.014,min(.02,h*.11))
 for i in range(3):port(x+w*(.17+i*.10),y+h*.22,z+d/2+.015,min(.008,h*.05))
 for xx in [x-w*.45,x+w*.45]:
  for yy in [y+.024,y+h-.024]:screw(xx,yy,z+d/2+.01)
 for i in range(6):box('Cooling_Slot',x-w*.35+i*w*.055,y+h+.0008,z,w*.022,.002,d*.58,'Dark',.0003)
 for xx in [x-w*.35,x+w*.35]:
  for zz in [z-d*.30,z+d*.30]:box('Instrument_Foot',xx,y-.006,zz,.035,.012,.035,'Rubber',.002)
 label(x,y+h/2,z-d/2-.001,w*.55,h*.45,7)
def tray(x,y,z,w=.40,d=.29,mat='Steel'):
 box('Tray_Base',x,y,z,w,.012,d,mat,.004)
 for xx in [x-w/2+.008,x+w/2-.008]:box('Tray_Folded_Rim',xx,y+.015,z,.012,.04,d,mat,.003)
 for zz in [z-d/2+.008,z+d/2-.008]:box('Tray_Folded_Rim',x,y+.015,zz,w-.025,.04,.012,mat,.003)
def pedestal(x,w=.52,d=.65,top=.88):
 box('Underbench_Cabinet',x,top/2-.015,0,w,top-.09,d,'Coat',.014)
 for i in range(3):
  y=.2+i*.21;box('Drawer_Face',x,y,d/2+.012,w-.035,.19,.025,'Coat',.005);box('Drawer_Reveal',x,y+.10,d/2+.024,w-.03,.005,.003,'Dark',.0005);c.pull(x,y+.04,d/2+.03,.18)
def optical(x,y,z,w=1.0,d=.55):
 box('Optical_Breadboard',x,y,z,w,.06,d,'Steel',.008)
 # Individual counterbored mounting holes remain legible from first person.
 for i in range(max(2,int(w/.09))):
  for j in range(max(2,int(d/.09))):
   xx=x-w/2+.045+i*.09;zz=z-d/2+.045+j*.09;cyl('Threaded_Hole',(xx,y+.0302,zz),(xx,y+.031,zz),.004,'Dark',10)
def stage(x,y,z):
 for zz in [z-.07,z+.07]:cyl('Linear_Guide',(x-.20,y+.035,zz),(x+.20,y+.035,zz),.014,'Steel',16)
 box('Translation_Carriage',x,y+.067,z,.19,.07,.22,'Dark',.007);cyl('Micrometer_Barrel',(x+.09,y+.068,z),(x+.28,y+.068,z),.015,'Steel',20);cyl('Micrometer_Thimble',(x+.28,y+.068,z),(x+.34,y+.068,z),.023,'Dark',20)
 for i in range(5):box('Scale_Tick',x+.20+i*.013,y+.085,z,.002,.001,.012,'Mark',0)
def sensor(x,y,z):
 box('Sensor_Housing',x,y,z,.12,.10,.17,'Coat',.008);cyl('Lens_Barrel',(x,y,z+.08),(x,y,z+.14),.033,'Dark',24);cyl('Optical_Coating',(x,y,z+.141),(x,y,z+.143),.025,'Lens',24)
 for xx in [x-.045,x+.045]:screw(xx,y+.032,z+.086)
def enclosure(x,y,z,w=.9,h=.65,d=.62):
 for xx in [x-w/2,x+w/2]:
  for zz in [z-d/2,z+d/2]:box('Extruded_Frame_Post',xx,y+h/2,zz,.035,h,.035,'Steel',.004)
 for yy in [y+.018,y+h-.018]:
  for zz in [z-d/2,z+d/2]:box('Frame_Cross_Rail',x,yy,zz,w,.035,.035,'Steel',.004)
  for xx in [x-w/2,x+w/2]:box('Frame_Side_Rail',xx,yy,z,.035,.035,d,'Steel',.004)
 for xx in [x-w/2,x+w/2]:box('Safety_Side_Glazing',xx,y+h/2,z,.007,h-.045,d-.045,'Glass',.0007)
 box('Lift_Guard_Glazing',x,y+h/2,z+d/2,w-.045,h-.045,.007,'Glass',.0007)
 c.pull(x,y+h*.28,z+d/2+.02,.16);box('Interlock_Switch',x+w/2+.025,y+h*.75,z+d/2,.034,.085,.04,'Dark',.004)
def save(name,collision=True):
 source=[o for o in bpy.context.scene.objects if o.type=='MESH']
 for o in source:
  if o.get('display_uv'):continue
  if not o.data.uv_layers:o.data.uv_layers.new(name='UVMap')
  for p in o.data.polygons:
   axes=[i for i in range(3) if i!=max(range(3),key=lambda j:abs(p.normal[j]))]
   for li in p.loop_indices:
    v=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;o.data.uv_layers.active.data[li].uv=(v[axes[0]],v[axes[1]])
 bpy.ops.wm.save_as_mainfile(filepath=str(H/(name+'.blend')))
 dep=bpy.context.evaluated_depsgraph_get();counts={}
 for mode in (['collision','render'] if collision else ['render']):
  res=[];removed=0
  for o in source:
   if mode=='collision' and (o.get('visual_only') or max(o.dimensions)<.10):continue
   me=bpy.data.meshes.new_from_object(o.evaluated_get(dep),depsgraph=dep) if mode=='render' else o.data.copy()
   n=bpy.data.objects.new(o.name,me);bpy.context.collection.objects.link(n);n.matrix_world=o.matrix_world.copy();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges));bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<2e-8];removed+=len(bad);bmesh.ops.delete(bm,geom=bad,context='FACES');bm.to_mesh(me);bm.free();res.append(n)
  bpy.ops.object.select_all(action='DESELECT')
  for o in res:o.select_set(True)
  bpy.context.view_layer.objects.active=res[0];bpy.ops.object.join();obj=bpy.context.object;obj.name=name if mode=='render' else name.replace('LB_','LC_');bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
  if mode=='collision':obj.data.materials.clear()
  bpy.ops.export_scene.fbx(filepath=str(OUT/(obj.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE')
  counts[mode]=len(obj.data.polygons);counts[mode+'_removed']=removed;bpy.data.objects.remove(obj,do_unlink=True)
 manifest[name]={'triangles':counts['render'],'collisionTriangles':counts.get('collision',0),'parts':len(source),'beveledParts':sum(bool(o.get('bevel_width_m',0)) for o in source),'asset':str(OUT/(name+'.fbx'))}
 (H/'models.json').write_text(json.dumps(manifest,indent=2),encoding='utf8');print('LAB_EXPORTED',name,counts,flush=True)
