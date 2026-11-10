from pathlib import Path
import json,math
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;R=H.parents[1];data=json.loads((H/'layout.json').read_text(encoding='utf8'));models=json.loads((H/'models.json').read_text())
dest=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/06.Data/AssetSources/B2_DomeNetwork.json'
record={'version':'0.01','author':'송예찬','date':'2026-11-10','source':'Blender 5.2.2 LTS','scene':'Assets/Afrer_Seconds/01.Scenes/Stage/Level_B2_Circular.unity','sources':['SourceAssets/B2_DomeNetwork/build.py','SourceAssets/B2_DomeNetwork/connections.py'],'description':'B2 functional dome plant density; 3 new ring mezzanines, existing C02 connection, 7 upper junctions on 6 tunnels. Static level art only.','models':[],'placements':data['placements']}
for name,m in models.items():record['models'].append({'name':name,'asset':Path(m['asset']).relative_to(R/'Unity/After_Seconds_Build_V0.01').as_posix(),'triangles':m['triangles'],'lod':bool(m.get('distance_only'))})
dest.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
D=R/'Docs/도면/Decision/원형공동/B2_배관통로';original=json.loads((R/'SourceAssets/B2_FullFloor/plan.json').read_text(encoding='utf8'))
im=Image.new('RGB',(1800,1220),'#11191f');draw=ImageDraw.Draw(im)
def text(p,s,size=22,col='#e4e8eb'):draw.text(p,s,font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',size),fill=col)
text((60,35),'B2 기계층 | 공동 설비·상부 정비 동선',38);text((60,94),'V0.03 · 2026-11-10 · 작성자 송예찬 · Unity 실배치 기준',20,'#aeb9c1')
rooms={r['id']:r for r in data['rooms']};scale=3.8
def xy(x,v):return (70+(x+140)*scale,150+(v+90)*scale)
for t in original['tunnels']:
 code=t['id'].split('-')[1];pp=[xy(*p) for p in t['path']];on=code in data['ends'];col='#6cd6ba' if on else '#697983';draw.line(pp,fill=col,width=7 if on else 4)
 p=pp[len(pp)//2] if len(pp)>2 else ((pp[0][0]+pp[1][0])/2,(pp[0][1]+pp[1][1])/2);text((p[0]-17,p[1]-10),code,16,col)
for id,r in rooms.items():
 x,y=xy(r['x'],r['v']);rr=r['r']*scale;on=id in ['E01','E02','W02','C02'];draw.ellipse((x-rr,y-rr,x+rr,y+rr),fill='#24343e',outline='#6cd6ba' if on else '#a0b4c1',width=3 if on else 2)
 if id in data['decks']:
  dr=data['decks'][id]*scale;draw.ellipse((x-dr,y-dr,x+dr,y+dr),outline='#dfa478',width=5)
 text((x-20,y-12),id,18)
for t in data['tunnels']:
 for id in data['ends'][t['id']]:
  r=rooms[id];d=next(d for d in r['doors'] if d['id']=='B2-'+t['id']);p=xy(r['x']+d['x'],r['v']-d['z']);draw.ellipse((p[0]-5,p[1]-5,p[0]+5,p[1]+5),fill='#f6c78f')
text((1180,168),'선택 공동: 상하 이동과 우회',28)
for i,s in enumerate(['C02 냉각 → T01 / 기존 U형 메자닌','W02 예비 전력 → T11·T12','E01 급수 → T14·T15','E02 공조 → T15·T16']):text((1190,225+i*45),s,20)
text((1180,455),'연결 단면',28)
draw.line((1190,745,1710,745),fill='#8195a1',width=7)
draw.line((1190,624,1320,624,1390,565,1690,565),fill='#dfa478',width=8)
draw.line((1190,553,1305,553,1400,450),fill='#8195a1',width=5)
draw.line((1390,565,1390,745),fill='#8195a1',width=5);draw.line((1590,565,1470,745),fill='#9eacb5',width=5)
text((1185,790),'터널 2.42m → 공동 데크 3.60m',22,'#f6c78f');text((1185,830),'터널: 앉기 / 공동: 서서 정비',22);text((1185,870),'하부 보행과 장비 전면 접근 유지',22)
text((60,970),'청록: 공동 상부에 연결한 6개 통로   /   황토: 정비 메자닌·7개 접속부',25)
text((60,1020),'추가 설비 97배치: 급수 탱크·공조 플레넘·연료 보조 탱크·분배 매니폴드·모터·정비 장비',23)
text((60,1070),'기존 19개 복층 통로 유지. 선택한 끝의 계단은 상부 직결로 대체하고 나머지 진입은 유지.',23)
text((60,1120),'활성 광원 158개 유지 · 배관 공급/회수 연결 · 게임 UI 및 게임 로직 추가 없음',22,'#adbcc5')
im.save(D/'B2_공동상부연결.png')
ab=json.loads((D/'as_built_layout.json').read_text(encoding='utf8'));ab['detailRevision']='2026-11-10 V0.03';ab['domeServiceNetwork']=data;(D/'as_built_layout.json').write_text(json.dumps(ab,ensure_ascii=False,indent=2),encoding='utf8')
print('Recorded',len(models),'models and latest drawing')
