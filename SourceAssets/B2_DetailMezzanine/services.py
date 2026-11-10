"""B2 upper process lines and distinctive industrial luminaires. Author 송예찬."""
import sys,json,math
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(R/'SourceAssets/B2_FullFloor'))
from common import *
H=Path(__file__).resolve().parent;b.H=H;b.manifest=json.loads((H/'models.json').read_text(encoding='utf8'))
plan=json.loads((H/'layout.json').read_text(encoding='utf8'))
def save(n):
 b.OUT=b.A/'Environment/B2';b.raw_export('BD_'+n);b.manifest['BD_'+n]['category']='Environment';(H/'models.json').write_text(json.dumps(b.manifest,indent=2),encoding='utf8')
for t in plan['tunnels']:
 reset();ps=[Vector((p[0],0,-p[1])) for p in t['path']];L=t['length'];positions=[]
 for x,y,r,mat in [(-1.30,2.95,.15,'Steel'),(1.30,2.90,.12,'Steel'),(-1.32,3.30,.065,'PipeRed'),(1.32,3.30,.045,'Dark')]:
  # Both ends bend down into the lower side-wall service circuits.
  pp=[]
  for d in [4.1+1.4*i/16 for i in range(16)]+[5.5+i*(L-11)/max(1,math.ceil((L-11)/.5)) for i in range(max(1,math.ceil((L-11)/.5))+1)]+[L-5.5+1.4*i/16 for i in range(1,17)]:
   p,di=at(ps,d);rr=Vector((di.z,0,-di.x));fac=max(0,min(1,(d-4.1)/1.4,(L-4.1-d)/1.4));fac=fac*fac*(3-2*fac);xx=(2.28 if x>0 else -2.28)*(1-fac)+x*fac;yy=1.62*(1-fac)+y*fac;pp.append(tuple(p+rr*xx+Vector((0,yy,0))))
  tube('UpperProcessMain' if r>.1 else 'SignalAndReturnLine',pp,r,mat)
 # Every six metres: gasketed pipe joints and channel brackets bolted to the shell.
 for d in [6.2+i*6 for i in range(max(1,int((L-12.4)/6)+1))]:
  if d>L-5.6:continue
  p,di=at(ps,d);old=set(bpy.context.scene.objects)
  for x,y,r in [(-1.30,2.95,.15),(1.30,2.90,.12)]:
   flange(x,y,0,r,'z');box('PipeSaddle',x,y-r-.035,0,.40,.07,.24,'Steel',.008)
   side=1 if x>0 else -1;box('WallChannel',side*1.97,2.88,0,.07,.42,.30,'Steel',.006);box('Cantilever',side*1.64,2.72,0,.66,.09,.085,'Steel',.006)
   for yy in [2.75,3.02]:
    cyl('WallAnchor',(side*1.91,yy,-.10),(side*2.02,yy,-.10),.021,'Steel',6)
  transform(set(bpy.context.scene.objects)-old,p.x,0,p.z,math.degrees(math.atan2(di.x,di.z)))
 # Local isolation/pressure check points, facing the crouching maintenance aisle.
 for k,d in enumerate([max(6.2,min(L/2,L-6.2))]):
  p,di=at(ps,d);old=set(bpy.context.scene.objects)
  for side in [-1,1]:
   # Valve stem and readable analogue dial sit outside the 1.5m clear deck.
   cyl('IsolationValve',(side*1.30,2.90,-.18),(side*1.30,2.90,.18),.18,'Red',24)
   cyl('ValveStem',(side*1.30,2.90,0),(side*.98,2.90,0),.025,'Steel',12)
   tube('IsolationHandwheel',[(side*.97,2.90+.13*math.cos(math.tau*j/32),.13*math.sin(math.tau*j/32)) for j in range(33)],.013,'Red')
   for j in range(3):
    a=math.tau*j/3;cyl('WheelSpoke',(side*.97,2.90,0),(side*.97,2.90+.12*math.cos(a),.12*math.sin(a)),.008,'Steel',8)
   oldg=set(bpy.context.scene.objects);gauge(0,3.18,0);transform(set(bpy.context.scene.objects)-oldg,side*1.04,0,.35,-90 if side>0 else 90)
  transform(set(bpy.context.scene.objects)-old,p.x,0,p.z,math.degrees(math.atan2(di.x,di.z)))
 save(t['id']+'_UpperProcessLines')
 print('UPPER_SERVICES',t['id'],flush=True)

reset()
cyl('CastBulkhead',(0,0,-.07),(0,0,.055),.23,'Dark',40)
cyl('SealRing',(0,0,.055),(0,0,.08),.215,'Rubber',40)
cyl('RedPrismaticLens',(0,0,.08),(0,0,.16),.18,'RedLamp',48)
for a in [0,math.pi/2,math.pi,math.pi*1.5]:
 x,y=.205*math.cos(a),.205*math.sin(a);cyl('CoverFastener',(x,y,.07),(x,y,.115),.019,'Steel',6)
tube('CastGuardRing',[(.203*math.cos(math.tau*i/48),.203*math.sin(math.tau*i/48),.18) for i in range(49)],.018,'Steel')
for x in [-.085,0,.085]:
 dy=math.sqrt(.19**2-x*x);tube('ProtectiveBar',[(x,-dy,.16),(x,-dy*.7,.205),(x,dy*.7,.205),(x,dy,.16)],.009,'Steel')
for y in [-.285,.285]:box('MountEar',0,y,-.04,.15,.18,.07,'Steel',.012);cyl('MountScrew',(0,y,-.003),(0,y,.02),.018,'Steel',6)
cyl('CableGland',(0,-.23,-.015),(0,-.37,-.015),.027,'Dark',12)
save('RoundBulkhead')

reset()
# Double-skinned flared metal shade, open underneath; all rolled rims are real geometry.
vs=[];fs=[];N=48
for y,r in [(.13,.16),(-.12,.39),(.12,.145),(-.115,.375)]:
 for i in range(N):a=math.tau*i/N;vs.append((r*math.cos(a),y,r*math.sin(a)))
for i in range(N):
 j=(i+1)%N;fs.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(N+i,N+j,3*N+j,3*N+i),(i,2*N+i,2*N+j,j)])
mesh('EnamelMetalShade',vs,fs,'Steel',.006,True)
cyl('LampSocket',(0,.08,0),(0,.26,0),.08,'Dark',24)
cyl('RedLampCore',(0,-.28,0),(0,.02,0),.105,'RedLamp',32)
for y in [-.30,-.18,-.06]:tube('CageRing',[(.155*math.cos(math.tau*i/40),y,.155*math.sin(math.tau*i/40)) for i in range(41)],.011,'Steel')
for i in range(8):
 a=math.tau*i/8;x,z=.155*math.cos(a),.155*math.sin(a);cyl('GuardRod',(x,-.30,z),(x,.02,z),.009,'Steel',8)
cyl('SuspensionStem',(0,.22,0),(0,.4,0),.025,'Steel',16)
save('ServicePendant')
reset()
for x in [-.07,.07]:cyl('SuspensionCable',(x,0,0),(x,1,0),.008,'Dark',10)
box('CeilingAnchor',0,1,0,.30,.025,.14,'Steel',.006)
save('PendantSuspension')
print('SERVICE_MODELS_COMPLETE',flush=True)
