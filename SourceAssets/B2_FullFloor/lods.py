"""Keep original near meshes; make shared, UV-preserving distant meshes only."""
from pathlib import Path
import bpy,bmesh,json,struct,numpy as np
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/B4';plan=json.loads((H/'lod_plan.json').read_text(encoding='utf8'));results=[]
for p in plan:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 with (H/'mesh_data'/f"{p['name']}.bin").open('rb') as f:
  count,subs=struct.unpack('<ii',f.read(8));a=np.frombuffer(f.read(count*32),dtype='<f4').reshape(count,8).copy();tris=[];mi=[]
  for sub in range(subs):
   n=struct.unpack('<i',f.read(4))[0];t=np.frombuffer(f.read(n*4),dtype='<i4').reshape(-1,3).copy();tris.extend(t.tolist());mi.extend([sub]*len(t))
 xyz=a[:,:3][:,[0,2,1]].copy();xyz[:,:2]*=-1
 tris=[(t[0],t[2],t[1]) for t in tris] # reflection changes winding
 O=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model'/('Props' if '/Props/' in p['asset'] else 'Environment')/'B2'
 me=bpy.data.meshes.new(p['name']);me.from_pydata(xyz.tolist(),[],tris);me.update();src=bpy.data.objects.new(p['name'],me);bpy.context.collection.objects.link(src)
 for i,n in enumerate(p['materialNames']):me.materials.append(bpy.data.materials.new('FL_SLOT_'+str(i).zfill(2)))
 uv=me.uv_layers.new(name='UVMap')
 for face,mat in zip(me.polygons,mi):
  face.material_index=mat;face.use_smooth=True
  for li in face.loop_indices:uv.data[li].uv=a[me.loops[li].vertex_index,6:8]
 normals=a[:,3:6][:,[0,2,1]].copy();normals[:,:2]*=-1;me.normals_split_custom_set_from_vertices(normals.tolist())
 for lod,ratio in [(1,.43),(2,.16)]:
  ob=src.copy();ob.data=src.data.copy();bpy.context.collection.objects.link(ob);ob.name=p['name']+'_LOD'+str(lod);bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
  dec=ob.modifiers.new('Distance_Only_Decimation','DECIMATE');dec.ratio=ratio;dec.use_collapse_triangulate=True;dec.delimit={'MATERIAL','UV','SEAM'};bpy.ops.object.modifier_apply(modifier=dec.name)
  bm=bmesh.new();bm.from_mesh(ob.data);bad=[f for f in bm.faces if f.calc_area()<1e-8];bmesh.ops.delete(bm,geom=bad,context='FACES');bm.to_mesh(ob.data);bm.free()
  bpy.ops.export_scene.fbx(filepath=str(O/(ob.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE')
  ob.data.calc_loop_triangles();results.append(dict(name=ob.name,source=p['asset'],lod=lod,triangles=len(ob.data.loop_triangles),ratio=len(ob.data.loop_triangles)/p['tri'],slots=sorted(set(x.material_index for x in ob.data.polygons))));bpy.data.objects.remove(ob,do_unlink=True)
 (H/'lod_models.json').write_text(json.dumps(results,indent=2),encoding='utf8');print('DISTANT_LODS',p['name'],results[-2]['triangles'],results[-1]['triangles'],flush=True)
print('LODS_DONE',len(results),flush=True)
