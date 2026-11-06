# 실험동 출입문 제작 V0.01

작성자: 송예찬 · 2026-11-07

C01은 사용자 호칭 **실험동**이다. 실험동 쪽 T01·T03·T11 문 3세트만 `CDR_ClinicalPortal`로 교체한다. 다른 쪽 문과 다른 구역의 공용 도어는 보존한다.

원래 터널은 폭4.2m·높이3.4m이고 직사각형 문 상단은3.08m였다. 새 문은 통행 폭2.4m·높이2.79m, 곡선 상부 최대3.65m, 터널 방향 마감 깊이1m다. 양면 외장과 실제 빈 포켓, 좌우 문짝, 좁은 유리 관찰창, 킥플레이트·금속 트림·키패드·점검 커버를 갖춘다. 문짝 이동량은 좌우 각각1.235m이며 `Left/Right_Open/Closed` 앵커를 둔다.

- `build_doors.py`: Blender 편집 원본과 FBX 생성. 모서리 베벨·UV·평활 노멀, 기능별 메시3개/28,364tri.
- `Apply.cs`: **저장된 현재 B5 씬**에만 적용한다. 예전 문은 각 문 아래 `Previous_Rectangular_Door_Inactive`에 비활성 보관한다. 전체 구역 제작기를 재실행하지 않는다.
- `Audit.cs`: 열린 통로, 임시 닫힘 상태 단면 차폐, 문짝42자세/문 간섭, 메시·재질·배치 보존을 확인하고 저장 씬을 다시 연다.
- `VerifyC01Routes.cs` / `WalkC01Routes.cs`: 복도 표본과 기존 CharacterController 왕복 이동. 기존 검수 파일을 덮어쓰지 않도록 이 작업 보고서 폴더에 기록한다.
- `Capture.cs`: 안/밖/상부와 임시 닫힘 사진. 종료 후 저장된 열린 상태로 복원한다.
- `PlayC01.cs`: 기존 Input System의 W 입력으로 실험동 T01 문을 통과한 뒤 입력/포커스 설정을 복구한다. `Inside` 진입점이 문 통과 검수다.
- `prepare.py` / `finish.py`: 수정 전 씬 백업·파일 해시와 전후 비교. 다음 작업부터 수정 가능성이 있는 재질도 원문 백업한다.

새 모델은 `05.Model/Environment/B5/CDR_ClinicalPortal.fbx`, 전용 재질3개는 같은 폴더의 `Materials/CDR_*`다. 기존 CP PBR 재질은 참조해서 재사용한다. 게임 C#·Animator·개폐/잠금 로직은 없다. 세 문은 **열린 상태**로 씬에 저장한다.

재질 전체 `SaveAssets`는 관련 없는 URP 자동 갱신까지 기록할 수 있으므로 적용기는 새 재질의 `SaveAssetIfDirty`만 사용한다. `RestoreMaterialSerialization.cs`는 이번 실행에서 확인한 자동 직렬화 변경의 정리용이며 일반 제작 순서에 포함하지 않는다.

[검수 결과](../../Docs/검수/2026-11-07_C01_Doors/검수결과.md)와 최신 이어하기를 함께 읽는다. 로컬 저장 상태이며 커밋·push하지 않았다.
