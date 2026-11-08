"""Write reviewed local artifacts and increment handoff versions once. Author 송예찬."""
from pathlib import Path
import json,hashlib,html
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'Unity/After_Seconds_Build_V0.01';O=R/'Docs/검수/2026-11-08_B4_ExperimentOperations'
def read(p):return json.loads(p.read_text(encoding='utf8'))
plan=read(H/'layout.json');models=read(H/'models.json');audit=read(O/'audit.json');walk=read(O/'walk.json');preserve=read(O/'preservation.json');plays=[read(f) for f in sorted(O.glob('play_*.json'))]
assert len(plays)==16 and all(p['complete'] and not p['errors'] and p['displacement']>.1 and p['framesAdvanced']>0 for p in plays)
assert not audit['issues'] and not walk['planningFailures'] and len(walk['results'])==320 and all(p['passed'] for p in walk['results'])
assert not preserve['missing'] and not preserve['unexpectedChanges']
source={'author':'송예찬','date':'2026-11-08','task':'B4 능력 측정·발달·강화층 실험 운용 설비','scene':audit['scene'],'source':'로컬 Blender 모델 제작, Pillow 정적 계측/운용 화면과 밀착 라벨 제작. 기존 B4 공용 Base/Normal PBR와 B5 작업의자 재사용.','newModels':[{'name':n,'asset':Path(m['asset']).relative_to(P).as_posix(),'triangles':m['triangles'],'source':f'SourceAssets/B4_ExperimentOperations/{n}.blend','sha256':hashlib.sha256(Path(m['asset']).read_bytes()).hexdigest(),'placed':any(p['model']==n for p in plan['newPlacements'])} for n,m in models.items()],'placements':len(plan['newPlacements']),'usedNewModels':len({p['model'] for p in plan['newPlacements']}),'reusedAssets':['Assets/Afrer_Seconds/05.Model/Props/B5/SF_TaskChair.fbx','Assets/Afrer_Seconds/05.Model/Environment/B4/Materials/B4O_*'],'textures':['BX_Display_23..40: 정적 화면18장','BX_Display_41..42: 밀착 장비/접근 라벨2장','기존 B4O Base/Normal 공용 PBR 재사용'],'sourcePrograms':['equipment.py','worklight.py','textures.py'],'sceneAssembly':['Apply.cs','Repair.cs','BoothAccess.cs','FunctionScreens.cs'],'layout':'SourceAssets/B4_ExperimentOperations/layout.json','report':'Docs/검수/2026-11-08_B4_ExperimentOperations/검수결과.md','limits':['정적 아트; 화면 수치는 장식용 예시이며 게임 규칙이 아님','문/승강기/시험장비/감시 기능 및 B5↔B4↔B3 전환은 후속','최종 아트와 조명/성능은 사용자 전체 검수 후 마감']}
(P/'Assets/Afrer_Seconds/06.Data/AssetSources/B4_ExperimentOperations_20261108.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
roles={
'C01':('종합 계측·반복 시험','중앙 정밀 플랫폼·가변 표적, 유리 관측 부스, 준비/센서 착용·현장 통제·회수 카트. 기존 상부 관찰 데크와 계단 유지.'),
'C02':('시험 전 접수·센서 준비','실험체 확인·호송 대기·센서 부착과 착용대, 청결 장비 보관·기구 세척·응급/수집 카트. 같은 조건의 시험을 준비하는 구역.'),
'C03':('계측기 교정·정비','분해 정비대·정밀 교정랙·전원/신호 접속반, 장비 케이스·케이블 릴·세척/회수. 실험체 시험실을 지원하는 작업실.'),
'C04':('정밀 신호 분석','분석 작업섬·기준/현재 비교석, 시간 기준·교정·수집·소모품/장비 보관. 연구원 작업면을 향한 좌석.'),
'C05':('회차 기록 대조·인계','검토 테이블·기록 인수 확인대, 기존 봉인 기록 랙/서버·인계 해치와 연결. B3의 영구 보관과 구분되는 B4 회차 처리 공간.'),
'W01':('투척 조건·지연 측정','기존 투척 레인에 가변 표적·규격 시험물 보관장·회수 카트·시간 동기화·센서 착용을 보강. 보호 관측석에서 시간 계측과 회차 비교.'),
'W02':('궤적·추적 발달 시험','광학 게이트/좌표 표적에 가변 추적 궤도·교정·수집 설비. 관측 부스에서 목표/실험체 궤적 오차와 반복 결과 비교.'),
'W03':('자극 반응·반응시간 시험','전신 자극벽·압력/위치 계측 플랫폼·차음 구획, 센서 착용·응답 시간 기록·호송 대기. 기존 개별 자극 부스와 함께 사용.'),
'E01':('영상·측정 결과 판독','기존 대형 비교 화면에 동일 조건의 영상 비교석·공동 판독 테이블·기록/수집 카트를 추가.'),
'E02':('발달 계획·다음 시험 준비','회차 검토 테이블·연구 작업열·장비 준비대, 소모품/청결 보관·세척·회수. 시험 조건을 검토하고 다음 세션을 준비.'),
'E03':('시험 후 관찰·회복','리클라이너2곳·센서 제거/상태 검사대·응급 카트·청결 보관·세척, 기존 검사 침대와 연결. B5 생활 공간과 구분되는 단기 시험 후 관찰.'),
'N01':('통합 진행 관찰·통제','개체별 비교석·합동 검토 테이블·경비 이송 상태 감시, 기존 통합 관찰벽/제어석. 세션 상태·반복 기록·호송 인계를 함께 확인.'),
'S01':('차폐·고부하 반복 시험','부하 반복 리그·차폐 전원 제어·현장 통제·응급/회수 설비, 유리 보호 관측석. 구체적인 능력 강화 원리나 약물은 확정하지 않음.'),
'VA':('층간 이송·통제 A','기존17m 계단을 유지하고 경비 현장 통제석·비상 대응 설비 추가.'),
'VB':('층간 이송·통제 B','기존17m 계단을 유지하고 경비 현장 통제석·비상 대응 설비 추가.'),
'VL':('장비 반입·인계','화물 인수 확인대·케이스 보관·회수 카트. 기존 캐빈과 대기화물, 출입 연결 유지.')}
roomrows='\n'.join(f"| {r['id']} | {roles[r['id']][0]} | {sum(p['room']==r['id'] for p in plan['newPlacements'])} | {roles[r['id']][1]} |" for r in plan['rooms'])
playrows='\n'.join(f"| {p['label']} | {p['displacement']:.3f}m | {p['framesAdvanced']} | {p['medianMs']:.2f} / {p['p95Ms']:.2f}ms | 0 |" for p in plays)
report=f'''# B4 실험 운용 설비 검수 V0.01

작성자 송예찬 · 2026-11-08

**B5는 생활·격리/기본 관리, B4는 정밀 측정·발달·강화 진행을 연구하는 본격 실험층**이라는 사용자 결정을 반영했다. 13개 돔과3개 이동 코어에 전용 설비를 채웠으며, 기존22복도와 건축 구조는 유지했다. 현재 저장 씬은 `Level_B4_Circular.unity`, 루트는 `B4_능력측정발달강화층_V0.03`, 새 설비는 그 아래 `B4_실험운용설비`다.

## 각 돔의 운용

| 코드 | 기능 | 새 설비 배치 | 구성과 사용 방식 |
|---|---|---:|---|
{roomrows}

실험체는 **호송 인계 → 대기 → 센서 준비 → 정밀/반복 시험 → 센서 제거·관찰**을 거치도록 잡았다. 경비는 출입·인계·시험 구획을 관리하고, 연구원은 준비/교정·보호 관측·판독/기록·장비 회수를 맡는 구성이다. 보관과 접속 설비는 가능한 벽 주변, 실제 시험 구획은 내부, 연구원 조작석은 유리 보호 구획/작업섬으로 구분했다. 사람과 카트가 지나갈 여유는 남겼다. 실제 인원 AI나 시험 절차 스크립트가 구현된 것은 아니다.

## 제작 내용

- 전용 모델 **35종 제작 /34종 사용**, 새 설비 **210배치**와 기존 작업의자 **27배치**. 별도 출입 게이트 모델 `BX_ScreenedEntry`는 통로 보존을 위해 이번 씬에는 사용하지 않았다.
- 베벨, 장비 베젤·스탠드·키보드, 후면 통풍/접속부, 돌출 손잡이·잠금·캐스터, 기구 교정/보관/회수 부품을 제작했다. 보관장은 내부 선반과 물품이 유리 너머 보이도록 빈 내부 구조를 사용한다.
- 정적 운용/계측 화면18장과 밀착 장비 라벨2장. 기존66개 화면 Renderer도 새 연구 목적에 맞게 씬에서 교체했다. 부스4곳의 주 화면은 각각 압력/위치·시간 기준·추적 오차·부하 신호이며, 보조 화면에는 조건별 비교 막대를 표시한다. 회차 이력은 표로 구분했다. 숫자는 아트 예시다.
- 재질은 기존 B4 금속/코팅/고무/유리의 Base·Normal 맵을 재사용했고 새 LCD/라벨 텍스처를 연결했다. 새 조명44개는 작업등36개와 부스등8개로, 물리 등기구 아래 실제 광원을 맞췄다. 기존261개 광원과 건축 구조는 유지했다.
- `05.Model/Props/B4`에 모델을 두고 하위 `Materials`, `Textures`를 사용한다. 편집 원본35개 `.blend`, 생성/배치/검수 도구는 `SourceAssets/B4_ExperimentOperations`에 보관한다. 외부 생성·업로드는 하지 않았다.

## 배치 보수와 검증

초기 검수에서 C05 기록실의 카트 통로와 W01 시험 통제대, E02 소모품 보관장, E03 청결 보관장 접근이 막혔다. C05 중앙 비상설비1개는 추가 배치에서 제외하고 카트를 이동했으며, 나머지는 접근면을 연결하도록 재배치했다. 관측 부스4곳의 두 의자 간 중앙 통로는1.38m로 넓혔다. 기존 프랍을 덮어쓰거나 옮기지 않고 새 설비만 수정했다.

- 실제 CharacterController **320/320** 경로 통과. 기존 복도/출입/17m 계단104경로 + 새 설비 접근210경로 + 부스 내부4곳/실험체 계측 위치2곳. 계획 실패0. 성인 크기 Controller로 벽/설비 충돌과 바닥 높이를 검사했다.
- 기존 Transform **1,317개** 위치·회전·크기·활성 상태 유지. 재질 누락0, 돔/코어 내부 안내 정점0, 새 광원 방향 문제0. 안내선은 복도 전용이다.
- Renderer {audit['renderers']}, Collider {audit['colliders']}, Light {audit['lights']}, 모든 인스턴스 최고 해상도 삼각형 {audit['triangles']:,}. 새 고유 모델 합계 {sum(m['triangles'] for m in models.values()):,}tri. 기존 B4 가림 베이크와 카메라의 가림 사용을 유지한다. 새 소품은 가림 차폐물로 추가 베이크하지 않았다.
- 작업 시작 Assets/Packages/ProjectSettings **{preserve['protectedFiles']:,}파일 중 대상 B4 씬만 변경**, 나머지 **{preserve['unchanged']:,}파일 SHA-256 동일**. B5, 다른 층, 기존 모델/재질, 게임 C#/Animator, 패키지와 사용자 설정을 보존했다. 시작 상태 네이티브 씬 백업은 SourceAssets에 있다.

| 실제 키보드 Play | 이동 | 진행 프레임 | 중앙값 / P95 | 새 게임 경고·오류 |
|---|---:|---:|---:|---:|
{playrows}

13개 돔과3개 이동 코어에서 각각8초 동안 기존 키보드 W 입력, 실제 이동·프레임 진행·새 게임 로그를 확인했다. 최초1.5초를 제외한 **Editor Play** 프레임 시간으로 출시 빌드 성능 보증은 아니다. 임시 마우스/시점/포커스 설정과 백그라운드 실행은 복원했다. 제작·검수 C#은 SourceAssets에만 있으며 게임 런타임에는 추가하지 않았다.

방별 입구/반대편32장·복도22장·설비/관측석31장·실제 Play16장을 [검수 화면](review.html)에 모았다. 관측 부스에서는 화면 위와 유리 너머 시험 구획이 보인다. 개별 설비와 사용자의 체감 밀도/밝기는 최종 검수 대상으로 남긴다.

## 다음 작업

1. 사용자 관점으로 각 돔의 용도·프랍 디테일·밀도·시야를 검수하고 지적 부분 보수.
2. 전체 층을 기준으로 최종 조명/색감·LOD/그림자 예산 마감. 현재 밝기와 아트는 최종 확정 아님.
3. 화면 애니메이션·실험장비 동작·문/승강기·감시 AI와 B5↔B4↔B3 실제 연결은 별도 게임 기능 작업.

로컬 저장했고 이번 변경은 커밋·push하지 않았다. [이동](walk.json) · [구조/보존 대상](audit.json) · [파일 보존](preservation.json) · [최종 씬](final_state.json).

## Revision History

- V0.01 (2026-11-08): B4 각 돔의 시험·조작·인계·준비/회수 설비 제작과 접근·Play·보존 검수. 송예찬.
'''
(O/'검수결과.md').write_text(report,encoding='utf8')
sections=[]
views=read(O/'role_views.json')
groups=[('시험장과 연구원 관측석',[(v['file'][:-4],v['name']+' · '+v['view']) for v in views]),('각 돔과 이동 코어',[(r['id']+suffix,r['id']+' · '+roles[r['id']][0]+' · '+('진입' if suffix=='_room' else '반대편')) for r in plan['rooms'] for suffix in ['_room','_overview']]),('연결 복도',[(t['id'],t['id']+' · '+t['a']+' ↔ '+t['b']) for t in plan['tunnels']]),('실제 플레이',[(p.stem,p.stem) for p in sorted(O.glob('play_*.png'))])]
for title,pics in groups:
 cards=''.join(f'<figure><a href="{n}.png"><img loading="lazy" src="{n}.png" alt="{html.escape(t)}"></a><figcaption>{html.escape(t)}</figcaption></figure>' for n,t in pics)
 sections.append(f'<h2>{title}</h2><article>{cards}</article>')
table=''.join(f'<tr><td>{r["id"]}</td><td>{roles[r["id"]][0]}</td><td>{roles[r["id"]][1]}</td></tr>' for r in plan['rooms'])
(O/'review.html').write_text('''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>B4 실험 운용 설비 검수</title><style>body{margin:0;background:#10151b;color:#e0e7e8;font:16px/1.65 system-ui,sans-serif}main{max-width:1450px;margin:auto;padding:32px 24px}p{color:#bcc9cf}article{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:20px}figure{margin:0;background:#1b242c;border:1px solid #35414a;border-radius:8px;overflow:hidden}img{display:block;width:100%}figcaption{padding:12px 16px}a{color:#b8d8cc}table{border-collapse:collapse;width:100%}td,th{text-align:left;padding:10px;border-bottom:1px solid #35414a}td:first-child{white-space:nowrap}h2{margin-top:48px}@media(max-width:500px){article{grid-template-columns:1fr}td{font-size:13px;padding:6px}}</style><main><h1>B4 · 능력 측정·발달·강화층</h1><p>실험체의 인계·준비·시험·회복 / 경비의 출입·현장 통제 / 연구원의 교정·조작·판독·기록<br>전용 모델35종 · 신규 설비210배치 + 의자27개 · 작업 광원44개<br>이동320/320 · 16구역 실제 Play 새 경고/오류0 · 송예찬 · 2026-11-08<br><a href="검수결과.md">검수 결과와 범위</a> · 사진을 누르면 원본이 열립니다.</p><table><thead><tr><th>코드</th><th>기능</th><th>배치</th></tr></thead><tbody>'''+table+'</tbody></table>'+''.join(sections)+'<p>현재는 정적 외형이며 계측 화면과 수치는 아트 예시입니다. 최종 밝기·아트는 사용자 검수 후 마감합니다.</p></main></html>',encoding='utf8')
note='''2026-11-08 B4 실험 운용 설비 보강: **B5 생활·격리/기본 관리, B4 본격적인 정밀 측정·발달·강화 연구**라는 결정에 따라13돔·3코어에 새 전용 설비210배치와 의자27개를 추가했다. 모델35종 제작/34종 사용, 정적 화면18장·밀착 라벨2장, 실제 등기구에 맞춘 작업 광원44개. 실험체 인계/대기·센서 준비·시험·회복, 경비 통제, 연구원 교정·보호 관측·판독/기록·회수로 용도를 구분했다. 투척/궤적/반응/차폐·부하 시험은 전용 장비와 화면으로 구별한다. 기존1,317 Transform과22복도 구조 보존, Controller320/320·실제 키보드 Play16구역 새 게임 경고/오류0. 기존6,389파일 중 B4 씬만 변경하고6,388파일 동일. 현재 씬 루트는 B4_능력측정발달강화층_V0.03, 새 하위 그룹은 B4_실험운용설비. **다음은 사용자 전체 검수 → 지적 설비/배치 보수 → 전체 조명·성능 마감**. 화면/설비는 정적이며 구체적인 강화 방식·약물/수치·게임 동작은 확정하지 않았다. 안내선은 복도 전용, B5↔B4↔B3 실제 연결과 문/승강기·실험·AI 기능은 별도다. 로컬 저장, 이번 변경 커밋·push 미실시. 작성자 송예찬.'''
for rel,old,new,prefix in [('AGENTS.md','V0.63','V0.64','Docs/'),('CLAUDE.md','V0.63','V0.64','Docs/'),('Docs/이어하기_2026-11-06.md','V0.47','V0.48',''),('Docs/회사_작업목록_2026-11-06.md','V0.45','V0.46',''),('Unity/README.md','V0.48','V0.49','../Docs/'),('Docs/AfterSeconds_메인기획서.md','V0.54','V0.55','')]:
 p=R/rel;s=p.read_text(encoding='utf8');title,body=s.split('\n',1);assert old in title,(rel,title)
 p.write_text(title.replace(old,new)+'\n\n'+note+f' [검수 화면]({prefix}검수/2026-11-08_B4_ExperimentOperations/review.html) · [검수 결과]({prefix}검수/2026-11-08_B4_ExperimentOperations/검수결과.md).\n\n이전 단계 기록:\n'+body.lstrip()+f'\n- {new} (2026-11-08): B4 시험·보호 관측·준비/기록·회복 설비 보강과 접근/Play 검수. 송예찬.\n',encoding='utf8')
(H/'README.md').write_text('''# B4 실험 운용 설비 제작 V0.01

작성자 송예찬 · 2026-11-08

B4의13돔·3코어에 실험체·경비·연구원 관점의 설비를 보강했다. 새 모델35종 중34종210개를 사용하고 작업의자27개, 실제 광원44개를 연결했다. BX_ScreenedEntry는 제작 에셋으로 보관하며 씬에 배치하지 않았다. 원본 BX_*.blend와 반입 Props/B4/BX_*.fbx, Textures/BX_Display_23..42.png와 대응 재질,06.Data/AssetSources/B4_ExperimentOperations_20261108.json을 사용한다. 기존 B4/B5 원본 모델·공용 Base/Normal 맵을 보존했다.

## 제작과 재실행

`prepare.py`, `Survey.cs`는 시작 기준/백업으로 다시 실행하지 않는다. baseline.json은 이번 작업 시작6,389파일, scene_before.json은 기존1,317 Transform, B4_before.unity는 네이티브 백업이다. equipment.py와 worklight.py는 Blender, textures.py는 Pillow를 사용한다. BX_ONLY=모델명 환경변수는 선택 모델만 재생성한다. 예: BX_ONLY=ProjectileCabinet,CleanReturnCabinet. 모델 파트의 베벨은 export에서 적용되며 LCD/라벨 UV를 별도 유지한다.

초기 반입 Catalog.cs → layout.py → Apply.cs 후, repair_layout.py+Repair.cs로 접근을 보수했다. **현재 layout.json이 최종 배치이며 초기 layout.py/Apply.cs를 다시 실행하지 않는다.** C05 중앙 비상설비 제외·카트 이동, W01 통제대/E02 소모품/E03 대기석 이동 내역은 access_repairs.json이다. BoothAccess.cs로8의자 간격을 조정하고 FunctionScreens.cs로4관측 부스의 주 화면을 방별 계측으로 구별했다. role_access.py는 검사용 부스 내부4점/계측2점을 추가한다. 초기배치와 최종배치의 차이를 유지한다.

## 검수

Review.cs Walk:320경로 Controller 검증; Capture:16공간32뷰+22복도; Roles:설비/관측석31뷰. Audit.cs는 기존 Transform·재질·복도 전용 안내·새 광원 방향을 검사한다. Play.cs는 기존 플레이어의 키보드 W를 사용하고 임시 시점/입력 설정을 복원한다. `play_checks.py C01 C02 C03 C04 C05 W01 W02 W03 E01 E02 E03 N01 S01 VA VB VL`로 이번16구역을 검사했다. 인수 없이 실행하면 기본12구역이므로 전체 검수에는 위 목록을 사용한다.

preservation.py는6,389개 시작 파일 중 B4 씬만 변경되었는지 검사한다. report.py는 모든 검사가 통과한 뒤 문서 버전을 한 번 갱신하므로 중복 실행하지 않는다. FinalState.cs는 복사 보관이 확인된 이번 Play 임시 캡처만 제거하고 B4 편집/저장·원래 플레이어·백그라운드 해제 상태를 확인한다. 검사 C#은 게임 Assets에 넣지 않는다.

작업 중 NavGrid.cs/nav_plot.py는 막힌 접근을 찾은 초기 진단이며 nav_grid.png는 최종 결과가 아니다. 최신 결과는 Docs/검수/2026-11-08_B4_ExperimentOperations/review.html, walk.json과final_state.json이다. 최종 정적 화면·설비 아트이며 실험/문/승강기/감시 동작·층간 전환은 후속이다. 커밋·push하지 않았다.

- V0.01 (2026-11-08): B4 실험 운용 설비·배치 보수·검수·재실행 주의점. 송예찬.
''',encoding='utf8')
print(json.dumps({'createdModels':len(models),'usedModels':source['usedNewModels'],'placements':len(plan['newPlacements']),'playAreas':len(plays),'walkPaths':len(walk['results']),'documentsUpdated':6},ensure_ascii=False))
