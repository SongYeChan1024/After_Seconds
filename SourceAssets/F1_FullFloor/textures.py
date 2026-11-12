from pathlib import Path
import sys,json
H=Path(__file__).resolve().parent;R=H.parents[1];sys.path.insert(0,str(R/'Unity/After_Seconds_Build_V0.01/Temp/ZFightingReview/deps'))
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np
E=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/1F/Textures';E.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1112);n=1024
coarse=Image.fromarray(rng.integers(165,254,(64,64),dtype=np.uint8)).resize((n,n),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(5));a=np.asarray(coarse,dtype=np.float32)+rng.normal(0,5,(n,n));im=Image.fromarray(np.uint8(np.clip(a,0,255))).convert('RGB');d=ImageDraw.Draw(im)
for i in range(800):
 x,y=rng.integers(0,n,2);w=int(rng.integers(1,10));h=int(rng.integers(1,5));c=int(rng.integers(100,185));d.ellipse((int(x),int(y),int(x+w),int(y+h)),fill=(c,c,c))
im=Image.blend(Image.new('RGB',(n,n),(250,250,250)),im,.36);im.save(E/'F1_SurfaceWear.png')
coarse=Image.fromarray(rng.integers(135,225,(128,128),dtype=np.uint8)).resize((n,n),Image.Resampling.BICUBIC);a=np.asarray(coarse,dtype=np.float32)+rng.normal(0,11,(n,n));im=Image.fromarray(np.uint8(np.clip(a,0,255))).convert('RGB');d=ImageDraw.Draw(im)
for i in range(24):
 x,y=rng.integers(0,n,2);pts=[(int(x),int(y))]
 for j in range(5):x+=int(rng.integers(-25,26));y+=int(rng.integers(5,30));pts.append((int(x),int(y)))
 d.line(pts,fill=(88,89,83),width=1)
im.save(E/'F1_Concrete.png')
out=E.parent.parent.parent/'Props/1F/Textures';out.mkdir(parents=True,exist_ok=True)
im=Image.new('RGB',(2048,2048));d=ImageDraw.Draw(im)
def font(n,b=False):return ImageFont.truetype('C:/Windows/Fonts/'+('consolab.ttf' if b else 'consola.ttf'),n)
titles=['DISPATCH REGISTER','DELIVERY QUEUE','STOCK / RECONCILE','PALLET INDEX','SHIFT HANDOVER','GATE / ACCESS LOG','RADIO CHANNELS','STAFF ROSTER','MAINTENANCE DUE','VOICE MEMO','SHIPPING MANIFEST','VEHICLE CHECKLIST','INSPECTION RECORD','SHIFT BRIEF','STOCK TRANSFER','DUTY REPORT']
for i,title in enumerate(titles):
 x=i%4*512;y=i//4*512;paper=i>=10;bg=(226,224,202) if paper else (22,32,29);fg=(40,51,45) if paper else (193,213,192);muted=(116,127,106) if paper else (101,146,123)
 d.rectangle((x,y,x+511,y+511),fill=bg);d.rectangle((x+22,y+24,x+490,y+68),fill=(190,199,177) if paper else (43,67,54));d.text((x+32,y+35),title,font=font(24,True),fill=fg);d.text((x+32,y+85),'1F / FACTORY SERVICES',font=font(17),fill=muted)
 lines=['REF. F01-026  /  SHIFT A','BAY 02     DELIVERY 04','COUNT ______  CHECK _____','STAFF ___________________','TIME  ______  SIGN ______','NOTES ___________________','________________________'] if paper else ['BAY   LOAD   STATUS','02    014    RECEIVED','03    027    CHECKED','01    006    ON HOLD','RADIO CH. 04 / READY']
 for j,line in enumerate(lines):d.text((x+32,y+138+j*40),line,font=font(20),fill=fg);d.line((x+32,y+168+j*40,x+477,y+168+j*40),fill=muted,width=1)
 d.text((x+32,y+468),'INTERNAL COPY / '+str(i+1).zfill(2),font=font(16),fill=muted)
im.save(out/'F1_WorkRecords.png');print('1F textures saved')
