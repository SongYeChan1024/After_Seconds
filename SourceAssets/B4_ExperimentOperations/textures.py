from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math,json
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B4/Textures';O.mkdir(exist_ok=True)
def f(n):return ImageFont.truetype('C:/Windows/Fonts/consola.ttf',n)
ink='#bfd0d3';muted='#718b96';green='#91b6a1';amber='#c6ad7c';blue='#8faac6'
def txt(d,xy,s,n=20,c=ink):d.text(xy,s,font=f(n),fill=c)
titles=['SUBJECT / SESSION INTAKE','ESCORT / LOCAL INTERLOCK','TRIAL CONTROL / ACQUISITION','DEVELOPMENT / COMPARISON','FORCE PLATE / POSITION','RESISTANCE / REPETITION','PURSUIT / TRACKING ERROR','STIMULUS / RESPONSE','CONDITIONING / SESSION','SUBJECT / STATUS','CALIBRATION / REFERENCE','TIMEBASE / SYNCHRONIZATION','LIVE ACQUISITION / CHANNELS','SENSOR FIT / CONTACT','POST-TRIAL / OBSERVATION','BASELINE / CURRENT','TRIAL HISTORY / REVIEW','PROTOCOL / SESSION PLAN']
for k,title in enumerate(titles,23):
 im=Image.new('RGB',(1280,800),'#101c23');d=ImageDraw.Draw(im);d.rectangle((0,0,1279,77),fill='#263942');txt(d,(28,22),title,29);txt(d,(1010,27),'B4 / RESEARCH',22,green)
 txt(d,(28,102),'SUBJECT S-03   |   SESSION 014   |   BASELINE 001',23)
 d.rectangle((28,150,920,700),fill='#182a33');d.rectangle((946,150,1250,700),fill='#20323b')
 if k in [23,24,33,36,40]:
  sets={23:['SUBJECT ID       S-03','ESCORT CHECK     COMPLETE','BASELINE FILE    001 / LOADED','SENSOR FIT       VERIFIED','TRIAL ORDER      014 / READY','RECOVERY SLOT    E03 / RESERVED'],24:['ENTRY DOOR       OPEN / LOCAL','TEST ENVELOPE    CLEAR','GUARD POST       OCCUPIED','OPERATOR LINK    AVAILABLE','EMERGENCY LOOP   STANDBY','TRIAL ENABLE     AWAITING OPERATOR'],33:['OPTICAL OFFSET   0.002 m','TIMEBASE ERROR   0.001 ms','CHANNEL GAIN     1.000','REFERENCE LOAD   20.00 N','ENCODER ZERO     VERIFIED','NEXT CHECK       BEFORE SESSION'],36:['HEAD REFERENCE   CONTACT OK','LEFT ARM         CONTACT OK','RIGHT ARM        CONTACT OK','TORSO REFERENCE  CONTACT OK','ANKLE TRACKERS   PAIRED','SIGNAL QUALITY   99.2 %'],40:['01  INTAKE / SENSOR FIT','02  BASELINE MEASUREMENT','03  CONTROLLED REPETITIONS','04  REPEAT MEASUREMENT','05  IMAGE / SIGNAL REVIEW','06  POST-TRIAL OBSERVATION']}
  for i,s in enumerate(sets[k]):
   y=177+i*80;d.rectangle((50,y,895,y+54),fill='#243c46');txt(d,(69,y+15),s,24);d.ellipse((860,y+19,875,y+34),fill=green)
 elif k==39:
  txt(d,(55,172),'TRIAL    CONDITION      RESULT      REVIEW',22,green)
  for i in range(8):
   y=225+i*55;d.rectangle((50,y,895,y+40),fill='#243c46' if i%2==0 else '#1c3039')
   txt(d,(65,y+8),f'{i+7:03}      MATCHED        {79+i:02}.4        '+('CONFIRMED' if i<7 else 'PENDING'),21)
  txt(d,(65,677),'RECORDS / SAME-SUBJECT COMPARISON',19,muted)
 elif k==26:
  txt(d,(65,172),'MATCHED CONDITIONS / BASELINE VS CURRENT',22,green)
  for i,label in enumerate(['TIMING','ACCURACY','REPEATABILITY','TRACKING']):
   y=235+i*105;txt(d,(65,y),label,21);d.rectangle((280,y,600+i*24,y+20),fill=muted);d.rectangle((280,y+28,700+i*35,y+48),fill=green)
  txt(d,(65,677),'NORMALIZED RESEARCH VIEW / SESSION 014',19,muted)
 elif k in [31,38]:
  for x in range(75,900,76):d.line((x,198,x,605),fill='#304954')
  for y in range(198,606,58):d.line((75,y,900,y),fill='#304954')
  for line,c in [(0,muted),(1,green)]:
   pts=[(85+i*74,560-i*(23 if line else 12)+math.sin(i*1.5)*20+line*12) for i in range(11)];d.line(pts,fill=c,width=4)
   for x,y in pts:d.ellipse((x-5,y-5,x+5,y+5),fill=c)
  txt(d,(80,640),'BASELINE  - - -    CURRENT / REPEATED TRIALS',23);txt(d,(85,165),'PERFORMANCE / CONDITION-MATCHED',21,green)
 elif k in [27,29]:
  for x in range(75,900,55):d.line((x,195,x,650),fill='#304954')
  for y in range(195,650,55):d.line((75,y,900,y),fill='#304954')
  if k==27:
   for x in [330,580]:
    d.rounded_rectangle((x,295,x+95,540),45,outline=muted,width=3)
    for i in range(5):d.ellipse((x+20,320+i*37,x+75,358+i*37),outline=green,width=3)
   d.line((470,185,470,651),fill=amber,width=2);txt(d,(95,663),'CENTER OF PRESSURE / m',20)
  else:
   pts=[(90+i,410+math.sin(i*.010)*130) for i in range(780)];d.line(pts,fill=muted,width=5);d.line([(x,y+math.sin(x*.04)*12) for x,y in pts],fill=green,width=3);txt(d,(95,663),'TARGET / SUBJECT TRACK',20)
 elif k==30:
  for i in range(20):
   x=80+(i%5)*160;y=210+(i//5)*110;d.rounded_rectangle((x,y,x+115,y+74),8,fill='#304954',outline=green if i in [3,8,12] else muted,width=2);txt(d,(x+16,y+18),f'{280-i*3}ms',22,green)
  txt(d,(85,660),'RESPONSE LATENCY / SAME STIMULUS',20)
 elif k==34:
  txt(d,(88,226),'00 : 14 . 820',76,green);txt(d,(90,362),'MASTER / LOCKED',36)
  for i in range(15):d.line((80+i*54,520,80+i*54,610 if i%5==0 else 570),fill=amber,width=3)
  txt(d,(90,645),'TRIGGER ALIGNMENT     +0.001 ms',23)
 else:
  for j,c in enumerate([green,blue,amber]):
   for y in [225+j*145,275+j*145]:d.line((70,y,895,y),fill='#304954')
   pts=[(70+i,250+j*145+math.sin(i*.02+j)*22+math.sin(i*.09)*5) for i in range(825)];d.line(pts,fill=c,width=3);txt(d,(75,175+j*145),['CHANNEL A / REFERENCE','CHANNEL B / CURRENT','CHANNEL C / DEVIATION'][j],18,c)
 txt(d,(968,175),'SESSION CONTROL',21,green)
 for i,(a,bv) in enumerate([('SUBJECT','S-03'),('REPETITION','014 / 020'),('DATA CAPTURE','ARMED'),('CONDITION','CONTROLLED'),('ARCHIVE LINK','B3 / ONLINE')]):txt(d,(970,230+i*88),a,17,muted);txt(d,(970,255+i*88),bv,24)
 txt(d,(30,745),'AFTER SECONDS   /   PRECISION MEASUREMENT & DEVELOPMENT',20,muted);txt(d,(1070,745),'B4 LAB',22,green);im.save(O/f'BX_Display_{k:02}.png')
for k,title,lines in [(41,'CALIBRATED EQUIPMENT',['B4 / RESEARCH OPERATIONS','ASSET    BX-041','INSPECT BEFORE EACH SESSION']), (42,'LOCAL SAFETY / ACCESS',['B4 / CONTROLLED TRIAL AREA','AUTHORIZED STAFF ONLY','CHECK SUBJECT AND ESCORT STATUS'])]:
 im=Image.new('RGB',(1024,320),'#c7cbc6');d=ImageDraw.Draw(im);d.rectangle((0,0,1024,72),fill='#28373c');txt(d,(24,16),title,33,'#e0e4da')
 for i,s in enumerate(lines):txt(d,(26,100+i*58),s,28,'#25343a')
 for i in range(37):d.rectangle((840+i*4,110,841+i*4,267),fill='#25343a')
 im.save(O/f'BX_Display_{k:02}.png')
print('20 operations textures')
