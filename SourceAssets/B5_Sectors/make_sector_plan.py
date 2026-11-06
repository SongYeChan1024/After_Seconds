"""Legacy seven-dome generator. Superseded by full_sector_plan.py."""
raise RuntimeError('구 7개 돔 생성기는 사용 종료했습니다. full_sector_plan.py를 사용하세요.')
from pathlib import Path
import json, math, shutil, hashlib
from xml.sax.saxutils import escape
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[2]
DESIGN=ROOT/'Docs/도면/Decision/원형공동'
OUT=DESIGN/'B5_섹터'
DELIVERY=Path('C:/Users/503-26/Documents/Codex/2026-11-06/dl/outputs/after_seconds_reviewed/B5_섹터')
OUT.mkdir(parents=True,exist_ok=True)
data=json.loads((DESIGN/'facility_layout.json').read_text('utf-8'))
floor=next(f for f in data['floors'] if f['id']=='B5')
rooms={r['id']:r for r in floor['rooms'] if not r.get('wing')}
ref=json.loads((OUT/'scene_reference.json').read_text('utf-8'))
assert len(ref['domes'])==7 and len(ref['tunnels'])==7
assert all(v['active'] for v in ref['domes']+ref['tunnels'])
assert not ref['dirty'] and not ref['playing']
ids=['C01','C02','C03','C04','VA','VB','VL']
names=['피험체 격리','경비·모니터링','냉각','유틸리티','계단 A','계단 B','화물 승강기']
focus=[
 '포드 · 침상 · 생활 구획 · 배식·위생 · 관찰 시야',
 '관제 데스크 · 기록 · 보안 설비 · 감시와 우회',
 '펌프 · 탱크 · 연결 배관 · 정비 통로 · 엄폐',
 '배전 · 공조 · 점검 장비 · 배관·케이블 접속',
 '계단 · 참 · 난간 · 방화 구획 · 상층 접점',
 '계단 · 참 · 난간 · 우회 동선 · 상층 접점',
 '화물 출입 · 승강로 · 문 수납 · 적재 여유',
]
status=['부분 제작 / 완료 전 재검수','기본 구조 / 미완료','기본 구조 / 미완료','기본 구조 / 미완료','외피 / 계단·참 미완료','외피 / 계단·참 미완료','외피 / 승강로 미완료']
sector_index={rid:i+1 for i,rid in enumerate(ids)}
stages=['구조·문 접합','프랍·설비','재질·생활 흔적','조명·시야','이동·충돌·성능 검수']
sectors=[]
for i,rid in enumerate(ids):
 r=rooms[rid]
 sectors.append(dict(id=f'B5-S{i+1:02}',number=i+1,room_id=rid,name=names[i],x=r['x'],v=r['v'],radius=r['r'],focus=focus[i],status=status[i],complete=False,checks={s:False for s in stages}))
tunnels=[]
for t in floor['tunnels']:
 if t['a'] in rooms and t['b'] in rooms:
  tunnels.append(dict(id=t['id'],from_sector=sector_index[t['a']],to_sector=sector_index[t['b']],p=t['p'],q=t['q'],length=t['length'],width=t['w'],height=t['h'],status='부분 마감 / 재검수' if t['id']=='B5-T01' else '기본 구조·문 / 미완료',complete=False,checks={s:False for s in stages}))
sequence=['B5-S01','B5-T01','B5-S02','B5-T02','B5-S05','B5-T03','B5-S03','B5-T04','B5-S04','B5-T05','B5-T06','B5-S07','B5-T07','B5-S06','B5-INTEGRATION']
plan=dict(title='B5 현재 제작 구역 섹터도 V0.01',author='송예찬',date='2026-11-06',scope='현재 Unity에 있는 돔 7개 + 복도 구역(7개 터널). 외곽 계획 8실은 이번 구분 밖이며 삭제하지 않음.',scene=ref['scene'],coordinate='X 동쪽, v 남쪽. Unity Z=-v, B5 루트 Y=-82m. 위쪽은 북쪽(+Z).',sectors=sectors,corridor_area=dict(id='B5-COR',name='복도 구역',segments=tunnels,owns=['터널 외피·바닥','리브·문 접합 칼라','양 끝 문틀·문짝·수납 포켓','양면 키패드','복도 조명·배관·트레이','안내선·벽측 엄폐'],boundary='도면 p/q 문 경계에서 인접 돔과 함께 접합 검사. 복도 1개는 단독 작업 단위로 검수.'),completion_stages=stages,work_sequence=sequence,next='B5-S01',numbering_rule='공간 코드 C01~C04, VA/VB/VL 순서. 번호는 작업 우선순위·플레이 이동 순서와 별개.',completion_rule='5단계 검사와 증빙이 모두 끝난 단위만 완료. 기본 구조/파일 존재/일부 배치를 완료로 계산하지 않음.',runtime_scope='AI·문·스위치 동작·미니맵은 사용자 직접 구현. 이번 번호는 제작 관리용 도면 표기.',source_layout_sha256=hashlib.sha256((DESIGN/'facility_layout.json').read_bytes()).hexdigest())
assert {s['room_id'] for s in sectors}==set(rooms)
assert {t['id'] for t in tunnels}=={x['name'].split('_')[1] for x in ref['tunnels']}
assert len(set(sequence))==len(sequence)==15
assert set(sequence[:-1])=={s['id'] for s in sectors}|{t['id'] for t in tunnels}
# Regenerating the drawing must preserve reviewed completion and evidence.
if (OUT/'sector_plan.json').exists():
 previous=json.loads((OUT/'sector_plan.json').read_text('utf-8'))
 old_units={u['id']:u for u in previous['sectors']+previous['corridor_area']['segments']}
 for unit in sectors+tunnels:
  old=old_units.get(unit['id'],{})
  for key in ['status','complete','checks','evidence','review_note','focus']:
   if key in old:unit[key]=old[key]
 for key in ['title','next','latest_decision','updated','pending_revision','scope']:
  if key in previous:plan[key]=previous[key]
