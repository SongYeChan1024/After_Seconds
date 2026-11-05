"""경비 실체 얼굴·투명 바이저 보수 V0.03 · 송예찬.
의사코드: 원본 경비/연구원 보존 -> 얼굴 그림이 붙은 막힌 바이저 제거 ->
기존 연구원의 실제 머리 메시를 헬멧 내부에 맞춤 -> 렌즈·프레임 분리 -> Head 본에 결속 -> 별도 FBX.
53본 리그와 몸/헬멧 원본 UV를 보존한다. 게임 동작 코드를 만들지 않는다.
"""
import bpy,bmesh,json,math,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
src=Path(__file__).parent;repo=src.parents[1];npc=src/'NPC'
dest=repo/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Enemy'
bpy.ops.wm.open_mainfile(filepath=str(npc/'AS_V03_Guard.blend'))
body=next(o for o in bpy.context.scene.objects if o.type=='MESH');arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
with bpy.data.libraries.load(str(npc/'AS_V03_Researcher.blend'),link=False) as (a,b):b.objects=['AS_V03_Researcher']
face=b.objects[0];bpy.context.scene.collection.objects.link(face);face.data=face.data.copy();face.name='AS_Guard_RealFace'
for mod in list(face.modifiers):face.modifiers.remove(mod)
bm=bmesh.new();bm.from_mesh(face.data);remove=[v for v in bm.verts if v.co.z<1.500 or abs(v.co.x-.0035)>.16];bmesh.ops.delete(bm,geom=remove,context='VERTS')
# Retain actual neck skin to meet the body, while removing the researcher's collar.
original_bs=next(n for n in face.data.materials[0].node_tree.nodes if n.type=='BSDF_PRINCIPLED');base=original_bs.inputs['Base Color'].links[0].from_node.image
pixels=np.array(base.pixels[:],dtype=np.float32).reshape(base.size[1],base.size[0],4);layer=bm.loops.layers.uv.active;collar=[]
for f in bm.faces:
    if f.calc_center_median().z>=1.58:continue
    uv=sum((loop[layer].uv for loop in f.loops),Vector((0,0)))/len(f.loops);r,g,b=pixels[int((uv.y%1)*(base.size[1]-1)),int((uv.x%1)*(base.size[0]-1)),:3]
    if r-g<.015 or b>r*.98:collar.append(f)
if collar:bmesh.ops.delete(bm,geom=collar,context='FACES')
bm.to_mesh(face.data);bm.free()
for v in face.data.vertices:
    p=v.co.copy();v.co=(.0035+(p.x-.0035)*.96,.015+(p.y-.0035)*.90,1.530+(p.z-1.540)*.88)
for p in face.data.polygons:p.use_smooth=True
face.matrix_world=Matrix.Identity(4)
face.vertex_groups.clear();group=face.vertex_groups.new(name='Head');group.add([v.index for v in face.data.vertices],1,'REPLACE')
skin=face.data.materials[0].copy();skin.name='AS_Guard_RealSkin';face.data.materials.clear();face.data.materials.append(skin)
bs=next(n for n in skin.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
for key,value in (('Metallic',0),('Roughness',.62)):
    for link in list(bs.inputs[key].links):skin.node_tree.links.remove(link)
    bs.inputs[key].default_value=value
# Close the neck behind the jaw with real geometry; do not leave a view through the head.
patch=min(face.data.polygons,key=lambda p:abs(p.center.z-1.515)+abs(p.center.x)*2+abs(p.center.y+.025))
uv_layer=face.data.uv_layers.active;skin_uv=sum((uv_layer.data[li].uv for li in patch.loop_indices),Vector((0,0)))/len(patch.loop_indices)
nv=[];nf=[];n=20;rings=4
for ring in range(rings):
    t=ring/(rings-1);z=1.445+t*.125;rx=.056-t*.006;ry=.050+t*.006;cy=.025*(1-t)
    for k in range(n):nv.append((.0035+rx*math.cos(k*math.tau/n),cy+ry*math.sin(k*math.tau/n),z))
for ring in range(rings-1):
    for k in range(n):j=(k+1)%n;nf.append((ring*n+k,ring*n+j,(ring+1)*n+j,(ring+1)*n+k))
nf.extend((tuple(reversed(range(n))),tuple((rings-1)*n+k for k in range(n))))
nm=bpy.data.meshes.new('Guard_Neck_Closure');nm.from_pydata(nv,[],nf);nm.materials.append(skin);nm.update();nu=nm.uv_layers.new(name='UVMap')
for p in nm.polygons:
    p.use_smooth=True
    for li in p.loop_indices:
        ring,k=divmod(nm.loops[li].vertex_index,n);nu.data[li].uv=skin_uv+Vector(((k/n-.5)*.006,(ring/(rings-1)-.5)*.006))
neck=bpy.data.objects.new('Guard_Neck_Closure',nm);bpy.context.scene.collection.objects.link(neck);hg=neck.vertex_groups.new(name='Head');ng=neck.vertex_groups.new(name='Neck')
for v in nm.vertices:
    t=(v.co.z-1.445)/.125
    if t>0:hg.add([v.index],t,'REPLACE')
    if t<1:ng.add([v.index],1-t,'REPLACE')
bpy.ops.object.select_all(action='DESELECT');face.select_set(True);neck.select_set(True);bpy.context.view_layer.objects.active=face;bpy.ops.object.join()
# Open the opaque surface that carried a painted face. Keep the helmet shell/neck.
bm=bmesh.new();bm.from_mesh(body.data)
# Split on the opening planes first; deleting whole original triangles left a jagged brow.
for point,normal in [((0,0,1.520),(0,0,1)),((0,0,1.694),(0,0,1)),((0,-.047,0),(0,1,0)),((-.1225,0,0),(1,0,0)),((.1295,0,0),(1,0,0))]:
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=point,plane_no=normal,dist=.000001,use_snap_center=False,clear_outer=False,clear_inner=False)
cut=[]
for f in bm.faces:
    c=f.calc_center_median()
    if 1.5200001<c.z<1.6939999 and abs(c.x-.0035)<.1259999 and c.y<-.0470001:cut.append(f)
