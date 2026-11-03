"""[의사코드] 최종 FBX를 새 Blender 세션에 다시 읽어 실제 내보낸 메시를 검증한다."""
# [코딩]
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
folder=Path(__file__).resolve().parent
results=[]
for filename,expected in [('ObservationPod_Visual.fbx',None),('ObservationPod_Collision.fbx',24)]:
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.fbx(filepath=str(folder/filename),use_anim=False)
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    points=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
    mn=[min(p[k] for p in points) for k in range(3)];mx=[max(p[k] for p in points) for k in range(3)]
    report={'file':filename,'meshCount':len(objects),'blenderBoundsMin':mn,'blenderBoundsMax':mx,'dimensionsXYZ':[mx[k]-mn[k] for k in range(3)],'objects':[]}
    for obj in objects:
        bm=bmesh.new();bm.from_mesh(obj.data)
        row={'name':obj.name,'boundaryEdges':sum(e.is_boundary for e in bm.edges),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'zeroAreaFaces':sum(f.calc_area()<1e-11 for f in bm.faces),'triangles':sum(len(f.verts)-2 for f in bm.faces),'materials':[m.name for m in obj.data.materials if m]}
        bm.free();report['objects'].append(row)
        assert not row['boundaryEdges'] and not row['nonManifoldEdges'] and not row['zeroAreaFaces'],row
    if expected:assert len(objects)==expected
    assert all(math.isfinite(n) for n in mn+mx)
    assert abs(report['dimensionsXYZ'][0]-(2.8 if expected else 2.81))<.002
    assert abs(report['dimensionsXYZ'][2]-(3.19 if expected else 3.221))<.002
    results.append(report)
(folder/'fbx_roundtrip_verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print('ROUNDTRIP_OK',[(r['file'],r['meshCount'],r['dimensionsXYZ']) for r in results],flush=True)
# [주석] 반입 검증용 새 세션이며 실제 Unity Assets와 씬에는 접근하지 않는다.
