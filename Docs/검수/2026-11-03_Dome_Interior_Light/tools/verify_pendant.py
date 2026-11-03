# 작성자 송예찬 / 2026-11-03
# [의사코드] 최종 FBX를 새 세션에서 열고 실제 크기·위쪽 고정점·아래쪽 조명 앵커와 닫힌 표면을 대조한다.
# [코딩]
import bpy,bmesh,pathlib,json,math,hashlib
from mathutils import Vector
w=pathlib.Path(__file__).parent;a=json.loads((w/'manifest.json').read_text(encoding='utf8'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=a['fbx'],use_custom_normals=True)
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];facts=[];points=[]
for o in meshes:
 points += [o.matrix_world@Vector(v) for v in o.bound_box]
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=2e-7)
 facts.append({'name':o.name,'triangles':sum(len(f.verts)-2 for f in bm.faces),'boundaryEdges':sum(e.is_boundary for e in bm.edges),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'zeroAreaFaces':sum(f.calc_area()<1e-12 for f in bm.faces),'finiteVertices':all(math.isfinite(float(v.co[i])) for v in bm.verts for i in range(3)),'materials':[m.name for m in o.data.materials]});bm.free()
lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)];size=[hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]]
anchors={}
for key in ['DP_TopMountAnchor','DP_DownwardLightAnchor']:
 o=bpy.data.objects.get(key);assert o is not None,key;p=o.matrix_world.translation;anchors[key]=[p.x,p.z,-p.y]
accepted=len(meshes)==1 and max(abs(size[i]-a['unitySizeXYZ'][i]) for i in range(3))<.0001 and all(f['boundaryEdges']==f['nonManifoldEdges']==f['zeroAreaFaces']==0 and f['finiteVertices'] for f in facts)
out={'name':a['name'],'accepted':accepted,'sha256':hashlib.sha256(pathlib.Path(a['fbx']).read_bytes()).hexdigest(),'unitySizeXYZ':size,'anchorUnityPositions':anchors,'meshes':facts}
(w/'fbx_verification.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out,indent=2));assert accepted,out
# [주석] 여러 제조 부품의 정상 접합은 의도된 구조다. 원점은 바닥이 아니라 윗 고정부 중앙이다.
