from pathlib import Path
import json,html,re

R=Path(__file__).resolve().parents[2]
O=R/'Docs/검수/2026-11-08_B5_CeilingLighting'
P=R/'Unity/After_Seconds_Build_V0.01'
audit=json.loads((O/'audit.json').read_text(encoding='utf-8'))
plays=json.loads((O/'play_summary.json').read_text(encoding='utf-8'))
assert len(plays)==5 and all(x['complete'] and not x['errors'] for x in plays)
room_counts=' · '.join(f"{x['code']} {x['fixtures']}개" for x in audit['domes'])
note=('2026-11-08 천장/복도 조명 보강 완료: 일반 돔12곳에 밀폐형 천장등80개와 실제 광원을 대칭 배치했다. '
      '13복도의 기존 등기구98개를 리브 사이로 정렬하고 끝 구간13개를 보강했다. 나머지6복도의 기존 광원16개에는 등기구를 연결했다. '
      '새 광원93개, 씬 Light340개. 리브–등기구 최소 간격52.6cm, 천장 외부 관통/재질 누락0. '
      '같은 시점의 전후 비교에서12돔 모두 밝아졌고 Play5구역 실제 이동·새 게임 경고/오류0을 확인했다. '
      '기존247 Light의 밝기·색·그림자 설정, 프랍·바닥 충돌·게임 C#/Animator·복도 전용 안내선을 보존했다. '
      '새 조명 이름은 구역코드_한글용도_번호이며 전체 하이라키 일괄 개명은 하지 않았다. '
      '**다음은 사용자 외형/밝기 검수 → 지적 사항 보수 → 전체 색감·성능 마감**. 최종 아트 판정0/34 유지. '
      '로컬 저장, 이번 변경 커밋·push 미실시. 작성자 송예찬.')
for rel,old,new,prefix in [
 ('AGENTS.md','0.59','0.60','Docs/'),('CLAUDE.md','0.59','0.60','Docs/'),
 ('Docs/이어하기_2026-11-06.md','0.43','0.44',''),('Docs/회사_작업목록_2026-11-06.md','0.41','0.42','')]:
 p=R/rel;s=p.read_text(encoding='utf-8')
 if note not in s:
  title,body=s.split('\n',1);assert 'V'+old in title
  links=f' [검수 화면]({prefix}검수/2026-11-08_B5_CeilingLighting/review.html) · [검수 결과]({prefix}검수/2026-11-08_B5_CeilingLighting/검수결과.md).'
  p.write_text(title.replace('V'+old,'V'+new)+'\n\n'+note+links+'\n\n이전 단계 기록:\n'+body.lstrip(),encoding='utf-8')
p=R/'Docs/AfterSeconds_메인기획서.md';s=p.read_text(encoding='utf-8')
if note not in s:
 title,body=s.split('\n',1)
 s=title+'\n\n'+note+' [검수 화면](검수/2026-11-08_B5_CeilingLighting/review.html).\n\n'+body.lstrip()
 s=s.replace('- V0.48 (2026-11-08): 사용자 요청에 따른 돔 천장등 보강과 터널 리브 사이 조명 배치 기준. 기존 작업등과 복도 전용 안내선 보존. 송예찬.',
 '- V0.48 (2026-11-08): 돔12곳 천장등80개·13복도98등 리브 사이 정렬·29등 외형 보강, 기하/보존/전후/Play 검수. 기존 작업등 설정과 복도 전용 안내선 유지. 송예찬.')
 p.write_text(s,encoding='utf-8')

