# B4 전체 제작 V0.02

2026-11-08 영문 이름 전환: 현재 씬은 SourceAssets/EnglishNaming/name_map.json 기준이다. 이전 일회성 생성·Apply 도구는 당시 이름을 담은 제작 이력으로, 현재 씬에 그대로 재실행하지 않는다. 최신 Review/Audit 도구는 영문 경로에 맞췄다. 새 제작은 처음부터 영어 이름을 사용한다.

작성자 송예찬 · 2026-11-08

Decision 원형 도면의 B4 전체를 구현했다. C01/T02 기존 외형은 보존하고 나머지12돔·3코어·21복도를 제작했다. 현재 씬은 `Level_B4_Circular.unity`, 원본은 BF_*.blend, 반입 모델은05.Model/{Environment,Props}/B4, 맵/재질은 각 Textures/Materials, 출처는06.Data/AssetSources/B4_FullFloor_20261108.json이다.

`prepare.py`와 `Survey.cs`는 작업 전 기준/백업 수집용으로 다시 실행하지 않는다. `architecture.py`→`props.py`→`textures.py`→`NewCatalog.cs`→`layout.py` 순서로 초기 모델/배치를 만들었다. `BF_ONLY=VerticalStairs` 환경변수로 새 계단만 선택 재생성할 수 있다.

씬 최초 반영은 `Apply.cs`, 후속은 `refine_plan.py`+`Refine.cs`, `refine_measurement.py`+`MeasureRefine.cs`, `CargoClearance.cs`다. 마지막은 VL 대기화물을 로컬(3.1,0,-1.3)으로 옮겨 C05 쪽 진입을 비운다. `layout.json`이 최종107장비 배치이며 `zones`는 초기 자동 배치 참고치다. 초기 레이아웃/전체 Apply를 재실행하면 보수한 배치를 잃으므로 대상만 수정한다. `Refine`의 복제는 중복 실행을 거부한다. 변경 기록은 refinements*.json에 있다.

`Review.cs`가104개 실제 Controller 경로와 구조/복도 안내를 검사한다. `Occlusion.Begin` 최초 설정 후 `Bake`를 실행하며 완료 전 씬을 다시 열지 않는다. `Play.cs`/`play_checks.py`는 실행 중인 Editor에서 실제 키보드 W를 넣어12구역을 확인하고 설정을 복원한다. 재검사는 `play_checks.py VL`처럼 대상만 지정하고 기존 결과는 previous_attempt_CODE.json에 보관한다. `preservation.py`는 작업 시작5,900파일과 비교하며 B4 씬만 변경을 허용한다.

`report.py` 문서 버전 갱신은 최초1회용이다. 검수 C#은 SourceAssets에만 보관하며 게임 런타임으로 반입하지 않는다. 화면/결과는 Docs/검수/2026-11-08_B4_FullFloor/review.html에 있다. 문/승강기·실험 장비·모니터는 정적이며 층간 전환/게임 기능은 별도 구현한다.

- V0.01 (2026-11-08): B4 전체 첫 제작과 배치 보수·검수 도구·재실행 주의점. 송예찬.

- V0.02 (2026-11-08): 영문 이름 전환과 최신 검수 도구/이전 생성기 구분. 송예찬.
