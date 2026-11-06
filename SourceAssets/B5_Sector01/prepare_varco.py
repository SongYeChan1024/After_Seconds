"""VARCO prop preparation V0.01. Metric normalization, bevel, PBR extraction, LODs."""
import bpy,bmesh,json,math,numpy as np,sys
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1]
OUT=REPO/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B5'
TEX=OUT/'Textures';TEX.mkdir(parents=True,exist_ok=True)
REPORT=REPO/'Docs/검수/2026-11-06_B5_Sector01';REPORT.mkdir(parents=True,exist_ok=True)
sizes={'IsolationBed':(.85,2.05,.80),'SanitaryUnit':(.6,.8,.95),'VitalMonitor':(.55,.55,1.48)}

def pixels_save(name,arr):
 h,w,c=arr.shape;im=bpy.data.images.new(name,width=w,height=h,alpha=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(arr.astype(np.float32).reshape(-1));im.filepath_raw=str(TEX/(name+'.png'));im.file_format='PNG';im.save();return im
def render(name,ob,height,back=False):
 sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=16;sc.render.resolution_x=640;sc.render.resolution_y=640;sc.render.resolution_percentage=100
 sc.world=bpy.data.worlds.new('ReviewWorld');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.25,.28,.30,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
 camd=bpy.data.cameras.new('Review');cam=bpy.data.objects.new('Review',camd);sc.collection.objects.link(cam);sc.camera=cam
 s=-1 if back else 1;cam.location=(height*1.5*s,-height*2.2*s,height*1.5);target=Vector((0,0,height*.45));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=max(height*1.5,ob.dimensions.x*1.6,ob.dimensions.y*1.6)
 lights=[]
 for pos,power,scale in [((2,-3,4),550,3),((-3,0,2),350,2),((0,3,4),500,2)]:
  ld=bpy.data.lights.new('ReviewLight','AREA');ld.energy=power;ld.shape='DISK';ld.size=scale;lo=bpy.data.objects.new('ReviewLight',ld);sc.collection.objects.link(lo);lo.location=Vector(pos)*height;lo.rotation_euler=(target-lo.location).to_track_quat('-Z','Y').to_euler();lights.append(lo)
 sc.render.filepath=str(REPORT/(name+('_back' if back else '_front')+'.png'));sc.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True)
 for x in lights+[cam]:bpy.data.objects.remove(x,do_unlink=True)
 sc.camera=None
manifest=[]
names=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else list(sizes)
for name in names:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene;sc.unit_settings.system='METRIC'
 bpy.ops.import_scene.gltf(filepath=str(HERE/'Varco'/('S1_'+name+'.glb')))
 obs=[o for o in sc.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
 for ob in obs:ob.select_set(True)
 bpy.context.view_layer.objects.active=obs[0]
 if len(obs)>1:bpy.ops.object.join()
 ob=bpy.context.object;ob.name='S1_'+name+'_LOD0'
 bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 lo=Vector(tuple(min(v.co[i] for v in ob.data.vertices) for i in range(3)));hi=Vector(tuple(max(v.co[i] for v in ob.data.vertices) for i in range(3)));dim=hi-lo
 target=sizes[name];factor=Vector(((2.05/max(dim.x,dim.y)) if name=='IsolationBed' else (target[2]/dim.z),)*3);target=(dim.x*factor.x,dim.y*factor.y,dim.z*factor.z)
 for v in ob.data.vertices:v.co=Vector(((v.co.x-(lo.x+hi.x)/2)*factor.x,(v.co.y-(lo.y+hi.y)/2)*factor.y,(v.co.z-lo.z)*factor.z))
 ob.location=(0,0,0);ob.data.update()
 # Explicit edge treatment; only sharp manufactured angles, UVs and original sculpt preserved.
 bm=bmesh.new();bm.from_mesh(ob.data);deg=[f for f in bm.faces if f.calc_area()<1e-12]
 bmesh.ops.delete(bm,geom=deg,context='FACES');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
 bevel=ob.modifiers.new('Manufactured_Edge_Bevel_1mm','BEVEL');bevel.width=.001;bevel.segments=2;bevel.limit_method='ANGLE';bevel.angle_limit=math.radians(55);bevel.use_clamp_overlap=True;bevel.harden_normals=True
 materialrows=[]
 for idx,mat in enumerate(ob.data.materials):
  mat.name='S1_'+name+('_'+str(idx) if idx else '');tree=mat.node_tree;bs=next(n for n in tree.nodes if n.type=='BSDF_PRINCIPLED');info={'name':mat.name}
  for slot,key in [('Base Color','Albedo'),('Roughness','ORM'),('Normal','Normal')]:
   links=list(bs.inputs[slot].links)
   if not links:continue
   node=links[0].from_node
   if node.type=='NORMAL_MAP':node=node.inputs['Color'].links[0].from_node if node.inputs['Color'].links else node
   if node.type=='SEPARATE_COLOR':node=node.inputs['Color'].links[0].from_node
   if node.type=='SEPRGB':node=node.inputs[0].links[0].from_node
   if node.type!='TEX_IMAGE':continue
   im=node.image;path=TEX/(mat.name+'_'+key+'.png');im.filepath_raw=str(path);im.file_format='PNG';im.save();info[key]=path.name
   if key=='ORM':
    a=np.empty(len(im.pixels),np.float32);im.pixels.foreach_get(a);a=a.reshape(im.size[1],im.size[0],4);out=np.ones_like(a);out[:,:,0]=a[:,:,2];out[:,:,1:3]=0;out[:,:,3]=1-a[:,:,1];pixels_save(mat.name+'_MetallicSmoothness',out);info['MetallicSmoothness']=mat.name+'_MetallicSmoothness.png'
  materialrows.append(info)
 ob['source']='VARCO V0.03; remeshed then Blender metric/bevel/LOD';ob['bevel_width_m']=.001
 bpy.ops.wm.save_as_mainfile(filepath=str(HERE/('S1_'+name+'.blend')))
 render(name,ob,target[2]);render(name,ob,target[2],True)
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=bevel.name)
 output=[ob];tris=[]
 for i,ratio in enumerate([1,.40,.12]):
  if i:lod=ob.copy();lod.data=ob.data.copy();sc.collection.objects.link(lod);lod.name='S1_'+name+'_LOD'+str(i);bpy.context.view_layer.objects.active=lod;m=lod.modifiers.new('LOD_Reduction','DECIMATE');m.ratio=ratio;bpy.ops.object.modifier_apply(modifier=m.name);output.append(lod)
  else:lod=ob
  bm=bmesh.new();bm.from_mesh(lod.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(lod.data);bm.free();tris.append(len(lod.data.polygons))
 bpy.ops.object.select_all(action='DESELECT')
 for x in output:x.select_set(True)
 bpy.context.view_layer.objects.active=ob
 bpy.ops.export_scene.fbx(filepath=str(OUT/('S1_'+name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,use_mesh_modifiers=True,bake_anim=False,mesh_smooth_type='FACE',use_custom_props=True,path_mode='STRIP')
 manifest.append(dict(name=name,dimensions=[target[0],target[2],target[1]],triangles=tris,materials=materialrows,degenerateRemoved=len(deg),source='VARCO remesh + Blender bevel/LOD'))
 (HERE/(name+'_manifest.json')).write_text(json.dumps(manifest[-1],indent=2))
 print('PROP_DONE',name,tris,flush=True)
