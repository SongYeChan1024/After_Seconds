# [의사코드] 저장된 배치·반입 명세를 따라 모델/시각 배치와 검수 결과를 재현한다.
# [코딩]
"""의사코드: 원본 GLB를 열고 형상·UV를 보존해 감량한다.
삼각형/경계 검사를 거친 뒤 바닥 피벗 FBX, 2K 텍스처, 검사 렌더와 수치를 저장한다.
프로젝트 Assets는 수정하지 않고 tmp의 독립 파생본만 만든다.
"""
import bpy,bmesh,hashlib,json,math,struct,sys
from pathlib import Path
from mathutils import Vector,Matrix,geometry
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
names=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [p.stem for p in (R/'raw').glob('*.glb')]

def bounds(objects):
    pts=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
    return Vector([min(p[i] for p in pts) for i in range(3)]),Vector([max(p[i] for p in pts) for i in range(3)])

def audit(mesh,strict=False):
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.faces.ensure_lookup_table();bm.faces.index_update()
    result={'triangles':len(bm.faces),'vertices':len(bm.verts),'boundaryEdges':sum(e.is_boundary for e in bm.edges),'overusedEdges':sum(len(e.link_faces)>2 for e in bm.edges),'zeroAreaFaces':sum(f.calc_area()<1e-14 for f in bm.faces)}
    if strict:
        lo=Vector([min(v.co[i] for v in bm.verts) for i in range(3)]);hi=Vector([max(v.co[i] for v in bm.verts) for i in range(3)]);eps=(hi-lo).length*1e-6
        tree=BVHTree.FromBMesh(bm);cross=[]
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
            if found:cross.append([i,j])
        result['strictCrossingPairs']=len(cross);result['crossingPairsSample']=cross[:20];result['crossingPairs']=cross
    bm.free();return result

def cleanup(mesh):
    bm=bmesh.new();bm.from_mesh(mesh)
    lo=Vector([min(v.co[i] for v in bm.verts) for i in range(3)]);hi=Vector([max(v.co[i] for v in bm.verts) for i in range(3)]);diag=(hi-lo).length
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=diag*1e-8)
    bmesh.ops.dissolve_degenerate(bm,dist=diag*1e-8,edges=list(bm.edges));bm.verts.index_update()
    seen=set();bad=[]
    for f in bm.faces:
        key=tuple(sorted(v.index for v in f.verts))
        if key in seen or f.calc_area()<(diag*1e-8)**2:bad.append(f)
        seen.add(key)
    if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
    loose=[v for v in bm.verts if not v.link_faces]
    if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
    seen=set();discard=[]
    for v in bm.verts:
        if v in seen:continue
        stack=[v];component=[];seen.add(v)
        while stack:
            current=stack.pop();component.append(current)
            for edge in current.link_edges:
                nxt=edge.other_vert(current)
                if nxt not in seen:seen.add(nxt);stack.append(nxt)
        if len(component)<=3:discard.extend(component)
    if discard:bmesh.ops.delete(bm,geom=discard,context='VERTS')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bm.to_mesh(mesh);bm.free();mesh.update()

