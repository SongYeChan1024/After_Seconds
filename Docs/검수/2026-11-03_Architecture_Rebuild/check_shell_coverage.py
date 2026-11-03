import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).parent;P=R.parent.parent/'Unity/After_Seconds_Build_V0.01';report=[]
for a in json.loads((R/'rebuild_manifest.json').read_text()):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.fbx(filepath=str(P/a['modelPath']),use_image_search=False)
 obj=next(o for o in bpy.context.scene.objects if o.type=='MESH' and 'Opaque' in o.name);bm=bmesh.new();bm.from_mesh(obj.data);bm.transform(obj.matrix_world);bmesh.ops.triangulate(bm,faces=list(bm.faces));tree=BVHTree.FromBMesh(bm);holes=[];opening_blocked=[];samples=0;opening=0
 horizontal='Floor' in a['name'] or 'Ceiling' in a['name'];w=a['sizeUnity'][0];h=a['sizeUnity'][2] if horizontal else a['sizeUnity'][1]
 for i in range(41):
  for j in range(41):
   x=-w/2+.0001+(w-.0002)*i/40;z=(-h/2+.0001 if horizontal else .0001)+(h-.0002)*j/40
   origin=Vector((x,z,-1)) if horizontal else Vector((x,-1,z));direction=Vector((0,0,1)) if horizontal else Vector((0,1,0));hit=tree.ray_cast(origin,direction,2)[0];expected_open=a['name']=='Env_ObservationWall_4m' and abs(x)<1.3 and 1.25<z<2.9
   if expected_open:
    opening+=1
    if hit is not None:opening_blocked.append([x,z])
   else:
    samples+=1
    if hit is None:holes.append([x,z])
 report.append({'name':a['name'],'opaqueShellSamples':samples,'unintendedPassThroughRays':len(holes),'windowOpeningSamples':opening,'unexpectedOpaqueWindowHits':len(opening_blocked),'failedLocations':holes[:20]+opening_blocked[:20]});bm.free()
(R/'shell_coverage.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report),flush=True)