completed=sum(u['complete'] for u in sectors+tunnels)
(OUT/'sector_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')

W,H=2300,1700
im=Image.new('RGB',(W,H),'#f4f7fa');dr=ImageDraw.Draw(im)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',f'<rect width="{W}" height="{H}" fill="#f4f7fa"/>']
font_file=Path('C:/Windows/Fonts/malgun.ttf');bold_file=Path('C:/Windows/Fonts/malgunbd.ttf')
fonts={}
def font(size,bold=False):
 key=(size,bold)
 if key not in fonts:fonts[key]=ImageFont.truetype(str(bold_file if bold else font_file),size)
 return fonts[key]
def txt(x,y,text,size=24,color='#233947',bold=False,center=False):
 anchor='mm' if center else 'lm'
 dr.text((x,y),text,font=font(size,bold),fill=color,anchor=anchor)
 svg.append(f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="{"middle" if center else "start"}" dominant-baseline="central" font-family="Malgun Gothic, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}">{escape(text)}</text>')
def rect(x,y,w,h,fill,stroke=None,sw=1,r=0):
 dr.rounded_rectangle((x,y,x+w,y+h),radius=r,fill=fill,outline=stroke,width=sw)
 svg.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{r}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>')
def line(a,b,color,sw=2):
 dr.line([tuple(a),tuple(b)],fill=color,width=sw)
 svg.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke="{color}" stroke-width="{sw}"/>')
def circle(x,y,r,fill,stroke=None,sw=2):
 dr.ellipse((x-r,y-r,x+r,y+r),fill=fill,outline=stroke,width=sw)
 svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{fill or "none"}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>')

txt(65,62,'AFTER SECONDS  /  B5 격리층',26,'#4c687a',True)
txt(65,123,'기존 Unity 구역 · 11개 돔 재편 준비' if plan.get('pending_revision') else '돔 1~7섹터 + 복도 구역',48,bold=True)
txt(65,178,'현재 Unity에 만들어진 7개 돔을 기준으로 구분 · 공간 위치와 터널 연결은 그대로 유지',25,'#586d7d')
txt(2090,66,plan['title'].split()[-1]+' · 2026-11-06',23,'#586d7d',False,True)
rect(45,230,1480,1060,'#ffffff','#d7e1e9',2,16)
rect(1550,230,705,1060,'#ffffff','#d7e1e9',2,16)
S=13.2
def xy(x,v):return (780+x*S,765+v*S)
for x in range(-50,51,10):line(xy(x,-36),xy(x,36),'#eaf0f5',1)
for v in range(-30,31,10):line(xy(-52,v),xy(52,v),'#eaf0f5',1)
txt(85,278,'평면 · 1 m = 13.2 px',21,'#607485')
txt(1415,280,'북 / +Z',21,'#233947',True,True)
line((1415,360),(1415,315),'#233947',4)
line((1415,315),(1405,331),'#233947',4);line((1415,315),(1425,331),'#233947',4)
for t in tunnels:
 a,b=xy(*t['p']),xy(*t['q'])
 line(a,b,'#667b8e',int(t['width']*S)+6)
 line(a,b,'#dfe8ef',int(t['width']*S))
for sec in sectors:
 x,y=xy(sec['x'],sec['v']);rad=sec['radius']*S
 fill='#deeff5' if sec['number']<=4 else '#e8edf4'
 circle(x,y,rad,fill,'#547489',4)
 if sec['number']==1:circle(x,y,rad+7,None,'#26988d',5)
 n=sec['number']
 if rad>=90:
  txt(x,y-38,f'{n}섹터',35,bold=True,center=True)
  txt(x,y+10,sec['name'],24,bold=True,center=True)
  txt(x,y+48,sec['room_id'],22,'#607485',center=True)
 elif rad>=75:
  txt(x,y-25,f'{n}섹터',29,bold=True,center=True);txt(x,y+9,sec['name'],23,bold=True,center=True);txt(x,y+39,sec['room_id'],19,'#607485',center=True)
 else:
  txt(x,y-22,f'{n}섹터',27,bold=True,center=True);txt(x,y+13,sec['room_id'],23,'#607485',center=True)
  txt(x,y+rad+26,sec['name'],25,bold=True,center=True)
# Door boundaries represent current tunnel endpoint markers, not an added wall.
for t in tunnels:
 dx=t['q'][0]-t['p'][0];dv=t['q'][1]-t['p'][1];le=math.hypot(dx,dv);nx=-dv/le;nv=dx/le
 for p in (t['p'],t['q']):
  line(xy(p[0]-nx*1.2,p[1]-nv*1.2),xy(p[0]+nx*1.2,p[1]+nv*1.2),'#b27f38',4)
 mid=((t['p'][0]+t['q'][0])/2,(t['p'][1]+t['q'][1])/2)
 x,y=xy(*mid);rect(x-40,y-19,80,38,'#314d62',r=8);txt(x,y,t['id'][-3:],23,'#ffffff',True,True)
txt(500,1150,'C01 실험 공동으로 재작업' if plan.get('pending_revision') else ('1섹터 레벨·아트 검수 완료' if sectors[0]['complete'] else '1섹터부터 마감 시작'),27,'#187c72',True,True)
line((500,1121),(530,1047),'#26988d',2)
line((90,1210),(222,1210),'#324d62',4)
line((90,1202),(90,1218),'#324d62',3);line((222,1202),(222,1218),'#324d62',3)
txt(155,1240,'10 m',20,'#607485',center=True)
txt(350,1235,'청색 원: 돔 섹터    회색 통로: 복도 구역    황토선: 문 경계',22,'#586d7d')

txt(1580,282,'섹터별 완성 대상',30,bold=True)
for i,sec in enumerate(sectors):
 y=347+i*128
 circle(1604,y,24,'#314d62');txt(1604,y,str(i+1),25,'#ffffff',True,True)
 txt(1643,y,f'{sec["name"]}  /  {sec["room_id"]}',27,bold=True)
 # Split long focus on separators into two compact lines if needed.
 parts=sec['focus'].split(' · ')
 txt(1583,y+43,' · '.join(parts[:3]),22,'#536b7d')
 txt(1583,y+75,' · '.join(parts[3:]),22,'#536b7d')
 if i<6:line((1580,y+102),(2220,y+102),'#e4ebf1',1)

rect(45,1315,2210,275,'#e6edf3',r=16)
txt(75,1363,'복도 구역 — T01~T07을 각각 완성',30,bold=True)
left=tunnels[:4];right=tunnels[4:]
for col,arr in enumerate([left,right]):
 for j,t in enumerate(arr):
  x=78+col*680;y=1422+j*43
  txt(x,y,t['id'][-3:],25,'#314d62',True)
  txt(x+100,y,f'{t["from_sector"]}섹터 ↔ {t["to_sector"]}섹터',25)
  txt(x+380,y,f'{t["length"]:.1f} m',22,'#607485')
txt(1510,1420,'복도 작업에 포함',24,bold=True)
txt(1510,1466,'문틀·문짝·수납 포켓·키패드',23,'#536b7d')
txt(1510,1507,'터널 외피·리브·조명·배관·안내선',23,'#536b7d')
txt(1510,1548,'인접 돔과 문 양쪽 접합 함께 검수',23,'#536b7d')
txt(65,1634,'완료 기준: 구조·접합 → 프랍·설비 → 재질·생활 흔적 → 조명·시야 → 이동·충돌·성능 검수',25,bold=True)
txt(65,1676,'이전 C01 완료 판정 철회 · 11개 돔 구성 확인 후 새 섹터도 작성 · 위 지도는 현재 Unity 구조의 참고 기록입니다.' if plan.get('pending_revision') else f'레벨·아트 완료 {completed}/14단위 · 다음 {plan["next"]} · 게임 기능은 별도 구현. 외곽 계획 8실은 확장 범위로 보존합니다.',22,'#586d7d')
svg.append('</svg>')
(OUT/'B5_섹터구분도.svg').write_text('\n'.join(svg),encoding='utf-8')
temp_png=OUT/'sector_diagram_pending.png'
im.save(temp_png)
temp_png.replace(OUT/'B5_섹터구분도.png')
DELIVERY.mkdir(parents=True,exist_ok=True)
for name in ['B5_섹터구분도.svg','B5_섹터구분도.png','sector_plan.json','scene_reference.json']:shutil.copy2(OUT/name,DELIVERY/name)
print(json.dumps({'sectors':len(sectors),'corridors':len(tunnels),'assigned_once':True,'complete_units':completed,'scene':ref['scene'],'outputs':str(OUT)},ensure_ascii=False))
