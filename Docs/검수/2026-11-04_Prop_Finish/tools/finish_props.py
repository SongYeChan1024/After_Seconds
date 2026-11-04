"""소품의 로컬 좌표·UV를 유지한 베벨 및 각도 기반 스무스 준비. 작성자 송예찬."""
# 의사코드: Unity 원본을 읽기 → UV 루프를 보존하며 중복 위치 묶기 → 작은 베벨 평가
# → 형태·닫힌 면 검사 → 각도 기반 스무스와 Weighted Normal → 별도 결과 출력.
import bpy, bmesh, json, math, sys
from pathlib import Path
from mathutils import Vector

ROOT=Path(sys.argv[sys.argv.index('--')+1])
OUT=ROOT/'output'; OUT.mkdir(exist_ok=True)
REPO=ROOT.parents[1]
SOURCE=REPO/'SourceAssets'/'PropEdgeFinish';SOURCE.mkdir(parents=True,exist_ok=True)
filter_names=set(sys.argv[sys.argv.index('--')+2].split(',')) if len(sys.argv)>sys.argv.index('--')+2 else set()
if filter_names and (SOURCE/'PropEdgeFinish.blend').exists():bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'PropEdgeFinish.blend'))
else:bpy.ops.wm.read_factory_settings(use_empty=True)

def topology(mesh):
    bm=bmesh.new();bm.from_mesh(mesh)
    result={'boundaryEdges':sum(e.is_boundary for e in bm.edges),
            'overusedEdges':sum(len(e.link_faces)>2 for e in bm.edges),
            'zeroAreaFaces':sum(f.calc_area()==0 for f in bm.faces),
            'triangles':sum(len(f.verts)-2 for f in bm.faces)}
    bm.free();return result

def bounds(mesh):
    vv=mesh.vertices
    return [[min(v.co[i] for v in vv) for i in range(3)],[max(v.co[i] for v in vv) for i in range(3)]]

def export(mesh,data):
    mesh.calc_loop_triangles(); normals=mesh.corner_normals; uv=mesh.uv_layers.active
    vertices=[];nns=[];uvs=[];indices={};sub=[[] for _ in data['submeshes']]
    for tri in mesh.loop_triangles:
        for li in tri.loops:
            point=tuple(mesh.vertices[mesh.loops[li].vertex_index].co)
            normal=tuple(normals[li].vector)
            tex=tuple(uv.data[li].uv) if uv else (0.,0.)
            key=point+normal+tex
            if key not in indices:
                indices[key]=len(vertices);vertices.append(point);nns.append(normal);uvs.append(tex)
            sub[min(tri.material_index,len(sub)-1)].append(indices[key])
    return {'key':data['key'],'id':data['id'],'source':data['source'],'name':data['name'],
            'vertices':vertices,'normals':nns,'uv':uvs,'submeshes':sub}

