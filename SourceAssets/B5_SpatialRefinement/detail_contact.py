from pathlib import Path
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parents[2]/'Docs/검수/2026-11-08_B5_SpatialRefinement'
for page,names in enumerate([['W03_inside','E01_inside','E02_inside','E03_inside','S01_inside','C02_inside'],['W03_detail','C03_detail','N01_detail','E02_detail','E03_detail','S01_detail']]):
 im=Image.new('RGB',(1440,470*3),'#18202a');d=ImageDraw.Draw(im)
 for i,n in enumerate(names):
  a=Image.open(D/(n+'.png'));a.thumbnail((720,440));x=i%2*720;y=i//2*470;im.paste(a,(x,y+25));d.text((x+10,y+5),n,fill='white')
 im.save(D/f'detail_contact_{page}.jpg')
