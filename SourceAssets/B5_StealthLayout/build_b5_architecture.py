"""B5 잠입층 맞춤 건축 제작 V0.02 · 작성자 송예찬.
의사코드: 새 평면 읽기 -> 공유 벽/문 구간 분할 -> 바닥/피트/마감 제작 ->
형상별 베벨/노멀 -> 편집 원본 저장 -> 평가 메시를 구역별로 묶어 FBX/검수 자료 출력.
원본 B5 씬과 기존 모델은 수정하지 않는다. Blender 5.2 배치 실행용.
"""
import bpy, json, math, hashlib
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
import numpy as np

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds'
MODEL=ROOT/'05.Model/Environment/B5'
TEX=MODEL/'Textures'
SOURCE=Path(__file__).parent
PLAN=REPO/'Docs/도면/잠입_탐색/layout.json'
for p in (MODEL,TEX,SOURCE): p.mkdir(parents=True,exist_ok=True)
plan=next(p for p in json.loads(PLAN.read_text(encoding='utf-8-sig'))['floors'] if p['floor']=='B5')
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1.0
raw=bpy.data.collections.new('B5_Editable_BevelSources');scene.collection.children.link(raw)
meshes={};objects=[];colliders=[];lights=[];bevels=[];groups=defaultdict(list)
materials={}
palette={'Panel':(.80,.84,.85,1),'Core':(.20,.23,.25,1),'Floor':(.28,.32,.34,1),'Ceiling':(.68,.73,.75,1),'Metal':(.095,.125,.145,1),'Accent':(.78,.27,.055,1),'Light':(.62,.9,1,1),'Water':(.025,.17,.20,1),'Hazard':(.82,.57,.10,1)}
for name,color in palette.items():
    m=bpy.data.materials.new('SL_'+name);m.diffuse_color=color;m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color
    bs.inputs['Roughness'].default_value=.55 if name not in ('Metal','Water') else .3
    bs.inputs['Metallic'].default_value=.3 if name not in ('Water','Light') else 0
    if name=='Light':bs.inputs['Emission Color'].default_value=color;bs.inputs['Emission Strength'].default_value=2
    materials[name]=m

def texture_files():
    rng=np.random.default_rng(705);n=1024
    noise=rng.normal(0,.004,(n,n)).astype(np.float32)
    yy,xx=np.mgrid[0:n,0:n]
    soft=.004*np.sin(xx/93)+.003*np.sin(yy/57)
    for name in ('Base','Normal','MetallicSmoothness'):
        a=np.ones((n,n,4),dtype=np.float32)
        if name=='Base':
            a[:,:,:3]=np.clip(.88+noise[:,:,None]+soft[:,:,None],0,1)
            scratches=(rng.random((n,n))>.9992)
            a[scratches,:3]*=.88
        elif name=='Normal':
            a[:,:,0]=.5+noise*.25;a[:,:,1]=.5+noise*.25;a[:,:,2]=1
        else:
            a[:,:,:3]=.22;a[:,:,3]=np.clip(.52+noise*5+soft,0,1)
        image=bpy.data.images.new('SL_Painted_'+name,width=n,height=n,alpha=True)
        image.pixels.foreach_set(a.ravel());image.filepath_raw=str(TEX/('SL_Painted_'+name+'.png'));image.file_format='PNG';image.save()
texture_files()

def world(u,h,v):return (24-u,16-v,h) # Unity FBX importer mirrors Blender X with this axis conversion.
def zone(u,v):return f'{int(max(0,min(47.9,u))//8)}_{int(max(0,min(31.9,v))//8)}'
def mesh_box(size,mat):
    key=tuple(round(s,5) for s in size)+(mat,)
    if key in meshes:return meshes[key]
    x,y,z=(s/2 for s in size)
    vs=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    fs=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me=bpy.data.meshes.new('SL_Box');me.from_pydata(vs,[],fs);me.update();me.materials.append(materials[mat])
    uv=me.uv_layers.new(name='UVMap')
    for poly in me.polygons:
        axis=max(range(3),key=lambda k:abs(poly.normal[k]));axes=[i for i in range(3) if i!=axis]
        for li in poly.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]*.5,co[axes[1]]*.5)
        poly.use_smooth=True
    meshes[key]=me;return me
def finish(ob,mat,width,sector):
    bevel=ob.modifiers.new('Manufactured_Bevel','BEVEL');bevel.width=width;bevel.segments=1;bevel.limit_method='ANGLE';bevel.angle_limit=math.radians(30);bevel.use_clamp_overlap=True;bevel.harden_normals=True
    normal=ob.modifiers.new('Weighted_Face_Normals','WEIGHTED_NORMAL');normal.keep_sharp=True;normal.weight=50
    ob['bevel_width_m']=width;ob['bevel_segments']=1;ob['source']='B5_StealthLayout V0.02 Lite'
    objects.append(ob);groups[(mat,sector)].append(ob)
    bevels.append({'object':ob.name,'width_m':width,'segments':1,'clamp_overlap':True})
    return ob
