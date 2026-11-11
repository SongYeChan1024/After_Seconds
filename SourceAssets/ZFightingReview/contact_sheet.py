from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Unity/After_Seconds_Build_V0.01/Temp/ZFightingReview/deps'))
from PIL import Image,ImageDraw
O=ROOT/'Docs/Review/2026-11-11_ZFighting'
shots=json.loads((Path(__file__).parent/'shots.json').read_text())
paths=[O/('after_'+s['name']+'.png') for s in shots]
for start in range(0,len(paths),8):
 part=paths[start:start+8];canvas=Image.new('RGB',(1280,4*474),(20,23,27));draw=ImageDraw.Draw(canvas)
 for i,p in enumerate(part):
  if not p.exists():continue
  im=Image.open(p);im.thumbnail((640,450));x=(i%2)*640;y=(i//2)*474;canvas.paste(im,(x,y));draw.text((x+8,y+452),p.stem,fill='white')
 canvas.save(O/f'contact_{start//8+1}.jpg',quality=90)
print('Contact sheets created')
