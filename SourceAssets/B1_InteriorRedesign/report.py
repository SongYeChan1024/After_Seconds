"""Publish local review evidence after every required check has passed."""
from pathlib import Path
import json,hashlib,html,shutil
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-12_B1_Interior';U=R/'Unity/After_Seconds_Build_V0.01'
def read(p):return json.loads(p.read_text(encoding='utf8'))
p=read(H/'layout.json');old=read(H.parent/'B1_StaffDataRevision/layout.json');audit=read(O/'audit.json');walk=read(O/'walk.json');public=read(O/'public_walk.json');sight=read(O/'sightlines.json');geometry=read(O/'geometry.json');preserve=read(O/'preservation.json');occ=read(O/'occlusion.json');end=read(O/'final_state.json');culling=read(O/'culling_comparison.json')
plays=[read(f) for f in sorted(O.glob('play_*.json'))];models=read(H/'models_environment.json')
assert not audit['errors'] and not audit['missingScripts'] and not preserve['errors'] and not geometry['patches']
assert not walk['planningFailures'] and all(x['passed'] for x in walk['results'])
assert not public['planningFailures'] and all(x['passed'] for x in public['results'])
assert not sight['privacyExposed'] and not sight['blockedSeats']
assert len(plays)==13 and all(q['complete'] and q['framesAdvanced']>10 and q['displacement']>.3 and not q['errors'] for q in plays)
assert not occ['running'] and end['saved'] and not end['playing'] and end['mouseEnabled'] and end['keyboardEnabled']
assert abs(occ['smallestHole']-.05)<.001 and len(culling['views'])==27
old_by={q['name']:q for q in old['placements']}
moved=sum(1 for q in p['placements'] if q['name'] in old_by and (q['position']!=old_by[q['name']]['position'] or q['yaw']%360!=old_by[q['name']]['yaw']%360))
asset_bytes=sum((U/v['asset']).stat().st_size for v in models.values());triangles=sum(v['triangles'][0] for v in models.values())
metrics={'rooms':13,'cores':3,'tunnels':22,'occupiedZones':len(p['interior']['zones']),'wallRuns':len(p['interior']['walls']),'partialCeilings':len(p['interior']['ceilings']),'placements':len(p['placements']),'relocatedExisting':moved,'reusedExtra':len(p['placements'])-len(old['placements']),'newArchitecturalModels':len(models),'newModelBytes':asset_bytes,'newModelTriangles':triangles,'newTextures':0,'newMaterials':0,'relocatedExistingLights':len(p['interior']['lights']),'activeLights':audit['activeLights'],'shadowLights':audit['shadowLights'],'lodGroups':audit['lodGroups'],'walkPass':len(walk['results']),'publicWalkPass':len(public['results']),'playRooms':len(plays),'framesAdvanced':[min(q['framesAdvanced'] for q in plays),max(q['framesAdvanced'] for q in plays)],'protectedFiles':preserve['checked'],'protectedTransforms':audit['protectedTransforms'],'occlusionBytes':occ['bytes']}
(O/'resources.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf8')
labels={'C01':('자료 열람·대조','남측 열람실과 북측 대조 자리를 분리하고 동·북측 공용 통행을 유지했다.',['reading','comparison','arrival']), 'C02':('기록 인계·정리','네 방향 통로 사이에 인계 업무석·분류 선반·대기 자리를 구분했다.',['intake']), 'C03':('기록 보관','정렬된 보관 선반과 접수·검색 업무를 별도 구획으로 나눴다.',['archive']), 'C04':('직원 의무실','두 진료 자리의 가림, 대기·위생·약품 보관을 분리했다.',['clinic','waiting']), 'C05':('8인 회의장','발표 화면과 좌석을 유지하고 회의실 바깥으로 지나갈 수 있게 했다. 진입 측 창으로 용도가 보인다.',['meeting','arrival','bypass']), 'W01':('직원 사무실','6개 업무석과 기록 보관을 사무 구획으로 묶고 남측 공용 통행을 분리했다.',['office','arrival']), 'W02':('조리·식당·휴게','조리→배식→식사, 식기 회수·휴게와 동측 통과 길을 나눴다. 기존 식탁·소파를 재사용했다.',['dining','kitchen']), 'W03':('직원 침실·위생','4개 이층침대씩 두 침실, 입구 가림, 북측 위생·세탁을 구분했다.',['sleep','vestibule','hygiene']), 'E01':('출입 보안 업무','보안 업무석과 방문·대기·통과 공간을 분리했다. B4→B3 출입 보안 의미를 유지한다.',['security','arrival']), 'E02':('기밀 기록 보관','서측 통과 길과 꺾인 인계 전실, 기록 보관·확인 자리를 구분했다.',['archive','vestibule']), 'E03':('경비 침실·교대','침실·위생·교대 장비·휴게를 나누고 두 출입구 사이 공용 길을 유지했다.',['sleep','handover']), 'N01':('연구 데이터 분석','마주 보는 분석 업무열과 중앙 대조 테이블을 구성했다. 부분 천장 사이에 기존 돔이 보인다.',['analysis','arrival']), 'S01':('백업·서버','서버 두 열과 점검 통로, 백업 업무석·공용 통행을 분리했다.',['servers','backup'])}
rows='\n'.join(f'| {k} | {v[0]} | {v[1]} |' for k,v in labels.items())
report=f'''# B1 전체 실내 구획 재설계 검수 V0.01

작성자 송예찬 · 2026-11-12

11월 11일 합의한 **전체 B1 재설계**를 저장했다. 기존 13공동·3코어·22통로를 유지하며 연구 데이터 업무와 직원 생활을 17개 주요 체류 구획으로 나눴다. 회의장 한 곳의 보수가 아니다. 다음은 사용자 전체 외형·공간 수용 검수이며 1F 진행은 그 뒤에 결정한다.

[구역별 화면](review.html) · [전체 구획도](B1_interior_plan.svg) · [PNG 배치도](B1_interior_plan.png) · [제작 원본](../../../SourceAssets/B1_InteriorRedesign/README.md)

| 구역 | 용도 | 변경 |
| --- | --- | --- |
{rows}

## 구현

- 칸막이 103개 구간, 부분 천장 21개, 낮은 구획·창·전실·기둥·마감. 벽/기둥/천장 등에 새 충돌체269개.
- 기존 가구{moved}개 재배치, 기존 가구 복제5개 추가, 주요 배치203개. 원래 가구198개를 삭제하지 않았다. 직원/경비 이층침대8/4개, 회의석8개를 유지했다.
- 새 FBX13종 **{asset_bytes/1048576:.2f}MiB**, 합계{triangles:,}tri. 새 텍스처0·재질0, 기존 보수 메시·가구 LOD·재질 재사용. 새 구조는 작은 단일 메시이며 구조 형상에 거리 감면을 적용하지 않았다.
- 기존 등기구44개를 부분 천장 아래로 옮겼다. 활성 광원209개·그림자 광원32개, LOD330그룹. 광원 수는 늘리지 않았다.
- 반사16개 갱신(13개 실내 위치 조정), 가림 베이크{occ['bytes']:,}bytes. 천장 틈에서 외벽이 잘못 사라지는 문제를 발견해 최소 구멍 크기를0.25m→0.05m로 조정하고 재비교했다. 이번 첫 베이크732,352bytes 대비119,696bytes 증가했다.

## 검증

- 전체 통로 왕복·출입구·가구 접근·18m 계단: CharacterController **{len(walk['results'])}/{len(walk['results'])}**, 계획 실패0.
- 17개 체류 구획을 통과할 수 없도록 별도로 제한한 공용 동선: **{len(public['results'])}/{len(public['results'])}**, 계획 실패0. 회의·침실 안을 가로지르지 않고 기존 출입구들을 연결할 수 있다.
- 직원/경비 숙소의 모든 출입구→침대 위·아래 자리64개 시선 검사: 직접 노출0. 회의석8개→발표 화면 가림0. 실제 AI 감지 검사가 아니며 좌석에서 화면 쪽으로 고개를 돌렸을 때의 기하학적 시야다.
- 실제 Play **13개 구역**: 기존 키보드 W 입력과 프레임 진행({metrics['framesAdvanced'][0]}~{metrics['framesAdvanced'][1]}프레임/구역), 이동 확인, 새 경고/오류0. 임시 시점·입력 설정과 Run In Background 복구, 편집 모드 저장.
- 전체 B1 정밀 깊이 충돌: 중복 메시0·내부 겹침 후보0, 1mm 후보5개는 0.05mm 정밀 검사에서 실제 겹침0. 불투명 평면0.005m² 이상과 상호 배타적 LOD를 구분한 범위다. 모든 미세/투명 면·모든 플레이 시점을 보증하지 않는다.
- 가림 사용/미사용을27개 눈높이 시점에서 대조했다. E03/W03 침실과 E02 보관실 천장 틈, C05 창 시점을 전후 화면으로 확인했다. 밝기·그림자 차이를 기하 누락과 구분한다. 최종 가림 갱신 뒤 E03/W03/C05 실제 Play 입력·이동·새 로그도 재확인했다.
- 기존 구조·코어·통로 등 Transform **{audit['protectedTransforms']}개 보존**, 보호파일 **{preserve['checked']}개 SHA-256 일치**. 다른 층·B2 펌프·게임 C#·Player 씬·Animator 보존. 반사 위치와 이번 등기구/가구 배치는 의도한 변경이다.
- 메시·재질·스크립트 누락0,203개 계획과 저장 씬 일치. 새 구조 Read/Write 꺼짐.

## 다음 검수

사용자가 C01→C05→W01→W02→W03→E01→E02→E03→N01→S01 및 C02/C03/C04를 실제 눈높이에서 확인한다. 특히 회의장 외곽 우회, 숙소 진입 가림과 체감 폭, 식당 배식/회수 방향을 본다. **통행 합격과 전체 아트 최종 수용은 별도다.**

문·CCTV·에너미 AI·승강기·층간 전환·물건 사용은 미구현이다. 배포 빌드 RAM/VRAM·프레임 시간, 전체 파생 메시2.32GiB 경량화는 별도 할 일로 남았다. 이번에는 재설계와 관련 검수만 수행했으며 커밋·push·블로그 게시는 하지 않았다.
'''
(O/'Review.md').write_text(report,encoding='utf8')
css='body{margin:0;background:#edf1f3;color:#203746;font:16px/1.7 system-ui,"Malgun Gothic",sans-serif}main{max-width:1240px;margin:auto;padding:36px 24px}h1{font-size:32px}h2{border-top:1px solid #c5d3db;padding-top:28px}a{color:#146c82}nav{display:flex;gap:8px;flex-wrap:wrap}nav a{padding:7px 12px;background:#fff;border-radius:5px;text-decoration:none}figure{margin:16px 0;background:#fff;padding:14px;border-radius:8px}img{width:100%;height:auto;display:block}figcaption{font-size:14px;color:#506876;margin-top:8px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.plan{max-height:520px;object-fit:contain}details{padding:12px;background:#fff}small{color:#536a78}@media(max-width:760px){.grid{grid-template-columns:1fr}main{padding:20px 14px}}'
page=['<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>B1 전체 실내 구획 재설계 V0.01</title><style>'+css+'</style><main><small>AFTER SECONDS · 2026-11-12 · 송예찬</small><h1>B1 전체 실내 구획 재설계</h1><p>연구 데이터 업무와 직원 생활을 구획하고, 통과 길과 머무는 자리를 분리했다. 기존 13공동·3코어·22통로는 유지했다.</p><p>이동297/297 · 공용 우회104/104 · 실제 Play13구역 · 사용자 외형 검수 대기</p><nav>']
page += [f'<a href="#{k}">{k} {v[0]}</a>' for k,v in labels.items()]
page.append('</nav><figure><a href="B1_interior_plan.svg"><img src="B1_interior_plan.png" alt="B1 전체 실내 구획과 공용 동선 배치도"></a><figcaption>클릭하면 확대 가능한 원본 SVG. 주황선은 체류 구획을 피하는 검증 통과 경로.</figcaption></figure>')
for k,(title,desc,shots) in labels.items():
 page.append(f'<section id="{k}"><h2>{k} · {title}</h2><p>{desc}</p><div class="grid"><figure><a href="{k}_plan.svg"><img class="plan" src="{k}_plan.svg" alt="{k} 실내 구획 평면도"></a><figcaption>현재 배치 · 부분 천장과 공용 통과 길</figcaption></figure><figure><img loading="lazy" src="{k}_room.jpg" alt="{k} 출입구에서 보는 현재 실내"><figcaption>현재 출입구 시점 · 실제 씬 조명</figcaption></figure></div>')
 for shot in shots:page.append(f'<figure><img loading="lazy" src="{k}_{shot}.jpg" alt="{k} {shot} 눈높이 검수"><figcaption>{k} · {shot} · 눈높이1.7m, 통행 가능한 위치</figcaption></figure>')
 page.append(f'<details><summary>재설계 이전 출입구 화면</summary><img loading="lazy" src="../2026-11-11_B1_StaffData/{k}_room.jpg" alt="{k} 재설계 이전"></details></section>')
