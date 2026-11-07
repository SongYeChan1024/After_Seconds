"""Review gallery, source record and handoff. Author 송예찬."""
from pathlib import Path
import json,html,re,collections
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_B5_RemainingDomes';A=R/'Unity/After_Seconds_Build_V0.01/Assets'
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
plan=load(H/'plan.json');guide=load(H/'guidance.json');spacing=load(H/'guide_spacing.json');models=load(H/'models.json');verify=load(D/'verification.json');walk=load(D/'walk.json');pres=load(D/'preservation.json');survey=load(H/'survey.json')
play={name:load(D/f'play_{name}.json') for name in ['living','control','meal','cooling','lift','stairs','corridor']}
assert all(x['passed'] for x in walk['results']) and len(walk['results'])==71
assert all(r['blocked']==0 and r['missing']==0 for r in verify['routes'])
assert verify['degenerate']==0 and not verify['missingMats'] and not pres['missingFiles'] and not pres['gameCodeChanges']
assert not [o for o in survey['overlaps'] if not o['a'].startswith('VB/')]
assert all(p['complete'] and not p['errors'] and p['cameraRotation'][0]<.1 for p in play.values())
names={k:v['name'] for k,v in guide['destinations'].items()}
descriptions={
'C03':'이중 냉각 펌프, 팽창 탱크, 판형 열교환기, 밸브 매니폴드와 실제 포트에 연결한 배관.',
'C04':'분전반·공조기·정비대와 배선. 세 출입구 사이 이동 공간을 확보했다.',
'W01':'침대·책상·세면·변기·개인 수납을 갖춘 생활 자리 4곳, 간호 인계대와 린넨/반납 설비.',
'W02':'생활 자리 4곳과 상태 관찰·이송 인계·생활 물품 수납. 침대 구획과 공용 통로를 분리했다.',
'W03':'진찰 침대, 분리 커튼, 진찰등, 바이탈·초음파 카트, 의료 가스와 소독·약품 수납.',
'E01':'물자 선반, 봉인 상자, 냉장 보관, 입고 확인 작업대와 운반 카트.',
'E02':'조리·배식 준비대, 세척/식기 장비, 식재 보관, 급식 조립 작업대와 트레이 카트.',
'E03':'제염 샤워, 보호구 지급함, 장화 건조대, 교체 벤치와 오염물 반납 설비.',
'N01':'2열 6인 관제석, 시설 지도·재실 상태·전력·공조·기록·정비의 서로 다른 6개 화면, 기록 보관 랙.',
'S01':'시험 갠트리, 제어 콘솔, 진찰/대기 자리, 기록·설비 보관. 화면은 격리 상태의 정적 표현이다.',
'VB':'16m 높이의 8구간·96단 계단, 중간참·난간·소방함·인터폰·등기구. 상부는 닫힌 정적 문이다.',
'VL':'19.4m 승강로, 밀폐된 화물 칸, 가이드·상부 승강장·호출부·층 표시. 승강 동작은 없다.'}
order=['C03','C04','W01','W02','W03','E01','E02','E03','N01','S01','VB','VL']
sections=[]
for code in order:
 imgs=[f'{code}_0.png',f'{code}_1.png']
 for extra in [f'{code}_detail.png','VL_front.png' if code=='VL' else '']:
  if extra and (D/extra).exists():imgs.append(extra)
 cards=''.join(f'<a href="{p}" target="_blank"><img loading="lazy" src="{p}" alt="{html.escape(names[code])} {i+1}"><span>{"입구 시점 "+str(i+1) if i<2 else "세부 확인"}</span></a>' for i,p in enumerate(imgs))
 sections.append(f'<section id="{code}" data-sector="{code[0] if len(code)==3 else "CORE"}"><h2><small>{code}</small> {names[code]}</h2><p>{descriptions[code]}</p><div class="grid">{cards}</div></section>')
