"""Close-up corrections to the metric, UV-mapped pickup meshes.

Lengths for the replacement parts are in millimetres. Original UV islands use
15/16 of the atlas. The last strip supplies the new metal, rubber and plastic.
"""
import math
import subprocess

import bmesh
import bpy
import numpy as np
from mathutils import Vector


METAL, EDGE, DARK, RUBBER, GOLD, BEIGE, LABEL, OXIDE = range(8)
SWATCHES = [(139,145,146),(184,187,185),(61,64,64),(37,39,39),
            (174,150,92),(149,151,140),(181,178,159),(109,103,92)]
LOOSE = {'Labeler':2, 'Stopwatch':2, 'VoiceRecorder':2, 'VoltageMeter':2,
         'Helmet':40, 'ResearchNotebook':34}


def swatch_uv(index, u, v):
    return ((964+56*u)/1024, (index+.08+.84*v)/8)


def part(name, verts, faces, tiles, smooth=()):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(c*.001 for c in v) for v in verts], [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    uv = mesh.uv_layers.new(name='UVMap')
    xyz = np.array(verts)
    low = xyz.min(axis=0)
    size = np.maximum(np.ptp(xyz,axis=0),.001)
    for face in mesh.polygons:
        face.use_smooth = face.index in smooth
        axis = max(range(3),key=lambda i:abs(face.normal[i]))
        a,b = [i for i in range(3) if i!=axis]
        tile = tiles if isinstance(tiles,int) else tiles[face.index]
        for loop in face.loop_indices:
            v = (xyz[mesh.loops[loop].vertex_index]-low)/size
            uv.data[loop].uv = swatch_uv(tile,v[a],v[b])
    bm=bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-9)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    return obj


def bevel(obj, width, segments=3):
    bpy.context.view_layer.objects.active = obj
    mod=obj.modifiers.new('Machined edge','BEVEL')
    mod.width=width*.001
    mod.segments=segments
    mod.affect='EDGES'
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj


def loft(name, rings, tiles, caps=True, smooth=False):
    count=len(rings[0])
    faces=[]
    tint=[]
    for j in range(len(rings)-1):
        for i in range(count):
            faces.append((j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i))
            tint.append(tiles if isinstance(tiles,int) else tiles[j])
    smooth_faces=range(len(faces)) if smooth else ()
    if caps:
        faces += [tuple(reversed(range(count))),tuple(range((len(rings)-1)*count,len(rings)*count))]
        tint += [tint[0],tint[-1]]
    return part(name,[p for ring in rings for p in ring],faces,tint,smooth_faces)


def plate(name, outline, z0, z1, tile, width):
    rings=[[(x,y,z) for x,y in outline] for z in (z0,z1)]
    return bevel(loft(name,rings,tile),width)


def box(name, center, size, tile, radius):
    x,y,z=center
    a,b,c=[v/2 for v in size]
    return plate(name,[(x-a,y-b),(x+a,y-b),(x+a,y+b),(x-a,y+b)],z-c,z+c,tile,radius)


def ring(axis, pos, r, center, n):
    # (a,b,axis) is right handed for each cyclic permutation.
    a,b=(axis+1)%3,(axis+2)%3
    pts=[]
    for i in range(n):
        theta=math.tau*i/n
        v=list(center)
        v[axis]=pos
        v[a]+=r*math.cos(theta)
        v[b]+=r*math.sin(theta)
        pts.append(v)
    return pts


def turning(name, axis, center, profile, tiles, n=56):
    return loft(name,[ring(axis,z,r,center,n) for z,r in profile],tiles,smooth=True)


def cut(obj, axis, mm, keep_negative=True):
    bm=bmesh.new()
    bm.from_mesh(obj.data)
    p=Vector((0,0,0));p[axis]=mm*.001
    n=Vector((0,0,0));n[axis]=1 if keep_negative else -1
    result=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
                                  dist=.0000001,plane_co=p,plane_no=n,clear_outer=True)
    cut_edges=[e for e in result['geom_cut'] if isinstance(e,bmesh.types.BMEdge) and e.is_valid and e.is_boundary]
    uv=bm.loops.layers.uv.active
    for f in bmesh.ops.holes_fill(bm,edges=cut_edges,sides=0)['faces']:
        for loop in f.loops:
            loop[uv].uv=swatch_uv(DARK,.5,.5)
    bm.normal_update()
    bm.to_mesh(obj.data)
    bm.free()


