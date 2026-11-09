# After Seconds 집에서 이어하기와 11월 9일 작업 마감 V0.01

작성자 송예찬 · 2026-11-09

오늘은 B5/B4 표면·설비·통행 보수, B3 시료층 구조와 밀도 개선, B2 기계층 전체 연결, 플레이어 크라우칭 구현과 애니메이션 연결까지 진행했다. 집에서는 **Player 씬에서 앉기 조작감을 먼저 확인한 뒤 B2 외형 검수**를 이어간다. B1을 바로 제작하거나 기존 제작 도구를 다시 실행하는 단계가 아니다.

## 집에서 시작하는 순서

1. 집 저장소에서 `git status`로 미보존 작업을 확인한다. 변경이 있으면 보존한 뒤 `git pull --ff-only`를 실행한다. 이 문서와 저장소의 최신 AGENTS.md를 읽는다.
2. `Unity/After_Seconds_Build_V0.01`을 **Unity 6000.4.0f1**로 연다. 다른 버전으로 자동 업그레이드하지 않는다. 새 에셋의 첫 반입이 끝날 때까지 기다린다.
3. `Assets/Afrer_Seconds/01.Scenes/Player.unity`를 연다. Player 전용 씬은 Old에서 이 위치로 복귀했으며 GUID를 유지했다. 기능별 Player·Enemy·UI/UX 씬을 구버전 레벨과 함께 Old로 보내지 않는다.
4. C로 앉기/일어서기, WASD 이동, 전진+Shift, 앉은 상태의 전진+Shift를 확인한다. 좌우·후진은 Shift를 눌러도 달리지 않는 것이 현재 규칙이다. 전방 대각선은 달리기를 허용한다.
5. 낮은 장애물 아래에서 일어서기 거부와 빠른 C 연속 입력, 시점 높이·발 미끄러짐·1인칭 몸 노출을 확인한다. 조작감이나 클립 자세가 어색한 지점을 기록한다.
6. `Stage/Level_B2_Circular.unity`에서 T01의 배관형 통로, C02 메자닌, C01/W02/N01의 밀도·밝기·설비 접근을 검수한다. 지적된 구역부터 보수한다.

## 현재 파일과 연결

Unity 에셋 경로의 `Afrer_Seconds` 철자는 기존 프로젝트 이름이다.

| 대상 | 현재 기준 |
| --- | --- |
| 플레이어 전용 씬 | `Assets/Afrer_Seconds/01.Scenes/Player.unity` |
| 현재 레벨 | `Assets/Afrer_Seconds/01.Scenes/Stage/Level_B2_Circular.unity` |
| 플레이어 프리팹 | `Assets/Afrer_Seconds/05.Model/Player/Player_Dummy_V0.1.prefab` |
| 활성 모델/Avatar | `05.Model/Player/PlayerDummy_Rigged_V0.3.fbx` |
| 실제 연결된 Controller | `07.Animator/Player/Controllers/Player_Animator_Blend.controller` |
| 이전 Controller | `Player_Animator.controller` — 보존본. 새 활성 연결로 착각하지 않는다 |
| 앉기 클립 | `07.Animator/Player/Clips/Crouch/` |
| 출처와 연결 기록 | `06.Data/AssetSources/Player_Crouch_VARCO.json` |

`Player_Animator_Blend`는 이제 검토용 초안이 아니라 실제 프리팹에 연결된 구성이다. Player 씬과 현재 B2의 상속 참조를 확인했다. Root Motion은 꺼져 있고 이동은 CharacterController가 담당한다.

## 플레이어 구현 맥락

사용자가 구현한 C 토글, 캡슐 높이/중심 변경, 천장 검사, 앉기 속도 선택을 유지했다. 이후 사용자의 명시적 요청으로 애니메이션 전달과 시점 보간을 연결했다. 앞으로도 요청 없이 다른 게임 로직을 대신 작성하지 않는다.

```text
PlayerInput 이벤트 → PlayerPresenter
  → PlayerMotor: 앉기/일어서기 판정과 실제 이동
  → PlayerLook: 확정된 높이 차이를 눈 높이에 보간
  → PlayerAnimationSystem.SetLocomotion: 같은 자세·방향·달리기 결과 전달

Standing Blend Tree:   Idle(0) → Walk(1) → Run(2)
Crouching Blend Tree:  Idle(0) → 방향별 Walk(1) → Sprint(2)
```

- `IsCrouch`는 버튼 요청이 아니라 `PlayerMotor.IsCrouching`의 확정 상태다. 천장 때문에 일어서지 못하면 애니메이션도 앉아 있는다.
- `Speed`는 m/s가 아닌 정규화된 애니메이션 값이다. 1.5이면 걷기/달리기를 절반씩 섞는다. 앉은 Walk 안에는 `MoveX`, `MoveY`를 사용하는 방향별 2D 트리가 있다.
- 자세 전환 0.28초, Speed 감쇠 0.12초, 방향 감쇠 0.1초, 눈 높이 SmoothDamp 기준 0.12초. 시점과 애니메이션의 조작감 조정값이며 게임 규칙은 아니다.
- 빠른 토글은 전환 목적지에서 역방향 전환을 허용한다. 소스 전환을 매번 다시 검사해 같은 전환이 끝없이 재시작되던 설정을 수정했다.
- 현재 이동 설정: 서서 걷기 5m/s·달리기 7.5m/s, 앉아서 걷기 3m/s·달리기 4.5m/s, 서 있는 캡슐 1.8m·앉은 캡슐 1.2m. 모델/씬의 중심과 눈 위치는 시작 시 읽는다.
- VARCO에서 가져온 앉기 클립을 V0.3에 리타깃하고 접지를 보정했다. 앉기 대기는 한쪽 무릎을 낮춘 자세다. Sprint는 무기를 든 원본의 팔·손 곡선을 비무장 걷기 곡선으로 조정한 파생본이다.