def box(name,u,h,v,sx,sy,sz,mat='Panel',bevel=.012,collision=False):
    # Blender local size (X,Y,Z) = requested Unity (width,depth,height).
    ob=bpy.data.objects.new(name,mesh_box((sx,sz,sy),mat));raw.objects.link(ob);ob.location=world(u,h,v)
    finish(ob,mat,min(bevel,min(sx,sy,sz)*.22),zone(u,v))
    if collision:colliders.append({'name':name,'center':[u-24,h,v-16],'size':[sx,sy,sz]})
    return ob
def rect_difference(rect,cut):
    x,y,w,h=rect;a,b,c,d=cut;x1=max(x,a);x2=min(x+w,a+c);y1=max(y,b);y2=min(y+h,b+d)
    if x1>=x2 or y1>=y2:return [rect]
    out=[]
    if y1>y:out.append((x,y,w,y1-y))
    if y2<y+h:out.append((x,y2,w,y+h-y2))
    if x1>x:out.append((x,y1,x1-x,y2-y1))
    if x2<x+w:out.append((x2,y1,x+w-x2,y2-y1))
    return out
def tiles(rect,height,mat,prefix,ceiling=False):
    x,y,w,d=rect
    u=x
    while u<x+w-.001:
        tw=min(2,x+w-u);v=y
        while v<y+d-.001:
            td=min(2,y+d-v)
            box(prefix,u+tw/2,height,v+td/2,tw-.012,.16 if ceiling else .24,td-.012,mat,.006)
            v+=td
        u+=tw

room_heights={r['id']:(7.2 if r['id']=='A' else 11.1 if r['id']=='STA' else 4.0) for r in plan['rooms']}
pit=next(b for b in plan['blocks'] if b['kind']=='pit')
for r in plan['rooms']:
    rect=(r['x'],r['y'],r['w'],r['h']);parts=rect_difference(rect,(pit['x'],pit['y'],pit['w'],pit['h']))
    for k,p in enumerate(parts):
        tiles(p,-.12,'Floor','Floor_'+r['id'])
        x,v,w,d=p;colliders.append({'name':'Floor_'+r['id']+'_'+str(k),'center':[x+w/2-24,-.12,v+d/2-16],'size':[w,.24,d]})
    tiles(rect,room_heights[r['id']]+.08,'Ceiling','Ceiling_'+r['id'],True)
    if r['id']!='STA':
        nx=max(1,math.ceil(r['w']/5));nz=max(1,math.ceil(r['h']/5))
        for ix in range(nx):
            for iz in range(nz):
                u=r['x']+(ix+.5)*r['w']/nx;v=r['y']+(iz+.5)*r['h']/nz;h=room_heights[r['id']]-.16
                if r['kind']=='corridor' and r['w']<r['h']:sx,sz=.34,1.45
                else:sx,sz=1.45,.34
                box('LightBody',u,h,v,sx,.1,sz,'Metal',.012)
                box('LightLens',u,h-.057,v,sx-.12,.025,sz-.10,'Light',.003)
                lights.append({'room':r['id'],'position':[u-24,h-.32,v-16],'range':6.5 if h<5 else 9,'intensity':2.3 if h<5 else 3.8})

# 경계 중복을 합치고 실제 출입구에서 벽을 나눈다.
edges=defaultdict(list)
for r in plan['rooms']:
    x,v,w,d=r['x'],r['y'],r['w'],r['h']
    for axis,c,a,b in [('H',v,x,x+w),('H',v+d,x,x+w),('V',x,v,v+d),('V',x+w,v,v+d)]:edges[(axis,c)].append((a,b,r['id']))
