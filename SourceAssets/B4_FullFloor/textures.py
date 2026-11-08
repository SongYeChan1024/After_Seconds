from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math,random,json
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B4/Textures';O.mkdir(exist_ok=True)
def f(s):return ImageFont.truetype('C:/Windows/Fonts/consola.ttf',s)
ink=(188,204,207);green=(118,180,152);muted=(96,120,132);amber=(201,169,104)
def text(d,p,s,n=22,c=ink):d.text(p,s,font=f(n),fill=c)
titles=['SENSOR CALIBRATION','SPECTRAL ANALYSIS','DELAY / IMPACT TIMING','STIMULUS / RESPONSE','DIAGNOSTIC BASELINE','PROTOCOL / RESEARCH','OPTICAL CAPTURE A','OPTICAL CAPTURE B','SUBJECT MOTION REVIEW','TIME ALIGNMENT','B4 FACILITY OVERVIEW','TRIAL STATUS SUMMARY','SHIELDED LOAD TEST','RECORD TRANSFER','RECOVERY OBSERVATION','CARGO LIFT / B4']
for k,title in enumerate(titles,7):
 im=Image.new('RGB',(1024,640),(13,23,30));d=ImageDraw.Draw(im);d.rectangle((0,0,1024,68),fill=(32,47,56));text(d,(28,17),title,28);text(d,(820,25),f'B4 / {k:02}',20,green)
 for y in range(112,554,44):d.line((35,y,750,y),fill=(33,51,61))
 for x in range(35,751,55):d.line((x,112,x,554),fill=(33,51,61))
 if k in [13,14,15,17]:
  if k==17:
   p=json.loads((H/'plan.json').read_text(encoding='utf-8'));scale=2.4
   for t in p['tunnels']:d.line((390+t['p'][0]*scale,330+t['p'][1]*scale,390+t['q'][0]*scale,330+t['q'][1]*scale),fill=muted,width=3)
   for r in p['rooms']:
    x,y,rr=390+r['x']*scale,330+r['v']*scale,r['r']*scale;d.ellipse((x-rr,y-rr,x+rr,y+rr),outline=green,width=2);text(d,(x-15,y-10),r['id'],13)
  else:
   for off in [-140,140]:
    cx=390+off;d.ellipse((cx-24,170,cx+24,218),outline=green,width=3);pts=[(cx,220),(cx,350),(cx-54,450),(cx-70,510),(cx-54,450),(cx,350),(cx+54,450),(cx+70,510),(cx+54,450),(cx,350),(cx,250),(cx-75,305),(cx-115,285),(cx-75,305),(cx,250),(cx+75,305),(cx+110,275)];d.line(pts,fill=green,width=3)
    for x,y in pts:d.ellipse((x-4,y-4,x+4,y+4),fill=amber)
 elif k in [12,18,20,22]:
  for i in range(6):
   y=123+i*65;d.rectangle((35,y,750,y+45),fill=(25,40,49));text(d,(50,y+9),f'{i+1:02}  '+['CALIBRATION','ACQUISITION','CLOCK SYNC','TRIAL RECORD','ARCHIVE CHECK','INTERLOCK'][i],20);text(d,(585,y+9),'VERIFIED' if i<4 else 'STANDBY',18,green)
 else:
  for j,c in enumerate([green,amber,(121,158,188)]):
   pts=[]
   for i in range(700):
    t=i/700;v=math.sin(t*(3+j)*math.tau+k)*.20+math.sin(t*71+k)*.035;pts.append((35+i,190+j*145-v*230))
   d.line(pts,fill=c,width=2)
 text(d,(785,111),'TRIAL / 014',24)
 for i,(a,b) in enumerate([('SAMPLE RATE','120 Hz'),('CLOCK SYNC','LOCKED'),('DEVIATION','0.038'),('RECORD','READY')]):text(d,(785,182+i*93),a,17,muted);text(d,(785,211+i*93),b,24,green)
 d.line((28,592,995,592),fill=muted);text(d,(28,610),'AFTER SECONDS / B4 RESEARCH SYSTEM',16,muted);text(d,(800,610),'00:14.820',17,green);im.save(O/f'BF_Display_{k:02}.png')
names={'C01':'OBSERVATION','C02':'DIAGNOSTICS','C03':'SENSOR SUPPORT','C04':'ANALYSIS','C05':'RECORDS','VA':'STAIR A','VB':'STAIR B','VL':'CARGO LIFT','W01':'THROW DELAY','W02':'TRAJECTORY','W03':'REACTION TIME','E01':'IMAGE REVIEW','E02':'RESEARCH','E03':'RECOVERY','N01':'CONTROL','S01':'SHIELDED TEST'}
palette=['70A8A3','879FC0','B39B71','9EB77B','B38EAA','7EB290','C4AE74','9B92BD','CB9872','82AFBE','B2BA75','9B9FC8','78A9B7','A7B5C0','BEA284','9AA67A']
for (code,name),color in zip(names.items(),palette):
 im=Image.new('RGBA',(1024,256),(0,0,0,0));d=ImageDraw.Draw(im);c=tuple(int(color[i:i+2],16) for i in [0,2,4])+(255,);text(d,(20,40),code,124,c);text(d,(340,95),name,40,c);d.polygon([(925,57),(1005,128),(925,199),(925,151),(860,151),(860,105),(925,105)],fill=c);im.save(O/f'BF_Guide_{code}.png')
(H/'guide_colors.json').write_text(json.dumps(dict(zip(names,palette)),indent=2),encoding='utf-8');print('Textures32')
