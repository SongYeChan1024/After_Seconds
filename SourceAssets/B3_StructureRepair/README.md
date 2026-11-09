# B3 구조와 밀도 보수 제작 원본 V0.03

OnLook 후속: 검수 후 마우스 장치 비활성 상태가 발견되어 활성화하고 실제 회전을 검증했다. Play.cs는 실제 마우스 장치를 끄지 않도록 보수했다. 기존 검사 결과의 기기 복구 문구만으로 입력 정상 여부를 판단하지 않는다. [진단](../Diagnostics/OnLook_20261109/README.md).

작성자 송예찬 · 2026-11-09

Unity B3 씬에 적용·저장하고 검수를 마쳤다. [검수 결과](../../Docs/Review/2026-11-09_B3_StructureRepair/Review.md)와 [실제 화면](../../Docs/Review/2026-11-09_B3_StructureRepair/review.html), [현재 Decision 도면](../../Docs/도면/Decision/원형공동/B3_구조보수/README.md)을 먼저 읽는다. 사용자 승인 후 Player 씬 작업을 저장하고 B3 검수를 진행했으며 Player 씬으로 복귀했다.

`layout_before.json`은150배치 원본, `layout_route.json`은 구조 보수안, `layout_after.json`은302배치와 실제 검수 경로를 반영한 현재 상태다. 기존14개를 재배치하고150개 바닥 설비와2개 작업대 소품을 추가했다. `density_delta.json`은 적용 차이이며 unplaced는 여유가 부족해 배치하지 않은 추가 후보다.

Blender 건축8개·상세 프랍7개·LOD12개를 반입했다.5개 표면 파생 메시에서 극소 퇴화 삼각형3개를 제거했다. 고밀도 모델114배치에 LOD를 더하고 기존 반사16개·가림 데이터를 갱신했다. 원본 모델과 기존 비활성 리브/안내는 보존했다.

`Apply.cs`는 이미 실행했다. 전체 Apply 또는 이전 B3 제작기를 현재 씬에 재실행하지 않는다. `State.cs`, `Quality.cs`, `Review.cs`는 저장된 B3 편집 씬에서만 실행한다. `Play.cs`는 외부 검수 도구이며 게임 스크립트가 아니다. before_play 이름은 이전 도구에서 상속한 이름으로 이 폴더의6파일은 모두 보수 후 검사다.

`sync_design.py`는 실제 검수 routes.json을 Decision 도면에 반영한다. `finalize.py`는 이번 마감 보고를 작성한 일회성 도구다. `protected_result.json`에서 B3와 사용자 Animator 파일의 비교 차이를 구분하며 나머지 보호74파일은 동일하다. Player·Enemy·UI/UX 기능별 씬은 Old 정리 대상에서 제외한다.

## 변경 기록

- V0.01: 구조·밀도 보수안과 Blender 모델 준비.
- V0.02: Unity 적용,394경로·10,730표본·Play6곳 검수,Decision 동기화와 Player 씬 복귀.

- V0.03: 마우스 입력 복구·외부 검수 도구 보수.