removed=len(cut);bmesh.ops.delete(bm,geom=cut,context='FACES');loose=[v for v in bm.verts if not v.link_faces]
if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
bm.to_mesh(body.data);bm.free();body.data.update()
def bind(ob):
    ob.parent=arm;ob.matrix_world=Matrix.Identity(4)
    mod=ob.modifiers.new('Bind_To_Guard_Head','ARMATURE');mod.object=arm
    if 'Head' not in ob.vertex_groups:
        vg=ob.vertex_groups.new(name='Head');vg.add(list(range(len(ob.data.vertices))),1,'REPLACE')
bind(face)
def surface_y(x):return -.135+.030*(abs(x-.0035)/.119)**2
corners=[Vector((-.116,1.695)),Vector((.116,1.695)),Vector((.102,1.532)),Vector((-.102,1.532))]
path=[]
for i,c in enumerate(corners):
    prev=corners[i-1];nxt=corners[(i+1)%4];a=c+(prev-c).normalized()*.013;b=c+(nxt-c).normalized()*.013
    for k in range(7):
        t=k/6;path.append((1-t)**2*a+2*(1-t)*t*c+t*t*b)
verts=[];n=len(path)
for depth in (-.002,.006):
    for side in (-1,1):
        for i,p in enumerate(path):
            tangent=(path[(i+1)%n]-path[i-1]).normalized();normal=Vector((-tangent.y,tangent.x));q=p+normal*(side*.0065);x=q.x+.0035;verts.append((x,surface_y(x)+depth,q.y))
faces=[]
for k in range(n):
    j=(k+1)%n;faces.extend(((k,j,n+j,n+k),(2*n+k,3*n+k,3*n+j,2*n+j),(k,2*n+k,2*n+j,j),(n+k,n+j,3*n+j,3*n+k)))
def mesh_ob(name,verts,faces,material):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(material);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    uv=me.uv_layers.new(name='UVMap')
    for p in me.polygons:
        p.use_smooth=True
        for li in p.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=((v.x+.13)/.26,(v.z-1.50)/.22)
    ob=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(ob);return ob
