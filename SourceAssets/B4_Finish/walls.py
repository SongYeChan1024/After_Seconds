from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter,ImageDraw
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/Common/Textures';N=2048
def noise(rng,n):return np.asarray(Image.fromarray(rng.normal(0,1,(n,n)).astype('float32')).resize((N,N),Image.Resampling.BICUBIC))
for floor,amp in [('B5',.60),('B4',.80),('B3',1.0)]:
 rng=np.random.default_rng(int(floor[-1])*331);yy=np.linspace(4,0,N)[:,None];low=np.exp(-yy/.32);mid=np.exp(-((yy-.88)/.60)**2);a=noise(rng,12);b=noise(rng,64);grain=noise(rng,512)
 grime=np.maximum(a+.4,0)*(low*24+mid*5)+np.maximum(b+.1,0)*low*10
 mask=Image.new('L',(N,N));d=ImageDraw.Draw(mask)
 for i in range(45):
  x=rng.uniform(0,N);y=rng.uniform(.68,.98)*N;length=rng.uniform(15,130);d.line((x,y,x+length,y+rng.uniform(-5,5)),fill=int(rng.uniform(8,30)),width=int(rng.uniform(1,5)))
 rub=np.asarray(mask.filter(ImageFilter.GaussianBlur(2.8))).astype(float)*np.clip(.7+noise(rng,256)*.3,0,1)
 c=242+grain*.7+a*.7-amp*(grime+rub);c=np.stack([c,c+.2,c+.4],-1)
 Image.fromarray(np.uint8(np.clip(c,0,255))).save(O/('WW_'+floor+'_Base.png'))
 ms=np.zeros((N,N,4));ms[:,:,0]=18;ms[:,:,3]=118-grime*1.1*amp-rub*amp+grain*2
 Image.fromarray(np.uint8(np.clip(ms,0,255))).save(O/('WW_'+floor+'_MetalSmooth.png'))
 v=np.stack([-(np.roll(grain,-1,1)-grain)*.006,(np.roll(grain,-1,0)-grain)*.006,np.ones_like(grain)],-1);v/=np.linalg.norm(v,axis=-1,keepdims=True)
 Image.fromarray(np.uint8((v*.5+.5)*255)).save(O/('WW_'+floor+'_Normal.png'))
print('Nine restrained wall finish maps')
