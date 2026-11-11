"""냉각 펌프 형상 보수 V0.01 · 송예찬.
원본 본체/UV 보존 -> 받침대 재제작 -> 모터 덮개 축 정렬 -> 접합된 LOD 출력.
Unity 내부 게임 코드는 추가하지 않는다.
"""
import bpy,bmesh,json,math,struct,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[1];OUT=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B2'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
with (H/'BM_CoolingPump_source.bin').open('rb') as f:
 n,subs=struct.unpack('<ii',f.read(8));v=np.frombuffer(f.read(n*12),'<f4').reshape(-1,3).copy();uv=np.frombuffer(f.read(n*8),'<f4').reshape(-1,2).copy();tris=[]
 for _ in range(subs):
  count=struct.unpack('<i',f.read(4))[0];tris.extend(np.frombuffer(f.read(count*4),'<i4').reshape(-1,3).tolist())
xyz=v[:,[0,2,1]].copy();xyz[:,:2]*=-1;tris=np.array(tris)[:,[0,2,1]]
bvh=BVHTree.FromPolygons(xyz.tolist(),tris.tolist(),all_triangles=True)
steel=bpy.data.materials.new('CP_Original_PBR');aligned=bpy.data.materials.new('CP_Aligned_Metal')
def source_uv(point):
 q,normal,idx,dist=bvh.find_nearest(point)
 if idx is None:return (0,0)
 ids=tris[idx];a,b,c=[Vector(xyz[i]) for i in ids];ab=b-a;ac=c-a;ap=q-a;d00=ab.dot(ab);d01=ab.dot(ac);d11=ac.dot(ac);d20=ap.dot(ab);d21=ap.dot(ac);den=d00*d11-d01*d01
 if abs(den)<1e-16:return tuple(uv[ids[0]])
 beta=(d11*d20-d01*d21)/den;gamma=(d00*d21-d01*d20)/den;val=uv[ids[0]]*(1-beta-gamma)+uv[ids[1]]*beta+uv[ids[2]]*gamma;return tuple(val)
def finish_uv(ob):
 me=ob.data;layer=me.uv_layers.new(name='UVMap');me.update()
 for p in me.polygons:
  p.material_index=1;normal=ob.matrix_world.to_3x3()@p.normal;axis=max(range(3),key=lambda i:abs(normal[i]));axes=[i for i in range(3) if i!=axis]
  for li in p.loop_indices:
   q=ob.matrix_world@me.vertices[me.loops[li].vertex_index].co;layer.data[li].uv=(q[axes[0]]*2,q[axes[1]]*2)
def weld(me):
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
def stats(me):
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);r=dict(boundary=sum(e.is_boundary for e in bm.edges),overused=sum(len(e.link_faces)>2 for e in bm.edges),degenerate=sum(f.calc_area()<1e-12 for f in bm.faces));bm.free();return r
def mesh_obj(name,verts,faces):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(steel);me.materials.append(aligned);ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);return ob
src=mesh_obj('CP_Source',xyz.tolist(),tris.tolist());layer=src.data.uv_layers.new(name='UVMap')
for p in src.data.polygons:
 for li in p.loop_indices:layer.data[li].uv=uv[src.data.loops[li].vertex_index]
weld(src.data)
# The source is already upright in Blender Z-up, with the motor at negative X.
# Preserve thickness while reducing radial waviness around the motor shaft.
aligned_vertices=0
for vert in src.data.vertices:
 x,y,z=vert.co;radius=math.hypot(y,z-.454)
 wx=max(0,min(1,(-x-.57)/.045));wr=max(0,min(1,(radius-.175)/.025))
 if wx>0 and wr>0 and .23<z<.69 and radius<.29:
  amount=wx*wr*.78;new_r=radius+(.207-radius)*amount
  vert.co.y=y*new_r/radius;vert.co.z=.454+(z-.454)*new_r/radius;aligned_vertices+=1
src.data.update()
# Replace the buckled skid below the mounting feet. The cap is inside the new plate,
# 2 mm below its top, avoiding coincident exposed surfaces.
bm=bmesh.new();bm.from_mesh(src.data);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(0,0,.178),plane_no=(0,0,1),dist=1e-7,clear_inner=True)
edges=[e for e in bm.edges if e.is_boundary];newfaces=bmesh.ops.holes_fill(bm,edges=edges,sides=0)['faces'];uvlayer=bm.loops.layers.uv.active
for face in newfaces:
 for loop in face.loops:loop[uvlayer].uv=source_uv(loop.vert.co)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(src.data);bm.free();weld(src.data)
for p in src.data.polygons:
 p.use_smooth=True