frame_mat=bpy.data.materials.new('AS_Guard_VisorFrame');frame_mat.use_nodes=True;bs=frame_mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.025,.035,.042,1);bs.inputs['Roughness'].default_value=.42
# Broad brow gasket bridges the lens to the helmet rim and covers the cut seam.
for side_x in (-1,1):
    x=.0035+side_x*.124;lo=len(verts);sx=.008
    verts.extend([(x+dx,y,z) for dx,y,z in [(-sx,-.110,1.671),(sx,-.110,1.671),(sx,-.008,1.671),(-sx,-.008,1.671),(-sx,-.110,1.702),(sx,-.110,1.702),(sx,-.008,1.702),(-sx,-.008,1.702)]])
    faces.extend(tuple(lo+j for j in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
lo=len(verts)
for k in range(21):
    x=-.130+k*.013;verts.extend([(x,surface_y(x)-.001,1.687),(x,-.045,1.687),(x,-.045,1.712),(x,surface_y(x)-.001,1.712)])
for k in range(20):
    for j in range(4):faces.append((lo+k*4+j,lo+k*4+(j+1)%4,lo+(k+1)*4+(j+1)%4,lo+(k+1)*4+j))
faces.extend((tuple(lo+j for j in (3,2,1,0)),tuple(lo+80+j for j in (0,1,2,3))))
frame=mesh_ob('AS_Guard_VisorFrame',verts,faces,frame_mat);bevel=frame.modifiers.new('Manufactured_Bevel_1mm','BEVEL');bevel.width=.001;bevel.segments=3;bevel.limit_method='ANGLE';bevel.harden_normals=True;bind(frame)
lens_mat=bpy.data.materials.new('AS_Guard_ClearVisor');lens_mat.use_nodes=True;bs=lens_mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.75,.88,.91,.14);bs.inputs['Alpha'].default_value=.14;bs.inputs['Roughness'].default_value=.08;bs.inputs['Transmission Weight'].default_value=.95;bs.inputs['IOR'].default_value=1.49
if hasattr(lens_mat,'surface_render_method'):lens_mat.surface_render_method='DITHERED'
center=Vector((0,1.608));lens_verts=[(.0035,surface_y(.0035)+.002,1.608)]
for ring in range(1,7):
    for p in path:
        q=center+(p-center)*(ring/6);x=q.x+.0035;lens_verts.append((x,surface_y(x)+.002,q.y))
lens_faces=[]
for k in range(n):lens_faces.append((0,1+(k+1)%n,1+k))
for r in range(1,6):
    for k in range(n):
        j=(k+1)%n;a=1+(r-1)*n+k;b=1+(r-1)*n+j;c=1+r*n+j;d=1+r*n+k;lens_faces.append((a,b,c,d))
lens=mesh_ob('AS_Guard_ClearVisor',lens_verts,lens_faces,lens_mat)
# A thin curved physical lens, separate from both face and frame.
for p in lens.data.polygons:
    if p.normal.y>0:p.flip()
solid=lens.modifiers.new('Lens_Thickness_1_5mm','SOLIDIFY');solid.thickness=.0015;solid.offset=0
bevel=lens.modifiers.new('Lens_Edge_Bevel_0_5mm','BEVEL');bevel.width=.0005;bevel.segments=2;bind(lens)
# Keep editable modifiers in a hidden source collection. The FBX uses explicitly
# triangulated, validated rest-pose geometry so Unity never has to tessellate
# the very small non-planar polygons produced by the bevel modifier.
editable=bpy.data.collections.new('Editable_Modifier_Sources');bpy.context.scene.collection.children.link(editable)
export_checks=[]
for ob in (body,face,frame,lens):
    original=ob.copy();original.data=ob.data.copy();original.name=ob.name+'_Editable_Source';editable.objects.link(original);original.hide_render=True;original.hide_set(True)
    armature_mods=[m for m in ob.modifiers if m.type=='ARMATURE']
    for m in armature_mods:m.show_viewport=False;m.show_render=False
    tri=ob.modifiers.new('Explicit_Export_Triangles','TRIANGULATE');tri.quad_method='BEAUTY';tri.ngon_method='BEAUTY';tri.keep_custom_normals=True
    bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();evaluated=ob.evaluated_get(dep)
    mesh=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=dep)
    before_faces=len(mesh.polygons);zero_before=sum(p.area<1e-14 for p in mesh.polygons)
    bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7)
    bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY')
    loose=[v for v in bm.verts if not v.link_faces]
    if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
    # Bevel interpolation can leave tiny weight-sum drift; preserve the ratios.
    deform=bm.verts.layers.deform.active
    if deform:
        for v in bm.verts:
            weights=v[deform];total=sum(weights.values())
            if total<=1e-8:raise RuntimeError('Unweighted export vertex in '+ob.name)
            for key in list(weights.keys()):weights[key]/=total
    bm.to_mesh(mesh);bm.free();mesh.update()
    if any(len(p.vertices)!=3 or p.area<1e-14 for p in mesh.polygons):raise RuntimeError('Invalid export triangle in '+ob.name)
    if any(abs(sum(g.weight for g in v.groups)-1)>.001 for v in mesh.vertices):raise RuntimeError('Invalid export weights in '+ob.name)
    ob.data=mesh
    for m in list(ob.modifiers):ob.modifiers.remove(m)
    mod=ob.modifiers.new('Guard_Rig_Deform','ARMATURE');mod.object=arm
    export_checks.append({'mesh':ob.name,'triangles':len(mesh.polygons),'inputZeroAreaTriangles':zero_before,'outputZeroAreaTriangles':0,'nonTriangles':0,'removedDegenerateFaces':before_faces-len(mesh.polygons),'uvLayers':len(mesh.uv_layers),'weightsValid':True})
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(npc/'AS_V03_Guard_HeadRepaired.blend'))
bpy.ops.object.select_all(action='DESELECT')
for ob in (body,arm,face,frame,lens):ob.select_set(True)
bpy.context.view_layer.objects.active=arm
bpy.ops.export_scene.fbx(filepath=str(dest/'AS_V03_Guard_HeadRepaired.fbx'),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,add_leaf_bones=False,bake_anim=False,use_mesh_modifiers=True,mesh_smooth_type='FACE',use_custom_props=True,path_mode='AUTO')
report={'title':'Guard real face / clear visor V0.03','author':'송예찬','removedOpaqueVisorFaces':removed,'faceSource':'AS_V03_Researcher.blend, actual head geometry / preserved UV','newParts':[face.name,frame.name,lens.name],'skinBinding':'Head weights on face/lens/frame; neck closure blends Neck and Head; original guard body weights retained','bones':len(arm.data.bones),'faceTriangles':sum(len(p.vertices)-2 for p in face.data.polygons),'lensThickness_m':.0015,'noAnimationController':True,'exportChecks':export_checks,'editableSources':'Editable_Modifier_Sources hidden collection; bevel widths and segments preserved'}
(npc/'guard_head_repair.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('GUARD_HEAD_REPAIR',json.dumps(report))
