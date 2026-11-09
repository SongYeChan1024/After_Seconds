from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;R=H.parents[1];labels=json.loads((H/'key_labels.json').read_text());im=Image.new('RGBA',(1024,1024),(0,0,0,0));d=ImageDraw.Draw(im)
for i,label in enumerate(labels):
 if label=='Space':continue
 font=ImageFont.truetype('C:/Windows/Fonts/consolab.ttf',38 if len(label)==1 else 20 if len(label)<=3 else 16)
 bb=d.textbbox((0,0),label,font=font);x=(i%16)*64+(64-bb[2]+bb[0])/2-bb[0];y=(i//16)*64+(64-bb[3]+bb[1])/2-bb[1];d.text((x,y),label,font=font,fill=(230,234,235,255))
out=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B4/Textures/PD_KeyLegends.png';out.parent.mkdir(parents=True,exist_ok=True);im.save(out)
print('Key legends',len(labels))