def patch_crossings(mesh):
    # Only the faces around measured crossings are retriangulated; UVs interpolate from the saved surface.
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.triangulate(bm,faces=list(bm.faces))
    source=bm.copy();source.faces.ensure_lookup_table();source.faces.index_update();tree=BVHTree.FromBMesh(source)
    srcuv=source.loops.layers.uv.active;uv=bm.loops.layers.uv.active
    initial=abs(bm.calc_volume());steps=[];patchlayer=bm.faces.layers.int.new('LocalPatch')
    lo=Vector([min(v.co[i] for v in bm.verts) for i in range(3)]);hi=Vector([max(v.co[i] for v in bm.verts) for i in range(3)]);eps=(hi-lo).length*1e-6
    for iteration in range(20):
        bm.to_mesh(mesh);mesh.update();check=audit(mesh,strict=True)
        if not check['strictCrossingPairs'] and not check['boundaryEdges'] and not check['overusedEdges']:break
        bm.faces.ensure_lookup_table();bm.faces.index_update()
        pairs=check.get('crossingPairs',[])
        bad={bm.faces[i] for pair in pairs for i in pair}
        bad|={f for e in bm.edges if len(e.link_faces)>2 for f in e.link_faces}
        # FBX may drop a pair of almost coincident caps that meet at one vertex.
        # Remove that vertex star before capping, so the patch boundary has simple loops.
        borderjunctions=[v for v in bm.verts if sum(e.is_boundary for e in v.link_edges) not in (0,2)]
        bad|={f for v in borderjunctions for f in v.link_faces}
        for ring in range(1+iteration//3):bad|={n for f in list(bad) for e in f.edges for n in e.link_faces}
        for _ in range(20):
            border={e for f in bad for e in f.edges if sum(n in bad for n in e.link_faces)==1};degree={}
            for e in border:
                for v in e.verts:degree[v]=degree.get(v,0)+1
            junctions=[v for v,d in degree.items() if d!=2]
            if not junctions:break
            bad|={f for v in junctions for f in v.link_faces}
        if len(bad)>max(1500,len(bm.faces)*.25):raise RuntimeError('Excessive local patch growth')
        if bad:bmesh.ops.delete(bm,geom=list(bad),context='FACES_ONLY')
        wires=[e for e in bm.edges if not e.link_faces]
        if wires:bmesh.ops.delete(bm,geom=wires,context='EDGES')
        loose=[v for v in bm.verts if not v.link_edges]
        if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
        boundary={e for e in bm.edges if e.is_boundary};filled=[]
        while boundary:
            edge=next(iter(boundary));start=edge.verts[0];v=edge.verts[1];loop=[start];boundary.remove(edge)
            for _ in range(20000):
                if v==start:break
                loop.append(v);n=[e for e in v.link_edges if e in boundary]
                if len(n)!=1:raise RuntimeError('Patch boundary not simple')
                e=n[0];boundary.remove(e);v=e.other_vert(v)
            existing=next((f for f in loop[0].link_faces if set(f.verts)==set(loop)),None)
            if existing:bmesh.ops.delete(bm,geom=[existing],context='FACES_ONLY')
            elif len(loop)>=3:filled.append(bm.faces.new(loop))
        newfaces=bmesh.ops.triangulate(bm,faces=filled,quad_method='BEAUTY',ngon_method='BEAUTY')['faces']
        for face in newfaces:face[patchlayer]=1
        for edge in list(bm.edges):
            if not edge.is_valid or len(edge.link_faces)!=4:continue
            faces=[f for f in edge.link_faces if f[patchlayer]][:2]
            if len(faces)<2:continue
            a,b=edge.verts;midpoint=bm.verts.new((a.co+b.co)*.5)
            normal=sum((f.normal for f in faces),Vector())
            if normal.length:midpoint.co+=normal.normalized()*eps*.25
            thirds=[next(v for v in f.verts if v not in edge.verts) for f in faces]
            bmesh.ops.delete(bm,geom=faces,context='FACES_ONLY')
            for c in thirds:
                for vertices in [(a,midpoint,c),(midpoint,b,c)]:
                    exists=next((f for f in vertices[0].link_faces if set(f.verts)==set(vertices)),None)
                    if exists is None:
                        face=bm.faces.new(vertices);face[patchlayer]=1;newfaces.append(face)
        for f in newfaces:
            if not f.is_valid:continue
            for l in f.loops:
                hit,normal,index,distance=tree.find_nearest(l.vert.co);sl=list(source.faces[index].loops)
                value=geometry.barycentric_transform(hit,*(l.vert.co for l in sl),*(Vector((l[srcuv].uv.x,l[srcuv].uv.y,0)) for l in sl))
                l[uv].uv=value.xy
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));steps.append({'iteration':iteration,'removedFaces':len(bad),'rebuiltFaces':sum(f.is_valid for f in newfaces)})
    bm.to_mesh(mesh);mesh.update();final=audit(mesh,strict=True);volume=abs(bm.calc_volume());change=abs(volume-initial)/initial if initial else 0
    bm.free();source.free()
    final['patchSteps']=steps;final['relativeVolumeChange']=change
    if final['strictCrossingPairs'] or final['boundaryEdges'] or final['overusedEdges'] or change>.03:raise RuntimeError('Local repair rejected '+str(final))
    return final