def remove_fragments(obj, limit):
    bm=bmesh.new()
    bm.from_mesh(obj.data)
    # The imported file can represent a single loose triangle as two opposing faces.
    span=max(max(v.co[i] for v in bm.verts)-min(v.co[i] for v in bm.verts) for i in range(3))
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=span*1e-6)
    pending=set(bm.faces)
    toss=[]
    while pending:
        stack=[pending.pop()]
        group=[]
        while stack:
            face=stack.pop()
            group.append(face)
            for edge in face.edges:
                for f in edge.link_faces:
                    if f in pending:
                        pending.remove(f)
                        stack.append(f)
        if len(group)<=limit:
            toss.extend(group)
    bmesh.ops.delete(bm,geom=toss,context='FACES')
    bm.to_mesh(obj.data)
    bm.free()


def usb(obj):
    cut(obj,1,21.2)
    def opening(y,w,h):
        a,b=w/2,h/2
        d=.48
        return [(x,y,5.05+z) for x,z in
                [(-a+d,-b),(-a,-b+d),(-a,b-d),(-a+d,b),(a-d,b),(a,b-d),(a,-b+d),(a-d,-b)]]
    rings=[opening(20.6,13,5.3),opening(30.8,13,5.3),opening(31,12.7,5.0),
           opening(31,11.65,4.05),opening(20.65,11.65,4.05),opening(20.6,13,5.3)]
    shell=loft('Folded connector shell',rings,[METAL,EDGE,EDGE,DARK,METAL],caps=False)
    bits=[shell,box('Insulating tongue',(0,25,4.35),(10.8,9,1.05),RUBBER,.18)]
    for x in (-3.7,-1.24,1.24,3.7):
        bits.append(box('Contact',(x,25.6,4.93),(1.05,5.9,.15),GOLD,.06))
    for x in (-3.15,3.15):
        bits.append(box('Retention mark',(x,25.2,7.71),(1.7,1.5,.13),DARK,.06))
    return bits


def flashlight(obj):
    cut(obj,0,71)
    return [turning('Tail cap with recessed push switch',0,(0,.15,22.55),
             [(70.6,18.7),(71.6,19.4),(72.25,20.3),(73.1,20.3),(73.5,19.9),
              (80.9,19.9),(81.3,20.4),(83.8,20.4),(85,19.2),(85,14.2),
              (84.15,13.3),(83.3,13.3),(83.3,11.5),(84.2,10.7),(84.45,8.5)],
             [DARK,DARK,METAL,DARK,DARK,DARK,DARK,EDGE,DARK,RUBBER,RUBBER,DARK,RUBBER,RUBBER])]


def thermometer(obj):
    cut(obj,1,61.8)
    return [turning('Closed temperature probe',1,(.18,0,12.5),
                    [(61.4,2.88),(63,2.93),(67.4,2.90),(68.3,2.7),(69.1,2.22),(69.7,1.38),(70,.42)],
                    [METAL,METAL,METAL,EDGE,EDGE,EDGE],32)]


def pager(obj):
    cut(obj,1,2.2,False)
    bits=[box('Rear housing',(-.2,2.35,26.3),(73,3.1,44.3),DARK,1.45),
          box('Battery door',(-.3,.65,23),(49,1.2,26),DARK,.55)]
    profile=[(.7,42),(-2.4,42.4),(-4.8,41.8),(-6.1,39.2),(-6.1,19),
             (-5.7,15.4),(-4.1,12.6),(-2.4,12.1),(-1.7,13.0),(-3.0,15),
             (-3.8,18.1),(-3.8,38.3),(-3.0,39.7),(.7,39.7)]
    rings=[[(x,y,z) for y,z in profile] for x in (-16,16)]
    bits.append(bevel(loft('Curved belt spring',rings,DARK),.55))
    return bits


def wrench():
    # Trace a continuous perimeter from one open jaw through the shank to the other.
    half=[(5.4,48),(6.6,57),(12.6,64),(16.3,73),(16.3,81),(12.6,88),
          (9.2,90),(8,87.5),(8,76),(3.9,71.8),(-4.0,71.8),(-8,76),
          (-8,86.6),(-9.2,87.7),(-13.1,85),(-16,78.5),(-16.3,71.5),
          (-13.5,63.8),(-6.8,57),(-5.4,48)]
    outline=half+[(-x,-y) for x,y in half]
    bits=[plate('One-piece forged spanner',outline,0,5.3,METAL,.75)]
    panel=[(3.25,-49),(3.8,-45),(3.8,45),(3.25,49),(-3.25,49),(-3.8,45),(-3.8,-45),(-3.25,-49)]
    bits.append(plate('Upper forging ridge',panel,5.15,5.75,DARK,.28))
    bits.append(plate('Lower forging ridge',panel,-.4,.13,DARK,.22))
    return bits


