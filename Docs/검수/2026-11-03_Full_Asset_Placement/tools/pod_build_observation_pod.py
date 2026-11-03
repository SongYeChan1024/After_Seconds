"""작성자 송예찬 / 2026-11-03 / B5 유리 관찰 포드 제작.

[의사코드]
현재 감방과 플레이어 좌표를 기준으로 2.8m 원형 하부와 반구 유리를 만든다.
유리/흰 받침/검은 프레임/닫힌 배식구/청백 LED를 별도 재질로 분리한다.
원본 바닥을 계속 쓰고, 통행 구멍이나 동작은 만들지 않는다.
닫힌 충돌 패널 24개를 별도 FBX로 내보내고 실제 렌더와 메시 검사를 기록한다.
"""

# [코딩]
import bpy, bmesh, math, json, hashlib, sys
from pathlib import Path
from mathutils import Vector

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
SOURCE=REPO/'SourceAssets/ObservationPod'
SOURCE.mkdir(parents=True,exist_ok=True)
HERE.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.context.preferences.filepaths.save_version=0
for block in list(bpy.data.materials):
    if block.users==0:bpy.data.materials.remove(block)

def material(name,color,metal=0,rough=.35,transmission=0,emission=None):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=rough
    p.inputs['IOR'].default_value=1.45
    p.inputs['Transmission Weight'].default_value=transmission
    if emission:
        p.inputs['Emission Color'].default_value=(*emission,1)
        p.inputs['Emission Strength'].default_value=2
    m.diffuse_color=(*color,.15 if transmission else 1)
    return m

white=material('OP_ClinicalWhite',(0.78,.80,.80),.15,.28)
black=material('OP_BlackFrame',(.018,.025,.030),.72,.24)
steel=material('OP_BrushedSteel',(.34,.39,.43),.82,.22)
glass=material('OP_ClearGlass',(.92,.97,.99),0,.055,1)
led=material('OP_CoolWhiteLED',(.56,.85,.96),.05,.2,emission=(.54,.84,1.0))
seal=material('OP_HatchSeal',(.008,.012,.015),.1,.55)
collision_mat=material('OP_CollisionOnly',(.1,.2,.2),0,.9)

visual=bpy.data.collections.new('ObservationPod_Visual')
collision=bpy.data.collections.new('ObservationPod_Collision')
qa=bpy.data.collections.new('QA_Only_Not_Exported')
for col in (visual,collision,qa):bpy.context.scene.collection.children.link(col)

def move_to(obj,collection):
    for c in list(obj.users_collection):c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj

def mesh_obj(name,verts,faces,mat,collection=visual,smooth=False):
    mesh=bpy.data.meshes.new(name+'_Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);collection.objects.link(obj)
    mesh.materials.append(mat)
    bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bm.to_mesh(mesh);bm.free();mesh.update()
    for poly in mesh.polygons:poly.use_smooth=smooth
    uv=mesh.uv_layers.new(name='SurfaceUV')
    for poly in mesh.polygons:
        axis=max(range(3),key=lambda k:abs(poly.normal[k]));axes=[k for k in range(3) if k!=axis]
        for li in poly.loop_indices:
            co=mesh.vertices[mesh.loops[li].vertex_index].co
            uv.data[li].uv=(co[axes[0]],co[axes[1]])
    return obj

def lathe(name,profile,mat,segments=128,collection=visual,smooth=True,start=0,span=2*math.pi):
    full=abs(span-2*math.pi)<1e-6
    verts=[];rows=[]
    for r,z in profile:
        if abs(r)<1e-7:
            rows.append([len(verts)]);verts.append((0,0,z))
        else:
            row=[]
            for k in range(segments if full else segments+1):
                a=start+span*k/segments
                row.append(len(verts));verts.append((r*math.cos(a),r*math.sin(a),z))
            rows.append(row)
    faces=[]
    for j in range(len(rows)):
        a=rows[j];b=rows[(j+1)%len(rows)]
        if len(a)==1 and len(b)==1:continue
        for k in range(segments):
            nxt=(k+1)%len(a) if full and len(a)>1 else k+1
            nxtb=(k+1)%len(b) if full and len(b)>1 else k+1
            if len(a)==1:faces.append((a[0],b[k],b[nxtb]))
            elif len(b)==1:faces.append((a[k],b[0],a[nxt]))
            else:faces.append((a[k],b[k],b[nxtb],a[nxt]))
    if not full:
        faces.append(tuple(row[0] for row in reversed(rows)))
        faces.append(tuple(row[-1] for row in rows))
    return mesh_obj(name,verts,faces,mat,collection,smooth)

def box(name,location,scale,mat,bevel=0,collection=visual):
    bpy.ops.mesh.primitive_cube_add(size=1,location=location)
    o=bpy.context.object;o.name=name;o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat);move_to(o,collection)
    if bevel:
        mod=o.modifiers.new('ManufacturedEdge','BEVEL');mod.width=bevel;mod.segments=2
        bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
    return o

