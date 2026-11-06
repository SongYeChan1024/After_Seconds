"""Draw the complete B5 aerial layout. Does not change Unity or source coordinates."""
from pathlib import Path
import json, shutil, hashlib
from xml.sax.saxutils import escape
from PIL import Image, ImageDraw, ImageFont

R=Path(__file__).resolve().parents[2]; D=R/'Docs/도면/Decision/원형공동'; O=D/'B5_섹터'
DELIVERY=Path('C:/Users/503-26/Documents/Codex/2026-11-06/dl/outputs/after_seconds_reviewed/B5_섹터')
source=D/'facility_layout.json'
floor=next(f for f in json.loads(source.read_text('utf-8'))['floors'] if f['id']=='B5')
ref=json.loads((O/'scene_reference.json').read_text('utf-8'))
previous=json.loads((O/'sector_plan.json').read_text('utf-8'))
if previous.get('schema_version')!=2:
    archive=R/'Docs/도면/Old/원형공동/B5_섹터/V0.03'; archive.mkdir(parents=True,exist_ok=True)
    for name in ('sector_plan.json','B5_섹터구분도.png','B5_섹터구분도.svg'):
        if not (archive/name).exists(): shutil.copy2(O/name,archive/name)
stages=['구조·문 접합','프랍·설비','재질·생활 흔적','조명·시야','이동·충돌·성능 검수']
built_rooms={v['name'].split('_')[2] for v in ref['domes'] if v['active']}
built_tunnels={v['name'].split('_')[1] for v in ref['tunnels'] if v['active']}
focus={
 'C01':'실험 포드 · 계측·관찰 · 안전 설비 · T11 출입부',
 'C02':'관제 데스크 · 보안 설비 · 기록 · 감시와 우회',
 'C03':'펌프 · 냉각 탱크 · 연결 배관 · 정비 통로',
 'C04':'배전 · 공조 · 점검 장비 · 케이블 연결',
 'W01':'생활 모듈 · 침상·개인 수납 · 세면 · 관리 동선',
 'W02':'추가 생활 모듈 · 생활 흔적 · 분리 관찰',
 'W03':'검사대 · 의료 안정 · 장비·소모품 · 이송 여유',
 'E01':'리넨 · 생활물품 · 보급 선반 · 수거 분리',
 'E02':'배식 준비 · 보온·회수 카트 · 위생 관리',
 'E03':'제염 구획 · 보호구 · 세척·폐기물 처리',
 'N01':'격리 관제 · 모니터 · 기록 · 직원 업무',
 'S01':'폐쇄 시험 시설 · 잔존 장비 · 방치 흔적',
 'VA':'계단 · 참 · 난간 · 방화 구획 · 상층 접점',
 'VB':'계단 · 참 · 난간 · 우회 동선 · 상층 접점',
 'VL':'승강로 · 화물 문 · 적재 여유 · 상층 접점'}
names={r['id']:r['name'] for r in floor['rooms']}; names['C01']='피험체 실험·격리 공동'
sectors=[]; cores=[]; tunnels=[]
for r in floor['rooms']:
    rid=r['id']; built=rid in built_rooms
    u=dict(id=f'B5-{rid}',room_id=rid,kind=r['kind'],name=names[rid],x=r['x'],v=r['v'],radius=r['r'],focus=focus[rid],structure_present=built,status='실험용 배치·아트 재작업' if rid=='C01' else ('기본 구조 / 미완료' if built else '미제작'),complete=False,checks={s:False for s in stages})
    if rid=='C01':
        u['previous_evidence']='Docs/검수/2026-11-06_B5_Sector01/검수결과.md'
        u['review_note']='이전 생활 배치 검사는 이력이다. 실험 배치와 T11 출입부를 포함해 재검수한다.'
        u['role']='실험·일시 격리. 생활시설은 W01·W02에 배치한다.'
    (cores if r['kind']=='core' else sectors).append(u)
for t in floor['tunnels']:
    built=t['id'] in built_tunnels
    tunnels.append(dict(id=t['id'],from_room=t['a'],to_room=t['b'],p=t['p'],q=t['q'],length=t['length'],width=t['w'],height=t['h'],structure_present=built,status='기본 구조·문 / 미완료' if built else '미제작',complete=False,checks={s:False for s in stages}))
units=sectors+cores+tunnels
# Old B5-S01 identified C01. Schema 2 uses the real southern room S01;
# never migrate old review evidence using that ID alone.
if previous.get('schema_version')==2:
    old={u['id']:u for u in previous['sectors']+previous['cores']+previous['corridor_area']['segments']}
    for u in units:
        for key in ('status','complete','checks','evidence','review_note','structure_present'):
            if key in old.get(u['id'],{}): u[key]=old[u['id']][key]
