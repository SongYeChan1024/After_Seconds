from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import json,math,random,numpy as np
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B3/Textures'
def font(s):return ImageFont.truetype('C:/Windows/Fonts/consola.ttf',s)
def txt(d,p,t,s=22,c=(190,207,212)):d.text(p,t,font=font(s),fill=c)
titles=['ULT STORAGE / C02','COLD STORAGE / W02','ARCHIVE NETWORK','SAMPLE INDEX / NODE 01','SAMPLE INDEX / NODE 02','ARCHIVE UPS','RECEIVING BALANCE','CHAIN OF CUSTODY','POUCH SEALER','AIR HANDLING / FILTER','SIGNAL ANALYSIS','ACCESSION / INSPECTION','COLD LOG','STERILIZATION','WASTE / HOLD','INVENTORY','COLD RETURN','REAGENT PREP','WASH STATION','DECONTAMINATION','EQUIPMENT SERVICE','SAMPLE TRANSFER','CARGO LIFT / B3']
for k,title in enumerate(titles,1):
 im=Image.new('RGB',(1024,640),(13,21,27));d=ImageDraw.Draw(im);d.rectangle((0,0,1024,70),fill=(33,47,55));txt(d,(28,20),title,30);txt(d,(860,25),'B3 / %02d'%k,18)
 if k in [1,2,13]:
  txt(d,(48,106),'-80.2 C' if k!=2 else '+4.1 C',83);txt(d,(52,210),'SET -80.0 C    DOOR SEALED' if k!=2 else 'SET +4.0 C    DOOR SEALED',24,(120,184,160));txt(d,(52,252),'CONTINUOUS COLD CIRCUIT / ACTIVE',22)
  for y in range(324,534,42):d.line((48,y,964,y),fill=(39,57,64))
  rng=random.Random(k);d.line([(48+i,427+math.sin(i*.019)*8+rng.uniform(-2,2)) for i in range(916)],fill=(132,184,199),width=3);txt(d,(52,556),'24 HOUR TREND / NO EXCURSIONS',20)
 elif k in [4,5,8,12,16,22]:
  txt(d,(40,105),'BATCH ID     LOCATION   TEMP    CHAIN STATUS',24)
  for i in range(7):
   y=161+i*52;d.rectangle((36,y-4,985,y+39),fill=(23,35,43));txt(d,(48,y),'AS-%03d-%02d   R%02d-%02d   %s   %s'%(k,i+12,k%5+1,i+1,'-80 C' if i%3 else '+04 C','SEALED' if i!=5 else 'REVIEW'),23,(181,199,205))
  txt(d,(48,559),'RECEIPT 0148  /  HANDOFF CHECK REQUIRED',22,(199,171,113))
 else:
  labels=['SYSTEM','CYCLE','INTERLOCK','FILTER DP','RECORD','NEXT CHECK'];values=['STANDBY','COMPLETE','SECURED','124 Pa','SAVED','06:00']
  if k==7:labels=['LOAD','TARE','CALIBRATION','STABILITY','RECORD','BATCH'];values=['128.42 g','24.00 g','VERIFIED','SETTLED','READY','AS-0148']
  if k==6:labels=['LINE','BATTERY','LOAD','RUNTIME','BYPASS','SERVICE'];values=['220.1 V','98 %','31 %','47 MIN','OFF','NORMAL']
  for i,(a,b) in enumerate(zip(labels,values)):
   y=118+i*70;d.line((42,y+49,975,y+49),fill=(45,62,69));txt(d,(48,y),a,25);txt(d,(610,y),b,29,(127,187,164))
 txt(d,(40,609),'AFTER SECONDS / SAMPLE SERVICES     LOCAL PANEL',17,(115,136,146));im.save(O/('B3_Display_%02d.png'%k))
