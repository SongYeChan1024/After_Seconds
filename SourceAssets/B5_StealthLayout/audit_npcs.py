"""경비·연구원 메시/웨이트 정적 검수 V0.01 · 송예찬. 읽기 전용 검수.
의사코드: 원본 blend 열기 -> 표면/UV/노멀/웨이트 검사 -> UV 분리 정점 용접 사본의 위상 검사 -> JSON.
"""
import bpy,bmesh,json,math
from pathlib import Path
root=Path(__file__).parent/'NPC';out=[]
for role in ('Guard','Researcher'):
    bpy.ops.wm.open_mainfile(filepath=str(root/f'AS_V03_{role}.blend'))
    arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
    ob=next(o for o in bpy.context.scene.objects if o.type=='MESH' and any(m.type=='ARMATURE' for m in o.modifiers))
    me=ob.data;bonegroups={g.index:g.name for g in ob.vertex_groups if g.name in arm.data.bones};weights=[];unweighted=[];nonnormal=[];bad=[]
    for v in me.vertices:
        ws=[g.weight for g in v.groups if g.group in bonegroups and g.weight>.000001];weights.append(len(ws));s=sum(ws)
        if not ws:unweighted.append(v.index)
        if abs(s-1)>.001:nonnormal.append({'vertex':v.index,'sum':s})
        if not all(math.isfinite(x) for x in v.co):bad.append(v.index)
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bm.normal_update()
    boundaries=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold and not e.is_boundary for e in bm.edges);loose=sum(not v.link_faces for v in bm.verts);degenerate=sum(f.calc_area()<1e-12 for f in bm.faces)
    seen=set();duplicates=0
    for f in bm.faces:
        key=tuple(sorted(v.index for v in f.verts))
        if key in seen:duplicates+=1
        seen.add(key)
    bm.free();uv=me.uv_layers.active;bad_uv=sum(not all(math.isfinite(t) for t in x.uv) for x in uv.data) if uv else len(me.loops)
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());evaluated=ev.to_mesh();tri=sum(len(p.vertices)-2 for p in evaluated.polygons);ev.to_mesh_clear()
    out.append({'role':role,'source':str(root/f'AS_V03_{role}.blend'),'vertices':len(me.vertices),'sourceTriangles':sum(len(p.vertices)-2 for p in me.polygons),'evaluatedTriangles':tri,'bones':len(arm.data.bones),'weightedBoneGroups':len(bonegroups),'maxInfluences':max(weights),'unweightedVertices':len(unweighted),'weightSumsOutsideTolerance':len(nonnormal),'weightExamples':nonnormal[:8],'nonFinitePositions':len(bad),'UVLayers':len(me.uv_layers),'invalidUVLoops':bad_uv,'topologyAfterTemporarySeamWeld':{'boundaryEdges':boundaries,'nonManifoldNonBoundaryEdges':nonmanifold,'looseVertices':loose,'degenerateFaces':degenerate,'duplicateFaces':duplicates},'note':'Open boundaries may be intentional clothing/detail; this audit does not alter source or prove animation quality.'})
(root/'mesh_audit.json').write_text(json.dumps({'title':'Enemy Mesh Audit V0.01','author':'송예찬','models':out},ensure_ascii=False,indent=2),encoding='utf-8')
print('NPC_AUDIT_RESULT',json.dumps(out,ensure_ascii=False))