def bolt():
    rings=[]
    tiles=[]
    n=48
    def course(z, radii, tile):
        rings.append([(r*math.cos(math.tau*i/n),r*math.sin(math.tau*i/n),z) for i,r in enumerate(radii)])
        tiles.append(tile)
    for z,r in [(0,4.3),(.75,5.1)]:
        course(z,[r]*n,METAL)
    for j in range(100):
        z=1.05+j*.31
        wave=[max(0,1-2*abs(((z/3.45-i/n)%1)-.5)) for i in range(n)]
        course(z,[5.12+1.3*w*min(1,z/2,(33-z)/2) for w in wave],METAL)
    for z,r in [(32.5,5.35),(33.4,5.45),(34.1,6.20)]:
        course(z,[r]*n,METAL)
    for z,dist in [(34.3,9.7),(35.1,10.6),(42.8,10.6),(44,9.4)]:
        course(z,[dist/math.cos((math.tau*i/n+math.pi/6)%(math.pi/3)-math.pi/6) for i in range(n)],METAL)
    result=loft('Hex bolt with continuous thread',rings,tiles[1:],smooth=False)
    for face in result.data.polygons:
        # Smooth only the turned section; each wrench flat on the head remains planar.
        if max(result.data.vertices[i].co.z for i in face.vertices)<.034:
            face.use_smooth=True
    return [result]


def key_and_tag():
    # Broad decorative notches; there is no corresponding lock profile.
    stem=[(-3,-31),(0,-33),(3,-30),(3,-26),(.5,-24),(3,-21),(3,-18),(.2,-16),
          (3,-13),(3,-8),(-3,-8)]
    bits=[plate('Key blade',stem,0,2.1,METAL,.23)]
    out=[(-6.4,-9.3),(-10,-5),(-10,3.6),(-6.6,7.3),(6.6,7.3),(10,3.6),(10,-5),(6.4,-9.3)]
    # Annular loft gives the key bow a proper punched opening.
    outer=[(x,y+0.2) for x,y in out]
    inner=[(-2,1),(-3,2),(-3,4.2),(-2,5.5),(2,5.5),(3,4.2),(3,2),(2,1)]
    def flatloop(loop,z):return [(x,y,z) for x,y in loop]
    bits.append(bevel(loft('Punched key bow',[flatloop(outer,0),flatloop(outer,2.2),
              flatloop(inner,2.2),flatloop(inner,0),flatloop(outer,0)],METAL,caps=False),.25))
    # A separate thin tag hangs from the same wire ring; its hole passes through the faces.
    tag=[(4.7,11),(4.7,36),(6.5,39),(18,39),(20,36),(20,11),(17.2,7.8),(7.5,7.8)]
    hole=[(8.5,11),(8.5,13),(9.5,14),(11.5,14),(12.5,13),(12.5,11),(11.5,10),(9.5,10)]
    bits.append(bevel(loft('ID fob',[flatloop(tag,2.5),flatloop(tag,4.7),flatloop(hole,4.7),
                     flatloop(hole,2.5),flatloop(tag,2.5)],DARK,caps=False),.65))
    bits.append(box('Inset paper ID window',(12.35,26.4,4.70),(11.6,18.7,.32),BEIGE,.14))
    for y,length in [(21.1,7.2),(23.1,5.5)]:
        bits.append(box('Faded identification mark',(12.0,y,4.88),(length,.48,.09),OXIDE,.04))
    rings=[]
    for i in range(73):
        a=math.tau*i/72
        center=(5+6*math.cos(a),7.6+6*math.sin(a),2.1+3.25*math.cos(a))
        rings.append([(center[0]+.65*math.cos(b)*math.cos(a),center[1]+.65*math.cos(b)*math.sin(a),
                       center[2]+.65*math.sin(b)) for b in (math.tau*j/10 for j in range(10))])
    bits.append(loft('Steel keyring',rings,EDGE,caps=False,smooth=True))
    return bits