def tube(name,points,radius,mat,sides=8,collection=visual):
    points=[Vector(p) for p in points];verts=[]
    for j,p in enumerate(points):
        tangent=(points[min(j+1,len(points)-1)]-points[max(j-1,0)]).normalized()
        basis=tangent.cross(Vector((0,0,1)))
        if basis.length<.01:basis=tangent.cross(Vector((0,1,0)))
        basis.normalize();other=tangent.cross(basis).normalized()
        for k in range(sides):
            a=2*math.pi*k/sides;v=p+radius*(basis*math.cos(a)+other*math.sin(a));verts.append(tuple(v))
    faces=[]
    for j in range(len(points)-1):
        for k in range(sides):
            n=(k+1)%sides;faces.append((j*sides+k,j*sides+n,(j+1)*sides+n,(j+1)*sides+k))
    faces.append(tuple(reversed(tuple(range(sides)))))
    faces.append(tuple((len(points)-1)*sides+k for k in range(sides)))
    return mesh_obj(name,verts,faces,mat,collection,True)

def ring(name,r,z,tube_r,mat):
    return lathe(name,[(r+tube_r*math.cos(2*math.pi*k/8),z+tube_r*math.sin(2*math.pi*k/8)) for k in range(8)],mat,128)

R=1.33;RI=1.312;EQUATOR=1.86;BOTTOM=.14
def shell_profile(bottom=BOTTOM,rings=24,collision_profile=False):
    if collision_profile:bottom=BOTTOM
    p=[(R,bottom),(R,EQUATOR)]
    p.extend((R*math.cos(math.pi*.5*k/rings),EQUATOR+R*math.sin(math.pi*.5*k/rings)) for k in range(1,rings+1))
    p.append((0,EQUATOR+RI))
    p.extend((RI*math.cos(math.pi*.5*k/rings),EQUATOR+RI*math.sin(math.pi*.5*k/rings)) for k in range(rings-1,-1,-1))
    p.append((RI,bottom))
    if collision_profile:
        p.extend([(1.29,.14),(1.29,0),(1.40,0),(1.40,.14)])
    return p

lathe('ObservationPod_GlassShell',shell_profile(),glass)
lathe('ObservationPod_WhiteBase',[(1.40,0),(1.40,.105),(1.375,.14),(1.29,.14),(1.29,.085),(1.31,.045),(1.31,0)],white)
lathe('ObservationPod_BlackFoot',[(1.405,0),(1.405,.028),(1.395,.034),(1.36,.034),(1.36,0)],black)
ring('ObservationPod_BaseSeal',1.338,.154,.012,black)
ring('ObservationPod_EquatorFrame',1.341,EQUATOR,.016,black)
ring('ObservationPod_BaseLED',1.376,.131,.008,led)
ring('ObservationPod_InteriorLED',1.299,.152,.006,led)

