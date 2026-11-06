"""Blender: complete B5 shell from approved coordinates, plus C01 lining.
Only AF_* assets are written. Existing CF/S1 sources remain unchanged.
"""
from pathlib import Path
import json,math
H=Path(__file__).resolve().parent; R=H.parents[1]
old=R/'SourceAssets/CircularFacility/build_geometry.py'
code=old.read_text('utf-8').split("if '--pipes-only' in sys.argv:")[0]
code=code.replace("Docs/도면/원형공동/facility_layout.json","Docs/도면/Decision/원형공동/facility_layout.json")
env={'__file__':str(old),'__name__':'authoring_library'};exec(compile(code,str(old),'exec'),env)
env['HERE']=H
globals().update({k:v for k,v in env.items() if not k.startswith('__')})
H=Path(__file__).resolve().parent if '__file__' in globals() else H
f=next(f for f in DATA['floors'] if f['id']=='B5');rooms=f['rooms'];ts=f['tunnels']
assert len(rooms)==15 and len(ts)==19
reset()
interior={r['id']:sphere('Cut_'+r['id'],r['x'],r['v'],r['r']) for r in rooms}
cuts=[sweep('Cut_'+t['id'],t,extend=4) for t in ts]
for r in rooms:
    o=sphere('CF_B5_'+r['id']+'_Dome',r['x'],r['v'],r['r']+.22);o.data.materials.append(env['mats']['Shell'])
    boolean(o,interior[r['id']]);bottom=box('CutBottom',r['x'],-r['r'],r['v'],r['r']*3,r['r']*2,r['r']*3,bevel=0);boolean(o,bottom);bpy.data.objects.remove(bottom,do_unlink=True)
    for t,cut in zip(ts,cuts):
        if r['id'] in (t['a'],t['b']):boolean(o,cut)
    for p in o.data.polygons:p.use_smooth=True
    m=o.modifiers.new('Opening_Bevel_12mm','BEVEL');m.width=.012;m.segments=3;m.limit_method='ANGLE';m.angle_limit=.6;o['bevel_width_m']=.012
    print('ROOM',r['id'],flush=True)
for i,t in enumerate(ts):
    o=sweep('CF_'+t['id']+'_Vault',t,pad=.18,mat='Shell');boolean(o,cuts[i])
    for r in rooms:
        if r['id'] in (t['a'],t['b']):boolean(o,interior[r['id']])
    m=o.modifiers.new('Vault_Edge_Bevel_8mm','BEVEL');m.width=.008;m.segments=2;m.limit_method='ANGLE';o['bevel_width_m']=.008
floor=cylinder('CF_B5_Floor',rooms[0]['x'],rooms[0]['v'],rooms[0]['r'])
for r in rooms[1:]:
    ob=cylinder('JoinFloor',r['x'],r['v'],r['r']);boolean(floor,ob,'UNION');bpy.data.objects.remove(ob,do_unlink=True)
for t in ts:
    ob=floorbar(t);boolean(floor,ob,'UNION');bpy.data.objects.remove(ob,do_unlink=True)
for ob in list(interior.values())+cuts:bpy.data.objects.remove(ob,do_unlink=True)
m=floor.modifiers.new('Slab_Bevel_12mm','BEVEL');m.width=.012;m.segments=2;m.limit_method='ANGLE';floor['bevel_width_m']=.012
export('AF_B5_FullLayout','B5')
shell_manifest=dict(env['manifest'])

# Reuse the established bevel, UV and triangulation authoring helpers.
detail=R/'SourceAssets/B5_Sector01/build_details.py';code=detail.read_text('utf-8').split('# Structural ribs')[0]
de={'__file__':str(detail),'__name__':'detail_library'};exec(compile(code,str(detail),'exec'),de);de['H']=H
reset2=de['reset'];mesh2=de['mesh'];box2=de['box'];cyl2=de['cyl'];tube2=de['tube'];export2=de['export']
portal=[]
for t in ts:
    if 'C01' in (t['a'],t['b']):
        other=next(r for r in rooms if r['id']==(t['b'] if t['a']=='C01' else t['a']))
        portal.append(math.degrees(math.atan2(-(other['v']-10),other['x']+15))%360)
