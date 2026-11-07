import json
from pathlib import Path
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_B5_SpatialRefinement';gs=json.loads((H/'grids.json').read_text());plan=json.loads((H/'plan.json').read_text(encoding='utf8'))
for code,g in gs.items():
 n=g['size'];im=Image.new('RGB',(n,n));im.putdata([(215,225,230) if f=='1' else (32,42,50) for f in g['flags']]);im=im.resize((n*5,n*5));d=ImageDraw.Draw(im)
 def pt(x,z):return((x-g['cx'])/g['step']+g['half'])*5,((z-g['cz'])/g['step']+g['half'])*5
 for i,p in enumerate(plan['rooms'][code]['doors']):
  x,y=pt(*p['position']);d.ellipse((x-9,y-9,x+9,y+9),fill='orange');d.text((x+12,y),str(i),fill='red')
 for p in plan['placements']:
  if p['room']==code:
   x,y=pt(p['position'][0]+g['cx'],p['position'][2]+g['cz']);d.text((x,y),p['model'][3:9],fill='red')
 im.save(D/(code+'_plan.png'))