for k in range(8):
    angle=2*math.pi*k/8
    r=1.344
    lower=1.23 if k==6 else .15
    points=[(r*math.cos(angle),r*math.sin(angle),lower),(r*math.cos(angle),r*math.sin(angle),EQUATOR)]
    points.extend(((R+.014)*math.cos(math.pi*.5*j/28)*math.cos(angle),(R+.014)*math.cos(math.pi*.5*j/28)*math.sin(angle),EQUATOR+(R+.014)*math.sin(math.pi*.5*j/28)) for j in range(1,27))
    tube('ObservationPod_MeridianFrame_%02d'%k,points,.012,black)
lathe('ObservationPod_Crown',[(.17,3.178),(.17,3.206),(.145,3.221),(0,3.221),(0,3.178)],steel,64)
ring('ObservationPod_CrownLED',.165,3.208,.004,led)

# 배식구는 유리를 뚫지 않는 닫힌 덮개다. -BlenderY 쪽에 장식한다.
# 전체 포드는 회전 대칭이므로 Unity에서는 이 노드의 수평 방향을 -Z로 맞춘다.
hatch_y=-math.sqrt(R*R-.30*.30)-.019
box('ObservationPod_HatchBacking',(0,hatch_y,.68),(.69,.04,1.04),white,.015)
box('ObservationPod_HatchSeal',(0,hatch_y-.027,.69),(.51,.014,.29),seal,.008)
box('ObservationPod_FoodHatch_Closed',(0,hatch_y-.039,.69),(.455,.018,.235),steel,.012)
box('ObservationPod_HatchHandle',(.174,hatch_y-.060,.69),(.018,.022,.115),black,.006)
box('ObservationPod_HatchStatusLED',(0,hatch_y-.036,.90),(.18,.009,.012),led,.002)
for x in [-.275,.275]:
    for z in [.23,1.12]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=.014,location=(x,hatch_y-.025,z))
        bolt=bpy.context.object;bolt.name='ObservationPod_HatchFastener';bolt.scale=(1,.35,1)
        bolt.data.materials.append(steel);move_to(bolt,visual)

# 각 패널은 옆 단면까지 막힌 독립 고체다. 바닥판은 만들지 않는다.
for k in range(24):
    lathe('ObservationPod_CollisionSegment_%02d'%k,shell_profile(0,16,True),collision_mat,4,collision,False,start=2*math.pi*k/24,span=2*math.pi/24)

def audit(objects):
    items=[]
    for o in objects:
        if o.type!='MESH':continue
        bm=bmesh.new();bm.from_mesh(o.data)
        items.append({'name':o.name,'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'boundaryEdges':sum(e.is_boundary for e in bm.edges),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'zeroAreaFaces':sum(f.calc_area()<1e-11 for f in bm.faces),'signedVolume':bm.calc_volume(signed=True),'materials':[m.name for m in o.data.materials]})
        bm.free()
    return items

visual_audit=audit(visual.objects);collision_audit=audit(collision.objects)
bad=[a for a in visual_audit+collision_audit if a['boundaryEdges'] or a['nonManifoldEdges'] or a['zeroAreaFaces'] or a['signedVolume']<=0]
if bad:raise RuntimeError('Mesh topology validation failed: '+json.dumps(bad))

def export(collection,path):
    bpy.ops.object.select_all(action='DESELECT')
    for o in collection.objects:o.hide_set(False);o.select_set(True)
    bpy.context.view_layer.objects.active=list(collection.objects)[0]
    bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=False,path_mode='STRIP',use_mesh_modifiers=True)

visual_fbx=HERE/'ObservationPod_Visual.fbx';collision_fbx=HERE/'ObservationPod_Collision.fbx'
export(visual,visual_fbx);export(collision,collision_fbx)
collision.hide_render=True;collision.hide_viewport=True
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'ObservationPod.blend'))

