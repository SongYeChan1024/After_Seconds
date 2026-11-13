"""Build a local review from measured evidence. Does not touch the Unity scene."""
from pathlib import Path
import json,html
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent;O=R/'Docs/Review/2026-11-13_1F_DetailPass'
def read(n):return json.loads((O/n).read_text(encoding='utf-8-sig'))
f=read('final_check.json');p=read('preservation.json');play=read('play.json');walk=read('walk_floor.json');moving=read('moving_parts.json');instances=read('apply.json');ivy=json.loads((H/'ivy.json').read_text());props=json.loads((H/'props.json').read_text());lift=json.loads((H/'lift.json').read_text());walls=json.loads((H/'walls.json').read_text())
assert not f['transformChanges'] and not f['attachmentErrors'] and not f['lodErrors'] and f['missingScripts']==f['missingMeshes']==f['missingMaterials']==f['shaderErrors']==0
assert not p['changedProtectedFiles'] and not p['originalTransformChanges'] and not p['changedGUIDs']
assert play['complete'] and play['framesAdvanced']>0 and not play['errors'] and walk['failed']==0 and not walk['planningFailures']
assert f['saved'] and not f['playing'] and not f['runInBackground']
prop_instances=[q for q in instances if q['integratedLOD'] or q['name'] in ['FD_MotorBench','FD_ToolCart']]
assert len(prop_instances)==49
models=props+lift+walls+[ivy];base=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model';size=sum(next(base.glob('*/1F/'+q['name']+'.fbx')).stat().st_size for q in models)/1024**2
md=f'''# 1F 벽·승강기·아이비·프랍 디테일 검수 V0.01

작성자 송예찬 · 2026-11-13

요청한 네 영역의 근접 디테일을 저장했다. [전후 화면](review.html) · [제작 원본과 부품 연결](../../../SourceAssets/F1_DetailPass/README.md).

## 반영

| 영역 | 반영 내용 |
|---|---|
| 벽 14구역 | 도장 금속판의 볼트 홈·접합부 가장자리·판별 미세 색차·좁은 골, 창 위 물끊기·하단 금속 마감·덮개와 체결점 |
| 승강기 11배치 | 카 패널·바닥 돌기·환기구·조작판, 문 롤러/고무 모서리, 권상기 방열핀/플랜지/브레이크/배선, 도르래 허브, 가이드 이음/피트 스프링/평형추 체결부 |
| 벽 아이비 | 줄기 {ivy['vines']}개·가지 {ivy['branches']:,}개·잎 {ivy['leaves']:,}장. 잎자루·굽은 갈래 잎·잎맥·녹색 명도차와 일부 마른 잎, 창 개구부 회피 |
| 프랍 24종·49배치 | 프레스 호스/계기/가이드, 컨베이어 베어링/장력 조절/모터, 지게차 체인/호스/조작부/타이어, 랙/포장/팔레트/드럼/릴, 수납장/정비대/카트/책상/의자/검사대 마감 |

새 부가 모델 45개와 기존 아이비 모델 1개를 반입했다. 합계 {size:.2f} MiB이며 각 모델은 3단계 LOD를 사용한다. 아이비 삼각형은 LOD0 {ivy['triangles'][0]:,}, LOD1 {ivy['triangles'][1]:,}, LOD2 {ivy['triangles'][2]:,}다. 기존 프랍은 해당 LOD에 새 부품을 포함했다. 생성 면적 0 면은 0개다.

승강기 조작판 글자 방향과 손잡이 간섭을 근접 화면에서 보수했다. 가동부 자식 연결과 기존 피벗·로프 기준은 유지했다. 버튼과 표시는 정적 외형이며 운행·문 제어·무게 제한 기능은 연결하지 않았다. 게임 스크립트는 사용자가 후속 작성한다.

기존 창 비율·지붕 파손·황야와 내부 배치는 유지했다. 비활성화된 운영 소품을 다시 켜지 않았고 다른 층의 공유 원본 모델도 수정하지 않았다.

## 검증

| 검사 | 결과 | 근거 |
|---|---|---|
| 기존 배치/충돌 | 기존 1,778 Transform 변경 0, 부품 296 Transform 추가 → 2,074, Collider 165개 유지 | [최종 상태](final_check.json) |
| 참조/셰이더/LOD | 누락 메시·재질·스크립트·셰이더 오류·LOD 누락 모두 0 | [최종 상태](final_check.json) |
| 승강기 분리 | 카·평형추 이동과 도르래 회전 추종, 고정부 유지 모두 통과 | [부모 연결 검사](moving_parts.json) |
| 통행 | {walk['tested']}/{walk['tested']} 통과, 계획 실패 0 | [통행 검사](walk_floor.json) |
| 실제 Play | 3시점, {play['framesAdvanced']}프레임 진행, 오류/경고 0 | [Play 기록](play.json) |
| 파일/GUID | 보호 기존 파일 {p['protectedExistingFiles']:,}개 해시 일치, 확인한 기존 GUID 변경 0 | [보존 검사](preservation.json) |
| 반사/가림 | 반사 8개 갱신. 기존 가림 데이터 {f['occlusionBytes']:,} bytes 유지 | [반사 목록](reflections.json) |

Play 표본의 프레임 시간 중앙값 {play['medianMs']:.2f}ms·95백분위 {play['p95Ms']:.2f}ms는 이 PC의 에디터에서 짧게 관찰한 값이다. 임시 카메라 렌더 비용을 포함하며 빌드 전체 성능이나 최저 FPS 보장은 아니다. Player·입력·게임 코드는 변경하지 않았다.

다른 층을 실행 중이던 동안에는 [Unity의 분리 미리보기 씬](https://docs.unity3d.com/6000.4/Documentation/ScriptReference/SceneManagement.EditorSceneManager.OpenPreviewScene.html)으로 참조·외형을 검사했다. 사용 중인 씬과 Play 상태를 보존한 기록은 [미리보기 검사](preview_check.json)에 있다. 이후 1F 편집 상태에서 통행과 Play 검사를 수행하고 저장된 편집 상태로 복귀했다. 커밋·push는 하지 않았다.

## 이어서

`Level_1F_Factory.unity`의 저장본이 최신이다. 승강기 조작판/권상기 → C01 프레스/컨베이어/지게차 → C02 랙/적재물 → C03/C04 벽·아이비 순으로 근접 확인할 수 있다. 이전 전체 제작기와 이번 첫 반입 도구를 사용자 후속 수정 뒤 일괄 재실행하지 않는다.

변경 기록: V0.01 — 요청 4영역 제작·보수·검수와 게임 기능 인계 범위 기록. 송예찬.
'''
(O/'Review.md').write_text(md,encoding='utf8')
captions={'Wall':'벽 표면과 아이비 근접','Facade':'공장 외벽과 창 마감','Ivy':'창 주변 아이비와 금속 마감','Lift':'승강기 카 내부','Hoist':'권상기와 도르래','Press':'프레스','ConveyorLong':'컨베이어','Forklift':'지게차','PartsRack':'부품 랙','Switchgear':'배전반','CableReel':'케이블 릴','OfficeDesk_A':'사무 책상·의자','KitchenCounter':'휴게실 작업대','MotorBench':'정비 작업대','ToolCart':'공구 카트','LiftControl':'승강기 조작판 근접'}
sections=[]
for name,title in captions.items():
 after=O/'after'/f'{name}.jpg';before=O/'before'/f'{name}.jpg'
 if not after.exists():continue
 images=''
 if before.exists():images+=f'<figure><figcaption>작업 전</figcaption><a href="before/{name}.jpg"><img loading="lazy" src="before/{name}.jpg" alt="{title} 작업 전"></a></figure>'
 images+=f'<figure><figcaption>작업 후</figcaption><a href="after/{name}.jpg"><img loading="lazy" src="after/{name}.jpg" alt="{title} 작업 후"></a></figure>'
 sections.append(f'<section id="{name}"><h2>{title}</h2><div class="pair">{images}</div></section>')
