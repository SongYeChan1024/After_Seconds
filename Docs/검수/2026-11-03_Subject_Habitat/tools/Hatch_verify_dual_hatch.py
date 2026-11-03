"""작성자 송예찬. [의사코드] 저장 FBX를 다시 열어 토폴로지·문 중심·실제 관통을 검사한다."""
# [코딩]
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent
manifest=json.loads((HERE/'manifest.json').read_text(encoding='utf8'))
results={}
for key,path in manifest['exports'].items():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=path)
 objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];records=[]
 for o in objects:
  bm=bmesh.new();bm.from_mesh(o.data)
  rec={'name':o.name,'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'boundaryEdges':sum(e.is_boundary for e in bm.edges),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'zeroAreaFaces':sum(f.calc_area()<1e-11 for f in bm.faces),'pivotBlender':list(o.matrix_world.translation),'materials':[m.name.split('.')[0] for m in o.data.materials]}
  bm.free();records.append(rec)
  assert rec['boundaryEdges']==rec['nonManifoldEdges']==rec['zeroAreaFaces']==0,rec
 expected=24 if key=='shellCollision' else 6 if key=='hatchCollision' else 3 if key=='hatchVisual' else None
 if expected is not None:assert len(records)==expected,(key,len(records))
 # 관통 단면의 9개 점을 짧은 전후 광선으로 검사한다. 닫힌 문은 별도 제외한다.
 hits=[]
 if key in ('shellVisual','shellCollision','hatchVisual','hatchCollision'):
  for o in objects:
   if 'Door' in o.name:continue
   mesh=o.data;verts=[o.matrix_world@v.co for v in mesh.vertices];faces=[tuple(p.vertices) for p in mesh.polygons];tree=BVHTree.FromPolygons(verts,faces)
   for x in [-.10,0,.10]:
    for z in [.43,.525,.62]:
     h=tree.ray_cast(Vector((x,-1.50,z)),Vector((0,1,0)),.35)
     if h[0] is not None:hits.append({'object':o.name,'x':x,'z':z,'distance':h[3]})
 assert not hits,(key,hits)
 results[key]={'file':path,'sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),'meshCount':len(records),'triangles':sum(x['triangles'] for x in records),'meshes':records,'passageRayHitsWithDoorsExcluded':hits,'accepted':True}

# 양면 문들은 단순 충돌 상자와 회전 중심 좌표가 일치한다.
for info in manifest['doorPivots']:
 visual=next(x for x in results['hatchVisual']['meshes'] if x['name']==info['name'])
 collider=next(x for x in results['hatchCollision']['meshes'] if x['name']==info['name'].replace('_Pivot','_Collider'))
 for p in [visual['pivotBlender'],collider['pivotBlender']]:assert max(abs(a-b) for a,b in zip(p,info['sourcePivot']))<1e-5,(info,p)
(HERE/'fbx_roundtrip_verification.json').write_text(json.dumps({'accepted':True,'files':results,'passageRaySamplesPerFile':9,'note':'Door leaves exported closed; tunnel and shell remain unblocked when door meshes are excluded.'},ensure_ascii=False,indent=2),encoding='utf8')
print('ROUNDTRIP_ACCEPTED',json.dumps({k:{'meshes':v['meshCount'],'triangles':v['triangles']} for k,v in results.items()}),flush=True)
# [주석] 이 검사는 저장된 기하와 피벗 검수다. 실제 게임 배식/개폐 기능을 뜻하지 않는다.
