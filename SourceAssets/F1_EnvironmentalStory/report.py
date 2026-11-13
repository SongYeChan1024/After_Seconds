from pathlib import Path
import json,hashlib,re,shutil
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-13_1F_EnvironmentalStory'
read=lambda n:json.loads((O/n).read_text(encoding='utf8'))
check=read('final_check.json');play=read('play.json');audit=read('audit.json');walk=read('walk_floor.json')
assert check['saved'] and not check['playing'] and not check['runInBackground']
assert not check['transformChanges'] and not check['shaderErrors'] and not check['missingMeshes'] and not check['missingMaterials'] and not check['attachmentErrors'] and not check['lodErrors']
assert play['complete'] and not play['errors'] and walk['tested']==75 and walk['failed']==0 and not audit['changedProtected']
baseline=read('protected_before.json');p='Unity/After_Seconds_Build_V0.01/ProjectSettings/ProjectSettings.asset';assert hashlib.sha256((R/p).read_bytes()).hexdigest()==baseline[p]
models=json.loads((H/'models.json').read_text())+[json.loads((H/(n+'.json')).read_text()) for n in ['ivy','litter']]
E=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/1F';size=sum((E/(q['name']+'.fbx')).stat().st_size for q in models)/1024**2
body=f'''# 1F 사용 흔적과 환경 연결 검수 V0.01

작성자 송예찬 · 2026-11-13

사용자 승인 순서인 **바닥·설비 주변 → 위치별 벽 노후화 → 식생·파손 잔해 연결**을 저장된 `Level_1F_Factory`에 반영했다. [전후 비교 화면](review.html)에서 같은 카메라의 결과를 비교할 수 있다.

1. 바닥·설비 주변: 프레스와 컨베이어에서 배전반 방향으로 이어지는 낮은 트렌치 덮개·전선·연결구를 추가했다. 프레스 바닥 고정판, 두 철거 자리의 절단 앵커8개, 먼지 경계와 끌림 자국, 설비 주변의 국소 기름때, 하역 구역의 굽은 바퀴 마모를 구분했다. 바닥 전용 재질을 실제 `AE_InteriorFloor` Renderer에 연결하고 넓은 콘크리트 줄눈과 미세 마모를 반영했다.
2. 벽: 전체 면의 균일한 녹 얼룩을 줄였다. 실제 창턱 위치에서 내려오는 세로 빗물 흔적, 벽 하단 수분·흙 오염, 판재 이음과 체결점 부식을 집중했다. 앞서 만든 금속판·볼트·창 마감과 줄인 창 비율은 유지했다.
3. 식생·잔해: 61개 뿌리에서 낮게 뻗고 갈라지는 아이비 군락과 잎7,410장, 뿌리 주변 마른 낙엽922장을 제작했다. 녹색·마른 잎을 혼합하고 창 개구부를 피했다. 뿌리61개와 낙엽 정점7,918개의 실제 지면 높이를 조회해 접지를 보정했다. 지붕 파손 아래8곳에 금속 골판 잔해 또는 콘크리트 파편·골재·노출 철근을 구분하고 작은 식생을 함께 배치했다.

| 확인 항목 | 결과 |
|---|---|
| 기존 Transform | 2,074개 위치·회전·스케일·활성 상태 변경0 |
| 추가 구성 | 8개 모델 배치, Transform33개 추가 → 2,107 |
| 모델 | 신규8 FBX + 기존 아이비1 FBX 갱신, 모두3 LOD, 합계{size:.2f} MiB |
| 충돌체·통행 | 기존165개 유지, CharacterController75/75 통과 |
| 메시·재질·스크립트·LOD 참조 | 누락0 |
| 셰이더 | 오류0 |
| 실제 Play | 3시점, {play['framesAdvanced']}프레임 진행, 새 경고·오류0 |
| 관측 프레임 시간 | 중앙값{play['medianMs']:.2f}ms, 95백분위{play['p95Ms']:.2f}ms |
| 보호 파일 | 기존 Unity13,131개 해시 일치 |
| 기존 아이비·표면 GUID | 유지 |
| 지면 접지 | 뿌리61/61 지면+2mm, 허용 범위 이탈0 |
| 반사·가림 | 반사8개 갱신, 기존 가림 데이터229,568바이트 유지 |

프레임 시간은 에디터의 짧은 실제 Play 관측이며 배포 빌드 성능 보장은 아니다. 바닥 부스러기·낙엽·전선은 시각 구성이고 기존 충돌을 바꾸지 않았다. 승강기 운행·문 제어·엔딩 스크립트는 사용자가 작성한다. 이 검수는 요청한 보수 범위의 결과이며 공장 전체 아트의 최종 완성 판정은 아니다.

현재 1F 저장 편집 상태, `EnvironmentalStory` 선택. Player/Input·Animator·다른 층·승강기 피벗·황야는 보존했다. 커밋·push는 하지 않았다. 제작 원본은 [F1_EnvironmentalStory](../../../SourceAssets/F1_EnvironmentalStory/README.md), 에셋 출처 기록은 `Assets/Afrer_Seconds/06.Data/AssetSources/1F_EnvironmentalStory_20261113.json`이다. 첫 Apply와 이전 전체 제작기를 재실행하지 않는다.

검수 자료 관리: 도구를 분리하는 과정에서 이전 DetailPass의 보조 before 캡처 일부와 inventory가 이번 시작 상태로 갱신됐다. 이번 비교의 기준은 이 폴더의 before 자료다. 이전 단계의 수치·완료 상태는 그 단계의 final_check·audit·after 자료를 따른다.

변경 기록: V0.01 — 보수 범위·전후 화면·통행·Play·보존 검수. 송예찬.
'''
(O/'Review.md').write_text(body,encoding='utf8')
views=[('Factory','생산동 전체'),('Footprint','철거 자리와 바닥 마모'),('PressFloor','설비 주변 바닥'),('Loading','하역 구역'),('Facade','창턱·벽 하단 노후화'),('Wall','금속판 근접'),('Ivy','식생 배치 변화'),('OfficeDebris','콘크리트 지붕 아래 잔해')]
html='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>1F 환경 연결 보수 V0.01</title><style>body{margin:0;background:#171b19;color:#e2e3dc;font:16px/1.7 system-ui,sans-serif}main{max-width:1400px;margin:auto;padding:32px}h1{font-size:30px}section{margin:32px 0 52px}a{color:#c8dfb8}.compare{position:relative;aspect-ratio:1.6;overflow:hidden;background:#080a09}.compare img{width:100%;height:100%;object-fit:contain;position:absolute;inset:0}.compare .after{clip-path:inset(0 0 0 50%)}input{width:100%;accent-color:#afbc83}img.full{width:100%;display:block}.label{display:flex;justify-content:space-between;color:#b9c6af}p{max-width:1000px}</style><main><h1>1F 사용 흔적과 환경 연결 보수 V0.01</h1><p>송예찬 · 2026-11-13<br>바닥·설비 연결 → 창턱과 벽 하단의 노후화 → 식생·재질별 지붕 잔해. 기존 동선과 가동부 구조를 유지했습니다.</p><p>슬라이더를 옮겨 같은 카메라의 보수 전·후를 비교하세요. <a href="Review.md">검수 기록</a></p>'''
for key,label in views:
 assert (O/'before'/f'{key}.jpg').exists() and (O/'after'/f'{key}.jpg').exists()
 html+=f'<section><h2>{label}</h2><div class="label"><span>보수 전</span><span>보수 후</span></div><div class="compare"><img src="before/{key}.jpg" alt="{label} 보수 전"><img class="after" src="after/{key}.jpg" alt="{label} 보수 후"></div><input aria-label="{label} 비교 위치" type="range" value="50" min="0" max="100" oninput="this.previousElementSibling.querySelector(\'.after\').style.clipPath=\'inset(0 0 0 \'+this.value+\'%)\'"></section>'