report=f'''# B5 천장·복도 조명 검수 V0.01

작성자 송예찬 · 2026-11-08

일반 돔12곳에 천장등80개와 광원을 추가하고, 터널 조명은 리브 사이로 정렬했다. 씬 저장과 재로드, 동일 시점 전후 화면, 실제 Play 입력 검수까지 완료했다. 사용자 최종 외형 판정과 전체 색감·빌드 성능 마감은 남아 있다.

- [전후 비교 전체 화면](review.html)
- 대상: `Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular.unity`
- 시작 Git: `e891c5256911aa1a40763adc91c7318acaff40cc`; 재개 시 `git pull --ff-only` 최신 확인. 이번 변경은 로컬이며 커밋/push하지 않았다.

## 배치

{room_counts}.

기존 CL_PodCeilingLight 모델의 밀폐 하우징·베벨·패킹·확산판·체결부를 재사용했다. 천장 곡면에 맞춰 대칭 배치하고 각 확산판 안쪽에서 실제 Spot Light가 아래를 비춘다. C01은 기존 리브 사이 각도를 사용했다. 다른 모델·공유 재질은 수정하지 않고 `DL_CeilingDiffuser.mat`만 새로 만들었다. 차가운 백색으로 바닥/장비 가독성을 보강했다. 계단/화물 코어 VA·VB·VL의 기존 조명은 유지했다.

13복도(T01,T08~T19)의 기존 등기구98개와 자식 광원을 인접 리브의 중점으로 옮겼다. 양 끝은 문틀–리브 사이로 배치하고13개를 추가해 끝 구간도 맞췄다. T02~T07은 기존 Point Light16개에 외형을 연결하고 광원을 확산판 아래로 정렬했다. 복도에 추가된 외형은29개, 새 광원은13개다. 돔까지 합쳐 새 광원93개, 전체340개다.

하이라키에서 `B5_천장조명 > C01_천장조명 > C01_천장등_01 > 광원`, `B5_복도조명_보강`으로 찾을 수 있다. 전체 기존 하이라키 개명은 이번 범위가 아니다.

## 검수 결과

| 항목 | 결과 |
|---|---|
| 돔/복도 확인 | 12돔 / 19복도 |
| 천장등 메시 정점 | 312,320개 확인, 돔 외부 관통0 |
| 돔 등기구 최저 높이 | 바닥 위4.693m |
| 리브–등기구 종방향 최소 간격 | 52.6cm |
| 문틀–등기구 최소 간격 | 65.2cm |
| 재질 누락 / 배치 검사 문제 | 0 / 0 |
| 기존 Light247개의 설정 | 모두 보존; 복도 위치만 이동 |
| 기존 Renderer/Collider 속성 | 자산·재질·활성·회전 및 Collider 직렬화 속성 동일 |
| 보호 대상 기존 Transform 변경 | 0 |
| 기존 파일5,784개 비교 | 대상 씬만 변경, 나머지5,783개 동일, 삭제0 |
| 기존 게임 코드 / Animator 변경 | 0 / 0 |

복도98등과 그 자식 광원, 외형에 맞춘 기존 광원16개의 위치 변경을 허용 목록으로 기록했다. 기존 천장 충돌체98개는 등기구와 함께 이동했고 새13등의 충돌체도 머리 위에 있다. 바닥·보행 충돌체는 보존했다. 새 돔 등기구에는 보행 충돌체를 추가하지 않았다.

전후 캡처35쌍(돔12·천장4·복도19)은1440×900, 동일 카메라/노출로 촬영했다. 외형 비교용 캡처는 후처리와 가림 컬링을 끄고 촬영했다. C04는 출입 시점이 장비에 가려져 같은 상부 시점에서 새 천장 조명 그룹을 켜고 끈 비교다. 화면의 같은 영역을 비교한 sRGB 평균은12돔 모두 증가했다. 물리적인 조도(lux) 측정으로 해석하지 않는다. 주변광/파이프라인 설정은 변경하지 않았다.

## Play 확인

기존 키보드 W 입력을 약0.5초 주고 구역별8초 동안 프레임 진행과 이동을 기록했다. 실제 Game View를 캡처했으며 게임 카메라의 기존 가림 컬링은 유지했다. 입력·시야 고정·백그라운드 실행은 검수 때만 바꾸고 복구했다.

| 구역 | 진행 프레임 | 이동(m) | 중앙 프레임시간(ms) | p95(ms) | 새 경고/오류 |
|---|---:|---:|---:|---:|---:|
'''
for d in plays:
 report+=f"| {d['label']} | {d['framesAdvanced']} | {d['displacement']:.3f} | {d['medianMs']:.2f} | {d['p95Ms']:.2f} | {len(d['errors'])} |\n"
