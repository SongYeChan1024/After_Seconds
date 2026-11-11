"""VARCO 국소 메시 보수 V0.01 · 송예찬. 원본 UV/형상을 보존하고 연결된 면에서 LOD 재생성."""
import bpy,bmesh,json,sys,math,numpy as np
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1];sys.path.insert(0,str(H))
from analyze import read
OUT=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B2'
rows=[]
def weld(me):
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
def topology(me):
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);a={'boundary':sum(e.is_boundary for e in bm.edges),'overused':sum(len(e.link_faces)>2 for e in bm.edges),'degenerate':sum(f.calc_area()<1e-12 for f in bm.faces)};bm.free();return a
def imported(key):
 v,uv,ix,mi=read(key);xyz=v[:,[0,2,1]];xyz[:,:2]*=-1
 me=bpy.data.meshes.new(key);me.from_pydata(xyz.tolist(),[],ix[:,[0,2,1]].tolist());layer=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  for li in p.loop_indices:layer.data[li].uv=uv[me.loops[li].vertex_index]
 ob=bpy.data.objects.new(key,me);bpy.context.collection.objects.link(ob);return ob
for name,ratios in [('SD_CylinderTrolley',[1,.40,.12]),('BM_HVACUnit',[.25,.10]),('B2_EmergencyGenerator',[1,.43,.16])]:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
 if name=='SD_CylinderTrolley':
  bpy.ops.wm.open_mainfile(filepath=str(R/'SourceAssets/B345_Dressing/SD_CylinderTrolley.blend'));src=next(o for o in bpy.context.scene.objects if o.type=='MESH')
  for m in list(src.modifiers):src.modifiers.remove(m)
 else:src=imported('BM_HVACUnit_source' if name=='BM_HVACUnit' else name+'_0')
 src.data.materials.clear();src.data.materials.append(bpy.data.materials.new('VA_OriginalMaterial'));weld(src.data)
 if src.data.has_custom_normals:src.data.normals_split_custom_set([(0,0,0)]*len(src.data.loops))
 for p in src.data.polygons:p.use_smooth=True
 levels=[];output=[]
 for level,ratio in enumerate(ratios):
  ob=src.copy();ob.data=src.data.copy();bpy.context.collection.objects.link(ob);ob.name='VA_'+name+'_LOD'+str(level);bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
  if ratio<1:
   mod=ob.modifiers.new('Welded_Surface_LOD','DECIMATE');mod.ratio=ratio;mod.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=mod.name)
  weld(ob.data)
  # Sharp manufactured edges remain hard; smooth cylinders and chamfers stay smooth.
  bm=bmesh.new();bm.from_mesh(ob.data)
  for e in bm.edges:e.smooth=not(e.is_manifold and e.calc_face_angle()>math.radians(50))
  bm.to_mesh(ob.data);bm.free();ob.data.update()
  normal=ob.modifiers.new('Aligned_Panel_Normals','WEIGHTED_NORMAL');normal.keep_sharp=True;normal.weight=50;bpy.ops.object.modifier_apply(modifier=normal.name)
  ob.data.calc_loop_triangles();stat=topology(ob.data)
  if stat['boundary'] or stat['overused']:raise RuntimeError((name,level,stat))
  levels.append(dict(name=ob.name,level=level,triangles=len(ob.data.loop_triangles),vertices=len(ob.data.vertices),**stat));output.append(ob)
 bpy.data.objects.remove(src,do_unlink=True)
 bpy.ops.object.select_all(action='DESELECT')
 for o in output:o.select_set(True)
 bpy.context.view_layer.objects.active=output[0]
 path=OUT/('VA_'+name+'.fbx');bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE',path_mode='STRIP')
 bpy.data.orphans_purge(do_recursive=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(H/('VA_'+name+'.blend')),compress=True)
 rows.append(dict(model=name,asset=path.relative_to(R/'Unity/After_Seconds_Build_V0.01').as_posix(),levels=levels));print('REPAIRED',rows[-1],flush=True)
 (H/'repair_models.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