def pen():
    # One axis from the ball to the push button. The clip is the only bowed part.
    profile = [
        (-72.50, .16), (-72.25, .38), (-71.15, .48), (-70.85, .82),
        (-68.8, 1.10), (-57.0, 4.48), (-56.3, 4.62), (-55.8, 4.62),
        (-55.6, 4.49), (-55.2, 4.55), (-53.9, 4.78), (28.0, 4.78),
        (28.2, 4.87), (29.2, 4.87), (29.4, 4.78), (59.8, 4.78),
        (60.2, 4.83), (61.3, 4.83), (61.5, 4.64), (64.4, 4.60),
        (65.0, 4.16), (65.1, 3.35), (65.6, 3.20), (71.8, 3.20), (72.50, 2.75)
    ]
    finishes = [EDGE, METAL, EDGE, METAL, METAL, EDGE, EDGE, DARK, RUBBER,
                DARK, DARK, METAL, METAL, EDGE, DARK, LABEL, LABEL, DARK,
                DARK, METAL, RUBBER, RUBBER, METAL, EDGE]
    barrel = turning('Graphite barrel, writing point and push button', 1, (0,0,0),
                     profile, finishes, n=26)
    # Half-width and height of a bent stainless spring. The foot returns toward
    # the barrel, while the long middle section leaves space for pocket fabric.
    path = [(24.8,.61,5.18),(25.5,1.02,5.04),(26.7,1.32,5.07),
            (28.0,1.44,5.35),(30.4,1.50,5.94),(37.0,1.51,6.25),
            (47.0,1.53,6.42),(54.0,1.54,6.43),(57.5,1.58,6.33),
            (59.5,1.62,6.03),(60.7,1.63,5.53),(61.4,1.60,4.96),
            (61.5,1.46,4.46)]
    rings = []
    for y, w, z in path:
        rings.append([(x,y,z+dz) for x,dz in [
            (-w+.26,-.29),(-w,-.13),(-w,.13),(-w+.26,.29),
            (w-.26,.29),(w,.13),(w,-.13),(w-.26,-.29)]])
    clip = loft('Formed pocket clip', rings, EDGE, smooth=True)
    return [barrel, clip]