im=Image.new('RGB',(2048,2048),(221,223,213));d=ImageDraw.Draw(im)
names=['RETAINED SAMPLE','SEALED / DO NOT OPEN','COLD CHAIN','RETURN / ANALYSIS','ACCESSION CHECKED','HOLD FOR REVIEW','ARCHIVE / SET A','ARCHIVE / SET B','QC REFERENCE','REAGENT STOCK','STERILE CONTAINER','TRANSFER CASE','RACK A / ROW 01','RACK B / ROW 02','RACK C / ROW 03','ULT / -80 C','CHILLED / +4 C','SERVER / INDEX','ARCHIVE / NODE','DATA / VERIFY','CONTROL / LINK','BACKUP / READY','NETWORK / PATCH','UPS / COLD LOAD','CALIBRATED','RECEIVING / BALANCE','CLEAN / PACKING','WORK LIGHTS','SEALED WASTE','CONTAMINATED','FILTER / INSPECTION','SERVICE / ISOLATE']
for k,title in enumerate(names):
 x=k%4*512;y=k//4*256;ink=(39,52,59);d.rectangle((x+6,y+6,x+505,y+249),outline=ink,width=3);txt(d,(x+22,y+18),title,25,ink);txt(d,(x+22,y+61),'AS / B3  LOT %04d'%(1400+k*7),21,ink);txt(d,(x+22,y+94),'CHECKED  2026-11-09  /  YC',18,ink)
 rng=random.Random(k+330)
 for bx in range(25,480,4):
  if rng.random()>.30:d.rectangle((x+bx,y+133,x+bx+rng.choice([1,2,3]),y+201),fill=ink)
 txt(d,(x+22,y+215),'RECORD %06d   SEAL INTACT'%(443200+k),17,ink)
im.save(O/'B3_Labels.png')
# Independently authored, soft irregular handling wear; no tiled decorative motifs.
rng=np.random.default_rng(811);n=1024
def noise(size):return np.asarray(Image.fromarray(rng.normal(0,1,(size,size)).astype('float32')).resize((n,n),Image.Resampling.BICUBIC))
coarse=noise(13);grain=noise(512);mask=Image.new('L',(n,n));d=ImageDraw.Draw(mask)
for i in range(160):
 x,y=rng.uniform(0,n,2);d.line((x,y,x+rng.uniform(-65,65),y+rng.uniform(-15,15)),fill=int(rng.uniform(9,60)),width=int(rng.integers(1,4)))
rub=np.asarray(mask.filter(ImageFilter.GaussianBlur(1.2)));base=240+grain*1.7-np.maximum(coarse,0)*10-rub*.65
Image.fromarray(np.uint8(np.clip(np.stack([base,base,base+.4],-1),0,255))).save(O/'B3_CaseWear_Base.png')
ms=np.zeros((n,n,4));ms[:,:,0]=20;ms[:,:,3]=110-grain*5-np.maximum(coarse,0)*15-rub*.40;Image.fromarray(np.uint8(np.clip(ms,0,255))).save(O/'B3_CaseWear_MetalSmooth.png')
names={'C01':'SAMPLE STORE','C02':'COLD STORAGE','C03':'WASTE / CHANGE','C04':'DECONTAMINATION','C05':'SAMPLE PREP','VA':'STAIR A','VB':'STAIR B','VL':'CARGO LIFT','W01':'RAW SAMPLES','W02':'COLD ARCHIVE','W03':'SEALED WASTE','E01':'SIGNAL ANALYSIS','E02':'DATA ARCHIVE','E03':'SUPPLY STORE','N01':'RECEIVING','S01':'STERILIZATION'}
colors=json.loads((R/'SourceAssets/B4_FullFloor/guide_colors.json').read_text())
for code,name in names.items():
 im=Image.new('RGBA',(1024,256));d=ImageDraw.Draw(im);c=tuple(int(colors[code][i:i+2],16) for i in [0,2,4])+(255,);txt(d,(20,40),code,116,c);txt(d,(300,98),name,32,c);d.polygon([(925,57),(1005,128),(925,199),(925,151),(860,151),(860,105),(925,105)],fill=c);im.save(O/('BS_Guide_'+code+'.png'))
(H/'guide_colors.json').write_text(json.dumps(colors,indent=2));print('B3 textures ready')