reset2()
def near_portal(deg,margin=17):return min(abs((deg-a+180)%360-180) for a in portal)<margin
# Real curved panel thickness with 3 mm bevels. Gaps are joints, not protruding walls.
for lo,hi in [(0.04,1.27),(1.30,2.60),(2.63,3.98),(4.01,5.4),(5.43,6.8),(6.83,8.1),(8.13,9.3)]:
    for deg in range(5,360,10):
        if lo<4.01 and near_portal(deg):continue
        vs=[];nx=5;ny=4
        for depth in [0,.024]:
            for j in range(ny+1):
                y=lo+(hi-lo)*j/ny;rad=math.sqrt(100-y*y)-.04-depth
                for k in range(nx+1):
                    a=math.radians(deg-4.9+9.8*k/nx);vs.append((rad*math.cos(a),y,rad*math.sin(a)))
        n=(nx+1)*(ny+1);fs=[]
        for j in range(ny):
            for k in range(nx):
                q=j*(nx+1)+k;fs.extend([(q,q+1,q+nx+2,q+nx+1),(n+q,n+q+nx+1,n+q+nx+2,n+q+1)])
        edge=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,ny+1)]+[ny*(nx+1)+k for k in range(nx-1,-1,-1)]+[j*(nx+1) for j in range(ny-1,0,-1)]
        for a,b in zip(edge,edge[1:]+edge[:1]):fs.append((a,b,n+b,n+a))
        mesh2('Curved_Clinical_Panel',vs,fs,'Coat',.003,True)
export2('AF_C01_CurvedLining')
reset2()
# C01 ribs now use continuous, eight-way symmetric geometry.
# The targeted tool also preserves the original AF model name and output path.
import runpy
runpy.run_path(str(R/'SourceAssets/C01_Finish/build_ribs.py'),run_name='__main__')
de['manifest']['AF_C01_ThreePortalRibs']=json.loads((R/'SourceAssets/C01_Finish/rib_geometry.json').read_text('utf-8'))
reset2()
# A low, flush measurement ring and four sensor posts inside the observation pod.
for deg in range(0,360,5):
    a,b=math.radians(deg),math.radians(deg+4.6)
    tube2('Measurement_Ring',[(2.55*math.cos(a),.012,2.55*math.sin(a)),(2.55*math.cos(b),.012,2.55*math.sin(b))],.009,'Dark')
for deg in [45,135,225,315]:
    a=math.radians(deg);x,z=2.85*math.cos(a),2.85*math.sin(a)
    box2('Sensor_Foot',x,.025,z,.32,.05,.32,'Steel',.007)
    cyl2('Sensor_Column',(x,.05,z),(x,1.55,z),.035,'Steel')
    box2('Sensor_Head',x,1.53,z,.22,.18,.16,'Coat',.008)
    cyl2('Sensor_Lens',(x,1.53,z-.085),(x,1.53,z-.095),.045,'Dark')
    for dx in [-.11,.11]:
        for dz in [-.11,.11]:cyl2('Foot_Bolt',(x+dx,.05,z+dz),(x+dx,.064,z+dz),.012,'Steel',6)
export2('AF_C01_MeasurementRig')
reset2()
from mathutils import Vector
for t in ts:
    for rid,end,other in [(t['a'],t['p'],t['q']),(t['b'],t['q'],t['p'])]:
        r=next(r for r in rooms if r['id']==rid)
        p=Vector((end[0]-r['x'],0,-end[1]+r['v']));q=Vector((other[0]-r['x'],0,-other[1]+r['v']))
        fw=(q-p).normalized();right=Vector((fw.z,0,-fw.x));vs=[];count=49;spring=t['h']-t['w']/2
        for sphere_r in [r['r']-.08,r['r']-.03]:
            for profile_r in [t['w']/2-.018,t['w']/2+.22]:
                for i in range(count):
                    a=math.pi*i/(count-1);cross=profile_r*math.cos(a);y=spring+profile_r*math.sin(a);u=p+right*cross;d=u.dot(fw)
                    along=-d+math.sqrt(max(0,d*d+sphere_r*sphere_r-y*y-u.length_squared));pt=u+fw*along;vs.append((r['x']+pt.x,y,-r['v']+pt.z))
        fs=[];k=count
        for i in range(k-1):fs.extend([(i,i+1,k+i+1,k+i),(2*k+i,3*k+i,3*k+i+1,2*k+i+1),(i,2*k+i,2*k+i+1,i+1),(k+i,k+i+1,3*k+i+1,3*k+i)])
        fs.extend([(0,k,3*k,2*k),(k-1,3*k-1,4*k-1,2*k-1)])
        mesh2(t['id']+'_'+rid+'_PortalCollar',vs,fs,'Coat',.004,True)
export2('AF_B5_PortalCollars')
(H/'geometry_manifest.json').write_text(json.dumps(dict(shell=shell_manifest,details=de['manifest'],portals_deg=portal),ensure_ascii=False,indent=2),encoding='utf-8')
