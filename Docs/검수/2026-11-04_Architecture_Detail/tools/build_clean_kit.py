"""VARCO 시안을 참고해 치수와 모서리를 제어한 건축 마감 3종을 직접 제작한다."""
# 의사코드: 실제 부품 치수 → 덮개/고정대/가스켓/볼트 조립 → 베벨/가중 노멀
# → 공용 UV atlas와 PBR 베이크 → 원본 편집 부품을 보존하고 Unity 좌표 데이터 출력.
import bpy,math,json
import numpy as np
from mathutils import Vector
from pathlib import Path
REPO=Path(__file__).resolve().parents[4];TMP=REPO/'tmp/ArchitectureDetail_20261104';OUT=REPO/'Docs/검수/2026-11-04_Architecture_Detail';SOURCE=REPO/'SourceAssets/ArchitectureDetail';MODEL=REPO/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/Common'
for p in (TMP,OUT,SOURCE,MODEL/'Textures'):p.mkdir(exist_ok=True,parents=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.use_denoising=True
parts=[];role='';offset=Vector((0,0,0));materials={}

def material(name,color,metal,rough,emission=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 n=m.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=450;n.inputs['Detail'].default_value=2
 ramp=m.node_tree.nodes.new('ShaderNodeMapRange');ramp.inputs['From Min'].default_value=0;ramp.inputs['From Max'].default_value=1;ramp.inputs['To Min'].default_value=max(.1,rough-.065);ramp.inputs['To Max'].default_value=min(.95,rough+.065);m.node_tree.links.new(n.outputs['Fac'],ramp.inputs['Value']);m.node_tree.links.new(ramp.outputs['Result'],p.inputs['Roughness'])
 bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.00013;m.node_tree.links.new(n.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
 if emission:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
 materials[name]=m;return m
paint=material('Clinical_Enamel',(.57,.63,.66),.25,.43)
dark=material('Anodised_Charcoal',(.035,.045,.054),.7,.34)
steel=material('Brushed_Stainless',(.32,.35,.37),.9,.29)
rubber=material('Neoprene_Gasket',(.009,.012,.015),0,.78)
blue=material('Recessed_Blue_Identity',(.035,.13,.21),.25,.39)
light=material('Diffuser',(.65,.8,.85),.05,.35,1.2)

def finish(o,name,mat,bevel=.0015):
 o.name=role+'_'+name;o.location+=offset;o.data.materials.append(mat);o['role']=role
 if bevel:
  mod=o.modifiers.new('Machined_Edge','BEVEL');mod.width=bevel;mod.segments=3;mod.limit_method='ANGLE'
  norm=o.modifiers.new('Weighted_Planar_Normals','WEIGHTED_NORMAL');norm.keep_sharp=True
 for p in o.data.polygons:p.use_smooth=True
 parts.append(o);return o
def box(name,loc,size,mat,bevel=.0015):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,name,mat,min(bevel,min(size)*.22))
def bolt(name,x,y,z,r=.0035):
 bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=.0028,end_fill_type='NGON',location=(x,y,z),rotation=(math.pi/2,0,0));o=bpy.context.object;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,name,steel,.00045)
 bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=r*.42,depth=.0008,end_fill_type='NGON',location=(x,y-.0015,z),rotation=(math.pi/2,0,0));o=bpy.context.object;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,name+'_Socket',dark,.00012)
