# B5 1섹터 제작 원본 V0.04

2026-11-06 Unity 반영: 조감도의 B5 일반 공동12개·이동 코어3개·연결 복도19개 전체 평면 구조를 Level_B5_Circular 씬에 제작·저장했다. 문38세트, C01의 T01·T03·T11 출입 연결, 실험 계측 포드·관찰 콘솔·곡면 벽 패널을 반영했다. C01 생활 배치는 비활성 보관하고 W01·W02에 생활 가구 각4모듈을 배치했다. 복도4854표본 막힘·바닥 누락0, CharacterController 왕복38회 및 문38세트 검수 통과. Play 두 구간 실제 이동·프레임 진행·새 경고/오류0을 확인했다. 전체 기본 구조 반영과 아트 완성은 구분한다. 외곽 프랍24배치의 에셋, 층간 계단·승강로, C01 세부 마감이 남아 아트 완료는0/34다. 최신 기록은 Docs/검수/2026-11-06_B5_FullLayout/검수결과.md, 제작 원본은 SourceAssets/B5_FullLayout이다. 기존 자동 Apply·finalize 도구를 재실행해 이전 완료 상태를 복구하지 않는다.

아래는 이전 작업 기록이다. 최신 범위·완료 상태는 위 문단을 우선한다.

작성자 송예찬 · 2026-11-06

현재 씬의 C01 레벨·아트 마감 원본이다. [검수 결과](../../Docs/검수/2026-11-06_B5_Sector01/검수결과.md)를 먼저 읽는다. 새 Decision 조감도는 분위기 참고이며 포드 안 생활시설 배치는 사용자 확인대로 유지한다.

VARCO 3종과 Blender 20종의 편집 원본·생성/반입 기록을 보관한다. 모든 C#은 Assets 밖의 제작·검수 도구이며 게임 런타임 스크립트가 아니다. `start.py`·`InspectSector.Read`는 작업 전 스냅샷이므로 재실행하지 않는다. `ApplySector.Apply`는 현재 그룹을 재생성하므로 후속 사용자 편집을 확인하지 않고 다시 실행하지 않는다. 현재 최종 배치는 검수 폴더의 `final_state.json`과 Unity 씬을 우선한다.

원본 제작 순서는 prepare_varco.py → build_details.py/make_textures.py → Import → Apply → RefineSector → PolishSector → DeskSector → FinishSector → CollarSector였다. 이후 추가 보수와 명시 재반입을 수행했으므로 이 순서를 자동 재실행하는 것은 복구 절차가 아니다. `AuditSector`, `WalkSector`, `FinalCheck`는 저장된 Edit 씬에서 사용하며 `PlaySector`는 기존 입력·이동 코드를 실제 Play에서 검수하고 일시 설정을 복구한다.
