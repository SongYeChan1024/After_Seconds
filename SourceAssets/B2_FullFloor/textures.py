from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,numpy as np
H=Path(__file__).resolve().parent;R=H.parents[1];A=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model';T=A/'Environment/B2/Textures';P=A/'Props/B2/Textures'
f=lambda s:ImageFont.truetype('C:/Windows/Fonts/consola.ttf',s)
for i,title,lines in [(11,'MAIN DISTRIBUTION',['TR-201  /  400 V','630 kVA  |  50 Hz','ISOLATE BEFORE SERVICE']), (12,'AIR FILTER / F7',['AHU-202 / SUPPLY AIR','FILTER DP  124 Pa','REPLACE AT 250 Pa']), (13,'EXTRACT FAN',['EF-201 / MECHANICAL','KEEP GUARD IN PLACE','LOCK OUT BEFORE SERVICE']), (14,'WATER TREATMENT',['WT-201 / DUPLEX FILTER','INLET 4.2 / OUTLET 3.8 bar','BACKWASH EACH SHIFT']), (15,'SEALED WASTE TANK',['WW-201 / PROCESS RETURN','CLOSED SYSTEM / 1800 L','INSPECT LEVEL BEFORE TRANSFER']), (16,'MAINTENANCE SPARES',['MECH / SEALS / COUPLINGS','LOT 02-047 / BIN 06','RETURN CLEAN PARTS ONLY']), (22,'B2 / FREIGHT LIFT',['SAFE LOAD  2000 kg','KEEP LANDING CLEAR','SERVICE LEVEL / B1'])]:
 im=Image.new('RGB',(1024,512),(193,197,187));d=ImageDraw.Draw(im);d.rectangle((12,12,1012,500),outline=(40,46,48),width=5);d.text((35,32),title,font=f(43),fill=(31,38,40))
 for j,txt in enumerate(lines):d.text((35,155+j*100),txt,font=f(30),fill=(120,37,31) if j==2 else (38,45,46))
 im.save(T/f'BM_Display_{i:02}.png')
# GLTF ORM: B=metallic, G=roughness -> Unity R=metallic A=smoothness.
orm=np.array(Image.open(P/'B2_EmergencyGenerator_0_1.png').convert('RGB'));out=np.zeros((*orm.shape[:2],4),np.uint8);out[:,:,:3]=orm[:,:,2,None];out[:,:,3]=255-orm[:,:,1];Image.fromarray(out).save(P/'B2_EmergencyGenerator_MetalSmooth.png')
plan=json.loads((H/'plan.json').read_text(encoding='utf8'));colors=['B88E68','679BA7','C9AB67','83A99D','9AA9BA','BF7D76','B89ABD','BC9678','94AB81','A5957D','7FA6AB','A1A9B7','A9A77B','7A9B91','A28A9E'];names=['CENTRIFUGE','COOLING / PUMPS','DISTRIBUTION','PLANT CONTROL','STAIR A','STAIR B','FREIGHT','MAIN POWER','BACKUP POWER','MAINTENANCE','WATER SUPPLY','AIR FILTER','WASTE WATER','MAIN VENTILATION','PLANT SERVICE'];guides={}
for r,col,label in zip(plan['rooms'],colors,names):
 rgb=tuple(int(col[i:i+2],16) for i in (0,2,4));guides[r['id']]={'hex':col,'label':label};im=Image.new('RGBA',(1024,256),(0,0,0,0));d=ImageDraw.Draw(im);d.rectangle((8,8,1016,248),outline=rgb+(235,),width=6);d.text((34,40),r['id']+'  /  '+label,font=f(44),fill=rgb+(245,));d.polygon([(770,170),(920,170),(920,135),(990,195),(920,235),(920,200),(770,200)],fill=rgb+(245,));im.save(T/('BM_Guide_'+r['id']+'.png'))
(H/'guide_colors.json').write_text(json.dumps(guides,indent=2),encoding='utf8')
print('B2 materials and destination labels prepared')
