"""Manufacturing prints and surface PBR. Author 송예찬."""
from pathlib import Path
import json,re
from PIL import Image,ImageDraw,ImageFont
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B5/Textures';O.mkdir(exist_ok=True)
source=json.loads((H/'prop_sources.json').read_text());assert len(source)<=64,len(source)
im=Image.new('RGB',(4096,2048),(24,34,39));d=ImageDraw.Draw(im);font=lambda n:ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf',n)
for name,item in source.items():
 i=item['label'];x=(i%8)*512;y=(i//8)*256;title=re.sub(r'(?<=[a-z])(?=[A-Z])',' ',name.replace('SF_','').replace('SC_','').replace('SR_','')).upper()
 d.rounded_rectangle((x+7,y+7,x+505,y+249),radius=8,fill=(202,213,210),outline=(59,79,83),width=4)
 d.rectangle((x+13,y+13,x+499,y+59),fill=(23,62,70));d.text((x+27,y+21),'ASE  /  ENGINEERED SYSTEMS',font=font(24),fill=(220,234,230))
 words=title.split();lines=['']
 for w in words:
  if len(lines[-1])+len(w)>23:lines.append('')
  lines[-1]+=(' ' if lines[-1] else '')+w
 for j,line in enumerate(lines[:2]):d.text((x+28,y+70+j*31),line,font=font(25),fill=(24,42,48))
 d.text((x+28,y+146),f'B5 / AS-{i+100:04}  REV 02',font=font(21),fill=(41,62,65));d.text((x+28,y+177),'SERVICE ACCESS / INSPECT SEALS',font=font(15),fill=(41,62,65))
 for j in range(96):
  if (j*j+37*i+j*13)%7<4:d.rectangle((x+28+j*4,y+208,x+29+j*4,y+232),fill=(24,42,48))
im.save(O/'SF_EquipmentPrint.png')
rng=np.random.default_rng(811);n=1024;y,x=np.indices((n,n));grain=rng.normal(0,1.2,(n,n));scuff=np.zeros((n,n))
for i in range(260):
 xx,yy=rng.integers(0,n,2);length=int(rng.integers(5,110));scuff[yy:yy+1,xx:min(n,xx+length)]=rng.uniform(1,5)
for name,col,metal,smooth in [('Coat',[211,220,222],30,95),('Steel',[178,191,196],215,150),('Floor',[161,177,183],8,60)]:
 pat=grain+(np.sin(y*.7)*.7 if name=='Steel' else 0)-scuff*.4
 base=np.clip(np.array(col)[None,None,:]+pat[:,:,None],0,255).astype('uint8');Image.fromarray(base).save(O/f'SF_{name}_Base.png')
 normal=np.empty((n,n,3),dtype='uint8');normal[:,:,0]=np.clip(128+np.gradient(pat,axis=1)*.8,0,255);normal[:,:,1]=np.clip(128+np.gradient(pat,axis=0)*.8,0,255);normal[:,:,2]=255;Image.fromarray(normal).save(O/f'SF_{name}_Normal.png')
 packed=np.zeros((n,n,4),dtype='uint8');packed[:,:,:3]=metal;packed[:,:,3]=np.clip(smooth+grain*2-scuff*4,0,255);Image.fromarray(packed).save(O/f'SF_{name}_MetalSmooth.png')
print('Print labels',len(source),'surface maps 9')
