"""실측 페인트·시설 코드 텍스처. 작성자: 송예찬."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/B5/Textures'
O.mkdir(exist_ok=True)
font_path=Path('C:/Windows/Fonts/bahnschrift.ttf')
if not font_path.exists():font_path=Path('C:/Windows/Fonts/consolab.ttf')
rng=np.random.default_rng(1107)
# 페인트에는 작은 붓결·마찰 차이만 넣고 코드 가독성을 유지한다.
noise=rng.normal(0,2,(512,512));v=np.clip(247+noise,232,255).astype(np.uint8)
paint=np.stack([v,v,v,np.full_like(v,255)],axis=-1)
for i in range(42):
 x,y=rng.integers(0,512,2);paint[y:min(y+2,512),x:min(x+int(rng.integers(2,12)),512),:3]=rng.integers(186,225)
Image.fromarray(paint).save(O/'CW_Paint_Base.png')
for code in ['R1','S1','M1']:
 for mode in ['Floor','Plate']:
  im=Image.new('RGBA',(512,768),(255,255,255,0));d=ImageDraw.Draw(im)
  if mode=='Floor':
   d.polygon([(256,26),(355,140),(295,140),(295,245),(217,245),(217,140),(157,140)],fill='white')
   font=ImageFont.truetype(str(font_path),234);d.text((256,420),code,font=font,anchor='mm',fill='white')
   if code=='R1':
    d.rectangle((145,603,190,706),fill='white');d.rectangle((322,603,367,706),fill='white')
   elif code=='S1':d.rectangle((196,593,316,713),outline='white',width=24)
   else:
    for yy in [583,635,687]:d.rectangle((220,yy,292,yy+28),fill='white')
  else:
   d.rounded_rectangle((16,16,496,752),radius=24,outline=(255,255,255,220),width=8)
   font=ImageFont.truetype(str(font_path),218);d.text((256,300),code,font=font,anchor='mm',fill='white')
   # Small route-type symbol rather than a room name or puzzle instruction.
   if code=='R1':
    d.rectangle((154,488,195,640),fill='white');d.rectangle((317,488,358,640),fill='white')
   elif code=='S1':d.rectangle((183,486,329,632),outline='white',width=25)
   else:
    for yy in [488,548,608]:d.rectangle((220,yy,292,yy+26),fill='white')
  im.save(O/f'CW_{mode}_{code}.png')
(H/'texture_manifest.json').write_text(json.dumps(dict(author='송예찬',textures=[p.name for p in O.glob('CW_*.png')],font=font_path.name,purpose='업무 코드·방향/패턴; 정적 텍스처'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Textures:',len(list(O.glob('CW_*.png'))))
