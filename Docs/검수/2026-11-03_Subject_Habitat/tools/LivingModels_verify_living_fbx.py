# [의사코드] 저장 FBX를 새 세션에서 열고 치수·닫힌 메시·면적을 원본과 대조한다.
# [코딩]
import bpy,bmesh,json,pathlib,hashlib,math
from mathutils import Vector
w=pathlib.Path(__file__).parent;manifest=json.loads((w/'manifest.json').read_text(encoding='utf8'));out=[]
for a in manifest:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=a['fbx'],use_custom_normals=True)
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];ps=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
 lo=[min(p[i] for p in ps) for i in range(3)];hi=[max(p[i] for p in ps) for i in range(3)];facts=[]
 for o in meshes:
  bm=bmesh.new();bm.from_mesh(o.data)
  # FBX may split vertices at hard normals. Weld only identical spatial seam duplicates for this topology audit.
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0000002)
  facts.append({'mesh':o.name,'triangles':sum(len(p.verts)-2 for p in bm.faces),'boundaryEdges':sum(e.is_boundary for e in bm.edges),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'zeroAreaFaces':sum(f.calc_area()<1e-12 for f in bm.faces),'finiteVertices':all(math.isfinite(float(v.co[i])) for v in bm.verts for i in range(3))});bm.free()
 size=[hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]]
 dimension=max(abs(size[i]-a['unitySizeXYZ'][i]) for i in range(3))<.0001
 accepted=dimension and all(f['boundaryEdges']==f['nonManifoldEdges']==f['zeroAreaFaces']==0 and f['finiteVertices'] for f in facts)
 marker=next((o.name for o in bpy.context.scene.objects if o.name.startswith('HM_FrontMarker')),None);a['frontMarker']=marker
 out.append({'name':a['name'],'accepted':accepted,'fbxSha256':hashlib.sha256(pathlib.Path(a['fbx']).read_bytes()).hexdigest(),'unitySizeXYZ':size,'meshes':facts,'frontMarkerFound':marker is not None})
(w/'fbx_verification.json').write_text(json.dumps(out,indent=2),encoding='utf8');assert all(x['accepted'] for x in out),out
(w/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print(json.dumps(out,indent=2))
# [주석] 제조 부품끼리 연결되는 의도적 접합은 면 관통 검사 대상이 아니다.
