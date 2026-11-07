from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
H=Path(__file__).resolve().parent;R=H.parents[1]
OUT=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/B5/Textures'
OUT.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(107);n=1024
for name,color,rough,metal in [('Coat',(160,170,172),.55,.12),('Floor',(72,83,88),.71,.02),('Steel',(114,126,132),.38,.80)]:
    grain=rng.normal(0,1.3,(n,n));coarse=np.asarray(Image.fromarray(rng.integers(96,161,(32,32),dtype=np.uint8)).resize((n,n),Image.Resampling.BICUBIC),float)-128
    signal=grain+coarse*.12
    if name=='Steel': signal+=rng.normal(0,.9,(n,1))
    rgb=np.clip(np.array(color)[None,None,:]+signal[:,:,None],0,255).astype('uint8')
    Image.fromarray(rgb).save(OUT/f'TC_{name}_Base.png')
    h=Image.fromarray(np.clip(128+signal*1.8,0,255).astype('uint8')).filter(ImageFilter.GaussianBlur(.6))
    gy,gx=np.gradient(np.asarray(h,float)/255);normal=np.stack((-gx*1.2,-gy*1.2,np.ones_like(gx)),axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
    Image.fromarray(np.uint8(np.clip((normal*.5+.5)*255,0,255))).save(OUT/f'TC_{name}_Normal.png')
    mask=np.empty((n,n,4),dtype=np.uint8);mask[:,:,0]=int(metal*255);mask[:,:,1:3]=0;mask[:,:,3]=np.uint8(np.clip((1-rough)*255+signal*.4,0,255))
    Image.fromarray(mask).save(OUT/f'TC_{name}_MetalSmooth.png')
font='C:/Windows/Fonts/malgunbd.ttf'
for code,title in [('C01','실험동'),('C02','보안관제동')]:
    im=Image.new('RGBA',(768,1792));d=ImageDraw.Draw(im);c=(222,231,226,255)
    d.polygon([(384,95),(555,300),(454,300),(454,490),(314,490),(314,300),(213,300)],fill=c)
    def line(text,y,size):
        f=ImageFont.truetype(font,size);b=d.textbbox((0,0),text,font=f);d.text(((768-(b[2]-b[0]))/2-b[0],y-b[1]),text,font=f,fill=c)
    line('SECTOR C',575,68);line(code,740,248);line(title,1130,112 if code=='C01' else 99)
    d.line((95,1390,673,1390),fill=c,width=8);line('B5  /  R1',1480,72)
    im.save(OUT/f'TC_Floor_{code}.png')
print('Created 9 PBR maps and 2 floor stencils')
