"""Create an engineering drawing from the actual route coordinates, no scene markers."""
from pathlib import Path
import json,math,html
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;R=H.parents[1]
D=R/'Docs/도면/Decision/원형공동/B2_배관통로'
plan=json.loads((R/'SourceAssets/B2_FullFloor/plan.json').read_text(encoding='utf8'))
detail=json.loads((H/'layout.json').read_text(encoding='utf8'))
upper={t['id'] for t in detail['tunnels']}
im=Image.new('RGB',(1800,1220),'#11191f');d=ImageDraw.Draw(im)
font='C:/Windows/Fonts/malgun.ttf'
def text(p,s,size=22,color='#e4e8eb'):d.text(p,s,font=ImageFont.truetype(font,size),fill=color)
text((60,35),'B2 기계층  |  복층 정비 통로',38);text((60,94),'V0.02 · 2026-11-10 · 작성자 송예찬',20,'#aeb9c1')
xs=[r['x'] for r in plan['rooms']];zs=[r['v'] for r in plan['rooms']];xmin=min(xs)-15;zmin=min(zs)-15;scale=min(1030/(max(xs)-xmin+15),900/(max(zs)-zmin+15))
def xy(x,z):return (65+(x-xmin)*scale,170+(z-zmin)*scale)
for t in plan['tunnels']:
 code=t['id'].split('-')[1];pp=[xy(*v) for v in t['path']];col='#e57955' if code in upper else '#829098';d.line(pp,fill=col,width=9)
 if code in upper:d.line(pp,fill='#ffccb2',width=2)
 p=pp[len(pp)//2] if len(pp)>2 else ((pp[0][0]+pp[1][0])/2,(pp[0][1]+pp[1][1])/2)
 d.rounded_rectangle((p[0]-22,p[1]-12,p[0]+22,p[1]+14),5,fill='#11191f');text((p[0]-19,p[1]-12),code,16,col)
for r in plan['rooms']:
 x,y=xy(r['x'],r['v']);rr=r['r']*scale;d.ellipse((x-rr,y-rr,x+rr,y+rr),fill='#24343e',outline='#a0b4c1',width=2);text((x-20,y-13),r['id'],18)
text((1160,170),'통로 단면',28)
cx,cy,sc=1440,530,85
pts=[]
for i in range(241):
 a=-math.asin(1.35/2.5)+(math.pi+2*math.asin(1.35/2.5))*i/240;x=2.5*math.cos(a);y=1.35+2.5*math.sin(a);pts.append((cx+x*sc,cy-y*sc))
d.line(pts,fill='#8b9da7',width=8);floor=cy;d.line((cx-2.1*sc,floor,cx+2.1*sc,floor),fill='#9cabb3',width=10)
deck=cy-2.42*sc;d.line((cx-.75*sc,deck,cx+.75*sc,deck),fill='#eaaa7c',width=8)
for x in [cx-.79*sc,cx+.79*sc]:d.line((x,deck,x,deck-.86*sc),fill='#9cabb3',width=4)
for x,y,rr in [(-1.3,2.95,.15),(1.3,2.9,.12),(-1.32,3.3,.065),(1.32,3.3,.045)]:d.ellipse((cx+(x-rr)*sc,cy-(y+rr)*sc,cx+(x+rr)*sc,cy-(y-rr)*sc),fill='#ca6950',outline='#edb393',width=2)
text((1190,570),'하부: 서서 이동 / 계단 옆 우회',21);text((1190,610),'상부: 앉아서 통과하는 그레이팅',21,'#edac8c');text((1190,650),'데크 2.42m · 폭 1.50m',21);text((1190,690),'상부 여유 약 1.30–1.43m',21);text((1190,730),'양 끝 13단 계단 / 별도 로딩 없음',21)
text((1160,810),'조명과 구조',28)
for i,s in enumerate(['상부 공급·회수 배관 + 정비 그레이팅','원형 보호망등 + 금속 갓 펜던트','난간·발끝막이·받침보·체결부','기존 공동 출입구와 평면 유지']):text((1180,858+i*36),s,21)
text((65,1090),'주황: 복층 19개   /   회색: T04·T06 짧은 단층 접속부',25)
text((65,1140),'상부는 통로 안의 계단으로 오르내립니다. C02 공동의 기존 3.6m 메자닌은 별도 높이입니다.',22,'#b6c1c8')
im.save(D/'B2_복층통로.png')
old=json.loads((D/'as_built_layout.json').read_text(encoding='utf8'));old['detailRevision']='2026-11-10 V0.02';old['upperServiceRoutes']=detail;old['lightingIntent']='Dark iron with red practical fixtures; white primary emitters removed.';(D/'as_built_layout.json').write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf8')
print('Drawing and as-built specification updated')