def security_prop():
    """Closed exterior for the fictional security prop, modelled in side elevation."""
    def flank(name, outline, width, finish, chamfer, offset=0):
        loops=[[(x,side,z) for x,z in outline] for side in (offset-width/2,offset+width/2)]
        return bevel(loft(name,loops,finish),chamfer,3)

    def top_section(x,w,bottom,top):
        return [(x,y,z) for y,z in [(-w+1,bottom),(-w,bottom+1),(-w,top-3.3),
                (-w+3,top), (w-3,top),(w,top-3.3),(w,bottom+1),(w-1,bottom)]]

    parts=[bevel(loft('Satin graphite upper casing',
                 [top_section(x,w,b,t) for x,w,b,t in [(-82,10,12,29),(-78,12,11,33),
                  (-55,12,11,34),(52,12,11,34),(60,11.8,12,33),(64,10.9,14,30)]],
                 METAL),.70)]
    outline=[(-76,11.8),(58,12.7),(62,15),(68,15),(66,10),(58,6),(50,4),
             (48,0),(48,-9),(58,-56),(54,-60),(29,-62),(24,-57),
             (14,-14),(9,-6),(4,-3),(-22,-3),(-32,.5),(-70,1.8),(-76,4.4)]
    parts.append(flank('Moulded frame and backstrap',outline,20,DARK,1.9))
    guard=[(-37,3),(-32,-1),(-29,-13),(-26,-17),(-20,-18.8),(4,-18.8),
           (12,-15),(17,-12),(20,-17),(12,-22),(6,-24),(-21,-24),
           (-29,-22.4),(-33,-19.6),(-36,-15),(-40,-.5),(-42,2)]
    parts.append(flank('Continuous rounded guard',guard,11.3,DARK,1.45))
    parts.append(flank('Fixed inset silhouette',[(.5,.3),(5.8,.3),(5.1,-3.2),(2,-7),
                 (.2,-10.1),(.7,-12.2),(3,-13.5),(2,-14.5),(-.7,-13.3),(-2.0,-11.3),
                 (-2.1,-8.6),(-.7,-5.3),(1.0,-2.3)],6.3,RUBBER,.8))
    panel=[(22,-8),(27,-6),(43,-7),(46,-12),(54.5,-52),(51,-56),
           (32,-57),(29,-53),(20,-15)]
    for sign in (-1,1):
        parts.append(flank('Stippled grip surface',panel,2.2,RUBBER,.95,sign*10))
        for j in range(6):
            x=27+j*4.1
            parts.append(flank('Cast surface groove',[(x,15),(x+1.25,15),(x+5.25,28),
                               (x+4.0,28)],.45,OXIDE,.12,sign*12))
    parts.append(flank('Rubber heel',[(27,-57.4),(54.7,-54.8),(58.6,-55.3),
                       (60,-60.8),(32,-64),(27.5,-63)],23,RUBBER,1.15))
    parts.append(flank('Flush side insert',[(-9,18),(15,18),(17,20),(17,28),
                       (15.5,29),(-8.5,29),(-10,27.6)],.48,OXIDE,.22,12))
    parts.append(flank('Frame detail',[(21,4),(34,4),(36,5.2),(34,6.8),(22,6.8)],
                       1.4,METAL,.38,-10))
    # A closed, shallow inset on the front of the prop.
    parts.append(turning('Sealed front medallion',0,(0,0,22.4),
                 [(-82.3,5.5),(-82.15,6.35),(-81.5,6.45)],[OXIDE,METAL],28))
    # One rear silhouette with a real gap above the bridge. The two pale marks
    # and the contrasting front mark belong to the model and remain visible from behind.
    rear=[(-7.5,33),(-7.5,38.5),(-6.9,39.9),(-2.8,39.9),(-2.55,36.0),
          (2.55,36.0),(2.8,39.9),(6.9,39.9),(7.5,38.5),(7.5,33)]
    parts.append(bevel(loft('Notched rear sight', [[(x,y,z) for y,z in rear] for x in (47,55)],DARK),.30))
    parts.append(flank('Front sight post',[(-69,32.3),(-61,32.8),(-62.2,39.1),(-65.8,39.4)],
                       3.1,DARK,.33))
    for side in [-1,1]:
        parts.append(turning('Rear sight paint',0,(0,side*5.05,38.05),
                     [(54.9,.87),(55.17,.87)],[BEIGE],14))
    parts.append(flank('Front sight paint',[(-62.9,36.4),(-62.16,36.4),(-62.40,38.7),
                       (-63.1,38.7)],1.8,LABEL,.12))
    # The front mark is painted on the camera-facing face of the post.
    parts.append(turning('Front sight index',0,(0,0,37.7),
                 [(-62.05,.94),(-61.64,.94)],[LABEL],16))
    for obj in parts:
        for v in obj.data.vertices:
            x,y,z=v.co
            v.co=(y,-x,z)
        obj.data.update()
    return parts


PISTOL_MARKERS = {
    'RearSightReference': (0,-.05517,.0377),
    'FrontSightReference': (0,.06164,.0377),
    'GripReference': (0,-.036,-.025),
}


PATCHES={'UsbDrive':usb,'Flashlight':flashlight,'Thermometer':thermometer,'Pager':pager}
REBUILDS={'Wrench':wrench,'Bolt':bolt,'Key':key_and_tag,'Pen':pen,'Pistol':security_prop}


