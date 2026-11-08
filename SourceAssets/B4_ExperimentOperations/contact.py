from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;O=H.parents[1]/'Docs/검수/2026-11-08_B4_ExperimentOperations'
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
groups={'rooms':sorted(O.glob('*_room.png')),'overview':sorted(O.glob('*_overview.png')),'roles':sorted(O.glob('*_role_*.png'))}
for label,paths in groups.items():
 for j in range(0,len(paths),12):
  chunk=paths[j:j+12];canvas=Image.new('RGB',(1440,330*((len(chunk)+2)//3)),(22,29,35));d=ImageDraw.Draw(canvas)
  for i,p in enumerate(chunk):
   im=Image.open(p);im.thumbnail((480,300));x=i%3*480;y=i//3*330;canvas.paste(im,(x,y+30));d.text((x+8,y+2),p.stem,fill='white',font=font)
  canvas.save(O/f'contact_{label}_{j//12+1}.jpg',quality=90)
print('Contact sheets ready')
