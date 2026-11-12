"""1F local hard-surface authoring. Metres, Unity +Z front. Author: 송예찬."""
from pathlib import Path
import bpy,bmesh,math,json,os
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;R=H.parents[1];U=R/'Unity/After_Seconds_Build_V0.01';A=U/'Assets/Afrer_Seconds/05.Model'
manifest={};mats={}
specs={'Coat':('#99998A',.05,.22),'Green':('#657563',.3,.28),'Steel':('#777B77',.75,.42),'Dark':('#242B2C',.15,.25),'Rubber':('#252828',0,.16),'Wood':('#887450',0,.18),'Paper':('#D6D2BD',0,.14),'Rust':('#82523A',.15,.22),'Floor':('#77786F',0,.18),'Glass':('#ADC5C6',.05,.76),'Red':('#973F35',.1,.28),'Hazard':('#C5A658',.1,.26),'Lamp':('#EBE9D9',0,.3),'Indicator':('#62B19B',0,.32),'Fabric':('#625D4D',0,.18)}
def xyz(x,y,z):return(-x,-z,y)
def reset():
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.unit_settings.system='METRIC';mats.clear()
 for n,(color,metal,smooth) in specs.items():
  c=tuple(int(color[i:i+2],16)/255 for i in (1,3,5))+(1,);m=bpy.data.materials.new('F1M_'+n);m.diffuse_color=c;m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=c;p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=1-smooth;mats[n]=m
def finish(o,n,mat,bev=0):
 o.name=n;o.data.materials.append(mats[mat])
 if bev:
  md=o.modifiers.new('RoundedEdges','BEVEL');md.width=bev;md.segments=2
 return o
def box(n,p,s,mat='Green',bev=.012,yaw=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(*p));o=bpy.context.object;o.dimensions=(s[0],s[2],s[1]);o.rotation_euler.z=-math.radians(yaw);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n,mat,bev)
def cyl(n,p,r,d,mat='Steel',axis='y',verts=20):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=d,location=xyz(*p));o=bpy.context.object
 if axis=='x':o.rotation_euler.y=math.pi/2
 if axis=='z':o.rotation_euler.x=math.pi/2
 for f in o.data.polygons:f.use_smooth=len(f.vertices)==4
 return finish(o,n,mat,.004)
def beam(n,a,b,w=.04,mat='Steel',square=True):
 av,bv=Vector(xyz(*a)),Vector(xyz(*b));d=bv-av
 if square:
  bpy.ops.mesh.primitive_cube_add(size=1,location=(av+bv)/2);o=bpy.context.object;o.dimensions=(w,w,d.length);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 else:
  bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=w/2,depth=d.length,location=(av+bv)/2);o=bpy.context.object
 o.rotation_mode='QUATERNION';o.rotation_quaternion=d.to_track_quat('Z','Y');return finish(o,n,mat,0)
def mesh(n,vs,fs,mat='Coat'):
 me=bpy.data.meshes.new(n);me.from_pydata([xyz(*v) for v in vs],[],fs);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);return finish(o,n,mat)
def text(n,words,p,size=.15,mat='Paper',yaw=0):
 bpy.ops.object.text_add(location=xyz(*p));o=bpy.context.object;o.name=n;o.data.body=words;o.data.size=size;o.data.align_x='CENTER';o.data.align_y='CENTER';o.data.extrude=.0008;o.rotation_euler=(math.pi/2,0,math.pi);o.rotation_euler.z-=math.radians(yaw);o.scale.x=-1;o.data.materials.append(mats[mat]);bpy.ops.object.convert(target='MESH');return bpy.context.object
def turn(objects,x,y,z,yaw):
 m=Matrix.Translation(Vector(xyz(x,y,z)))@Matrix.Rotation(-math.radians(yaw),4,'Z')
 for o in objects:o.matrix_world=m@o.matrix_world
def save(name,category='Props',lod=True):
 source=list(bpy.context.scene.objects);dep=bpy.context.evaluated_depsgraph_get();res=[]
 for ob in source:
  if ob.type!='MESH':continue
  me=bpy.data.meshes.new_from_object(ob.evaluated_get(dep),depsgraph=dep);o=bpy.data.objects.new(ob.name,me);bpy.context.collection.objects.link(o);o.matrix_world=ob.matrix_world.copy()
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
  if not me.uv_layers:me.uv_layers.new(name='UVMap')
  for f in me.polygons:
   norm=o.matrix_world.to_3x3()@f.normal;ax=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(norm[i]))]
   for li in f.loop_indices:
    v=o.matrix_world@me.vertices[me.loops[li].vertex_index].co;me.uv_layers.active.data[li].uv=(v[ax[0]]/2,v[ax[1]]/2)
  res.append(o)
 bpy.ops.object.select_all(action='DESELECT')
 for o in res:o.select_set(True)
 bpy.context.view_layer.objects.active=res[0];bpy.ops.object.join();o=bpy.context.object;o.name='F1_'+name+('_LOD0' if lod else '');bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 vv=[(-v.co.x,v.co.z,-v.co.y) for v in o.data.vertices];lo=[min(v[i] for v in vv) for i in range(3)];hi=[max(v[i] for v in vv) for i in range(3)];counts=[len(o.data.polygons)]
 if lod:
  for i,ratio in [(1,.42),(2,.16)]:
   ob=o.copy();ob.data=o.data.copy();bpy.context.collection.objects.link(ob);ob.name='F1_'+name+'_LOD'+str(i);bpy.context.view_layer.objects.active=ob;md=ob.modifiers.new('DistanceDetail','DECIMATE');md.ratio=ratio;md.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=md.name);ob.select_set(True);counts.append(len(ob.data.polygons))
 out=A/category/'1F';out.mkdir(parents=True,exist_ok=True);path=out/('F1_'+name+'.fbx');bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE')
 manifest[name]=dict(asset=path.relative_to(U).as_posix(),category=category,center=[(lo[i]+hi[i])/2 for i in range(3)],size=[hi[i]-lo[i] for i in range(3)],triangles=counts,materials=[m.name for m in o.data.materials]);(H/('models_'+category.lower()+'.json')).write_text(json.dumps(manifest,indent=2),encoding='utf8');print('DONE',name,counts,flush=True)