def refine(obj, key):
    if key in LOOSE:
        remove_fragments(obj, LOOSE[key])
        return False
    if key not in PATCHES and key not in REBUILDS:
        return False
    uv=obj.data.uv_layers.active
    for loop in uv.data:
        loop.uv.x *= 960/1024
    if key in REBUILDS:
        obj.data.clear_geometry()
        bits=REBUILDS[key]()
    else:
        bits=PATCHES[key](obj)
    bpy.ops.object.select_all(action='DESELECT')
    for bit in bits:
        bit.data.materials.append(obj.data.materials[0])
        if key in REBUILDS:
            for loop in bit.data.uv_layers[0].data:
                u,v=loop.uv
                tile=min(7,max(0,int(v*8)))
                local_u=(u*1024-964)/56
                local_v=(v*8-tile-.08)/.84
                loop.uv=((tile%2+.02+.96*local_u)/2,(tile//2+.025+.95*local_v)/4)
        bit.select_set(True)
    obj.select_set(True)
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.join()
    return True


def pack_strip(path, normal):
    command=['ffmpeg','-v','error','-i',str(path),'-vf','scale=960:1024:flags=lanczos',
             '-f','rawvideo','-pix_fmt','rgb24','pipe:1']
    src=np.frombuffer(subprocess.check_output(command),dtype=np.uint8).reshape(1024,960,3)
    pixels=np.empty((1024,1024,3),dtype=np.uint8)
    pixels[:,:960]=src
    rng=np.random.default_rng(34)
    for index,color in enumerate(SWATCHES):
        rows=slice((7-index)*128,(8-index)*128)
        if normal:
            pixels[rows,960:]=(128,128,255)
        else:
            grain=rng.normal(0,1.5,(128,64,1))+rng.normal(0,1.25,(128,1,1))
            pixels[rows,960:]=np.clip(np.array(color)+grain,0,255)
    subprocess.run(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1024x1024',
                    '-i','pipe:0','-frames:v','1',str(path)],input=pixels.tobytes(),check=True)


def forged_atlas(out, prefix, key):
    """Use full-size metal and polymer swatches with distinct wear and reflectance."""
    rng=np.random.default_rng(610)
    albedo=np.empty((1024,1024,3),np.uint8)
    normal=np.empty_like(albedo)
    packed=np.zeros((1024,1024,4),np.uint8)
    y,x=np.mgrid[:256,:512]
    for i,base in enumerate(SWATCHES):
        rows=slice((3-i//2)*256,(4-i//2)*256)
        cols=slice((i%2)*512,(i%2+1)*512)
        metal=i in (METAL,EDGE,GOLD,OXIDE) or (key=='Wrench' and i==DARK)
        cloud=np.zeros((256,512))
        for freq,amp in [(1.2,3.2),(3.4,2.4),(8,1.2)]:
            cloud+=amp*np.sin(x*freq/77+y*freq/133+rng.uniform(0,6))*np.cos(y*freq/81+rng.uniform(0,6))
        grain=rng.normal(0,1.7,(256,512))+rng.normal(0,1.15,(256,1))
        wear=np.zeros_like(cloud)
        for _ in range(65 if metal else 28):
            px,py=rng.uniform(0,512),rng.uniform(0,256)
            length=rng.uniform(5,35)
            slope=rng.uniform(-.45,.45)
            dx=x-px
            wear+=np.maximum(0,1-np.abs(y-py-slope*dx)/.95)*np.maximum(0,1-np.abs(dx)/length)
        color=np.array(base,dtype=float)
        if key=='Wrench' and i in (METAL,DARK):
            color=np.array((105,118,119) if i==METAL else (88,101,102))
        if key=='Bolt' and i==METAL:
            color=np.array((112,105,94))
        if key=='Key' and i==METAL:
            color=np.array((152,148,131))
        if key=='Pen' and i==DARK:
            color=np.array((51,59,64))
        if key=='Pen' and i==LABEL:
            color=np.array((48,82,115))
        if key=='Pistol':
            color=np.array({METAL:(75,84,91),DARK:(64,67,65),RUBBER:(48,51,49),
                            OXIDE:(50,57,60),BEIGE:(209,212,195),LABEL:(232,174,90)}.get(i,base))
        albedo[rows,cols]=np.clip(color+(cloud+grain+wear*(18 if metal else 9))[:,:,None],0,255)
        dy,dx=np.gradient(wear)
        if key=='Pistol' and i==RUBBER:
            pits=rng.random((64,128)).repeat(4,axis=0).repeat(4,axis=1)
            texture=.40*pits+.15*np.roll(pits,1,axis=1)+.15*np.roll(pits,1,axis=0)
            sy,sx=np.gradient(texture)
            dy+=sy*16
            dx+=sx*16
            albedo[rows,cols]=np.clip(albedo[rows,cols].astype(float)+(texture-.35)[:,:,None]*31,0,255)
        normal[rows,cols]=np.stack([np.clip(128+dx*12,0,255),np.clip(128+dy*12,0,255),
                                    np.full_like(wear,255)],axis=-1)
        packed[rows,cols,0]=np.clip((174 if metal else 5)+cloud,0,255)
        packed[rows,cols,3]=np.clip((120 if metal else 67)+cloud+wear*22,0,255)
    for name,pixels,format in [('Albedo',albedo,'rgb24'),('Normal',normal,'rgb24'),('MetallicGloss',packed,'rgba')]:
        path=out/(prefix+'_'+name+'.png')
        subprocess.run(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt',format,'-s','1024x1024',
                        '-i','pipe:0','-frames:v','1',str(path)],input=pixels.tobytes(),check=True)
