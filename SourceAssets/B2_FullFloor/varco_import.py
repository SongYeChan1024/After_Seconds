import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B2';records=[]
for name,height in [('B2_EmergencyGenerator',1.80)]:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
 bpy.ops.import_scene.gltf(filepath=str(H/(name+'.glb')))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];points=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box];low=Vector([min(v[i] for v in points) for i in range(3)]);high=Vector([max(v[i] for v in points) for i in range(3)]);center=Vector(((low.x+high.x)/2,(low.y+high.y)/2,low.z));scale=height/(high.z-low.z)
 mats=[]
 for i,m in enumerate([m for m in bpy.data.materials if m.users]):
  m.name=name+'_PBR_'+str(i);nodes=[]
  for nd in m.node_tree.nodes:
   if nd.type=='TEX_IMAGE' and nd.image:
    im=nd.image;filename=name+'_'+str(i)+'_'+str(len(nodes))+'.png';im.filepath_raw=str(O/'Textures'/filename);im.file_format='PNG';im.save();nodes.append({'name':nd.name,'file':filename,'links':[(l.to_node.type,l.to_socket.name) for l in nd.outputs[0].links]})
  mats.append({'name':m.name,'textures':nodes})
 tris=0;degen=0
 for o in meshes:
  world=o.matrix_world.copy();o.parent=None;o.matrix_world.identity()
  for v in o.data.vertices:v.co=(world@v.co-center)*scale
  bm=bmesh.new();bm.from_mesh(o.data);n=len(bm.faces);bmesh.ops.dissolve_degenerate(bm,dist=.000001,edges=list(bm.edges));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces));degen+=n-len(bm.faces);bm.to_mesh(o.data);bm.free();tris+=len(o.data.polygons)
  for p in o.data.polygons:p.use_smooth=True
 bpy.ops.object.select_all(action='DESELECT')
 for o in meshes:o.select_set(True)
 bpy.context.view_layer.objects.active=meshes[0];bpy.ops.wm.save_as_mainfile(filepath=str(H/(name+'_Prepared.blend')))
 bpy.ops.export_scene.fbx(filepath=str(O/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=False,bake_space_transform=True)
 records.append({'name':name,'asset':'Assets/Afrer_Seconds/05.Model/Props/B2/'+name+'.fbx','height':height,'triangles':tris,'materials':mats})
 # Source mesh preview with PBR, no geometry changes for presentation.
 scene=bpy.context.scene;scene.world=bpy.data.worlds.new('ReviewWorld');scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=720;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.world.color=(.22,.22,.22)
 for loc,power,size in [((2,-3,4),350,3),((-2,1,3),250,2)]:
  bpy.ops.object.light_add(type='AREA',location=tuple(a*height for a in loc));bpy.context.object.data.energy=power*height*height;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=size*height;bpy.context.object.rotation_euler=(Vector((0,0,height*.5))-bpy.context.object.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add(location=(height*1.5,-height*2.1,height*1.35));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,height*.5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=max((high-low)*scale)*1.45;scene.camera=cam;scene.render.filepath=str(H/(name+'_mesh.png'));bpy.ops.render.render(write_still=True)
(H/'varco_assets.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print('B2_VARCO_READY',flush=True)