base=[]
def bevel(ob,width=.002,segments=2):
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;m=ob.modifiers.new('Manufactured_Edge','BEVEL');m.width=width;m.segments=segments;m.limit_method='ANGLE';m.angle_limit=math.radians(35);m.use_clamp_overlap=True;bpy.ops.object.modifier_apply(modifier=m.name)
def box(name,center,size):
 bpy.ops.mesh.primitive_cube_add(size=1,location=center);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(steel);o.data.materials.append(aligned);[o.data.uv_layers.remove(u) for u in list(o.data.uv_layers)];finish_uv(o);bevel(o);base.append(o);return o
def rail(name,y):
 w=.118;t=.012;web=.015;height=.165
 prof=[(-w/2,0),(w/2,0),(w/2,t),(web/2,t),(web/2,height-t),(w/2,height-t),(w/2,height),(-w/2,height),(-w/2,height-t),(-web/2,height-t),(-web/2,t),(-w/2,t)]
 vs=[(x,y+yy,z) for x in [-.75185,.75198] for yy,z in prof];k=len(prof);fs=[tuple(reversed(range(k))),tuple(range(k,2*k))]+[(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)]
 ob=mesh_obj(name,vs,fs);weld(ob.data);finish_uv(ob);bevel(ob,.0015);base.append(ob)
rail('CP_Skid_Left',-.302);rail('CP_Skid_Right',.302)
for x in [-.683,0,.683]:box('CP_CrossMember',(x,0,.083),(.075,.515,.14))
box('CP_Level_MountingPlate',(.0000675,0,.172),(1.50383,.73006,.016))
for x in [-.66,-.21,.24,.66]:
 for y in [-.285,.285]:
  for name,z,r,dep,sides in [('Washer',.181,.018,.004,16),('Bolt',.186,.012,.008,6)]:
   bpy.ops.mesh.primitive_cylinder_add(vertices=sides,radius=r,depth=dep,location=(x,y,z));o=bpy.context.object;o.name='CP_'+name;o.data.materials.append(steel);o.data.materials.append(aligned);[o.data.uv_layers.remove(u) for u in list(o.data.uv_layers)];finish_uv(o);bevel(o,.0007,1);base.append(o)
# Join the straight support parts once; every instance shares these LOD meshes.
bpy.ops.object.select_all(action='DESELECT')
for o in base:o.select_set(True)
bpy.context.view_layer.objects.active=base[0];bpy.ops.object.join();skid=bpy.context.object;skid.name='CP_Aligned_Skid';weld(skid.data)
levels=[];output=[]
for level,target in [(0,10000),(1,4000)]:
 body=src.copy();body.data=src.data.copy();bpy.context.collection.objects.link(body);support=skid.copy();support.data=skid.data.copy();bpy.context.collection.objects.link(support)
 bpy.ops.object.select_all(action='DESELECT');support.select_set(True);bpy.context.view_layer.objects.active=support
 if level:
  d=support.modifiers.new('Support_Distance_LOD','DECIMATE');d.ratio=.48;d.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=d.name)
 support.data.calc_loop_triangles();body.data.calc_loop_triangles();budget=max(1200,target-len(support.data.loop_triangles));bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body
 dec=body.modifiers.new('Welded_Body_LOD','DECIMATE');dec.ratio=min(1,budget/len(body.data.loop_triangles));dec.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=dec.name)
 support.select_set(True);bpy.ops.object.join();body.name='VA_BM_CoolingPump_LOD'+str(level);weld(body.data)
 bm=bmesh.new();bm.from_mesh(body.data)
 for e in bm.edges:e.smooth=not(e.is_manifold and e.calc_face_angle()>math.radians(50))
 for f in bm.faces:f.smooth=True
 bm.to_mesh(body.data);bm.free();normal=body.modifiers.new('Aligned_Surface_Normals','WEIGHTED_NORMAL');normal.keep_sharp=True;normal.weight=50;bpy.ops.object.modifier_apply(modifier=normal.name)
 body.data.calc_loop_triangles();st=stats(body.data)
 if st['boundary'] or st['overused']:raise RuntimeError(st)
 levels.append(dict(level=level,name=body.name,triangles=len(body.data.loop_triangles),vertices=len(body.data.vertices),**st));output.append(body)
bpy.data.objects.remove(src,do_unlink=True);bpy.data.objects.remove(skid,do_unlink=True);bpy.ops.object.select_all(action='DESELECT')
for ob in output:ob.select_set(True)
bpy.context.view_layer.objects.active=output[0];path=OUT/'VA_BM_CoolingPump.fbx'
bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE',path_mode='STRIP')
bpy.data.orphans_purge(do_recursive=True);bpy.ops.wm.save_as_mainfile(filepath=str(H/'VA_BM_CoolingPump.blend'),compress=True)
result=[dict(model='BM_CoolingPump',asset=path.relative_to(R/'Unity/After_Seconds_Build_V0.01').as_posix(),alignedMotorVertices=aligned_vertices,levels=levels,source='Props_CoolingPump_Repaired.asset + manually rebuilt level skid',bodyOriginalUVPreserved=True,newSkidUV="planar tiling")]
(H/'repair_models.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result),flush=True)
