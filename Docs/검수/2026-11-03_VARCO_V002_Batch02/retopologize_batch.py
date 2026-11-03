import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector,geometry
from mathutils.bvhtree import BVHTree
R=Path(__file__).parent
floors=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [a['id'] for a in json.loads((R/'batch_manifest.json').read_text(encoding='utf-8-sig'))['assets']]

def crossings(bm,eps):
    bm.faces.index_update();bm.faces.ensure_lookup_table();tree=BVHTree.FromBMesh(bm);pairs=[]
    for i,j in tree.overlap(tree):
        if i>=j:continue
        a,b=bm.faces[i],bm.faces[j]
        if set(a.verts)&set(b.verts):continue
        found=False
        for src,dst in [(a,b),(b,a)]:
            tri=[v.co for v in dst.verts]
            for edge in src.edges:
                p,q=[v.co for v in edge.verts];d=q-p
                if d.length<=eps:continue
                hit=geometry.intersect_ray_tri(*tri,d.normalized(),p,True)
                if hit is not None and eps<(hit-p).dot(d.normalized())<d.length-eps:
                    areas=[(tri[(k+1)%3]-tri[k]).cross(hit-tri[k]).length for k in range(3)]
                    if min(areas)>eps*eps:found=True;break
            if found:break
        if found:pairs.append((a,b))
    return pairs

