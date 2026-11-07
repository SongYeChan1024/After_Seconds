"""Static instrument optics and textile PBR. Author 송예찬."""
import json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B5/Textures';O.mkdir(exist_ok=True)
font=lambda s:ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf',s)
BG=(7,17,23);INK=(195,218,223);DIM=(83,120,131);TEAL=(70,188,182);GREEN=(144,210,166);AMBER=(232,180,79)
titles=['ISOLATION / OBSERVATION','PATIENT VITALS','ULTRASOUND / B-MODE','STERILIZATION / CYCLE','COOLANT / PRESSURE','DISTRIBUTION / LOAD','AIR HANDLING / PRESSURE','STOCK / INVENTORY','COLD STORAGE / TEMPERATURE','WAREWASH / RINSE','B5 / OPERATIONS','ISOLATION / OCCUPANCY','FACILITY / TOPOLOGY','AIR / DIFFERENTIAL PRESSURE','RECORDING / ARRAY','TEST CELL / ISOLATED','MAINTENANCE / SCHEDULE','CARGO LIFT / B5']
plan=json.loads((H/'plan.json').read_text(encoding='utf-8'))
for i,title in enumerate(titles,1):
 im=Image.new('RGB',(1280,800),BG);d=ImageDraw.Draw(im);d.rectangle((0,0,1280,70),fill=(18,36,44));d.text((30,18),title,font=font(28),fill=INK);d.text((30,755),'ASE  /  LOCAL TERMINAL      00:42:16',font=font(18),fill=DIM);d.line((30,735,1250,735),fill=DIM,width=2)
 if i in [11,13]:
  def xy(r):return(640+r['x']*4.25,398+r['v']*3.6)
  for t in plan['tunnels']:
   p,q=xy(plan['rooms'][t['a']]),xy(plan['rooms'][t['b']]);d.line((p,q),fill=DIM,width=6)
  for code,r in plan['rooms'].items():
   x,y=xy(r);d.ellipse((x-22,y-22,x+22,y+22),fill=(22,59,67),outline=TEAL,width=3);d.text((x-26,y+26),code,font=font(19),fill=INK)
  d.text((35,100),'B5  /  15 NODES  /  19 LINKS',font=font(23),fill=GREEN)
 elif i==3:
  rng=np.random.default_rng(333);arr=rng.normal(56,20,(530,850));yy,xx=np.indices(arr.shape);mask=(abs(xx-425)<yy*.76)&(yy>40);arr=np.where(mask,arr+32*np.sin(np.sqrt((xx-425)**2+(yy-120)**2)*.055),5);a=np.clip(arr,0,255).astype('uint8');im.paste(Image.fromarray(a).convert('RGB'),(40,135));d=ImageDraw.Draw(im)
  for y in range(160,650,70):d.line((870,y,895,y),fill=INK,width=2)
  for j,t in enumerate(['B-MODE','7.5 MHz','GAIN  48','DEPTH  80 mm','FREEZE','FRAME  0124']):d.text((960,160+j*75),t,font=font(25),fill=TEAL if j==4 else INK)
 elif i in [2,1,12]:
  for j,(label,value,col) in enumerate([('ECG  /  II','72',GREEN),('SpO2','98',TEAL),('RESP','16',AMBER)]):
   y=160+j*177;d.text((38,y-48),label,font=font(23),fill=col);pts=[]
   for x in range(820):
    phase=(x+37*j)%155;v=math.sin(x*.045)*4
    if j==0:v+=-48*math.exp(-((phase-60)/3)**2)+19*math.exp(-((phase-65)/6)**2)
    elif j==1:v+=28*math.sin(phase/155*math.tau)
    else:v+=22*math.sin(x*.024)
    pts.append((40+x,y+v))
   d.line(pts,fill=col,width=3);d.text((960,y-45),value,font=font(73),fill=col)
 elif i in [5,6,7,14]:
  for j in range(3):
   y=180+j*176;d.rounded_rectangle((40,y-55,350,y+65),radius=10,outline=DIM,width=2);d.text((65,y-25),['SUPPLY','RETURN','FILTER'][j] if i!=6 else ['BUS A','BUS B','UPS'][j],font=font(29),fill=INK);d.line((350,y,650,y,650,350,870,350),fill=TEAL,width=7);d.ellipse((600,y-30,660,y+30),outline=INK,width=4);d.polygon([(614,y-15),(648,y),(614,y+15)],fill=TEAL)
  d.rounded_rectangle((875,230,1220,490),radius=12,outline=DIM,width=3);d.text((910,270),'SYSTEM READY',font=font(27),fill=GREEN);d.text((940,335),'2.40 bar' if i==5 else '218 Pa' if i in [7,14] else '400 V',font=font(43),fill=INK)
 elif i==16:
  d.rounded_rectangle((45,130,1235,360),radius=18,fill=(55,35,24),outline=AMBER,width=3);d.text((85,170),'TEST CELL ISOLATED',font=font(55),fill=AMBER);d.text((85,265),'POWER BUS DISCONNECTED',font=font(32),fill=INK)
  for j,t in enumerate(['INTERLOCK  /  OPEN','SENSOR ARRAY  /  OFFLINE','LAST SESSION  /  ARCHIVED']):d.text((80,420+j*85),t,font=font(29),fill=DIM)
 else:
  labels={4:['CYCLE  04 / HOLD','CHAMBER  121.0 C','PRESSURE  2.1 bar','TIME REMAINING  07:18'],8:['CLEAN LINEN  042','SEALED KITS  028','PPE SETS  064','RETURN BAGS  006'],9:['CHAMBER A  +3.2 C','CHAMBER B  +3.5 C','DOOR SEAL  /  OK','DEFROST  /  STANDBY'],10:['RINSE  82.0 C','WASH  65.0 C','CYCLE  03:24','FILTER  /  CLEAR'],15:['CHANNELS  24 / 24','ARCHIVE  82 %','MIRROR  /  READY','UPS  98 %'],18:['LEVEL  B5','LOAD  0000 kg','DOORS  /  CLOSED','DRIVE  /  ISOLATED']}.get(i,['FILTER A  /  VERIFIED','FILTER B  /  VERIFIED','INSPECTION  /  LOGGED','SERVICE  /  SCHEDULED'])
  for j,txt in enumerate(labels):
   y=118+j*145;d.rounded_rectangle((35,y,1245,y+119),radius=9,fill=(15,31,39),outline=(31,55,63),width=2);d.text((65,y+35),txt,font=font(34),fill=INK);d.ellipse((1160,y+46,1188,y+74),fill=GREEN)
 im.save(O/f'RD_Display_{i:02}.png')
rng=np.random.default_rng(118);n=512;y,x=np.indices((n,n));weave=(np.sin(x*math.pi/2)+np.sin(y*math.pi/2))*3+rng.normal(0,1,(n,n));base=np.clip(np.array([119,140,143])+weave[:,:,None],0,255).astype('uint8');Image.fromarray(base).save(O/'RD_Fabric_Base.png');normal=np.zeros((n,n,3),dtype='uint8');normal[:,:,0]=np.clip(128+np.sin(x*math.pi/2)*8,0,255);normal[:,:,1]=np.clip(128+np.sin(y*math.pi/2)*8,0,255);normal[:,:,2]=255;Image.fromarray(normal).save(O/'RD_Fabric_Normal.png');metal=np.zeros((n,n,4),dtype='uint8');metal[:,:,3]=35;Image.fromarray(metal).save(O/'RD_Fabric_MetalSmooth.png')
print('18 role-specific static screens, fabric PBR 3 maps')
