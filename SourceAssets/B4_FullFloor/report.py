from pathlib import Path
import json,hashlib,html
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'Unity/After_Seconds_Build_V0.01';O=R/'Docs/검수/2026-11-08_B4_FullFloor'
def read(p):return json.loads(p.read_text(encoding='utf8'))
plan=read(H/'layout.json');models=read(H/'models.json');audit=read(O/'audit.json');walk=read(O/'walk.json');preserve=read(O/'preservation.json');occ=read(O/'occlusion_result.json');plays=[read(f) for f in sorted(O.glob('play_*.json'))]
assert len(plays)==12 and all(p['complete'] and not p['errors'] and p['displacement']>.1 for p in plays)
assert not audit['issues'] and not walk['planningFailures'] and all(p['passed'] for p in walk['results'])
assert not preserve['missing'] and not preserve['unexpectedChanges'] and occ['bytes']>0
source={'author':'송예찬','date':'2026-11-08','task':'B4 남은 전체 구역 일괄 제작','scene':audit['scene'],'source':'로컬 Blender 모델 제작, Pillow 정적 화면·안내 텍스처 제작. 기존 B4/B5 장비와 공용 PBR 재사용. 외부 다운로드·유료 생성 없음.','newModels':[{'name':n,'asset':Path(m['asset']).relative_to(P).as_posix(),'triangles':m['triangles'],'source':f'SourceAssets/B4_FullFloor/{n}.blend','sha256':hashlib.sha256(Path(m['asset']).read_bytes()).hexdigest()} for n,m in models.items()],'reusedAssets':sorted({p['asset'] for p in plan['placements'] if '/BF_' not in p['asset']})+['Assets/Afrer_Seconds/05.Model/Environment/B4/BO_VaultPortal.fbx','Assets/Afrer_Seconds/05.Model/Environment/B4/BO_SealedTaskLight.fbx','Assets/Afrer_Seconds/05.Model/Environment/Common/CFD_TunnelRib.prefab'],'textures':['BF_Display_07..22: 정적 계측/진단/관제 화면16장','BF_Guide_CODE: 목적지16장; 복도에만 배치','기존 B4O 재질의 Base/Normal 공용 PBR 재사용'],'authoring':['architecture.py','props.py','textures.py','layout.py','refine_plan.py','refine_measurement.py'],'sceneAssembly':['Apply.cs','Refine.cs','MeasureRefine.cs','Occlusion.cs'],'report':'Docs/검수/2026-11-08_B4_FullFloor/검수결과.md','limits':['전체 B4 첫 외형 제작, 최종 아트는 사용자 검수 대기','모니터/측정 장비/문/화물 승강기 정적','B5↔B4↔B3 실제 연결과 게임 기믹·AI 미구현']}
(P/'Assets/Afrer_Seconds/06.Data/AssetSources/B4_FullFloor_20261108.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
roles={'C01':'기존 중앙 측정 영역·상부 관찰 데크 보존','C02':'기초 진단 센서의자·시료 준비·진단 구획','C03':'광학 센서 교정·측정기 정비·케이스 출납','C04':'신호/시료 분석 작업섬·냉장/멸균·데이터 랙','C05':'봉인 기록 랙3열·인계 해치·기록 서버','W01':'투척 지연 레인·충돌판·계측 제어/감독 구획','W02':'3단 광학 게이트·좌표 타깃·고속영상 수집','W03':'자극/응답 부스2곳·피험체 좌석·생체 기록','E01':'4분할 비교 판독벽을 바라보는 판독석2곳','E02':'연구 작업열3석·분리 구획·검토 회의석','E03':'검사/회복 침대2곳·가림·바이탈·의료가스/리넨','N01':'6분할 통합 관찰벽을 바라보는 제어석3곳·연락/데이터 설비','S01':'차폐 하중 시험 챔버·외부 제어·시험 후 분석','VA':'104단 17m 계단·중간참·난간·상부 문 앞 연결부','VB':'104단 17m 계단·중간참·난간·상부 문 앞 연결부','VL':'화물 캐빈·기계 레일·완충대·문턱/호출 표시'}
roomrows='\n'.join(f"| {r['id']} | {r['name']} | {roles[r['id']]} |" for r in plan['rooms'])
playrows='\n'.join(f"| {p['label']} | {p['displacement']:.3f}m | {p['framesAdvanced']} | {p['medianMs']:.2f} / {p['p95Ms']:.2f}ms | 0 |" for p in plays)
report=f'''# B4 전체 구역 검수 V0.01

작성자 송예찬 · 2026-11-08

사용자의 “전체 전부다 일단 만들어줘”에 따라 C01/T02 대표 구역에서 멈추지 않고 B4 남은12돔·3코어·21복도를 제작했다. **현재13돔·3이동 코어·22복도의 첫 외형 제작이 완료됐다.** 씬은 `Level_B4_Circular.unity`, 루트는 `B4_능력측정관찰층_V0.02`다. 전체 아트 최종 판정과 게임 기능 완료를 뜻하지 않는다.

## 공간과 장비

| 코드 | 도면 명칭 | 실제 배치와 용도 |
|---|---|---|
{roomrows}

Decision 도면의 위치·반지름·22개 연결 관계와 B4 바닥 Y=-66m를 따른다. 기존 C01/T02의 Transform93개를 유지하고 임시 닫힌 문4곳, 기존 T02 단일 안내2오브젝트만 비활성화했다. 새 목적지별 안내는 양방향44선과44개 바닥 표기로 모든 복도를 연결하며 돔·코어 내부에는 없다.

건축·운용설비·조명별 하위 그룹과 `B4_구역코드_한글용도_번호` 이름을 사용한다. 복도 등기구는 리브 사이에 있고 돔 천장등과 코어 작업등에는 실제 광원을 연결했다. 새 등기구243개, 기존18개를 포함한 총261 Light다. 회색/흑연색 재질과 중성 광원이며 최종 색감/밝기는 사용자 전체 검수 후 마감한다.

신규 모델 **{len(models)}종**, 방별 장비107배치와 VL 대기화물1배치. 그중13종은 B4 전용 측정/진단/연구 장비다. 장비 베벨·베젤/후면 통풍·키보드/버튼·케이블/단자·유리 구획을 제작하고 정적 화면16장과 목적지 텍스처16장을 적용했다. 기존 B4/B5 장비와 공용 Base/Normal 맵을 재사용했다. 과도한 원주 배치를 피하기 위해 관제/판독석은 대형 화면을 향하게, 연구동은 작업열/회의 구역으로, 분석동은 작업섬으로 배치했다. 측정실 앞쪽은 시험·운반 여유 공간이다.

## 검증

- CharacterController **104/104** 경로 통과: 22복도 양방향44, 방별 출입 연결56, VA/VB17m 계단 왕복4. 계단 상부 연결문 앞까지 이동 확인. 경로 계획 실패0.
- 기존93 Transform 위치/회전 보존. 재질 누락0, 광원 방향 문제0, 돔 내부 안내 정점0.
- Renderer {audit['renderers']}, Collider {audit['colliders']}, Light {audit['lights']}, 인스턴스 삼각형 {audit['triangles']:,}. 쉘/바닥54오브젝트와38개 관측 영역으로 B4 전용 가림 베이크 {occ['bytes']:,}bytes를 생성했고 플레이 카메라에서 사용한다.
- 기존 Assets/Packages/ProjectSettings {preserve['protectedFiles']:,}파일 중 B4 대상 씬1개만 변경, 나머지 **{preserve['unchanged']:,}파일 SHA-256 동일**. B5·다른 씬·게임 C#·Animator·기존 모델/재질 보존. 작업 전 B4 네이티브 백업과 원본 모델은 SourceAssets에 있다.

| 실제 키보드 Play | 이동 | 진행 프레임 | 중앙값 / P95 | 새 경고·오류 |
|---|---:|---:|---:|---:|
{playrows}

각8초 동안 기존 키보드 W 입력과 프레임 진행을 확인했다. VL 최초 검사는 대기화물이 C05 쪽 직진 진입을 막아 실패했으며, 화물을 캐빈 반대쪽 대기 공간으로 옮긴 뒤104경로와 VL 실제 이동을 재검증했다. 최초 결과는 previous_attempt_VL.json으로 보관했다. 최초1.5초를 제외한 Editor Play 프레임 시간이며 출시 빌드 성능 확정값이 아니다. 가림은 적용했고 LOD·최종 조명/그림자 예산은 후속 마감 대상이다. 임시 마우스/시점/포커스·백그라운드 실행 설정은 복원했다. 검사 C#은 SourceAssets에만 있고 게임 런타임에는 추가하지 않았다.

16공간의 입구/반대편 화면32장, 복도22장, 장비/상부 문 상세9장, 실제 Play12장을 [검수 화면](review.html)에 모았다. 화면은 현재 저장 씬과 실제 Game View에서 캡처했다.

## 다음 검수

1. B4 전체를 순회하며 방별 역할·프랍 밀도·실제 시야·밝기를 사용자 검수한다.
2. 지적된 구조/장비를 보수하고 전체 조명·색감·LOD/성능을 마감한다.
3. B5↔B4↔B3 실제 층 연결, 문/승강기 개폐, 실험/감시/AI, 모니터 동작은 후속 게임 기능이다. 상부 문은 현재 닫힌 정적 외형이다.

로컬 저장 상태이며 이번 변경의 커밋·push는 하지 않았다. 이전 C01/T02 전용 검수는 당시 이력이다. [이동](walk.json) · [구조](audit.json) · [보존](preservation.json) · [최종 씬 상태](final_state.json).

## Revision History

- V0.01 (2026-11-08): B4 전체 첫 외형과 장비 제작, 배치 보수, 이동·Play·가림·보존 검수. 송예찬.
'''
(O/'검수결과.md').write_text(report,encoding='utf8')
sections=[]
for title,pics in [('공간별 장비와 구조',[(r['id']+'_detail',roles[r['id']]) for r in plan['rooms'] if (O/(r['id']+'_detail.png')).exists()]),('전체 공간',[(r['id']+suffix,r['id']+' · '+r['name']+' · '+('진입' if suffix=='_room' else '반대편')) for r in plan['rooms'] for suffix in ['_room','_overview']]),('연결 복도',[(t['id'],t['id']+' · '+t['a']+' ↔ '+t['b']) for t in plan['tunnels']]),('실제 플레이',[(p.stem,p.stem) for p in sorted(O.glob('play_*.png'))])]:
 cards=''.join(f'<figure><a href="{n}.png"><img loading="lazy" src="{n}.png" alt="{html.escape(t)}"></a><figcaption>{html.escape(t)}</figcaption></figure>' for n,t in pics)
 sections.append(f'<h2>{title}</h2><article>{cards}</article>')
(O/'review.html').write_text('''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>B4 전체 구역 검수</title><style>body{margin:0;background:#10151b;color:#e0e7e8;font:16px/1.6 system-ui,sans-serif}main{max-width:1400px;margin:auto;padding:32px 24px}p{color:#b9c5cc}article{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:20px}figure{margin:0;background:#1b242c;border:1px solid #35414a;border-radius:8px;overflow:hidden}img{display:block;width:100%}figcaption{padding:12px 16px}a{color:#b8d8cc}@media(max-width:500px){article{grid-template-columns:1fr}}</style><main><h1>B4 · 능력 측정/관찰층 전체</h1><p>13돔 · 3이동 코어 · 22복도 / 첫 외형 제작 · 송예찬 · 2026-11-08<br>이동104/104 · Play12구역 새 경고/오류0 · 복도 전용 목적지 안내<br>사진을 누르면 원본이 열립니다. <a href="검수결과.md">검수 결과와 후속 범위</a></p>'''+''.join(sections)+'<p>전체 외형 사용자 검수 대기. 장비/모니터/문/승강기는 정적 아트이며 층간 전환과 게임 기능은 후속입니다.</p></main></html>',encoding='utf8')
note=f'''2026-11-08 B4 전체 일괄 제작: 사용자 요청에 따라 남은12돔·3코어·21복도를 제작해 **B4 전체13돔·3코어·22복도의 첫 외형을 완료**했다. C01/T02 기존 구조·93 Transform 보존, 임시 폐쇄4곳과 이전 안내2개만 비활성화했다. 신규 모델{len(models)}종·구역 장비107+화물1배치, 정적 화면16장, 목적지별 안내는 복도에만 배치했다. 관제/판독석·연구 작업열·분석 작업섬과17m 계단 상부 문 앞 연결부까지 보수했다. Controller104/104, 실제 키보드 Play12구역 새 게임 경고/오류0, B4 전용 가림 베이크 완료. 기존5,900파일 중 B4 씬만 변경, 나머지5,899파일 동일. **다음은 B4 사용자 전체 외형/밀도/밝기 검수 → 지적 사항 보수 → 전체 조명·성능 마감**. B5↔B4↔B3 실제 연결과 문/승강기·실험·AI 게임 기능은 별도다. 전체 아트 최종 판정 전이며 로컬 저장, 커밋·push 미실시. 작성자 송예찬.'''
for rel,old,new,prefix in [('AGENTS.md','V0.61','V0.62','Docs/'),('CLAUDE.md','V0.61','V0.62','Docs/'),('Docs/이어하기_2026-11-06.md','V0.45','V0.46',''),('Docs/회사_작업목록_2026-11-06.md','V0.43','V0.44',''),('Unity/README.md','V0.46','V0.47','../Docs/'),('Docs/AfterSeconds_메인기획서.md','V0.51','V0.52','')]:
 p=R/rel;s=p.read_text(encoding='utf8');title,body=s.split('\n',1);assert old in title,(rel,title)
 p.write_text(title.replace(old,new)+'\n\n'+note+f' [검수 화면]({prefix}검수/2026-11-08_B4_FullFloor/review.html) · [검수 결과]({prefix}검수/2026-11-08_B4_FullFloor/검수결과.md).\n\n이전 단계 기록:\n'+body.lstrip()+f'\n- {new} (2026-11-08): B4 전체 첫 외형·배치·이동/Play 검수와 사용자 일괄 검수 단계. 송예찬.\n',encoding='utf8')
(H/'README.md').write_text('''# B4 전체 제작 V0.01

작성자 송예찬 · 2026-11-08

Decision 원형 도면의 B4 전체를 구현했다. C01/T02 기존 외형은 보존하고 나머지12돔·3코어·21복도를 제작했다. 현재 씬은 `Level_B4_Circular.unity`, 원본은 BF_*.blend, 반입 모델은05.Model/{Environment,Props}/B4, 맵/재질은 각 Textures/Materials, 출처는06.Data/AssetSources/B4_FullFloor_20261108.json이다.

`prepare.py`와 `Survey.cs`는 작업 전 기준/백업 수집용으로 다시 실행하지 않는다. `architecture.py`→`props.py`→`textures.py`→`NewCatalog.cs`→`layout.py` 순서로 초기 모델/배치를 만들었다. `BF_ONLY=VerticalStairs` 환경변수로 새 계단만 선택 재생성할 수 있다.

씬 최초 반영은 `Apply.cs`, 후속은 `refine_plan.py`+`Refine.cs`, `refine_measurement.py`+`MeasureRefine.cs`, `CargoClearance.cs`다. 마지막은 VL 대기화물을 로컬(3.1,0,-1.3)으로 옮겨 C05 쪽 진입을 비운다. `layout.json`이 최종107장비 배치이며 `zones`는 초기 자동 배치 참고치다. 초기 레이아웃/전체 Apply를 재실행하면 보수한 배치를 잃으므로 대상만 수정한다. `Refine`의 복제는 중복 실행을 거부한다. 변경 기록은 refinements*.json에 있다.

`Review.cs`가104개 실제 Controller 경로와 구조/복도 안내를 검사한다. `Occlusion.Begin` 최초 설정 후 `Bake`를 실행하며 완료 전 씬을 다시 열지 않는다. `Play.cs`/`play_checks.py`는 실행 중인 Editor에서 실제 키보드 W를 넣어12구역을 확인하고 설정을 복원한다. 재검사는 `play_checks.py VL`처럼 대상만 지정하고 기존 결과는 previous_attempt_CODE.json에 보관한다. `preservation.py`는 작업 시작5,900파일과 비교하며 B4 씬만 변경을 허용한다.

`report.py` 문서 버전 갱신은 최초1회용이다. 검수 C#은 SourceAssets에만 보관하며 게임 런타임으로 반입하지 않는다. 화면/결과는 Docs/검수/2026-11-08_B4_FullFloor/review.html에 있다. 문/승강기·실험 장비·모니터는 정적이며 층간 전환/게임 기능은 별도 구현한다.

- V0.01 (2026-11-08): B4 전체 첫 제작과 배치 보수·검수 도구·재실행 주의점. 송예찬.
''',encoding='utf8')
print(json.dumps({'models':len(models),'props':len(plan['placements']),'plays':len(plays),'docsUpdated':6},ensure_ascii=False))
