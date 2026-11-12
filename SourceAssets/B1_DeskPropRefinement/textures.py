"""One shared 2048 atlas for local work screens and printed records."""
from pathlib import Path
import sys,math,json
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(R/'Unity/After_Seconds_Build_V0.01/Temp/ZFightingReview/deps'))
from PIL import Image,ImageDraw,ImageFont
out=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B1/Textures'
out.mkdir(parents=True,exist_ok=True)
im=Image.new('RGB',(2048,2048),(227,226,214));d=ImageDraw.Draw(im)
def font(n,bold=False):return ImageFont.truetype('C:/Windows/Fonts/'+('consolab.ttf' if bold else 'consola.ttf'),n)
titles=['RECORD CATALOG','RECEIPT REGISTER','REVIEW / COMPARE','ARCHIVE INDEX','SHIFT HANDOVER','ACCESS / B4 TO B3','BACKUP STATUS','STAFF HEALTH','ULTRASOUND / READY','VOICE MEMO','READING NOTES','INTAKE CHECKLIST','COMPARISON SHEET','MEETING AGENDA','ARCHIVE TRANSFER','SHIFT REPORT']
for i,title in enumerate(titles):
 x=(i%4)*512;y=(i//4)*512;paper=i>=10;bg=(231,230,216) if paper else (18,29,32);fg=(38,54,57) if paper else (196,216,213);muted=(104,117,114) if paper else (111,150,151);accent=(47,100,103) if paper else (93,182,165)
 d.rectangle((x,y,x+511,y+511),fill=bg);d.rectangle((x+22,y+24,x+490,y+68),fill=(192,202,190) if paper else (33,66,70));d.text((x+32,y+34),title,font=font(24,True),fill=fg);d.text((x+32,y+85),'B1 / STAFF SERVICES' if i in [4,7,8] else 'B1 / RESEARCH RECORDS',font=font(17),fill=muted)
 if i in [2,7,8]:
  for yy in range(145,350,25):d.line((x+34,y+yy,x+477,y+yy),fill=(37,53,53),width=1)
  for xx in range(34,480,25):d.line((x+xx,y+145,x+xx,y+350),fill=(37,53,53),width=1)
  if i==8:
   d.polygon([(x+255,y+150),(x+108,y+340),(x+406,y+340)],fill=(90,104,101));d.text((x+67,y+380),'PROBE CONNECTED / STANDBY',font=font(20),fill=fg)
  else:
   pts=[(x+35+k*2,y+252+int(30*math.sin(k*.14)+10*math.sin(k*.37))) for k in range(220)];d.line(pts,fill=accent,width=3);d.text((x+35,y+375),'REVIEW A / B' if i==2 else 'PATIENT --  /  SENSOR READY',font=font(20),fill=fg)
 elif i==9:
  d.text((x+55,y+182),'REC  04:18',font=font(51,True),fill=accent);d.text((x+55,y+282),'MEMO  017',font=font(30),fill=fg)
 else:
  heads=['REF       REV   STATE','S03-041   R02   CHECKED','S03-042   R06   FILED','S03-043   R02   REVIEW','S03-044   R01   RECEIVED']
  if i==5:heads=['ZONE     B4 -> B3','STAIR A  STAFF ONLY','STAIR B  STAFF ONLY','CARGO    CHECK-IN','EVENTS   003 / REVIEW']
  if i==6:heads=['NODE   COPY     STATUS','B1-A   09:30    VERIFIED','B1-B   09:35    VERIFIED','B1-C   09:40    QUEUED','CHECKSUM  /  12 OF 12']
  if paper:heads=['REF. S03-043  /  REV.02','DATE 11.12  /  SHIFT A','AUTHOR __________________','CHECK  [x] READ  [ ] FILE','NOTES ___________________','_________________________','SIGN ____________________']
  for j,line in enumerate(heads):d.text((x+32,y+135+j*40),line,font=font(21 if not paper else 20),fill=fg);d.line((x+32,y+167+j*40,x+477,y+167+j*40),fill=muted,width=1)
 d.text((x+32,y+468),'INTERNAL COPY  /  '+str(i+1).zfill(2),font=font(16),fill=muted)
im.save(out/'DP_WorkRecords.png')
(H/'atlas.json').write_text(json.dumps({'size':2048,'titles':titles,'asset':'Assets/Afrer_Seconds/05.Model/Props/B1/Textures/DP_WorkRecords.png'},indent=2))
print('Atlas saved',im.size)
