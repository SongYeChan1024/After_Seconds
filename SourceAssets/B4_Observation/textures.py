"""Procedural observation readouts. Static art, not live gameplay UI. 송예찬."""
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from pathlib import Path
import math,random
R=Path(__file__).resolve().parents[2];OUT=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B4/Textures';OUT.mkdir(parents=True,exist_ok=True)
font='C:/Windows/Fonts/consola.ttf'
def f(n):return ImageFont.truetype(font,n)
ink=(187,202,203);mute=(92,115,124);green=(115,183,153);amber=(198,172,106);grid=(34,51,61)
def text(d,p,s,n=19,c=ink):d.text(p,s,font=f(n),fill=c)
def base(title,code):
 im=Image.new('RGB',(1024,640),(13,23,30));d=ImageDraw.Draw(im)
 d.rectangle((0,0,1024,68),fill=(31,47,56));text(d,(32,18),title,27);text(d,(810,25),code,19,green)
 d.line((32,593,992,593),fill=mute,width=1);text(d,(32,610),'B4 / C01   OBSERVATION NETWORK',16,mute);text(d,(790,610),'SYNC  00:14.820',16,green)
 return im,d
def chart(d,box):
 x,y,w,h=box
 for i in range(9):d.line((x+i*w/8,y,x+i*w/8,y+h),fill=grid)
 for i in range(6):d.line((x,y+i*h/5,x+w,y+i*h/5),fill=grid)
def plot(d,box,phase,col,amp=.3):
 x,y,w,h=box;pts=[]
 for i in range(int(w)):
  t=i/w;v=math.sin(t*math.tau*3+phase)*amp+math.sin(t*39+phase)*.035
  pts.append((x+i,y+h*(.5-v)))
 d.line(pts,fill=col,width=2)
im,d=base('SUBJECT TRACKING / OPTICAL','OBS-01')
chart(d,(35,105,620,450));cx,cy=345,330
for rr in [85,165,210]:d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline=mute,width=2)
d.arc((cx-205,cy-205,cx+205,cy+205),205,335,fill=ink,width=8)
for ang in [22.5,112.5,202.5,292.5]:
 a=math.radians(ang);x=cx+190*math.cos(a);y=cy+190*math.sin(a);d.rectangle((x-5,y-5,x+5,y+5),fill=green);d.line((x,y,cx,cy),fill=grid,width=1)
body=[(345,296),(345,342),(326,373),(318,401),(345,342),(369,371),(377,399),(345,308),(315,330),(296,319),(315,330),(345,308),(374,325),(390,308)]
d.line(body,fill=green,width=3);d.ellipse((336,276,354,294),outline=green,width=2)
for x,y in body:d.ellipse((x-3,y-3,x+3,y+3),fill=amber)
text(d,(704,105),'CAPTURE VOLUME',22);text(d,(704,144),'DIAMETER  5.2 m',20,mute)
for i,(a,b) in enumerate([('TRACKING','LOCKED'),('CAMERAS','04 / 04'),('MARKERS','14 / 14'),('ERROR','0.82 mm'),('RATE','120 Hz')]):
 text(d,(704,210+i*57),a,17,mute);text(d,(704,234+i*57),b,23,green)
im.save(OUT/'BO_Display_01.png')
im,d=base('KINEMATIC RESPONSE / CAPTURE','OBS-02')
for i,title in enumerate(['POSITION / X Y Z','VELOCITY / m s-1','RESPONSE / NORMALIZED']):
 y=98+i*157;text(d,(35,y),title,18,mute);box=(35,y+29,700,105);chart(d,box)
 for j,c in enumerate([green,amber,(123,155,190)]):plot(d,box,j+i,c,.28-j*.06)
text(d,(782,107),'TRIAL  014',25)
for i,(a,b) in enumerate([('LATENCY','182 ms'),('PEAK','2.36 m/s'),('VARIANCE','0.024'),('WINDOW','14.82 s')]):text(d,(782,175+i*92),a,16,mute);text(d,(782,202+i*92),b,24,green)
im.save(OUT/'BO_Display_02.png')
im,d=base('TRIAL SEQUENCE / CONTROL','CTL-01')
text(d,(35,98),'PROTOCOL   M-04 / MOTOR RESPONSE',24)
for i,(a,b,c) in enumerate([('01','BASELINE ACQUISITION','RECORDED'),('02','OPTICAL CALIBRATION','VERIFIED'),('03','STIMULUS WINDOW','READY'),('04','RESPONSE CAPTURE','STANDBY'),('05','ARCHIVE VALIDATION','PENDING')]):
 y=163+i*72;d.rounded_rectangle((32,y,730,y+57),radius=5,fill=(25,39,47));text(d,(49,y+15),a,21,mute);text(d,(105,y+15),b,21);text(d,(571,y+17),c,16,green if i<3 else mute)
text(d,(775,171),'INTERLOCKS',21);text(d,(775,223),'DOOR    SAFE',18,green);text(d,(775,267),'AREA    CLEAR',18,green);text(d,(775,311),'SYNC    READY',18,green);text(d,(775,421),'NO STIMULUS',20,amber);text(d,(775,451),'ARMED',26,amber)
im.save(OUT/'BO_Display_03.png')
im,d=base('TRAJECTORY / SPATIAL REVIEW','CTL-02');chart(d,(40,113,660,435))
for k in range(5):
 pts=[(65+i*6,500-(math.sin(i/100*math.pi)*290+k*4)) for i in range(100)];d.line(pts,fill=green if k==2 else grid,width=2)
text(d,(768,120),'REFERENCE / 04',20);text(d,(768,182),'PATH DEVIATION',17,mute);text(d,(768,215),'0.038 m',28,green);text(d,(768,298),'REVIEW WINDOW',17,mute);text(d,(768,334),'00:14.820',25);text(d,(768,448),'ARCHIVE READY',20,green)
im.save(OUT/'BO_Display_04.png')
im,d=base('SENSOR SYNCHRONIZATION','DAQ-04');text(d,(36,110),'MASTER CLOCK   120.000 Hz',27,green)
for i in range(6):
 y=180+i*57;text(d,(38,y),f'CH {i+1:02}    OPTICAL / {i+101:03}',20);d.line((425,y+14,768,y+14),fill=grid,width=8);d.line((425,y+14,730+(i%3)*12,y+14),fill=green,width=8);text(d,(825,y),'LOCKED',20,green)
im.save(OUT/'BO_Display_05.png')
im=Image.new('RGB',(1024,384),(184,190,184));d=ImageDraw.Draw(im);d.rectangle((15,15,1009,369),outline=(45,56,58),width=5);text(d,(45,40),'B4 / OPTICAL SENSOR SET',48,(34,45,48));text(d,(45,122),'CALIBRATED  /  C01 - 014',32,(34,45,48))
random.seed(404)
for x in range(48,650,5):
 if random.random()>.4:d.rectangle((x,205,x+2,320),fill=(35,43,46))
text(d,(700,225),'AS / 04',39,(34,45,48));im.save(OUT/'BO_Display_06.png')
im=Image.new('RGBA',(1024,256),(0,0,0,0));d=ImageDraw.Draw(im);text(d,(38,38),'C01',125,(191,196,191,255));text(d,(355,60),'CENTRAL',47,(191,196,191,255));text(d,(355,122),'OBSERVATION',47,(191,196,191,255));d.polygon([(900,60),(988,128),(900,196),(900,151),(830,151),(830,105),(900,105)],fill=(191,196,191,255));im.save(OUT/'BO_Floor_C01.png')
print('TEXTURES COMPLETE',len(list(OUT.glob('BO_*.png'))))
