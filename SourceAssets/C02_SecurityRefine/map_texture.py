"""Build monitor 05 from current B5 geometry; no manually invented nodes. 송예찬."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,math
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B5/Textures'
data=R/'Docs/도면/Decision/원형공동/facility_layout.json';way=R/'Docs/도면/Decision/원형공동/B5_안내체계/wayfinding_plan.json'
floor=next(f for f in json.loads(data.read_text(encoding='utf-8'))['floors'] if f['id']=='B5');rooms=floor['rooms'];links=floor['tunnels'];assert len(rooms)==15 and len(links)==19
names={d['code']:d for d in json.loads(way.read_text(encoding='utf-8'))['destinations']}
font=lambda s:ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf',s)
bg=(8,18,24);ink=(196,218,223);dim=(81,127,141);teal=(80,182,190);green=(131,210,172);amber=(223,169,83)
im=Image.new('RGB',(1600,1000),bg);d=ImageDraw.Draw(im)
d.rectangle((0,0,1600,84),fill=(19,37,47));d.text((36,26),'B5 / SECURITY OVERVIEW',font=font(30),fill=ink);d.ellipse((1501,31,1517,47),fill=green)
# Same scale on X/v, north up, actual room radii and tunnel endpoints.
scale=4.10;cx,cy=660,504
xy=lambda x,v:(cx+x*scale,cy+v*scale)
for x in range(95,1230,41):d.line((x,112,x,899),fill=(15,29,36))
for y in range(135,900,41):d.line((90,y,1230,y),fill=(15,29,36))
for t in links:
 p=xy(*t['p']);q=xy(*t['q']);d.line((*p,*q),fill=(42,74,85),width=round(t['w']*scale));d.line((*p,*q),fill=(94,145,152) if 'C02' in (t['a'],t['b']) else (53,102,116),width=3)
for r in rooms:
 x,y=xy(r['x'],r['v']);radius=r['r']*scale;code=r['id'];color=amber if code=='S01' else green if code=='C02' else teal
 d.ellipse((x-radius,y-radius,x+radius,y+radius),fill=(13,34,43),outline=color,width=4 if code=='C02' else 2)
 # All labels are screen annotations, not world-space nameplates.
 f=font(22 if r['r']>=7 else 18);b=d.textbbox((0,0),code,font=f);d.text((x-(b[2]-b[0])/2,y-(b[3]-b[1])/2-b[1]),code,font=f,fill=ink)
 if code=='C02':d.ellipse((x-radius-7,y-radius-7,x+radius+7,y+radius+7),outline=green,width=2)
for txt,x,y in [('SECTOR W',160,190),('SECTOR E',1000,190),('SECTOR N',705,166),('SECTOR S',705,835),('SECTOR C',600,651)]:d.text((x,y),txt,font=font(21),fill=dim)
d.line((1262,113,1262,897),fill=(38,68,81),width=2)
for i,(a,b,c) in enumerate([('LAYOUT','15 DESTINATIONS',ink),('LINKS','19 CORRIDORS',ink),('SELECTED','C02 / SECURITY',green),('SECTOR S','RESTRICTED',amber)]):
 y=145+i*148;d.text((1290,y),a,font=font(20),fill=dim);d.text((1290,y+35),b,font=font(19),fill=c)
d.polygon([(1486,779),(1473,806),(1499,806)],fill=ink);d.text((1478,818),'N',font=font(22),fill=ink)
d.line((1300,881,1382,881),fill=dim,width=3);d.text((1393,868),'20 m',font=font(20),fill=dim)
d.line((35,927,1565,927),fill=dim,width=2);d.text((35,951),'ASE  /  OPERATIONS SYSTEM     B5-C02',font=font(22),fill=dim);d.text((1265,951),'PLAN REV. 03',font=font(22),fill=dim)
im.save(O/'SC_Display_05.png')
atlas=Image.new('RGB',(1024,1024),(16,30,36));a=ImageDraw.Draw(atlas)
for row,(title,sub) in enumerate([('AV SIGNAL ROUTER','ENCODERS / VIDEO DISTRIBUTION'),('CONTROLLED KEYS','AUTHORISED ISSUE / 12 POSITIONS'),('BADGE RETURN','SEALED COLLECTION / SHIFT HANDOVER'),('EVIDENCE STORAGE','RESTRICTED / SEALED CASES'),('SEALED / SECURE','CHAIN OF CUSTODY'),('SHIFT EQUIPMENT','HEADSETS / CHARGED SPARES'),('AIR RETURN / C02','FILTER BANK / MAINTAIN CLEARANCE'),('ASE DISPLAY / M42','DP / DATA / DC POWER')]):
 y=row*128;a.line((24,y+12,1000,y+12),fill=teal,width=3);a.text((27,y+26),title,font=font(37),fill=ink);a.text((29,y+82),sub,font=font(19),fill=dim)
atlas.save(O/'SR_EquipmentPrint.png')
(H/'map_manifest.json').write_text(json.dumps({'author':'송예찬','source':str(data.relative_to(R)),'sha256':hashlib.sha256(data.read_bytes()).hexdigest(),'rooms':[r['id'] for r in rooms],'links':[t['id'] for t in links],'sameScaleXZ':True,'static':True},ensure_ascii=False,indent=2),encoding='utf-8')
print('Current B5 map: 15 destinations / 19 corridors; equipment atlas created')
