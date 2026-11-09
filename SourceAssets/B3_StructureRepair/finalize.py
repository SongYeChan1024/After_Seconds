from pathlib import Path
from collections import Counter
import json,html,re
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-09_B3_StructureRepair'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
p=read(H/'layout_after.json');before=read(H/'layout_before.json');delta=read(H/'density_delta.json');walk=read(O/'walk.json');width=read(O/'width.json');audit=read(O/'audit.json');protect=read(H/'protected_result.json');state=read(H/'scene_state_result.json')
plays=[read(f) for f in sorted(O.glob('before_play_*.json'))]
assert len(plays)==6 and all(x['complete'] and x['framesAdvanced']>100 and x['displacement']>.3 and not x['errors'] for x in plays)
assert len(walk['results'])==394 and all(x['passed'] for x in walk['results']) and not walk['planningFailures']
assert width['failed']==0 and not state['placementErrors'] and not state['missingOriginalTransforms']
assert len(p['placements'])==302 and len(delta['additions'])==152 and len(delta['moves'])==14
(O/'play_summary.json').write_text(json.dumps({'version':'V0.01','allPassed':True,'tests':plays,'note':'After-repair tests; before_play file prefix is inherited helper naming, not before-repair evidence. Editor timings only.'},indent=2),encoding='utf-8')
bc=Counter(q['room'] for q in before['placements']);ac=Counter(q['room'] for q in p['placements'])
rows='\n'.join(f"| {r['id']} {r['name']} | {bc[r['id']]} | {ac[r['id']]} |" for r in p['rooms'] if r['kind']!='core')
report=f'''# B3 구조와 프랍 밀도 보수 검수 V0.01

작성자 송예찬 · 2026-11-09

`Level_B3_Circular.unity`에 T08 곡선 우회와302개 프랍 배치를 저장했다. T02/T08뿐 아니라 T07/T08의 공동 밖 외피 중첩도 함께 해소했다. 13공동·3코어의 위치와22복도의 연결 관계는 유지했다.

[전후 화면과 근접 검수](review.html) · [현재 구조·배치도](as_built_plan.png) · [Decision 기준](../../도면/Decision/원형공동/B3_구조보수/README.md)

## 구조와 배치

T08은 C03 폐기·환복 공동에서 C04 제염 공동으로 이어지는 남쪽 곡선 통로다. 길이는40.84m에서51.826m로 바뀌었다. 두 공동의 개구부·벽 패널·문틀·출입등과 통로 외피·바닥·리브·설비·안내선을 함께 수정했다. 기존 직선 리브와 안내는 비활성 상태로 보존했다.

프랍은150개에서302개로 늘렸다. 바닥 설비150개와 작업대 소품2개를 추가하고, 기존14개는 출입 여유와 작업열 정렬에 맞춰 옮겼다. 랙 안 용기·서랍 등 모델 내부 부품을 각각 한 배치로 세지 않았다. CCTV·스위치·벽 지지대는 이302개 집계와 별도다.

시료 보관은 중앙 랙 열과 적재 팔레트, 저온 저장은 냉동고 열과 이동 용기, 인수 구역은 검수·포장 작업대, 세척 구역은 멸균기·트레이 랙으로 구분했다. 새 팔레트3종·서랍 보관대·적재 카트·멸균 트레이 랙·밀봉 키트는 기존 상세 케이스 부품과 재질을 재사용해 Blender에서 제작했다. 프레임·손잡이·잠금쇠·바퀴·라벨·예각 베벨을 포함한다. 이번 보수의 새 VARCO 생성은 없으며 기존 VARCO 저온 용기와 운반함을 재사용했다.

| 공동 | 보수 전 | 보수 후 |
|---|---:|---:|
{rows}

기본 소등5구역(C01/C02/W01/W02/E03)을 유지했다. 화면의 점등·근접 검수는 임시 조명을 사용한 경우 따로 표시했다. 조명 스위치 작동은 아직 구현하지 않았다.

## 실제 검수

| 항목 | 결과 |
|---|---|
| 22복도 외피의4높이 평면 검사 | 공동 밖 겹침·비대상 공동 관통 후보0 |
| 복도 중앙·양옆 캡슐 검사 | 10,730표본 막힘·바닥 누락0, 중앙 최소 머리 여유3.33m |
| CharacterController 이동 | 394/394 통과: 복도 왕복·문·장비 앞·15m 계단 |
| 실제 Play | T08 서쪽·곡선·동쪽, C01/N01/W02 총6곳 이동·프레임 진행, 검사 중 새 경고/오류0 |
| 현재 배치 대조 | 302/302 위치·회전·활성 일치 |
| 기존 오브젝트 | 보수 전3,267 Transform 모두 보존 |
| 메시·재질·스크립트 참조 | 누락0, 활성/보존 메시의 퇴화 삼각형0 |
| 최적화·반사 | 고밀도 프랍 LOD12개와114그룹 추가, 반사16개·가림 데이터 재베이크 |

원본 FBX의 극소 삼각형3개는 실제 씬에 사용하는 파생 메시에서 제거했다. 반사·가림 데이터는 바뀐 통로와 설비 배치 기준이다. Play의1920×1080 에디터 프레임 중앙값은8.55~10.23ms였으며 빌드·목표 하드웨어 성능 보증으로 사용하지 않는다. 기존 Unity AI `NoSubscription` 로그와 과거 컴파일 이력은 신규 게임 오류와 분리했다. 검사 종료 시 컴파일 실패·현재 콘솔 경고/오류0이었다.

## 보존과 이어하기

사용자 허용 후 편집 중이던 Player 씬을 저장하고 B3를 검수했다. 종료 후 `01.Scenes/Player.unity` 편집 모드로 복귀했다. 작업 전 저장본을 기준으로 Player 씬·게임 C#·B4/B5 등 다른 씬은 동일하다. 보호 비교76파일 중 변경은 B3 씬과 `Player_Animator.controller`다. Animator에는 사용자 작업의 IsSprint·전환 조건 변경이 남아 있으며, 이번 도구에서는 Animator 설정을 편집하지 않았다. 비교 차이를 임의로 되돌리지 않았다.

Decision 설계는V0.05, B3 현재 배치도는V0.01이다. 기존 Excel V0.03은 수급 목록으로 보존하고,302배치의 좌표는 `B3_구조보수/as_built_layout.json`을 우선한다. 자료 출처는 `AfterSeconds_프랍환경_제작목록.xlsx`의 B3 제작/배치 항목이며 추출한 행 번호는 `SourceAssets/B3_StructureRepair/inventory.json`에 있다. 문·승강기·스위치·AI와 층간 실제 연결은 사용자 게임 구현 범위다.

다음은 사용자 B3 통로·밀도·근접 외형 확인 후 지적 구역을 보수한다. 전체 아트 최종 승인을 대신하지 않는다. `Apply.cs`나 이전 전체 제작기를 다시 실행하지 않는다. 이번 변경은 로컬 저장이며 커밋·push하지 않았다.

## 변경 기록

- V0.01: T08 구조,302배치,통행·Play 검수와 Player 작업 씬 복귀.
'''
(O/'Review.md').write_text(report,encoding='utf-8')
def fig(file,label):return '<figure><a href="'+file+'"><img loading="lazy" src="'+file+'" alt="'+html.escape(label)+'"></a><figcaption>'+html.escape(label)+'</figcaption></figure>'
body=['<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>B3 구조와 밀도 보수 V0.01</title><style>body{max-width:1600px;margin:32px auto;padding:0 20px;background:#111820;color:#dbe6ed;font:16px/1.65 system-ui}h1{font-size:28px}img{width:100%;height:auto}section{margin:38px 0}article{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0}figcaption{padding:8px}a{color:#a9d7e9}summary{cursor:pointer;padding:12px;background:#263441}small{color:#a9bbc8}@media(max-width:750px){article{grid-template-columns:1fr}}</style><h1>B3 구조와 프랍 밀도 보수 V0.01</h1><p>작성자 송예찬 · 2026-11-09</p><p>T08 접합부 겹침을 곡선 우회로 보수했습니다. 프랍은150→302배치, 기존14개를 재배치했습니다.</p><p><a href="Review.md">검수 결과와 이어하기</a> · <a href="as_built_plan.png">현재 구조·배치도</a></p>']
body.append('<section><h2>새 통로와 실제 Play</h2><article>'+fig('C03_T08_portal.png','C03에서 새 T08 출입구')+fig('C04_T08_portal.png','C04에서 새 T08 출입구')+'</article><article>'+fig('T08_inside_9.png','T08 곡선 내부 · 저장 조명')+fig('play_game_camera.png','실제 Play의 Main Camera · 가림 적용')+'</article></section>')
body.append('<section><h2>변경 전후 밀도</h2><p>같은 위치·화각·임시 점검등으로 비교했습니다. 저장된 기본 소등 설정은 유지했습니다.</p>')
for rid in ['C01','C04','W01','W02','N01','S01']:
 name=next(r['name'] for r in p['rooms'] if r['id']==rid);body.append('<h3>'+rid+' '+name+'</h3><article>'+fig('before_'+rid+'.png','보수 전')+fig('after_'+rid+'.png','보수 후')+'</article>')
