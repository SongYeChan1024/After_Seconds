"""Physical finishes, flush equipment printing and static operational LCDs. 송예찬."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B5/Textures';O.mkdir(exist_ok=True)
font='C:/Windows/Fonts/consola.ttf';f=lambda n:ImageFont.truetype(font,n)
names=['POSITION EXCHANGE / CALIBRATION','INSTRUMENTED TEST SURROGATE','OPTICAL TRACKING / ARRAY','SEALED MEALS / STAFF','EXTERNAL SUPPLY / RECEIVING','REGENERATION / CLOSED TRAYS','NUTRITION / CONTROLLED ISSUE','RESTRICTED / SEALED CASSETTES','SOILED PPE / RETURN','BAG / SEAL / CONTAIN','WASH / BOOT SOLES','CLEAN PPE / DONNING','DRY / AIR CHECK','A / CONSUMABLES','B / SERVICE PARTS','C / SEALED STOCK','D / BULK RESERVE','INBOUND / SCAN AND CHECK','OUTBOUND / VERIFIED','FREIGHT LIFT / B5','LOAD LIMIT / 2000 kg','KEEP SILL CLEAR','POWER / SUPPLY OK','INTERLOCK / READY','STANDBY / LOCAL','ISOLATE BEFORE ACCESS','DO NOT OPEN / ACTIVE CYCLE','COLD CHAIN / SEALED','RETURN / EMPTY CONTAINERS','SENSOR / PATCH FIELD','TRACKING / CAPTURE ARMED','ASSET / SERIAL 0511']
im=Image.new('RGB',(4096,2048),(182,194,193));d=ImageDraw.Draw(im)
for i,n in enumerate(names):
 x=i%4*1024;y=i//4*256;d.rectangle((x+4,y+4,x+1019,y+251),fill=(184,199,197),outline=(42,64,68),width=8)
 d.rectangle((x+22,y+24,x+1000,y+80),fill=(32,60,68));d.text((x+38,y+30),f'AFTER SECONDS   /   {i+1:02}',font=f(36),fill=(218,230,227))
 d.text((x+30,y+105),n,font=f(32),fill=(22,39,45));d.text((x+32,y+198),'B5  |  CONTROLLED FACILITY STOCK',font=f(23),fill=(45,63,66))
 for j in range(75):
  if ((j*37+i*11)%13)>5:d.rectangle((x+660+j*4,y+180,x+662+j*4,y+234),fill=(24,41,44))
im.save(O/'OD_Tags.png');(H/'labels.json').write_text(json.dumps(names,indent=2),encoding='utf-8')
rng=np.random.default_rng(5811)
for name,col,metal,rough in [('Carton',(136,120,88),0,.83),('Powder',(62,85,96),.35,.53),('Polymer',(144,164,163),.03,.58)]:
 noise=rng.normal(0,1.2,(1024,1024));noise+=np.sin(np.arange(1024)[None,:]*2.1)*(.8 if name=='Carton' else .18)
 base=np.clip(np.array(col)[None,None,:]+noise[:,:,None],0,255).astype('uint8');Image.fromarray(base).save(O/f'OD_{name}_Base.png')
 normal=np.zeros((1024,1024,3),dtype='uint8');normal[:,:,0]=np.clip(128+np.gradient(noise,axis=1)*1.2,0,255);normal[:,:,1]=np.clip(128+np.gradient(noise,axis=0)*1.2,0,255);normal[:,:,2]=255;Image.fromarray(normal).save(O/f'OD_{name}_Normal.png')
 spec=np.zeros((1024,1024,4),dtype='uint8');spec[:,:,0]=int(metal*255);spec[:,:,3]=np.clip((1-rough)*255+noise,0,255);Image.fromarray(spec).save(O/f'OD_{name}_MetalSmooth.png')
for name,heading,lines in [('Stock','GOODS / INTAKE CONTROL',['SCAN > WEIGH > STORE','CONSIGNMENT  AF-0511','QUANTITY  MATCHED','STORAGE BAY  A / 04']),('Test','EXCHANGE / TRACKING',['SURROGATE 01    FIXTURE LOCKED','REFERENCE FRAME    S01-CELL','POSITION DELTA     0.000 m','CAPTURE BUFFER     STANDBY']),('Food','SEALED MEAL / REGEN',['STAFF DISTRIBUTION','CART 02   DOOR SEALED','BATCH INTAKE  VERIFIED','REGEN CYCLE   READY']),('Issue','CONTROLLED / ISSUE',['NUTRITION CASSETTES','SEALED STOCK  08 / 12','ACCESS  LOCKED','ISSUE RECORD  REQUIRED']),('Decon','DECONTAMINATION',['RETURN  > WASH  > CLEAN','WATER LOOP     READY','EXTRACT FLOW   NORMAL','PPE DISPENSE   SEALED']),('Lift','B5 / FREIGHT',['2000 kg  MAXIMUM LOAD','B5  LOWER LANDING','DOOR INTERLOCK  CLOSED','CALL UP / DOWN']),('Power','POWER / DISTRIBUTION',['SUPPLY  A  CONNECTED','LOAD     062 %','LOCAL / ISOLATION READY','FAULT LOG  CLEAR'])]:
 im=Image.new('RGB',(1024,640),(8,19,25));d=ImageDraw.Draw(im);d.rectangle((18,18,1006,104),fill=(26,68,77));d.text((40,35),heading,font=f(43),fill=(142,217,218))
 for i,line in enumerate(lines):d.text((38,136+i*66),line,font=f(32),fill=(175,208,207));d.line((38,187+i*66,985,187+i*66),fill=(30,63,72),width=2)
 for x in range(40,986,40):d.line((x,443,x,594),fill=(20,43,53))
 for y in range(443,595,30):d.line((40,y,985,y),fill=(20,43,53))
 if name=='Test':
  for j,c in enumerate([(89,187,182),(198,154,92),(119,157,201)]):
   pts=[(x,510+j*14+int(9*np.sin(x*.018+j))) for x in range(40,986,3)];d.line(pts,fill=c,width=3)
 else:
  for j in range(12):d.rounded_rectangle((46+j*77,470,97+j*77,566),radius=7,fill=(45,106,107) if j<8 else (29,52,61))
 im.save(O/f'OD_Screen_{name}.png')
print('17 textures: 9 PBR maps, 1 printed atlas and 7 static screens ready')
