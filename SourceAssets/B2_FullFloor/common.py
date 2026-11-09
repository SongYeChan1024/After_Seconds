import importlib.util,json,math,sys,bpy,bmesh
from pathlib import Path
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;R=H.parents[1]
s=importlib.util.spec_from_file_location('b2_cooling_helpers',R/'SourceAssets/B2_Cooling/common.py');q=importlib.util.module_from_spec(s);s.loader.exec_module(q)
for k,v in vars(q).items():
 if not k.startswith('_') and k not in ['H','R','reset','save']:globals()[k]=v
b.H=H;b.manifest=json.loads((H/'models.json').read_text()) if (H/'models.json').exists() else {}
def reset():
 q.reset()
 for i in range(11,25):
  m=bpy.data.materials.new('B4O_Display_%02d'%i);b.mats['Display_%02d'%i]=m
 for name,col in [('Pipe',(.32,.37,.41,1)),('PipeRed',(.24,.055,.04,1))]:
  m=bpy.data.materials.new('BM_'+name);m.diffuse_color=col;b.mats[name]=m
def save(n,category='Environment'):
 b.OUT=b.A/category/'B2';b.raw_export('BM_'+n);b.manifest['BM_'+n]['category']=category;(H/'models.json').write_text(json.dumps(b.manifest,indent=2),encoding='utf8')
def path_points(t,extend=0):
 ps=[Vector((p[0],0,-p[1])) for p in t.get('path',[t['p'],t['q']])]
 if extend:ps[0]-=(ps[1]-ps[0]).normalized()*extend;ps[-1]+=(ps[-1]-ps[-2]).normalized()*extend
 return ps
def frames(ps):
 return [Vector(((ps[min(i+1,len(ps)-1)]-ps[max(0,i-1)]).normalized().z,0,-(ps[min(i+1,len(ps)-1)]-ps[max(0,i-1)]).normalized().x)) for i in range(len(ps))]
def sweep(n,t,outer=2.5,inner=None,extend=0,mat='Pipe',segments=64):
 ps=path_points(t,extend);rights=frames(ps);vs=[];rings=[outer] if inner is None else [outer,inner];stride=len(ps)*segments
 for rad in rings:
  for p,rr in zip(ps,rights):
   for j in range(segments):
    a=math.tau*j/segments;v=p+rr*(rad*math.cos(a))+Vector((0,1.35+rad*math.sin(a),0));vs.append(tuple(v))
 fs=[]
 for k,rad in enumerate(rings):
  for i in range(len(ps)-1):
   for j in range(segments):
    a=k*stride+i*segments+j;bb=k*stride+i*segments+(j+1)%segments;fs.append((a,bb,bb+segments,a+segments))
 if inner is None:fs.extend([tuple(range(segments-1,-1,-1)),tuple(range(stride-segments,stride))])
 else:
  for i in [0,len(ps)-1]:
   for j in range(segments):
    a=i*segments+j;bb=i*segments+(j+1)%segments;fs.append((a,a+stride,bb+stride,bb))
 return mesh(n,vs,fs,mat,.004,True)
def ribbon(n,t,w=4.20,y0=-.22,y1=0,mat='Floor'):
 ps=path_points(t);rr=frames(ps);vs=[]
 for y in [y0,y1]:
  for p,v in zip(ps,rr):
   for sign in [-1,1]:vs.append(tuple(p+v*w*.5*sign+Vector((0,y,0))))
 count=len(ps)*2;fs=[]
 for i in range(len(ps)-1):
  a=i*2;fs.extend([(a,a+2,a+3,a+1),(count+a,count+a+1,count+a+3,count+a+2),(a,count+a,count+a+2,a+2),(a+1,a+3,count+a+3,count+a+1)])
 fs.extend([(0,1,count+1,count),(count-2,2*count-2,2*count-1,count-1)]);return mesh(n,vs,fs,mat,.002)
def at(ps,d):
 for i in range(1,len(ps)):
  L=(ps[i]-ps[i-1]).length
  if d<=L:return ps[i-1].lerp(ps[i],max(0,d/L)),(ps[i]-ps[i-1]).normalized()
  d-=L
 return ps[-1],(ps[-1]-ps[-2]).normalized()
