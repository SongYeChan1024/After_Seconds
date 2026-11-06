"""기존 곡면 벽 타일의 출입구 누락 부분만 제작. 작성자: 송예찬."""
from pathlib import Path
import math,json
import bpy
H=Path(__file__).resolve().parent;R=H.parents[1]
lib=R/'SourceAssets/B5_Sector01/build_details.py';e={'__file__':str(lib),'__name__':'tile_library'}
code=lib.read_text('utf-8').split('# Structural ribs')[0]
code=code.replace('bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me)',"bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<5e-9],context='FACES');bm.to_mesh(me)")
exec(compile(code,str(lib),'exec'),e);e['H']=H;e['reset']()
f=next(f for f in json.loads((R/'Docs/도면/Decision/원형공동/facility_layout.json').read_text('utf-8'))['floors'] if f['id']=='B5')
portals=[]
for t in f['tunnels']:
 if 'C01' not in [t['a'],t['b']]:continue
 other=next(r for r in f['rooms'] if r['id']==(t['b'] if t['a']=='C01' else t['a']))
 portals.append(dict(id=t['id'],angle=math.degrees(math.atan2(-(other['v']-10),other['x']+15))%360))
cutters=[]
for p in portals:
 a=math.radians(p['angle']);fw=(math.cos(a),math.sin(a));rt=(fw[1],-fw[0]);rad=2.12
 profile=[(-rad,-.1),(rad,-.1),(rad,1.3)]+[(rad*math.cos(math.pi*i/64),1.3+rad*math.sin(math.pi*i/64)) for i in range(1,65)]
 vs=[(fw[0]*z+rt[0]*x,y,fw[1]*z+rt[1]*x) for z in [7.8,12] for x,y in profile];k=len(profile)
 fs=[tuple(range(k-1,-1,-1)),tuple(range(k,2*k))]+[(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)]
 cutters.append(e['mesh']('CUT_'+p['id'],vs,fs,'Coat',0))
panels=[]
for lo,hi in [(0.04,1.27),(1.30,2.60),(2.63,3.98)]:
 for deg in range(5,360,10):
  close=[i for i,p in enumerate(portals) if abs((deg-p['angle']+180)%360-180)<17]
  if not close:continue
  vs=[];nx=8;ny=6
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
  o=e['mesh']('CutToArch_Tile_'+str(deg)+'_'+str(lo),vs,fs,'Coat',0,True)
  for i in close:
   bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Actual_Arched_Opening','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutters[i];bpy.ops.object.modifier_apply(modifier=m.name)
  if not o.data.polygons:bpy.data.objects.remove(o,do_unlink=True);continue
  be=o.modifiers.new('Tile_Edge_3mm','BEVEL');be.width=.003;be.segments=3;be.limit_method='ANGLE';be.angle_limit=.45;be.harden_normals=True
  wn=o.modifiers.new('Weighted_Normal','WEIGHTED_NORMAL');wn.keep_sharp=True;o['bevel_width_m']=.003
  panels.append(dict(name=o.name,lo=lo,hi=hi,angle=deg,portals=[portals[i]['id'] for i in close]))
for o in cutters:bpy.data.objects.remove(o,do_unlink=True)
e['export']('AF_C01_PortalTileInfill')
(H/'geometry.json').write_text(json.dumps(dict(author='송예찬',portals=portals,panels=panels,model=e['manifest']['AF_C01_PortalTileInfill'],existingWallUnchanged=True),ensure_ascii=False,indent=2),encoding='utf-8')
print('PORTAL_TILE_PANELS',len(panels))
