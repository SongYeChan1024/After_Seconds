import bpy,bmesh,json,math,sys,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).parent
MODE=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'high'
CONFIG=json.loads((R/'batch_manifest.json').read_text(encoding='utf-8'))
report=[]
def clear():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    for collection in [bpy.data.meshes,bpy.data.materials,bpy.data.images]:
        for item in list(collection):
            if item.users==0:collection.remove(item)
for asset in CONFIG['assets']:
    path=R/(asset['id']+'_'+MODE+'.glb')
    if not path.exists():continue
    clear();bpy.ops.import_scene.gltf(filepath=str(path))
    records=[]
    for obj in [o for o in bpy.context.scene.objects if o.type=='MESH']:
        bm=bmesh.new();bm.from_mesh(obj.data);raw=len(bm.verts)
        lo=Vector(tuple(min(v.co[i] for v in bm.verts) for i in range(3)));hi=Vector(tuple(max(v.co[i] for v in bm.verts) for i in range(3)));diag=(hi-lo).length
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=max(diag*1e-8,1e-10));bm.verts.index_update();bm.verts.ensure_lookup_table();bm.faces.index_update()
        visited=set();components=[]
        for v in bm.verts:
            if v.index in visited:continue
            stack=[v];visited.add(v.index);count=0
            while stack:
                u=stack.pop();count+=1
                for e in u.link_edges:
                    w=e.other_vert(u)
                    if w.index not in visited:visited.add(w.index);stack.append(w)
            components.append(count)
        seen=set();duplicate=0
        for face in bm.faces:
            key=tuple(sorted(v.index for v in face.verts));duplicate+=key in seen;seen.add(key)
        records.append({'rawVertices':raw,'weldedVertices':len(bm.verts),'triangles':sum(len(f.verts)-2 for f in bm.faces),'uvLayers':len(obj.data.uv_layers),'nonfiniteVertices':sum(not all(math.isfinite(x) for x in v.co) for v in bm.verts),'looseVertices':sum(not v.link_faces for v in bm.verts),'boundaryEdges':sum(e.is_boundary for e in bm.edges),'overusedEdges':sum(len(e.link_faces)>2 for e in bm.edges),'inconsistentWindingEdges':sum(len(e.link_faces)==2 and not e.is_contiguous for e in bm.edges),'zeroAreaFaces':sum(f.calc_area()<=(diag*1e-8)**2 for f in bm.faces),'duplicateFaces':duplicate,'componentVertexCounts':sorted(components,reverse=True),'sourceSize':list(hi-lo),'limitations':'Basic topology scan after seam welding; not a self-intersection or silhouette quality pass; modular connector accuracy is not established.'})
        bm.free()
    item={'id':asset['id'],'name':asset['name'],'stage':MODE,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'objects':records};report.append(item)
    print('AUDIT',asset['id'],MODE,json.dumps(records),flush=True)
    (R/('audit_'+MODE+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
