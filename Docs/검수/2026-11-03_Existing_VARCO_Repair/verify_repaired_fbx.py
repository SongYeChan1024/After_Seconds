import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector, geometry
from mathutils.bvhtree import BVHTree
R=Path(__file__).parent;report=[]
stage='retopo' if '--retopo' in sys.argv else 'optimized'
for item in json.loads((R/'repair_export_manifest.json').read_text(encoding='utf-8-sig')):
    floor=item['name']
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.fbx(filepath=str(R.parent.parent/'Unity/After_Seconds_Build_V0.01'/item['repairedModelPath']),use_image_search=False)
    entry={'floor':floor,'objects':[]}
    for obj in [o for o in bpy.context.scene.objects if o.type=='MESH']:
        mesh=obj.data;bm=bmesh.new();bm.from_mesh(mesh)
        coords=[v.co for v in bm.verts];lo=Vector(tuple(min(p[i] for p in coords) for i in range(3)));hi=Vector(tuple(max(p[i] for p in coords) for i in range(3)));diag=(hi-lo).length
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=diag*1e-7)
        bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.faces.index_update();bm.faces.ensure_lookup_table()
        tree=BVHTree.FromBMesh(bm);crossings=[];candidates=0;selected=set();eps=diag*1e-6
        for i,j in tree.overlap(tree):
            if i>=j:continue
            a,b=bm.faces[i],bm.faces[j]
            if set(a.verts).intersection(b.verts):continue
            candidates+=1;found=False
            for src,dst in [(a,b),(b,a)]:
                tri=[v.co for v in dst.verts]
                for edge in src.edges:
                    p,q=[v.co for v in edge.verts];d=q-p
                    if d.length<=eps:continue
                    hit=geometry.intersect_ray_tri(*tri,d.normalized(),p,True)
                    if hit is not None and eps<(hit-p).dot(d.normalized())<d.length-eps:
                        # Edge/vertex touches are not strict interior crossings.
                        areas=[(tri[(k+1)%3]-tri[k]).cross(hit-tri[k]).length for k in range(3)]
                        if min(areas)>eps*eps:
                            found=True;break
                if found:break
            if found:
                selected.update(v.index for f in (a,b) for v in f.verts)
                center=sum((v.co for f in (a,b) for v in f.verts),Vector())/6
                crossings.append({'faces':[i,j],'center':list(center)})
        uv_count=len(mesh.uv_layers);uv_bad=sum(not all(math.isfinite(v) for v in d.uv) for layer in mesh.uv_layers for d in layer.data)
        entry['objects'].append({'verticesAfterWeld':len(bm.verts),'triangles':len(bm.faces),'boundaryEdges':sum(e.is_boundary for e in bm.edges),'overusedEdges':sum(len(e.link_faces)>2 for e in bm.edges),'zeroAreaFaces':sum(f.calc_area()<=eps*eps*1e-4 for f in bm.faces),'uvLayers':uv_count,'nonFiniteUVs':uv_bad,'materialSlots':len(mesh.materials),'bvhCandidatePairs':candidates,'strictEdgeTriangleCrossings':len(crossings),'crossingLocations':crossings[:100],'limitation':'Sampled edge-triangle intersection test; coplanar overlaps and all possible edge contacts are not exhaustively resolved.'})
        bm.free()
    report.append(entry)
(R/('retopology_verification.json' if stage=='retopo' else 'export_verification.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report),flush=True)
