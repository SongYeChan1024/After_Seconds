import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).parent;PROJECT=R.parent.parent/'Unity/After_Seconds_Build_V0.01'
sources=json.loads((R/'audit_current_sources.json').read_text(encoding='utf-8-sig'));results=[]
original='--original' in sys.argv
for item in sources:
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    for col in [bpy.data.meshes,bpy.data.materials,bpy.data.images]:
        for d in list(col):
            if d.users==0:col.remove(d)
    bpy.ops.import_scene.fbx(filepath=str(R/(item['name']+'_original.fbx') if original else PROJECT/item['modelPath']),use_image_search=False)
    records=[]
    for obj in [o for o in bpy.context.scene.objects if o.type=='MESH']:
        bm=bmesh.new();bm.from_mesh(obj.data);lo=Vector(tuple(min(v.co[i] for v in bm.verts) for i in range(3)));hi=Vector(tuple(max(v.co[i] for v in bm.verts) for i in range(3)));diag=(hi-lo).length
        raw=len(bm.verts);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=diag*1e-7);bm.verts.index_update()
        records.append({'rawVerts':raw,'weldedVerts':len(bm.verts),'triangles':sum(len(f.verts)-2 for f in bm.faces),'boundary':sum(e.is_boundary for e in bm.edges),'overused':sum(len(e.link_faces)>2 for e in bm.edges),'winding':sum(len(e.link_faces)==2 and not e.is_contiguous for e in bm.edges),'degenerate':sum(f.calc_area()<=(diag*1e-8)**2 for f in bm.faces),'meshLocalSize':list(hi-lo),'worldSize':list(obj.dimensions),'negativeDeterminant':obj.matrix_world.determinant()<0});bm.free()
    result={'name':item['name'],'path':item['modelPath'],'objects':records};results.append(result);print('EXISTING',json.dumps(result),flush=True)
    (R/('original_audit.json' if original else 'current_import_audit.json')).write_text(json.dumps(results,indent=2),encoding='utf-8')