corridors=''.join(f'<a href="{t}.png" target="_blank"><img loading="lazy" src="{t}.png" alt="{t} 연결 복도"><span>{t}</span></a>' for t in ['T08','T13','T19'])
plays=''.join(f'<a href="Play_{n}.png" target="_blank"><img loading="lazy" src="Play_{n}.png" alt="{names[c]} 플레이"><span>{names[c]} · 이동 {play[n]["displacement"]:.2f}m</span></a>' for n,c in [('living','W01'),('control','N01'),('meal','E02'),('cooling','C03'),('lift','VL'),('stairs','VB'),('corridor','S01')])
document='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>B5 남은 돔 일괄 검수 · 2026-11-08</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#10161e;color:#e5ebf2;font:16px/1.7 "Malgun Gothic",sans-serif}header,main{max-width:1440px;margin:auto;padding:32px}header{padding-bottom:16px}h1{font-size:32px;letter-spacing:-1px;margin:12px 0}h2{font-size:23px;margin:0}small{color:#8fd3db;margin-right:10px;font:16px monospace}p{color:#b4c2cf;max-width:1100px}a{color:#9ed9e0}nav{position:sticky;top:0;z-index:2;background:#10161ef5;border-block:1px solid #303f50;padding:12px 32px;display:flex;flex-wrap:wrap;gap:8px}button{border:1px solid #3b5266;background:#1c2835;color:#d7e7f6;padding:8px 16px;border-radius:6px;cursor:pointer;font:inherit}button[aria-pressed=true]{background:#396775;color:white}section{margin:12px 0 44px;padding-top:16px;scroll-margin-top:100px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.grid a{display:block;border:1px solid #324152;background:#19222d;text-decoration:none;overflow:hidden;border-radius:8px}.grid img{width:100%;display:block;aspect-ratio:1.6;object-fit:contain;background:#0b1016}.grid span{display:block;padding:10px 14px}.facts{display:flex;flex-wrap:wrap;gap:12px}.facts span{border-left:3px solid #7ccbd4;background:#1b2936;padding:10px 18px}footer{padding:26px 0;color:#9badbf}section[hidden]{display:none}@media(max-width:760px){header,main{padding:20px}.grid{grid-template-columns:1fr}h1{font-size:26px}nav{padding:10px 20px}}</style>
<header><small>AFTER SECONDS / B5 · 2026.11.08</small><h1>남은 돔 일괄 검수</h1><p>작성자 송예찬 · 10개 돔, 계단 B·화물 승강기, T03~T19 복도를 제작해 저장했다. 사진을 누르면 원본 크기로 볼 수 있다. 밝기 보정 없이 현재 씬을 캡처했으며 전체 조명·색감은 사용자 검수 후 조정한다.</p><div class="facts"><span>새 모델 103종</span><span>목적지 15곳 · 복도 19개</span><span>통행 검사 71 / 71</span><span>외형 사용자 검수 대기</span></div><p><a href="검수결과.md">검수 기록</a> · <a href="../../../SourceAssets/B5_RemainingDomes/README.md">제작 원본 안내</a></p></header>
<nav aria-label="구역 필터">'''+''.join(f'<button type="button" data-filter="{key}" aria-pressed="{str(key=="all").lower()}">{text}</button>' for key,text in [('all','전체'),('C','설비'),('W','생활·의료'),('E','생활지원'),('N','중앙관제'),('S','폐쇄시험'),('CORE','이동 코어'),('T','복도'),('PLAY','플레이 확인')])+'''</nav><main>'''+''.join(sections)+f'<section data-sector="T"><h2>연결 복도</h2><p>T03~T19의 곡면 벽, 보호 레일, 배수, 배선과 목적지 색 안내선을 연결했다.</p><div class="grid">{corridors}</div></section><section data-sector="PLAY"><h2>실제 플레이 확인</h2><p>기존 플레이어의 키보드 입력으로 이동했다. 화면은 정적이며 문·승강기 동작과 B4 씬 연결은 후속 작업이다.</p><div class="grid">{plays}</div></section><footer>Unity 씬: Level_B5_Circular · 로컬 저장 · 이번 변경 커밋/push 미실시</footer>'+'''</main><script>document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{const filter=button.dataset.filter;document.querySelectorAll('section[data-sector]').forEach(s=>s.hidden=filter!=='all'&&s.dataset.sector!==filter);document.querySelectorAll('[data-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));window.scrollTo({top:0,behavior:'smooth'});}));</script></html>'''
(D/'review.html').write_text(document,encoding='utf-8')
rows='\n'.join(f'| {c} {names[c]} | {descriptions[c]} |' for c in order)
perf='\n'.join(f'| {names[c] if n!="corridor" else "T19 복도"} | {play[n]["framesAdvanced"]} | {play[n]["displacement"]:.3f}m | {play[n]["screen"][0]}×{play[n]["screen"][1]} | {play[n]["medianMs"]:.2f} / {play[n]["p95Ms"]:.2f}ms | 0 |' for n,c in [('living','W01'),('control','N01'),('meal','E02'),('cooling','C03'),('lift','VL'),('stairs','VB'),('corridor','S01')])
report=f'''# B5 남은 돔 일괄 제작·검수 V0.01

작성자 송예찬 · 2026-11-08

남은 10개 돔과 VB·VL 코어, T03~T19 복도의 외형·용도별 설비·바닥 안내를 `Level_B5_Circular.unity`에 저장했다. 기존 C01·C02·VA 및 T01·T02의 외형을 보존했다. **제작 및 자체 기술 검수를 마쳤으며, 사용자 전체 외형 검수는 남아 있다.** 기존 전체 아트 최종 판정 0/34는 사용자 승인 전까지 유지한다.

[전체 사진을 한곳에서 보기](review.html) · [제작 원본](../../../SourceAssets/B5_RemainingDomes/README.md)

## 제작 범위

| 구역 | 반영 내용 |
| --- | --- |
{rows}

T03~T19 17개 복도에 패널·레일·배수·배선·환기/제어 디테일을 반영하고 남은 문 접합부 29곳을 Clinical Portal로 통일했다. 구형 프랍과 문 원본은 비활성 보관했다. 새 FBX 103종(프랍 48, 환경 55), 프랍 배치 174개와 기존 의자 모델 재사용 6개다. 모델 원본 합계 {pres['modelTriangles']:,}tri, 안내·재사용 구조를 포함한 새 그룹의 고유 메시 {verify['uniqueMeshes']}개 / {verify['triangles']:,}tri다. 인스턴스 반복·그림자 패스의 프레임 통계와는 다르다.

각 모델은 베벨·곡면 노멀, 손잡이·힌지·통풍·소켓·기계 연결부를 포함한다. 기존 도장/강철/바닥 PBR 재질을 재사용하고 천 재질 Base/Normal/MetalSmooth 3장과 역할별 정적 LCD 18장을 추가했다. 중앙관제동 6개 화면은 시설 지도·재실·전력·공조·기록·정비를 나눠 표시한다. 화면 애니메이션과 게임 기능은 구현하지 않았다.

## 안내선

목적지별 색상 15개를 전체 19복도에 연결했다. 새 복도는 양쪽의 직접 연결 목적지를 안내하며, 기존 C01/C02/VA 통과 경로를 유지해 총 38경로다. 15개 선을 모든 복도에 동시에 그리는 방식은 아니다. 새 방향별 바닥 이름 68곳과 목적지 색 범례 15곳, 기존 T01/T02의 표기를 함께 쓴다. 구역 이름은 벽 명판 대신 바닥 안내선에 적는다.

서로 다른 목적지 선/화살표의 최소 여백 {spacing['minMarkerClearance']*100:.2f}cm, 선과 방향 글자 영역 사이 최소 {spacing['minLabelClearance']*100:.2f}cm. 실험동의 흰 R1 순환선과 S1/M1 국소 작업 표시는 유지했다. 계단 도착선은 하단까지 연결하고 출발선은 문 앞 로비부터 시작해 계단 아래에서 교차하지 않도록 했다. S01의 잠금·출입 제한은 아직 게임 기능이 아니다.

## 검수 결과

- 실제 충돌 기준 안내선 {verify['samples']:,}표본: 막힘 0, 바닥 누락 0.
- 기존 CharacterController(반경 0.28m·높이 1.8m)의 38안내 경로, 돔 내부 문 사이 31경로, VB 96단 계단 왕복 2경로: **71/71 통과**.
- 새 그룹 고유 메시: 퇴화 삼각형 0, 재질 누락 0.
- 가구 간 충돌 깊이 15mm 초과 0. VB의 남은 10쌍은 계단·난간·상부 문과 구조 기둥의 접합이며 30~80mm다. `ComputePenetration` 결과와 화면을 대조했으며 비볼록 메시의 모든 표면 접촉을 완전히 증명하는 검사는 아니다.
- 일부 추가 프랍 5개가 반복 재임포트 중 원점으로 돌아가는 현상을 보수했다. 174개 좌표를 계획과 대조하고 프리팹 변경 기록을 저장했다. 공유 모델 4종 강제 재임포트 및 씬 재개방 후 174/174 일치를 확인했다.
- 의료 커튼 방향/정확한 메시 충돌, VB T18 앞 소방함 위치, 냉각 설비 연결 포트, 화물 승강기 표시창 방향을 보수했다.

## 실제 Play

편집기 Game View, 기존 키보드 W 입력, 각 8초 표본. 캡처와 에디터 창 상태에 따라 보고된 해상도는 아래와 같으며 모든 구역의 동일 해상도 성능 비교는 아니다. 마우스/시야 입력은 검수 시에만 정면으로 고정하고 복원했다. 이후 플레이를 종료하고 원래 플레이어 위치(-9.2,-81.36,-10)와 Run In Background=false로 복구했다.

| 위치 | 진행 프레임 | 수평 이동 | 보고 해상도 | 중앙값 / P95 | 새 게임 경고·오류 |
| --- | ---: | ---: | --- | ---: | ---: |
{perf}

VB의 실제 입력 상승량 {play['stairs']['rise']:.3f}m. 벽 너머 구역을 그리지 않도록 34개 가림 검수 영역과 35개 구조 가림 메시를 구성했고, 가림 데이터 191,568bytes를 베이크했다. 문짝은 가림 구조로 굽지 않았다. 생활동 정면 표본에서 가림 적용 전 약30.6ms, 적용 후 약21.4ms를 확인했다(짧은 이동 표본이라 끝점에 약0.3m 차이). 앞선 천장 시점의 약11ms 값은 비교에서 제외했다. 이 값은 편집기 표본이며 독립 실행 빌드의 성능 보장은 아니다. 생활동/설비동의 높은 그림자·렌더링 비용은 최종 조명 조정과 빌드 프로파일링에서 다시 확인한다.

## 보존·남은 작업

작업 시작 시 `git pull --ff-only`는 Already up to date였다. 기존 Assets 파일 4,081개 중 대상 씬만 변경됐고 나머지 **4,080개 SHA256 동일**, 삭제 0, 기존 게임 C#/Animator 변경 0이다. 기존 씬 변경은 원본 문 29곳의 비활성 보관, 이전 외곽 프랍/안내선 비활성 보관, VB/VL 구형 돔 렌더러/충돌 해제, 가림 플래그를 포함한다. 기존 동일 경로 Transform 변경은 VB 광원 2개의 위치뿐이고 색·밝기·범위는 동일하다. 기존 Light 195개를 보존하고 VB 상부 8개를 추가해 203개다. 초기/후속 미저장 상태는 각 단계에서 Temp 백업을 남겼다.

다음은 **사용자 일괄 외형 검수 → 피드백 보수 → B5 전체 조명·색감 조정**이다. B4 실제 씬 연결, 승강기·문 개폐, 화면 애니메이션, 게임 로직은 남아 있다. 게임 C#/Animator는 사용자 직접 구현 방침을 유지한다. 로컬 저장 상태이며 이번 변경은 커밋·push하지 않았다.

원시 근거: [충돌/메시](verification.json), [71경로](walk.json), [기존 자산 보존](preservation.json), [재임포트 배치 보수](placement_repair.json), [가림 베이크](occlusion_result.json), `play_*.json`, [Play 종료 복원](post_play.json).
'''
(D/'검수결과.md').write_text(report,encoding='utf-8')
readme=f'''# B5 남은 돔 일괄 제작 V0.02

작성자 송예찬 · 2026-11-08

사용자 요청에 따라 C03·C04·W01~03·E01~03·N01·S01의 10개 돔, VB·VL 코어, T03~T19를 제작하고 자체 검수를 마쳤다. [전체 검수 화면](../../Docs/검수/2026-11-08_B5_RemainingDomes/review.html) · [결과와 남은 범위](../../Docs/검수/2026-11-08_B5_RemainingDomes/검수결과.md).

새 FBX 103종, 프랍 174배치+의자6, 역할별 LCD18장과 천 PBR3장. 목적지15색/38경로/19복도, 자체 통행71/71 통과. 최종 사용자 외형 검수와 전체 조명 조정은 남는다. 정적 아트만 제작했으며 게임 C#/Animator는 변경하지 않았다.

## 원본과 좌표

- `plan.json`: 현재 174개 프랍과 15목적지/19복도 좌표. `models.json`: 103개 모델 및 삼각형 수.
- `build.py`, `architecture.py`, `cores.py`, `detail.py`, `finish.py`, `safety_fix.py`: Blender 제작. `RD_*.blend`: 편집 가능한 개별 원본.
- `textures.py`: 18가지 정적 화면과 천 PBR. `screen_detail_fix.py`: 서로 다른 관제 화면 6개.
- `guidance.json`: 최종 38경로와 방향 표기/범례. `guides.py`는 물리 충돌 그리드로 라인을 설계한다.
- `Apply.cs`, `CoreApply.cs`, `DetailApply.cs`, `FinishApply.cs`, `SafetyFix.cs`: 단계별 Unity 반영 이력. **전체 재실행 금지**. 이미 존재하는 구조를 유지하고 필요한 부분만 수정한다.
- `PlacementRepair.cs`: 프리팹 재임포트 좌표 보수와 174개 대조. 프리팹을 수정하면 `RecordPrefabInstancePropertyModifications`를 기록한 후 저장한다.
- `Grid.cs`, `Verify.cs`, `Walk.cs`, `Survey.cs`: 물리/메시/접촉 검수. `Play.cs`, `run_play.py`: 실제 입력과 프레임 진행 검수. `Capture.cs`: 현재 씬의 사진, `write_review.py`: 검수 문서/갤러리.
- `Occlusion.cs`: 문을 제외한 구조물의 가림 베이크. 가림 데이터는 씬 옆 `Level_B5_Circular/OcclusionCullingData.asset`이다.

`plan.py`와 `detail_plan.py`는 초기 단계 생성기이며 현재 plan.json에 재실행하면 누적 수정이 사라지거나 중복된다. `prepare_play.py`와 `fix_play_*.py` 역시 초기 제작 이력이며 현재 Play.cs 위에 재실행하지 않는다. Blender 모델은 FBX+재질을 `05.Model/{{Props|Environment}}/B5`로 내보내고 .blend는 이 폴더에 보관한다. 씬은 Unity Editor API로만 수정한다.

대상 씬은 `Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular.unity`, 새 그룹은 `Remaining_Domes_Art`, `Remaining_DestinationGuidance`, `B5_Occlusion_ViewVolumes`다. 이전 원형/전체 Apply를 재실행하지 않는다. 게임 구현·B4 연결과 최종 조명은 후속 범위다.
'''
(H/'README.md').write_text(readme,encoding='utf-8')
record=dict(version='V0.01',author='송예찬',date='2026-11-08',scene='Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular.unity',source='SourceAssets/B5_RemainingDomes',review='Docs/검수/2026-11-08_B5_RemainingDomes/review.html',creation='Local Blender geometry and raster textures; existing project PBR materials reused',scope=plan['construction'],models={k:{**v,'asset':str(Path(v['asset']).relative_to(R)).replace('\\','/')} for k,v in models.items()},placements=174,reusedChairs=6,staticDisplays=18,gameplayCodeChanged=False,userArtReview='pending',lightingReview='pending',guidance=dict(destinations=15,corridors=19,routes=38,labels=68,legends=15),verification=dict(controllerPathsPassed=71,guideSamples=verify['samples'],blocked=0,missingFloor=0,degenerateTriangles=0,missingMaterials=0))
(A/'Afrer_Seconds/06.Data/AssetSources/B5_RemainingDomes_20261108.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
summary='2026-11-08 残여 돔 일괄 제작: C03·C04·W01~03·E01~03·N01·S01 10돔, VB 계단/화물 승강기 VL, T03~T19 17복도의 외형을 저장했다. 새 모델103종·프랍174+의자6·정적LCD18장, 목적지15색/38경로/19복도와 방향 표기68곳·색 범례15곳. 통행18,366표본 막힘0·Controller71/71·Play7구역 새 게임 로그0. 프리팹 재임포트 좌표 보수 후174/174 일치. 대상 씬 외 기존 Assets4,080파일 동일, 게임 C#/Animator변경0, Light195개 설정 보존·VB2개 위치 정렬·상부8개 추가. C01/C02/VA/T01/T02 외형 유지, 전체 구조 가림 베이크 반영. **다음은 사용자 일괄 외형 검수 → 보수 → B5 전체 조명·색감 조정**. B4 실제 씬 연결·문/승강기 동작은 미구현. 전체 아트 최종 판정0/34는 사용자 검수 전까지 유지한다. 로컬 저장, 이번 변경 커밋/push 미실시. 작성자 송예찬.'.replace('残여','남은')
docs=[('AGENTS.md','0.54','0.55','Docs/검수/2026-11-08_B5_RemainingDomes'),('CLAUDE.md','0.54','0.55','Docs/검수/2026-11-08_B5_RemainingDomes'),('Docs/AfterSeconds_메인기획서.md','0.43','0.44','검수/2026-11-08_B5_RemainingDomes'),('Docs/이어하기_2026-11-06.md','0.38','0.39','검수/2026-11-08_B5_RemainingDomes'),('Docs/회사_작업목록_2026-11-06.md','0.36','0.37','검수/2026-11-08_B5_RemainingDomes')]
for rel,old,new,link in docs:
 p=R/rel;s=p.read_text(encoding='utf-8-sig');head,tail=s.split('\n',1)
 if f'V{new}' not in head:
  assert f'V{old}' in head,(rel,head)
  s=head.replace(f'V{old}',f'V{new}')+'\n\n'+summary+f' [전체 검수 화면]({link}/review.html) · [검수 결과]({link}/검수결과.md).\n\n이전 단계 기록:\n'+tail.lstrip('\n')
  if rel.endswith('AfterSeconds_메인기획서.md'):
   s=s.replace('| V0.43 | 2026-11-08 |', '| V0.44 | 2026-11-08 | 송예찬 | 남은10돔·2코어·17복도 제작,15목적지 안내 확장, 프리팹 좌표/통행/Play/가림 검수와 일괄 사용자 검수 순서 기록. |\n| V0.43 | 2026-11-08 |',1)
  p.write_text(s,encoding='utf-8')
p=R/'Docs/도면/Decision/원형공동/B5_안내체계/README.md';s=p.read_text(encoding='utf-8-sig');head,tail=s.split('\n',1)
if 'V0.07' not in head:
 s=head.replace('V0.06','V0.07')+'\n\n2026-11-08 전체 현장 확장: 남은 돔과 코어를 제작해 목적지15색·38경로·전체19복도를 연결했다. 새 방향 바닥 표기68곳과 범례15곳, 기존 T01/T02 표기를 함께 쓴다. 각 복도는 직접 연결 목적지별 두 방향 선을 기본으로 하며 기존 C01/C02/VA 통과 경로를 유지한다. 서로 다른 선/화살표 최소 여백9.15cm, 글자 영역 최소45cm, 물리 통행18,366표본 막힘0이다. 이름은 바닥 안내에 표기하며 실험동 국소 R1/S1/M1은 보존했다. 사용자 전체 외형 검수는 남는다. 작성자 송예찬. [현재 좌표·제작 기준](../../../../../SourceAssets/B5_RemainingDomes/README.md) · [검수](../../../../검수/2026-11-08_B5_RemainingDomes/검수결과.md).\n\n이전 단계 기록:\n'+tail.lstrip('\n')
 p.write_text(s,encoding='utf-8')
print('Review gallery, report, source record, and six handoff documents written.')