records=json.loads((ROOT/'finish_manifest.json').read_text(encoding='utf-8')) if filter_names else []
if filter_names:records=[r for r in records if r['name'] not in filter_names]
for path in sorted((ROOT/'input').glob('*.json')):
    data=json.loads(path.read_text(encoding='utf-8-sig'))
    if filter_names and data['name'] not in filter_names:continue
    old=bpy.data.objects.get(data['id'])
    if old:bpy.data.objects.remove(old,do_unlink=True)
    name=data['name'];faces=[];mats=[]
    for slot,triangles in enumerate(data['submeshes']):
        for i in range(0,len(triangles),3):faces.append(triangles[i:i+3]);mats.append(slot)
    mesh=bpy.data.meshes.new(data['id']+'_OriginalUV');mesh.from_pydata(data['vertices'],[],faces);mesh.update()
    layer=mesh.uv_layers.new(name='UVMap')
    for poly,slot in zip(mesh.polygons,mats):
        poly.material_index=slot;poly.use_smooth=True
        for li in poly.loop_indices:
            vi=mesh.loops[li].vertex_index;layer.data[li].uv=data['uv'][vi] if data['uv'] else (0,0)
    for slot in range(len(data['submeshes'])):mesh.materials.append(bpy.data.materials.new(data['id']+'_Slot'+str(slot)))
    lo,hi=bounds(mesh);diagonal=(Vector(hi)-Vector(lo)).length
    bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=max(diagonal*1e-9,1e-12))
    bm.normal_update()
    sharp=sum(e.is_manifold and e.calc_face_angle()>math.radians(75) for e in bm.edges)
    bm.to_mesh(mesh);bm.free();mesh.update()
    before=topology(mesh)
    obj=bpy.data.objects.new(data['id'],mesh);bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active=obj;obj.select_set(True)
    native=name.startswith(('LivingDesk','MealTraySet','BedLinen','HygieneStation','TestMonitorStand'))
    extent=max(hi[i]-lo[i] for i in range(3))*data['metersPerLocalUnit']
    width_world=min(.004,max(.001,extent*.002));width=width_world/data['metersPerLocalUnit']
    bevel=None
    if not native and sharp:
        bevel=obj.modifiers.new('Bevel_2mm_to_4mm','BEVEL');bevel.width=width;bevel.segments=2
        bevel.limit_method='ANGLE';bevel.angle_limit=math.radians(75);bevel.use_clamp_overlap=True
        bevel.harden_normals=True
    accepted=False;attempts=[];final_mesh=None
    for attempt in range(3):
        bpy.context.view_layer.update();evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        candidate=bpy.data.meshes.new_from_object(evaluated)
        cleanup=bmesh.new();cleanup.from_mesh(candidate)
        bmesh.ops.remove_doubles(cleanup,verts=list(cleanup.verts),dist=max(diagonal*1e-10,1e-13))
        bmesh.ops.dissolve_degenerate(cleanup,dist=max(diagonal*1e-10,1e-13),edges=list(cleanup.edges))
        cleanup.to_mesh(candidate);cleanup.free();candidate.update()
        check=topology(candidate);attempts.append({'widthLocal':bevel.width if bevel else 0,**check})
        if check['boundaryEdges']==before['boundaryEdges'] and check['overusedEdges']==0 and check['zeroAreaFaces']==0 and check['triangles']<=before['triangles']*3.0+3000:
            final_mesh=candidate;accepted=True;break
        bpy.data.meshes.remove(candidate)
        if bevel:bevel.width*=.5;bevel.angle_limit=math.radians(80+attempt*4)
    weighted_edge_count=0
    if not accepted and bevel:
        # 복잡한 생성 메시에서는 서로 맞닿지 않는 긴 외곽 모서리만 선별해 충돌을 피한다.
        edge_bm=bmesh.new();edge_bm.from_mesh(mesh);edge_bm.edges.ensure_lookup_table();edge_bm.verts.ensure_lookup_table();edge_bm.normal_update()
        candidates=[e for e in edge_bm.edges if e.is_manifold and math.radians(75)<e.calc_face_angle()<math.radians(115) and e.calc_length()>width*5]
        candidates.sort(key=lambda e:e.calc_length(),reverse=True);chosen=set();used=set()
        for edge in candidates:
            vi={v.index for v in edge.verts}
            if not vi&used:chosen.add(edge.index);used|=vi
            if len(chosen)>=128:break
        edge_bm.free();attr=mesh.attributes.get('bevel_weight_edge') or mesh.attributes.new('bevel_weight_edge','FLOAT','EDGE')
        for i,value in enumerate(attr.data):value.value=1 if i in chosen else 0
        bevel.limit_method='WEIGHT';bevel.width=width*.5;weighted_edge_count=len(chosen)
        bpy.context.view_layer.update();candidate=bpy.data.meshes.new_from_object(obj.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        cleanup=bmesh.new();cleanup.from_mesh(candidate);bmesh.ops.remove_doubles(cleanup,verts=list(cleanup.verts),dist=max(diagonal*1e-10,1e-13));bmesh.ops.dissolve_degenerate(cleanup,dist=max(diagonal*1e-10,1e-13),edges=list(cleanup.edges));cleanup.to_mesh(candidate);cleanup.free();candidate.update()
        check=topology(candidate);attempts.append({'selectedIndependentEdges':weighted_edge_count,**check})
        if check['boundaryEdges']==before['boundaryEdges'] and check['overusedEdges']==0 and check['zeroAreaFaces']==0:
            final_mesh=candidate;accepted=True
        else:bpy.data.meshes.remove(candidate)
    if not accepted:
        if bevel:obj.modifiers.remove(bevel);bevel=None
        bpy.context.view_layer.update();final_mesh=bpy.data.meshes.new_from_object(obj.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    final_mesh.polygons.foreach_set('use_smooth',[True]*len(final_mesh.polygons))
    final_mesh.set_sharp_from_angle(angle=math.radians(60))
    temp=bpy.data.objects.new(data['id']+'_Normals',final_mesh);bpy.context.collection.objects.link(temp)
    obj.select_set(False);temp.select_set(True);bpy.context.view_layer.objects.active=temp
    weighted=temp.modifiers.new('WeightedNormals60','WEIGHTED_NORMAL');weighted.keep_sharp=True;weighted.weight=50
    bpy.ops.object.modifier_apply(modifier=weighted.name)
    final_mesh=temp.data;final_mesh.update()
    record={'key':data['key'],'id':data['id'],'source':data['source'],'name':name,
            'metersPerLocalUnit':data['metersPerLocalUnit'],'bevelApplied':bevel is not None,
            'bevelWidthMeters':bevel.width*data['metersPerLocalUnit'] if bevel else 0,
            'bevelSegments':2 if bevel else 0,'bevelAngleDegrees':math.degrees(bevel.angle_limit) if bevel else 0,'sharpEdgeCandidates':sharp,'smoothAngleDegrees':60,
            'selectedIndependentBevelEdges':weighted_edge_count if bevel else 0,
            'weightedNormals':True,'existingAuthoredBevelPreserved':native,'before':before,'after':topology(final_mesh),
            'boundsBefore':[lo,hi],'boundsAfter':bounds(final_mesh),'attempts':attempts,
            'reason':'Existing authored bevel retained; shading adjusted' if native else ('Selective sharp-edge bevel and smooth normals' if bevel else 'Smooth normals only; bevel unnecessary or unsafe')}
    (OUT/(data['id']+'.json')).write_text(json.dumps(export(final_mesh,data),separators=(',',':')),encoding='utf-8')
    records.append(record);(ROOT/'finish_manifest.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    bpy.data.objects.remove(temp,do_unlink=True);obj.hide_set(True)
    print('PROP_FINISHED',name,record['bevelApplied'],before['triangles'],record['after']['triangles'],flush=True)
for o in bpy.data.objects:
    if 'LaboratoryWorkbench' in o.name:o.hide_set(False);bpy.context.view_layer.objects.active=o
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'PropEdgeFinish.blend'))
print('ALL_PROPS_DONE',len(records),flush=True)
