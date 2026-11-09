from pathlib import Path
import json,html,collections
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-09_B4_LabIdentity'
def read(p):return json.loads(p.read_text(encoding='utf8'))
models=read(H/'models.json');changes=read(H/'changes.json');catalog=read(H/'catalog.json');v=read(O/'verification.json');walk=read(O/'walk.json');local=read(O/'machine_walk.json');protected=read(O/'protected_files.json');plays=[read(p) for p in sorted(O.glob('play_*.json'))]
assert not v['failures'] and not v['stateDiff'] and not v['missingMesh'] and not v['missingMaterials']
assert not walk['planningFailures'] and all(x['passed'] for x in walk['results']) and all(x['passed'] for x in local)
assert all(p['complete'] and p['framesAdvanced']>0 and p['displacement']>.2 and not p['errors'] for p in plays)
visual=sum(m['triangles'] for m in models.values());physical=sum(m['collisionTriangles'] for m in models.values())
md=f'''# B4 실험 시설·1인칭 근접 디테일 보강 V0.01

작성자 송예찬 · 2026-11-09 · 로컬 저장 · 커밋·push 미실시

사용자 피드백은 사무실처럼 보이는 공간, 선으로 대신한 보고서 글자, 단순한 전극 준비대, 어색한 키보드·배선과 왼쪽 마우스였다. **1인칭에서 가까이 보는 디테일을 우선**한다. B4의 기존 공동 목적과 배치는 유지하면서 전용 설비 16종으로 50개 배치를 교체했다. 이전 책상 보조물 18개와 E02 의자 2개는 비활성 보존했다.

## 실제 반영

| 구역/대상 | 변경 |
|---|---|
| E02 연구원 작업실 | 책상 두 곳을 전자 계측대·보호 커버가 있는 시험 챔버로 교체. 중앙 광학 계측 섬과 센서 준비대, 기록석을 구분 |
| C01·W03 | 분리된 힘 측정 발판, 다중 광학 센서와 참조 표식. 센서는 피험체 위치를 향함 |
| C03·C04 | 광학 교정대, 미세 이송/마이크로미터, 신호 분석기·입력 단자·DAQ 랙 |
| W01·W02·S01 | 충격 센서/완충 표적, 통과 축을 향한 광학 게이트, 구동축·로드셀·보호판이 있는 부하 시험기 |
| C02·E03 | 생체 신호 카트와 전극 준비/회수대. 접촉 확인기, 전극 패드/젤/스냅, 개별 포트, 밀봉·개봉 포장, 집게·면봉·마커·회수 리드선 |
| 기록대/클립보드 | 제목·회차·측정표·그래프·관찰 메모·확인란을 갖춘 기록지 6종. 칸을 가짜 직선으로 채우지 않음 |
| 컴퓨터 주변기기 | 오른손 마우스, 폭과 간격이 구별되는 키 배열·키 문자, 후면 단자까지 이어지는 가는 곡선 배선. 인쇄면 방향도 보수 |

기록 보관 C05, 영상 판독 E01, 통합 관찰 N01은 본래 역할을 유지했다. 연구 장비는 밝은 분체도장 케이스·금속 프레임·고무·광학부·유리의 마감을 구분했다. 기존 어두운 무채색 분위기와 광원 수치, 복도 전용 안내선을 유지했다. 화면·문서의 수치와 인물명은 정적 환경 아트 예시이며 확정 게임 규칙·서사·실제 의학 기준이 아니다.

## 확인 결과

| 항목 | 결과 |
|---|---|
| 시각 모델 | 16종, 고유 {visual:,}tri |
| 별도 충돌 모델 | 14종, 고유 {physical:,}tri; 정적 비볼록 MeshCollider |
| 임포트 | 시각/충돌 총 30종, 퇴화 삼각형 {sum(c['degenerate'] for c in catalog)} |
| 씬 누락 | Mesh {v['missingMesh']}, Material {v['missingMaterials']} |
| 주요 통로·설비 접근 | CharacterController {sum(x['passed'] for x in walk['results'])}/{len(walk['results'])}, 경로 계획 실패 0 |
| 측정 발판 두 곳·궤적 게이트 | 진입/이탈 6/6 |
| 기존 Transform·Light | {v['transforms']:,}개 위치/회전/스케일 및 Light {v['lights']}개 설정 보존 |
| 기존 보호 파일 | {protected['total']:,}개 중 B4 씬만 변경, {protected['unchanged']:,}개 동일 |

실제 키보드 Play 검증:
'''
for p in plays:md+=f"\n- `{p['label']}`: {p['framesAdvanced']}프레임, {p['displacement']:.3f}m 이동, 새 게임 경고/오류 {len(p['errors'])}개."
md+='''

발판은 평바닥보다 높으므로 초기 평면 검사에서 C01/W03 접근 두 곳을 잘못 막힘으로 분류했다. 검사기의 발밑 높이를 실제 Raycast 결과로 수정한 뒤 전체 331경로와 발판 진입/이탈을 실제 CharacterController.Move로 통과했다. Collider를 제거하거나 플레이어를 축소하지 않았다.

Play 입력/카메라/백그라운드 설정은 복원했다. B5, 게임 C#/Animator, 기존 에셋 GUID/재질, Player 시작 위치와 물리 설정을 보존했다. Unity 네이티브 API로 저장했으며 현재 B4 편집 모드다. `git diff --check`의 공백 지적은 Unity가 직렬화한 씬의 빈 필드에만 있다. YAML을 손으로 수정하지 않았다.

## 확인 화면과 다음 작업

[전후 비교·근접 사진](review.html)에서 먼저 E03 전극 준비대, 실제 보고서, E02 계측/시험 구획을 본다. E03 전극 준비대를 Unity에서 선택해 두었다. 화면은 후처리를 끈 네이티브 카메라 검수 이미지이며 실제 플레이와 완전히 같은 노출을 보장하지 않는다.

이번 범위의 외형과 기술 검수를 마쳤으며, 모든 프랍의 최종 아트 판정은 아니다. 사용자 근접 검수에서 지적한 대상만 후속 보수한다. 전체 층의 드로콜/LOD·가림 성능과 최종 조명 마감은 별도다. Play 수치는 현재 PC/Editor의 짧은 구간이며 성능 목표 달성을 뜻하지 않는다. 게임 내부 실험·문/AI 코드는 사용자 주도 구현 방침을 유지한다.

[제작 원본](../../../SourceAssets/B4_LabIdentity/README.md) · [이전 바닥·통행 보수](../2026-11-09_FloorSurfaceWear/Review.md)
'''
(O/'Review.md').write_text(md,encoding='utf8')
details=[('close_E03_electrodes','E03 — 전극 패드·포트·준비 도구'),('close_E03_record','E03 — 읽을 수 있는 작업 기록'),('close_E02_keyboard','기록대 — 키 문자·오른손 마우스·배선'),('close_E02_record','기록대 — 회차별 측정표와 관찰 메모'),('detail_B4_E02_ElectronicsBench_03','E02 — 전자계측 작업대'),('detail_B4_E02_TestChamberBench_05','E02 — 보호 챔버와 시험 장치'),('detail_B4_E02_MetrologyIsland','E02 — 광학 계측 작업섬'),('detail_B4_E02_SensorPrepBench_07','E02 — 센서·치구 준비'),('detail_B4_C04_AnalysisBench_01','C04 — 신호 분석'),('detail_B4_C03_SensorWorkbench_01','C03 — 광학 교정'),('detail_B4_C02_VitalCart_02','C02 — 생체신호 수집'),('detail_B4_C03_CalibrationRack_03','C03 — 계측 랙'),('detail_B4_C01_PrecisionPlatform_01','C01 — 측정 발판'),('detail_B4_W01_AdaptiveTargetArray_02','W01 — 충격 표적'),('detail_B4_W02_TrajectoryGantry_01','W02 — 광학 게이트'),('detail_B4_S01_LoadResistanceRig_01','S01 — 부하 시험'),('close_E02_rear','기록대 — 후면 연결')]
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>B4 실험 시설·근접 디테일 V0.01</title><style>body{background:#11191f;color:#e0e8ed;font:16px/1.7 system-ui;margin:36px auto;max-width:1440px;padding:0 24px}h1{font-size:30px}h2{font-size:22px;margin:42px 0 14px}p{max-width:1000px}a{color:#95d4d1}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:22px}figure{margin:0;background:#1b262e;border:1px solid #344650}img{width:100%;display:block}figcaption{padding:12px 16px}.note{padding:16px 20px;background:#203139;border-left:3px solid #95d4d1}nav{position:sticky;top:0;background:#11191fee;padding:12px 0}nav a{margin-right:24px}@media(max-width:800px){.grid{grid-template-columns:1fr}}</style><h1>B4 실험 시설·1인칭 근접 디테일 V0.01</h1><p>2026-11-09 · 송예찬 · Unity 네이티브 렌더</p><p class="note">전용 모델 16종 · 50개 배치 교체 · 읽을 수 있는 기록지 6종 · 331개 통행 경로와 장비 진입/이탈 6방향 통과</p><nav><a href="#close">근접 검수</a><a href="#rooms">공동별 전후</a><a href="Review.md">검수 기록</a></nav><p>기존 공동 역할과 위치를 유지하며 측정·시험·준비/회수의 설비를 구분했습니다. 이미지를 누르면 원본 크기로 봅니다. 수치·기록은 정적 아트 예시이며 게임 동작은 구현하지 않았습니다.</p><h2 id="close">가까이에서 보는 작업 흔적과 설비</h2><div class="grid">'''
for name,caption in details:
 assert (O/(name+'.png')).exists();page+=f'<figure><a href="{name}.png"><img loading="lazy" src="{name}.png" alt="{html.escape(caption)}"></a><figcaption>{html.escape(caption)}</figcaption></figure>'
page+='</div><h2 id="rooms">공동별 동일 시점 비교</h2>'
rooms=read(H/'layout.json')['rooms']
for r in rooms:
 if r['kind']=='core':continue
 code=r['id'];page+=f'<h2>{code}</h2><div class="grid">'
 for phase,caption in [('before','변경 전'),('after','변경 후')]:
  file=f'{phase}_{code}_overview.png';assert (O/file).exists();page+=f'<figure><a href="{file}"><img loading="lazy" src="{file}" alt="{code} {caption}"></a><figcaption>{caption}</figcaption></figure>'
 page+='</div>'
page+='</html>';(O/'review.html').write_text(page,encoding='utf8')
provenance=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/06.Data/AssetSources/B4_LabIdentity_20261109.json'
provenance.write_text(json.dumps(dict(version='0.01',author='송예찬',source='Original Blender construction and PIL typeset fictional records/displays',models=models,changes=changes,review='Docs/Review/2026-11-09_B4_LabIdentity/Review.md',runtimeCodeChanged=False),ensure_ascii=False,indent=2),encoding='utf8')
prefix='''2026-11-09 B4 실험 시설·1인칭 디테일: 사무실 느낌을 줄이기 위해 전용 모델16종으로50배치를 교체했다. E02 전자계측/보호 시험 챔버/광학 계측/센서 준비와 기록석을 구분하고 C01·C03·C04·W01~03·S01의 측정·시험 설비를 강화했다. E03 전극대에 패드/젤/스냅/개별 포트/밀봉·개봉 포장/회수 리드/집게를 반영하고 읽을 수 있는 보고서6종, 계측 화면8종·라벨을 제작했다. 키보드 문자 방향과 오른손 마우스·곡선 배선도 보수했다. 기존 보조물18·의자2 비활성 보존. Controller331/331·장비 왕복6/6·Play3구역 새 경고/오류0, 기존1865 Transform·305 Light·B5/게임 코드 보존. **다음은 E03/E02 근접 사용자 검수 → 지적 프랍만 보수 → 전체 조명·성능 마감**. 앞으로 1인칭 근접 디테일을 우선하고 보고서 글자를 가짜 직선으로 대체하지 않는다. 저장된 B4 편집 모드, E03 전극대 선택. 커밋·push 미실시. [검수](Docs/Review/2026-11-09_B4_LabIdentity/Review.md) · [전후/근접 화면](Docs/Review/2026-11-09_B4_LabIdentity/review.html). 작성자 송예찬.
'''
for name in ['AGENTS.md','CLAUDE.md']:
 p=R/name;s=p.read_text(encoding='utf8')
 if '2026-11-09 B4 실험 시설·1인칭 디테일:' not in s:
  s=s.replace('V0.68','V0.69',1).replace('\n\n','\n\n'+prefix+'\n아래는 이전 단계 기록이다.\n\n',1);s+='\n- V0.69 (2026-11-09): B4 전용 설비·1인칭 근접 기록/전극/입력 장치와 검수 기준. 송예찬.\n';p.write_text(s,encoding='utf8')
print('Report ready',len(models),'models',len(changes['replacements']),'instances',visual,'visual triangles')
