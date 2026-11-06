# B5 전체 평면 제작 원본 V0.02

2026-11-07: `AF_C01_ThreePortalRibs.blend`/FBX는 [C01 전용 보수 도구](../C01_Finish/README.md)의 연속 리브8개 버전이다. `build_layout.py`도 리브 생성만 새 원본으로 위임한다. 이 문서의 나머지 전체 Apply/Repair를 현재 씬에 재실행하지 않는다.

작성자 송예찬 · 2026-11-06

Decision 조감도의12공동·3코어·19복도를 기존 B5 씬에 반영한 원본이다. [검수 기록](../../Docs/검수/2026-11-06_B5_FullLayout/검수결과.md)을 따른다. 기본 평면 구현 완료와 세부 아트·층간 구조 완성을 구분한다.

- `build_layout.py`: 기존 CF/S1의 형상 제작 함수만 읽어 새 AF 모델5개를 생성한다. 기존 모델 원본은 덮어쓰지 않는다. AF 모델의 후속 수정을 확인한 뒤 실행한다.
- `ApplyFullLayout.cs`: 반입과 최초 씬 반영. Apply는 이미 반영한 그룹이 있으면 중단한다. 사용자의 후속 편집을 지우기 위해 이 방어를 제거하지 않는다.
- `RepairFullLayout.cs`: T11 주변 설비6개 위치 보정. 이후 사용자 배치가 있으면 자동 재실행하지 않는다.
- `VerifyFullLayout.cs`, `WalkFullLayout.cs`, `DetailAudit.cs`: 저장된 B5 편집 상태에서 구조·문·프랍·왕복 검수. Capture는 촬영용 절개를 일시 적용하고 저장 씬을 다시 연다.
- `PlayFullLayout.cs`: Play에서 현재 플레이어를 두 검수 위치로 일시 이동하여5초간 입력·프레임·오류를 검사한다. 백그라운드 실행과 자동 tick을 먼저 확인하고, 검사 뒤 Play를 종료해 저장 위치로 복구한다.
- `before.unity`, `protected_before.json`: 반영 전 기록. 자동 덮어쓰기·복구를 하지 않는다.
- 모든 C#은 Assets 밖의 Editor 제작/검수 도구다. 게임 런타임 코드는 추가하지 않았다.
