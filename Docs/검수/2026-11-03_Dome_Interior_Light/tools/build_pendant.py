# 작성자 송예찬 / 2026-11-03
# [의사코드]
# 1. 돔 내부 고정 캡과 세 가닥 지지선으로 매단 얇은 링 조명을 실제 미터 크기로 만든다.
# 2. 윗 고정부 원점을 유지해 FBX와 조명 앵커를 내보내고 닫힌 표면을 검사한다.
# 3. Blender 원본과 실제 상하부 렌더를 저장한다.
# [코딩]
import bpy,bmesh,math,json,pathlib,hashlib
from mathutils import Vector
W=pathlib.Path(__file__).parent
R=W.parents[2]
S=R/'SourceAssets/SubjectHabitat';S.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
bpy.context.preferences.filepaths.save_version=0
PALETTE={
 'DP_ClinicalWhite':{'baseColor':[.75,.79,.80,1],'metallic':.12,'smoothness':.55,'emission':0},
 'DP_DarkFrame':{'baseColor':[.022,.030,.035,1],'metallic':.65,'smoothness':.52,'emission':0},
 'DP_BrushedSteel':{'baseColor':[.30,.36,.40,1],'metallic':.80,'smoothness':.65,'emission':0},
 'DP_CoolDiffuser':{'baseColor':[.82,.92,1,1],'metallic':0,'smoothness':.35,'emission':1.5},
}
M={}
for n,c in PALETTE.items():
 m=bpy.data.materials.new(n);m.use_nodes=True;m.diffuse_color=c['baseColor'];bs=m.node_tree.nodes.get('Principled BSDF')
 bs.inputs['Base Color'].default_value=c['baseColor'];bs.inputs['Metallic'].default_value=c['metallic'];bs.inputs['Roughness'].default_value=1-c['smoothness']
 bs.inputs['Emission Color'].default_value=c['baseColor'];bs.inputs['Emission Strength'].default_value=c['emission'];M[n]=m

def assign(o,n):o.data.materials.append(M[n]);return o
def annular(n,profile,mat,N=64):
 v=[];faces=[];K=len(profile)
 for r,z in profile:
  v += [(r*math.cos(2*math.pi*i/N),r*math.sin(2*math.pi*i/N),z) for i in range(N)]
 for k in range(K):
  q=(k+1)%K
  for i in range(N):j=(i+1)%N;faces.append((k*N+i,k*N+j,q*N+j,q*N+i))
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],faces);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);assign(o,mat)
 for p in me.polygons:p.use_smooth=True
 return o
def cyl(n,loc,radius,depth,mat,vertices=32,bevel=0):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc);o=bpy.context.object;o.name=n;assign(o,mat)
 if bevel:
  b=o.modifiers.new('Small manufactured edge','BEVEL');b.width=bevel;b.segments=2;bpy.ops.object.modifier_apply(modifier=b.name)
 for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
 return o
def cable(n,a,b):
 av,bv=Vector(a),Vector(b);o=cyl(n,(av+bv)*.5,.0035,(bv-av).length,'DP_BrushedSteel',12);o.rotation_euler=(bv-av).to_track_quat('Z','Y').to_euler();return o

parts=[]
parts.append(annular('Pendant_Housing',[(.560,-1.120),(.568,-1.110),(.692,-1.110),(.700,-1.118),(.700,-1.172),(.692,-1.180),(.568,-1.180),(.560,-1.172)],'DP_ClinicalWhite'))
parts.append(annular('Pendant_DarkLowerTrim',[(.557,-1.181),(.702,-1.181),(.702,-1.194),(.557,-1.194)],'DP_DarkFrame'))
parts.append(annular('Pendant_DownwardDiffuser',[(.577,-1.1945),(.675,-1.1945),(.675,-1.201),(.577,-1.201)],'DP_CoolDiffuser'))
parts.append(cyl('Pendant_TopMount',(0,0,0),.11,.06,'DP_ClinicalWhite',48,.004))
parts.append(cyl('Pendant_MountGasket',(0,0,-.0335),.112,.007,'DP_DarkFrame',48))
for i in range(3):
 a=math.radians(30+i*120);co,si=math.cos(a),math.sin(a)
 top=(.067*co,.067*si,-.027);bottom=(.620*co,.620*si,-1.105)
 parts.append(cable('Pendant_SuspensionCable_'+str(i),top,bottom))
 parts.append(cyl('Pendant_CableMount_'+str(i),bottom,.014,.014,'DP_BrushedSteel',20))
 parts.append(cyl('Pendant_CapEye_'+str(i),top,.009,.012,'DP_DarkFrame',16))