변경을 살펴볼 코드: `PlayerAnimationSystem.cs`의 SetLocomotion/ResetLocomotion, `PlayerPresenter.cs`의 Update/OnDisable, `PlayerLook.cs`의 SetEyeDrop. 사용자가 작성한 PlayerMotor·Settings·입력 연결도 이번 마감에 함께 보존한다.

## 오늘 레벨 작업

| 범위 | 완료한 내용 | 근거 |
| --- | --- | --- |
| B5/B4 표면·통행 | 바닥/벽 먼지·마찰과 화물 승강기 사용감, 소방 벽 부착, 작업등/설비 충돌 보수 | [표면·충돌](Review/2026-11-09_FloorSurfaceWear/Review.md), [마감](Review/2026-11-09_B4_Finish/Review.md) |
| B4 연구 시설 | 전용 설비16종으로50배치 교체, 계측/시험/준비/기록 구분, 전극·문서·키보드·오른손 마우스·곡선 배선 상세화 | [B4 검수](Review/2026-11-09_B4_LabIdentity/Review.md) |
| B3 시료층 | 13공동·3코어·22복도, T08 곡선 우회로 중첩 해소, 프랍150→302배치 | [B3 검수](Review/2026-11-09_B3_StructureRepair/Review.md) |
| B2 기계층 | 12공동·3코어·21통로 연결, 배관형 원형 통로, C02 그레이팅 메자닌, 신규 설비144배치 | [B2 검수](Review/2026-11-09_B2_FullFloor/Review.md) |

B3의 기본 소등5구역은 의도된 상태이며 스위치 동작은 아직 없다. B2는 철색·붉은 보조등과 설비층 분위기를 사용한다. 안내선은 복도에만 두며 플레이어 예상 경로를 월드 디버그 선으로 추가하지 않는다.

## 확인된 범위

- 크라우칭: Play 모드에서 임시 가상 키보드/마우스를 별도 프리팹에 페어링해 실제 InputAction 콜백 경로28개, 794프레임, 새 게임 오류0. 천장 거부·방향별 이동·전진 달리기·연속 토글과 중간 블렌드를 확인했다. [결과](../SourceAssets/PlayerCrouch/integration_play.json)
- 새 Controller의 Playable 미리보기14개 통과. 자세 중간과 최종 앉기/달리기 렌더도 확인했다. [이미지](../SourceAssets/PlayerCrouch/Preview/Blend_Crouched.png)
- B3 Controller394/394, B2 통로21/21·장비 접근186/186·계단왕복4/4 통과. 상세 조건과 수치는 각 단계 검수 기록을 따른다.
- OnLook 문제는 실제 Mouse 장치 비활성화 상태를 복구했다. 검수 도구가 실제 Mouse/Keyboard를 비활성화하지 않도록 수정했다. 마감 검수에서 두 장치 모두 활성, 임시 입력 장치 제거, B2 편집 모드와 씬 저장 상태를 확인했다.
- Unity AI의 `NoSubscription`은 AI 서비스 구독 관련 로그다. 이동/크라우칭 오류와 구분한다. 그림자 아틀라스 해상도 경고가 보이면 후속 조명 성능 검수에서 별도 확인한다.

## 다음 할 일

1. **Player 조작감:** C 전환 속도, 카메라 낮아지는 정도, 웅크린 자세와 전진 달리기의 자연스러움을 직접 검수한다. 현재 클립의 자세가 목적에 맞는지 확인한 뒤 필요한 클립만 교체한다.
2. **실험체 모델:** VARCO 지정 V0.03 플로우에 올린 두 이미지는 서로 다른 인물의 정면 콘셉트다. 같은 인물의 앞/뒤 뷰로 합치지 않는다. 사용할 인물 선정 → 3D 생성 → 리메시/손·얼굴·소매/천 재질 → 리깅 → Avatar 재연결과 접지 재검수 순서다. 현재 3D 생성은 하지 않았다.
3. **B2 사용자 검수:** T01 배관 통로 인상과 붉은 조명, C02 위/아래 시야, 각 공동 밀도·설비 디테일을 확인하고 지적 구역을 보수한다. B3 T08과 B4 E03/E02 근접 외형도 남은 사용자 검수 대상이다.
4. **이후 범위:** 위 검수 후 B1 설계를 확인한다. 실제 층간 로딩, 문/승강기/스위치, 경비·CCTV·연구원 AI, 미니맵/UI는 별도 구현이다. Jump/Land/Pickup 클립이 Controller에 있어도 입력과 게임 동작이 완성된 것으로 보지 않는다.

`SourceAssets/PlayerCrouch`와 각 층의 Apply/Import 도구는 제작 이력이다. 현재 에셋에 일괄 재실행하면 트림/연결/배치를 되돌릴 수 있다. 먼저 해당 도구와 검수 기록을 읽고 필요한 부분만 수정한다.

## 공개 기록

- [11월9일 데일리로그](https://songyechan1024.github.io/Kasil_DevLog/posts/daily-log-space-detail-and-crouch-state/)
- [11월9일 After Seconds 일일개발일지](https://songyechan1024.github.io/Kasil_DevLog/posts/after-seconds-b2-b3-and-crouch-blending/)

위 두 글의 원본은 블로그 저장소 `_posts/`에 있으며, 수업메모 `261109_NCAI`와 별도 글이다.
