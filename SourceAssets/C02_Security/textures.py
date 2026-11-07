from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageEnhance
import numpy as np,math,json,runpy
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B5/Textures';O.mkdir(exist_ok=True)
font=lambda s:ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf',s)
BG=(8,18,24);INK=(191,215,220);DIM=(83,126,137);CYAN=(78,181,191);GREEN=(119,202,161);AMBER=(221,168,77)
feeds=[R/'Docs/검수/2026-11-07_C01_Wayfinding'/x for x in ['After_RouteOverview.png','After_S1_Transfer.png','After_NorthJunction.png']]+[R/'Docs/검수/2026-11-07_T01_Corridor/After_ToSecurity.png']
updated=[R/f'Docs/검수/2026-11-08_C02_Refine/Feed_{i:02}.png' for i in range(1,5)]
if all(p.exists() for p in updated):feeds=updated
coloured=[R/f'Docs/검수/2026-11-08_B5_DestinationColors/Feed_{i:02}.png' for i in range(1,5)]
two_domes=[R/f'Docs/검수/2026-11-08_B5_TwoDomeGuidance/Feed_{i:02}.png' for i in range(1,5)]
if all(p.exists() for p in two_domes):coloured=two_domes
stair_a=[R/f'Docs/검수/2026-11-08_T02_StairA/Feed_{i:02}.png' for i in range(1,5)]
if all(p.exists() for p in stair_a):coloured=stair_a
if all(p.exists() for p in coloured):feeds=coloured
for i in range(1,11):
 im=Image.new('RGB',(1280,800),BG);d=ImageDraw.Draw(im)
 titles=['C01 / OBSERVATION','C01 / SAMPLE TRANSFER','C01 / NORTH ACCESS','T01 / TRANSIT','B5 / SECURITY OVERVIEW','ACCESS EVENT JOURNAL','OPERATOR 01 / ACCESS','OPERATOR 02 / RECORDING','INCIDENT REVIEW / ARCHIVE','POWER / NETWORK HEALTH']
 d.rectangle((0,0,1280,68),fill=(19,37,47));d.text((30,20),titles[i-1],font=font(25),fill=INK);d.ellipse((1190,25,1205,40),fill=GREEN)
 if i<=4:
  view=ImageOps.fit(Image.open(feeds[i-1]).convert('RGB'),(1216,618));view=ImageEnhance.Color(view).enhance(.38);view=ImageEnhance.Brightness(view).enhance(.95);im.paste(view,(32,86));d=ImageDraw.Draw(im);d.rectangle((49,102,260,143),fill=BG);d.text((62,113),f'CAM {i:02}  /  B5',font=font(18),fill=INK)
  d.text((55,654),'REC   00:42:16     /     SECURE CHANNEL',font=font(20),fill=INK)
 elif i==5:
  runpy.run_path(str(R/'SourceAssets/C02_SecurityRefine/map_texture.py'));continue
 elif i in [6,7,9]:
  d.text((35,96),'TIME          NODE       EVENT                              STATUS',font=font(22),fill=DIM)
  for row in range(8):
   y=150+row*65;d.rectangle((25,y-7,1255,y+44),fill=(13+row%2*4,28+row%2*4,36+row%2*4));d.text((40,y),f'00:{42-row:02d}:16     {"T01" if row%3==0 else "C01" if row%3==1 else "VA "}        '+['CREDENTIAL VERIFIED','DOOR CONTACT / CLOSED','RECORD SEGMENT SAVED'][row%3],font=font(23),fill=INK);d.text((1120,y),'OK',font=font(23),fill=GREEN)
  d.text((35,703),'LOCAL BUFFER  /  REVIEW READY',font=font(23),fill=CYAN)
 else:
  for row,(title,val) in enumerate([('CAMERA LINKS','12 / 12'),('STORAGE ARRAY','82 %'),('UPS CHARGE','98 %'),('ROOM TEMPERATURE','22.4 C')]):
   y=105+row*142;d.rounded_rectangle((30,y,1245,y+120),radius=10,fill=(14,30,39),outline=(32,58,70),width=2);d.text((55,y+20),title,font=font(23),fill=DIM);d.text((55,y+51),val,font=font(39),fill=INK)
   for j in range(40):d.rectangle((575+j*15,y+75-math.sin(j*.24+row)*17,585+j*15,y+96),fill=CYAN if row%2==0 else GREEN)
 d.line((30,747,1250,747),fill=DIM,width=2);d.text((30,764),'ASE   /   OPERATIONS SYSTEM     B5-C02',font=font(18),fill=DIM);d.text((1050,764),'00:42:16',font=font(18),fill=DIM);im.save(O/f'SC_Display_{i:02}.png')
rng=np.random.default_rng(208);n=512;v=rng.normal(0,2,(n,n))+np.indices((n,n)).sum(axis=0)%2*2;rgb=np.clip(np.array([47,61,67])[None,None,:]+v[:,:,None],0,255).astype('uint8');Image.fromarray(rgb).save(O/'SC_Fabric_Base.png')
for code,title in [('C04','유틸리티동'),('VA','계단 A')]:
 im=Image.new('RGBA',(768,1792));d=ImageDraw.Draw(im);col=(222,231,226,255);d.polygon([(384,95),(555,300),(454,300),(454,490),(314,490),(314,300),(213,300)],fill=col)
 for text,y,size in [('SECTOR C' if code=='C04' else 'VERTICAL',575,68),(code,740,248),(title,1130,99),('B5  /  R1',1480,72)]:
  f=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',size);b=d.textbbox((0,0),text,font=f);d.text(((768-b[2]+b[0])/2-b[0],y-b[1]),text,font=f,fill=col)
 d.line((95,1390,673,1390),fill=col,width=8);im.save(O/f'SC_Floor_{code}.png')
print('10 static display textures, fabric map and 2 destination stencils created')
