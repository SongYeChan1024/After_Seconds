from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter,ImageDraw
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/B5/Textures';O.mkdir(parents=True,exist_ok=True)
N=1024;rng=np.random.default_rng(1039)
for name in ['Floor','Coat','Linen']:
 field=np.zeros((N,N),np.float32)
 for res,weight in [(9,.45),(37,.35),(155,.2)]:field+=np.asarray(Image.fromarray(np.uint8(rng.random((res,res))*255)).resize((N,N),Image.Resampling.BICUBIC))/255*weight
 dirt=Image.new('L',(N,N));dr=ImageDraw.Draw(dirt)
 for j in range(70 if name=='Floor' else 25):
  x,y=rng.integers(0,N,2);dx,dy=rng.integers(-45,45,2);dr.line((int(x),int(y),int(x+dx),int(y+dy)),fill=int(rng.integers(8,40)),width=int(rng.integers(1,4)))
 scuff=np.asarray(dirt.filter(ImageFilter.GaussianBlur(1.1)))/255
 gray=232-(field-.32)*29-scuff*80+rng.normal(0,.8,(N,N))
 if name=='Linen':
  yy,xx=np.mgrid[:N,:N];gray+=np.sin(xx*2.09)*1.2+np.sin(yy*2.1)*1.2
 Image.fromarray(np.uint8(np.clip(np.repeat(gray[:,:,None],3,axis=2),0,255))).save(O/f'S1_{name}_Base.png')
 ms=np.zeros((N,N,4),np.uint8);ms[:,:,0]=10 if name=='Floor' else 16 if name=='Coat' else 0
 ms[:,:,3]=np.uint8(np.clip((65 if name=='Floor' else 90 if name=='Coat' else 18)-(field-.5)*35-scuff*55,8,120))
 Image.fromarray(ms).save(O/f'S1_{name}_MetallicSmoothness.png')
normal=np.empty((N,N,3),np.uint8);normal[:]=[128,128,255];normal[:,:,:2]=np.uint8(np.clip(128+rng.normal(0,.8,(N,N,2)),125,131));Image.fromarray(normal).save(O/'S1_Micro_Normal.png')
print('S1 PBR maps ready')