for key,label in [('UtilityConnection','트렌치와 설비 배선'),('FallenMetal','금속 골판 잔해와 작은 식생'),('IvyCluster','분기하는 아이비·창턱 오염·접지한 낙엽')]:html+=f'<section><h2>{label}</h2><a href="after/{key}.jpg"><img class="full" src="after/{key}.jpg" alt="{label}"></a></section>'
html+=f'<p>통행75/75 · 기존2,074 Transform 보존 · 실제Play {play["framesAdvanced"]}프레임 · 새 경고·오류0. 게임 운행·문 제어는 후속 구현 범위입니다.</p></main>'
(O/'review.html').write_text(html,encoding='utf8')
p=H/'README.md';s=p.read_text(encoding='utf8').replace('V0.01\n','V0.02\n',1);s+='''

## 최종 반입과 검수

`models.py`는 설비 연결·앵커·지붕 낙하 흔적·싹을 만든다. `surfaces.py`는 월드 위치에 맞춘 바닥 mode7과 창턱·벽 하단 마스크를 만든다. `ivy.py`는 분기 식생·낙엽을 만들고 `GroundCheck`·`LitterGround`·`ground_litter.py`는 실제 지면 높이에 맞춘다. 바닥 Renderer에는 `AE_M_Floor`가 연결되며 공용 `AE_M_Concrete`를 일괄 변경하지 않는다.

최신 씬에는 `1F_AbandonedFactory/EnvironmentalStory` 아래8개 모델을 연결했다. 기존 `AE_WallIvy`는 같은 GUID로 갱신했다. 원본 프로퍼티·충돌체165개 보존, 통행75/75와 실제Play3시점 통과. 세부 수치는 [검수 기록](../../Docs/Review/2026-11-13_1F_EnvironmentalStory/Review.md)과 [전후 화면](../../Docs/Review/2026-11-13_1F_EnvironmentalStory/review.html)을 따른다.

`Apply.Run`은 처음 반입할 당시의 절차이며 현재 씬에 다시 실행하지 않는다. `FloorBinding`, `RefineModels`, `RefineGrowth`, `Refine`는 이번 검수 중 사용한 제한 갱신이다. 재실행 전에 이후 사용자 변경과 비교해야 한다. `setup.py`도 기존 검수 기준을 덮어쓰므로 다시 실행하지 않는다. 작업 전 백업과 FBX 후보는 `%LOCALAPPDATA%/Temp/AfterSeconds_EnvironmentalStory_20261113/`에 있다.

변경 기록: V0.02 — 실제 재질 연결·접지 보정·최종 모델과 검수 경로 기록. 송예찬.
''';p.write_text(s,encoding='utf8')
intro=f'2026-11-13 최신 환경 연결 보수: 바닥 설비 연결·철거 앵커/마모·국소 기름때 → 창턱/벽 하단 노후화 → 분기 아이비·접지 낙엽·지붕 재질별 잔해를 반영했다. 신규8모델과 아이비 갱신, 기존2,074Transform 변경0·33추가→2,107·Collider165유지. 통행75/75·실제Play3시점{play["framesAdvanced"]}프레임·새 경고/오류0, 보호13,131파일 해시 일치. 승강기 피벗·Player/Input·게임 C#/Animator·다른층·황야 보존. 게임 운행·문 제어는 사용자 후속 구현이다. 저장된 Level_1F_Factory에서 EnvironmentalStory 선택, 로컬 저장·커밋/push 미실시. 첫 Apply/이전 제작기를 일괄 재실행하지 않는다. 작성자 송예찬. '
for name,old,new,prefix in [('AGENTS.md','V1.11','V1.12',''),('CLAUDE.md','V1.11','V1.12',''),('Docs/이어하기_2026-11-12.md','V0.10','V0.11','../')]:
 p=R/name;s=p.read_text(encoding='utf-8-sig');title,rest=s.split('\n',1);assert old in title
 review=('Review/' if prefix else 'Docs/Review/')+'2026-11-13_1F_EnvironmentalStory/'
 s=title.replace(old,new)+'\n\n'+intro+f'[최신 검수]({review}Review.md) · [전후 화면]({review}review.html) · [제작 원본]({prefix}SourceAssets/F1_EnvironmentalStory/README.md).\n\n이전 단계 기록:\n'+rest
 s+=f'\n- {new} (2026-11-13): 바닥·벽 위치별 노후화·식생/잔해 연결과 접지·보존·통행·Play 검수. 송예찬.\n';p.write_text(s,encoding='utf8')
