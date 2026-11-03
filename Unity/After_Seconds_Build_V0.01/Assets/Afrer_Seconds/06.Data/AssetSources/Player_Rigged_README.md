# AS05 플레이어 리깅·애니메이션 후보 반입 V0.07

2026-10-29 · 작성자 송예찬

회색 플레이어 더미의 기존 리깅 모델과 동작 6종을 유지하면서, 손가락 본을 보존하고 하체 관절·스킨 인덱스를 보정한 별도 V0.3 후보를 반입했다. 신규 모델은 `Models/PlayerDummy_Rigged_V0.3.fbx`, 신규 동작 6종은 `Assets/Afrer_Seconds/07.Animator/Player/Clips/Rigged_V0.3`에 분리했다. FBX 변환·Unity Humanoid 반입·지정 시점 미리보기 검수 후 SampleScene의 플레이어 외형과 Animator에 V0.3을 연결했다. 이후 사용자가 입력과 애니메이션을 연결하는 코드를 작성했으며, 최신 V0.3 걷기는 시작·정지 동작을 제외한 프레임 `124–160`으로 반복 구간과 높이·이동 속도를 보정했다.

기존 모델의 현재 파일명은 사용자가 지정한 `Models/PlayerDummy_Rigged_V0.2.fbx`다. `AS05_PlayerDummy_Rigged.fbx`는 이전 반입 당시 이름이다. 아래의 기존 동작과 당시 Unity 검수 기록은 V0.3과 구분해 보존한다.

앞으로 `03.Art`에는 UI·컷씬 등에 쓰는 2D 이미지만 용도별 폴더로 보관한다. 기준 모델·리깅 모델은 `05.Model`에, 스크립트와 결합해 기능이 완성된 에셋은 `04.Prefabs`에 둔다. 아래에서 참조하는 기존 원본·재질은 이전 반입 위치에 남아 있으며, 이전 반입에서는 애니메이션용 FBX 6개만 새 분류로 이동했다.

애니메이션과 Animator 구성 리소스는 `07.Animator`에서 대상별로 관리한다. 플레이어용 애니메이션 FBX·클립은 `07.Animator/Player/Clips`, Controller·Override Controller는 `07.Animator/Player/Controllers`, Avatar Mask는 필요할 때 만드는 `07.Animator/Player/Masks`에 둔다.

## 최신 V0.3 걷기 연결·플레이 검수

사용자가 작성한 `PlayerPresenter`가 이동 입력 여부를 `PlayerAnimationSystem.isMove`에 전달하고, 이 함수가 Animator의 `IsMoving`을 갱신한다. WASD 입력과 Idle·Walk 전환이 연결되어 있으며, 더 이상 파라미터를 수동으로만 바꿔 보는 단계는 아니다. `isMove`는 실제 이동 거리보다 이동 입력 유무를 기준으로 한다.

| 항목 | 현재 설정 |
| --- | --- |
| 대상 | `07.Animator/Player/Clips/Rigged_V0.3/Player_Walk.fbx`의 `Player_Walk` |
| Unity import 프레임 | `124–160` · 30fps |
| 클립 실측 길이 | `1.20000029초` |
| 반복 | Loop Time·Loop Pose 모두 켬 |
| 높이 오프셋 | `heightOffset=0.227` · 구간을 자른 뒤 기존 `0.164`에서 다시 보정 |
| 실제 이동 속도 | `PlayerMotorSettings.MoveSpeed=1.5m/s` |
| Walk State 재생 속도 | `1.5배` · 한 보행 주기 약 `0.8초` |
| 씬 Animator | Apply Root Motion 끔 · 위치 이동은 Motor가 담당 |

원본 V0.3 FBX에는 약 7.5초의 전체 시퀀스가 그대로 남아 있다. 시작·정지 자세가 매번 반복되던 문제를 줄이기 위해 **Unity importer의 사용 구간만** 줄였으며 FBX·모델·스킨·원본 키는 다시 쓰지 않았다. Controller가 참조하는 걷기 클립의 GUID·fileID도 유지했다. 기존 V0.2 모델과 상위 `Clips/`의 약 7.5초 걷기, 과거 반입 JSON은 당시 기록으로 보존한다.

