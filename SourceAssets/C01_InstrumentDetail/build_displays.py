"""Static instrument LCD artwork; no gameplay UI or runtime behaviour. 송예찬."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math,json
H=Path(__file__).resolve().parent;R=H.parents[1]
O=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B5/Textures';O.mkdir(exist_ok=True)
W,Ht=1024,640
def font(s,b=False):return ImageFont.truetype('C:/Windows/Fonts/'+('seguisb.ttf' if b else 'segoeui.ttf'),s)
BG=(5,13,19);INK=(201,225,227);DIM=(99,137,149);CYAN=(72,209,218);GREEN=(112,225,162);AMBER=(235,181,83)
def canvas(title,tag):
 im=Image.new('RGB',(W,Ht),BG);d=ImageDraw.Draw(im)
 d.rectangle((0,0,W,67),fill=(17,36,47));d.text((28,17),title,font=font(25,True),fill=INK)
 d.text((800,22),'ASE  /  '+tag,font=font(19),fill=DIM)
 d.line((24,575,1000,575),fill=(38,63,74),width=2);d.text((28,596),'CONNECTED   •   CALIBRATION VALID',font=font(17),fill=DIM)
 d.text((795,596),'11:42:08  UTC',font=font(17),fill=DIM)
 return im,d
def panel(d,box):d.rounded_rectangle(box,radius=9,fill=(9,22,30),outline=(33,58,70),width=2)
def text(d,xy,t,s=22,c=INK):d.text(xy,t,font=font(s),fill=c)
def graph(d,box,color=CYAN,phase=0,kind='smooth'):
 x,y,w,h=box
 for i in range(9):d.line((x+i*w/8,y,x+i*w/8,y+h),fill=(20,42,52))
 for i in range(5):d.line((x,y+i*h/4,x+w,y+i*h/4),fill=(20,42,52))
 pts=[]
 for i in range(int(w)):
  a=i/w
  if kind=='ecg':
   t=(a*5+phase)%1;v=.04*math.sin(t*math.tau)+.17*math.exp(-((t-.18)/.05)**2)-.22*math.exp(-((t-.38)/.022)**2)+.9*math.exp(-((t-.42)/.014)**2)-.3*math.exp(-((t-.47)/.024)**2)+.20*math.exp(-((t-.69)/.08)**2)
  elif kind=='peaks':v=.07+.73*math.exp(-((a-.28)/.038)**2)+.4*math.exp(-((a-.53)/.065)**2)+.58*math.exp(-((a-.79)/.029)**2)
  elif kind=='temperature':v=.36+.03*math.sin(a*17+phase)+.02*math.sin(a*7)
  else:v=.38+.24*math.sin(a*math.tau*3+phase)
  pts.append((x+i,y+h*(.80-v*.72)))
 d.line(pts,fill=color,width=3)
for kind in ['Vital','ObservationA','ObservationB','Assay','Centrifuge','Cold','PCR','Balance','Chromatography','Plate','Sterilizer','Bath','Printer']:
 titles={'Vital':'PATIENT MONITOR','ObservationA':'PHYSIOLOGICAL MONITORING','ObservationB':'CHAMBER ENVIRONMENT','Assay':'OPTICAL ASSAY READER','Centrifuge':'REFRIGERATED CENTRIFUGE','Cold':'SPECIMEN COLD STORAGE','PCR':'THERMAL CYCLER','Balance':'ANALYTICAL BALANCE','Chromatography':'LIQUID CHROMATOGRAPHY','Plate':'MICROPLATE WORKSTATION','Sterilizer':'STEAM STERILIZER','Bath':'ULTRASONIC CLEANER','Printer':'SPECIMEN LABEL PRINTER'}
 im,d=canvas(titles[kind],kind[:3].upper())
 if kind in ['Vital','ObservationA']:
  for row,(label,value,unit,col) in enumerate([('ECG  II','72','bpm',GREEN),('SpO2','98','%',CYAN),('RESP','16','rpm',AMBER)]):
   y=90+row*145;panel(d,(20,y,704,y+132));text(d,(38,y+9),label,18,col);graph(d,(40,y+35,640,84),col,row*.13,'ecg' if row==0 else 'smooth')
   panel(d,(724,y,1004,y+132));text(d,(744,y+8),label,18,col);text(d,(745,y+26),value,69,col);text(d,(927,y+88),unit,19,col)
  text(d,(37,538),'NIBP    118 / 76   (90) mmHg     •     LEADS ATTACHED',19)
 elif kind=='ObservationB':
  for i,(label,value,unit) in enumerate([('AIR TEMPERATURE','22.4','°C'),('RELATIVE HUMIDITY','45.2','%'),('DIFFERENTIAL PRESSURE','-12','Pa')]):
   x=24+i*332;panel(d,(x,92,x+312,268));text(d,(x+17,110),label,17,DIM);text(d,(x+17,146),value,63,CYAN);text(d,(x+240,215),unit,22)
  panel(d,(24,290,1000,550));graph(d,(48,327,926,180),CYAN,0,'temperature');text(d,(50,302),'ENVIRONMENT HISTORY  /  LAST 30 MIN',18,DIM)
 elif kind in ['Assay','Chromatography']:
  panel(d,(24,90,690,464));text(d,(44,108),'ABSORBANCE  [AU]' if kind=='Assay' else 'DETECTOR RESPONSE  [mAU]',20,CYAN);graph(d,(62,155,600,260),CYAN,0,'peaks')
  for i,v in enumerate(['0.0','2.5','5.0','7.5','10.0']):text(d,(50+i*146,430),v,16,DIM)
  panel(d,(714,90,1000,550));text(d,(737,112),'SAMPLE  08 / 24',23);text(d,(737,174),'0.482',55,GREEN);text(d,(738,242),'405 nm   •   READING',18,DIM)
  for i in range(5):text(d,(738,300+i*41),f'{i+3:02d}    {0.210+i*.068:.3f}    PASS',20,GREEN)
  text(d,(34,505),'RUN  000127   /   REFERENCE CORRECTED',21)
 elif kind=='Plate':
  panel(d,(24,90,720,551));text(d,(44,109),'PLATE A  /  96 WELLS',23)
  for j in range(8):
   for i in range(12):
    x,y=56+i*51,167+j*43;col=(28,95+((i*13+j*7)%90),126+((i+j)%3)*26);d.ellipse((x,y,x+28,y+28),fill=col,outline=(81,158,178),width=2)
  text(d,(755,120),'INCUBATING',22,GREEN);text(d,(752,177),'37.0°',55,CYAN);text(d,(750,277),'08:42',55);text(d,(750,353),'REMAINING',18,DIM)
 elif kind=='Balance':
  text(d,(40,100),'STABLE   •   NET WEIGHT',24,GREEN);text(d,(100,209),'14.2286',126,CYAN);text(d,(820,292),'g',54)
  for i,label in enumerate(['TARE','ZERO','UNITS','PRINT']):panel(d,(26+i*248,453,254+i*248,546));text(d,(68+i*248,484),label,24)
 elif kind=='Printer':
  text(d,(40,116),'LABEL QUEUE',27);text(d,(40,185),'SAMPLE  004218',54,CYAN);text(d,(42,280),'2D CODE  /  25 × 50 mm',28,DIM)
  for i in range(55):d.rectangle((50+i*12,360,52+i*12+(i%3),475),fill=INK)
  text(d,(780,185),'READY',33,GREEN);text(d,(780,260),'024',72);text(d,(780,350),'REMAINING',18,DIM)
 else:
  data={'Centrifuge':('4,200','RPM','02:18','REMAINING','4.0 °C'), 'Cold':('-20.0','°C','NORMAL','STORAGE STATUS','DOOR SEALED'), 'PCR':('72.0','°C','32 / 40','CYCLE','EXTENSION'), 'Sterilizer':('121.0','°C','01:42','HOLD TIME','1.8 bar'), 'Bath':('37.0','°C','05:00','CLEANING CYCLE','40 kHz')}
  val,unit,sec,label,small=data[kind];panel(d,(24,92,620,385));text(d,(48,112),'CURRENT VALUE',21,DIM);text(d,(60,177),val,108,CYAN);text(d,(500,305),unit,33)
  panel(d,(644,92,1000,385));text(d,(666,114),label,21,DIM);text(d,(665,195),sec,48,GREEN);text(d,(668,313),small,22)
  panel(d,(24,410,1000,551));graph(d,(45,431,935,99),CYAN,1,'temperature')
 im.save(O/('ID_LCD_'+kind+'.png'))
# Small manufactured nameplates, each has specific equipment family and serial markings.
for kind in ['Optics','Prep','Thermal','Fluidics','Wash','Storage']:
 im=Image.new('RGB',(512,128),(38,48,53));d=ImageDraw.Draw(im);d.rounded_rectangle((2,2,509,125),radius=7,outline=(154,165,168),width=2)
 d.text((16,14),'ASE  /  '+kind.upper(),font=font(27,True),fill=(215,222,220));d.text((17,62),'MOD. 07A   •   SN 061102   •   24 V DC',font=font(18),fill=(175,192,196))
 for i in range(22):d.rectangle((370+i*5,24,371+i*5+(i%2),101),fill=(181,198,204))
 im.save(O/('ID_Label_'+kind+'.png'))
print('Created 13 LCD layouts and 6 manufactured nameplates')
