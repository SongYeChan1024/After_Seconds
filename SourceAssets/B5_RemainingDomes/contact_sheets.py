from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_B5_RemainingDomes'
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
groups=[['C03_0','C03_1','C04_0','C04_1','W01_0','W01_1'],['W02_0','W02_1','W03_0','W03_1','E01_0','E01_1'],['E02_0','E02_1','E03_0','E03_1','N01_0','N01_1'],['S01_0','S01_1','VB_0','VB_1','VL_0','VL_1'],['T08','T13','T19','Play_cooling','Play_stairs','Play_lift']]
for n,names in enumerate(groups,1):
 sheet=Image.new('RGB',(1280,1290),(17,22,30));draw=ImageDraw.Draw(sheet)
 for i,name in enumerate(names):
  im=Image.open(D/(name+'.png'));im.thumbnail((640,400))
  x=(i%2)*640;y=(i//2)*430;sheet.paste(im,(x,y));draw.text((x+12,y+401),name,font=font,fill='white')
 sheet.save(D/('ReviewSheet_'+str(n)+'.jpg'),quality=93)
print('5 contact sheets saved')