plan=dict(title='B5 전체 공동·코어·복도 섹터도 V0.05',schema_version=2,author='송예찬',date='2026-11-06',
 scope='조감도 전체 구성: 일반 공동 12개 + 수직 이동 코어 3개 + 연결 복도 19개. 총 34개 작업 단위.',
 latest_decision='11개 통합안 취소. 조감도의 공간 코드·공동 위치·연결을 유지한다. C01은 실험·일시 격리, W01·W02는 생활시설이다.',
 counts=dict(caverns=12,cores=3,corridors=19,work_units=34),scene=ref['scene'],coordinate='X 동쪽, v 남쪽. Unity Z=-v, B5 루트 Y=-82m. 위쪽은 북쪽(+Z).',sectors=sectors,cores=cores,
 corridor_area=dict(id='B5-COR',name='연결 복도',segments=tunnels,owns=['터널 외피·바닥','리브·문 접합 칼라','양 끝 문틀·문짝·수납 포켓','양면 키패드','복도 조명·배관·트레이','안내선·벽측 설비 엄폐'],boundary='복도 p/q 문 경계와 인접 공동을 함께 검수한다. 각 복도는 별도 작업 단위다.'),
 next='B5-C01',next_tasks=['C01 실험·관찰 장비의 세부 연결과 공간 밀도 마감','C01의 T01·T03·T11 세 출입 관계 유지','조감도 기준 재질·국소 조명·소품 마감','외곽 공동의 부족 프랍 및 이동 코어의 층간 구조 제작'],completion_stages=stages,
 completion_rule='5단계 검사와 실제 화면 증빙을 모두 확인한 단위만 완료한다. 구조 존재나 이전 생활 배치 검사를 완료 증거로 세지 않는다.',
 numbering_rule='조감도의 C/W/E/N/S 및 VA/VB/VL 코드를 사용한다. 옛 1~7 번호는 사용 종료. B5-S01은 이제 실제 남쪽 시험 공동 S01을 뜻한다.',
 legacy_number_map={'1':'C01','2':'C02','3':'C03','4':'C04','5':'VA','6':'VB','7':'VL'},
 runtime_scope='AI·문·스위치 동작·미니맵은 사용자 직접 구현. 이번 표기는 도면·제작 관리용이다.',
 scene_reference_note='scene_reference.json은 활성 공동·코어 15개와 복도 19개의 구조 검사 기록이다. 기본 구조 반영과 아트·층간 연결 완성은 구분한다.',
 source_layout_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),aerial_reference='층별조감도/B5_실내조감도.png')
assert (len(sectors),len(cores),len(tunnels))==(12,3,19)
assert len({u['id'] for u in units})==34
assert {u['room_id'] for u in sectors+cores}=={r['id'] for r in floor['rooms']}
assert all(t['from_room'] in names and t['to_room'] in names for t in tunnels)
assert {t['id'] for t in tunnels}=={t['id'] for t in floor['tunnels']}
completed=sum(u['complete'] for u in units)
(O/'sector_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')

W,H=2600,1800; im=Image.new('RGB',(W,H),'#f1f5f8'); dr=ImageDraw.Draw(im)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',f'<rect width="{W}" height="{H}" fill="#f1f5f8"/>']; fonts={}
def font(size,bold=False):
    if (size,bold) not in fonts: fonts[size,bold]=ImageFont.truetype('C:/Windows/Fonts/'+('malgunbd.ttf' if bold else 'malgun.ttf'),size)
    return fonts[size,bold]
