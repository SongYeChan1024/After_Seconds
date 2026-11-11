from pathlib import Path
import bpy,numpy as np,json,struct,collections
H=Path(__file__).resolve().parent;R=H.parents[1];U=R/'Unity/After_Seconds_Build_V0.01';plan=json.loads((H/'local_plans/B1_SharedMeshes.json').read_text());groups=collections.defaultdict(list)
for p in plan['patches']:groups[p['renderer']].append(p)
manifest=[]
for ri,patches in groups.items():
 row=plan['rows'][ri];bpy.ops.wm.read_factory_settings(use_empty=True)
 with (U/'Temp/B1Review'/f"{row['mesh']}.bin").open('rb') as f:
  n,subs,hasuv2=struct.unpack('<iii',f.read(12));stride=10 if hasuv2 else 8;data=np.frombuffer(f.read(n*stride*4),'<f4').reshape(n,stride).copy();indices=[]
  for s in range(subs):count=struct.unpack('<i',f.read(4))[0];indices.append(np.frombuffer(f.read(count*4),'<i4').reshape(-1,3).copy())
 vs=data.tolist();faces=[];slots=[]
 for si,ix in enumerate(indices):
  patch=next((p for p in patches if p['submesh']==si),None);edits={p['triangle']:p['bary'] for p in patch['edits']} if patch else {}
  for ti,ids in enumerate(ix):
   if ti not in edits:faces.append(ids.tolist());slots.append(si);continue
   for bary in edits[ti]:
    face=[]
    for weights in bary:
     k=next((i for i,x in enumerate(weights) if abs(x-1)<1e-10),None)
     if k is not None:face.append(int(ids[k]));continue
     d=np.array(weights)@data[ids];norm=np.linalg.norm(d[3:6]);d[3:6]/=max(norm,1e-20);face.append(len(vs));vs.append(d.tolist())
    p=np.array([vs[i][:3] for i in face]);area=np.linalg.norm(np.cross(p[1]-p[0],p[2]-p[0]))
    if area>1e-9:faces.append(face);slots.append(si)
 arr=np.array(vs);xyz=arr[:,[0,2,1]].copy();xyz[:,:2]*=-1;normal=arr[:,[3,5,4]].copy();normal[:,:2]*=-1
 name='BL_Clean_'+row['meshName'].replace(' ','_')+'_'+row['mesh'][:6];me=bpy.data.meshes.new(name);me.from_pydata(xyz.tolist(),[],[[f[0],f[2],f[1]] for f in faces]);me.update()
 for si in range(subs):me.materials.append(bpy.data.materials.new(f'Slot_{si:03}'))
 for p,si in zip(me.polygons,slots):p.material_index=si;p.use_smooth=True
 for layer,start in [('UVMap',6)]+([('UV2',8)] if hasuv2 else []):
  uv=me.uv_layers.new(name=layer)
  for loop in me.loops:uv.data[loop.index].uv=arr[loop.vertex_index,start:start+2]
 me.normals_split_custom_set_from_vertices(normal.tolist());obj=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(obj);obj.select_set(True);bpy.context.view_layer.objects.active=obj
 category='Props' if '/Props/' in row['asset'] else 'Environment';path=U/'Assets/Afrer_Seconds/05.Model'/category/'B1'/f'{name}.fbx';bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE')
 manifest.append(dict(sourceMesh=row['mesh'],source=row['asset'],sourceName=row['meshName'],asset=path.relative_to(U).as_posix(),triangles=len(faces),submeshes=subs));print('CLEANED',name,len(faces),flush=True)
(H/'clean_models.json').write_text(json.dumps(manifest,indent=2));print('COMPACT CLEANUP COMPLETE',len(manifest),flush=True)
