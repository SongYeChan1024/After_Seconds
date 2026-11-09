from pathlib import Path
import json,hashlib,subprocess,html,re
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-09_B4_LayoutPolish'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
a=read(O/'audit.json');walk=read(O/'walk.json');plays=[read(p) for p in sorted(O.glob('play_*.json'))]
assert not walk['planningFailures'] and all(r['passed'] for r in walk['results'])
assert len(plays)==7 and all(p['complete'] and p['framesAdvanced']>10 and p['displacement']>.1 and not p['errors'] for p in plays)
assert not a['lightDiff'] and not a['missingMeshes'] and not a['missingMaterials'] and all(not m['degenerate'] and not m['invalid'] and not m['missingMaterials'] for m in a['meshAudit'])
before=read(H/'protected_before.json');changed=[];formatonly=[]
for rel,sha in before.items():
 p=R/rel
 if not p.exists():changed.append(rel+' MISSING');continue
 current=p.read_bytes()
 if hashlib.sha256(current).hexdigest()==sha:continue
 old=subprocess.run(['git','show','HEAD:'+rel],cwd=R,capture_output=True,check=True).stdout
 norm=lambda b:b.decode('utf-8-sig').replace('\r\n','\n').strip()
 if norm(old)==norm(current):formatonly.append(rel)
 else:changed.append(rel)
expected='Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/01.Scenes/Stage/Level_B4_Circular.unity'
assert changed==[expected],changed
protection=dict(files=len(before),contentChanged=changed,serializationOnly=formatonly,unchangedContent=len(before)-len(changed))
(O/'protection.json').write_text(json.dumps(protection,indent=2),encoding='utf8')
models=read(H/'models.json')
provenance=dict(title='B4 layout and equipment polish V0.01',author='Song Ye Chan',date='2026-11-09',source='Blender authored refinement of existing B4 equipment language',scene=a['scene'],models=[dict(name=k,source=f'SourceAssets/B4_LayoutPolish/{k}.blend',asset=f'Assets/Afrer_Seconds/05.Model/Props/B4/{k}.fbx',triangles=v['triangles'],parts=v['parts'],beveled_parts=v['beveled_parts']) for k,v in models.items()],activeAssemblies=113,wallSafety=12,review='Docs/Review/2026-11-09_B4_LayoutPolish/review.html',runtimeCodeChanged=False)
f=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/06.Data/AssetSources/B4_LayoutPolish_20261109.json';f.write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf8')
doc='''# B4 소방 설비와 장비 배치 보수 V0.01

작성자: 송예찬 · 2026-11-09 · 로컬 저장 완료, 커밋·push 미실시

`Level_B4_Circular`의 벽에서 떨어진 소방 설비, 흩어진 카트, 빈 작업대와 벽면을 보수했다. B4는 정밀 측정·발달·강화 연구층이라는 기존 역할을 유지한다. [전후 화면과 상세 검수](review.html).

## 반영한 내용

- 소방 설비 12곳: 독립형 받침대와 큰 세움판을 비활성화하고, 돔 곡률에 맞춘 앵커·고정판으로 벽에 부착했다. 소방함에는 문틀·가스켓·힌지·손잡이·호스 릴, 소화기에는 받침·고정띠·밸브·압력계·안전핀·호스·노즐을 넣었다.
- 카트·수납장·분석대의 배치를 조정했다. 카트를 관련 작업대 옆으로 묶고, 출입 동선과 장비 사용면을 구분했다. C04는 분석대를 안쪽으로 옮겨 소방함 접근 통로를 확보했고, 통로를 막던 이번 추가 랙 1개는 비활성화했다.
- 벽 설비 52개, 작업대 소품 26개, 하부 서랍장 14개, 회수 랙 4개, 계측 카트 3개를 보강했다. E02·N01에는 양면 계측 작업대 각 1개를 추가했다. 새 활성 조립체는 소방 설비를 포함해 113개다.
- 신규 모델 21종을 Blender에서 제작하고 제조 부품의 모서리에 베벨을 적용했다. 얇은 종이·인쇄면은 불필요한 미세 베벨을 제거했다. 소방함·금속·도장 재질은 B4 전용 복제 재질을 사용한다.

## 검수 결과

- CharacterController 이동·장비 접근 331/331 통과. 연결 복도 22곳의 양방향과 VA/VB 17m 계단을 포함한다.
- 실제 Play 7구역(C03·C04·E01·E02·N01·S01·VA): 기존 키보드 W 입력으로 이동, 프레임 진행과 새 경고·오류 0 확인. 샘플별 이동 약 0.92~1.05m. 이 짧은 샘플은 전체 게임 성능 확정을 뜻하지 않는다.
- 모델 21종: 검사 기준 이하 퇴화 삼각형·비정상 정점·누락 재질 0. 씬 누락 메시·재질 0.
- 기존 Light 305개의 위치·밝기·범위·각도 보존. 기존 보호 파일 5,207개 중 내용 변경은 B4 씬 1개다. 게임 C#·Animator·B5와 다른 층은 보존했다.
- 플레이어 시작 위치를 복원하고 B4 편집 모드로 종료했다. Unity Scene 뷰는 C04, 선택은 새 소방 설비다.

## 이어서 볼 부분

사용자가 C04 소방함 접근, E02·N01 작업 구역의 밀도와 정렬을 직접 확인한다. 추가 취향 조정 후 B4 전체 색감·성능 마감으로 이어간다. 이번 변경은 정적인 레벨·프랍 보수이며 문·키패드·적 AI 동작 구현은 포함하지 않는다.

근거: [이동 검사](walk.json), [모델·조명 검사](audit.json), [기존 파일 보존](protection.json), [최종 Editor 상태](final_state.json).
'''
(O/'Review.md').write_text(doc,encoding='utf8')
source='''# B4 배치 보수 제작 원본 V0.01

작성자: 송예찬 · 2026-11-09

현재 완성 배치는 Unity의 `Level_B4_Circular.unity`, 접근 검수 기준은 이 폴더의 `layout.json`이다. [검수 기록](../../Docs/Review/2026-11-09_B4_LayoutPolish/Review.md)을 먼저 읽는다.

- `build.py`, `bay.py`, `BP_*.blend`: 21종 모델 원본. 미터 단위, Unity 전방 +Z, 제조 부품 베벨과 삼각화 후 FBX 반입.
- `Apply.cs`: 반입·1차 적용. `Run`은 중복 적용을 막는다. 기존 배치에 다시 전체 적용하지 않는다. `Import`는 BP 전용 모델·재질만 매핑한다.
- `plan.py`, `changes.json`, `layout_review.png`: **1차 배치 계산 자료**다. 이후 C04 접근 보수와 중앙 작업대 추가가 있으므로 최종 배치처럼 재실행하지 않는다.
- `Refine.cs`, `refinements.json`: C04 접근 보수와 소품 높이 정리. `Enrich.cs`, `enrichment.json`: 하부 서랍장과 양면 작업대 추가.
- `layout.json`, `final_instances.json`, `transform_changes.json`: 최종 검수 기준과 실제 배치 기록. 접근점과 씬을 함께 갱신한다.
- `Review.cs`, `Audit.cs`, `Play.cs`, `play_checks.py`, `FinalState.cs`: 검수용 외부 Editor 작업. 게임 Assets에 C#을 생성하지 않는다. Play 검수 시 기존 입력 상태를 복원하고 종료 후 background override를 해제한다.
- `before.unity`, `*_before.json`, `geometry.json`: 최초 보존본. 덮어쓰지 않는다. 기존 B4_FullFloor/ExperimentOperations 전체 Apply와 구형 배치 생성기를 실행하지 않는다.

소방 설비는 구형 12개를 비활성 보관하고 새 벽 부착형 12개로 대체했다. C04 추가 회수 랙 1개는 통행 때문에 비활성화했다. 모든 새 이름은 ASCII다. 기존 305 Light와 B5/게임 코드는 보존했다. 커밋·push는 하지 않았다.
'''
(H/'README.md').write_text(source,encoding='utf8')
style='body{margin:0;background:#151c22;color:#e8edf1;font:16px/1.6 system-ui,sans-serif}main{max-width:1440px;margin:auto;padding:32px}h1{font-size:32px}h2{margin-top:48px}a{color:#9bcbdc}p{max-width:1000px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}figure{margin:0;background:#202c35;border-radius:10px;overflow:hidden}img{display:block;width:100%;height:auto}figcaption{padding:12px 16px}.muted{color:#b6c3cd}@media(max-width:850px){.grid{grid-template-columns:1fr}main{padding:18px}}'
body=['<h1>B4 소방 설비와 배치 보수 V0.01</h1><p>벽 부착 소방 설비 12곳 · 작업대와 카트 정렬 · 벽 설비와 수납 보강. 331개 이동·접근 검사와 실제 Play 7구역을 확인했습니다.</p><p><a href="Review.md">검수 기록</a> · <a href="audit.json">모델 검사</a> · <a href="walk.json">이동 검사</a></p>']
def fig(file,label):
 assert (O/file).exists(),file
 with Image.open(O/file) as im:im.verify()
 return f'<figure><a href="{file}"><img loading="lazy" src="{file}" alt="{html.escape(label)}"></a><figcaption>{html.escape(label)}</figcaption></figure>'
