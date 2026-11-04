"""정확한 실제 치수의 FBX와 역할별 독립 프리뷰를 만든다. 원래 부품은 보존한다."""
import bpy,json,math
from mathutils import Vector
from pathlib import Path
REPO=Path(__file__).resolve().parents[4];TMP=REPO/'tmp/ArchitectureDetail_20261104';OUT=REPO/'Docs/검수/2026-11-04_Architecture_Detail';SOURCE=REPO/'SourceAssets/ArchitectureDetail'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'ArchitectureDetail_Clean.blend'))
atlas=bpy.data.objects['Production_Atlas_Assembly'];material=atlas.data.materials[0];atlas.hide_render=True;atlas.hide_set(True)
collection=bpy.data.collections.new('Production_Separated_Models');bpy.context.scene.collection.children.link(collection)
objects={};fbxdir=TMP/'clean-fbx';fbxdir.mkdir(exist_ok=True)
for role in ('pillar','reveal','sign','panel'):
 data=json.loads((TMP/(role+'_template.json')).read_text(encoding='utf-8-sig'));lo=Vector(data['sourceBounds']['min']);hi=Vector(data['sourceBounds']['max']);size=hi-lo
 coords=[(v[0]*size.x,-v[2]*size.y,v[1]*size.z) for v in data['vertices']];normals=[tuple(Vector((n[0]/size.x,-n[2]/size.y,n[1]/size.z)).normalized()) for n in data['normals']];indices=data['submeshes'][0];mesh=bpy.data.meshes.new('AD_'+role+'_Manufactured');mesh.from_pydata(coords,[],[indices[i:i+3] for i in range(0,len(indices),3)]);mesh.update();uv=mesh.uv_layers.new(name='UVMap')
 for loop in mesh.loops:uv.data[loop.index].uv=data['uv'][loop.vertex_index]
 for p in mesh.polygons:p.use_smooth=True
 mesh.normals_split_custom_set([normals[loop.vertex_index] for loop in mesh.loops]);obj=bpy.data.objects.new('AD_'+role+'_Manufactured',mesh);collection.objects.link(obj);mesh.materials.append(material);objects[role]=obj
 bpy.ops.object.select_all(action='DESELECT');obj.hide_set(False);obj.select_set(True);bpy.context.view_layer.objects.active=obj
 bpy.ops.export_scene.fbx(filepath=str(fbxdir/('AD_'+role+'_Manufactured.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_anim=False,add_leaf_bones=False,path_mode='AUTO')
for obj in objects.values():obj.hide_render=True
scene=bpy.context.scene;cam=scene.camera;cam.data.type='ORTHO';scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.cycles.samples=32
def look(target):cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
for role,scale in [('pillar',5.5),('reveal',3.3),('sign',2.25),('panel',1.8)]:
 obj=objects[role];obj.hide_render=False;cam.location=(2,-6,1.6);look((0,0,0));cam.data.ortho_scale=scale;scene.render.filepath=str(OUT/('AD_Clean_'+role+'.png'));bpy.ops.render.render(write_still=True);obj.hide_render=True
for role,obj in objects.items():
 obj.hide_render=False;obj.location={'pillar':(-2.5,0,1.8),'reveal':(0,0,.4),'sign':(2.5,0,2.1),'panel':(0,.35,2.3)}[role]
cam.location=(6,-11,5.5);look((0,0,1.7));cam.data.ortho_scale=8.3;scene.render.filepath=str(OUT/'AD_Clean_Kit.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'ArchitectureDetail_Clean.blend'))
print('CLEAN_FBX_AND_PREVIEWS_READY',flush=True)
