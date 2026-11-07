from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageEnhance
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_B5_TwoDomeGuidance';O=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B5/Textures'
font=lambda s:ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf',s)
BG=(8,18,24);INK=(191,215,220);DIM=(83,126,137)
for i,title in enumerate(['C01 / OBSERVATION','C01 / SAMPLE TRANSFER','C01 / NORTH ACCESS','T01 / TRANSIT'],1):
 im=Image.new('RGB',(1280,800),BG);d=ImageDraw.Draw(im);d.rectangle((0,0,1280,68),fill=(19,37,47));d.text((30,20),title,font=font(25),fill=INK);d.ellipse((1190,25,1205,40),fill=(119,202,161))
 view=ImageOps.fit(Image.open(D/f'Feed_{i:02}.png').convert('RGB'),(1216,618));view=ImageEnhance.Color(view).enhance(.38);view=ImageEnhance.Brightness(view).enhance(.95);im.paste(view,(32,86));d=ImageDraw.Draw(im);d.rectangle((49,102,260,143),fill=BG);d.text((62,113),f'CAM {i:02}  /  B5',font=font(18),fill=INK);d.text((55,654),'REC   00:42:16     /     SECURE CHANNEL',font=font(20),fill=INK);d.line((30,747,1250,747),fill=DIM,width=2);d.text((30,764),'ASE   /   OPERATIONS SYSTEM     B5-C02',font=font(18),fill=DIM);d.text((1050,764),'00:42:16',font=font(18),fill=DIM);im.save(O/f'SC_Display_{i:02}.png')
print('Refreshed static feeds 01-04 from current saved scene')
