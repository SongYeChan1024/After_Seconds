"""Clearly readable but maintained resin and freight wear; original PBR textures."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/Common/Textures';N=2048
def noise(rng,n):
 a=rng.normal(0,1,(n,n)).astype('float32');a=np.pad(a,((1,1),(1,1)),mode='wrap');step=N//n
 return np.asarray(Image.fromarray(a).resize((N+2*step,N+2*step),Image.Resampling.BICUBIC))[step:step+N,step:step+N]
def save(n,a):Image.fromarray(np.uint8(np.clip(a,0,255))).save(O/(n+'.png'))
def normal(h,scale=1):
 dx=(np.roll(h,-1,1)-np.roll(h,1,1))*scale;dy=(np.roll(h,-1,0)-np.roll(h,1,0))*scale;v=np.stack([-dx,dy,np.ones_like(h)],-1);v/=np.linalg.norm(v,axis=-1,keepdims=True);return (v*.5+.5)*255
for kind,seed in [('B5',5193),('B4',4193),('CargoFloor',7193),('CargoWall',7194),('CargoEdge',7195)]:
 rng=np.random.default_rng(seed);large=noise(rng,8)*4.2+noise(rng,32)*2.5;grain=noise(rng,256)*2.0+rng.normal(0,.9,(N,N));mask=Image.new('L',(N,N));draw=ImageDraw.Draw(mask);scar=Image.new('L',(N,N));sd=ImageDraw.Draw(scar);seam=np.zeros((N,N))
 if kind in ['B5','B4']:
  x=np.arange(N)[None,:];y=np.arange(N)[:,None];dx=np.minimum(x%(N//2),N//2-x%(N//2));dy=np.minimum(y%(N//2),N//2-y%(N//2));seam=np.maximum(np.exp(-(dx/2.0)**2),np.exp(-(dy/2.0)**2))
  for _ in range(105):
   x,y=rng.uniform(.06,.94,2)*N;length=rng.uniform(25,180);draw.line((x,y,x+length,y+rng.uniform(-35,35)),fill=int(rng.integers(12,45)),width=int(rng.integers(3,16)))
  for _ in range(55):
   x,y=rng.uniform(.06,.80,2)*N;w=rng.uniform(50,230);draw.arc((x,y,x+w,y+w*.7),int(rng.integers(0,100)),int(rng.integers(150,280)),fill=int(rng.integers(7,22)),width=3)
 elif kind=='CargoFloor':
  for lane in [.24,.68]:
   for _ in range(70):
    x=(lane+rng.uniform(-.025,.025))*N;y=rng.uniform(.06,.95)*N;length=rng.uniform(25,220);draw.line((x,y,x+rng.uniform(-22,22),y+length),fill=int(rng.integers(24,110)),width=int(rng.integers(8,34)))
  for _ in range(130):
   x,y=rng.uniform(.05,.95,2)*N;sd.line((x,y,x+rng.uniform(10,90),y+rng.uniform(-16,16)),fill=int(rng.integers(35,110)),width=int(rng.integers(1,5)))
 elif kind=='CargoWall':
  for _ in range(170):
   x=rng.uniform(.01,.98)*N;y=rng.uniform(.64,.99)*N;length=rng.uniform(8,160);draw.line((x,y,x+length,y+rng.uniform(-12,12)),fill=int(rng.integers(25,105)),width=int(rng.integers(4,20)))
  for _ in range(220):
   x=rng.uniform(.01,.98)*N;y=rng.uniform(.66,.99)*N;sd.line((x,y,x+rng.uniform(10,100),y+rng.uniform(-9,9)),fill=int(rng.integers(30,125)),width=int(rng.integers(1,4)))
 else:
  for _ in range(650):
   x,y=rng.uniform(0,1,2)*N;sd.line((x,y,x+rng.uniform(10,110),y+rng.uniform(-10,10)),fill=int(rng.integers(25,125)),width=int(rng.integers(1,5)))
  for _ in range(90):
   x,y=rng.uniform(0,1,2)*N;draw.ellipse((x,y,x+rng.uniform(5,45),y+rng.uniform(3,16)),fill=int(rng.integers(18,80)))
 # Thin intermittent abrasion has color/roughness, not deep stamped rectangles.
 # Break broad marks with multi-scale contamination and soften their endings.
 wear=np.asarray(mask.filter(ImageFilter.GaussianBlur(5 if 'Cargo' in kind else 2.8))).astype(float)
 wear*=np.clip(.65+noise(rng,128)*.35+noise(rng,512)*.18,.05,1.05)
 scratch=np.asarray(scar.filter(ImageFilter.GaussianBlur(.6))).astype(float)
 scratch*=np.clip(.55+noise(rng,256)*.5,0,1)
 if kind=='CargoWall':
  lower=np.clip((np.arange(N)[:,None]/N-.62)/.32,0,1)
  wear+=np.maximum(noise(rng,16)+.1,0)*lower*18
 if kind=='CargoEdge':
  wear+=np.maximum(noise(rng,24)-.35,0)*35
 c=224+large+grain-seam*24-wear*(1.65 if 'Cargo' in kind else .95)+scratch*(.80 if 'Cargo' in kind else .32)
 save('FM_'+kind+'_Base',np.stack([c,c+.2,c+.6],-1));ms=np.zeros((N,N,4));ms[:,:,0]=(5 if kind in ['B5','B4'] else 120 if kind=='CargoWall' else 175)+scratch*.5;ms[:,:,3]=np.clip(98+large*2+grain*2-seam*23-wear*.9+scratch*.55,20,180);save('FM_'+kind+'_MetalSmooth',ms)
 save('FM_'+kind+'_Normal',normal(grain*.008-seam*.23-wear*.0006-scratch*.0015,.6))
print('15 stronger surface maps created')
