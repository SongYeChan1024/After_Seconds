"""수정된 판 간격을 Blender 원본과 패널 FBX에 반영한다. UV와 나머지 세 부품은 유지한다."""
import bpy,json,shutil
from pathlib import Path
from mathutils import Vector
repo=Path(__file__).resolve().parents[4];tmp=repo/'tmp/ArchitectureDetail_20261104';source=repo/'SourceAssets/ArchitectureDetail/ArchitectureDetail_Clean.blend';out=repo/'Docs/검수/2026-11-04_Architecture_Detail'
backup=tmp/'ArchitectureDetail_before_clearance.blend'
if not backup.exists():shutil.copyfile(source,backup)
bpy.ops.wm.open_mainfile(filepath=str(source))
data=json.loads((tmp/'panel_template.json').read_text());old=json.loads((tmp/'panel_template.before_clearance.json').read_text())
lo=Vector(data['sourceBounds']['min']);hi=Vector(data['sourceBounds']['max']);size=hi-lo;center=(lo+hi)*.5
changed={tuple(round(x,6) for x in (ov[0]*size.x+center.x,-ov[2]*size.y+center.y,ov[1]*size.z+center.z)) for ov,nv in zip(old['vertices'],data['vertices']) if ov!=nv}
atlas=bpy.data.objects['Production_Atlas_Assembly'];atlas.hide_render=True
sx=.962/.966;sz=1.162/1.166
mesh=atlas.data;normals=[n.vector.copy() for n in mesh.corner_normals];changed_ids=set()
for v in mesh.vertices:
 if tuple(round(x,6) for x in v.co) in changed:
  v.co.x=center.x+(v.co.x-center.x)*sx;v.co.z=center.z+(v.co.z-center.z)*sz;changed_ids.add(v.index)
mesh.update()
mesh.normals_split_custom_set([tuple(Vector((n.x/sx,n.y,n.z/sz)).normalized()) if mesh.loops[i].vertex_index in changed_ids else tuple(n) for i,n in enumerate(normals)])
editable=bpy.data.objects.get('panel_Replaceable_Enamel_Panel')
if editable:editable.dimensions.x*=sx;editable.dimensions.z*=sz
previous=bpy.data.objects.get('AD_panel_Manufactured')
if previous:bpy.data.objects.remove(previous,do_unlink=True)
coords=[(v[0]*size.x,-v[2]*size.y,v[1]*size.z) for v in data['vertices']];nn=[tuple(Vector((n[0]/size.x,-n[2]/size.y,n[1]/size.z)).normalized()) for n in data['normals']];ii=data['submeshes'][0]
model=bpy.data.meshes.new('AD_panel_Manufactured_Clearance');model.from_pydata(coords,[],[ii[i:i+3] for i in range(0,len(ii),3)]);model.update();uv=model.uv_layers.new(name='UVMap')
for loop in model.loops:uv.data[loop.index].uv=data['uv'][loop.vertex_index]
for p in model.polygons:p.use_smooth=True
model.normals_split_custom_set([nn[l.vertex_index] for l in model.loops]);obj=bpy.data.objects.new('AD_panel_Manufactured',model);bpy.context.scene.collection.objects.link(obj);model.materials.append(atlas.data.materials[0])
bpy.ops.object.select_all(action='DESELECT');obj.hide_set(False);obj.select_set(True);bpy.context.view_layer.objects.active=obj
folder=tmp/'clean-fbx';folder.mkdir(exist_ok=True)
bpy.ops.export_scene.fbx(filepath=str(folder/'AD_panel_Manufactured.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_anim=False,add_leaf_bones=False,path_mode='AUTO')
for o in bpy.data.objects:
 if o.type=='MESH':o.hide_render=(o!=obj)
scene=bpy.context.scene;cam=scene.camera;cam.location=(2,-6,1.6);cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.8;scene.render.filepath=str(out/'AD_Panel_ClearanceFixed.png');scene.cycles.samples=16;bpy.ops.render.render(write_still=True)
obj.location=(0,.35,2.3);obj.hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(source))
print('PANEL_CLEARANCE_FBX_DONE',len(changed_ids),flush=True)