약 `3.30초`의 런타임 검수에서 약 `4.13회` 반복했고, CharacterController 접지는 `51/51` 샘플이었다. 수평 이동 속도는 약 `1.5m/s`, 모델 로컬 yaw는 `0°`였다. 발바닥 높이 잔차는 지면 기준 약 `−0.016~+0.045m`로 남아 있어 완전한 발 고정이나 미끄러짐 제거까지 완료한 상태는 아니다. Run 등 다른 상태의 전이 조건은 이번 걷기 보정에서 바꾸지 않았다. 손·발의 미세 변형과 독립 발가락 굽힘·손 쥐기 제약도 아래와 같이 유지한다.

## V0.3 외형·Animator 최초 연결 당시 기록

SampleScene의 `Player_Dummy_V0.1/VisualRoot` 아래에 `PlayerDummy_Rigged_V0.3` 인스턴스를 추가해 활성 외형으로 연결했다. 기존 `AS05_PlayerDummy_Rigged` 외형(V0.2)은 같은 자리에 비활성으로 보관했다. 기존 로컬 위치·회전·스케일을 복사하고 VisualRoot의 기존 크기를 유지했다. 새 Animator는 유효한 V0.3 Avatar와 기존 [Player_Animator](../../../07.Animator/Player/Controllers/Player_Animator.controller)를 사용하며 Apply Root Motion은 껐다.

Controller의 기존 상태 6개에서 Motion만 신규 V0.3 클립으로 교체했다. 상태·전이·파라미터·속도는 보존했다. 보호 대상 134개 중 변경은 승인한 SampleScene·Controller 2개뿐이며 예상 밖 변경은 0개다. 원본 `Player_Dummy_V0.1.prefab`과 FBX·메타는 변경하지 않았다. 입력·이동·CameraRoot 등 모델 자식 바깥의 기존 씬 컴포넌트도 유지했다. 이 연결은 원본 프리팹에 적용하지 않은 씬 override이며 씬 저장 후 dirty는 false다. 활성 Animator 1개·기본 상태 `Player_Idle`, Play false, 최종 Console 오류·경고 0·컴파일 실패 false를 확인했다. [씬 연결 검수 기록](../../../../../../../Docs/검수/2026-10-29_Player_FullRig/scene-connection.json)에 남겼다.

최초 연결 당시에는 Play 중 Animator의 `IsMoving`을 수동으로 켜고 꺼 Idle·Walk를 확인하는 단계였다. 이후 사용자 코드의 WASD 연동과 걷기 보정은 위 최신 상태를 따른다. Run → Walk의 `IsMoving=true`·`false` 동시 조건, Land 조건, Pickup 복귀 등 기존 전이 설정은 이후 학습·검수 때 확인한다.

## V0.3 하체·스킨 보정 후보

기존 AI 리그에는 본 53개와 손가락 본 30개가 있었지만 `UpLeg`가 `Hips`에 겹치고, `Leg`가 고관절·`Foot`가 무릎·`ToeBase`가 발목 위치에 배치되어 있었다. 손가락이 없는 마커 재리깅 결과는 하체 비교용으로만 남겼다. 이번 V0.3은 손가락이 있는 AI 리그를 별도로 편집한 결과다.

중앙의 더미 `UpLeg` 본 2개를 제거하고 그 가중치를 `Hips`에 합쳤다. 실제 다리의 `Leg`·`Foot`·`ToeBase`를 각각 `UpLeg`·`Leg`·`Foot`로 바꾸고 발 앞쪽에 `ToeBase` 2개를 추가했다. 다리 관절 위치를 바로잡으면서 총 53개 본과 손가락 본 30개를 유지했다. 같은 편집 리그에서 아래 동작 6종을 다시 적용했다.

