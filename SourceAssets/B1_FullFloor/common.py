"""Compact FBX authoring; no Unity YAML mesh copies or runtime scripts."""
from pathlib import Path
import importlib.util,sys,json,math,bpy,bmesh
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;R=H.parents[1];A=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model'
s=importlib.util.spec_from_file_location('b1_base',R/'SourceAssets/B4_FullFloor/common.py');base=importlib.util.module_from_spec(s);s.loader.exec_module(base)
for k,v in vars(base).items():
 if not k.startswith('_') and k not in ['H','R','A','reset','save']:globals()[k]=v
manifest={}
def reset():
 base.reset()
 for key,m in b.mats.items():m.name='B1M_'+key
def save(name,category='Environment',lod=False):
 name='BL_'+name;source=[o for o in bpy.context.scene.objects if o.type=='MESH'];dep=bpy.context.evaluated_depsgraph_get();res=[]
 for o in source:
  me=bpy.data.meshes.new_from_object(o.evaluated_get(dep),depsgraph=dep)
  for i in range(len(me.materials)):
   if me.materials[i] is None:me.materials[i]=b.mats['Coat']
  ob=bpy.data.objects.new(o.name,me);bpy.context.collection.objects.link(ob);ob.matrix_world=o.matrix_world.copy()
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
  if not me.uv_layers:me.uv_layers.new(name='UVMap')
  if not o.get('display_uv'):
   for p in me.polygons:
    wn=ob.matrix_world.to_3x3()@p.normal;axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(wn[i]))]
    for li in p.loop_indices:
     co=ob.matrix_world@me.vertices[me.loops[li].vertex_index].co;me.uv_layers.active.data[li].uv=(co[axes[0]]/3,co[axes[1]]/3)
  res.append(ob)
 bpy.ops.object.select_all(action='DESELECT')
 for o in res:o.select_set(True)
 bpy.context.view_layer.objects.active=res[0];bpy.ops.object.join();o=bpy.context.object;o.name=name+('_LOD0' if lod else '');bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 verts=[o.matrix_world@v.co for v in o.data.vertices];uvs=[(-v.x,v.z,-v.y) for v in verts];lo=[min(v[i] for v in uvs) for i in range(3)];hi=[max(v[i] for v in uvs) for i in range(3)]
 tris=len(o.data.polygons);counts=[tris]
 if lod:
  ob=o.copy();ob.data=o.data.copy();bpy.context.collection.objects.link(ob);ob.name=name+'_LOD1';bpy.context.view_layer.objects.active=ob;md=ob.modifiers.new('DistantDetail','DECIMATE');md.ratio=.42;md.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=md.name);ob.select_set(True);counts.append(len(ob.data.polygons))
 out=A/category/'B1';out.mkdir(parents=True,exist_ok=True)
 bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE')
 manifest[name]=dict(name=name,asset=(out/(name+'.fbx')).relative_to(R/'Unity/After_Seconds_Build_V0.01').as_posix(),category=category,triangles=counts,size=[hi[i]-lo[i] for i in range(3)],center=[(hi[i]+lo[i])/2 for i in range(3)],parts=len(source),materials=[m.name for m in o.data.materials])
 (H/('models_'+category.lower()+'.json')).write_text(json.dumps(manifest,indent=2));print('DONE',name,counts,flush=True)
def sphere(n,x,v,r):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=128,ring_count=64,radius=r,location=(-x,v,0));o=bpy.context.object;o.name=n;return o
def sweep(n,t,pad=0,extend=0):
 ps=[Vector((p[0],0,-p[1])) for p in t['path']]
 if extend:ps[0]-=(ps[1]-ps[0]).normalized()*extend;ps[-1]+=(ps[-1]-ps[-2]).normalized()*extend
 rights=[Vector(((ps[min(i+1,len(ps)-1)]-ps[max(0,i-1)]).normalized().z,0,-(ps[min(i+1,len(ps)-1)]-ps[max(0,i-1)]).normalized().x)) for i in range(len(ps))]
 w=t['w']/2+pad;spring=t['h']-t['w']/2;profile=[(-w,-.5-pad),(w,-.5-pad),(w,spring)]+[(w*math.cos(math.pi*i/32),spring+w*math.sin(math.pi*i/32)) for i in range(1,33)]
 vs=[tuple(p+right*x+Vector((0,y,0))) for p,right in zip(ps,rights) for x,y in profile];n0=len(profile);fs=[tuple(range(n0-1,-1,-1)),tuple(range(len(vs)-n0,len(vs)))]
 for i in range(len(ps)-1):
  for j in range(n0):a=i*n0+j;bb=i*n0+(j+1)%n0;fs.append((a,bb,bb+n0,a+n0))
 return mesh(n,vs,fs,'Coat',0,True)
def floorbar(t):
 ps=[Vector((p[0],0,-p[1])) for p in t['path']];rr=[Vector(((ps[min(i+1,len(ps)-1)]-ps[max(0,i-1)]).normalized().z,0,-(ps[min(i+1,len(ps)-1)]-ps[max(0,i-1)]).normalized().x)) for i in range(len(ps))];vs=[tuple(p+right*side*t['w']*.5+Vector((0,y,0))) for y in [-.24,0] for p,right in zip(ps,rr) for side in [-1,1]];n=len(ps)*2;fs=[(0,1,n+1,n),(n-2,2*n-2,2*n-1,n-1)]
 for i in range(len(ps)-1):a=i*2;fs.extend([(a,a+2,a+3,a+1),(n+a,n+a+1,n+a+3,n+a+2),(a,n+a,n+a+2,a+2),(a+1,a+3,n+a+3,n+a+1)])
 return mesh('Floor',vs,fs,'Floor',0)
