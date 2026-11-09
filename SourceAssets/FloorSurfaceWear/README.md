# B5·B4 바닥과 화물 승강기 표면 제작 V0.01

작성자 송예찬 · 2026-11-09

`textures.py`는 2048px PBR 15장을 절차적으로 제작한다. 일반 바닥에는 2m 간격의 옅은 이음선과 불규칙한 미세 표면 변화, 화물 승강기에는 운반 바퀴·하단 접촉·문턱 마모를 넣었다. 폐허나 녹슨 시설 표현은 아니다.

`Apply.cs`는 Unity 네이티브 API로 바닥 상향 면과 화물 설비 일부 면의 UV·재질 슬롯을 분리한 파생 메시를 생성한다. 벽과 공유하는 원래 재질을 수정하지 않는다. 실제 적용은 B5 20개, B4 39개 렌더러다. 대상 후보 중 천장·기초만 있는 셸은 적용하지 않았다. `applied.json`의 `changedTriangles > 0`을 실제 수량으로 사용한다.

- 새 텍스처: `05.Model/Environment/Common/Textures/FW_*`
- 파생 메시·재질: `05.Model/Environment/{B5,B4}/FW_*`, `Materials/FW_*`
- 원본 씬 사본·상태: `*_before.unity`, `*_state_before.json`
- 형상/UV 검수: `Verify.cs`, 최종 상태: `FinalState.cs`
- 전후 화면: `../../Docs/Review/2026-11-09_FloorSurfaceWear/review.html`

**현재 씬에 `Apply.Run`을 다시 실행하지 않는다.** 이전 단계 사본으로 복원하거나 다른 제작 도구를 일괄 재실행하지 않는다. 후속은 기존 FW 재질/텍스처의 제한적인 수정으로 진행한다. 런타임 게임 코드를 추가하지 않았다.

같은 작업 중 사용자 요청으로 기록대와 통행 충돌도 수정했다. 그 제작 원본과 검수는 `../B4_DeskAndCollision/`에 있다.