report+='''
프레임시간은 이 PC의 Unity Editor1920×1080에서 측정한 값이다. 배포 빌드 성능이나 목표60fps 달성의 증거는 아니다. 추가 광원에 저해상도 URP 그림자를 사용했으며 최종 성능 조정은 전체 마감 단계에서 진행한다. C01/C03은 천장을 올려다보는 실제 Play 화면도 별도로 확인했다. C01의 최종8등 재배치 후 실험동 이동·천장 시야를 다시 측정했다.

초기 설정 중 Built-in 전용 그림자 옵션 경고는 URP 전용 설정으로 수정했다. C01/C03의 약한 조명은 새 천장등에만 별도 shadow bias를 적용해 해결했다. 초기 캡처 경로 오류/중단 시 검수 스크립트 참조 오류는 준비 과정 기록에 보존했으며 성공한 최종5구역 측정과 구분한다. 게임 스크립트 오류로 집계하지 않는다.

## 근거와 다음 작업

[배치 검사](audit.json), [C01 리브 간격](c01_rib_clearance.json), [기존 상태 보존](preservation.json), [Play 측정](play_summary.json), [천장 Play 측정](play_ceiling_summary.json), [밝기 비교](brightness.json), [최종 에디터 상태](final_state.json), [최종 콘솔](final_console.json).

C01은8개 리브 사이에8등을45° 간격으로 배치했다. 전체 광원 세기를 유지하도록 각 등을13→9.75로 낮췄다. 등기구 바운딩 구와 실제 리브 삼각형의 보수적 최소 간격79.75cm를 확인했다. Unity가 새 등80개의 shadowNearPlane을0.1로 보정하는 동작을 확인해 이 값으로 저장했다. 초기 제작 내역 apply.json의78등/338광원은 보정 전 기록이며 현재 기준은 audit.json의80등/340광원이다.

사용자 시야에서 돔 밝기·터널 간격을 확인한 뒤 필요 지점을 보수한다. 전체 색감/후처리·성능 마감과 하이라키 전체 이름 정리는 별도다. 이동 안내선은 복도 전용으로 유지한다. 최종 아트 판정은 사용자 검수 전0/34를 유지한다.

## Revision History

| 버전 | 날짜 | 작성자 | 변경 |
|---|---|---|---|
| V0.01 | 2026-11-08 | 송예찬 | 돔 천장등·복도 정렬 및 보존/화면/Play 검수 |
'''
(O/'검수결과.md').write_text(report,encoding='utf-8')

sections=[]
for category,files in [('돔 내부',sorted((O/'after').glob('*_room.png'))),('천장 배치',sorted((O/'after').glob('*_ceiling.png'))),('복도 간격',sorted((O/'after').glob('B5-T*.png')))]:
 cards=''
 for f in files:
  cards+=f'<article><h3>{html.escape(f.stem)}</h3><div class="pair"><figure><a href="before/{f.name}"><img loading="lazy" src="before/{f.name}" alt="{f.stem} 변경 전"></a><figcaption>변경 전</figcaption></figure><figure><a href="after/{f.name}"><img loading="lazy" src="after/{f.name}" alt="{f.stem} 변경 후"></a><figcaption>변경 후</figcaption></figure></div></article>'
 sections.append(f'<section><h2>{category}</h2>{cards}</section>')