def polygon(w,h,c):return [(-w/2+c,-h/2),(w/2-c,-h/2),(w/2,-h/2+c),(w/2,h/2-c),(w/2-c,h/2),(-w/2+c,h/2),(-w/2,h/2-c),(-w/2,-h/2+c)]
def ring(name,outer,inner,front,back,mat):
 # X/Z의 닫힌 팔각형을 Y방향으로 압출한 프레임. 정면 법선은-Y.
 verts=[]
 for loop,y in ((outer,front),(inner,front),(outer,back),(inner,back)):verts.extend((x,y,z) for x,z in loop)
 n=len(outer);faces=[]
 for i in range(n):
  j=(i+1)%n;faces.extend(((i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);return finish(o,name,mat,.001)

role='pillar';offset=Vector((-2.5,0,0))
box('Structural_Backbone',(0,0,1.8),(.148,.13,3.57),dark,.0025)
for sign in (-1,1):
 box('Continuous_Side_Cover',(sign*.074,0,1.8),(.012,.146,3.56),paint,.002)
 box('Recessed_Side_Seal',(sign*.063,-.067,1.8),(.008,.006,3.46),rubber,.0008)
for index,(lo,hi) in enumerate(((.25,1.195),(1.207,2.39),(2.402,3.40))):
 box('Removable_Face_'+str(index),(0,-.067,(lo+hi)/2),(.116,.008,hi-lo),paint,.002)
 for z in (lo+.026,hi-.026):
  for x in (-.042,.042):bolt('Recessed_Fixing',x,-.072,z)
box('Service_Access_Lid',(0,-.073,3.23),(.083,.003,.12),steel,.0015)
box('Blue_Access_Notch',(0,-.075,3.19),(.031,.001,.008),blue,.0006)
for z in (.117,3.565):box('Protective_End_Cap',(0,0,z),(.16,.15,.22 if z<1 else .07),steel,.003)
box('Foot_Isolation_Gasket',(0,0,.012),(.154,.144,.024),rubber,.002)

role='reveal';offset=Vector((0,0,.5))
box('Extruded_Carrier',(0,.009,0),(2.744,.058,.096),dark,.002)
for z in (-.041,.041):box('Folded_Outer_Lip',(0,-.008,z),(2.752,.064,.018),paint,.002)
box('Recessed_Bumper_Seal',(0,-.026,0),(2.768,.012,.054),rubber,.001)
box('Replaceable_Central_Insert',(0,-.035,0),(2.735,.008,.036),blue,.0015)
for x in (-1.386,1.386):box('Closed_Endcap',(x,-.002,0),(.028,.076,.098),steel,.002)
for x in (-1.19,-.397,.397,1.19):bolt('Front_Fixing',x,-.0395,0,.0032)

role='sign';offset=Vector((2.65,0,1.8))
box('Closed_Rear_Casing',(0,.006,0),(1.77,.057,.425),dark,.012)
ring('Machined_Outer_Frame',polygon(1.8,.45,.03),polygon(1.62,.328,.014),-.035,-.005,paint)
ring('Inner_Stainless_Bezel',polygon(1.633,.342,.015),polygon(1.60,.313,.012),-.0365,-.028,steel)
box('Recessed_Legend_Backing',(0,-.026,0),(1.614,.006,.324),rubber,.004)
for x in (-.839,.839):
 for z in (-.166,.166):bolt('Tamper_Resistant_Screw',x,-.036,z,.0045)
for x in (-.60,.60):box('Rear_Wall_Bracket',(x,.044,0),(.085,.022,.15),steel,.003)
box('Diffuser_Channel',(0,-.036,.187),(1.31,.004,.016),dark,.002)
box('Low_Glare_Diffuser',(0,-.038,.187),(1.26,.002,.009),light,.001)
box('Blue_Identity_Tab',(-.683,-.036,.187),(.026,.004,.012),blue,.001)

role='panel';offset=Vector((0,.5,2.3))
box('Isolation_Gasket',(0,.003,0),(.994,.006,1.194),rubber,.001)
ring('Folded_Panel_Perimeter',polygon(1,1.2,.009),polygon(.966,1.166,.006),-.0115,-.001,paint)
box('Replaceable_Enamel_Panel',(0,-.006,0),(.962,.008,1.162),paint,.002)
for x in (-.462,.462):
 for z in (-.563,.563):
  bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.004,depth=.0012,location=(x,-.011,z),rotation=(math.pi/2,0,0));o=bpy.context.object;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,'Flush_Panel_Fixing',steel,0)
for o in parts:
 if o['role']=='panel':
  for mod in o.modifiers:
   if mod.type=='BEVEL':mod.segments=1

# 원래 부품과 편집 가능한 모디파이어를 보존하고 출력용 복사본만 적용한다.
editable=bpy.data.collections.new('Editable_Manufactured_Parts');scene.collection.children.link(editable)
for o in parts:
 for coll in list(o.users_collection):coll.objects.unlink(o)
 editable.objects.link(o)
