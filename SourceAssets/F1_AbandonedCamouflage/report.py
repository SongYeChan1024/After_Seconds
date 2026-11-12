"""Publish verified local handoff and review only. No Git/network writes. Author: 송예찬."""
from pathlib import Path
import json,re,html
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-12_1F_Abandoned';U=R/'Unity/After_Seconds_Build_V0.01'
def read(n):return json.loads((O/n).read_text(encoding='utf8'))
audit=read('audit.json');quality=read('quality.json');walk=read('walk.json');extra=read('walk_extra.json');geometry=read('geometry.json');protected=read('protected.json');look=read('look_test.json');shader=read('shader_validation.json');snapshot=read('snapshot.json');final=read('final_state.json')
plays=[read('play_'+n+'.json') for n in ['VA','VB','VL','C01','C02','C03','C04','OUT','DECK','ROAD','YARD']]
assert not audit['errors'] and not quality['errors'] and not shader['errors'] and not geometry['patches']
assert walk['failed']==0 and not walk['planningFailures'] and extra['failed']==0
assert protected['checked']==protected['unchanged']==13171
assert all(p['complete'] and p['framesAdvanced']>10 and p['displacement']>.3 and not p['errors'] for p in plays)
assert look['complete'] and look['events']>0 and look['yawChange']>.1 and look['pitchChange']>.1 and not look['errors']
assert final['saved'] and not final['playing'] and final['mouseEnabled'] and final['keyboardEnabled']
resources={'newFBX':quality['models'],'newMeshes':quality['meshCount'],'modelBytes':quality['modelBytes'],'lodGroups':audit['lodGroups'],'activeLights':audit['activeLights'],'shadowLights':audit['shadowLights'],'reflectionProbes':8,'terrainSize':[384,28,320],'heightmapResolution':513,'terrainLayers':3,'changedWeatherMaterials':10,'weatherRenderersIncludingLODs':252,'notes':'Editor validation only, not a packaged-build performance or recommended-hardware benchmark.'}
(O/'resources.json').write_text(json.dumps(resources,ensure_ascii=False,indent=2),encoding='utf8')
review=f'''# 1F 위장 폐공장·반복 무늬 보수 검수 V0.01

작성자 송예찬 · 2026-11-12 · Unity 6000.4.0f1 / URP17.4.0

사용자 정정에 따라 지상1층을 **사용하지 않는 위장용 폐공장**으로 다시 구성했다. 기존 운영형 초안은 현재 수용안이 아니다. `Docs/Reference/1F`의 사진6장과08 설계도를 참고했다. 08의 주거실 명칭은 이식하지 않고 중정과 계단 코어 주위 구획만 참고했다. [화면·전후 비교](review.html) · [실제 배치](snapshot.json) · [제작 원본](../../../SourceAssets/F1_AbandonedCamouflage/README.md).

큰 생산동의 파손 지붕·노출 트러스·깨진 격자창, 폐점검 데크와 계단·배관·굴뚝·사일로·붕괴 별동을 구성했다. 경비실과 옛 관리사무실의 화면/작업등을 끄고, 정상 업무·출하를 나타내던30개 배치를 제거했다. 기존 기물55개는 녹·먼지·뒤집힌 의자 등 방치 상태로 남겼다. 바닥과 벽 아래에는 잔해·낙엽·잡초, 외부에는 낡은 울타리와 열린 대문을 배치했다.

384×320m native Terrain에 완만한 기복·배수 저지대·흙/자갈/이끼3레이어, 서측 진입로와 깨진 포장·웅덩이·풀 군락·관목·나무를 구성했다. 높이 범위는 약−0.92~8.82m이며, 건물 가장자리에서 지형 구멍이 노출되지 않게 마감했다. 지하 세 도착점과7연결은 유지했다.

**AE_VA_Walls 후속 정정.** 같은2m 얼룩이 반복되는 현상을 확인해 벽돌 미세 패턴과 큰 벗겨짐을 분리했다. 벗겨짐·습기·녹·바닥 균열은 월드 좌표에 따라 불규칙하게 변하며, 벽돌의 실제 크기를 유지한다. VA/VB/VL, 생산·하역·사무동, 외벽과 굴뚝을 같은 시점에서 비교했다. 관련10재질·LOD 포함252렌더러에 적용했다. URP 기본 조명 코드를 기반으로 Forward/GBuffer 경로와 같은 UnityPerMaterial 배치를 유지한1F 전용 셰이더이며, Unity 패키지는 수정하지 않았다. 출처/라이선스는 제작 원본에 기록했다.

| 검수 | 결과와 근거 |
|---|---|
| 통행 | 주요75/75 + 점검 계단 왕복/외부 도로 왕복4/4. [주요](walk.json), [추가](walk_extra.json) |
| 실제 Play | VA/VB/VL/C01/C02/C03/C04/OUT/DECK/ROAD/YARD 11곳의 키보드 이동·프레임 진행·경고/오류0. 표면 변경 뒤 VA/C01/OUT, 1F 카메라 하늘 설정 뒤 C01/OUT 재검사 |
| Look | 실제 마우스 입력 이벤트와 좌우/상하 회전 확인. [결과](look_test.json). 초기 검수 도구의 너무 짧은 프레임 구간을 시간 기반 준비 구간으로 수정했으며 게임 코드는 미변경 |
| 깊이 충돌 | 불투명 평면0.005m² 이상,0.05mm 허용오차에서 내부/중복/정밀 겹침0. 근접 후보5개는 정밀 평면 불일치. [결과](geometry.json) |
| 메시/참조 | 191FBX·493메시의 비정상 좌표/영면적/역노멀/잘못된LOD0, Read/Write꺼짐. [결과](quality.json) |
| 셰이더 | 지원 상태 정상·컴파일 메시지/오류0. VA 근접과 실제 게임 화면 확인. [결과](shader_validation.json) |
| 조명 | 켜진 작업등/화면 발광0, 자연광1+하늘 반사광7, 그림자광1. 반사8개128px 재베이크·가림 데이터 갱신 |
| 보존 | 이전 Unity13171파일 SHA256 모두 일치. B1·다른층·기존 공유 에셋·게임 C#/Player 프리팹/Animator·빌드 설정 보존. 1F 씬 카메라에만 Skybox 오버라이드 |

새FBX 원본 합계는 **{quality['modelBytes']/1048576:.2f}MiB**다. 식생은 구역별 메시와LOD로 묶었고, 폐기된 초기 씬 오브젝트76개를 제거했다. 전체 프로젝트의 빌드 메모리/VRAM/FPS나 PC 권장 사양을 확정하는 측정은 아니다. [리소스 수치](resources.json).

현재 `Level_1F_Factory` 저장 편집 모드에서 **AE_VA_Walls**를 선택했다. 키보드·마우스 활성, 임시 Play/입력·Run In Background 설정을 복구했다. [마지막 상태](final_state.json). 커밋/push/블로그 게시 미실시.

다음은 사용자의 전체1F 분위기·VA 표면·외부 지형 검수와 지정 구역 보수다. 이번 결과는 정적 아트/충돌 제작과 기술 검수이며 최종 아트 수용을 의미하지 않는다. 실제 층 전환·문/승강기 작동·AI·결말은 별도 게임 기능이다. 다른 층 표면까지 새 셰이더로 바꾸지 않았다.
'''
(O/'Review.md').write_text(review,encoding='utf8')
compare=[('VA_wall','VA 벽 모서리'),('VA_wide','VA 전체 벽'),('VB_wall','VB 코어'),('VL_wall','VL 코어'),('C01_wall','생산동 벽'),('C04_wall','폐관리사무실'),('Factory_exterior','공장 외벽·굴뚝'),('Concrete_floor','콘크리트 바닥')]
cards=''.join(f'<article><h3>{label}</h3><div class="pair"><figure><a href="texture_before/{name}.jpg"><img loading="lazy" src="texture_before/{name}.jpg" alt="{label} 수정 전"></a><figcaption>수정 전 · 반복된 작은 얼룩</figcaption></figure><figure><a href="texture_after/{name}.jpg"><img loading="lazy" src="texture_after/{name}.jpg" alt="{label} 수정 후"></a><figcaption>수정 후 · 위치마다 다른 벗겨짐과 오염</figcaption></figure></div></article>' for name,label in compare)
gallery=['Exterior_approach','Exterior_factory','Exterior_stack','Exterior_courtyard','C01_production','C01_roof_damage','C01_catwalk','C02_loading','C03_checkpoint','C04_office','VA_arrival','VB_arrival','VL_arrival','OUT_gate','overview']
images=''.join(f'<figure><a href="{n}.jpg"><img loading="lazy" src="{n}.jpg" alt="{n}"></a><figcaption>{n}</figcaption></figure>' for n in gallery)
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>1F 위장 폐공장 검수 V0.01</title><style>:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#161b19;color:#e2e3d8;font:16px/1.65 system-ui,sans-serif}header,main{max-width:1320px;margin:auto;padding:32px}header{border-bottom:1px solid #465346}small{letter-spacing:.13em;color:#bbbe95}h1{font-size:38px;line-height:1.2;margin:18px 0}h2{margin-top:52px}h3{font-size:19px;font-weight:500}p{max-width:920px;color:#bfc6bd}a{color:#d1c99b}nav{display:flex;gap:24px}img{width:100%;display:block}figure{margin:0;background:#222a24}figcaption{padding:12px 16px;color:#c5cabd;font-size:14px}.pair,.gallery{display:grid;grid-template-columns:1fr 1fr;gap:16px}article{margin:36px 0}.gallery{gap:24px}.stats{display:flex;gap:30px;padding:24px 0;flex-wrap:wrap}.stats b{font-size:28px;display:block}.stats span{font-size:13px;color:#b6bead}@media(max-width:760px){header,main{padding:20px}.pair,.gallery{grid-template-columns:1fr}h1{font-size:30px}}</style><header><small>AFTER SECONDS / 1F / 2026.11.12 · V0.01</small><h1>연구시설을 숨기는 폐공장</h1><p>가동을 멈춘 생산동, 깨진 지붕과 창, 녹슨 철골과 방치된 마당. 사용자 레퍼런스에 따른 재작업과 AE_VA_Walls 반복 무늬 보수 기록.</p><nav><a href="#surfaces">표면 전후 비교</a><a href="#scene">전체 씬</a><a href="Review.md">검수 기록</a></nav><div class="stats"><div><b>79/79</b><span>통행 검수</span></div><div><b>11곳</b><span>실제 Play 이동</span></div><div><b>384×320m</b><span>Native Terrain</span></div><div><b>10재질</b><span>반복 얼룩 보수</span></div></div></header><main><h2 id="surfaces">벽돌 크기는 유지하고, 반복 얼룩을 제거</h2><p>같은 위치·시점의 Unity 렌더 비교. 이미지를 누르면 원본 크기로 열립니다. 큰 벗겨짐·습기·녹·균열은 월드 좌표를 따르며 작은 벽돌/표면 입자와 분리했습니다.</p>'''+cards+'''<h2 id="scene">폐공장과 주변 부지</h2><div class="gallery">'''+images+'''</div><p>작성자 송예찬. Unity6000.4.0f1. 정적 환경과 충돌 검수이며 최종 아트 수용·빌드 권장 사양 확정은 별도입니다. 커밋/push 미실시.</p></main></html>'''
(O/'review.html').write_text(page,encoding='utf8')
newread='''# 1F 위장 폐공장 제작 원본 V0.02

작성자 송예찬 · 2026-11-12

사용자 정정에 따라 지상1층은 **사용하지 않는 위장용 폐공장**이다. 초기 운영형 초안을 대체했으며, 이어서 AE_VA_Walls의 반복 얼룩을 보수했다. 최신 결과는 [검수](../../Docs/Review/2026-11-12_1F_Abandoned/Review.md)와 [화면 비교](../../Docs/Review/2026-11-12_1F_Abandoned/review.html)를 따른다.

레퍼런스는 `Docs/Reference/1F`의01/02 외관,03/04/06/07 내부 사진,08 평면도다. 08의 주거 용도를 이식하지 않고 중정/코어 구획만 참고했다. 원본 이미지는 수정하지 않았다.

- `architecture.py`, `landscape.py`, `site_structures.py`, `growth.py`: 파손 지붕·격자창·철골·데크·배관·굴뚝·사일로와 식생·잔해/울타리 원본. `site_structures.py`는 동일 구조의 빠른 직접 메시 생성 단계다.
- `site.py`/`terrain.bin`: 513높이맵·128알파맵·건물 하부 구멍. Terrain384×320m·흙/자갈/이끼3레이어. 건물 경계 바깥 구멍 노출 방지.
- `Apply.cs` 최초 적용 후 `Complete`, `Polish.cs`, `FrameCopies.cs`: 기존55기물을 방치 상태로 유지하고 새환경191FBX 반영. 초기 정상 업무 소품30개·대체된 구조/떠 있는 초기 등기구를 포함해76오브젝트 제거. 공유 기존 파일 수정 없음.
- `clean.py`/`CleanExport.cs`/`Refresh.cs`: 정밀 겹침 제거. `QualityExport.cs`의 영면적 면 제거 포함. 새AE모델만 수정하며GUID/노멀/UV를 유지했다.
- `weather_shader.py`/`AEWeathering.hlsl`/`Weather.cs`: 벽돌·미세입자와 큰 월드 좌표 오염을 분리. 관련10재질·LOD 포함252렌더러 적용. URP17.4 Lit 기반 코드의 출처/Unity Companion License는 `weather_source.json`/`Unity-URP-LICENSE.md`. 엔진 패키지 자체는 수정하지 않았다.
- `Walk.cs`, `Play.cs`, `Look.cs`, `Review.cs`, `WeatherReview.cs`: 통행79/79·실제Play11곳·Look·같은 시점 표면 비교. 외부 검수 C#만 사용하며 게임 C#을 추가하지 않았다. 에디터 임시 카메라는 두 번 렌더해 처음 프레임의 재질 초기화를 완료한 뒤 캡처한다.
- `Finish.cs`: 반사8개·가림 베이크/선택. `ExteriorCamera.cs`: 1F 씬 카메라만 SolidColor→Skybox. `Snapshot.cs`는 현재55기물/191환경모델과 반사 참조를 저장한다.

**현재 또는 이전 제작기를 일괄 재실행하지 않는다.** 생성기를 재실행하면 정밀 면 보수가 사라지고, `Apply.Import`를 다시 실행하면 최신 표면 셰이더가 초기 재질로 바뀐다. 후속 사용자의 수정이 있을 수 있으므로 현재 씬을 조사한 뒤 지정 부분만 보수한다. `before.unity`는 초기1F 백업이며Git 제외. `before_layout.json`은 초기 기준이고 현재 배치는 검수 `snapshot.json`과 Decision `as_built_layout.json`이다.

기존Unity13171파일 보존. B1·다른 층·공유 에셋·Player 프리팹/Animator/게임 코드·빌드 설정 미변경. 층 전환·문/승강기·AI·결말은 후속 기능이다. 저장된1F 편집 모드, AE_VA_Walls 선택. 커밋/push/블로그 요청 없음.
'''
(H/'README.md').write_text(newread,encoding='utf8')
summary='2026-11-12 최신 사용자 정정: 지상1F는 사용하지 않는 위장용 폐공장이다. 레퍼런스 기반 파손 지붕/창·철골·굴뚝/사일로·잔해/식생과384×320m Terrain을 저장했다. AE_VA_Walls의 반복 얼룩도 벽돌 크기를 유지한 월드 좌표 오염으로 보수했고 관련10재질에 적용했다. 통행79/79·실제Play11곳·Look·정밀 깊이 충돌0·새메시/셰이더 오류0, 기존Unity13171파일 보존. 현재 Level_1F_Factory 저장 편집, AE_VA_Walls 선택. **다음은 사용자 전체1F 분위기·표면·지형 검수와 지정 구역 보수**다. 이전1F 운영형 초안은 현재 수용안이 아니다. 제작기/Import/report를 후속 편집 뒤 일괄 재실행하지 않는다. 게임 C#/Player 프리팹/Animator·B1/다른층 보존, 1F 카메라에만 Skybox 오버라이드. 커밋/push/블로그 미실시. 작성자 송예찬.'
def prepend(file,oldver,newver,text):
 p=R/file;s=p.read_text(encoding='utf8');lines=s.splitlines();assert oldver in lines[0],(file,lines[0]);lines[0]=lines[0].replace(oldver,newver);s='\n'.join(lines);first,rest=s.split('\n',1);p.write_text(first+'\n\n'+text+'\n\n이전 단계 기록:\n'+rest+'\n\n- '+newver+' (2026-11-12): 지상1F 위장 폐공장·지형 재작업과 반복 무늬 보수/검수 기록. 송예찬.\n',encoding='utf8')