playcards=''.join(f'<figure><a href="{f.name}"><img loading="lazy" src="{f.name}" alt="{f.stem}"></a><figcaption>{f.stem}</figcaption></figure>' for f in sorted(O.glob('play_*.png')))
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>B5 천장·복도 조명 비교</title><style>body{margin:auto;max-width:1600px;padding:28px;background:#141c23;color:#e7edf2;font:16px/1.6 system-ui,sans-serif}h1,h2,h3{line-height:1.3}h2{margin-top:48px;border-bottom:1px solid #526675;padding-bottom:12px}article{margin:28px 0}.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}figure{margin:0}img{display:block;width:100%;border-radius:6px}figcaption{color:#afc0cc;padding:6px}a{color:#8ddbe8}.plays{display:grid;grid-template-columns:1fr 1fr;gap:16px}@media(max-width:650px){.pair,.plays{grid-template-columns:1fr}body{padding:16px}}header{padding:22px;background:#20303c;border-radius:10px}</style><header><h1>B5 천장·복도 조명</h1><p>돔12곳 천장등80개 · 터널13곳 리브 사이 정렬 · 복도6곳 등기구 보강</p><p>왼쪽 변경 전 / 오른쪽 변경 후. 이미지를 누르면 원본 크기로 볼 수 있습니다.</p><p>작성자 송예찬 · 2026-11-08 · <a href="검수결과.md">수치·보존·Play 검수 기록</a></p></header>'''+''.join(sections)+'<section><h2>실제 Play 화면</h2><div class="plays">'+playcards+'</div></section></html>'
(O/'review.html').write_text(page,encoding='utf-8')

source={'author':'송예찬','date':'2026-11-08','task':'B5 돔 천장등·복도 리브 사이 등기구 정렬','source':'기존 프로젝트 모델과 재질을 재사용. 외부 생성/다운로드 없음.',
 'reusedAssets':['Assets/Afrer_Seconds/05.Model/Environment/B5/CL_PodCeilingLight.fbx','Assets/Afrer_Seconds/05.Model/Environment/Common/CFD_SealedLight.prefab'],
 'newMaterial':'Assets/Afrer_Seconds/05.Model/Environment/B5/Materials/DL_CeilingDiffuser.mat','ceilingFixtures':80,'corridorFixturesMoved':98,'corridorFixturesAdded':29,'newLights':93,
 'script':'SourceAssets/B5_CeilingLighting/Apply.cs','report':'Docs/검수/2026-11-08_B5_CeilingLighting/검수결과.md','originalAssetsPreserved':True}
(P/'Assets/Afrer_Seconds/06.Data/AssetSources/B5_CeilingLighting_20261108.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'SourceAssets/B5_CeilingLighting/README.md';s=p.read_text(encoding='utf-8')
if 'V0.01' in s.splitlines()[0]:
 s=s.replace('V0.01','V0.02',1)
 s+='''

완료: 돔80등, 복도98등 이동·29등 외형 보강(새13광원), 총340 Light. [검수 결과](../../Docs/검수/2026-11-08_B5_CeilingLighting/검수결과.md)와 [전후 화면](../../Docs/검수/2026-11-08_B5_CeilingLighting/review.html)을 따른다.

`prepare.py`, `plan.py`, `Apply.cs`는 최초 작업용이다. 현재 씬에 다시 적용하지 않는다. `Audit.cs`와 `preservation.py`는 저장 상태 비교용이며 before/baseline은 덮어쓰지 않는다. `Capture.After` 재실행 시 `C04Comparison`도 뒤에 실행한다. `Play.cs`는 Assets 밖에서 실행하는 일시 검수 코드이며 게임 코드가 아니다. 검수 전용 경로 오류/중단 자료는 probe에 구분했다. `run_play.py`는 기본5구역, `--ceilings`는 천장 시야2구역을 확인하고 종료 시 배경 실행을 복구한다.

새 천장등은 URP 저해상도 그림자와 개별 bias(0.01/0.015)를 사용한다. 확산판은 `_EMISSION`과 BakedEmissive 플래그를 함께 저장해 URP 재임포트 후 발광이 유지되도록 했다. 새 라이트의 실제 조명은 Realtime Spot이다.

Revision History: V0.01 제작 기준, V0.02 배치·전후·보존·Play 검수 완료. 2026-11-08 송예찬.
'''
 p.write_text(s,encoding='utf-8')
print(json.dumps({'review':str(O/'review.html'),'report':str(O/'검수결과.md'),'playCases':len(plays),'domes':len(audit['domes'])},ensure_ascii=True))