for code,label in [('C04','분석 공동'),('E02','연구 작업 공동'),('N01','통합 관찰 공동')]:
 body.append(f'<h2>{code} {label} 전후</h2><div class="grid">'+fig(f'before_{code}.png','수정 전')+fig(f'{code}_room.png','수정 후')+'</div>')
body.append('<h2>벽 고정과 장비 디테일</h2><div class="grid">')
for file,label in [('B4_C04_WallSafety_003_mount.png','C04 소방함과 소화기의 벽 고정'),('B4_E02_CalibrationIsland_detail.png','양면 계측 작업대'),('B4_C04_AnalysisBench_02_detail.png','분석대 하부 수납과 소방 설비 접근'),('B4_E02_ResearchDesk_01_detail.png','기록 작업대의 소품과 서랍')]:body.append(fig(file,label))
body.append('</div><h2>전체 구역</h2><div class="grid">')
for r in read(H/'layout.json')['rooms']:body.append(fig(r['id']+'_overview.png',r['id']+' 배치'))
body.append('</div><h2>실제 Play 확인</h2><div class="grid">')
for p in plays:body.append(fig('play_'+p['label']+'.png',p['label']+f' · 이동 {p["displacement"]:.2f}m · 진행 {p["framesAdvanced"]}프레임 · 새 경고/오류 0'))
body.append('</div><p class="muted">작성자 송예찬 · 2026-11-09 · 로컬 저장. 클릭하면 원본 화면을 볼 수 있습니다.</p>')
(O/'review.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>B4 배치 보수 V0.01</title><style>'+style+'</style><main>'+''.join(body)+'</main></html>',encoding='utf8')
print(json.dumps({'protected':protection,'models':len(models),'walks':len(walk['results']),'playRooms':len(plays)},ensure_ascii=False))