body.append('</section><section><h2>공동별 배치와 점등 검수</h2><p>왼쪽은 작업등 임시 점등 화면, 오른쪽은 배치도입니다. 점등 검수 후 기본 상태를 복구했습니다.</p>')
for r in p['rooms']:
 if r['kind']=='core':continue
 rid=r['id'];body.append('<details><summary>'+rid+' '+r['name']+' · '+str(ac[rid])+'배치</summary><article>'+fig('inspection_'+rid+'.png','작업등 임시 점등')+fig(rid+'_layout_after.png','진한 색: 추가 설비 / 연한 색: 기존 설비')+'</article></details>')
body.append('</section><section><h2>새 프랍 근접 화면</h2><p>형태 확인용 임시 점검등을 사용했습니다.</p>')
labels={'SamplePallet_1':'프레임·손잡이·잠금쇠와 적재 팔레트','SampleDrawerIsland':'양면 서랍 보관대','LoadedTransferCart':'적재 카트·바퀴·손잡이','SterileTrayRack':'포장 트레이 보관 랙','SealingKit':'작업대 밀봉 키트'}
for key,label in labels.items():body.append('<details><summary>'+label+'</summary>'+fig('close_BR_B3_'+key+'.png',label)+'</details>')
body.append('</section><section><h2>현재 구조와 검수 경로</h2>'+fig('as_built_plan.png','경로는 도면 전용이며 Unity에 추가하지 않았습니다.')+'</section></html>')
page=''.join(body);(O/'review.html').write_text(page,encoding='utf-8');assert all((O/n).exists() for n in re.findall(r'src="([^"]+)"',page))
note='''2026-11-09 B3 구조·밀도 보수 완료: T02/T08와 T07/T08 중첩을 T08 남쪽 곡선 우회로 해소하고 C03/C04 개구부·문틀·마감·리브·안내선을 정합했다. 프랍150→302배치, 기존14개 재배치. Controller394/394·복도10,730표본·Play6곳 통과, 실제 배치302/302 일치·기존3,267 Transform 보존. 반사16개·가림 재베이크. [검수](Docs/Review/2026-11-09_B3_StructureRepair/Review.md) · [화면](Docs/Review/2026-11-09_B3_StructureRepair/review.html) · [현재 도면](Docs/도면/Decision/원형공동/B3_구조보수/README.md). **다음은 사용자 B3 통로·밀도·근접 외형 확인 → 지적 구역 보수**. 사용자 승인 후 Player 씬을 저장하고 검수했으며 종료 후 Player 편집 씬으로 복귀했다. 게임 C#은 수정하지 않았고 사용자 Animator 변경을 되돌리지 않았다. Player·Enemy·UI/UX 등 기능별 씬은 Old 이동 대상에서 제외한다. SourceAssets/B3_StructureRepair/README.md를 우선하고 Apply를 재실행하지 않는다. 로컬 저장, 커밋·push 미실시. 작성자 송예찬.'''
for name in ['AGENTS.md','CLAUDE.md']:
 file=R/name;s=file.read_text(encoding='utf-8');title,_,rest=s.split('\n\n',2);assert 'V0.72' in title;file.write_text(title.replace('V0.72','V0.73')+'\n\n'+note+'\n\n'+rest+'\n- V0.73 (2026-11-09): B3 구조·밀도 보수 적용과 검수·Player 씬 복귀. 송예찬.\n',encoding='utf-8')
