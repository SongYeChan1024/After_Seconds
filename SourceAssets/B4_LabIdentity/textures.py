"""Original fictional laboratory graphics; static environmental art, not game values."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math,random,json
H=Path(__file__).resolve().parent;R=H.parents[1]
O=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B4/Textures';O.mkdir(exist_ok=True)
F=Path('C:/Windows/Fonts')
def font(n,b=False):return ImageFont.truetype(str(F/('consolab.ttf' if b else 'consola.ttf')),n)
titles=['SENSOR CONTACT / POST-TRIAL','OPTICAL ALIGNMENT RECORD','CONTROLLED LOAD / RUN SUMMARY','SIGNAL QUALITY / SESSION REVIEW','EQUIPMENT VERIFICATION','SPECIMEN RESPONSE / OBSERVATION']
for k,title in enumerate(titles):
 rng=random.Random(931+k);im=Image.new('RGB',(1536,2048),(230,229,219));d=ImageDraw.Draw(im)
 # restrained paper fibres and irregular handling, never a repeated stripe substitute for writing
 for _ in range(18000):
  x=rng.randrange(1536);y=rng.randrange(2048);v=rng.randrange(211,240);d.point((x,y),fill=(v,v,min(255,v-6)))
 ink=(40,52,56);muted=(100,108,106);teal=(36,91,93)
 def tx(x,y,s,n=24,b=False,col=ink):d.text((x,y),s,font=font(n,b),fill=col)
 d.rectangle((90,90,1446,100),fill=teal);tx(90,128,'AFTER SECONDS  /  RESEARCH OPERATIONS',28,True)
 tx(90,208,title,42,True);tx(90,278,f'B4  |  RECORD {k+12:03d}-A  |  REV. 03',25)
 tx(1120,282,f'PAGE 01 / 02',22)
 fields=[('SUBJECT','AS-017'),('SESSION',f'R-{183+k:04d}'),('STATION',['E03 / CONTACT','C03 / OPTICAL','S01 / LOAD','C04 / ANALYSIS','E02 / VERIFY','W03 / RESPONSE'][k]),('OPERATOR','J. HAN'),('REVIEW','M. SEO'),('STATUS','REVIEW PENDING')]
 for i,(label,val) in enumerate(fields):
  x=90+(i%2)*700;y=352+(i//2)*77;tx(x,y,label,19,True,muted);tx(x,y+28,val,28);d.line((x,y+65,x+620,y+65),fill=(160,166,162),width=1)
 tx(90,626,'01  MEASUREMENT SUMMARY',27,True)
 rows=[['CH','PRE CHECK','POST CHECK','NOTE'],['01','1.42 kOhm','1.68 kOhm','RESEATED'],['02','1.51 kOhm','1.49 kOhm','STABLE'],['03','1.63 kOhm','1.72 kOhm','RECHECK'],['04','1.47 kOhm','1.53 kOhm','STABLE']]
 if k:rows=[['RUN','REFERENCE','MEASURED','DEVIATION']]+[[f'{i+1:02d}',f'{10+i*5:.2f}',f'{10+i*5+rng.uniform(-.08,.08):.3f}',f'{rng.uniform(-.09,.09):+.3f}'] for i in range(4)]
 xs=[90,280,655,1040,1446]
 for j,row in enumerate(rows):
  y=683+j*62
  if j==0:d.rectangle((90,y,1446,y+60),fill=(202,212,208))
  for i,s in enumerate(row):tx(xs[i]+16,y+17,s,24,j==0)
  d.line((90,y+62,1446,y+62),fill=(147,158,155),width=1)
 tx(90,1040,'02  RECORDED RESPONSE / RELATIVE AMPLITUDE',27,True)
 plot=(160,1110,1400,1440)
 for i in range(9):
  x=160+i*155;d.line((x,1110,x,1440),fill=(198,206,201),width=1);tx(x-12,1452,str(i*2),18,col=muted)
 for i in range(5):
  y=1110+i*82;d.line((160,y,1400,y),fill=(198,206,201),width=1);tx(102,y-10,f'{1-i*.5:.1f}',18,col=muted)
 for c,col in enumerate([teal,(137,91,65)]):
  pts=[]
  for n in range(620):
   t=n/619;wave=math.sin(t*(33+k*5)+c)*.25+math.sin(t*91)*.03
   wave+=math.exp(-((t-(.37+c*.09))/.035)**2)*.60
   pts.append((160+1240*t,1285-wave*200+c*28))
  d.line(pts,fill=col,width=3)
 tx(1180,1484,'TIME (s)',20);tx(90,1544,'03  OPERATOR OBSERVATIONS',27,True)
 notes=[['Contact at CH03 drifted after movement.','Lead connector inspected; pad replaced.','Repeat baseline before the next session.'],['Reference target cleaned before alignment.','Stage return checked in both directions.','Final residuals attached for review.'],['Fixture seated; fasteners witness-marked.','Load return settled without visible slip.','Inspect insert before the following run.'],['CH02 shows a short transient at capture.','Cable shielding and reference verified.','Raw segment retained with this record.'],['Service cover closed after verification.','Connector retention checked by hand.','Bench released for supervised setup.'],['One delayed response noted in run 03.','Observation window retained in archive.','Repeat only after recovery check.']][k]
 for i,s in enumerate(notes):tx(105,1607+i*43,s,27)
 tx(90,1780,'CHECKS',20,True,muted)
 for i,s in enumerate(['ID matched','Leads returned','Area cleared']):
  x=90+i*440;d.rectangle((x,1820,x+23,1843),outline=ink,width=2);d.line((x+4,1831,x+10,1838,x+21,1823),fill=teal,width=2);tx(x+39,1819,s,23)
 tx(90,1900,'OPERATOR  J.Han',24);tx(820,1900,'REVIEW  ______________',24)
 tx(90,1980,'CONTROLLED COPY  /  LOCAL WORKING RECORD  /  RETAIN WITH SESSION',18,col=muted)
 im.save(O/f'LB_Record_{k+1:02d}.png')
 # Screen includes real axes/channel identifiers and different equipment states.
for k,title in enumerate(['OPTICAL PROFILOMETRY','INSTRUMENT VERIFICATION','ENCLOSED TEST / CONDITION','SIGNAL ANALYSIS','CONTACT IMPEDANCE','FORCE PLATE / ACQUISITION','DAQ / SYNCHRONIZATION','OPTICAL GATE TIMING']):
 im=Image.new('RGB',(1024,640),(14,24,29));d=ImageDraw.Draw(im);teal=(126,188,181);grey=(169,185,188)
 d.rectangle((0,0,1024,70),fill=(30,49,55));d.text((25,21),title,font=font(29,True),fill=(218,227,222));d.text((25,91),f'B4 / STATION {k+1:02d}     SESSION R-0183',font=font(20),fill=grey)
 for x in range(48,735,68):d.line((x,151,x,445),fill=(42,59,65))
 for y in range(151,446,49):d.line((48,y,735,y),fill=(42,59,65))
 for c,col in enumerate([teal,(194,153,100),(120,148,190)]):
  pts=[]
  for n in range(680):
   t=n/679;v=math.sin(t*(21+k*3)+c)*(.15 if k==4 else .30)+math.sin(t*97+c)*.025
   if k==7:v=.5 if .3+c*.17<t<.33+c*.17 else -.15
   pts.append((48+n,270+c*50-v*150))
  d.line(pts,fill=col,width=2)
  d.text((760,160+c*85),f'CH 0{c+1}',font=font(22,True),fill=col);d.text((760,190+c*85),f'{1.42+c*.17:.2f}'+(' kOhm' if k==4 else ' rel.'),font=font(21),fill=grey)
 d.text((48,463),'0          2          4          6          8 s',font=font(18),fill=grey)
 d.rectangle((24,515,1000,616),outline=(67,91,95),width=1)
 d.text((44,533),'SYNC LOCKED   /   REFERENCE VERIFIED',font=font(23),fill=teal)
 d.text((44,577),'CAPTURE STORED     REVIEW REQUIRED',font=font(21),fill=grey)
 im.save(O/f'LB_Display_{43+k:02d}.png')
# One shared 4x4 technical label atlas, UV selected per object.
im=Image.new('RGB',(2048,1024),(208,218,211));d=ImageDraw.Draw(im)
labels=[('CHANNEL / INPUT','1  2  3  4   /   REF'),('ISOLATED HEADBOX','CONNECT BEFORE ACQUIRE'),('CLEAN / SEALED','SINGLE USE ELECTRODES'),('USED / RETURN','LEADS / SENSORS'),('CONTACT CHECK','VERIFY AFTER FITTING'),('SERVICE / POWER','ISOLATE BEFORE OPENING'),('OPTICAL REFERENCE','KEEP SURFACE CLEAN'),('INSTRUMENT ID','B4 / CAL-042 / REV.03'),('TEST ENCLOSURE','INTERLOCK / READY'),('FORCE TRANSDUCER','ZERO BEFORE SESSION'),('ACQUISITION','TRIGGER / SYNC / REF'),('RETURN TO STORAGE','CLEAN / INSPECT / PACK'),('RUN / ID','AS017 / R0183'),('PROBE / PORT','INPUT 01 / GROUND'),('CONTROLLED LOAD','FIXTURE CHECK REQUIRED'),('NO SAMPLE LOADED','SERVICE POSITION')]
for k,(a,b) in enumerate(labels):
 x=k%4*512;y=k//4*256;d.rectangle((x+9,y+9,x+503,y+247),outline=(46,65,68),width=3)
 d.text((x+25,y+30),a,font=font(24,True),fill=(25,43,46));d.text((x+25,y+88),b,font=font(19),fill=(32,49,50))
 d.text((x+25,y+132),f'AS / B4   {k+42:04d}',font=font(22),fill=(32,49,50))
 rng=random.Random(k)
 for j in range(85):
  if rng.random()>.4:d.rectangle((x+25+j*4,y+184,x+27+j*4,y+225),fill=(42,52,52))
im.save(O/'LB_EquipmentLabels.png')
print('Created 6 records, 8 displays and equipment label atlas.')
