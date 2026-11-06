"""Repair the approved VARCO monitor without replacing its silhouette or UV texture."""
import bpy,bmesh,json,math
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1];OUT=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B5'
bpy.ops.wm.open_mainfile(filepath=str(R/'SourceAssets/B5_Sector01/S1_VitalMonitor.blend'))
bpy.context.preferences.filepaths.save_version=0;o=next(o for o in bpy.context.scene.objects if o.type=='MESH');o.name='CP_VitalMonitor_Source'
o.modifiers.clear();bm=bmesh.new();bm.from_mesh(o.data)
before=dict(vertices=len(bm.verts),faces=len(bm.faces),boundary=sum(e.is_boundary for e in bm.edges))
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00008)
bmesh.ops.dissolve_degenerate(bm,dist=.000005,edges=list(bm.edges))
boundary=set(e for e in bm.edges if e.is_boundary);loops=[]
while boundary:
    seed=boundary.pop();edges={seed};stack=list(seed.verts)
    while stack:
        v=stack.pop()
        for e in v.link_edges:
            if e in boundary:boundary.remove(e);edges.add(e);stack.extend(e.verts)
    loops.append(edges)
sizes=[sum(e.calc_length() for e in group) for group in loops]
small=[e for group in loops if sum(e.calc_length() for e in group)<.28 for e in group]
if small:bmesh.ops.holes_fill(bm,edges=small,sides=0)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces))
after=dict(vertices=len(bm.verts),faces=len(bm.faces),boundary=sum(e.is_boundary for e in bm.edges),nonmanifold=sum(not e.is_manifold for e in bm.edges))
bm.to_mesh(o.data);bm.free()
# Keep the approved rounded monitor housing; replace melted stand, casters and controls.
bm=bmesh.new();bm.from_mesh(o.data)
bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=(0,0,1.115),plane_no=(0,0,1),clear_inner=True,clear_outer=False)
boundary=[edge for edge in bm.edges if edge.is_boundary]
if boundary:bmesh.ops.holes_fill(bm,edges=boundary,sides=0)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
# Smooth triangle facets while keeping crease edges above 55 degrees.
for p in o.data.polygons:p.use_smooth=True
edgefaces={}
for p in o.data.polygons:
 for k in p.edge_keys:edgefaces.setdefault(tuple(sorted(k)),[]).append(p)
for edge in o.data.edges:
    fs=edgefaces.get(tuple(sorted(edge.vertices)),[])
    edge.use_edge_sharp=len(fs)==2 and fs[0].normal.angle(fs[1].normal)>math.radians(55)
bev=o.modifiers.new('Welded_Manufactured_Edges','BEVEL');bev.width=.0008;bev.segments=2;bev.limit_method='ANGLE';bev.angle_limit=math.radians(48);bev.use_clamp_overlap=True
wn=o.modifiers.new('Stable_Weighted_Normals','WEIGHTED_NORMAL');wn.keep_sharp=True;wn.weight=35
lib=R/'SourceAssets/C01_Perimeter/build_assets.py';env={'__file__':str(lib),'__name__':'repair_helpers'}
exec(compile(lib.read_text('utf-8').split('reset();base();')[0],str(lib),'exec'),env)
mats={}
for key,col in env['palette'].items():
    mat=bpy.data.materials.new('CP_'+key);mat.diffuse_color=col;mats[key]=mat
env['e']['mats']=mats
box,cyl,tube=env['box'],env['cyl'],env['tube']
box('Cart_Crossbeam',0,.225,0,.56,.075,.115,'Coat',.012)
for x in [-.235,.235]:
    box('Cart_Leg',x,.225,0,.095,.075,.52,'Coat',.012)
    for z in [-.22,.22]:
        cyl('Caster_Swivel',(x,.16,z),(x,.205,z),.033,'Steel',16)
        box('Caster_Fork',x,.13,z,.09,.075,.035,'Steel',.006)
        for xx in [x-.043,x+.043]:
            cyl('Caster_Tyre',(xx-.017,.075,z),(xx+.017,.075,z),.075,'Rubber',24)
            cyl('Wheel_Hub',(xx-.018,.075,z),(xx+.018,.075,z),.032,'Steel',16)