document='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>1F 근접 디테일 검수 V0.01</title><style>body{margin:0;background:#151918;color:#e4e8df;font:16px/1.65 system-ui,sans-serif}main{max-width:1720px;margin:auto;padding:28px}h1{font-size:30px}h2{font-size:22px}a{color:#c7d9a4}.intro{max-width:1000px;color:#bbc7bb}.pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}figure{margin:0}img{width:100%;display:block}figcaption{padding:6px 0;color:#aab9a9}section{border-top:1px solid #3e4b40;margin-top:35px;padding-top:12px}nav{display:flex;gap:16px;flex-wrap:wrap}@media(max-width:800px){.pair{grid-template-columns:1fr}main{padding:16px}}</style><main><h1>1F 벽·승강기·아이비·프랍 디테일 V0.01</h1><p class="intro">기존 분위기·창 비율·배치를 유지하며 근접 부품을 보강했습니다. 승강기 운행과 문 제어는 후속 스크립트 작업입니다. 이미지를 누르면 원본을 엽니다. 작성자 송예찬 · 2026-11-13.</p><p><a href="Review.md">수치·검증·보존 기록</a></p><nav>'''+''.join(f'<a href="#{k}">{v}</a>' for k,v in captions.items())+'</nav>'+''.join(sections)+'</main></html>'
(O/'review.html').write_text(document,encoding='utf8')
print(json.dumps(dict(models=len(models),newModels=len(models)-1,instances=len(instances),propInstances=len(prop_instances),views=len(sections),modelMiB=round(size,2))))
