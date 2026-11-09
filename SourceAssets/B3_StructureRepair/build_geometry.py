import sys,runpy,copy,json,math
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
base=runpy.run_path(str(R/'SourceAssets/B3_FullFloor/common.py'))
for k,v in base.items():
 if not k.startswith('_') and k not in ['H','R','save']:globals()[k]=v
b.H=H;b.manifest={}
def save(name,category='Environment'):
 if name.endswith('_Floor'):return
 b.OUT=b.A/category/'B3';b.raw_export('BR_B3_'+name);b.manifest['BR_B3_'+name]['category']=category
 (H/'models.json').write_text(json.dumps(b.manifest,indent=2),encoding='utf-8')
plan=json.loads((H/'layout_route.json').read_text(encoding='utf-8'));rooms={r['id']:r for r in plan['rooms']};ts=plan['tunnels']
src=(R/'SourceAssets/B3_FullFloor/architecture.py').read_text(encoding='utf-8')
src=src[src.index("for r in plan['rooms']:"):src.index("for t in ts:\n code=")]
src=src.replace("for r in plan['rooms']:","for r in [r for r in plan['rooms'] if r['id'] in ['C03','C04']]:",1)
src=src.replace("  q=dict(t);", "  t=copy.deepcopy(t)\n  if t['id']=='B3-T08':\n   if code=='C03': t['p'],t['q']=t['path'][0],t['path'][1]\n   else: t['p'],t['q']=t['path'][-2],t['path'][-1]\n  q=dict(t);")
# Sweep cutters need to reach through the whole wall; endpoint directions are exact.
src=src.replace("extend=4)","extend=5)")
exec(compile(src,'room_repairs','exec'))
t=next(t for t in ts if t['id']=='B3-T08');path=t['path']
def offset(i,cross,y):
 a=path[max(0,i-1)];q=path[min(len(path)-1,i+1)];dx=q[0]-a[0];dv=q[1]-a[1];L=math.hypot(dx,dv)
 return (path[i][0]-dv/L*cross,y,-path[i][1]-dx/L*cross)
def sweep_curve(name,pad=0):
 w=2.1+pad;prof=[(-w,-.5-pad),(w,-.5-pad),(w,1.3)]+[(w*math.cos(math.pi*j/32),1.3+w*math.sin(math.pi*j/32)) for j in range(1,33)]
 vs=[offset(i,x,y) for i in range(len(path)) for x,y in prof];n=len(prof);fs=[tuple(reversed(range(n))),tuple(range((len(path)-1)*n,len(path)*n))]
 for i in range(len(path)-1):
  for j in range(n):fs.append((i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j))
 o=mesh(name,vs,fs,'Coat',0);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();return o
def ribbon(name,x0,x1,y0,y1,mat):
 prof=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)];vs=[offset(i,x,y) for i in range(len(path)) for x,y in prof];n=4;fs=[(3,2,1,0),tuple(range((len(path)-1)*4,len(path)*4))]
 for i in range(len(path)-1):
  for j in range(4):fs.append((i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j))
 o=mesh(name,vs,fs,mat,.003);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();return o
reset();shell_mats();outer=sweep_curve('Curved_Vault_Outer',.18);inner=sweep_curve('Curved_Vault_Interior')
# Move the end caps outwards without changing the bend shape.
for end,neighbor in [(0,1),(-1,-2)]:
 d=Vector(path[end])-Vector(path[neighbor]);d.normalize();delta=Vector((d.x*.6,d.y*.6,0))
 start=0 if end==0 else (len(path)-1)*35
 for v in inner.data.vertices[start:start+35]:v.co+=delta
cut(outer,inner)
for rid in ['C03','C04']:
 r=rooms[rid];cut(outer,env['sphere']('Dome_Clearance',r['x'],r['v'],r['r']))
be=outer.modifiers.new('Opening_Bevel','BEVEL');be.width=.006;be.segments=2;be.limit_method='ANGLE'
floor=ribbon('Curved_Floor',-2.1,2.1,-.30,0,'Floor')
for rid in ['C03','C04']:
 r=rooms[rid];cut(floor,cyl('Floor_Seam_Cut',(r['x'],-1,-r['v']),(r['x'],1,-r['v']),r['r']-.005,'Dark',128))
save('T08_Shell')
reset()
for side in [-1,1]:
 ribbon('Continuous_Wall_Bumper',side*2.02-.0325,side*2.02+.0325,.74,.86,'Steel')
 ribbon('Continuous_Drain',side*1.91-.05,side*1.91+.05,.002,.013,'Dark')
for x in [-.55,.55]:tube('Overhead_Conduit',[offset(i,x,3.24) for i in range(len(path))],.026,'Steel')
dist=0;last=-2
for i in range(1,len(path)-1):
 dist+=math.dist(path[i-1],path[i])
 if dist-last<1.8:continue
 last=dist
 for side in [-1,1]:
  for j in [-.04,0,.04]:
   a=offset(i,side*1.91+j,.017);cyl('Drain_Grid',a,(a[0],a[1],a[2]+.09),.005,'Steel',4)
 a=offset(i,-.61,3.26);q=offset(i,.61,3.26);cyl('Conduit_Hanger',a,q,.014,'Steel',10)
save('T08_Finish')
print('B3 structural replacement meshes complete',flush=True)
