"""B5 배관·난간·벽 이음 보수 V0.02 · 송예찬.
의사코드: 보존한 벽 마감 생성 코드 읽기 -> 관 프레임/UV·접합부 재제작 ->
연속 계단 난간과 지지부 제작 -> 돌출 덧댐을 얕은 실제 이음으로 변경 -> 별도 모델 출력.
기존 생성기·모델·충돌 정의·문/방 좌표는 보존한다. Unity 외부 아트 제작 도구다.
"""
from pathlib import Path
src=Path(__file__).parent
wall=src/'build_b5_wall_variants.py'
text=wall.read_text(encoding='utf-8-sig');env={'__file__':str(wall),'__name__':'__main__'}
exec(compile(text[:text.rindex('exec(compile(')],str(wall),'exec'),env)
code=env['code']
code=code.replace('\nvariant_textures()\n','\n# Reuse preserved wall PBR maps.\n').replace('\nbrushed_trim_textures()\n','\n# Reuse preserved trim PBR maps.\n')
code=code.replace("surface_box('FinishBand',axis,c,side,(a+b)/2,y,b-a-.012,h,mat,.160,.020,.004)","surface_box('FinishBand',axis,c,side,(a+b)/2,y,b-a-.030,h,mat,.152,.008,.0015)")
start=code.index('def access_panel(');end=code.index('\ndef grille(',start)
code=code[:start]+r'''
def face_ring(name,axis,c,side,along,y,w,h,border=.016):
    # One mitred rectangular ring, not four overlapping trim boxes.
    vs=[]
    for depth in (.151,.159):
        for ww,hh in ((w/2+border,h/2+border),(w/2,h/2)):
            for dx,dy in ((-ww,-hh),(ww,-hh),(ww,hh),(-ww,hh)):
                u,v=(along+dx,c+side*depth) if axis=='H' else (c+side*depth,along+dx)
                vs.append(world(u,y+dy,v))
    fs=[]
    for k in range(4):
        j=(k+1)%4;fs.extend(((k,j,4+j,4+k),(8+k,12+k,12+j,8+j),(k,8+k,8+j,j),(4+k,4+j,12+j,12+k)))
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(materials['WallTrim']);me.update()
    uv=me.uv_layers.new(name='UVMap')
    for p in me.polygons:
        p.use_smooth=True
        for li in p.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co.x*.5+co.y*.5,co.z*.5)
    ob=bpy.data.objects.new(name,me);raw.objects.link(ob)
    # Correct winding uniformly before manufactured edge bevels.
    import bmesh
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    finish(ob,'WallTrim',.0015,zone(along,c) if axis=='H' else zone(c,along));return ob
def access_panel(axis,c,side,along,y=1.65,w=.70,h=.88):
    global detail_count
    surface_box('Closed_Service_Panel',axis,c,side,along,y,w-.006,h-.006,'WallSteel',.150,.012,.002)
    face_ring('Mitred_ServicePanel_Frame',axis,c,side,along,y,w,h)
    surface_box('ServicePanel_Handle',axis,c,side,along+w*.30,y,.018,.15,'Metal',.161,.014,.002)
    detail_count+=1
''' +code[end:]
code=code.replace("'WallTrim',.169,.020,.004)","'WallTrim',.159,.010,.002)")
start=code.index('        start=a+.20\n');end=code.index("        if b-a>3.6",start)
code=code[:start]+r'''
        # Rib only at the real 2.8m panel joint; 3mm proud of the main face.
        count=max(1,math.ceil((b-a)/2.8))
        for j in range(1,count):
            at=a+j*(b-a)/count;lo=max(bottom,1.2)
            if h-lo>.1:surface_box('Flush_Steel_Joint',axis,c,side,at,(lo+h)/2,.022,h-lo-.040,'WallTrim',.153,.006,.001)
''' +code[end:]
start=code.index('        count=max(1,math.ceil((b-a)/(3.5');end=code.index("        if b-a>6",start)
code=code[:start]+"        # Concrete uses the existing recessed panel joint; no proud seam cover.\n"+code[end:]
start=code.index('def tube(');end=code.index('scene.cursor.location=',start)
code=code[:start]+r'''
for name,color,metal,rough in [('PipeSteel',(.30,.35,.38,1),.05,.50),('PipeCoupling',(.58,.62,.64,1),.96,.35),('Handrail',(.46,.50,.52,1),.96,.32)]:
    m=bpy.data.materials.new('AR_'+name);m.diffuse_color=color;m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color;bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;materials[name]=m
repair_stats={'pipeJoints':0,'railPosts':0,'railMounts':0,'transportFrameFlips':0}
def tube(name,points,radius=.11,mat='PipeSteel',sides=16):
    # Rotation-minimising transport frames; continuous arc-length UV, no sudden up-axis switch.
    pts=[Vector(world(u,h,v)) for u,h,v in points];pts=[p for i,p in enumerate(pts) if i==0 or (p-pts[i-1]).length>1e-7]
    tangents=[(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized() for i in range(len(pts))]
    t=tangents[0];ref=Vector((0,0,1)) if abs(t.z)<.9 else Vector((0,1,0));a=t.cross(ref).normalized();frames=[];distance=[0]
    for i,t in enumerate(tangents):
        if i:
            a=tangents[i-1].rotation_difference(t)@a;a=(a-t*a.dot(t)).normalized();distance.append(distance[-1]+(pts[i]-pts[i-1]).length)
        b=t.cross(a).normalized();frames.append((a.copy(),b.copy()))
    vs=[p+radius*(a*math.cos(2*math.pi*j/sides)+b*math.sin(2*math.pi*j/sides)) for p,(a,b) in zip(pts,frames) for j in range(sides)];fs=[]
    for i in range(len(pts)-1):
        for j in range(sides):fs.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
    fs.extend((tuple(reversed(range(sides))),tuple((len(pts)-1)*sides+j for j in range(sides))))
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(materials[mat]);me.update();uv=me.uv_layers.new(name='UVMap')
    for k,p in enumerate(me.polygons):
        p.use_smooth=k<(len(pts)-1)*sides
        for n,li in enumerate(p.loop_indices):
            vi=me.loops[li].vertex_index;ring,j=divmod(vi,sides)
            if k<(len(pts)-1)*sides:
                cell=k%sides;u=(cell+(1 if n in (1,2) else 0))/sides;uv.data[li].uv=(u,distance[ring]/.5)
            else:uv.data[li].uv=(.5+.5*math.cos(2*math.pi*j/sides),.5+.5*math.sin(2*math.pi*j/sides))
    ob=bpy.data.objects.new(name,me);raw.objects.link(ob);finish(ob,mat,.0015,zone(points[0][0],points[0][2]));ob.modifiers['Manufactured_Bevel'].segments=2;bevels[-1]['segments']=2
    return ob
def smooth_path(points,r=.28):
    points=[Vector(p) for p in points];out=[tuple(points[0])]
    for i in range(1,len(points)-1):
        a,b,c=points[i-1:i+2];d=min(r,(b-a).length*.45,(c-b).length*.45);u=(a-b).normalized();v=(c-b).normalized()
        if u.dot(v)<-.999:out.append(tuple(b));continue
        p=b+u*d;q=b+v*d
        for k in range(9):
            t=k/8;out.append(tuple((1-t)**2*p+2*(1-t)*t*b+t*t*q))
    return out+[tuple(points[-1])]
def coupler(name,center,axis,radius=.12):
    p=Vector(center);d=Vector(axis).normalized()
    tube(name+'_Flange',[(p-d*.032),(p+d*.032)],radius+.038,'PipeCoupling',20)
    tube(name+'_Gasket',[(p-d*.006),(p+d*.006)],radius+.042,'Metal',20)
    # Six actual bolt heads around the flange, with consistent winding and UV.
    ref=Vector((0,1,0)) if abs(d.y)<.9 else Vector((1,0,0));a=d.cross(ref).normalized();b=d.cross(a)
    for i in range(6):
        pos=p+(radius+.020)*(a*math.cos(i*math.tau/6)+b*math.sin(i*math.tau/6));tube(name+'_Bolt',[(pos-d*.041),(pos+d*.041)],.009,'PipeCoupling',6)
    repair_stats['pipeJoints']+=1
# Measured pump ports, in blueprint u/height/v coordinates. Two distinct circuits.
# South top centre=(5.138,1.222,6.158), front approximately=(4.88,.79,6.14) in Unity.
paths=[
 ('Supply',[(30.86,1.22,5.84),(30.86,3.50,5.84),(35.40,3.50,5.84),(35.40,3.50,22.16),(29.14,3.50,22.16),(29.14,1.22,22.16)],3.50),
 ('Return',[(31.12,.79,5.86),(31.75,.79,5.86),(31.75,3.10,5.86),(31.75,3.10,5.30),(35.40,3.10,5.30),(35.40,3.10,22.70),(28.25,3.10,22.70),(28.25,3.10,22.14),(28.25,.79,22.14),(28.88,.79,22.14)],3.10)
]
for label,path,height in paths:
    tube('Cooling_'+label+'_ContinuousPipe',smooth_path(path,.38),.12,'PipeSteel',20)
    if label=='Supply':
        joints=[((30.86,1.25,5.84),(0,1,0)),((29.14,1.25,22.16),(0,1,0)),((33.1,height,5.84),(1,0,0)),((35.4,height,11.0),(0,0,1)),((35.4,height,18.5),(0,0,1)),((32.4,height,22.16),(1,0,0))]
    else:
        joints=[((31.14,.79,5.86),(1,0,0)),((28.86,.79,22.14),(1,0,0)),((33.1,height,5.30),(1,0,0)),((35.4,height,11.0),(0,0,1)),((35.4,height,18.5),(0,0,1)),((32.4,height,22.70),(1,0,0))]
    for center,axis in joints:coupler('Cooling_'+label+'_Joint',center,axis)
    for v in (8.5,14.5,20.5):
        box('CoolingPipe_WallMount',35.80,height,v,.08,.26,.26,'PipeCoupling',.003)
        tube('CoolingPipe_MountArm',[(35.4,height,v),(35.77,height,v)],.027,'PipeCoupling',12)
        tube('CoolingPipe_Saddle',[(35.4,height,v-.04),(35.4,height,v+.04)],.145,'PipeCoupling',20)
# Continuous inner U and continuous outer handrail around the middle landing.
outer=[(42.96,.95,26.25),(42.96,.95,26),(42.96,4.85,20),(42.96,4.85,18.70),(39.54,4.85,18.70),(39.54,4.85,20),(39.54,8.75,26),(39.54,8.75,26.35),(39.17,8.75,26.35)]
inner=[(41.64,.95,26.25),(41.64,.95,26),(41.64,4.85,20)]
inner.extend([(41.35+.29*math.cos(k*math.pi/16),4.85,20-.29*math.sin(k*math.pi/16)) for k in range(1,17)])
inner.extend([(41.06,8.75,26),(41.06,8.75,26.35)])
tube('StairA_Outer_ContinuousRail',smooth_path(outer,.22),.035,'Handrail',16)
tube('StairA_Inner_ContinuousRail',smooth_path(inner,.08),.035,'Handrail',16)
for u,upper in ((42.96,False),(41.64,False),(39.54,True),(41.06,True)):
    for d in (.45,2.0,3.5,5.05):
        v=20+d if upper else 26-d;floor=3.9+math.ceil(d/.3)*.195 if upper else math.ceil(d/.3)*.195;top=4.85+d*.65 if upper else .95+d*.65
        tube('StairRail_Post',[(u,floor+.035,v),(u,top,v)],.022,'Handrail',12)
        box('StairRail_MountFoot',u,floor+.018,v,.08,.036,.10,'PipeCoupling',.003)
        repair_stats['railPosts']+=1;repair_stats['railMounts']+=1
for u,v in ((42.96,18.80),(39.54,18.80)):
    tube('LandingRail_Post',[(u,3.92,v),(u,4.85,v)],.022,'Handrail',12);box('LandingRail_Foot',u,3.918,v,.10,.036,.10,'PipeCoupling',.003);repair_stats['railPosts']+=1;repair_stats['railMounts']+=1
(SOURCE/'art_repair_details.json').write_text(json.dumps(repair_stats,ensure_ascii=False,indent=2),encoding='utf-8')
''' +code[end:]
code=code.replace('B5_StealthLayout_WallVariants.blend','B5_StealthLayout_ArtRepair.blend').replace('B5_Stealth_WallVariants.fbx','B5_Stealth_ArtRepair.fbx').replace('wall_variants_manifest.json','art_repair_manifest.json').replace('B5 Wall Finishes V0.02','B5 Art Repair V0.01')
exec(compile(code,str(src/'build_b5_architecture.py'),'exec'),{'__file__':str(src/'build_b5_architecture.py'),'__name__':'__main__'})
