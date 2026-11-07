from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_B5_CorridorOnlyGuidance'
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
for kind,files in [('corridors',sorted(D.glob('*_corridor.png'))),('domes',sorted(D.glob('*_dome.png'))),('thresholds',sorted(D.glob('*_threshold.png')))]:
 cols=3;w=600;h=405
 out=Image.new('RGB',(cols*w,((len(files)+cols-1)//cols)*h),'#171c22');draw=ImageDraw.Draw(out)
 for i,p in enumerate(files):
  im=Image.open(p).convert('RGB');im.thumbnail((w,h-30));x=i%cols*w;y=i//cols*h
  out.paste(im,(x,y));draw.text((x+8,y+h-29),p.stem,font=font,fill='white')
 out.save(D/f'{kind}_contact.jpg',quality=88)
print('Contact sheets ready')
