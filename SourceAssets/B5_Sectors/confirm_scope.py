"""Record the user's 12-cavern correction without changing Unity geometry."""
from pathlib import Path
from decimal import Decimal
import json,re,hashlib
R=Path(__file__).resolve().parents[2];D=R/'Docs/도면/Decision/원형공동';S=R/'SourceAssets/B5_Sector01'
scope=json.loads((S/'latest_scope.json').read_text('utf-8'))
if scope.get('dome_target')==12:
    raise SystemExit('12개 공동 기준이 이미 반영되었습니다.')
old=scope['decision']
decision='2026-11-06 확정: B5는 층별조감도대로 일반 공동 12개(C01~C04·W01~W03·E01~E03·N01·S01), 이동 코어 3개(VA·VB·VL), 연결 복도 19개(T01~T19)를 각각 별도 작업 단위로 만든다. 합계 34개이며 11개 통합안은 취소한다. 조감도의 공간 코드·공동 위치·연결 구성을 유지한다. C01은 실험·일시 격리 공동, W01·W02는 실험체 생활시설이다. 이전 Unity 1~7 번호는 사용 종료한다. 현재 공동 4개·코어 3개·복도 7개에 기본 구조가 있고 외곽 공동 8개·복도 12개는 미제작이다. 완료는 0/34이며 다음은 C01 실험 배치·아트 재작업이다.'
paths=['Docs/AfterSeconds_메인기획서.md','AGENTS.md','CLAUDE.md','Docs/이어하기_2026-11-06.md','Docs/회사_작업목록_2026-11-06.md','Docs/도면/Decision/원형공동/README.md','Docs/검수/2026-11-06_B5_Sector01/검수결과.md','SourceAssets/B5_Sector01/README.md']
for name in paths:
    p=R/name;text=p.read_text('utf-8');assert old in text,name
    head,body=text.split('\n',1)
    head=re.sub(r'V(\d+\.\d+)',lambda m:f'V{Decimal(m[1])+Decimal("0.01"):.2f}',head)
    text=(head+'\n'+body).replace(old,decision,1)
    p.write_text(text,encoding='utf-8')
mp=R/paths[0]
with mp.open('a',encoding='utf-8') as f:
    f.write('\n- V0.33 (2026-11-06): B5 조감도 전체 12공동·3이동 코어·19복도, 총34작업 단위로 확정. 11개 통합안 취소. C01 실험 / W01·W02 생활 역할 분리. 송예찬.\n')
floor=next(f for f in json.loads((D/'facility_layout.json').read_text('utf-8'))['floors'] if f['id']=='B5')
wl=R/'Docs/회사_작업목록_2026-11-06.md';text=wl.read_text('utf-8')
start=text.index('## 최신 우선 작업:');end=text.index('아래는 이번 구분 이전의 작업 기록이다.',start)
block='## 최신 우선 작업: B5 전체 34개 작업 단위\n\n작성자 송예찬 · 2026-11-06. [전체 섹터도 V0.04](도면/Decision/원형공동/B5_섹터/B5_섹터구분도.png)와 [작업 단위 데이터](도면/Decision/원형공동/B5_섹터/sector_plan.json)를 따른다. 조감도에 있는 공동과 복도를 모두 제작 범위에 포함한다. 현재 완성 판정은 0/34다.\n\n| 분류 | 코드 | 역할 | 현재 상태 |\n| --- | --- | --- | --- |\n'
for r in floor['rooms']:
    rid=r['id'];name='피험체 실험·일시 격리' if rid=='C01' else r['name']
    status='실험 배치·아트 재작업' if rid=='C01' else '기본 구조 / 미완료' if rid in ('C02','C03','C04','VA','VB','VL') else '미제작'
    block+=f'| {"이동 코어" if r["kind"]=="core" else "공동"} | {rid} | {name} | {status} |\n'
block+='\n복도는 아래 19개를 따로 완성한다. 양 끝 문틀·문짝·수납 포켓·키패드, 터널 외피·리브·조명·설비·안내선을 포함한다. 인접 공동 접합도 함께 검수한다.\n\n'
for t in floor['tunnels']:
    status='기본 구조 / 미완료' if int(t['id'][-2:])<=7 else '미제작'
    block+=f'- [ ] {t["id"][-3:]}: {t["a"]} ↔ {t["b"]} — {status}\n'
block+='\n다음은 C01이다. 생활 가구를 실험·계측·관찰 설비로 정리하고, T01·T03 외에 서쪽 T11 접합도 확보한 뒤 벽 패널·리브·설비 연결·재질·조명을 마감한다. W01·W02를 만들 때 기존 생활용 에셋을 재사용한다.\n\n완료 기준은 구조·문 접합 → 프랍·설비 → 재질·생활 흔적 → 조명·시야 → 이동·충돌·성능 검수다. 조감도와 실제 화면의 시각적 완성도까지 확인한다. 이전 생활 배치의 기술 검사만으로 완료 처리하지 않는다. 게임 기능은 사용자 직접 구현 범위를 유지한다.\n\n'
wl.write_text(text[:start]+block+text[end:],encoding='utf-8')
scope=dict(version='V0.03',decision=decision,C01_role='실험·일시 격리',living_facility=['W01','W02'],dome_target=12,includes_cores=False,vertical_cores=3,corridors=19,work_units=34,complete=False,next='B5-C01',scene_role_update_pending=True)
(S/'latest_scope.json').write_text(json.dumps(scope,ensure_ascii=False,indent=2),encoding='utf-8')
p=S/'decision.json';prior=json.loads(p.read_text('utf-8'))
current=dict(date='2026-11-06',decision=decision,reference=prior['reference'],reference_only=False,layout_source_sha256=prior['layout_source_sha256'],supersedes=prior['decision'],scene_role_update_pending=True)
p.write_text(json.dumps(current,ensure_ascii=False,indent=2),encoding='utf-8')
# The illustration bundle remains V0.01; this is a correction to its index text.
p=D/'층별조감도/README.md';text=p.read_text('utf-8')
text=text.replace('# After Seconds 층별 실내 조감도 V0.01','# After Seconds 층별 실내 조감도 안내 V0.02',1)
text=text.replace('실제 제작은 1~7섹터와 T01~T07을 순서대로 진행합니다. 외곽 생활·연구동은 확장 계획입니다.','B5 일반 공동12개·이동 코어3개·복도19개를 별도 단위로 제작합니다. 외곽 공동도 현재 제작 범위에 포함하며, C01은 실험·일시 격리, W01·W02는 생활시설입니다.')
text=text.replace('## 먼저 볼 자료','이 안내문 V0.02는 B5 전체 제작 범위 확정을 반영합니다. 조감도 이미지·PDF·좌표 도식은 기존 V0.01이며 다시 생성하지 않았습니다.\n\n## 먼저 볼 자료',1)
text+='\n안내문 V0.02 (2026-11-06): B5 12공동·3코어·19복도 제작 범위와 C01/W01/W02 역할을 정정. 그림·PDF V0.01 보존.\n'
p.write_text(text,encoding='utf-8')
print(json.dumps(dict(documents_updated=len(paths)+1,scope=scope['work_units'],unity_changed=False),ensure_ascii=False))
