import sys,importlib.util,json,math,bpy,bmesh
from pathlib import Path
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;R=H.parents[1]
s=importlib.util.spec_from_file_location('factory_helpers',R/'SourceAssets/B4_FullFloor/common.py');base=importlib.util.module_from_spec(s);s.loader.exec_module(base)
for k,v in vars(base).items():
 if not k.startswith('_') and k not in ['H','R','save']:globals()[k]=v
b.H=H;b.manifest=json.loads((H/'models.json').read_text()) if (H/'models.json').exists() else {}
def reset():
 b.reset()
 for n,c in [('Plate',(.25,.29,.32,1)),('RedLamp',(.8,.055,.035,1))]:
  m=bpy.data.materials.new('B2M_'+n);m.diffuse_color=c;b.mats[n]=m
 for i in range(7,11):
  m=bpy.data.materials.new('B4O_Display_%02d'%i);b.mats['Display_%02d'%i]=m
def save(n,category='Environment'):
 b.OUT=b.A/category/'B2';b.raw_export('BC_'+n);b.manifest['BC_'+n]['category']=category
 (H/'models.json').write_text(json.dumps(b.manifest,indent=2),encoding='utf-8')
def tube(name,pts,r,mat='Dark'):
 if len(pts)>2 and len(pts)<18 and r>=.03:
  v=[Vector(p) for p in pts];out=[v[0]]
  for i in range(1,len(v)-1):
   a,c=v[i]-v[i-1],v[i+1]-v[i];d=min(.40,a.length*.35,c.length*.35)
   if a.length<.0001 or c.length<.0001:continue
   p=v[i]-a.normalized()*d;q=v[i]+c.normalized()*d;out.append(p)
   for j in range(1,9):
    t=j/8;out.append((1-t)**2*p+2*(1-t)*t*v[i]+t*t*q)
  out.append(v[-1]);pts=[tuple(p) for p in out]
 return b.tube(name,pts,r,mat)
def flange(x,y,z,r=.13,axis='z'):
 a=[x,y,z];c=[x,y,z];j={'x':0,'y':1,'z':2}[axis];a[j]-=.035;c[j]+=.035
 cyl('Flange',a,c,r*1.6,'Steel',32)
 a[j]-=.006;c[j]=a[j]+.006;cyl('Gasket',a,c,r*1.52,'Rubber',32)
 for i in range(8):
  p=[x,y,z];t=math.tau*i/8;axes=[k for k in range(3) if k!=j];p[axes[0]]+=r*1.3*math.cos(t);p[axes[1]]+=r*1.3*math.sin(t);q=p.copy();p[j]-=.048;q[j]+=.048;cyl('FlangeBolt',p,q,.014,'Steel',6)
def valve(x,y,z,r=.10):
 cyl('ValveBody',(x,y,z-.14),(x,y,z+.14),r*1.35,'Red',24);flange(x,y,z-.18,r);flange(x,y,z+.18,r)
 cyl('ValveStem',(x,y,z),(x,y+.3,z),.027,'Steel',12)
 tube('Handwheel',[(x+.18*math.cos(math.tau*i/32),y+.32,z+.18*math.sin(math.tau*i/32)) for i in range(33)],.017,'Red')
 for i in range(3):
  a=math.tau*i/3;cyl('WheelSpoke',(x,y+.32,z),(x+.16*math.cos(a),y+.32,z+.16*math.sin(a)),.012,'Steel',10)
def gauge(x,y,z):
 cyl('PressureGauge',(x,y,z-.045),(x,y,z),.105,'Steel',32);cyl('DialFace',(x,y,z+.001),(x,y,z+.006),.090,'Paper',40)
 for i in range(13):
  a=math.radians(-220+260*i/12);cyl('Tick',(x+.072*math.cos(a),y+.072*math.sin(a),z+.009),(x+.084*math.cos(a),y+.084*math.sin(a),z+.009),.0015,'Dark',6)
 cyl('DialNeedle',(x,y,z+.014),(x-.045,y+.048,z+.014),.002,'Red',8)
 cyl('DialStem',(x,y-.20,z-.035),(x,y-.08,z-.035),.015,'Steel',10)
def rail(a,c):
 dx,dz=c[0]-a[0],c[1]-a[1];L=math.hypot(dx,dz);n=math.ceil(L/1.4)
 for i in range(n+1):
  x=a[0]+dx*i/n;z=a[1]+dz*i/n;cyl('GuardPost',(x,3.60,z),(x,4.70,z),.025,'Steel',12);box('PostFoot',x,3.61,z,.12,.02,.12,'Steel',.003)
 for y,th in [(4.70,.032),(4.15,.020)]:cyl('GuardRail',(a[0],y,a[1]),(c[0],y,c[1]),th,'Steel',16)
 old=set(bpy.context.scene.objects);box('ToeBoard',0,3.68,L/2,.03,.15,L,'Steel',.004);transform(set(bpy.context.scene.objects)-old,a[0],0,a[1],math.degrees(math.atan2(dx,dz)))