links=' [최신 검수](Docs/Review/2026-11-12_1F_Abandoned/Review.md) · [전후 화면](Docs/Review/2026-11-12_1F_Abandoned/review.html) · [원본](SourceAssets/F1_AbandonedCamouflage/README.md).'
for n in ['AGENTS.md','CLAUDE.md']:prepend(n,'V1.04','V1.05',summary+links)
prepend('Unity/README.md','V0.60','V0.61',summary+' [검수](../Docs/Review/2026-11-12_1F_Abandoned/Review.md) · [화면](../Docs/Review/2026-11-12_1F_Abandoned/review.html).')
prepend('Docs/이어하기_2026-11-12.md','V0.03','V0.04',summary+' [현재 검수](Review/2026-11-12_1F_Abandoned/Review.md) · [전후 비교](Review/2026-11-12_1F_Abandoned/review.html) · [제작 원본](../SourceAssets/F1_AbandonedCamouflage/README.md).')
prepend('Docs/AfterSeconds_메인기획서.md','V0.82','V0.83','**사용자 확정: 지상1층은 현재 가동/근무/출하에 사용하지 않는 위장용 폐공장이다.** 연구시설을 감추는 방치된 외관과 주변 부지를 표현한다. 켜진 작업등·정상 모니터·현재 직원 생활/운영 흔적을 배치하지 않는다. [최신 1F 검수](Review/2026-11-12_1F_Abandoned/Review.md) · [현재 모습](Review/2026-11-12_1F_Abandoned/review.html). 지하3도착점·7연결은 유지하며 실제 층 전환은 후속 기능이다.')
p=R/'Docs/AfterSeconds_메인기획서.md';s=p.read_text(encoding='utf8').replace('지상에 이르면 최근까지 사용한 하역 통로가 낡은 공장 외관과 만난다.','지상에 이르면 방치된 하역 통로가 파손된 공장 외관과 잡초가 자란 부지로 이어진다.').replace('| 1F 폐공장 위장층 | 폐하역장과 녹슨 생산동을 거쳐 출구 검문 구역에 닿는다. 먼지 사이로 최근에 쓰인 통로와 외광이 보인다. | 공장 외부 | 현행 평면 설계 · 원형 씬 제작 전 |','| 1F 폐공장 위장층 | 방치된 폐하역장·생산동·폐경비실에서 외부로 이어진다. 현재 운영하지 않으며 파손 지붕의 외광, 잔해와 식생으로 위장 장소를 표현한다. | 공장 외부 | 위장 폐공장·Terrain 제작 및 표면 보수 · 사용자 검수 |').replace('1F의 폐하역장 → 폐생산동 → 출구 검문 구역 → 외부','1F의 폐하역장 → 폐생산동 → 폐경비실 → 외부').replace('1F는 무전기·안전모·운송 자료를 중심으로 한다.','1F의 무전기·안전모·운송 자료는 과거 후보이며, 현재 위장 폐공장에는 정상 운영 소품으로 배치하지 않는다. 추후 획득 대상으로 채택하려면 방치된 상태와 용도를 다시 결정한다.')
s=s.replace('당장의 레벨 검수는 B1 C01·W02·W03·E01·C04·N01의 밀도·조명·근접 외형이다.','당장의 레벨 검수는 지상1F의 폐공장 분위기·VA 벽 표면·주변 지형과 외부 진입로다.');p.write_text(s,encoding='utf8')
decision=R/'Docs/도면/Decision/원형공동/1F_제작현황';layout=json.loads((H/'before_layout.json').read_text(encoding='utf8'));layout['version']='V0.02';layout['author']='송예찬';layout['condition']='사용하지 않는 위장용 폐공장';layout['placements']=snapshot['placements'];layout['environmentModels']=snapshot['models'];layout['terrain']=json.loads((H/'site.json').read_text(encoding='utf8'))['terrain'];layout['review']='Docs/Review/2026-11-12_1F_Abandoned/Review.md'
for room in layout['rooms']:
 if room['id']=='C01':room.update(name='폐생산동',h=9,roofPeak=11.35)
 if room['id']=='C02':room.update(name='폐하역장',h=7.3,roofPeak=9.1)
 if room['id']=='C03':room['name']='폐경비실'
 if room['id']=='C04':room['name']='폐관리사무실'