# Retain the earlier valid transform baseline; mark the accidentally recaptured auxiliary images as such.
old=R/'Docs/Review/2026-11-13_1F_DetailPass';original=R/'Docs/Review/2026-11-13_1F_WindowRoofDamage/after_transforms.json'
shutil.copy2(original,old/'before_transforms.json')
p=old/'Review.md';s=p.read_text(encoding='utf8').replace('V0.01\n','V0.02\n',1);s+='\n검수 자료 정정 V0.02: 후속 EnvironmentalStory 도구 분리 중 before/Wall·Facade·Ivy 캡처와 before_inventory가 후속 작업 시작 상태로 갱신됐다. 해당 세 before 이미지는 이 단계의 전후 근거로 사용하지 않는다. 나머지 이전 after·final_check·audit와 당시 검수 결과는 유지한다. before_transforms는 동일 배치인 직전 WindowRoofDamage의 최종1,778개 기록에서 복원했다. 현재 비교 자료는 [환경 연결 보수](../2026-11-13_1F_EnvironmentalStory/review.html)를 따른다. 송예찬.\n';p.write_text(s,encoding='utf8')
p=old/'review.html';s=p.read_text(encoding='utf8');note='<p style="padding:16px;background:#463d25;color:#fff">자료 정정: Wall·Facade·Ivy의 before 사진은 후속 작업 시작 화면으로 갱신되어 이전 단계 비교용으로 사용할 수 없습니다. 그 외 after·검수 수치는 당시 기록을 유지합니다. 최신 비교는 <a href="../2026-11-13_1F_EnvironmentalStory/review.html">환경 연결 보수</a>를 확인하세요.</p>';s=re.sub(r'(<body[^>]*>)',lambda m:m.group(1)+note,s,count=1);p.write_text(s,encoding='utf8')
print('REPORT_READY',len(models),round(size,2),'MiB','12 review views',play['framesAdvanced'],'frames')
