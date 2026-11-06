from pathlib import Path
from PIL import Image,ImageDraw
repo=Path(__file__).resolve().parents[2]
root=next((repo/'Docs').rglob('facility_layout.json')).parent
imgs=sorted((root/'도면').glob('page-*.png'))
w,h=600,460
out=Image.new('RGB',(w*4,h*((len(imgs)+3)//4)),'white')
for i,p in enumerate(imgs):
 im=Image.open(p);im.thumbnail((w-12,h-30));x=(i%4)*w;y=(i//4)*h
 out.paste(im,(x+6,y+25));ImageDraw.Draw(out).text((x+10,y+7),p.stem,fill='black')
out.save(root/'contact.png');print(root/'contact.png')