copies=[]
for o in parts:
 copy=o.copy();copy.data=o.data.copy();scene.collection.objects.link(copy);copies.append(copy)
 bpy.ops.object.select_all(action='DESELECT');copy.select_set(True);bpy.context.view_layer.objects.active=copy
 for mod in list(copy.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 group=copy.vertex_groups.new(name='role_'+o['role']);group.add(list(range(len(copy.data.vertices))),1,'REPLACE')
editable.hide_render=True;editable.hide_viewport=True
bpy.ops.object.select_all(action='DESELECT')
for o in copies:o.select_set(True)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();atlas=bpy.context.object;atlas.name='Production_Atlas_Assembly'
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.004);bpy.ops.object.mode_set(mode='OBJECT')
scene.render.bake.margin=12;scene.render.bake.use_selected_to_active=False

def bake_image(name,kind,channel=None):
 image=bpy.data.images.new(name,width=2048,height=2048,alpha=True);image.colorspace_settings.name='sRGB' if name.endswith(('BaseColor','Emission')) else 'Non-Color';restore=[];temporary=[]
 for slot in atlas.material_slots:
  m=slot.material;nodes=m.node_tree.nodes;links=m.node_tree.links;p=nodes.get('Principled BSDF');output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL');saved=[(l.from_socket,l.to_socket) for l in output.inputs['Surface'].links];restore.extend((m,a,b) for a,b in saved)
  tex=nodes.new('ShaderNodeTexImage');tex.image=image;nodes.active=tex;temporary.append((m,tex))
  if kind=='EMIT':
   emit=nodes.new('ShaderNodeEmission');temporary.append((m,emit))
   if channel=='color':emit.inputs['Color'].default_value=p.inputs['Base Color'].default_value
   elif channel=='emission':emit.inputs['Color'].default_value=p.inputs['Emission Color'].default_value if p.inputs['Emission Strength'].default_value>0 else (0,0,0,1)
   else:
    combine=nodes.new('ShaderNodeCombineXYZ');combine.inputs['X'].default_value=p.inputs['Metallic'].default_value;combine.inputs['Z'].default_value=1
    if p.inputs['Roughness'].is_linked:links.new(p.inputs['Roughness'].links[0].from_socket,combine.inputs['Y'])
    else:combine.inputs['Y'].default_value=p.inputs['Roughness'].default_value
    links.new(combine.outputs[0],emit.inputs['Color']);temporary.append((m,combine))
   links.new(emit.outputs[0],output.inputs['Surface'])
 bpy.ops.object.bake(type=kind)
 for m,node in temporary:m.node_tree.nodes.remove(node)
 for m,a,b in restore:m.node_tree.links.new(a,b)
 path=MODEL/'Textures'/(name+'.png');image.filepath_raw=str(path);image.file_format='PNG';image.save();image.pack();return image