def txt(x,y,text,size=24,color='#243d4d',bold=False,center=False):
    dr.text((x,y),text,font=font(size,bold),fill=color,anchor='mm' if center else 'lm')
    svg.append(f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="{"middle" if center else "start"}" dominant-baseline="central" font-family="Malgun Gothic, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}">{escape(text)}</text>')
def rect(x,y,w,h,fill,stroke=None,sw=1,r=0):
    dr.rounded_rectangle((x,y,x+w,y+h),radius=r,fill=fill,outline=stroke,width=sw)
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>')
def line(a,b,color,sw=2):
    dr.line([tuple(a),tuple(b)],fill=color,width=sw)
    svg.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke="{color}" stroke-width="{sw}"/>')
def circle(x,y,r,fill,stroke,sw=2):
    dr.ellipse((x-r,y-r,x+r,y+r),fill=fill,outline=stroke,width=sw)
    svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{fill or "none"}" stroke="{stroke}" stroke-width="{sw}"/>')
txt(60,57,'AFTER SECONDS  /  B5 격리층',25,'#567080',True)
txt(60,118,'공동 12개 · 이동 코어 3개 · 연결 복도 19개',46,bold=True)
txt(60,177,'조감도의 공간 코드와 연결 구성 유지  /  총 34개를 각각 완성·검수',26,'#567080')
txt(2240,60,'V0.05 · 2026-11-06',24,'#567080')
rect(40,225,1785,1110,'#ffffff','#d9e3eb',2,14); rect(1850,225,710,1110,'#ffffff','#d9e3eb',2,14)
S=5.9
def xy(x,v):return 930+x*S,750+v*S
for x in range(-140,141,20):line(xy(x,-86),xy(x,86),'#edf2f6',1)
for v in range(-80,81,20):line(xy(-140,v),xy(140,v),'#edf2f6',1)
txt(75,266,'공동·코어는 원, 복도는 T 코드로 구분',23,'#567080')
txt(1715,270,'북 / +Z',22,bold=True,center=True);line((1715,348),(1715,301),'#243d4d',4)
line((1715,301),(1704,319),'#243d4d',4);line((1715,301),(1726,319),'#243d4d',4)
for t in tunnels:
    a,b=xy(*t['p']),xy(*t['q'])
    line(a,b,'#718a9c' if t['structure_present'] else '#becbd5',int(t['width']*S)+5)
    line(a,b,'#d4e4ef' if t['structure_present'] else '#f0f3f6',int(t['width']*S))
for u in sectors+cores:
    x,y=xy(u['x'],u['v']);radius=u['radius']*S
    fill,stroke=('#ffedcf','#a77b38') if u['kind']=='core' else ('#d7e9f4','#4f7891') if u['structure_present'] else ('#f0f3f6','#9baebb')
    circle(x,y,radius,fill,stroke,3)
    if u['room_id']=='C01':circle(x,y,radius+7,None,'#178f84',4)
    txt(x,y,u['room_id'],26 if u['kind']=='core' else 29,bold=True,center=True)
for t in tunnels:
    x,y=xy((t['p'][0]+t['q'][0])/2,(t['p'][1]+t['q'][1])/2)
    rect(x-28,y-16,56,32,'#365b73' if t['structure_present'] else '#738795',r=6);txt(x,y,t['id'][-3:],20,'#ffffff',True,True)
line((100,1278),(218,1278),'#365b73',4);txt(159,1307,'20 m',20,'#567080',center=True)
for x,fill,stroke,label in [(330,'#d7e9f4','#4f7891','기본 구조 있음'),(610,'#f0f3f6','#9baebb','아직 미제작'),(880,'#ffedcf','#a77b38','이동 코어'),(1135,None,'#178f84','우선 제작 C01')]:
    circle(x,1290,10,fill,stroke,2);txt(x+20,1290,label,21)
txt(1885,271,'일반 공동 12개',29,bold=True)
for i,u in enumerate(sectors):
    y=324+i*47;txt(1885,y,u['room_id'],26,'#178f84' if u['room_id']=='C01' else '#365b73',True);txt(1965,y,u['name'],25)
line((1885,892),(2525,892),'#d9e3eb',2);txt(1885,932,'수직 이동 코어 3개',29,bold=True)
for i,u in enumerate(cores):txt(1885,985+i*46,u['room_id'],26,'#9a6b28',True);txt(1965,985+i*46,u['name'],25)
rect(1880,1135,650,165,'#eaf4f2',r=10);txt(1905,1171,'C01 → 실험·일시 격리',28,'#17796f',True)
txt(1905,1218,'W01·W02 → 실험체 생활시설',25);txt(1905,1261,'Unity 실험 배치·생활 가구 1차 반영',23,'#567080')
rect(40,1360,2520,320,'#e4edf3',r=14);txt(75,1400,'연결 복도 — T01~T19 개별 작업',29,bold=True)
for i,t in enumerate(tunnels):
    col,row=divmod(i,5);x=76+col*615;y=1455+row*44
    txt(x,y,t['id'][-3:],25,'#365b73',True);txt(x+85,y,f'{t["from_room"]} ↔ {t["to_room"]}',25);txt(x+315,y,f'{t["length"]:.1f} m',22,'#567080')
txt(60,1720,'복도 작업: 터널·리브·문틀·문짝·수납 포켓·키패드·조명·설비·안내선. 양 끝 공동 접합까지 함께 검수.',24)
txt(60,1770,f'아트 완료 {completed}/34  ·  Unity 기본 구조: 공동 {len(sectors)} + 코어 {len(cores)} + 복도 {len(tunnels)}  ·  다음: C01 세부 마감 · 층간 구조는 미완료',24,'#567080')
svg.append('</svg>');(O/'B5_섹터구분도.svg').write_text('\n'.join(svg),encoding='utf-8')
tmp=O/'sector_diagram_pending.png';im.save(tmp);tmp.replace(O/'B5_섹터구분도.png')
DELIVERY.mkdir(parents=True,exist_ok=True)
for name in ('B5_섹터구분도.svg','B5_섹터구분도.png','sector_plan.json','scene_reference.json'):shutil.copy2(O/name,DELIVERY/name)
print(json.dumps(dict(**plan['counts'],complete=completed,source_coordinates_unchanged=True,output=str(O)),ensure_ascii=False))