(decision/'as_built_layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),encoding='utf8')
(decision/'README.md').write_text('''# 1F 현재 제작 배치 V0.02

작성자 송예찬 · 2026-11-12

지상1층은 **사용하지 않는 위장용 폐공장**이다. 초기 운영형 배치는 이력이며 현재 실제 좌표·기물55개·환경191모델·Terrain은 `as_built_layout.json`을 따른다. 4구역·3코어·7연결과 B1 실제 도착 좌표는 유지했다. C01/C02의 벽 높이9/7.3m·지붕 마루11.35/9.1m, 폐점검 데크와 외부 공정 잔해를 추가했다.

파손 창/지붕·녹·미장 탈락·식생/잔해,384×320m Terrain의 흙/자갈/이끼·배수/진입로·낡은 울타리와 열린 문을 구성했다. AE_VA_Walls를 포함한 벽·철골·바닥의 반복 무늬를 보수했다. [최신 검수](../../../../Review/2026-11-12_1F_Abandoned/Review.md) · [전후 화면](../../../../Review/2026-11-12_1F_Abandoned/review.html).

통행79/79·실제Play11곳·Look·깊이 충돌/새메시/셰이더 검수 완료. 현재 AE_VA_Walls 선택. 다음은 사용자 외형 검수이며 실제 층 전환·AI·문/승강기/결말은 별도 게임 기능이다. 현재/이전 제작기 일괄 재실행 금지. 커밋/push 미실시.
''',encoding='utf8')
for file,oldver,newver in [('SourceAssets/F1_FullFloor/README.md','V0.02','V0.03'),('Docs/Review/2026-11-12_1F_FullFloor/Review.md','V0.01','V0.02')]:prepend(file,oldver,newver,'**이 문서는 초기 운영형 1F의 이력이다. 사용자가 위장 폐공장으로 정정해 전체 환경과 표면을 후속 보수했다. 현재 작업은 SourceAssets/F1_AbandonedCamouflage와 Docs/Review/2026-11-12_1F_Abandoned를 따른다. 이 단계 제작기를 재실행하지 않는다.**')
provenance={'version':'V0.01','author':'송예찬','date':'2026-11-12','project':'After Seconds','scope':'1F abandoned camouflage factory and terrain; repetitive material correction','scene':'Assets/Afrer_Seconds/01.Scenes/Stage/Level_1F_Factory.unity','references':[f'Docs/Reference/1F/{n}.jpg' for n in ['01','02','03','04','06','07','08']],'source':'SourceAssets/F1_AbandonedCamouflage','models':json.loads((H/'models_environment.json').read_text()),'weatherShader':json.loads((H/'weather_source.json').read_text(encoding='utf8')),'review':'Docs/Review/2026-11-12_1F_Abandoned/Review.md','resources':resources}
(U/'Assets/Afrer_Seconds/06.Data/AssetSources/1F_AbandonedCamouflage_20261112.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf8')
print('Verified review, comparison page, design, handoff and provenance written',flush=True)