def preview(objects,out,name):
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16
    scene.render.resolution_x=600;scene.render.resolution_y=600;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    if scene.world is None:scene.world=bpy.data.worlds.new('ReviewWorld')
    scene.world.color=(.22,.22,.22)
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
    lo,hi=bounds(objects);size=hi-lo;center=(hi+lo)/2;diag=size.length
    camdata=bpy.data.cameras.new('ReviewCamera');cam=bpy.data.objects.new('ReviewCamera',camdata);scene.collection.objects.link(cam);scene.camera=cam
    camdata.type='ORTHO';camdata.ortho_scale=max(size)*1.5
    cam.location=center+Vector((1.4,-2.0,1.25)).normalized()*diag*2;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    for index,offset in enumerate([(2,-3,4),(-3,-1,2),(0,3,3)]):
        data=bpy.data.lights.new('ReviewLight'+str(index),'AREA');data.energy=diag*diag*(100 if index==0 else 70);data.shape='DISK';data.size=diag*1.2
        obj=bpy.data.objects.new(data.name,data);scene.collection.objects.link(obj);obj.location=center+Vector(offset)*diag*.8;obj.rotation_euler=(center-obj.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(out/'preview.png');bpy.ops.render.render(write_still=True)

records=[]
for name in names:
    src=R/'raw'/(name+'.glb');out=R/'prepared'/name;out.mkdir(parents=True,exist_ok=True)
    if (out/'manifest.json').exists() and (out/'preview.png').exists():
        existing=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
        if all(not m['final']['strictCrossingPairs'] and not m['final']['boundaryEdges'] and not m['final']['overusedEdges'] for m in existing['meshes']):
            records.append(existing);print('REUSING_VALIDATED',name,flush=True);continue
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(src))
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];sourcefacts=[];facts=[]
    for o in objects:
        bpy.context.view_layer.objects.active=o; o.select_set(True)
        bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
        cleanup(o.data);sourcefacts.append(audit(o.data));original=o.data.copy()
        count=sourcefacts[-1]['triangles'];target=48000 if name.startswith('Props') else 32000
        if name in ['Env_LoadingShutterWall','Env_SteelGrating']:target=128000
        attempts=[];best=None;bestscore=None
        # Raise the density when collapse creates actual crossings; the source is retained unchanged.
        for density in [target,round(target*1.5),target*2]:
            o.data=original.copy()
            if count>density:
                mod=o.modifiers.new('SurfacePreservingReduction','DECIMATE');mod.decimate_type='COLLAPSE';mod.ratio=density/count;mod.use_collapse_triangulate=True
                bpy.ops.object.modifier_apply(modifier=mod.name)
            cleanup(o.data);measurement=audit(o.data,strict=True);attempts.append(measurement)
            print('AUDIT',name,density,measurement,flush=True)
            score=measurement['strictCrossingPairs']+measurement['overusedEdges']+measurement['boundaryEdges']
            if bestscore is None or score<bestscore:best=o.data.copy();bestscore=score
            if not measurement['strictCrossingPairs'] and not measurement['overusedEdges']:break
        o.data=best
        measurement=patch_crossings(o.data)
        print('REPAIRED',name,measurement,flush=True)
        for p in o.data.polygons:p.use_smooth=True
        if o.data.has_custom_normals:o.data.normals_split_custom_set([(0,0,0)]*len(o.data.loops))
        o.data.set_sharp_from_angle(angle=math.radians(40))
        mod=o.modifiers.new('SurfaceWeightedNormals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=50
        bpy.ops.object.modifier_apply(modifier=mod.name)
        facts.append({'name':o.name,'source':sourcefacts[-1],'attempts':attempts,'final':measurement})
    # glTF importer converts Y-up to Blender Z-up; retain orientation and bottom-center pivot.
    lo,hi=bounds(objects);center=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
    for o in objects:o.matrix_world=Matrix.Translation(-center)@o.matrix_world
    bpy.ops.object.select_all(action='DESELECT')
    for index,o in enumerate(objects):o.select_set(True);o.name=name+('_'+str(index) if len(objects)>1 else '')
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    texrecords=[];materials=[]
    for mat in {m for o in objects for m in o.data.materials if m}:
        mat.name=name+'_Material';bsdf=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
        material={'name':mat.name,'baseColorFactor':([1,1,1,1] if bsdf.inputs['Base Color'].is_linked else list(bsdf.inputs['Base Color'].default_value)),'metallic':float(bsdf.inputs['Metallic'].default_value),'roughness':float(bsdf.inputs['Roughness'].default_value)}
        for node in mat.node_tree.nodes:
            if node.type!='TEX_IMAGE' or not node.image:continue
            image=node.image;links=list(node.outputs['Color'].links)
            semantic='Normal' if any(link.to_node.type=='NORMAL_MAP' for link in links) else 'BaseColor'
            if max(image.size)>2048:
                ratio=2048/max(image.size);image.scale(round(image.size[0]*ratio),round(image.size[1]*ratio))
            dest=out/(name+'_'+semantic+'.png');image.filepath_raw=str(dest);image.file_format='PNG';image.save()
            texrecords.append({'semantic':semantic,'path':str(dest),'width':image.size[0],'height':image.size[1],'colorSpace':'linear' if semantic=='Normal' else 'sRGB'})
            material[semantic]=str(dest)
        materials.append(material)
    fbx=out/(name+'.fbx')
    bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},add_leaf_bones=False,axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,use_mesh_modifiers=True,mesh_smooth_type='OFF',bake_anim=False,path_mode='STRIP',embed_textures=False)
    lo,hi=bounds(objects)
    record={'name':name,'sourcePath':str(src),'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'fbx':str(fbx),'fbxSha256':hashlib.sha256(fbx.read_bytes()).hexdigest(),'blenderBoundsMin':list(lo),'blenderBoundsMax':list(hi),'blenderSizeXYZ':list(hi-lo),'unitySizeXYZ':[hi.x-lo.x,hi.z-lo.z,hi.y-lo.y],'triangles':sum(f['final']['triangles'] for f in facts),'meshes':facts,'materials':materials,'textures':texrecords,'pivot':'bottom-center','sourceFlowId':'3ace28ca-d501-4921-b5a8-0875b2468245','visualOnly':True,'preparation':'UV-preserving collapse with adaptive density, 40 degree sharp edges and weighted normals'}
    (out/'manifest.json').write_text(json.dumps(record,indent=2),encoding='utf-8');records.append(record)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')))
    preview(objects,out,name);print('PREPARED',name,record['triangles'],record['unitySizeXYZ'],flush=True)
(R/'prepared'/'prepared_manifest.json').write_text(json.dumps(records,indent=2),encoding='utf-8')

# [주석] 검수 자료의 작업 순서와 최신 경로표를 확인한 뒤 사용한다.
