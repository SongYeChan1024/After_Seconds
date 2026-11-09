from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np,random,json
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1];T=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/B2/Textures';T.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(20261109);n=1024
cloud=Image.fromarray(rng.integers(0,256,(32,32),dtype=np.uint8)).resize((n,n),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(17))
c=np.array(cloud).astype(float)/255;noise=rng.normal(0,1.9,(n,n));v=np.clip(180+24*c+noise,0,255).astype('uint8');im=Image.fromarray(np.dstack([v,v,v]))
dr=ImageDraw.Draw(im);rr=random.Random(81)
for i in range(290):
 x,y=rr.randrange(n),rr.randrange(n);l=rr.randrange(2,65);dr.line((x,y,x+l,y+rr.randrange(-3,4)),fill=(165,168,170),width=1)
im.save(T/'BC_SteelWear_Base.png');a=np.zeros((n,n,4),np.uint8);a[:,:,:3]=225;a[:,:,3]=np.clip(74+60*c+rng.normal(0,2,(n,n)),0,255);Image.fromarray(a).save(T/'BC_SteelWear_MetalSmooth.png')
fonts='C:/Windows/Fonts/';F=lambda s:ImageFont.truetype(fonts+'consola.ttf',s)
for idx,title,subtitle in [(1,'P-201 / ACTIVE','FLOW   142.6 L/min'),(7,'COOLING / LOOP A','B2 / SERVICE ACCESS'),(8,'ISOLATION MANIFOLD','RETURN | SUPPLY | BYPASS'),(9,'PUMP SERVICE RECORD','UNIT P-201  |  SHIFT 08')]:
 im=Image.new('RGB',(1024,512),(21,31,35) if idx==1 else (202,205,192));dr=ImageDraw.Draw(im);fg=(169,219,213) if idx==1 else (32,39,41)
 dr.rectangle((12,12,1012,500),outline=fg,width=4);dr.text((40,35),title,font=F(45),fill=fg);dr.text((40,103),subtitle,font=F(33),fill=fg)
 if idx==1:
  dr.text((40,188),'PRESSURE   3.2 bar',font=F(42),fill=fg);dr.text((40,245),'TEMP       12.4 C',font=F(42),fill=fg);dr.line((40,335,980,335),fill=fg,width=2)
  pts=[(40+i*8,405+int(20*np.sin(i*.18))) for i in range(115)];dr.line(pts,fill=(58,183,161),width=4)
 elif idx==9:
  for y,txt in [(185,'09:10  CHECK SEALS / NO LEAK'),(245,'09:25  FILTER DP  0.2 bar'),(305,'09:40  BEARING TEMP  38 C'),(395,'NEXT: INSPECT RETURN VALVE')]:dr.text((42,y),txt,font=F(30),fill=fg)
 else:
  dr.text((40,210),'LOCK OUT BEFORE SERVICE',font=F(37),fill=(130,39,31));dr.text((40,290),'MAX 6 bar  /  400 V  /  50 Hz',font=F(31),fill=fg);dr.text((40,400),'SERIAL  02-201-047   /   REV C',font=F(26),fill=fg)
 im.save(T/('BC_Display_%02d.png'%idx))
print('textures written',T)
