from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json
R=Path(__file__).resolve().parents[2];O=R/'Docs/검수/2026-11-08_B5_CeilingLighting'
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
names=sorted(p.name for p in (O/'after').glob('*.png'))
stats=[]
for name in names:
 a=np.asarray(Image.open(O/'before'/name).convert('RGB'),dtype=float)/255
 b=np.asarray(Image.open(O/'after'/name).convert('RGB'),dtype=float)/255
 # Compare identical framing without touching exposure; lower frame describes usable floor/props.
 def lum(x):return .2126*x[:,:,0]+.7152*x[:,:,1]+.0722*x[:,:,2]
 ya,yb=lum(a),lum(b);roi=(slice(350,850),slice(150,1290))
 stats.append(dict(image=name,beforeMean=float(ya[roi].mean()),afterMean=float(yb[roi].mean()),beforeDarkFraction=float((ya[roi]<.10).mean()),afterDarkFraction=float((yb[roi]<.10).mean()),afterBrightFraction=float((yb[roi]>.95).mean())))
(O/'brightness.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
for kind,selected,batch in [('rooms',[n for n in names if n.endswith('_room.png')],4),('ceilings',[n for n in names if n.endswith('_ceiling.png')],4),('corridors',[n for n in names if n.startswith('B5-T')],5)]:
 for start in range(0,len(selected),batch):
  ns=selected[start:start+batch];sheet=Image.new('RGB',(1440,len(ns)*474),(19,24,29));draw=ImageDraw.Draw(sheet)
  for i,name in enumerate(ns):
   for j,phase in enumerate(['before','after']):
    im=Image.open(O/phase/name).convert('RGB');im.thumbnail((720,450));sheet.paste(im,(j*720,i*474));draw.text((j*720+10,i*474+450),name.replace('.png','')+' / '+('변경 전' if phase=='before' else '변경 후'),font=font,fill='white')
  sheet.save(O/f'{kind}_{start//batch+1}.jpg',quality=90)
print([(s['image'],round(s['beforeMean'],3),round(s['afterMean'],3)) for s in stats if s['image'].endswith('_room.png')])
