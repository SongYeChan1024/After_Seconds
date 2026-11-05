"""CCTV 회전부 간섭 검수 V0.01 · 송예찬. 원본 수정 없음.
의사코드: 베벨 평가 형상 -> Unity 좌표에서 Y/X 검수 각도 적용 -> 헤드와 지지물 삼각형 교차 검사.
"""
import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
root=Path(__file__).parent/'CCTV';bpy.ops.wm.open_mainfile(filepath=str(root/'CCTV_SecurityCamera_Articulated.blend'))
deps=bpy.context.evaluated_depsgraph_get();parts=[]
for ob in bpy.context.scene.objects:
    if ob.type!='MESH':continue
    ev=ob.evaluated_get(deps);me=ev.to_mesh();vv=[ob.matrix_world@v.co for v in me.vertices];verts=[Vector((-v.x,v.z,-v.y)) for v in vv];faces=[tuple(p.vertices) for p in me.polygons];ev.to_mesh_clear();parts.append((ob.name,ob.get('rotation_part'),verts,faces))
pan=Vector((0,-.16,0));head=Vector((0,-.46,.035));out=[]
for yaw,tilt in [(0,10),(-90,10),(90,10),(0,-25),(0,25),(-90,-25),(90,25)]:
    ry=Matrix.Rotation(math.radians(yaw),3,'Y');rx=Matrix.Rotation(math.radians(tilt),3,'X');bvh=[];max_head_y=-999
    for name,part,verts,faces in parts:
        if part=='Head':vv=[pan+ry@(head-pan+rx@(v-head)) for v in verts];max_head_y=max(max_head_y,max(v.y for v in vv))
        elif part=='Pan':vv=[pan+ry@(v-pan) for v in verts]
        else:vv=verts
        bvh.append((name,part,BVHTree.FromPolygons(vv,faces,all_triangles=False,epsilon=.000001)))
    collisions=[]
    for name,part,a in bvh:
        if part!='Head':continue
        for other,other_part,b in bvh:
            if other_part=='Head' or other.startswith('Tilt_Axle'):continue # deliberate rotating axle contact
            hits=a.overlap(b)
            if hits:collisions.append({'head':name,'support':other,'intersectingTrianglePairs':len(hits)})
    out.append({'yaw':yaw,'tilt':tilt,'ceilingClearance':-max_head_y,'collisions':collisions})
result={'title':'CCTV Rotation Clearance V0.01','author':'송예찬','method':'Evaluated bevel meshes, triangle BVH overlap; intentional axle contact excluded; finite sampled angles, not continuous collision proof','states':out}
(root/'clearance_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
