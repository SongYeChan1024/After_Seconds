# 실험동 조명 연결 보수 V0.01

작성자: 송예찬 · 2026-11-07

실제 작업등의 S1_Lamp/CFD_Lamp는 EmissionColor가 있어도 `_EMISSION`이 꺼져 있었다. 반대로 외곽 보조 Spot5개와 중앙 보조 Point1개에는 대응하는 등기구가 없었다.

`Apply.cs`는 실험동 벽 작업등4개의 확산판을 새 `CL_Lamp`에 연결한다. EmissionColor와 `_EMISSION`, `BakedEmissive` 플래그를 함께 설정해 재로드 후 발광이 유지된다. 이 플래그는 발광 검증을 위한 재질 상태이며 이번 작업에서 GI를 베이크하지 않았다. 광원은 확산판 아래47.5mm, 아래 방향에서 실내 쪽6.84도, Spot135도/Inner90도·Intensity6.5·Range11m다.

포드의 기존 Point는 아래 방향 Spot으로 바꾸고, 광원 위58mm에 `CL_PodCeilingLight` 확산판을 배치했다. 기존 Intensity12/Range12m를 유지한다. 떠 있던 보조광6개는 컴포넌트만 비활성화하고 Transform과 수치를 보존했다. 사용자 조정 Worklight_52도 삭제하지 않았다. T01/T11 실제 밀폐등15개의 발광 표면도 동일한 전용 재질로 연결했고, 공용 원본 재질은 직접 수정하지 않았다.

편집 원본은 `CL_PodCeilingLight.blend`, 모델은 `05.Model/Environment/B5/CL_PodCeilingLight.fbx`(1,632tri), 재질은 같은 폴더의 `Materials/CL_Lamp.mat`다. `Capture.cs`의 동일 시점 전후 사진, `Audit.cs`의 광원/확산판 정합, `PlayC01.cs`의 실제 입력 검수 자료를 확인한다. `Audit.Restore`는 이 작업의 Play 검수 직후에만 사용하며 사용자 미저장 편집 복구용으로 쓰지 않는다.

다음 작업에서 옛 전체 Apply를 실행하면 비활성 보조광과 꺼진 발광 상태가 돌아올 수 있다. 현재 씬과 최신 인수인계를 우선한다. 스위치·점멸·경보 연동은 미구현이며 이번 작업에서 게임 C#을 추가하지 않았다.

[검수](../../Docs/검수/2026-11-07_C01_Lighting/검수결과.md). 로컬 저장, 커밋/push 미실시.
