"""Original local detail meshes in Unity metres; no previous generator runs."""
import sys,math,os,json,bpy,bmesh
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'F1_RoofLiftWilderness'))
from meshlib import Model as Base
OUT=Path(os.environ['LOCALAPPDATA'])/'Temp/AfterSeconds_EnvironmentalStory_20261113/candidate'
class Model(Base):
 def text(self,words,p,size=.055,mat='Paper'):
  curve=bpy.data.curves.new('TemporaryLettering','FONT');curve.body=words;curve.size=size;curve.align_x='CENTER';curve.align_y='CENTER';curve.extrude=.0004;curve.resolution_u=3
  o=bpy.data.objects.new('TemporaryLettering',curve);bpy.context.collection.objects.link(o);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
  self.add([(p[0]-v.co.x,v.co.y+p[1],v.co.z+p[2]) for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons],mat);bpy.data.objects.remove(o,do_unlink=True)
 def ring(self,c,r,t=.009,mat='Steel',axis='z',n=24):
  c=Vector(c);u=Vector((1,0,0)) if axis!='x' else Vector((0,0,1));v=Vector((0,1,0)) if axis!='y' else Vector((0,0,1));w=u.cross(v);verts=[]
  for i in range(n):
   a=i*math.tau/n;d=u*math.cos(a)+v*math.sin(a)
   for j in range(6):
    b=j*math.tau/6;verts.append(tuple(c+d*(r+t*math.cos(b))+w*t*math.sin(b)))
  self.add(verts,[(i*6+j,((i+1)%n)*6+j,((i+1)%n)*6+(j+1)%6,i*6+(j+1)%6) for i in range(n) for j in range(6)],mat)
 def bolt(self,p,r=.018,axis='z',sign=1):
  d=Vector({'x':(1,0,0),'y':(0,1,0),'z':(0,0,1)}[axis])*sign;p=Vector(p)
  self.beam(p-d*.0005,p+d*(r*.18),r*1.45,'Steel',12);self.beam(p+d*(r*.18),p+d*(r*.75),r,'Steel',6)
  self.beam(p+d*(r*.75),p+d*(r*.75+.0004),r*.32,'Dark',6)
 def label(self,p,w=.2,h=.07):
  x,y,z=p;self.box(p,(w,h,.004),'Paper');self.box((x-w*.29,y,z+.003),(w*.25,h*.55,.002),'Dark')
  for i in range(3):self.box((x+w*.12,y+h*(.25-i*.23),z+.003),(w*.42,h*.055,.002),'Dark')
 def gauge(self,p,r=.08):
  x,y,z=p;self.beam((x,y,z-.025),(x,y,z+.008),r,'Steel',24);self.beam((x,y,z+.009),(x,y,z+.012),r*.83,'Paper',24)
  for i in range(11):
   a=math.radians(-45+i*27);self.beam((x+math.cos(a)*r*.62,y+math.sin(a)*r*.62,z+.015),(x+math.cos(a)*r*.76,y+math.sin(a)*r*.76,z+.015),.0025,'Dark',4)
  self.beam((x,y,z+.019),(x-r*.4,y+r*.35,z+.019),.004,'Red',4)
 def export(self,lods=True):
  OUT.mkdir(parents=True,exist_ok=True);bpy.ops.wm.read_factory_settings(use_empty=True);me=bpy.data.meshes.new(self.name+'_LOD0');me.from_pydata([(-x,-z,y) for x,y,z in self.v],[],self.f);me.update()
  for mat in self.m:me.materials.append(bpy.data.materials.new('AE_M_'+mat))
  for p,mi in zip(me.polygons,self.fm):p.material_index=mi
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0000001);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.00000005);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
  me.uv_layers.new(name='UVMap')
  for f in me.polygons:
   axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(f.normal[i]))]
   for li in f.loop_indices:
    v=me.vertices[me.loops[li].vertex_index].co;me.uv_layers.active.data[li].uv=(v[axes[0]],v[axes[1]])
  for f in me.polygons:
   if self.m[f.material_index] in ['IvyDark','IvyMid','IvyLight','IvyDry','IvyBark']:f.use_smooth=True
  zero=sum(f.area<1e-12 for f in me.polygons);assert zero==0,(self.name,zero)
  objects=[];tri=[]
  for i,ratio in enumerate([1,.46,.18] if lods else [1]):
   mm=me if i==0 else me.copy();o=bpy.data.objects.new(self.name+'_LOD'+str(i),mm);bpy.context.collection.objects.link(o);o.select_set(True);bpy.context.view_layer.objects.active=o
   if i:
    d=o.modifiers.new('Distance detail','DECIMATE');d.ratio=ratio;bpy.ops.object.modifier_apply(modifier=d.name)
   o.data.name=o.name;tri.append(len(o.data.polygons));objects.append(o)
  bpy.ops.export_scene.fbx(filepath=str(OUT/(self.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE')
  return dict(name=self.name,triangles=tri,materials=['AE_M_'+n for n in self.m],zeroArea=zero)