wall_count=0
for (axis,c),ranges in edges.items():
    cuts=set(t for a,b,_ in ranges for t in (a,b))
    doors=[d for d in plan['doors'] if d['axis']==axis and abs((d['y'] if axis=='H' else d['x'])-c)<.001]
    for d in doors:
        mid=d['x'] if axis=='H' else d['y'];cuts.update((mid-d['width']/2,mid+d['width']/2))
    cuts=sorted(cuts)
    for a,b in zip(cuts,cuts[1:]):
        mid=(a+b)/2;owners=[rid for lo,hi,rid in ranges if lo-.001<=mid<=hi+.001]
        if not owners or b-a<.01:continue
        h=max(room_heights[o] for o in owners);is_door=any(abs(mid-(d['x'] if axis=='H' else d['y']))<d['width']/2-.001 for d in doors);bottom=2.8 if is_door else 0
        u,v=(mid,c) if axis=='H' else (c,mid);sx,sz=(b-a,.24) if axis=='H' else (.24,b-a)
        box('WallCore',u,(bottom+h)/2,v,sx,h-bottom,sz,'Core',.012,True);wall_count+=1
        n=max(1,math.ceil((b-a)/1.5));rows=max(1,math.ceil((h-bottom)/1.25))
        for j in range(n):
            along=a+(j+.5)*(b-a)/n;pw=(b-a)/n-.025
            if pw<.06:continue
            for k in range(rows):
                ph=(h-bottom)/rows-.025;cy=bottom+(k+.5)*(h-bottom)/rows
                for side in (-1,1):
                    pu,pv=(along,c+side*.139) if axis=='H' else (c+side*.139,along)
                    psx,psz=(pw,.028) if axis=='H' else (.028,pw)
                    box('WallPanel',pu,cy,pv,psx,ph,psz,'Panel',.010)
        for cy in (.20,2.35):
            if cy<bottom:continue
            for side in (-1,1):
                pu,pv=(mid,c+side*.162) if axis=='H' else (c+side*.162,mid)
                psx,psz=(b-a-.015,.035) if axis=='H' else (.035,b-a-.015)
                box('WallRail',pu,cy,pv,psx,.075,psz,'Metal',.009)

for i,d in enumerate(plan['doors']):
    axis=d['axis'];u,v=d['x'],d['y'];w=d['width']
    for side in (-1,1):
        pu,pv=(u+side*(w/2+.055),v) if axis=='H' else (u,v+side*(w/2+.055))
        sx,sz=(.11,.36) if axis=='H' else (.36,.11)
        box('DoorFrame',pu,1.42,pv,sx,2.84,sz,'Metal',.018)
    sx,sz=(w+.22,.36) if axis=='H' else (.36,w+.22)
    box('DoorLintel',u,2.87,v,sx,.16,sz,'Metal',.018)
    sx,sz=(w-.12,.045) if axis=='H' else (.045,w-.12)
    box('DoorStatus',u,2.88,v,sx,.025,sz,'Light' if d['state']=='open' else 'Accent',.003)
    if d['state']!='open':
        sx,sz=(w-.025,.085) if axis=='H' else (.085,w-.025)
        box('LockedDoorLeaf',u,1.35,v,sx,2.7,sz,'Metal',.018,True)
        box('LockedDoorInset',u,1.35,v,sx if axis=='H' else .10,2.3,.10 if axis=='H' else sz,'Panel',.012)

for b in plan['blocks']:
    if b['kind']=='baffle':box('CorridorScreen',b['x']+b['w']/2,1.8,b['y']+b['h']/2,b['w'],3.6,b['h'],'Panel',.025,True)

# 냉각조 바닥/옹벽: 위를 덮는 보행 메시를 만들지 않는다.
box('CoolingPitBase',29,-3.12,14.5,14,.24,5,'Core',.012,True)
for v in (12,17):
    box('PitRetainingWall',29,-1.5,v,14,3,.22,'Core',.012,True)
    for k in range(28):box('PitHazardInset',22.25+k*.5,.008,v+(-.22 if v==12 else .22),.28,.016,.18,'Hazard' if k%2==0 else 'Metal',.003)
for u in (22,36):box('PitEndWall',u,-1.5,14.5,.24,3,5,'Core',.012,True)
box('WaterSurface',29,-2.65,14.5,13.7,.025,4.7,'Water',.003)

# 계단A: 실제 보행 가능한 두 flight와 중간/상부 landing. 층간 이동 코드는 붙이지 않는다.
stairs=[]
steps=20;rise=7.8/(steps*2);tread=.30
for i in range(steps):
    h=(i+1)*rise;u=42.30;v=26-(i+.5)*tread
    box('StairA_Lower',u,h/2,v,1.40,h,tread+.012,'Floor',.012,True)
for i in range(steps):
    top=3.9+(i+1)*rise;u=40.30;v=20+(i+.5)*tread
    box('StairA_Upper',u,(3.9+top)/2,v,1.60,top-3.9,tread+.012,'Floor',.012,True)
box('StairA_MidLanding',41.25,3.80,19.25,4.25,.20,1.5,'Floor',.012,True)
box('StairA_TopLanding',41.25,7.70,28.25,4.25,.20,4.5,'Floor',.012,True)
box('StairA_ExitFrame',41.25,9.20,30.35,2.2,2.8,.22,'Metal',.02)
box('StairA_ExitInset',41.25,9.15,30.20,1.6,2.5,.045,'Panel',.01)
box('StairA_ExitLamp',41.25,10.65,30.16,1.0,.12,.08,'Light',.01)

