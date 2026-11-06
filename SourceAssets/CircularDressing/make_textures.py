from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter,ImageDraw
H=Path(__file__).resolve().parent;R=H.parents[1];OUT=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/Common/Textures';OUT.mkdir(exist_ok=True,parents=True)
N=1024
for i in range(4):
 rng=np.random.default_rng(719+i*113)
 field=np.zeros((N,N),np.float32)
 for res,weight in [(12,.5),(51,.3),(256,.2)]:
  im=Image.fromarray(np.uint8(rng.random((res,res))*255)).resize((N,N),Image.Resampling.BICUBIC)
  field+=np.asarray(im)/255*weight
 field=np.clip((field-.45)*.24,0,.10)
 wear=Image.new('L',(N,N));draw=ImageDraw.Draw(wear)
 for j in range(28):
  x=int(rng.integers(N));y=int(rng.integers(N));draw.line((x,y,x+int(rng.integers(-25,40)),y+int(rng.integers(2,9))),fill=int(rng.integers(8,35)),width=int(rng.integers(1,3)))
 scuff=np.asarray(wear.filter(ImageFilter.GaussianBlur(.8)))/255
 base=np.clip((1-field-scuff*.3)*235+rng.normal(0,.6,(N,N)),0,255)
 Image.fromarray(np.uint8(np.repeat(base[:,:,None],3,2))).save(OUT/f'CFD_Coat{i}_Base.png')
 ms=np.zeros((N,N,4),np.uint8);ms[:,:,0]=18;ms[:,:,3]=np.uint8(np.clip(95-field*380-scuff*200,30,110));Image.fromarray(ms).save(OUT/f'CFD_Coat{i}_MetallicSmoothness.png')
normal=np.empty((N,N,3),np.uint8);normal[:]=[128,128,255];rng=np.random.default_rng(57);normal[:,:,:2]=np.uint8(np.clip(128+rng.normal(0,1,(N,N,2)),123,133));Image.fromarray(normal).save(OUT/'CFD_Micro_Normal.png')
stripe=rng.normal(0,1,(N,1));micro=rng.normal(0,.9,(N,N));a=np.clip(190+stripe*2+micro,170,205);Image.fromarray(np.uint8(np.repeat(a[:,:,None],3,2))).save(OUT/'CFD_Steel_Base.png')
ms=np.zeros((N,N,4),np.uint8);ms[:,:,0]=230;ms[:,:,3]=np.uint8(np.clip(130+stripe*2+micro,110,145));Image.fromarray(ms).save(OUT/'CFD_Steel_MetallicSmoothness.png')
print('PBR textures',len(list(OUT.glob('CFD_*'))))
