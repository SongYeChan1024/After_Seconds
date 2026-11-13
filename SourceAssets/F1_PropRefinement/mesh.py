"""Scoped 1F prop surfaces. Unity metres, +Z front. Author Song Yechan."""
import sys,math,os,json,bpy,bmesh
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'F1_DetailPass'))
import importlib.util
spec=importlib.util.spec_from_file_location('previous_detail_helpers',H.parent/'F1_DetailPass/mesh.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);DetailModel=module.Model
OUT=Path(os.environ['LOCALAPPDATA'])/'Temp/AfterSeconds_PropRefinement_20261113/candidate'
class Model(DetailModel):
 def box(self,p,s,mat='Green',bev=.007):
  # Apply physical bevel before aggregation; weighted normals preserve the broad panels.
  me=bpy.data.meshes.new('part');x,y,z=p;a,b,c=[v/2 for v in s]
  vs=[(x+dx,y+dy,z+dz) for dx,dy,dz in [(-a,-b,-c),(a,-b,-c),(a,-b,c),(-a,-b,c),(-a,b,-c),(a,b,-c),(a,b,c),(-a,b,c)]]
  me.from_pydata(vs,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
  if bev:bmesh.ops.bevel(bm,geom=list(bm.edges),offset=min(bev,min(s)*.47),segments=5 if bev>=.025 else 3 if bev>=.01 else 2,profile=.5,affect='EDGES')
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();self.add([tuple(v.co) for v in me.vertices],[tuple(f.vertices) for f in me.polygons],mat);bpy.data.meshes.remove(me)
 def tube(self,pts,r=.018,mat='Rubber',n=10):
  # One connected parallel-transport tube, without intersecting segment caps.
  pp=[Vector(p) for p in pts];vv=[];last=None
  for i,p in enumerate(pp):
   tangent=(pp[min(i+1,len(pp)-1)]-pp[max(0,i-1)]).normalized()
   if last is None:
    ref=Vector((0,1,0)) if abs(tangent.y)<.92 else Vector((1,0,0));u=tangent.cross(ref).normalized()
   else:u=(last-tangent*last.dot(tangent)).normalized()
   v=tangent.cross(u).normalized();last=u
   for j in range(n):vv.append(tuple(p+r*(u*math.cos(j*math.tau/n)+v*math.sin(j*math.tau/n))))
  ff=[tuple(range(n-1,-1,-1)),tuple((len(pp)-1)*n+j for j in range(n))]
  ff.extend((i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j) for i in range(len(pp)-1) for j in range(n));self.add(vv,ff,mat)
 def curve(self,pts,r=.018,mat='Rubber',steps=9,n=10):
  p=[Vector(q) for q in pts];path=[]
  for i in range(len(p)-1):
   a,b,c,d=p[max(i-1,0)],p[i],p[i+1],p[min(i+2,len(p)-1)]
   for j in range(steps):
    t=j/steps;path.append(tuple(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)))
  path.append(tuple(p[-1]));self.tube(path,r,mat,n)
 def ring(self,c,r,t=.009,mat='Steel',axis='z',n=48):
  c=Vector(c);u=Vector((1,0,0)) if axis!='x' else Vector((0,0,1));v=Vector((0,1,0)) if axis!='y' else Vector((0,0,1));w=u.cross(v);vv=[];ns=10
  for i in range(n):
   a=i*math.tau/n;d=u*math.cos(a)+v*math.sin(a)
   for j in range(ns):
    b=j*math.tau/ns;vv.append(tuple(c+d*(r+t*math.cos(b))+w*t*math.sin(b)))
  self.add(vv,[(i*ns+j,((i+1)%n)*ns+j,((i+1)%n)*ns+(j+1)%ns,i*ns+(j+1)%ns) for i in range(n) for j in range(ns)],mat)
 def lathe(self,c,profile,mat='Rubber',axis='x',n=64):
  c=Vector(c);d=Vector({'x':(1,0,0),'y':(0,1,0),'z':(0,0,1)}[axis]);u=Vector((0,1,0)) if axis!='y' else Vector((1,0,0));w=d.cross(u);vv=[]
  for off,r in profile:
   vv.extend(tuple(c+d*off+r*(u*math.cos(i*math.tau/n)+w*math.sin(i*math.tau/n))) for i in range(n))
  self.add(vv,[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(profile)-1) for i in range(n)],mat)
 def wheel(self,c,r,w,hub='Steel',n=64):
  x,y,z=c;self.lathe(c,[(-w*.5,r*.53),(-w*.5,r*.82),(-w*.42,r*.96),(-w*.27,r),(w*.27,r),(w*.42,r*.96),(w*.5,r*.82),(w*.5,r*.53)],'Rubber','x',n)
  self.beam((x-w*.48,y,z),(x+w*.48,y,z),r*.54,hub,40)
  for side in [-1,1]:
   self.ring((x+side*w*.5,y,z),r*.53,r*.035,hub,'x',40)
   self.beam((x+side*w*.48,y,z),(x+side*w*.57,y,z),r*.22,'WornSteel',32)
   for i in range(6 if r>.15 else 1):
    a=i*math.tau/6;self.bolt((x+side*w*.51,y+r*.36*math.sin(a),z+r*.36*math.cos(a)),r*.045,'x',side)
  # Dry contact shoulder and recessed tread cuts follow the tyre, not painted dots.
  for i in range(28 if r>.15 else 18):
   a=i*math.tau/(28 if r>.15 else 18)
   self.curve([(x-w*.29,y+(r+.0005)*math.cos(a-.055),z+(r+.0005)*math.sin(a-.055)),(x,y+(r+.001)*math.cos(a),z+(r+.001)*math.sin(a)),(x+w*.29,y+(r+.0005)*math.cos(a+.055),z+(r+.0005)*math.sin(a+.055))],r*.008,'TireDust',steps=3,n=5)
 def export(self):
  OUT.mkdir(parents=True,exist_ok=True);bpy.ops.wm.read_factory_settings(use_empty=True);me=bpy.data.meshes.new(self.name+'_LOD0');me.from_pydata([(-x,-z,y) for x,y,z in self.v],[],self.f);me.update()
  for name in self.m:me.materials.append(bpy.data.materials.new('PR_M_'+name))
  for p,mi in zip(me.polygons,self.fm):p.material_index=mi;p.use_smooth=True
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
  me.uv_layers.new(name='UVMap')
  for f in me.polygons:
   ax=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(f.normal[i]))]
   for li in f.loop_indices:
    v=me.vertices[me.loops[li].vertex_index].co;me.uv_layers.active.data[li].uv=(v[ax[0]],v[ax[1]])
  o=bpy.data.objects.new(self.name+'_LOD0',me);bpy.context.collection.objects.link(o);o.select_set(True);bpy.context.view_layer.objects.active=o
  split=o.modifiers.new('Preserve hard junctions','EDGE_SPLIT');split.split_angle=math.radians(40);bpy.ops.object.modifier_apply(modifier=split.name)
  wn=o.modifiers.new('Area weighted surface normals','WEIGHTED_NORMAL');wn.keep_sharp=True;wn.weight=45;bpy.ops.object.modifier_apply(modifier=wn.name)
  tri=o.modifiers.new('Deterministic triangles','TRIANGULATE');tri.keep_custom_normals=True;bpy.ops.object.modifier_apply(modifier=tri.name)
  counts=[len(o.data.polygons)];objects=[o];zero=sum(f.area<1e-12 for f in o.data.polygons);assert zero==0,(self.name,zero)
  for i,ratio in [(1,.42),(2,.16)]:
   ob=o.copy();ob.data=o.data.copy();bpy.context.collection.objects.link(ob);ob.name=self.name+'_LOD'+str(i);bpy.context.view_layer.objects.active=ob;d=ob.modifiers.new('Distance geometry','DECIMATE');d.ratio=ratio;d.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=d.name);ob.select_set(True);objects.append(ob);counts.append(len(ob.data.polygons))
  for ob in objects:ob.data.name=ob.name
  bpy.ops.export_scene.fbx(filepath=str(OUT/(self.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE')
  lo=[min(p[i] for p in self.v) for i in range(3)];hi=[max(p[i] for p in self.v) for i in range(3)]
  return dict(name=self.name,triangles=counts,materials=['PR_M_'+n for n in self.m],zeroArea=zero,bounds=[lo,hi])
