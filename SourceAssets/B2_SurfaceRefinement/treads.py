from pathlib import Path
import numpy as np
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[1];T=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/B2/Textures'
n=512;rng=np.random.default_rng(432);x,z=np.meshgrid(np.linspace(0,1,n),np.linspace(0,1,n));noise=rng.normal(0,1,(n,n));wear=np.exp(-((x-.49)/.33)**4)*np.exp(-((z-.5)/.45)**4);dust=np.clip((np.abs(x-.5)-.30)*4,0,.65)
col=np.zeros((n,n,3),float)+[71,78,77];col+=(noise*2+wear*32)[...,None];col=col*(1-dust[...,None])+np.array([61,51,38])*dust[...,None]
for i in range(100):
 xx=rng.integers(70,450);zz=rng.integers(15,490);length=rng.integers(4,28);col[zz:min(n,zz+length),xx:xx+1]+=rng.uniform(8,30)
Image.fromarray(np.clip(col,0,255).astype('uint8')).save(T/'BR_Tread_Base.png');ms=np.zeros((n,n,4),np.uint8);ms[:,:,:3]=np.clip((.65+wear*.25-dust*.5)*255,0,255).astype('uint8')[...,None];ms[:,:,3]=np.clip((.20+wear*.29-dust*.15)*255,0,255);Image.fromarray(ms).save(T/'BR_Tread_MS.png');normal=np.zeros((n,n,3),np.uint8)+[128,128,255];Image.fromarray(normal.astype(np.uint8)).save(T/'BR_Tread_Normal.png')