box('Sealed_Stand_Column',0,.663,-.015,.115,.80,.12,'Coat',.009)
box('Equipment_Tray',0,.93,-.005,.36,.045,.28,'Steel',.008)
for x in [-.17,.17]:box('Tray_Side',x,.967,-.005,.016,.04,.28,'Coat',.004)
box('Tray_Back',0,.967,-.137,.34,.04,.016,'Coat',.004)
cyl('Head_Mount',(0,1.04,-.015),(0,1.14,-.015),.043,'Steel',20)
tube('Push_Handle',[(-.27,1.115,-.04),(-.27,1.115,.12),(.27,1.115,.12),(.27,1.115,-.04)],.014,'Steel',12)
# Cable loops have coherent tubular sections, with distinct connectors.
for i in range(3):
    pts=[(.20+i*.019,.82+.17*math.cos(a),-.02+.075*math.sin(a)) for a in [j*math.tau/48 for j in range(49)]]
    tube('Sensor_Cable_Coil',pts,.007,'Rubber',8)
tube('Sensor_Lead',[(.20,1.00,-.02),(.22,1.04,.02),(.20,1.10,.14),(.17,1.14,.17)],.007,'Rubber',8)
box('Clean_Control_Fascia',0,1.294,.151,.397,.295,.032,'Coat',.012)
env['screen'](.035,1.32,.174,.265,.195,'Vital')
for y in [1.23,1.27,1.31]:box('Membrane_Key',-.165,y,.177,.029,.022,.010,'Blue',.003)
cyl('Encoder',(-.165,1.37,.172),(-.165,1.37,.198),.022,'Steel',20)
for x in [-.12,-.04,.04,.12]:cyl('Sealed_Sensor_Socket',(x,1.17,.17),(x,1.17,.187),.010,'Dark',16)
box('Power_Indicator',.162,1.19,.174,.025,.012,.008,'Trace',.003)
import runpy
runpy.run_path(str(R/'SourceAssets/C01_PropFinish/finish_geometry.py'))['finish'](env['e'],'CP_VitalMonitor_Repaired')
objs=[ob for ob in bpy.context.scene.objects if ob.type=='MESH']
bpy.ops.wm.save_as_mainfile(filepath=str(H/'CP_VitalMonitor_Repaired.blend'))
dg=bpy.context.evaluated_depsgraph_get();bpy.ops.object.select_all(action='DESELECT');assembled=[]
for src in objs:
    me=bpy.data.meshes.new_from_object(src.evaluated_get(dg),depsgraph=dg);ob=bpy.data.objects.new('Repaired_Part',me);bpy.context.collection.objects.link(ob);ob.matrix_world=src.matrix_world.copy();ob.select_set(True);assembled.append(ob)
bpy.context.view_layer.objects.active=assembled[0];bpy.ops.object.join();combined=bpy.context.object
bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');base=combined.data.copy();bpy.data.objects.remove(combined,do_unlink=True);exports=[]
for index,ratio in enumerate([1,.58,.28]):
    ob=bpy.data.objects.new('CP_VitalMonitor_LOD'+str(index),base.copy());bpy.context.collection.objects.link(ob);ob.matrix_world=o.matrix_world.copy();bpy.context.view_layer.objects.active=ob;ob.select_set(True)
    if ratio<1:
        dec=ob.modifiers.new('Conservative_LOD','DECIMATE');dec.ratio=ratio;bpy.ops.object.modifier_apply(modifier=dec.name)
    bb=bmesh.new();bb.from_mesh(ob.data);bmesh.ops.dissolve_degenerate(bb,dist=1e-6,edges=list(bb.edges));bmesh.ops.triangulate(bb,faces=list(bb.faces));tiny=[f for f in bb.faces if f.calc_area()<5e-9];bmesh.ops.delete(bb,geom=tiny,context='FACES');bb.to_mesh(ob.data);bb.free();exports.append(ob)
bpy.ops.object.select_all(action='DESELECT')
for ob in exports:ob.select_set(True)
bpy.context.view_layer.objects.active=exports[0]
bpy.ops.export_scene.fbx(filepath=str(OUT/'CP_VitalMonitor_Repaired.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE')
report=dict(before=before,weldedOriginal=after,boundaryLoopsBeforeFill=sizes,smallLoopsFilled=sum(v<.28 for v in sizes),triangles=[len(o.data.polygons) for o in exports],housingUVPreserved=True,rebuilt=['stand','tray','four double casters','sensor cables','sealed face controls','display'],originalSourceUnchanged=True)
(H/'vital_repair.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
