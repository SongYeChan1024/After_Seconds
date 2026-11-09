import json,hashlib,html
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-09_B2_Cooling';A=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds'
before=json.loads((H/'protected_before.json').read_text());changed=[p for p,v in before.items() if not (R/p).exists() or hashlib.sha256((R/p).read_bytes()).hexdigest()!=v]
protection={'files':len(before),'changed':changed};(O/'preservation.json').write_text(json.dumps(protection,ensure_ascii=False,indent=2),encoding='utf8');print('preserved',len(before),'changed',changed)
audit=json.loads((O/'audit.json').read_text());walk=json.loads((O/'walk.json').read_text());play=json.loads((O/'play.json').read_text());look=json.loads((O/'look_test.json').read_text());access=json.loads((O/'access.json').read_text());models=json.loads((H/'models.json').read_text())
assert all(v['passed'] for v in walk) and all(v['reachable'] for v in access['targets'])
assert play['complete'] and not play['errors'] and all(v['distance']>.8 and v['frames']>30 for v in play['results'])
assert look['complete'] and look['yawChange']>0 and look['pitchChange']>0 and not look['errors']
assert not audit['meshIssues'] and audit['missingMeshes']==audit['missingMaterials']==audit['missingScripts']==0
text='''# B2 냉각·펌프 공동 검수 V0.01

작성: 송예찬 · 2026-11-09

B2 대표 구역 C02의 정적 외형과 통행을 제작했다. 새 씬은 `Assets/Afrer_Seconds/01.Scenes/Stage/Level_B2_Circular.unity`이며 현재 이 씬이 저장된 편집 모드로 열려 있다. **B2 전체 완성 상태는 아니다.** 나머지 11공동·3코어·21복도와 층간 실제 연결은 후속 제작이다. C02의 네 문은 도면 위치에 보존하고 닫힌 외형으로 마감했다.

## 제작 내용

- Decision V0.05의 중심 (19,-34,-1), 반지름 11m, 높이 3.6m U형 메자닌과 양쪽 20단 계단을 적용했다. 하부 펌프·탱크 위치는 일반 배치표보다 메자닌 전용 배치안을 우선했다.
- 실제 구멍이 있는 스틸 그레이팅, 기둥·I형 보·베이스 플레이트·앵커 볼트·접합판·난간·발끝막이·불투명 정비 발판을 만들었다. 보행 충돌은 그레이팅 위에 얇은 평면 충돌체를 따로 사용한다. 아래를 볼 수 있지만 이 충돌체를 무조건 시야 차단 대상으로 사용하는 미래 AI 레이캐스트는 별도 필터링이 필요하다.
- 기존 VARCO 펌프 2대·탱크 2대·HVAC 1대를 재사용했다. 탱크 가공 메시의 퇴화 면은 이번 씬용 파생 메시에서 제거했다. 원본 에셋은 보존했다. 이번에는 VARCO 신규 생성·과금 실행이 없다.
- 냉각 공정 배관과 둥근 엘보, 플랜지/가스켓/볼트, 밸브, 압력계, 바닥 지지대, 판형 열교환기, 인버터 제어반, 상부 밸브 스테이션 2대, 정비 작업대·바이스·공구·부품 트레이·정비 기록, 공구 카트, 벽 부착 소방 설비를 추가했다.
- 날카로운 제작 모서리에 베벨을 적용했다. 철색 표면에 불규칙한 마찰 흔적·먼지와 거칠기 변화를 넣고, 바닥 사용감·배수구·설비 경계선을 적용했다. 붉은 보조등과 중성 작업등, 정적 반사 2개를 사용한다.
- 분리 피벗이 있는 기존 CCTV 외형 1대를 벽 지지대에 설치했다. 게임 C#·Animator·문·키패드·밸브·CCTV 감지/회전 기능은 추가하지 않았다.

## 검증

| 항목 | 결과 |
|---|---|
| CharacterController | 중앙·계단 왕복·상부·정비 접근 12/12 |
| 공간 연결 | 상·하부 11,250격자 검사, 출입문 앞/설비 14/14 접근 |
| 실제 Play | 바닥·서/동 계단·상부 4곳, 각각 288~436프레임 진행, 이동 1.23~1.34m, 계단 약 0.94m 상승 |
| OnLook | 36프레임, 입력 22회, 좌우 6.60°·상하 3.30° 회전, 새 오류 0 |
| 에셋 | 누락 메시/재질/스크립트 0, 퇴화 면 0 |
| 거리 최적화 | 새 원거리 메시 14개, 신규 LOD 9그룹; 기존 포함 12그룹 |
| 조명·충돌 | Light 28개, Collider 27개, ReflectionProbe 2개 |

Play 검수 구간의 새 게임 오류는 0이다. 제작 중 일시적인 URP RenderGraph/Forward+ 렌더 상태 오류는 파이프라인 인스턴스를 재초기화해 복구했다. 렌더 설정과 Unity 버전은 바꾸지 않았다. 원거리 LOD 검사에서 발견한 퇴화 면 2개도 제거 후 재검증했다. 테스트 초기 OnLook 검사는 이동 검수의 임시 PlayerLook 비활성화 구간과 겹쳐 한 번 거절되었으며, 이동 검수 종료 후 정상 상태에서 다시 실시했다.

검수 도구는 실제 Mouse/Keyboard 장치를 비활성화하지 않는다. 최종 저장 상태에서 두 장치 활성화와 `runInBackground=false`를 확인했다. 성능 수치는 에디터의 해당 구역 검사 결과이며 빌드/전체 B2 성능 보증은 아니다.

## 이어서 할 일

1. 사용자가 C02 밝기·금속 질감·상하 시야와 양쪽 계단을 직접 확인한다.
2. VL 화물 코어와 T01 연결 통로를 도면에 맞춰 제작한다. 실제 문 너머 공간과 안내선은 연결 구역 제작과 함께 연장한다.
3. C01 원심분리 공동, C03 배전실, C04 제어실로 확장한다. 터널 외벽 교차와 출입부 폭을 모델 생성 전에 검사한다.
4. 나머지 기계층 지원 공동을 제작한 뒤 층 전체 안내·조명·가림/성능을 마감한다.

커밋·push는 하지 않았다. 기존 다른 층·플레이어 씬·게임 C#·Animator의 보존 비교는 [preservation.json](preservation.json)을 참조한다.

[실제 Play 화면](play_game_camera.png) · [전체 검수 화면](review.html) · [제작 원본](../../../SourceAssets/B2_Cooling/README.md)
'''
(O/'Review.md').write_text(text,encoding='utf8')
images=[('play_game_camera','실제 Play 카메라'),('01_entry','입구에서 본 냉각 공동'),('02_upper','그레이팅과 상하 시야'),('03_pumps','펌프·밸브·연결 배관'),('04_maintenance','정비 작업대'),('05_stair','계단과 지지 구조'),('06_control','열교환기·제어반')]
page='<!doctype html><html lang="ko"><meta charset="utf-8"><title>B2 냉각 공동 검수 V0.01</title><style>body{max-width:1440px;margin:40px auto;background:#12181e;color:#e4e9ed;font:18px system-ui}p{line-height:1.7}img{display:block;width:100%;border:1px solid #435360;border-radius:8px;margin-bottom:38px}h1{font-size:32px}a{color:#82bacd}</style><h1>B2 냉각·펌프 공동 V0.01</h1><p>송예찬 · 2026-11-09<br>3.6m 메자닌과 양쪽 계단, 철재·붉은 보조 조명. C02 대표 구역 제작이며 전체 B2 완성은 아닙니다.</p><p><a href="Review.md">검수 결과와 다음 작업</a></p>'
for n,t in images:page+=f'<h2>{html.escape(t)}</h2><a href="{n}.png"><img src="{n}.png" alt="{html.escape(t)}"></a>'
(O/'review.html').write_text(page+'</html>',encoding='utf8')
(H/'README.md').write_text('''# B2 냉각 공동 제작 원본 V0.01

작성: 송예찬 · 2026-11-09

최신 씬 `Level_B2_Circular.unity`의 C02 대표 구역 제작 기록이다. [검수/다음 작업](../../Docs/Review/2026-11-09_B2_Cooling/Review.md)을 먼저 읽는다. **Apply.Run은 최초 생성용이며 현재 씬에 재실행하지 않는다.** 기존 프리뷰는 보존했다. 전체 B2 미완성, 게임 C#/Animator 변경 없음.

- `source_design.json`, `workbook_B2.json`: Decision 도면과 엑셀 B2 행 조사 사본.
- `Plan.md`, `doors.json`, `final_layout.json`: 이번 범위·문 연결 각도·최종 실제 배치. 마지막 파일을 현재 배치 기준으로 사용한다.
- `build.py`, `props.py`, `refine_geometry.py`, `safety.py`, `.blend`: 치수/베벨을 가진 Blender 편집 원본. 최신 배관은 refine_geometry에 사용된 build.py와 common.py의 둥근 연결 처리 기준이다.
- `textures.py`, `adapt_tools.py`: 철재 표면과 실제 읽을 수 있는 정비/계기/안전 표기.
- `Apply.cs`, `Finish.cs`, `Repair.cs`: Assets 밖의 외부 Unity 제작/검수 도구. 런타임 컴포넌트가 아니다. 재질 저장은 이번 작업 에셋에 한정한다.
- `lod*`, `Lod*`: 원거리 메시 14개/9그룹. 재생성 시 `lods.py`의 퇴화 면 제거를 유지한다. adapt_tools는 초기 복사용이므로 수정된 도구 위에 다시 실행하지 않는다.
- `Review.cs`, `Access.cs`, `Play.cs`, `Look.cs`: 통행·접근·실제 입력 검사. Mouse/Keyboard DisableDevice 호출 금지. 임시 PlayerLook/focus 설정은 finally/종료 콜백에서 복구한다.
- `protected_before.json`, `final_state.json`: 사용자 코드/기존 씬 보존 및 최종 상태.

다음 범위는 사용자 C02 검수와 VL/T01 연결 제작이다. C02 문은 임시 닫힌 정적 외형이며 나머지 공간은 생성하지 않았다. 새 씬의 시작점은 중앙 남측이며 양쪽 계단을 통해 상부를 돌 수 있다.
''',encoding='utf8')
summary='2026-11-09 B2 C02 대표 공동 제작: 반지름11m·3.6m U형 스틸 그레이팅·양쪽20단 계단, 냉각 펌프/탱크·연결 배관/플랜지/밸브·열교환기/제어반·정비대/공구·벽 소방/CCTV 외형을 새 `Level_B2_Circular.unity`에 저장했다. 철색 표면·붉은 보조등·작업등·반사2개, 신규 LOD9그룹. Controller12/12·접근14/14·Play4곳·OnLook 좌우/상하 검증, 새 게임 오류0. **B2 전체 완성은 아니며 다음은 C02 사용자 검수 → VL/T01 연결 → C01/C03/C04 확장**. 문4곳은 닫힌 외형으로 보존, 게임 C#/Animator·원본 프리뷰·다른 층/Player 씬 보존. Mouse/Keyboard 활성화, 저장된 B2 편집 모드. 커밋·push 미실시. 작성자 송예찬.'
for rel,old,new,link in [('AGENTS.md','V0.74','V0.75','Docs/Review/2026-11-09_B2_Cooling/Review.md'),('CLAUDE.md','V0.74','V0.75','Docs/Review/2026-11-09_B2_Cooling/Review.md'),('Unity/README.md','V0.54','V0.55','../Docs/Review/2026-11-09_B2_Cooling/Review.md')]:
 p=R/rel;s=p.read_text(encoding='utf8');title,body=s.split('\n',1);p.write_text(title.replace(old,new)+'\n\n'+summary+' [검수 기록]('+link+').\n\n이전 단계 기록:\n'+body+'\n- '+new+' (2026-11-09): B2 C02 대표 공동 제작과 통행·Play·OnLook 검수. 송예찬.\n',encoding='utf8')
sources={'author':'송예찬','version':'V0.01','scene':'Level_B2_Circular','scope':'B2 C02 only','models':list(models),'varco':'Existing approved flow assets reused; no new generation','geometrySource':'SourceAssets/B2_Cooling','review':'Docs/Review/2026-11-09_B2_Cooling/Review.md','runtimeCodeAdded':False}
(A/'06.Data/AssetSources/B2_Cooling.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf8')
print('review/docs complete')
