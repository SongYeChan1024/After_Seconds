"""VARCO 원본을 보존하고 Blender 원본·PBR 채널·명시적인 Unity 좌표 메시를 준비한다."""
# 의사코드: GLB 반입 → 원래 축과 UV를 기록 → 재질 채널을 Unity 규약으로 변환
# → 모서리 노멀/UV를 보존한 단위 메시 출력 → 앞/뒤 렌더와 편집 원본 저장.
import bpy,sys,json,math
import numpy as np
from pathlib import Path
from mathutils import Vector
REPO=Path(__file__).resolve().parents[4]
TMP=REPO/'tmp/ArchitectureDetail_20261104'
OUT=REPO/'Docs/검수/2026-11-04_Architecture_Detail'
SOURCE=REPO/'SourceAssets/ArchitectureDetail'
MODEL=REPO/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/Common'
for p in (OUT,SOURCE,MODEL/'Textures',MODEL/'Materials'):p.mkdir(exist_ok=True,parents=True)

def upstream_image(socket):
 seen=set();pending=[link.from_node for link in socket.links]
 while pending:
  node=pending.pop(0)
  if node.as_pointer() in seen:continue
  seen.add(node.as_pointer())
  if node.type=='TEX_IMAGE' and node.image:return node.image
  pending.extend(link.from_node for inp in node.inputs for link in inp.links)

def save_image(image,path):
 image.filepath_raw=str(path);image.file_format='PNG';image.save()

def packed_image(name,values,path):
 h,w,_=values.shape;im=bpy.data.images.new(name,width=w,height=h,alpha=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(values.astype(np.float32).ravel());save_image(im,path);im.pack();return im

def look(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

facts=[]
for label,stem in [('pillar','AD_Pillar_VARCO'),('reveal','AD_Reveal_VARCO'),('sign','AD_Wayfinding_VARCO')]:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 source=TMP/(stem+'.glb');bpy.ops.import_scene.gltf(filepath=str(source))
 objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
 bpy.ops.object.select_all(action='DESELECT')
 for obj in objects:obj.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();obj=bpy.context.object;obj.name=stem
 bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 mesh=obj.data;mesh.calc_loop_triangles()
 low=Vector(tuple(min(v.co[i] for v in mesh.vertices) for i in range(3)));high=Vector(tuple(max(v.co[i] for v in mesh.vertices) for i in range(3)));size=high-low;center=(high+low)*.5
 channels=[]
 for mi,slot in enumerate(obj.material_slots):
  mat=slot.material;pbr=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
  albedo=upstream_image(pbr.inputs['Base Color']);rough=upstream_image(pbr.inputs['Roughness']);normal=upstream_image(pbr.inputs['Normal'])
  files={}
  for channel,im in [('BaseColor',albedo),('Normal',normal)]:
   if im:
    path=MODEL/'Textures'/f'{stem}_{mi}_{channel}.png';save_image(im,path);files[channel]=path.name
  if rough:
   pixels=np.empty(rough.size[0]*rough.size[1]*4,np.float32);rough.pixels.foreach_get(pixels);pixels=pixels.reshape(rough.size[1],rough.size[0],4)
   values=np.zeros_like(pixels);values[:,:,0]=pixels[:,:,2];values[:,:,3]=1-pixels[:,:,1]
   path=MODEL/'Textures'/f'{stem}_{mi}_MetallicSmoothness.png';packed_image(stem+'_MetallicSmoothness',values,path);files['MetallicSmoothness']=path.name
   values=np.ones_like(pixels);values[:,:,:3]=pixels[:,:,0,None]
   path=MODEL/'Textures'/f'{stem}_{mi}_Occlusion.png';packed_image(stem+'_Occlusion',values,path);files['Occlusion']=path.name
  channels.append({'slot':mi,'name':mat.name,'textures':files})
 vertices=[];normals=[];uv=[];submeshes=[[] for _ in obj.material_slots]
 for tri in mesh.loop_triangles:
  for li in tri.loops:
   loop=mesh.loops[li];v=mesh.vertices[loop.vertex_index].co;raw=(v-center)
   # Blender Z-up → Unity Y-up. front -Y becomes +Z.
   vertices.append([raw.x/size.x,raw.z/size.z,-raw.y/size.y])
   n=mesh.corner_normals[li].vector;n=Vector((n.x*size.x,n.z*size.z,-n.y*size.y)).normalized();normals.append(list(n))
   uv.append(list(mesh.uv_layers.active.data[li].uv));submeshes[tri.material_index].append(len(vertices)-1)
 data={'vertices':vertices,'normals':normals,'uv':uv,'uv2':[],'submeshes':submeshes,'materials':channels,'front':'+Z','sourceBounds':{'min':list(low),'max':list(high)},'source':source.name}
 (TMP/(label+'_template.json')).write_text(json.dumps(data,separators=(',',':')),encoding='utf-8')
 for im in bpy.data.images:
  if im.size[0] and im.source!='GENERATED':
   try:im.pack()
   except RuntimeError:pass
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True;scene.render.resolution_x=840;scene.render.resolution_y=840;scene.render.resolution_percentage=100;scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.5,.5,.5,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
 radius=max(size)*2.4
 for loc,energy,scale in [((3,-4,5),1000,4),((-4,-2,2),700,3),((2,3,4),900,3)]:
  bpy.ops.object.light_add(type='AREA',location=center+Vector(loc).normalized()*radius);light=bpy.context.object;light.data.energy=energy;light.data.shape='DISK';light.data.size=radius*.8;look(light,center)
 bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=max(size)*1.3;scene.camera=cam
 for side in (-1,1):
  cam.location=center+Vector((.6,side*2,.35)).normalized()*radius;look(cam,center);scene.render.filepath=str(OUT/(stem+('_Front' if side==-1 else '_Back')+'.png'));bpy.ops.render.render(write_still=True)
 bpy.context.view_layer.objects.active=obj;bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
 bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/(stem+'.blend')))
 facts.append({'role':label,'source':source.name,'vertices':len(mesh.vertices),'triangles':len(mesh.loop_triangles),'bounds':{'min':list(low),'max':list(high)},'materials':channels})
(OUT/'varco_preparation.json').write_text(json.dumps(facts,indent=2),encoding='utf-8')
print('ARCH_VARCO_PREPARED',len(facts),flush=True)