def tube(name,points,radius=.11,mat='Metal'):
    pts=[Vector(world(u,h,v)) for u,h,v in points];vs=[];fs=[];n=16
    for i,p in enumerate(pts):
        tangent=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized();up=Vector((0,0,1))
        if abs(tangent.dot(up))>.95:up=Vector((0,1,0))
        a=tangent.cross(up).normalized();b=tangent.cross(a).normalized()
        vs.extend(p+radius*(a*math.cos(2*math.pi*j/n)+b*math.sin(2*math.pi*j/n)) for j in range(n))
    for i in range(len(pts)-1):
        for j in range(n):fs.append((i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j))
    fs.extend((tuple(reversed(range(n))),tuple((len(pts)-1)*n+j for j in range(n))))
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(materials[mat]);me.update()
    for p in me.polygons:p.use_smooth=True
    ob=bpy.data.objects.new(name,me);raw.objects.link(ob);finish(ob,mat,.004,zone(points[0][0],points[0][2]));return ob
def fillet(points,r=.35):
    result=[points[0]]
    for i in range(1,len(points)-1):
        a,b,c=(Vector(p) for p in points[i-1:i+2]);va=(a-b).normalized();vc=(c-b).normalized();rr=min(r,(a-b).length*.35,(c-b).length*.35)
        if abs(va.dot(vc))>.01:result.append(tuple(b));continue
        center=b+va*rr+vc*rr;v0=-vc*rr;v1=-va*rr
        for k in range(9):
            t=k*math.pi/16;result.append(tuple(center+v0*math.cos(t)+v1*math.sin(t)))
    return result+[points[-1]]
for offset in (-.22,.22):
    tube('CoolingServicePipe',fillet([(33.5,.9,30.5+offset),(33.5,3.5,30.5+offset),(35.5,3.5,30.5+offset),(35.5,3.5,22.2+offset),(30,3.5,22.2+offset),(30,.95,22.2+offset)]),.12)
for side in (41.53,43.07):tube('StairA_Handrail',[(side,.95,26),(side,4.85,20)],.035)
for side in (39.43,41.17):tube('StairA_Handrail',[(side,4.85,20),(side,8.75,26)],.035)

scene.cursor.location=(0,0,0)
source_blend=SOURCE/'B5_StealthLayout_Lite.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(source_blend))
deps=bpy.context.evaluated_depsgraph_get();export_collection=bpy.data.collections.new('B5_Export_Baked');scene.collection.children.link(export_collection)
joined=[]
for (mat,sector),obs in groups.items():
    baked=[]
    for ob in obs:
        me=bpy.data.meshes.new_from_object(ob.evaluated_get(deps),depsgraph=deps)
        new=bpy.data.objects.new('Baked_'+ob.name,me);new.matrix_world=ob.matrix_world.copy();export_collection.objects.link(new);baked.append(new)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in baked:ob.select_set(True)
    bpy.context.view_layer.objects.active=baked[0];bpy.ops.object.join();ob=bpy.context.object
    ob.name='SL_'+mat+'_'+sector;bpy.ops.object.origin_set(type='ORIGIN_CURSOR');joined.append(ob)
bpy.ops.object.select_all(action='DESELECT')
for ob in joined:ob.select_set(True)
bpy.context.view_layer.objects.active=joined[0]
fbx=MODEL/'B5_Stealth_Architecture_Lite.fbx'
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,use_mesh_modifiers=True,mesh_smooth_type='FACE',use_custom_props=True,path_mode='AUTO')
triangles=sum(sum(len(p.vertices)-2 for p in ob.data.polygons) for ob in joined)
report={'title':'B5 Stealth Architecture V0.02 Lite','author':'송예찬','blender':bpy.app.version_string,'sourcePlanSHA256':hashlib.sha256(PLAN.read_bytes()).hexdigest(),'fbx':str(fbx),'sourceBlend':str(source_blend),'coordinates':'Blender (24-u,16-v,height); verified Unity (u-24,height,v-16)','sourceObjects':len(objects),'exportMeshes':len(joined),'triangles':triangles,'wallSegments':wall_count,'bevels':bevels,'colliders':colliders,'lights':lights,'stairRise':7.8,'optimization':'Same bevel widths, 1-segment chamfers with weighted normals. Original high detail source retained.','pending':'B4 floor height/transition not implemented; independent review level'}
(SOURCE/'architecture_lite_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('B5_ARCHITECTURE_RESULT',json.dumps({k:report[k] for k in ('sourceObjects','exportMeshes','triangles','wallSegments')},ensure_ascii=False))
