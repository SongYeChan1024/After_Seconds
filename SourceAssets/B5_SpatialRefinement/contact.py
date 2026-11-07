from pathlib import Path
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent; R=H.parents[1]; D=R/'Docs/검수/2026-11-08_B5_SpatialRefinement'
for page, names in enumerate([['C02','C03','C04','W01','W02','W03'],['E01','E02','E03','N01','S01','VA','VB','VL']]):
 im=Image.new('RGB',(1200,420*((len(names)+1)//2)),'#18202a'); d=ImageDraw.Draw(im)
 for i,n in enumerate(names):
  p=D/(n+'_0.png'); a=Image.open(p);a.thumbnail((600,390)); x=(i%2)*600;y=(i//2)*420; im.paste(a,(x,y+25));d.text((x+10,y+5),n,fill='white')
 im.save(D/f'contact_{page}.jpg')