VARCO 편집 저장본에서는 깊이 우선 탐색(DFS) 본 순서와 스킨 인덱스가 맞지 않는 정점 4,121개를 발견했다. 로컬에서 기존 스킨 인덱스를 새 본의 역할에 맞게 전체 재매핑해 복구했다. 새 rest·bind·메쉬·애니메이션 키·타이밍·텍스처는 보존했다. **웹의 새 raw 결과에는 이 스킨 오류가 남아 있으므로, 해당 웹 결과를 그대로 다시 내려받아 프로젝트의 보정 FBX를 대체하지 않는다.**

| 용도 | 프로젝트 위치 | VARCO 생성 출처 |
| --- | --- | --- |
| 기준 리깅 모델 | [Models/PlayerDummy_Rigged_V0.3.fbx](Models/PlayerDummy_Rigged_V0.3.fbx) | [편집 리그](https://3d.varco.ai/animate/eb6d7efc-2d6d-4cce-a8b7-ccd779cb4412) |
| 대기 1 | [Rigged_V0.3/Player_Idle.fbx](../../../07.Animator/Player/Clips/Rigged_V0.3/Player_Idle.fbx) | [대기 결과](https://3d.varco.ai/animate/2c78d9f5-841e-4903-be11-e784ef309845) |
| 좌발 전방걷기 | [Rigged_V0.3/Player_Walk.fbx](../../../07.Animator/Player/Clips/Rigged_V0.3/Player_Walk.fbx) | [걷기 결과](https://3d.varco.ai/animate/6f2946f9-5ffb-4d3f-9b2c-3f25f6786cd4) |
| 달리기 | [Rigged_V0.3/Player_Run.fbx](../../../07.Animator/Player/Clips/Rigged_V0.3/Player_Run.fbx) | [달리기 결과](https://3d.varco.ai/animate/afb12e28-70c6-47e2-ad14-edafb058eaa1) |
| 제자리 점프 | [Rigged_V0.3/Player_Jump.fbx](../../../07.Animator/Player/Clips/Rigged_V0.3/Player_Jump.fbx) | [점프 결과](https://3d.varco.ai/animate/2f631525-f5f3-43c6-ae7d-55d7c146ef40) |
| 가벼운 착지 1 | [Rigged_V0.3/Player_Land.fbx](../../../07.Animator/Player/Clips/Rigged_V0.3/Player_Land.fbx) | [착지 결과](https://3d.varco.ai/animate/1c2a2873-af9b-49a7-9550-729d901a32af) |
| 줍기 | [Rigged_V0.3/Player_Pickup.fbx](../../../07.Animator/Player/Clips/Rigged_V0.3/Player_Pickup.fbx) | [줍기 결과](https://3d.varco.ai/animate/013934a9-5ce6-4c31-a162-930a8743a1a7) |

### V0.3 검증 범위와 제한

아래 반입·지정 시점 검수와 JSON은 걷기를 전체 약 7.5초로 사용하던 당시 기록이다. 최신 걷기 import 구간·Loop Pose·높이·속도와 런타임 결과는 위 항목과 아래 최신 클립 표를 따른다.

- FBX 7개를 다시 읽는 roundtrip 검사를 통과했다. 파일마다 본 53개·손가락 본 30개·정점 5,285개·삼각형 8,000개·이미지 2개를 확인했고 노드 스케일은 1이다.
- 보정 USD와 FBX의 핵심 포즈 26개 비교에서 최대 위치 차이는 약 `8.52 × 10⁻⁶m`다. 초기 리그·걷기 비교와 20개 포즈 비교보다 넓은 최종 검수 범위의 결과다.
- 동작 6종의 선형 블렌드 스키닝(LBS) 계산값이 모두 유한하며, 가장자리 늘어남의 99백분위(P99 edge stretch)는 최대 1.82였다. 이는 수치 검수 범위이며 연속 재생·접지·루프·손 쥐기 품질의 완료 판정이 아니다.
- 기존·신규 점프는 키 143개, 프레임 약 `2–143.99998`, FBX 길이 약 `4.733333초`로 같다. 이번 스킨 복구를 위해 점프 타이밍을 재편집하지 않았다.
- 새 7개 파일 모두 `Avatar.isValid=true`, `Avatar.isHuman=true`이며 Human 매핑 52개(몸 22·손가락 30, 왼쪽 LittleDistal 포함)를 확인했다. 뼈 참조와 bindpose는 각각 53개이고 누락된 뼈는 0개다. global·file·node 스케일은 모두 1이며 기존 URP 재질을 참조한다. 신규 FBX의 Runtime Animator Controller는 비어 있다.
- 임시 PreviewScene에서 동작 6종을 9개 시점씩 총 54개 샘플로 확인했다. 수치 검사를 통과했고 PNG 16개를 저장했으며 렌더 경고는 0개였다. 정면·측면의 걷기·줍기와 대기·달리기·점프·착지 대표 이미지에서 큰 함몰·과도한 늘어남이 보이지 않는 범위를 확인했다. 미세 찝힘·지면 접촉·연속 루프·손 쥐기 품질은 추가 검수한다.
- 새 `ToeBase` 본의 가중치는 0이어서 발은 `Foot`의 영향을 받아 함께 움직이며, 독립적인 발가락 굽힘은 없다. 왼쪽 `LittleDistal` 본도 존재하지만 원본 가중치가 0이다. 손가락 Human 매핑 30개를 지정해도 독립 가중치가 생기거나 쥐기 품질이 완성되지는 않는다. 손가락 본 보존과 손 상호작용 구현은 별도 작업이다.
- 반입·미리보기 후 보호 대상 기존 파일 116개의 SHA-256이 모두 동일했다. 활성·로드된 씬이 바뀌지 않았고 씬 dirty와 Play 상태는 false다. 임시 PreviewScene은 종료했으며 새 FBX와 `.meta`도 검수 전후 동일했다. 기존 V0.2와 구 동작 6종은 유지하고 사용자 씬·프리팹·Animator Controller 연결을 자동 교체하지 않았다.
- 새 V0.3 검수 JSON 3개도 Unity `.meta`·GUID 생성을 확인했다. 브릿지 실패 로그는 임시 폴더에 보관했으며 이번 작업의 Console을 정리한 최종 상태는 오류 0·경고 0·`compilationFailed=false`다.

| V0.3 클립 | Unity 실측 길이(초) | Loop Time |
| --- | --- | --- |
| `Player_Idle` | 약 8.900001 | 켬 |
| `Player_Walk` | 약 1.20000029 · import 124–160 | 켬 · Loop Pose도 켬 |
| `Player_Run` | 약 1.56666672 | 켬 |
| `Player_Jump` | 약 4.73333359 | 끔 |
| `Player_Land` | 약 2.10000014 | 끔 |
| `Player_Pickup` | 약 6.933334 | 끔 |

Loop Time 설정은 반복 경계나 접지가 완성됐다는 판정이 아니다. 각 FBX를 펼쳐 사용하는 클립과 프로젝트의 보정 모델을 기준으로 연결·플레이 검수를 진행한다.

Unity 브릿지는 다운로드가 0바이트여서 중지하고 manifest·lock을 원래 바이트로 복원했다. 공식 Blender 브릿지 1.1.2 서버로 파일만 수신했으며 자동 배치는 하지 않았다. 수신기는 작업 후 종료했다. 집에서 열 프로젝트에는 브릿지 절대 경로 의존성이 없다.

## 이전에 반입한 파일 — V0.2와 기존 동작 6종

`Models/PlayerDummy_Rigged_V0.2.fbx`는 이전에 반입한 애니메이션 클립 없는 T포즈 리깅 모델이며 사용자 변경 이름을 유지한다. [07.Animator/Player/Clips](../../../07.Animator/Player/Clips)의 기존 각 FBX에는 같은 캐릭터의 모델·뼈대와 아래 클립 한 개가 들어 있다. Unity Project 창에서 FBX를 펼쳐 해당 이름의 AnimationClip을 확인할 수 있다. `__preview__Scene`은 Unity의 미리보기용 클립이다. 아래 표는 V0.3 하위 폴더 밖에 보존한 기존 파일의 당시 기록이다.

| 파일·클립 이름 | 바르코 원명 | 원본 프레임 범위 | Unity 실측 길이 |
| --- | --- | --- | --- |
| [Player_Idle.fbx](../../../07.Animator/Player/Clips/Player_Idle.fbx) → `Player_Idle` | 대기 1 | 2–269 | 약 8.900초 |
| [Player_Walk.fbx](../../../07.Animator/Player/Clips/Player_Walk.fbx) → `Player_Walk` | **좌발 전방걷기** | 2–227 | 약 7.500초 |
| [Player_Run.fbx](../../../07.Animator/Player/Clips/Player_Run.fbx) → `Player_Run` | 달리기 | 2–49 | 약 1.567초 |
| [Player_Jump.fbx](../../../07.Animator/Player/Clips/Player_Jump.fbx) → `Player_Jump` | 제자리 점프 | 2–144 | 약 4.733초 |
| [Player_Land.fbx](../../../07.Animator/Player/Clips/Player_Land.fbx) → `Player_Land` | 가벼운 착지 1 | 2–65 | 약 2.100초 |
| [Player_Pickup.fbx](../../../07.Animator/Player/Clips/Player_Pickup.fbx) → `Player_Pickup` | 줍기 | 2–210 | 약 6.933초 |

애니메이션 6종은 모두 30fps다. 걷기는 사용자가 탈출 상황에 어울리는 동작으로 선택한 `좌발 전방걷기`이며, 앞서 비교한 기본 `걷기`나 `앞으로 걷기`는 이번 반입에 포함하지 않았다. `줍기`는 몸을 숙여 바닥의 물건을 집는 후보이므로 높은 버튼을 누르는 동작과 구분한다.

## 이전 반입 당시 Unity에서 확인한 상태 — V0.3 검증과 구분

- 모델 1개와 동작 FBX 6개 모두 `Human / Create From This Model`이며, 각각 `Avatar.isValid=true`, `Avatar.isHuman=true`를 확인했다.
- 각 FBX의 Humanoid 매핑은 51개, SkinnedMeshRenderer는 1개이며 뼈 참조 53개와 bindpose 53개가 있다. 누락된 뼈 참조는 0개다. 손가락 뼈대도 포함된다.
- 동작 FBX마다 실제 사용 클립 1개가 있으며, 6개 클립 모두 `isHumanMotion=true`다. T포즈 모델의 실제 사용 클립은 0개다.
- 새 FBX의 `mat_2` 재질 슬롯은 [기존 AS05 URP/Lit 재질](../../../03.Art/Candidates/VARCO/AS05_PlayerDummy/Materials/AS05_PlayerDummy_00_URP_Lit.mat)로 remap했다. 기존 색상·노멀 텍스처와 URP/Lit 재질을 재사용한다.
- 새 FBX에 포함된 Animator의 Runtime Animator Controller는 비어 있다. Animator Controller, 상태 전환, 입력 이벤트와의 연결은 아직 구성하지 않았다.
- 최종 `FBX_SCALE_UNITS` 변환 후 6개 클립을 리깅 모델의 `AS05_PlayerDummy_RiggedAvatar`에 적용하고, 별도 임시 PreviewScene에서 각각 5개 시점을 샘플링했다. 메쉬·머리·손 위치와 URP/Lit 재질을 확인했고, 단위 표현으로 인해 위치가 수m로 튀던 문제를 해결했다. 검수용 PreviewScene은 닫고 정리했다.

위 결과는 리그 데이터와 지정한 시점의 리타게팅·단위 표현을 확인한 것이다. 연속 재생에서 자동 리깅의 어깨·팔꿈치·손가락·골반·무릎 변형, 발 미끄러짐과 1인칭 화면에서의 팔 위치는 추가 검수해야 한다. 기존 SampleScene·C#·asmdef·프리팹 본체 16개의 SHA는 검수 전과 동일하다. 이 비교에는 사용자가 직접 바꾼 기존 FBX의 importer 메타는 포함하지 않는다.

## 사용자가 이어서 확인할 위치

1. V0.3의 검수 범위와 제한을 먼저 읽는다. 신규 후보는 이 폴더의 `Models/PlayerDummy_Rigged_V0.3.fbx`와 `Assets/Afrer_Seconds/07.Animator/Player/Clips/Rigged_V0.3/Player_*.fbx`다. 기존 V0.2 모델과 상위 `Clips`의 동작 6종은 비교·보존용으로 구분한다.
2. SampleScene의 `Player_Dummy_V0.1/VisualRoot/PlayerDummy_Rigged_V0.3`에서 연결한 외형과 크기·높이를 확인한다. 외형의 위치와 부모의 Motor·Presenter·CharacterController·CameraRoot 설정을 구분해 확인한다. 위 최초 연결 검수의 프리팹 보존 수치는 당시 기록이다.
3. 새 외형의 Animator에서 기존 `Player_Animator`와 V0.3 Avatar, Apply Root Motion 끔을 확인한다. Controller 상태 6개에는 V0.3 Motion이 연결되어 있다. WASD를 눌렀다 놓으며 `PlayerPresenter → PlayerAnimationSystem.isMove → IsMoving`을 통한 Idle·Walk 전환과 반복을 확인한다.
4. 최신 걷기는 import 124–160, Loop Time·Loop Pose 켬, 높이 오프셋 0.227, Motor 1.5m/s·State 1.5배를 기준으로 확인한다. 그 뒤 Run 등 기존 전이 조건과 점프·착지 구간을 분석한다. 상위 `Clips/`의 기존 동작 6종을 Loop Time·Loop Pose 끔으로 반입한 과거 기록과 구분한다.
5. 이동을 담당하는 `PlayerMotor`와 애니메이션의 역할을 확인한다. 연결한 씬 인스턴스의 Apply Root Motion은 이미 껐다. 반입 FBX의 기본값과 씬 인스턴스 설정을 구분하고, 실제 이동·루프·접지는 플레이 검수로 확인한다.

이전 [AS05 플레이어 원본](../../../03.Art/Candidates/VARCO/AS05_PlayerDummy/Models/AS05_PlayerDummy.fbx)과 AS06 경비 원본은 계속 뼈대 없는 정적 모델이다. 기존 AS05 원본에 사용자가 지정한 Humanoid Rig 설정은 그대로 두었으며, Rig 설정만으로 이 원본에 뼈대가 생기지는 않는다. 이 폴더의 새 리깅 모델과 구분한다. 기능이 완성된 프리팹을 만드는 단계는 사용자가 연결을 마친 뒤 진행한다.

## 이전 반입의 원본 동작과 좌표 보존

USDZ별로 메쉬와 bind transform의 원점 오프셋이 조금씩 다르다. 변환 과정에서 이를 임의로 같은 원점에 재정렬하거나 발을 바닥에 맞추지 않았다. 원본 USD는 Y-up·1단위=1m이며, FBX의 축은 Forward -Z / Up Y다. `source_manifest.json`의 원점 차이 벡터는 **원본 USD Y-up 좌표**, Root·Hips 샘플은 **변환 중 측정한 Blender Z-up 좌표**이므로 두 좌표의 수직 축을 혼동하지 않는다.

Blender 5.1.2의 FBX 단위 변환은 `FBX_SCALE_UNITS`를 사용한다. 미터 단위를 FBX의 단위 정보인 100cm로 표현하고 노드 스케일은 1로 기록하여, 캐릭터의 실제 형상·크기·애니메이션 키를 보존한다. 이는 캐릭터를 100배 확대하거나 축소하는 설정이 아니다.

초기 `FBX_SCALE_NONE` 결과는 노드에 100배 스케일이 남아 Unity Humanoid 미리보기에서 몸체 위치가 크게 튀는 문제가 있었다. Rig 모델과 Walk로 단위 표현 차이를 비교한 뒤, 최종 반입한 7개 FBX 모두 `FBX_SCALE_UNITS`로 다시 변환하고 Humanoid Avatar를 재생성했다. 6개 동작을 새 리깅 모델에 적용한 시점별 미리보기에서 위치가 수m로 튀던 문제를 해결한 것을 확인했다. 이 수정은 FBX의 단위 표현을 정리한 것이며, 원본 동작의 원점 오프셋·수직 움직임·프레임 범위를 보정한 작업과 구분한다.

걷기 약 7.5초를 포함해 원본 프레임 범위와 Root·Hips의 수직 움직임을 보존했다. 걷기의 시작·끝 자세를 맞추거나 반복 가능한 한 주기로 자르는 보정은 하지 않았다. 바르코의 제자리 동작 선택은 수직 움직임까지 0으로 만든다는 뜻이 아니며, 반복 경계와 지면 높이, 다른 동작으로 전환할 때의 위치·자세는 연결 단계에서 확인한다.

## 출처·검수 기록

- [v03-skin-repair.json](v03-skin-repair.json): V0.3 관절 수정·스킨 인덱스 재매핑과 FBX 변환 검수.
- [v03-unity-import-facts.json](v03-unity-import-facts.json): V0.3 새 7개 파일의 Unity Humanoid·본·매핑·클립·재질 상태.
- [v03-motion-preview-validation.json](v03-motion-preview-validation.json): V0.3 동작 54개 시점의 임시 미리보기 및 씬·파일 보존 확인.
- [동작별 정면·측면 대표 이미지](../../../../../../../Docs/검수/2026-10-29_Player_FullRig/animation-keyposes-front-and-side.jpg), 걷기 스킨 보정 [정면 비교](../../../../../../../Docs/검수/2026-10-29_Player_FullRig/walk-skin-repair-front-comparison.jpg)·[측면 비교](../../../../../../../Docs/검수/2026-10-29_Player_FullRig/walk-skin-repair-side-comparison.jpg).
- [V0.3 웹 생성 출처](../../../../../../../Docs/검수/2026-10-29_Player_FullRig/varco-source-results.json)와 [기존 보호 파일 기준](../../../../../../../Docs/검수/2026-10-29_Player_FullRig/existing-project-baseline.json).
- [최종 파일 보존 확인](../../../../../../../Docs/검수/2026-10-29_Player_FullRig/existing-project-preservation.json): 기존 116개 파일과 신규 FBX·메타의 보존, 최종 Unity 상태 확인.
- [source_manifest.json](source_manifest.json): 바르코 클라우드 결과 URL, 원본 USDZ와 반입 FBX의 SHA-256, 변환 설정, 프레임·원점 차이 및 동작 샘플.
- [unity-import-facts.json](unity-import-facts.json): Unity 6000.4.0f1에서 조회한 Avatar·뼈·클립·Animator 상태. 경로는 Unity 프로젝트 상대 경로다.
- [motion-preview-validation.json](motion-preview-validation.json): 별도 PreviewScene에서 새 리깅 모델의 Avatar에 6개 클립을 임시 적용한 시점별 검수 기록. 클립당 5개 시점의 메쉬 경계·머리·손 위치와 재질·Controller 상태를 보관한다.
- 원본 생성 플로우: [After_Seconds](https://3d.varco.ai/flow/b7248081-b012-4913-87ba-4b056a7381ea). 리깅과 각 동작의 클라우드 결과 링크는 manifest에 있다.

이 파일들과 FBX는 후보 반입 기록이다. Animator 연결·모델 교체·게임 플레이 검수를 완료한 최종 캐릭터 에셋 상태로 간주하지 않는다.
