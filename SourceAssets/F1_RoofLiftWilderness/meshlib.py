"""Scoped mesh authoring in Unity metres; no previous generator is executed."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector

class Model:
 def __init__(self,name):self.name=name;self.v=[];self.f=[];self.fm=[];self.m=[]
 def add(self,verts,faces,mat='Corrosion'):
  if mat not in self.m:self.m.append(mat)
  start=len(self.v);self.v.extend(verts);self.f.extend(tuple(start+i for i in f) for f in faces);self.fm.extend([self.m.index(mat)]*len(faces))
 def box(self,p,s,mat='Corrosion'):
  x,y,z=p;a,b,c=[v/2 for v in s];v=[(x+dx,y+dy,z+dz) for dx,dy,dz in [(-a,-b,-c),(a,-b,-c),(a,-b,c),(-a,-b,c),(-a,b,-c),(a,b,-c),(a,b,c),(-a,b,c)]]
  self.add(v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)
 def beam(self,a,b,r=.035,mat='Corrosion',n=8):
  av,bv=Vector(a),Vector(b);d=bv-av
  if d.length<1e-5:return
  d.normalize();u=d.cross(Vector((0,1,0)))
  if u.length<.01:u=d.cross(Vector((1,0,0)))
  u.normalize();w=d.cross(u);vs=[tuple(p+r*(u*math.cos(i*math.tau/n)+w*math.sin(i*math.tau/n))) for p in (av,bv) for i in range(n)]
  self.add(vs,[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat)
 def tube(self,pts,r=.022,mat='Steel',n=8):
  for a,b in zip(pts,pts[1:]):self.beam(a,b,r,mat,n)
 def torus(self,c,r,t,mat='Steel',axis='z',segments=48):
  x,y,z=c;pts=[]
  for i in range(segments+1):
   a=i*math.tau/segments;pts.append((x+r*math.cos(a),y+r*math.sin(a),z) if axis=='z' else (x,y+r*math.sin(a),z+r*math.cos(a)))
  self.tube(pts,t,mat,8)
 def slab(self,poly,height,thickness,mat='Corrosion'):
  from shapely import constrained_delaunay_triangles
  geoms=[poly] if poly.geom_type=='Polygon' else list(poly.geoms)
  for polygon in geoms:
   if polygon.area<.002:continue
   for triangle in constrained_delaunay_triangles(polygon).geoms:
    q=list(triangle.exterior.coords)[:3];top=[(x,height(x,z),z) for x,z in q]
    self.add(top+[(x,y-thickness,z) for x,y,z in top],[(0,1,2),(5,4,3)],mat)
   for ring in [polygon.exterior,*polygon.interiors]:
    q=list(ring.coords)
    for (x,z),(xx,zz) in zip(q,q[1:]):
     y,yy=height(x,z),height(xx,zz);self.add([(x,y,z),(xx,yy,zz),(xx,yy-thickness,zz),(x,y-thickness,z)],[(0,1,2,3)],mat)
 def bent(self,points,th=.035,mat='Corrosion'):
  n=len(points);self.add(points+[(x,y-th,z) for x,y,z in points],[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat)
 def export(self,folder):
  bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.unit_settings.system='METRIC';me=bpy.data.meshes.new(self.name);me.from_pydata([(-x,-z,y) for x,y,z in self.v],[],self.f);me.update()
  for n in self.m:
   mat=bpy.data.materials.new('AE_M_'+n);mat.diffuse_color=(.5,.5,.5,1);me.materials.append(mat)
  for face,i in zip(me.polygons,self.fm):face.material_index=i
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.0000001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
  if not me.uv_layers:me.uv_layers.new(name='UVMap')
  for f in me.polygons:
   axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(f.normal[i]))]
   for li in f.loop_indices:
    v=me.vertices[me.loops[li].vertex_index].co;me.uv_layers.active.data[li].uv=(v[axes[0]]/2,v[axes[1]]/2)
  o=bpy.data.objects.new(self.name,me);bpy.context.collection.objects.link(o);o.select_set(True);bpy.context.view_layer.objects.active=o
  path=Path(folder)/(self.name+'.fbx');path.parent.mkdir(parents=True,exist_ok=True)
  bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE')
  report=dict(name=self.name,file=path.name,triangles=len(me.polygons),materials=['AE_M_'+n for n in self.m],zeroArea=sum(f.area<1e-10 for f in me.polygons))
  assert report['zeroArea']==0,report
  return report
