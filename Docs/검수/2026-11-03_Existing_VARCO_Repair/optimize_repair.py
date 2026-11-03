import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).parent
targets=json.loads((R/'processing_targets.json').read_text(encoding='utf-8-sig'))
if '--' in __import__('sys').argv:
    selected=__import__('sys').argv[__import__('sys').argv.index('--')+1:]
    targets={k:v for k,v in targets.items() if k in selected}
reports=[]
for floor,target in targets.items():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    for collection in [bpy.data.meshes,bpy.data.materials,bpy.data.images]:
        for item in list(collection):
            if item.users==0:collection.remove(item)
    bpy.ops.import_scene.fbx(filepath=str(R/f'{floor}_original.fbx'),use_image_search=False)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    entry={'floor':floor,'method':'Blender collapse decimation from welded original; UV loops retained; no voxel remesh','targetTriangles':target,'objects':[]}
    for o in meshes:
        bpy.context.view_layer.objects.active=o
        bm=bmesh.new();bm.from_mesh(o.data)
        lo=Vector(tuple(min(v.co[i] for v in bm.verts) for i in range(3)));hi=Vector(tuple(max(v.co[i] for v in bm.verts) for i in range(3)));diag=(hi-lo).length
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=diag*1e-7)
        bm.verts.index_update();bm.verts.ensure_lookup_table()
        source=BVHTree.FromBMesh(bm)
        original_triangles=sum(len(f.verts)-2 for f in bm.faces)
        bm.to_mesh(o.data);bm.free();o.data.update()
        mod=o.modifiers.new('PreserveOriginalSurface','DECIMATE');mod.decimate_type='COLLAPSE';mod.ratio=target/original_triangles;mod.use_collapse_triangulate=True
        bpy.ops.object.modifier_apply(modifier=mod.name)
        # Keep the exported source shading/UVs; geometry is measured independently.
        bm=bmesh.new();bm.from_mesh(o.data);bm.verts.index_update();bm.verts.ensure_lookup_table()
        before_cleanup={'vertices':len(bm.verts),'faces':len(bm.faces)}
        bmesh.ops.dissolve_degenerate(bm,dist=diag*1e-7,edges=list(bm.edges))
        bm.verts.index_update()
        seen_faces=set();bad=[]
        for face in bm.faces:
            key=tuple(sorted(v.index for v in face.verts))
            if key in seen_faces or face.calc_area() <= (diag*1e-8)**2: bad.append(face)
            seen_faces.add(key)
        if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
        # An isolated component of <=3 vertices cannot enclose a solid volume;
        # these are collapsed remnants, unlike handles and pipes with real shells.
        visited_cleanup=set();discard=[]
        for v in bm.verts:
            if v in visited_cleanup:continue
            stack=[v];visited_cleanup.add(v);comp=[]
            while stack:
                u=stack.pop();comp.append(u)
                for e in u.link_edges:
                    w=e.other_vert(u)
                    if w not in visited_cleanup:visited_cleanup.add(w);stack.append(w)
            if len(comp)<=3:discard.extend(comp)
        if discard:bmesh.ops.delete(bm,geom=discard,context='VERTS')
        loose=[v for v in bm.verts if not v.link_faces]
        if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
        bm.verts.index_update();bm.verts.ensure_lookup_table()
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(len(e.link_faces)>2 for e in bm.edges)
        visited=set();components=[]
        for v in bm.verts:
            if v.index in visited:continue
            stack=[v];visited.add(v.index);vs=[]
            while stack:
                u=stack.pop();vs.append(u)
                for e in u.link_edges:
                    w=e.other_vert(u)
                    if w.index not in visited:visited.add(w.index);stack.append(w)
            comps_lo=[min(v.co[i] for v in vs) for i in range(3)];comps_hi=[max(v.co[i] for v in vs) for i in range(3)]
            components.append({'vertices':len(vs),'min':comps_lo,'max':comps_hi})
        distances=[]
        for v in bm.verts:
            hit=source.find_nearest(v.co)
            if hit[0] is not None:distances.append(hit[3])
        distances.sort()
        # Exact surface overlap candidates from a BVH, excluding shared vertices.
        bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.faces.index_update();bm.faces.ensure_lookup_table()
        tree=BVHTree.FromBMesh(bm);pairs=tree.overlap(tree);intersections=[]
        for i,j in pairs:
            if i>=j:continue
            f1=bm.faces[i];f2=bm.faces[j]
            if set(f1.verts).intersection(f2.verts):continue
            intersections.append([i,j])
        item={'vertices':len(bm.verts),'triangles':len(bm.faces),'cleanupBefore':before_cleanup,'collapsedRemnantVerticesRemoved':len(discard),'degenerateOrDuplicateFacesRemoved':len(bad),'boundaryEdges':boundary,'edgesWithMoreThanTwoFaces':nonmanifold,'components':sorted(components,key=lambda c:-c['vertices']),
            'sourceDistanceMaxFractionOfDiagonal':max(distances,default=0)/diag,'sourceDistanceP95FractionOfDiagonal':distances[int(.95*(len(distances)-1))]/diag if distances else 0,
            'nonAdjacentTriangleOverlapCandidateCount':len(intersections),'nonAdjacentTriangleOverlapCandidates':intersections[:30],
            'overlapLimit':'BVH overlaps are review candidates; coplanar touches and neighboring UV seams can give false positives.'}
        bm.to_mesh(o.data);bm.free();o.data.update();entry['objects'].append(item)
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(R/f'{floor}_optimized.glb'),export_format='GLB',use_selection=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(R/f'{floor}_optimized.blend'))
    reports.append(entry);(R/'optimization_report.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8-sig')
    print('OPTIMIZED',floor,json.dumps(entry),flush=True)

