"""Write verified as-built data and review links without changing gameplay rules."""
import json,hashlib,html,shutil
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-10_B2_Operations';D=R/'Docs/도면/Decision/원형공동';A=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,data):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
plan=read(H/'plan.json');ground=read(O/'ground.json');upper=read(O/'upper.json');tunnels=read(O/'all_tunnels.json');play=read(O/'play.json');state=read(O/'final_state.json')
assert all(t['reachable'] and (not t.get('move') or t['move']['passed']) for r in ground for t in r['targets'])
assert all(m['passed'] for r in upper for m in r['moves'])
assert all(t['passed'] for t in tunnels['routes'])
assert play['complete'] and all(r['passed'] for r in play['results']) and not play['errors']
assert not state['missingOriginal'] and not state['missingMeshes'] and not state['missingMaterials']
protected=read(H/'protected_before.json');changed=[p for p,h in protected.items() if not (R/p).is_file() or hashlib.sha256((R/p).read_bytes()).hexdigest()!=h]
write(O/'protected.json',dict(files=len(protected),changed=changed));assert not changed,changed
roles={'C01':'원심분리 · 두 공정열','C02':'냉각 · 펌프 점검로','C03':'배전 · U자 제어반','C04':'관제 · 운전석과 후면 정비로','W01':'주 전력 · 변압기와 차단반','W02':'예비 전력 · 발전기와 연료계통','W03':'부품 · 입고·보관·수리·출고','E01':'급수 · 축압 탱크와 가압 펌프','E02':'공조 · 필터 교체면과 모터 정비면','E03':'폐수 · 습식 공정과 건식 기록','N01':'환기 · 팬열과 덕트','S01':'정비 · 계측 작업대와 수리 인계'}
compact={k:v for k,v in plan.items() if k not in ['catalog','decks']};compact['decks']={k:{a:b for a,b in v.items() if a in ['paths','stairs','links','outline']} for k,v in plan['decks'].items()};compact['unity_state']=state
out=D/'B2_운영동선_재설계';write(out/'as_built_operations.json',compact)
write(A/'06.Data/AssetSources/B2_OperationsRebuild.json',dict(version='V0.01',author='송예찬',date='2026-11-10',scene=state['scene'],source='SourceAssets/B2_OperationsRebuild',reuse='기존 VARCO/Blender 장비의 재질·LOD·GUID를 유지하여 186배치. 신규 VARCO 생성 없음.',manufactured='Blender: 부분 데크4·공정 연결12·모터 정비대 변형1(6배치), 베벨·LOD·별도 보행 충돌',models=read(H/'models.json'),as_built='Docs/도면/Decision/원형공동/B2_운영동선_재설계/as_built_operations.json'))
facility=read(D/'facility_layout.json');facility['version']='V0.10';facility['production_status']['B2']='공동12의 설비 운영 동선 재배치186개, 부분 정비 데크4개, 공정 연결12개. 코어3·통로21·상부 연결7끝 유지. 정적 레벨 및 이동 검수, AI/설비 동작 미구현.'
facility['production_status']['B2_Operations']=dict(date='2026-11-10',status='Unity 적용·정적 통행 및 Play 검수 / 사용자 외형 검수 단계',as_built='B2_운영동선_재설계/as_built_operations.json',review='../../../Review/2026-11-10_B2_Operations/Review.md',supersedes_interior='B2_DomeNetwork',runtime_added=False)
history=facility.setdefault('revision_history',[])
if not any(isinstance(v,dict) and v.get('version')=='V0.10' for v in history):history.append(dict(version='V0.10',date='2026-11-10',author='송예찬',change='사용자 승인한 B2 점검·순찰 관점 내부 운영 동선을 Unity 12공동으로 확대. 현행 내부 실배치 참조 추가; 외부 공동·터널 연결 및 게임 규칙 유지.'))
write(D/'facility_layout.json',facility)
ab=read(D/'B2_배관통로/as_built_layout.json');ab['operations_revision']=dict(version='V0.01',path='../B2_운영동선_재설계/as_built_operations.json',note='내부 설비·데크는 이 참조가 최신. 본 파일의 이전 공동 내부 배치는 제작 이력이며 재적용하지 않는다.');write(D/'B2_배관통로/as_built_layout.json',ab)
doors=sum(t['kind']=='door' for r in ground for t in r['targets']);equipment=sum(t['kind']=='operatingFace' for r in ground for t in r['targets']);moves=sum(len(r['moves']) for r in upper);tunnelmoves=sum(len(t['movements']) for t in tunnels['routes']);frames=sum(t['frames'] for t in play['results'])
rows='\n'.join(f'| {r["id"]} | {roles[r["id"]]} | {sum(p["room"]==r["id"] for p in plan["placements"])} |' for r in plan['rooms'])
review=f'''# B2 설비 운영 동선 재구성 검수 V0.01

작성자 송예찬 · 2026-11-10

사용자가 승인한 점검원·경비 관점의 구조를 B2 전체 12공동에 적용했다. 현재 씬은 `Level_B2_Circular.unity`, 새 계층은 `B2_MachineryNetwork/B2_OperationsLayout`이다. 기존 벽·문·코어3·터널21을 유지하고 내부 설비를 186배치로 다시 구성했다. 이전 설비와 데크는 비활성 상태로 보존했다.

| 공동 | 역할과 배치 | 배치 수 |
|---|---|---:|
{rows}

C02의 두 펌프열은 중앙에서 운전 상태를 읽고 뒤쪽으로 돌아 정비한다. C01은 공급·분리·냉각을 두 공정열로 묶었다. W03은 입고와 출고 카트 주차를 통로에서 빼고 중앙 이동로를 확보했다. C03/C04에는 젖은 공정 설비를 두지 않고 전기·관제 역할을 분리했다. S01의 정비용 모터는 작업대 위에 놓아 통행을 막지 않게 했다.

상부는 C02의 U형, W02의 L형, E02의 직선 점검 데크, E01의 부분 곡선 데크로 구분했다. 기존 C02–T01, W02–T11/T12, E01–T14/T15, E02–T15/T16의 7개 끝을 유지한다. 공동 높이3.6m와 터널 높이2.42m 사이에는 계단과 수평 참을 둔다. 실제 충돌 검사에서 발견한 난간 간섭과 단차를 보수했다. 데크·계단·지지대에 베벨을 적용하고 LOD와 보행용 충돌을 분리했다.

기존 광원 {state['lights']}개를 유지했다. 공동별 기존 등기구 한 개의 색·밝기만 작업면을 읽기 쉬운 적황색으로 조정했고, 흰 직접광은 {state['whiteDirect']}개다. 반사와 가림 정보도 새 배치로 갱신했다.

검증 결과:

- 하부 공동 출입구 {doors}/{doors}, 설비 조작면 {equipment}/{equipment} 접근 연결 확인. 실제 Controller로 공동 출입구 간 이동도 검사했다.
- 상부 17경로의 Controller 왕복 {moves}/{moves} 통과.
- 기존 복층 터널 19개: {tunnels['lowerSamples']+tunnels['upperSamples']:,}표본, Controller 왕복 {tunnelmoves}/{tunnelmoves} 통과. 짧은 T04/T06은 기존 단층이며 출입 연결 검사에 포함했다.
- 실제 Play 6경로, {frames:,}프레임 진행, 새 게임 오류0. 키보드·마우스 활성 상태 복구.
- 기존 Transform {state['originalTransforms']:,}개 누락0. 보호 파일 {len(protected)}개 동일. 새 그룹의 메시·재질 누락0, 게임 스크립트 추가0.

검증은 통행과 정적 레벨을 대상으로 한다. 경비·CCTV의 실제 순찰/감지, 설비 작동, 문/승강기 동작과 최종 잠입 난이도는 이번 작업에 포함되지 않는다. 전체 아트의 최종 수용은 사용자의 1인칭 검수 뒤 판단한다.

[12공동 전후 화면](review.html) · [현재 실배치](../../도면/Decision/원형공동/B2_운영동선_재설계/as_built_operations.json) · [제작 원본](../../../SourceAssets/B2_OperationsRebuild/README.md)

다음 검수는 C02 중앙 점검로 → E02 필터 교체면 → W03 수리대 → E01/W02 상부 접속부 순서다. 현재 씬을 과거 Apply 도구로 재생성하지 않는다. 로컬 저장이며 커밋·push는 요청받지 않았다.

## 변경 기록

- V0.01: 12공동 운영 배치·4부분 데크·공정 연결·보행/Play 검증. 송예찬.
'''
(O/'Review.md').write_text(review,encoding='utf8')
cards=''.join(f'<article id="{id}"><h2>{id} · {html.escape(role)}</h2><div class="pair"><figure><img loading="lazy" src="before_{id}.png"><figcaption>변경 전</figcaption></figure><figure><img loading="lazy" src="after_{id}.png"><figcaption>운영 동선 재배치 후</figcaption></figure></div></article>' for id,role in roles.items())
(O/'review.html').write_text(f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>B2 공동 운영 동선 V0.01</title><style>body{{background:#11171d;color:#e8e7e3;font:16px/1.6 system-ui;margin:0 auto;max-width:1540px;padding:32px}}h1{{font-size:32px}}p{{color:#b8c6cc}}nav{{display:flex;flex-wrap:wrap;gap:16px;position:sticky;top:0;background:#11171def;padding:14px}}a{{color:#ffa777}}article{{padding:25px 0;border-top:1px solid #3a4046}}.pair{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}figure{{margin:0}}img{{width:100%;display:block}}figcaption{{padding:8px;background:#222b32}}@media(max-width:850px){{.pair{{grid-template-columns:1fr}}}}</style><h1>B2 · 설비를 점검하고 순찰하는 공간</h1><p>12공동 · 설비186배치 · 부분 데크4 · 기존 터널/상부 연결 유지. 실제 Unity 렌더이며 화면 밝기를 별도 보정하지 않았습니다.</p><nav>{''.join(f'<a href="#{id}">{id}</a>' for id in roles)}</nav>{cards}<p>작성자 송예찬 · 정적 레벨 및 보행 검수. AI와 설비 작동은 별도 구현 범위입니다.</p></html>''',encoding='utf8')
(H/'README.md').write_text('''# B2 설비 운영 동선 제작 원본 V0.01

작성자 송예찬 · 2026-11-10

사용자 승인 후 B2 전체12공동에 적용했다. `plan.json`은 실제186배치·4부분 데크·계단·점검 경로, `unity_as_built.json`은 저장된 Unity 위치다. `build.py`와 `bench.py`는 Blender 베벨 원본과38개 FBX/LOD/충돌을 생성한다. 기존 VARCO/Blender 프랍은 씬의 보수된 재질·LOD·맞춤 충돌을 재사용했다. 기존 정비대에서 부품 트레이를 비운 변형1종을 만들어6곳에 적용했고, 모터를0.65배 크기로 테이블 상면0.985m에 맞췄다. 신규 VARCO 생성은 추가하지 않았다.

`Apply.C02/Remaining`은 최초 적용 도구이며 현재 씬에 재실행하지 않는다. 기존 설비·데크는 비활성 보존했다. `Repair.Placements`는 현행 plan에 맞춘 범위 내 보수다. 상부 발판의 삼각형은 닫힌 바닥 충돌, 계단은 연속 경사 충돌이고 시각 그레이팅과 분리된다. 그레이팅 바닥 충돌은 향후 AI 감지용 불투명 면으로 그대로 쓰지 않는다.

`Audit`는 하부 연결/조작면·Controller·상부 왕복·렌더, `TunnelReview`는 기존19복층 통로, `Play`는 실제 플레이어 입력6구간, `Final`은 원본 보존/참조를 검사한다. C# 도구는 Assets 밖에서 일시 실행하며 게임 로직을 추가하지 않는다. 실제 Mouse/Keyboard 장치를 비활성화하지 않는다.

`Finish.Reflections/Occlusion/Complete`로 배치 이후 반사·가림을 갱신했다. `record.py`는 모든 검사가 통과한 뒤 출처·도면·검수 문서를 기록한다. 빌드/배치 재실행 전 현행 사용자 수정을 반드시 대조한다.

[검수](../../Docs/Review/2026-11-10_B2_Operations/Review.md) · [전후 화면](../../Docs/Review/2026-11-10_B2_Operations/review.html)

## 변경 기록

- V0.01: 12공동 운영 배치, 계단 참/난간 보수, 근접 접근과 Play 검증. 송예찬.
''',encoding='utf8')
print('RECORDED',doors,equipment,moves,tunnelmoves,frames,'protected',len(protected))
