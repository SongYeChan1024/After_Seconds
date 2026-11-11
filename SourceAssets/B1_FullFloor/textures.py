from pathlib import Path
import sys,math
H=Path(__file__).resolve().parent;R=H.parents[1];sys.path.insert(0,str(R/'Unity/After_Seconds_Build_V0.01/Temp/ZFightingReview/deps'))
from PIL import Image,ImageDraw,ImageFont
O=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B1/Textures';O.mkdir(parents=True,exist_ok=True)
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/consola.ttf',n)
for i,title in enumerate(['RESEARCH / SESSION ARCHIVE','LAUNDRY / CYCLE STATUS','PREDICTION / TIMECODE'],1):
 im=Image.new('RGB',(512,256),(17,28,33));d=ImageDraw.Draw(im)
 d.rectangle((0,0,512,36),fill=(38,66,73));d.text((14,8),title,font=font(20),fill=(216,225,216))
 d.text((15,49),'AFTER SECONDS    B1 / '+str(i).zfill(2),font=font(16),fill=(136,178,176))
 for y in [85,115,145,175,205]:d.line((18,y,490,y),fill=(41,60,65),width=1)
 if i==3:
  d.text((68,96),'00:00:03.000',font=font(48),fill=(218,221,198));d.text((98,181),'SYNC  /  STANDBY',font=font(23),fill=(158,191,183))
 else:
  for k in range(3):
   pts=[(18+x*3,119+k*32+int(12*math.sin(x*.12+k)+5*math.sin(x*.38))) for x in range(100)];d.line(pts,fill=[(104,174,160),(160,163,120),(109,143,170)][k],width=2)
  for k,s in enumerate(['LINK   OK','LOG   142','TEMP  24C','MODE HOLD']):d.text((342,87+k*28),s,font=font(16),fill=(192,211,204))
 d.text((14,233),'LOCAL RECORD / STATIC EQUIPMENT DISPLAY',font=font(12),fill=(118,143,144));im.save(O/f'BL_Display_{i:02}.png')
print('3 small display textures written')
