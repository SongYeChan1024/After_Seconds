import bpy,numpy as np
from pathlib import Path
R=Path(__file__).parent;P=R.parent.parent/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/Architecture_Rebuilt/Textures';P.mkdir(parents=True,exist_ok=True)
n=1024;rng=np.random.default_rng(731);a=np.clip(.94+rng.normal(0,.018,(n,n)),.84,1)
for _ in range(110):
 x,y=rng.integers(0,n,2);h=int(rng.integers(3,45));a[y:min(n,y+h),x]*=rng.uniform(.88,.97)
rgba=np.ones((n,n,4),dtype=np.float32);rgba[:,:,:3]=a[:,:,None];im=bpy.data.images.new('Fine_WornSurface',width=n,height=n,alpha=True);im.pixels.foreach_set(rgba.ravel());im.filepath_raw=str(P/'Fine_WornSurface.png');im.file_format='PNG';im.save()
