"""Original weathered rock and dry scrub geometry in Unity metres."""
import sys,os,math,random,json,bpy,bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.noise import noise_vector
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'F1_RoofLiftWilderness'))
from meshlib import Model as Base
OUT=Path(os.environ['LOCALAPPDATA'])/'Temp/AfterSeconds_WildernessDetail_20261113/candidate'
OUT.mkdir(parents=True,exist_ok=True)
class Model(Base):
 def export(self,kind):
  bpy.ops.wm.read_factory_settings(use_empty=True);me=bpy.data.meshes.new(self.name+'_LOD0');me.from_pydata([(-x,-z,y) for x,y,z in self.v],[],self.f);me.update()
  for n in self.m:me.materials.append(bpy.data.materials.new('WD_M_'+n))
  for f,i in zip(me.polygons,self.fm):f.material_index=i
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.0000001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
  me.uv_layers.new(name='UVMap')
  for f in me.polygons:
   f.use_smooth=kind in ['Rock','Shrub']
   axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(f.normal[i]))]
   for li in f.loop_indices:
    v=me.vertices[me.loops[li].vertex_index].co;me.uv_layers.active.data[li].uv=(v[axes[0]],v[axes[1]])
  assert not any(f.area<1e-12 for f in me.polygons),self.name
  tri=[]
  for i,ratio in enumerate([1,.42,.15]):
   mm=me if i==0 else me.copy();o=bpy.data.objects.new(self.name+'_LOD'+str(i),mm);bpy.context.collection.objects.link(o);o.select_set(True);bpy.context.view_layer.objects.active=o
   if i:
    mod=o.modifiers.new('Distance detail','DECIMATE');mod.ratio=ratio;bpy.ops.object.modifier_apply(modifier=mod.name)
   o.data.name=o.name;tri.append(len(o.data.polygons))
  bpy.ops.export_scene.fbx(filepath=str(OUT/(self.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE')
  return dict(name=self.name,kind=kind,triangles=tri,materials=['WD_M_'+n for n in self.m],zeroArea=0,boundsMin=[min(v[i] for v in self.v) for i in range(3)],boundsMax=[max(v[i] for v in self.v) for i in range(3)])

def rock(m,seed,center=(0,0,0),size=(1,.72,.85),sub=3,mat='Stone'):
 bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=sub,radius=1);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table();vv=[]
 offset=Vector((seed*.193,seed*.427,seed*.311))
 for v in bm.verts:
  p=v.co;wide=noise_vector(p*2.1+offset)[0];small=noise_vector(p*6.7+offset)[1];shape=1+wide*.19+small*.045
  x,z=p.x*shape*size[0],p.z*shape*size[2]
  # Buried base, weathered shoulders, localized fracture ledges.
  y=.32+p.y*.65*shape
  y=min(y,.87+.08*math.sin(x*1.9+seed)+.055*z)
  x*=1-.06*math.sin(y*17+z*2+seed)
  vv.append((center[0]+x,center[1]+max(-.16,y)*size[1],center[2]+z))
 m.add(vv,[tuple(v.index for v in f.verts) for f in bm.faces],mat);bm.free()

def blade(m,rng,root,h,w,angle,lean,mat='Straw'):
 x,y,z=root;dx,dz=math.cos(angle),math.sin(angle);nx,nz=-dz,dx;vs=[]
 for i in range(5):
  t=i/4;bend=lean*t*t;yy=h*(t-.14*t*t);ww=w*(1-t)*(.85+.15*math.sin(t*math.pi))+.00025
  for side in [-1,1]:vs.append((x+dx*bend+nx*ww*side,y+yy,z+dz*bend+nz*ww*side))
 m.add(vs,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(4)],mat)
def seedstalk(m,rng,root,h,angle):
 x,y,z=root;dx,dz=math.cos(angle),math.sin(angle);points=[(x+dx*.12*t*t,y+h*t,z+dz*.12*t*t) for t in [0,.3,.6,.82,1]]
 for i,(a,b) in enumerate(zip(points,points[1:])):m.beam(a,b,.0034*(1-i*.17),'Straw',4)
 for j in range(6):
  t=.69+j*.045;c=Vector((x+dx*.12*t*t,y+h*t,z+dz*.12*t*t));a=angle+j*2.399;tip=c+Vector((math.cos(a)*.035,.055,math.sin(a)*.035));m.beam(c,tip,.002,'Seed',4)
  side=Vector((math.sin(a)*.008,0,-math.cos(a)*.008));m.add([tuple(c-side),tuple(c+side),tuple(tip)],[(0,1,2)],'Seed')

reports=[]
for i in range(3):
 m=Model('WD_Rock'+chr(65+i));rock(m,79+i*17,size=[(1.02,.96,.86),(.95,.69,1.02),(1.08,.87,.75)][i]);reports.append(m.export('Rock'))
for i in range(4):
 rng=random.Random(193+i);m=Model('WD_Grass'+chr(65+i))
 for tuft in range(4 if i<3 else 6):
  a=rng.random()*math.tau;r=rng.uniform(.08,.75);x,z=math.cos(a)*r,math.sin(a)*r
  for j in range(rng.randint(12,23)):
   angle=rng.random()*math.tau;h=rng.uniform(.16,.46)*(1.3 if i==1 else .7 if i==3 else 1);root=(x+rng.uniform(-.07,.07),-.035,z+rng.uniform(-.07,.07));blade(m,rng,root,h,rng.uniform(.004,.011),angle,rng.uniform(.08,.26),rng.choice(['Straw','Straw','Faded','Sage']))
  if i!=3:
   for j in range(rng.randint(2,4)):seedstalk(m,rng,(x,-.02,z),rng.uniform(.35,.69),rng.random()*math.tau)
 reports.append(m.export('Grass'))
for i in range(3):
 rng=random.Random(937+i);m=Model('WD_Shrub'+chr(65+i));height=[.72,.44,1.0][i];spread=[.45,.7,.36][i]
 for limb in range(7):
  angle=limb*2.399+rng.uniform(-.4,.4);dx,dz=math.cos(angle),math.sin(angle);hh=height*rng.uniform(.65,1.05);rad=spread*rng.uniform(.6,1.1)
  pts=[Vector((dx*rad*t*t,hh*t-.03,dz*rad*t*t)) for t in [0,.27,.55,.80,1]]
  for j in range(4):m.beam(pts[j],pts[j+1],.016*(1-j*.19),'Twig',6)
  for branch in range(4):
   start=pts[1+branch//2];a=angle+rng.uniform(-1.7,1.7);end=start+Vector((math.cos(a)*rng.uniform(.12,.3),hh*rng.uniform(.2,.5),math.sin(a)*rng.uniform(.12,.3)));mid=start.lerp(end,.55)+Vector((0,.045,0))
   m.beam(start,mid,.007,'Twig',5);m.beam(mid,end,.0035,'Twig',5)
   if i<2 or branch%2==0:
    for k in range(4):
     c=mid.lerp(end,.25+k*.2);side=Vector((math.cos(a+1.2)*.026,.006,math.sin(a+1.2)*.026));tip=c+Vector((math.cos(a)*.045,.027,math.sin(a)*.045));m.add([tuple(c-side*.25),tuple(c+side),tuple(tip),tuple(c-side)],[(0,1,2,3)],rng.choice(['Sage','Faded','Straw']))
 reports.append(m.export('Shrub'))
for i in range(2):
 rng=random.Random(828+i);m=Model('WD_StonePatch'+chr(65+i))
 for j in range(22):
  a=rng.random()*math.tau;r=rng.random()**.6*.85;s=rng.uniform(.018,.085);rock(m,50+j,(math.cos(a)*r,-.01,math.sin(a)*r),(s,s*rng.uniform(.3,.8),s*.7),sub=1,mat='Gravel' if j%3 else 'Stone')
 reports.append(m.export('Pebbles'))
(H/'models.json').write_text(json.dumps(reports,indent=2),encoding='utf8');print('WILDERNESS_MODELS_READY',len(reports),sum(r['triangles'][0] for r in reports))
