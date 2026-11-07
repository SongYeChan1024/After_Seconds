from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
H=Path(__file__).resolve().parent;R=H.parents[1];p=json.loads((H/'plan.json').read_text(encoding='utf-8'));O=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/B5/Textures'
font=lambda s:ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',s)
def centered(d,text,y,size,w,color='white'):
 f=font(size);b=d.textbbox((0,0),text,font=f);d.text(((w-b[2]+b[0])/2-b[0],y-b[1]),text,font=f,fill=color)
for code,info in p['destinations'].items():
 im=Image.new('RGBA',(768,1792));d=ImageDraw.Draw(im);d.polygon([(384,95),(555,300),(454,300),(454,490),(314,490),(314,300),(213,300)],fill='white')
 for txt,y,size in [('SECTOR C' if info['sector']=='C' else 'VERTICAL',575,68),(code,740,248),(info['name'],1130,99),('DESTINATION / B5',1480,54)]:centered(d,txt,y,size,768)
 d.line((95,1390,673,1390),fill='white',width=8);im.save(O/f'ND_Floor_{code}.png')
im=Image.new('RGBA',(1040,1440));d=ImageDraw.Draw(im);col=(217,228,229)
centered(d,'DESTINATIONS',45,65,1040,col);centered(d,'C02 / 보안관제동',145,46,1040,col);d.line((45,235,995,235),fill=col,width=5)
for i,(code,info) in enumerate(p['destinations'].items()):
 y=290+i*264;c=info['color'];d.rectangle((70,y+24,102,y+180),fill=c);d.text((151,y),code,font=font(83),fill=c);d.text((151,y+113),info['name'],font=font(53),fill=c)
 # Same shapes also appear along the corresponding painted lane.
 x=868;yy=y+91;pattern=info['pattern']
 if pattern=='circle':d.ellipse((x-37,yy-37,x+37,yy+37),outline=c,width=12)
 elif pattern=='square':d.rectangle((x-34,yy-34,x+34,yy+34),outline=c,width=11)
 elif pattern=='diamond':d.polygon([(x,yy-45),(x+45,yy),(x,yy+45),(x-45,yy)],outline=c,width=11)
 else:
  for dx in [-22,22]:d.rectangle((x+dx-8,yy-37,x+dx+8,yy+37),fill=c)
im.save(O/'ND_Legend.png')
d.rectangle((0,130,1040,224),fill=(0,0,0,0));centered(d,'C01 / 실험동',145,46,1040,col);im.save(O/'ND_Legend_C01.png')
print('4 destination stencils and 2 four-colour floor legends')