root=bpy.data.objects.new('DomePendantLight',None);bpy.context.collection.objects.link(root)
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();fixture=bpy.context.object;fixture.name='DomePendantLight_Fixture'
bm=bmesh.new();bm.from_mesh(fixture.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(fixture.data);bm.free();fixture.data.update()
fixture.parent=root
anchors={}
for name,co in [('DP_TopMountAnchor',(0,0,.03)),('DP_DownwardLightAnchor',(0,0,-1.212))]:
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.parent=root;o.location=co;anchors[name]=o
objects=[root,fixture,*anchors.values()]
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=root
fbx=W/'DomePendantLight.fbx'
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,global_scale=1.0,add_leaf_bones=False,bake_anim=False,use_custom_props=True,path_mode='AUTO')
bm=bmesh.new();bm.from_mesh(fixture.data)
audit={'triangles':sum(len(f.verts)-2 for f in bm.faces),'boundaryEdges':sum(e.is_boundary for e in bm.edges),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'zeroAreaFaces':sum(f.calc_area()<1e-12 for f in bm.faces)};bm.free()
assert audit['triangles']<8000 and audit['boundaryEdges']==audit['nonManifoldEdges']==audit['zeroAreaFaces']==0,audit
points=[fixture.matrix_world@Vector(c) for c in fixture.bound_box];lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)]
bpy.ops.wm.save_as_mainfile(filepath=str(S/'DomePendantLight.blend'))
manifest={'name':'DomePendantLight','author':'송예찬','version':'V0.01','sourceBlend':'SourceAssets/SubjectHabitat/DomePendantLight.blend','fbx':str(fbx),'sha256':hashlib.sha256(fbx.read_bytes()).hexdigest(),'pivot':'top-mount center, keep origin; never bottom-center normalize','blenderBoundsMin':lo,'blenderBoundsMax':hi,'unitySizeXYZ':[hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]],'materials':PALETTE,'meshAudit':audit,'anchors':{'topMount':{'name':'DP_TopMountAnchor','unityLocalPosition':[0,.03,0]},'downwardLight':{'name':'DP_DownwardLightAnchor','unityLocalPosition':[0,-1.212,0]}},'alignment':'FBX -Z forward/Y up. Preserve imported root rotation; rotationally symmetric about vertical axis. Place topMount anchor just under interior dome crown. Geometry is actual meters, not subject to pod scale.','collision':'Visual model only; fixture remains high overhead and adds no gameplay Collider.'}
(W/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')

# Actual model review from below and above, with studio lights outside export selection.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_x=900;scene.render.resolution_y=1050;scene.render.resolution_percentage=100
scene.world.color=(.18,.18,.18)
scene.view_settings.view_transform='AgX'
def area(name,loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,-.65))-o.location).to_track_quat('-Z','Y').to_euler()
area('Review_Key',(2,-3,2),180,3);area('Review_Fill',(-2,-1,0),100,2);area('Review_Rim',(0,3,1),140,2)
bpy.ops.object.camera_add();camera=bpy.context.object;camera.data.lens=52;scene.camera=camera
for name,loc,target in [('pendant_below.png',(2.0,-2.5,-2.0),(0,0,-.62)),('pendant_overview.png',(2.0,-2.8,1.1),(0,0,-.60))]:
 camera.location=loc;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(W/name);bpy.ops.render.render(write_still=True)
print('MODEL_READY',json.dumps(audit),str(fbx))
# [주석] 지지선과 디퓨저는 정적 외형이며 실제 조명 컴포넌트는 Unity 조립 단계에서 연결한다.
