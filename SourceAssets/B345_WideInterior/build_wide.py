"""Derived architecture: widen corridors, remove old corridor luminaires, retain bevels/UVs."""
import bpy,bmesh,json,sys,math
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
SRC=Path(__file__).resolve().parent;sys.path.insert(0,str(SRC));from wide_plan import fx,fy
REPO=SRC.parents[1];ENV=REPO/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment'
plans=json.loads((SRC/'layout_before.json').read_text(encoding='utf-8-sig'))['floors']
final_plans=json.loads((REPO/'Docs/도면/잠입_탐색/layout.json').read_text(encoding='utf-8-sig'))['floors']
def warp(p,core):return Vector((24-fx(24-p.x),16-fy(16-p.y,core),p.z))
def build(floor,kind):
 path=REPO/(f'SourceAssets/B345_WallSurfaces/WS_{floor}_Walls.blend' if kind=='Walls' else 'SourceAssets/B345_Dressing/SD_B3_Architecture.blend' if floor=='B3' else f'SourceAssets/LevelContinuation/LC_{floor}_Architecture.blend')
 if kind=='Details':path=REPO/'SourceAssets/B4_StealthLayout/B4_ServiceDetails.blend'
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.preferences.filepaths.save_version=0
 rooms=next(f for f in plans if f['floor']==floor)['rooms'];corridors=[r for r in rooms if r['kind']=='corridor'];domes={r['id'] for r in next(f for f in final_plans if f['floor']==floor)['rooms'] if r.get('roof',{}).get('kind')=='dome'}
 removed=[];keys={};sources=[]
 states=[(ob,24-ob.location.x,16-ob.location.y,ob.matrix_world.copy()) for ob in bpy.context.scene.objects if ob.type=='MESH']
 for ob,u,v,old in states:
  room=next((r for r in rooms if r['x']<u<r['x']+r['w'] and r['y']<v<r['y']+r['h']),None)
  remove_screen=ob.name.startswith(('CorridorScreen','CorridorBaffle'))
  remove_dome_old=kind=='Architecture' and room and room['id'] in domes and ob.name.startswith(('Ceiling_','LightBody','LightLens'))
  if remove_screen or remove_dome_old:
   removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True);continue
  if kind=='Architecture' and ob.name.startswith(('LightBody','LightLens')) and any(r['x']-.01<=u<=r['x']+r['w']+.01 and r['y']-.01<=v<=r['y']+r['h']+.01 for r in corridors):
   removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True);continue
  keys[ob.name]=(ob.data.materials[0].name,int(max(0,min(47.9,u))//8),int(max(0,min(31.9,v))//8)) if kind!='Details' else (ob.data.materials[0].name,0,0)
  core=u>=38.99;new=old.copy();new.translation=warp(old.translation,core);inv=new.inverted();ob.data=ob.data.copy()
  for vertex in ob.data.vertices:vertex.co=inv@warp(old@vertex.co,core)
  ob.matrix_world=new;ob['wide_source']=str(path.relative_to(REPO));ob['wide_core_rigid']=core;sources.append(ob)
 bpy.context.view_layer.update()
 for im in bpy.data.images:
  if im.source=='FILE' and im.has_data and not im.packed_file:im.pack()
 bpy.ops.wm.save_as_mainfile(filepath=str(SRC/f'WC_{floor}_{kind}.blend'))
 dep=bpy.context.evaluated_depsgraph_get();col=bpy.data.collections.new('Wide_Export');bpy.context.scene.collection.children.link(col);batches=defaultdict(list)
 evaluated=[(ob,bpy.data.meshes.new_from_object(ob.evaluated_get(dep),depsgraph=dep),ob.matrix_world.copy()) for ob in sources]
 for ob,me,matrix in evaluated:
  n=bpy.data.objects.new('Export',me);col.objects.link(n);n.matrix_world=matrix;batches[keys[ob.name]].append(n)
 result=[]
 for (mat,x,z),obs in batches.items():
  bpy.ops.object.select_all(action='DESELECT')
  for ob in obs:ob.select_set(True)
  bpy.context.view_layer.objects.active=obs[0]
  if len(obs)>1:bpy.ops.object.join()
  ob=bpy.context.object;ob.name=f'{"WS" if kind=="Walls" else "LC"}_{floor}_{mat}_{x}_{z}' if kind!='Details' else 'B4_Detail_'+mat.split('_')[-1]+'_All';bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();result.append(ob)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in result:ob.select_set(True)
 bpy.context.view_layer.objects.active=result[0]
 bpy.ops.export_scene.fbx(filepath=str(ENV/floor/f'WC_{floor}_{kind}.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,use_mesh_modifiers=True,bake_anim=False,mesh_smooth_type='FACE')
 row=dict(floor=floor,kind=kind,removedFixtures=removed,sources=len(sources),meshes=len(result),triangles=sum(len(o.data.polygons) for o in result))
 (SRC/f'{floor}_{kind}.json').write_text(json.dumps(row,indent=2),encoding='utf-8');print('WIDE_DONE',row,flush=True)
if __name__=='__main__':
 if '--details' in sys.argv:build('B4','Details')
 else:
  for floor in (sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ('B5','B4','B3')):
   for kind in ('Architecture','Walls'):build(floor,kind)
