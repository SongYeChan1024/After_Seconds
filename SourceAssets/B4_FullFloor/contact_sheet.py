from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];O=R/'Docs/검수/2026-11-08_B4_FullFloor'
for group,files in [('rooms',sorted(O.glob('*_room.png'))),('overview',sorted(O.glob('*_overview.png'))),('tunnels',sorted(O.glob('B4-T*.png')))]:
 sheet=Image.new('RGB',(1600,((len(files)+2)//3)*360),(20,24,27));d=ImageDraw.Draw(sheet)
 for i,p in enumerate(files):
  im=Image.open(p);im.thumbnail((528,330));x=(i%3)*534;y=(i//3)*360
  sheet.paste(im,(x,y));d.text((x+12,y+332),p.stem,fill='white',font_size=18)
 sheet.save(O/f'contact_{group}.jpg',quality=90)
