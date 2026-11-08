# B4 실험 운용 설비 제작 V0.02

2026-11-08 영문 이름 전환: 현재 씬은 SourceAssets/EnglishNaming/name_map.json 기준이다. 이전 일회성 생성·Apply 도구는 당시 이름을 담은 제작 이력으로, 현재 씬에 그대로 재실행하지 않는다. 최신 Review/Audit 도구는 영문 경로에 맞췄다. 새 제작은 처음부터 영어 이름을 사용한다.

작성자 송예찬 · 2026-11-08

B4의13돔·3코어에 실험체·경비·연구원 관점의 설비를 보강했다. 새 모델35종 중34종210개를 사용하고 작업의자27개, 실제 Light44개를 연결했다. BX_ScreenedEntry는 제작 에셋으로 보관하며 씬에 배치하지 않았다. 원본 BX_*.blend와 반입 Props/B4/BX_*.fbx, Textures/BX_Display_23..42.png와 대응 재질,06.Data/AssetSources/B4_ExperimentOperations_20261108.json을 사용한다. 기존 B4/B5 원본 모델·공용 Base/Normal 맵을 보존했다.

## 제작과 재실행

`prepare.py`, `Survey.cs`는 시작 기준/백업으로 다시 실행하지 않는다. baseline.json은 이번 작업 시작6,389파일, scene_before.json은 기존1,317 Transform, B4_before.unity는 네이티브 백업이다. equipment.py와 worklight.py는 Blender, textures.py는 Pillow를 사용한다. BX_ONLY=모델명 환경변수는 선택 모델만 재생성한다. 예: BX_ONLY=ProjectileCabinet,CleanReturnCabinet. 모델 파트의 베벨은 export에서 적용되며 LCD/라벨 UV를 별도 유지한다.

초기 반입 Catalog.cs → layout.py → Apply.cs 후, repair_layout.py+Repair.cs로 접근을 보수했다. **현재 layout.json이 최종 배치이며 초기 layout.py/Apply.cs를 다시 실행하지 않는다.** C05 중앙 비상설비 제외·카트 이동, W01 통제대/E02 소모품/E03 대기석 이동 내역은 access_repairs.json이다. BoothAccess.cs로8의자 간격을 조정하고 FunctionScreens.cs로4관측 부스의 주 화면을 방별 계측으로 구별했다. role_access.py는 검사용 부스 내부4점/계측2점을 추가한다. 초기배치와 최종배치의 차이를 유지한다.

## 검수

Review.cs Walk:320경로 Controller 검증; Capture:16공간32뷰+22복도; Roles:설비/관측석31뷰. Audit.cs는 기존 Transform·재질·복도 전용 안내·새 Light 방향을 검사한다. Play.cs는 기존 플레이어의 키보드 W를 사용하고 임시 시점/입력 설정을 복원한다. `play_checks.py C01 C02 C03 C04 C05 W01 W02 W03 E01 E02 E03 N01 S01 VA VB VL`로 이번16구역을 검사했다. 인수 없이 실행하면 기본12구역이므로 전체 검수에는 위 목록을 사용한다.

preservation.py는6,389개 시작 파일 중 B4 씬만 변경되었는지 검사한다. report.py는 모든 검사가 통과한 뒤 문서 버전을 한 번 갱신하므로 중복 실행하지 않는다. FinalState.cs는 복사 보관이 확인된 이번 Play 임시 캡처만 제거하고 B4 편집/저장·원래 플레이어·백그라운드 해제 상태를 확인한다. 검사 C#은 게임 Assets에 넣지 않는다.

작업 중 NavGrid.cs/nav_plot.py는 막힌 접근을 찾은 초기 진단이며 nav_grid.png는 최종 결과가 아니다. 최신 결과는 Docs/검수/2026-11-08_B4_ExperimentOperations/review.html, walk.json과final_state.json이다. 최종 정적 화면·설비 아트이며 실험/문/승강기/감시 동작·층간 전환은 후속이다. 커밋·push하지 않았다.

- V0.01 (2026-11-08): B4 실험 운용 설비·배치 보수·검수·재실행 주의점. 송예찬.

- V0.02 (2026-11-08): 영문 이름 전환과 최신 검수 도구/이전 생성기 구분. 송예찬.
