import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).parent;P=R.parent.parent/'Unity/After_Seconds_Build_V0.01'
ROOT='Assets/Afrer_Seconds/05.Model/Environment/Architecture_Rebuilt'
specs={'Env_ConcreteWall_4m':(4,4,.18),'Env_MetalWall_4m':(4,4,.18),'Env_FireDoorWall_3m':(3,4,.18),'Env_ObservationWall_4m':(4,4,.18),'Env_FloorSlab_4m':(4,.12,4),'Env_CeilingPanel_4m':(4,.15,4)}
old=json.loads((R.parent/'Existing_VARCO_Repair_20261103/imported_sources.json').read_text(encoding='utf-8-sig'))
manifest=json.loads((R/'rebuild_manifest.json').read_text()) if (R/'rebuild_manifest.json').exists() else []
selection=set(sys.argv[sys.argv.index('--')+1:]) if '--' in sys.argv else set(specs)
def mat(name,color,metal=0,rough=.65):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;return m
def box(name,loc,scale,material,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
 if bevel:
  mod=o.modifiers.new('HighDetailEdgeBevel','BEVEL');mod.width=bevel;mod.segments=12
  bpy.ops.object.modifier_apply(modifier=mod.name)
 return o
def bolt(x,z,y,side,material):
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.018,depth=.005,location=(x,y,z),rotation=(math.pi/2,0,0));o=bpy.context.object;o.name='Sealed_Bolt';o.data.materials.append(material);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);mod=o.modifiers.new('BoltBevel','BEVEL');mod.width=.002;mod.segments=8;bpy.ops.object.modifier_apply(modifier=mod.name)
def frame(name,w,h,iw,ih,bottom,depth,material):
 # A single watertight extruded ring, no overlapping boxes at corners.
 outer=[(-w/2,0),(w/2,0),(w/2,h),(-w/2,h)];inner=[(-iw/2,bottom),(iw/2,bottom),(iw/2,bottom+ih),(-iw/2,bottom+ih)]
 verts=[(x,y,z) for y in [-depth/2,depth/2] for loop in [outer,inner] for x,z in loop];faces=[]
 for i in range(4):
  j=(i+1)%4;faces.extend([(i,j,4+j,4+i),(8+j,8+i,12+i,12+j),(j,i,8+i,8+j),(4+i,4+j,12+j,12+i)])
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(material);return o
def join(objects,name):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);return o
for name,size in specs.items():
 if name not in selection:continue
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for data in [bpy.data.meshes,bpy.data.materials]:
  for x in list(data):
   if x.users==0:data.remove(x)
 concrete=mat('AS_Concrete',(.38,.39,.37));steel=mat('AS_PaintedSteel',(.43,.46,.46),.45,.6);dark=mat('AS_Seal',(.055,.067,.071),.15,.72);boltmat=mat('AS_Fastener',(.25,.28,.29),.75,.4);yellow=mat('AS_SafetyYellow',(.55,.43,.13),.2,.7);glass=mat('AS_Glass',(.36,.48,.5),0,.18)
 w,height,dep=size
 if name=='Env_ObservationWall_4m':
  window=frame('Structural_WindowWall',4,4,2.6,1.65,1.25,.18,steel)
  window.data.materials.append(dark)
  for f in window.data.polygons:
   if f.index%4==3:f.material_index=1
  box('Separate_Glass',(0,0,2.075),(2.6,.012,1.65),glass)
  for x in [-1.38,1.38]:
   for z in [1.2,2.95]:
    for side in [-1,1]:bolt(x,z,side*.0925,side,boltmat)
 elif 'Wall' in name:
  box('Exact_Sealed_StructuralShell',(0,0,2),(w,.14,4),concrete if 'Concrete' in name else steel)
  for side in [-1,1]:
   if 'Metal' in name:
    for i in range(8):box('Steel_Rib',(-1.75+i*.5,side*.0775,2),(.032,.015,3.88),steel,.004)
   elif 'FireDoor' in name:
    box('Inset_DoorLeaf',(0,side*.078,1.3),(1.26,.016,2.45),steel,.012)
    for x in [-.69,.69]:box('Door_Trim',(x,side*.078,1.3),(.09,.016,2.58),dark,.008)
    box('Door_Header',(0,side*.078,2.635),(1.47,.016,.09),dark,.008)
    box('Door_PushBar',(0,side*.089,1.1),(.76,.006,.065),boltmat,.002)
   else:
    for x in [-1,1]:box('Concrete_FormPanel',(x,side*.075,2),(1.97,.01,3.96),concrete,.008)
   for x in [-w/2+.12,w/2-.12]:
    for z in [.12,3.88]:bolt(x,z,side*.0875,side,boltmat)
 else:
  thick=size[1];ceiling='Ceiling' in name
  baseheight=thick-.03 if ceiling else thick-.02
  box('Exact_Sealed_Slab',(0,0,baseheight*.5 if ceiling else .02+baseheight*.5),(4,4,baseheight),steel if ceiling else concrete)
  # Inlaid visual panels sit entirely inside the structural module footprint.
  for x in [-1,1]:
   for y in [-1,1]:
    z=thick-.015 if ceiling else .01
    box('Inset_Panel',(x,y,z),(1.96,1.96,.03 if ceiling else .02),steel,.004)
 opaque=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name!='Separate_Glass'];joined=join(opaque,name+'_Opaque');objects=[joined]+[o for o in bpy.context.scene.objects if o.name=='Separate_Glass']
 for o in objects:
  bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
  # Planar UVs in metre units; use tiled subtle procedural surface textures in Unity.
  mesh=o.data;uv=mesh.uv_layers.new(name='SurfaceUV')
  for poly in mesh.polygons:
   axis=max(range(3),key=lambda k:abs(poly.normal[k]));axes=[k for k in range(3) if k!=axis]
   for li in poly.loop_indices:
    co=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]],co[axes[1]])
 high=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objects);bpy.ops.wm.save_as_mainfile(filepath=str(R/(name+'_high.blend')))
 for o in objects:
  bpy.context.view_layer.objects.active=o
  # Retain the exact structural cage; collapse only the high-detail bevel tessellation.
  if o==joined:
   mod=o.modifiers.new('GameTopologyReduction','DECIMATE');mod.ratio=.22;mod.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=mod.name)
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
  for f in o.data.polygons:f.use_smooth=True
  o.data.set_sharp_from_angle(angle=math.radians(40));mod=o.modifiers.new('WeightedSurfaceNormals','WEIGHTED_NORMAL');mod.keep_sharp=True;bpy.ops.object.modifier_apply(modifier=mod.name)
 low=sum(len(o.data.polygons) for o in objects);folder=P/ROOT/name;'unused'
 (folder/'Models').mkdir(parents=True,exist_ok=True);(folder/'Materials').mkdir(exist_ok=True)
 fbx=folder/'Models'/(name+'_Rebuilt.fbx');bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=False,object_types={'MESH'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=False,path_mode='STRIP',use_mesh_modifiers=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(R/(name+'_retopo.blend')))
 source=next(a for a in old if a['name']==name);manifest=[a for a in manifest if a['name']!=name];manifest.append({'name':name,'sizeUnity':size,'prefabPath':source['prefabPath'],'modelPath':fbx.relative_to(P).as_posix(),'highTriangles':high,'lowTriangles':low,'method':'Exact sealed architectural cage with separate solid details; high bevel model first, collapse retopology and welded triangulation; separate glass shell for observation window'})
 (R/'rebuild_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');print('BUILT',name,high,low,flush=True)