manifest={
    'name':'ObservationPod','author':'송예찬','date':'2026-11-03',
    'approval':'User explicitly requested actual dome construction in this session.',
    'sourceBlend':str(SOURCE/'ObservationPod.blend'),'visualFbx':str(visual_fbx),'collisionFbx':str(collision_fbx),
    'visualSha256':hashlib.sha256(visual_fbx.read_bytes()).hexdigest(),'collisionSha256':hashlib.sha256(collision_fbx.read_bytes()).hexdigest(),
    'recommendedRoom01LocalPositionUnity':[0,0,10.45],'recommendedScale':[1,1,1],
    'orientation':'After importing, derive horizontal direction from root to ObservationPod_FoodHatch_Closed renderer center, and rotate whole visual/collision pair together so that hatch points Unity -Z toward guard. Root pivot is floor center.',
    'dimensionsMetres':{'baseOuterDiameter':2.81,'glassOuterDiameter':2.66,'glassInnerDiameter':2.624,'cylinderEquatorHeight':1.86,'glassTop':3.19,'overallHeight':3.221,'baseHeight':.14,'glassThickness':.018},
    'existingCellInteriorUnity':{'x':[-1.4,1.4],'z':[8.9,12.0],'oldCeiling':2.6,'roomCeiling':4},
    'playerSpawnUnity':[0,.65,10.8],'existingCameraHeightApprox':1.825,
    'spawnClearance':{'horizontalRadiusFromPodCentre':.35,'existingControllerHeight':1.8,'existingControllerRadius':.28,'existingControllerCentreY':.3,'existingSkinWidth':.08,'radialClearanceAfterControllerAndSkin':.602,'headClearanceAtSpawnMetresApprox':1.28},
    'materials':{'OP_ClinicalWhite':{'urp':'Lit','baseColor':[.78,.80,.80,1],'metallic':.15,'smoothness':.72},'OP_BlackFrame':{'urp':'Lit','baseColor':[.018,.025,.03,1],'metallic':.72,'smoothness':.76},'OP_BrushedSteel':{'urp':'Lit','baseColor':[.34,.39,.43,1],'metallic':.82,'smoothness':.78},'OP_ClearGlass':{'urp':'Lit Transparent','baseColor':[.70,.88,.96,.12],'metallic':0,'smoothness':.94,'cull':'Back; shell already contains inward and outward surfaces','zWrite':False,'castShadows':False},'OP_CoolWhiteLED':{'urp':'Lit','baseColor':[.56,.85,.96,1],'emission':[.54,.84,1.0],'emissionIntensity':2},'OP_HatchSeal':{'urp':'Lit','baseColor':[.008,.012,.015,1],'metallic':.1,'smoothness':.45}},
    'collision':{'segments':24,'type':'Static non-convex MeshCollider on each independently closed surface segment; no renderer; no Rigidbody. Not a floor plate.','boundsBaseRadius':1.40,'boundsTop':3.19,'noGameplayOpening':True,'topologyAudit':collision_audit},
    'oldObjectsToDisableAndPreserve':[
        'Room01_Isolation/Geometry/Cell_Wall_Left (Renderer + BoxCollider)',
        'Room01_Isolation/Geometry/Cell_Wall_Right (Renderer + BoxCollider)',
        'Room01_Isolation/Geometry/Cell_Wall_Rear (Renderer + BoxCollider)',
        'Room01_Isolation/Geometry/Cell_Ceiling (Renderer + BoxCollider)',
        'Room01_Isolation/Geometry/Cell_FrontBars/* (all Renderer + BoxCollider; preserve objects)',
        'Room01_Isolation/Decoration/Cell_Bench (Renderer + BoxCollider)',
        'Room01_Isolation/Decoration/Cell_Bench_LegA (Renderer + BoxCollider)',
        'Room01_Isolation/Decoration/Cell_Bench_LegB (Renderer + BoxCollider)',
        'Room01_Isolation/Lighting/Cell_Lamp (move above outside pod or disable lamp + its decorative Renderer; old y2.55 penetrates cap)',
    ],
    'objectsToRelocateAndPreserve':['P01_IsolationBunk_0 currently at (.8,0,10.8) must move outside circular pod because its rectangular footprint crosses glass.','Room01_Isolation/Decoration/Sign_S-03 should be relocated to the front/lower structure; previous y3.02/z8.74 floats in front of dome.'],
    'objectsToKeep':['Room01 floor and its collider','Player root/capsule/camera/Animator and current spawn','Other Room01 walls/ceilings, original ceiling orientation','Guard A at (0,7.4), existing puzzle coordinates'],
    'visualTopologyAudit':visual_audit,'visualTriangles':sum(a['triangles'] for a in visual_audit),'collisionTriangles':sum(a['triangles'] for a in collision_audit),
    'qa':{'renders':['pod_oblique.png','pod_front.png','pod_interior.png'],'roundtrip':'fbx_roundtrip_verification.json','renderNote':'Blender Cycles geometry/material preview. URP transparent material must be configured and inspected in Unity separately.'},
    'unimplemented':'No hatch opening, crawling, escape interaction, door, gun, swap or story mechanics. Glass shell remains closed.',
}
(HERE/'source_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('POD_EXPORTED',manifest['visualTriangles'],manifest['collisionTriangles'],flush=True)
if '--export-only' in sys.argv:raise SystemExit(0)

# 실제 모델 검수용 스튜디오. 이 컬렉션은 FBX 반입 대상에 넣지 않는다.
floor=box('QA_ExistingFacilityFloor',(0,0,-.085),(10,10,.16),material('QA_Floor',(.24,.27,.29),.15,.5),collection=qa)
back=box('QA_FacilityBackground',(0,3.4,2),(8,.2,4),material('QA_Wall',(.58,.62,.64),0,.65),collection=qa)
def aim(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def area(name,location,energy,size,target):
    data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size
    o=bpy.data.objects.new(name,data);qa.objects.link(o);o.location=location;aim(o,target)
area('QA_Key',(3,-4,5),800,4,(0,0,1.4))
area('QA_Rim',(-3,1,4),1100,3,(0,0,1.5))
area('QA_Fill',(0,-1,5),500,3,(0,0,1.2))
camera_data=bpy.data.cameras.new('QA_Camera');camera=bpy.data.objects.new('QA_Camera',camera_data);qa.objects.link(camera)
bpy.context.scene.camera=camera
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=16
scene.cycles.use_denoising=True;scene.cycles.transparent_max_bounces=8;scene.cycles.transmission_bounces=6
scene.render.resolution_x=800;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.world.color=(.22,.24,.27)
scene.view_settings.view_transform='AgX'
camera.location=(4.4,-6.4,3.3);camera_data.type='ORTHO';camera_data.ortho_scale=4.6;aim(camera,(0,0,1.55))
scene.render.filepath=str(HERE/'pod_oblique.png');bpy.ops.render.render(write_still=True)
camera.location=(0,-7,1.62);camera_data.ortho_scale=3.9;aim(camera,(0,0,1.62))
scene.render.filepath=str(HERE/'pod_front.png');bpy.ops.render.render(write_still=True)
camera.location=(0,.35,1.825);camera_data.type='PERSP';camera_data.lens=24;aim(camera,(0,-2,1.55))
scene.render.filepath=str(HERE/'pod_interior.png');bpy.ops.render.render(write_still=True)
print('POD_RENDERED',flush=True)

# [주석]
# FBX에는 실제 포드의 시각 메시 또는 닫힌 충돌 패널만 들어간다.
# QA 바닥·배경·카메라·조명은 별도 컬렉션이며 게임의 공간/조명을 바꾸지 않는다.
# 배식구에는 구멍이 없고 원본 바닥을 유지한다. 모델 제작과 탈출 규칙 구현을 구분한다.