report=json.loads((R/'local_retopology_report.json').read_text(encoding='utf-8')) if (R/'local_retopology_report.json').exists() else []
for floor in floors:
    bpy.ops.wm.open_mainfile(filepath=str(R/f'{floor}_optimized.blend'))
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];entry={'floor':floor,'method':'Local intersection patches removed and retriangulated; nearest-source UV interpolation; surrounding original topology preserved','objects':[]}
    for obj in objects:
        bpy.context.view_layer.objects.active=obj
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8)
        bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        source=bm.copy();source.faces.index_update();source.faces.ensure_lookup_table();source_tree=BVHTree.FromBMesh(source);srcuv=source.loops.layers.uv.active;uv=bm.loops.layers.uv.active
        lo=Vector(tuple(min(v.co[i] for v in bm.verts) for i in range(3)));hi=Vector(tuple(max(v.co[i] for v in bm.verts) for i in range(3)));diag=(hi-lo).length;eps=diag*1e-6
        initial_volume=bm.calc_volume(signed=False);before_cross=len(crossings(bm,eps));steps=[]
        patch_layer=bm.faces.layers.int.new('RetopoPatch')
        for iteration in range(16):
            pairs=crossings(bm,eps)
            junction_edges=[e for e in bm.edges if len(e.link_faces)>2]
            if not pairs and not junction_edges:break
            bad={f for pair in pairs for f in pair}|{f for e in junction_edges for f in e.link_faces}
            for ring in range(1+iteration//3):
                bad|={n for f in list(bad) for e in f.edges for n in e.link_faces}
            # Grow touching patches until their boundary is a set of simple
            # loops; a branching boundary cannot be safely capped.
            for _ in range(20):
                border={e for f in bad for e in f.edges if sum(n in bad for n in e.link_faces)==1}
                degree={}
                for e in border:
                    for v in e.verts:degree[v]=degree.get(v,0)+1
                junctions=[v for v,d in degree.items() if d!=2]
                if not junctions:break
                bad|={f for v in junctions for f in v.link_faces}
            if len(bad)>max(1500,len(bm.faces)*.25):
                print('PATCH_GROWTH_LIMIT',floor,flush=True);break
            count=len(bad);bmesh.ops.delete(bm,geom=list(bad),context='FACES_ONLY')
            wires=[e for e in bm.edges if not e.link_faces]
            if wires:bmesh.ops.delete(bm,geom=wires,context='EDGES')
            loose=[v for v in bm.verts if not v.link_edges]
            if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
            boundary={e for e in bm.edges if e.is_boundary};filled=[]
            while boundary:
                edge=next(iter(boundary));start=edge.verts[0];v=edge.verts[1]
                loop=[start];boundary.remove(edge)
                for _ in range(20000):
                    if v==start:break
                    loop.append(v);nexts=[e for e in v.link_edges if e in boundary]
                    if len(nexts)!=1:raise RuntimeError('Boundary is not a simple loop')
                    e=nexts[0];boundary.remove(e);v=e.other_vert(v)
                existing=next((f for f in loop[0].link_faces if set(f.verts)==set(loop)),None)
                if existing:
                    bmesh.ops.delete(bm,geom=[existing],context='FACES_ONLY')
                elif len(loop)>=3:filled.append(bm.faces.new(loop))
            result=bmesh.ops.triangulate(bm,faces=filled,quad_method='BEAUTY',ngon_method='BEAUTY')
            newfaces=result['faces']
            for f in newfaces:f[patch_layer]=1
            # A new triangulation diagonal can coincide with an existing edge
            # elsewhere on a folded surface. Give the patch its own midpoint
            # rather than joining four faces onto that old edge.
            split_count=0
            for edge in list(bm.edges):
                if not edge.is_valid or len(edge.link_faces)!=4:continue
                fs=[f for f in edge.link_faces if f[patch_layer]]
                if len(fs)<2:continue
                fs=fs[:2];a,b=edge.verts
                midpoint=bm.verts.new((a.co+b.co)*.5)
                n=sum((f.normal for f in fs),Vector())
                if n.length:midpoint.co+=n.normalized()*eps*.25
                thirds=[next(v for v in f.verts if v not in edge.verts) for f in fs]
                bmesh.ops.delete(bm,geom=fs,context='FACES_ONLY')
                for c in thirds:
                    for vertices in [(a,midpoint,c),(midpoint,b,c)]:
                        existing=next((face for face in vertices[0].link_faces if set(face.verts)==set(vertices)),None)
                        if existing is None:
                            f=bm.faces.new(vertices);f[patch_layer]=1;newfaces.append(f)
                split_count+=1
            for face in newfaces:
                if not face.is_valid:continue
                for loop in face.loops:
                    hit,normal,index,distance=source_tree.find_nearest(loop.vert.co)
                    src=source.faces[index];sl=list(src.loops)
                    value=geometry.barycentric_transform(hit,*(l.vert.co for l in sl),*(Vector((l[srcuv].uv.x,l[srcuv].uv.y,0)) for l in sl))
                    loop[uv].uv=value.xy
            bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
            steps.append({'iteration':iteration,'crossingPairs':len(pairs),'junctionEdges':len(junction_edges),'removedFaces':count,'splitPatchDiagonals':split_count,'rebuiltTriangles':sum(f.is_valid for f in newfaces),'remainingCrossings':len(crossings(bm,eps))})
            print('PATCH',floor,steps[-1],flush=True)
        remaining=crossings(bm,eps);boundary=sum(e.is_boundary for e in bm.edges);overused=sum(len(e.link_faces)>2 for e in bm.edges)
        volume=bm.calc_volume(signed=False);volchange=abs(volume-initial_volume)/initial_volume
        record={'initialCrossings':before_cross,'remainingCrossings':len(remaining),'boundaryEdges':boundary,'overusedEdges':overused,'triangles':len(bm.faces),'vertices':len(bm.verts),'relativeVolumeChange':volchange,'steps':steps}
        entry['objects'].append(record)
        if remaining or boundary or overused or volchange>.03:
            entry['accepted']=False;print('PATCH_REJECTED',floor,json.dumps(record),flush=True);bm.free();source.free();break
        entry['accepted']=True;bm.to_mesh(obj.data);bm.free();source.free();obj.data.update();obj.data.validate(clean_customdata=False)
        for p in obj.data.polygons:p.use_smooth=True
        obj.data.normals_split_custom_set([(0,0,0)]*len(obj.data.loops));obj.data.set_sharp_from_angle(angle=math.radians(40))
        mod=obj.modifiers.new('RetopoWeightedNormals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=50;bpy.ops.object.modifier_apply(modifier=mod.name)
    if entry.get('accepted'):
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects:obj.select_set(True)
        bpy.ops.export_scene.gltf(filepath=str(R/f'{floor}_retopo.glb'),export_format='GLB',use_selection=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(R/f'{floor}_retopo.blend'))
    report=[e for e in report if e['floor']!=floor];report.append(entry);(R/'local_retopology_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