page.append('<h2>검수 기록과 범위</h2><p><a href="Review.md">검수 보고서</a> · <a href="resources.json">리소스 변화</a> · <a href="walk.json">전체 통행</a> · <a href="public_walk.json">공용 우회</a> · <a href="sightlines.json">침실·회의장 시야</a></p><p>현재는 정적 공간 재설계다. 다른 층과 게임 코드를 보존했고, 다음 층 제작은 사용자 전체 B1 검수 뒤 결정한다.</p></main></html>')
(O/'review.html').write_text(''.join(page),encoding='utf8')
(H/'README.md').write_text('''# B1 전체 실내 재설계 제작 원본 V0.01

작성자 송예찬 · 2026-11-12

현재 저장된 B1의 최신 실내 제작 원본이다. [검수](../../Docs/Review/2026-11-12_B1_Interior/Review.md) · [화면](../../Docs/Review/2026-11-12_B1_Interior/review.html).

**Apply·plan·models를 사용자 후속 편집 뒤 일괄 재실행하지 않는다.** 이 도구들은 이번 제작의 재현 기록이다. 이전 B1_FullFloor와 B1_StaffDataRevision의 Apply도 현재 씬에 실행하지 않는다. 다음은 사용자 전체 외형·공간 검수 후 지정 범위 보수다.

- plan.py / layout.json: 실제203배치,17체류 구획,103벽 구간,21부분 천장, 기존 광원44개 재배치. 이전 StaffData198배치를 참조해 만든 이번 설계 원본.
- models.py / models_environment.json: Blender 베벨·UV·삼각화, 새 BL_RI_* FBX13개. 기존 B1 재질·텍스처 재사용. structural_colliders.json은 벽·천장·기둥 충돌체.
- Apply.cs: Unity 네이티브 적용·Undo·저장, 현재 배치/보존 감사. 게임 Assets 안에 C#을 추가하지 않았다.
- Inspect.cs / before_scene.json / protected_before.json: 작업 전 기준. 중복 이름 형제도 개별 Transform 값으로 대조하며 원본을 다시 수집해 덮어쓰지 않는다.
- Review.cs / PublicReview.cs: 실제 Collider와 CharacterController 통행. 후자는 체류 구획을 제외한 공용 동선만 검사한다.
- Visual.cs: 눈높이·침실 노출/회의석 화면 시야·가림 사용/미사용 비교.
- Play.cs / run_play.py: 실제 키보드 입력·프레임 진행·새 로그 확인. 임시 설정 복구 후 Play 종료.
- geometry.py: 기존 읽기 전용 Export/분석기를 사용한 전체 B1 깊이 충돌 검사. 정밀도와 한계는 보고서를 따른다.
- Finish.cs: 반사/가림 갱신과 편집 상태 마감. maps.py / report.py는 저장 결과를 바탕으로 로컬 검수 문서를 만든다.

이전 before.unity는 이번 PC의 복구용 사본으로 Git에서 제외했다. Git 기준 시작 커밋은 f663ea07010dc1f40698a55431f9db9ccf286e12다. 원본 메시/GUID·다른 층·Player·Animator·게임 코드 보존, 커밋·push 미실시.
''',encoding='utf8')
provenance={'version':'V0.01','date':'2026-11-12','author':'송예찬','purpose':'B1 research data and staff living interior zoning','source':'SourceAssets/B1_InteriorRedesign/models.py','sourceCommit':'f663ea07010dc1f40698a55431f9db9ccf286e12','method':'Blender procedural beveled architecture; native Unity scene editing; existing furniture, materials, textures and LOD reused','models':models,'metrics':metrics,'runtimeScriptsAdded':False}
(U/'Assets/Afrer_Seconds/06.Data/AssetSources/B1_Interior_Redesign.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf8')
decision=next((R/'Docs').glob('**/Decision/*/B1_제작현황'))
(decision/'as_built_layout.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf8')
(decision/'README.md').write_text('''# B1 현재 제작 배치 V0.03

작성자 송예찬 · 2026-11-12

B1은 연구 데이터 업무와 직원 생활층이다. 실험체 정상 활동은 B5/B4이며 B4→B3부터 상행 출입을 막는다. B1 현장 능력 실험은 없다.

`as_built_layout.json`은 현재203배치·13공동·3코어·22통로와 실내17체류 구획을 담는다. 칸막이·전실·창·부분 천장과 가구 재배치로 업무·회의·식사·수면·위생·교대를 구분했다. 방 위치·연결과 T08 보수는 유지했다.

[현재 구획도](../../../../Review/2026-11-12_B1_Interior/B1_interior_plan.svg) · [현재 화면](../../../../Review/2026-11-12_B1_Interior/review.html) · [검수](../../../../Review/2026-11-12_B1_Interior/Review.md)

전체297/297·공용 우회104/104 통행, 실제 Play13구역 검수. 다음은 사용자 전체 외형·공간 검수다. 실제 보안문·AI·층 전환·장비 UI는 미구현. 이전174/198배치와 실험층 자료는 과거 이력이며 제작기를 재실행하지 않는다.

- V0.02: 용도 정정과8인 회의장/198배치 반영.
- V0.03: B1 전체 실내 구획 재설계·203배치와 최신 검수 연결. 송예찬.
''',encoding='utf8')
print(json.dumps(metrics,ensure_ascii=False,indent=2))