albedo=bake_image('AD_Manufactured_BaseColor','EMIT','color')
emission=bake_image('AD_Manufactured_Emission','EMIT','emission')
orm=bake_image('AD_Manufactured_ORM_Source','EMIT','orm')
normal=bake_image('AD_Manufactured_Normal','NORMAL')
ao=bake_image('AD_Manufactured_Occlusion','AO')
pixels=np.empty(2048*2048*4,np.float32);orm.pixels.foreach_get(pixels);pixels=pixels.reshape(2048,2048,4);packed=np.zeros_like(pixels);packed[:,:,0]=pixels[:,:,0];packed[:,:,3]=1-pixels[:,:,1]
im=bpy.data.images.new('AD_Manufactured_MetallicSmoothness',width=2048,height=2048,alpha=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(packed.ravel());im.filepath_raw=str(MODEL/'Textures/AD_Manufactured_MetallicSmoothness.png');im.file_format='PNG';im.save();im.pack()

mesh=atlas.data;mesh.calc_loop_triangles();facts=[]
for role in ('pillar','reveal','sign','panel'):
 group=atlas.vertex_groups['role_'+role].index;members={v.index for v in mesh.vertices if any(g.group==group for g in v.groups)};vv=[mesh.vertices[i].co.copy() for i in members];low=Vector(tuple(min(v[i] for v in vv) for i in range(3)));high=Vector(tuple(max(v[i] for v in vv) for i in range(3)));size=high-low;center=(low+high)*.5
 vertices=[];normals=[];uv=[];triangles=[]
 for tri in mesh.loop_triangles:
  if not all(i in members for i in tri.vertices):continue
  for li in tri.loops:
   loop=mesh.loops[li];v=mesh.vertices[loop.vertex_index].co-center;n=mesh.corner_normals[li].vector
   vertices.append([v.x/size.x,v.z/size.z,-v.y/size.y]);normals.append(list(Vector((n.x*size.x,n.z*size.z,-n.y*size.y)).normalized()));uv.append(list(mesh.uv_layers.active.data[li].uv));triangles.append(len(vertices)-1)
 data={'vertices':vertices,'normals':normals,'uv':uv,'uv2':[],'submeshes':[triangles],'front':'+Z','sourceBounds':{'min':list(low),'max':list(high)},'materials':[{'textures':{'BaseColor':'AD_Manufactured_BaseColor.png','Normal':'AD_Manufactured_Normal.png','MetallicSmoothness':'AD_Manufactured_MetallicSmoothness.png','Occlusion':'AD_Manufactured_Occlusion.png'}}]}
 (TMP/(role+'_template.json')).write_text(json.dumps(data,separators=(',',':')),encoding='utf-8');facts.append({'role':role,'triangles':len(triangles)//3,'physicalSizeBlender':list(size)})

# 베이크 결과 표시 재질. 편집 컬렉션은 원래 부품 재질을 유지한다.
preview=bpy.data.materials.new('AD_Manufactured_Atlas_Preview');preview.use_nodes=True;p=preview.node_tree.nodes.get('Principled BSDF');nodes=preview.node_tree.nodes;links=preview.node_tree.links
tex=nodes.new('ShaderNodeTexImage');tex.image=albedo;links.new(tex.outputs['Color'],p.inputs['Base Color']);tex=nodes.new('ShaderNodeTexImage');tex.image=orm;sep=nodes.new('ShaderNodeSeparateColor');links.new(tex.outputs['Color'],sep.inputs[0]);links.new(sep.outputs['Red'],p.inputs['Metallic']);links.new(sep.outputs['Green'],p.inputs['Roughness']);tex=nodes.new('ShaderNodeTexImage');tex.image=normal;nm=nodes.new('ShaderNodeNormalMap');links.new(tex.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs['Normal'],p.inputs['Normal']);tex=nodes.new('ShaderNodeTexImage');tex.image=emission;links.new(tex.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=1.2
atlas.data.materials.clear();atlas.data.materials.append(preview)
for poly in atlas.data.polygons:poly.material_index=0
scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.32,.36,.40,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
def look(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
for loc,power in (((-2,-4,6),1100),((4,-3,4),900),((1,3,6),1200)):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=4;look(o,(0,0,1.5))
bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';scene.camera=cam;scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.cycles.samples=32
for role,center,width in (('pillar',(-2.5,0,1.8),4.3),('reveal',(0,0,.5),3.3),('sign',(2.65,0,1.8),2.2)):
 cam.location=Vector(center)+Vector((2,-6,1.6));look(cam,center);cam.data.ortho_scale=width;scene.render.filepath=str(OUT/('AD_Clean_'+role+'.png'));bpy.ops.render.render(write_still=True)
cam.location=(7,-11,6);look(cam,(0,0,1.8));cam.data.ortho_scale=9;scene.render.filepath=str(OUT/'AD_Clean_Kit.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'ArchitectureDetail_Clean.blend'))
(OUT/'clean_kit_manifest.json').write_text(json.dumps({'method':'Hand-authored procedural Blender assembly based on VARCO image references; raw generated meshes rejected for construction distortion','roles':facts,'atlasResolution':2048,'textures':['AD_Manufactured_BaseColor.png','AD_Manufactured_Normal.png','AD_Manufactured_MetallicSmoothness.png','AD_Manufactured_Occlusion.png']},indent=2),encoding='utf-8')
print('CLEAN_ARCHITECTURE_KIT_DONE',facts,flush=True)