f=R/'Unity/README.md';s=f.read_text(encoding='utf-8');title,_,rest=s.split('\n\n',2);assert 'V0.53' in title;f.write_text(title.replace('V0.53','V0.54')+'\n\n'+note.replace('(Docs/','(../Docs/')+'\n\n'+rest,encoding='utf-8')
f=R/'Docs/도면/Decision/원형공동/README.md';s=f.read_text(encoding='utf-8');title,rest=s.split('\n',1);assert 'V0.11' in title;f.write_text(title.replace('V0.11','V0.12')+'\n\n2026-11-09 B3 구조·밀도 보수: [현재 배치도와 명세](B3_구조보수/README.md)를 우선한다. `facility_layout.json` V0.05에 T08 곡선 경로·C03/C04 개구부와 실제 검수 동선을 반영했다. 프랍302배치는 별도 as_built_layout.json에 보관한다. 기존 Excel·PDF·SVG는 수급/초기 설계 기록으로 보존했으며 다른 층 좌표는 변경하지 않았다. 작성자 송예찬.\n\n이전 단계 기록:\n'+rest+'\n- V0.12: B3 구조·현재 배치·검수 경로 동기화.\n',encoding='utf-8')
(H/'README.md').write_text('''# B3 구조와 밀도 보수 제작 원본 V0.02

작성자 송예찬 · 2026-11-09

Unity B3 씬에 적용·저장하고 검수를 마쳤다. [검수 결과](../../Docs/Review/2026-11-09_B3_StructureRepair/Review.md)와 [실제 화면](../../Docs/Review/2026-11-09_B3_StructureRepair/review.html), [현재 Decision 도면](../../Docs/도면/Decision/원형공동/B3_구조보수/README.md)을 먼저 읽는다. 사용자 승인 후 Player 씬 작업을 저장하고 B3 검수를 진행했으며 Player 씬으로 복귀했다.

`layout_before.json`은150배치 원본, `layout_route.json`은 구조 보수안, `layout_after.json`은302배치와 실제 검수 경로를 반영한 현재 상태다. 기존14개를 재배치하고150개 바닥 설비와2개 작업대 소품을 추가했다. `density_delta.json`은 적용 차이이며 unplaced는 여유가 부족해 배치하지 않은 추가 후보다.

Blender 건축8개·상세 프랍7개·LOD12개를 반입했다.5개 표면 파생 메시에서 극소 퇴화 삼각형3개를 제거했다. 고밀도 모델114배치에 LOD를 더하고 기존 반사16개·가림 데이터를 갱신했다. 원본 모델과 기존 비활성 리브/안내는 보존했다.

`Apply.cs`는 이미 실행했다. 전체 Apply 또는 이전 B3 제작기를 현재 씬에 재실행하지 않는다. `State.cs`, `Quality.cs`, `Review.cs`는 저장된 B3 편집 씬에서만 실행한다. `Play.cs`는 외부 검수 도구이며 게임 스크립트가 아니다. before_play 이름은 이전 도구에서 상속한 이름으로 이 폴더의6파일은 모두 보수 후 검사다.

`sync_design.py`는 실제 검수 routes.json을 Decision 도면에 반영한다. `finalize.py`는 이번 마감 보고를 작성한 일회성 도구다. `protected_result.json`에서 B3와 사용자 Animator 파일의 비교 차이를 구분하며 나머지 보호74파일은 동일하다. Player·Enemy·UI/UX 기능별 씬은 Old 정리 대상에서 제외한다.

## 변경 기록

- V0.01: 구조·밀도 보수안과 Blender 모델 준비.
- V0.02: Unity 적용,394경로·10,730표본·Play6곳 검수,Decision 동기화와 Player 씬 복귀.
''',encoding='utf-8')
f=H/'Plan.md';s=f.read_text(encoding='utf-8');s=s.replace('V0.01','V0.02',1);s=s.replace('사용자가 편집 중인 씬을 전환하거나 저장하지 않는다. 현재 B3가 저장된 편집 상태일 때만 해당 씬을 보수한다.','2026-11-09 사용자 허용 후 Player 작업을 저장하고 B3를 보수했다. 종료 후 Player 씬에 복귀했다. 이후에도 편집 중인 사용자 씬을 전환할 때 작업 시간을 조율한다.');s+='\n\n## 변경 기록\n\n- V0.02:302배치 보수·실제 통행 및 Play 검수 완료. 현재 상태는 README V0.02와 검수 보고를 따른다.\n';f.write_text(s,encoding='utf-8')
f=R/'SourceAssets/B3_FullFloor/README.md';s=f.read_text(encoding='utf-8');title,rest=s.split('\n',1);m=re.search(r'V(\d+\.\d+)',title);title=title.replace(m.group(0),f'V{float(m.group(1))+.01:.2f}') if m else title+' V0.02';f.write_text(title+'\n\n2026-11-09 후속 구조·밀도 보수는 [B3_StructureRepair](../B3_StructureRepair/README.md)를 우선한다. 현재 layout.json은 T08 곡선과302배치를 반영했다. 이 폴더의 이전 전체 제작기를 다시 실행하지 않는다.\n'+rest,encoding='utf-8')
source=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/06.Data/AssetSources/B3_StructureRepair.json'
source.write_text(json.dumps({'version':'V0.01','author':'송예찬','date':'2026-11-09','source':'SourceAssets/B3_StructureRepair','models':read(H/'models.json'),'lodModels':read(H/'lod_models.json'),'design':'Docs/도면/Decision/원형공동/B3_구조보수/as_built_layout.json','review':'Docs/Review/2026-11-09_B3_StructureRepair/Review.md','newVarcoGenerations':0,'runtimeScriptsAdded':0,'addedPlacements':152,'movedPlacements':14,'totalPlacements':302},ensure_ascii=False,indent=2),encoding='utf-8')
print('Review, gallery, provenance and handoff saved; all local images exist.')
