"""Apply verified surface clipping to this task's FBXs only, retaining GUIDs, normals and UVs."""
from pathlib import Path
import bpy,numpy as np,json,struct,collections,sys
H=Path(__file__).resolve().parent;R=H.parents[1];U=R/'Unity/After_Seconds_Build_V0.01';quality='--quality' in sys.argv;plan=json.loads((H/('quality_export_plan.json' if quality else 'geometry_verified/Level_1F_Factory.json')).read_text());source=json.loads((H/'clean_source.json').read_text());chosen={};groups=collections.defaultdict(list)
for q in plan['patches']:
 row=plan['rows'][q['renderer']];key=(row['mesh'],q['submesh'])
 if key not in chosen:chosen[key]=q
for q in source:groups[q['asset']].append(q)
report=[]
for asset,rows in groups.items():
 assert '/1F/F1_' in asset
 bpy.ops.wm.read_factory_settings(use_empty=True)
 for row in rows:
  with (U/'Temp/F1MeshClean'/f"{row['key']}.bin").open('rb') as f:
   n,subs,hasuv2=struct.unpack('<iii',f.read(12));stride=10 if hasuv2 else 8;data=np.frombuffer(f.read(n*stride*4),'<f4').reshape(n,stride).copy();indices=[]
   for si in range(subs):count=struct.unpack('<i',f.read(4))[0];indices.append(np.frombuffer(f.read(count*4),'<i4').reshape(-1,3).copy())
  vs=data.tolist();faces=[];slots=[]
  for si,ix in enumerate(indices):
   patch=chosen.get((row['key'],si));edits={e['triangle']:e['bary'] for e in patch['edits']} if patch else {}
   for ti,ids in enumerate(ix):
    if ti not in edits:
     pp=data[ids,:3];cross=np.cross(pp[1]-pp[0],pp[2]-pp[0]);area=np.linalg.norm(cross)
     if area<1e-10:continue
     ns=data[ids,3:6].mean(axis=0);dot=np.dot(cross/area,ns/max(np.linalg.norm(ns),1e-20))
     if quality and dot<-.5:
      face=[]
      for vid in ids:
       v=data[vid].copy();v[3:6]=cross/area;face.append(len(vs));vs.append(v.tolist())
      faces.append(face)
     else:faces.append(ids.tolist())
     slots.append(si);continue
    for bary in edits[ti]:
     face=[]
     for weights in bary:
      k=next((i for i,x in enumerate(weights) if abs(x-1)<1e-10),None)
      if k is not None:face.append(int(ids[k]));continue
      d=np.array(weights)@data[ids];norm=np.linalg.norm(d[3:6]);d[3:6]/=max(norm,1e-20);face.append(len(vs));vs.append(d.tolist())
     pp=np.array([vs[i][:3] for i in face]);area=np.linalg.norm(np.cross(pp[1]-pp[0],pp[2]-pp[0]))
     if area>1e-9:faces.append(face);slots.append(si)
  arr=np.array(vs);xyz=arr[:,[0,2,1]].copy();xyz[:,:2]*=-1;normal=arr[:,[3,5,4]].copy();normal[:,:2]*=-1
  me=bpy.data.meshes.new(row['name']);me.from_pydata(xyz.tolist(),[],[[f[0],f[2],f[1]] for f in faces]);me.update()
  for n in row['materials']:
   mat=bpy.data.materials.get(n) or bpy.data.materials.new(n);me.materials.append(mat)
  for f,si in zip(me.polygons,slots):f.material_index=si;f.use_smooth=True
  for layer,start in [('UVMap',6)]+([('UV2',8)] if hasuv2 else []):
   uv=me.uv_layers.new(name=layer)
   for loop in me.loops:uv.data[loop.index].uv=arr[loop.vertex_index,start:start+2]
  me.normals_split_custom_set_from_vertices(normal.tolist());obj=bpy.data.objects.new(row['name'],me);bpy.context.collection.objects.link(obj);obj.select_set(True);bpy.context.view_layer.objects.active=obj
  report.append(dict(asset=asset,name=row['name'],triangles=len(faces),submeshes=subs))
 bpy.ops.export_scene.fbx(filepath=str(U/asset),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE');print('CLEANED',Path(asset).stem,flush=True)
(H/'clean_models.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('COMPACT CLEANUP COMPLETE',len(groups),len(report),flush=True)
