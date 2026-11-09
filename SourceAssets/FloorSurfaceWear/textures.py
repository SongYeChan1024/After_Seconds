"""Seamless resin surfacing and local cargo wear maps. Author Song Ye Chan."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
H=Path(__file__).resolve().parent;R=H.parents[1];OUT=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/Common/Textures';OUT.mkdir(parents=True,exist_ok=True)
N=2048
def periodic(rng,n,scale):
 a=rng.normal(0,1,(n,n)).astype('float32');a=np.pad(a,((1,1),(1,1)),mode='wrap')
 im=Image.fromarray(a).resize((N+2*N//n,N+2*N//n),Image.Resampling.BICUBIC)
 return np.asarray(im)[N//n:N//n+N,N//n:N//n+N]*scale
def save(n,arr):Image.fromarray(np.uint8(np.clip(arr,0,255))).save(OUT/(n+'.png'))
def normals(height,strength):
 dx=(np.roll(height,-1,1)-np.roll(height,1,1))*strength;dy=(np.roll(height,-1,0)-np.roll(height,1,0))*strength
 nz=np.ones_like(dx);v=np.stack([-dx,dy,nz],axis=-1);v/=np.linalg.norm(v,axis=-1,keepdims=True);return (v*.5+.5)*255
for f,seed in [('B5',5136),('B4',4136)]:
 rng=np.random.default_rng(seed);large=periodic(rng,12,1.1)+periodic(rng,42,.7);fine=rng.normal(0,.85,(N,N));grain=periodic(rng,256,.9)
 x=np.arange(N)[None,:];y=np.arange(N)[:,None]
 # Two-metre construction joints, only a few pixels wide, low contrast.
 dx=np.minimum(x%(N//2),N//2-x%(N//2));dy=np.minimum(y%(N//2),N//2-y%(N//2))
 seam=np.maximum(np.exp(-(dx/1.0)**2),np.exp(-(dy/1.0)**2))
 micro=rng.random((N,N));flakes=np.where(micro>.998,5,np.where(micro<.004,-5,0))
 color=232+large+fine+grain+flakes-seam*7
 rgb=np.stack([color,color+.15,color+.35],axis=-1);save('FW_'+f+'_Base',rgb)
 smooth=78+large*1.2+grain*2-seam*10
 ms=np.zeros((N,N,4),dtype=np.float32);ms[:,:,0]=4;ms[:,:,3]=smooth;save('FW_'+f+'_MetalSmooth',ms)
 height=grain*.008+fine*.003-seam*.22;save('FW_'+f+'_Normal',normals(height,.55))

rng=np.random.default_rng(9237)
for kind in ['CargoFloor','CargoWall','CargoEdge']:
 base=periodic(rng,18,1.7)+periodic(rng,90,1.2)+rng.normal(0,1.1,(N,N))
 marks=Image.new('L',(N,N));d=ImageDraw.Draw(marks)
 scratches=Image.new('L',(N,N));sd=ImageDraw.Draw(scratches)
 if kind=='CargoFloor':
  # Segmented, overlapping cart passes; no painted lanes.
  for track in [.22,.36,.64,.79]:
   for j in range(45):
    u=track+rng.uniform(-.025,.025);v=rng.uniform(.08,.94);length=rng.uniform(.015,.16)
    d.line([(u*N,v*N),((u+rng.uniform(-.008,.008))*N,min(.96,v+length)*N)],fill=int(rng.integers(8,48)),width=int(rng.integers(5,22)))
  for j in range(150):
   u,v=rng.uniform(.06,.94),rng.uniform(.10,.96);sd.line([(u*N,v*N),((u+rng.uniform(-.06,.06))*N,(v+rng.uniform(-.02,.02))*N)],fill=int(rng.integers(8,50)),width=int(rng.integers(1,3)))
 elif kind=='CargoWall':
  # Bottom 1.3m carries the impacts; the upper wall remains maintained.
  for j in range(210):
   u=rng.uniform(.03,.97);v=rng.uniform(.67,.98);length=rng.uniform(.004,.055)
   d.line([(u*N,v*N),((u+length)*N,(v+rng.uniform(-.005,.005))*N)],fill=int(rng.integers(6,58)),width=int(rng.integers(2,10)))
  for j in range(120):
   u=rng.uniform(.02,.98);v=rng.uniform(.67,.97)
   sd.line([(u*N,v*N),((u+rng.uniform(.004,.028))*N,(v+rng.uniform(-.006,.006))*N)],fill=int(rng.integers(12,60)),width=int(rng.integers(1,4)))
 else:
  for j in range(300):
   u,v=rng.uniform(0,1),rng.uniform(0,1);sd.line([(u*N,v*N),((u+rng.uniform(.004,.035))*N,(v+rng.uniform(-.003,.003))*N)],fill=int(rng.integers(5,55)),width=int(rng.integers(1,3)))
  for j in range(50):
   u,v=rng.uniform(0,1),rng.uniform(0,1);d.ellipse((u*N,v*N,(u+.03)*N,(v+.005)*N),fill=14)
 wear=np.asarray(marks.filter(ImageFilter.GaussianBlur(1.3))).astype(float);scuff=np.asarray(scratches.filter(ImageFilter.GaussianBlur(.3))).astype(float)
 c=230+base-wear*.75+scuff*.26
 save('FW_'+kind+'_Base',np.stack([c,c-.25,c-.6],axis=-1))
 ms=np.zeros((N,N,4));ms[:,:,0]=np.clip((155 if kind!='CargoWall' else 30)+scuff*2,0,235);ms[:,:,3]=np.clip(95+scuff*.7-wear*.75+base,35,150);save('FW_'+kind+'_MetalSmooth',ms)
 save('FW_'+kind+'_Normal',normals(base*.003-wear*.012-scuff*.005,.6))
print('Generated 15 PBR maps at 2048 x 2048')
