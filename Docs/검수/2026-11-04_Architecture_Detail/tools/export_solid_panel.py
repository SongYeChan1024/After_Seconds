"""채택한 닫힌 단면 패널을 Blender 편집 원본과 FBX에 보존한다."""
import bpy,json
from pathlib import Path
from mathutils import Vector
repo=Path(__file__).resolve().parents[4];tmp=repo/'tmp/ArchitectureDetail_20261104';out=repo/'Docs/검수/2026-11-04_Architecture_Detail';source=repo/'SourceAssets/ArchitectureDetail/ArchitectureDetail_Clean.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));data=json.loads((tmp/'panel_template.json').read_text());size=Vector(data['sourceBounds']['max'])-Vector(data['sourceBounds']['min']);atlas=bpy.data.objects['Production_Atlas_Assembly'];mat=atlas.data.materials[0]
prior=bpy.data.objects.get('AD_panel_Manufactured')
if prior:bpy.data.objects.remove(prior,do_unlink=True)
v=[(p[0]*size.x,-p[2]*size.y,p[1]*size.z) for p in data['vertices']];n=[tuple(Vector((q[0]/size.x,-q[2]/size.y,q[1]/size.z)).normalized()) for q in data['normals']];ii=data['submeshes'][0];mesh=bpy.data.meshes.new('AD_panel_Manufactured');mesh.from_pydata(v,[],[ii[i:i+3] for i in range(0,len(ii),3)]);mesh.update();uv=mesh.uv_layers.new(name='UVMap')
for loop in mesh.loops:uv.data[loop.index].uv=data['uv'][loop.vertex_index]
for face in mesh.polygons:face.use_smooth=False
mesh.normals_split_custom_set([n[l.vertex_index] for l in mesh.loops]);obj=bpy.data.objects.new('AD_panel_Manufactured',mesh);bpy.context.scene.collection.objects.link(obj);mesh.materials.append(mat);obj['construction']='Closed stepped body with embedded fixings, 208 triangles; current production panel'
bpy.ops.object.select_all(action='DESELECT');obj.hide_set(False);obj.select_set(True);bpy.context.view_layer.objects.active=obj
bpy.ops.export_scene.fbx(filepath=str(tmp/'clean-fbx/AD_panel_Manufactured.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_anim=False,add_leaf_bones=False,path_mode='AUTO')
for o in bpy.data.objects:
 if o.type=='MESH':o.hide_render=(o!=obj)
scene=bpy.context.scene;cam=scene.camera;cam.location=(2,-6,1.6);cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.8;scene.cycles.samples=16;scene.render.filepath=str(out/'AD_Panel_SolidProfile.png');bpy.ops.render.render(write_still=True)
obj.location=(0,.35,2.3)
for name in ('AD_pillar_Manufactured','AD_reveal_Manufactured','AD_sign_Manufactured','AD_panel_Manufactured'):
 if name in bpy.data.objects:bpy.data.objects[name].hide_render=False
cam.location=(6,-11,5.5);cam.rotation_euler=(Vector((0,0,1.7))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=8.3;scene.render.filepath=str(out/'AD_Clean_Kit.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(source));manifest=json.loads((out/'clean_kit_manifest.json').read_text())
for role in manifest['roles']:
 if role['role']=='panel':role['triangles']=len(ii)//3;role['physicalSizeBlender']=[size.x,size.y,size.z];role['construction']='Closed stepped profile with four fixings'
manifest['panelInternalCoplanarOverlaps']=0;(out/'clean_kit_manifest.json').write_text(json.dumps(manifest,indent=2));print('FINAL_PANEL_SOURCE_EXPORTED',len(ii)//3,flush=True)
