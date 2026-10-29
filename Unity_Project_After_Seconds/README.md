# After Seconds Unity 프로젝트 안내 V0.09

2026-10-29 · 작성자 송예찬 · 실제 저장된 폴더 구조 기준

## 프로젝트 열기

- Unity Hub에서 열 폴더: `After_Seconds_Build_V0.01` — `Assets`, `Packages`, `ProjectSettings`가 있는 폴더.
- Unity: **6000.4.0f1**
- URP: **17.4.0**
- Input System: **1.19.0**
- Cinemachine: **2.10.7**, Pipeline: **0.9.1-exp.1**
- 실제 작업 루트: `Assets/Afrer_Seconds/`. 현재 폴더명을 그대로 사용한다.

집에서는 최신 `main`을 먼저 받은 뒤 연다. CLI 설치·로그인·조회 명령은 [집 CLI 안내](../README.md#집에서-unity-cli로-이어하기)를 따른다. VARCO 브릿지는 선택 설치로 분리했으므로 학원 PC의 Downloads 경로 없이 패키지를 복원할 수 있다. 기존 FBX와 현재 SampleScene에는 브릿지가 필요하지 않다.

## 현재 폴더 구조

아래는 `After_Seconds_Build_V0.01` 안의 게임 작업 폴더다. `.meta`는 생략했다. V0.3은 별도 보정 후보이며 Unity Humanoid 반입과 임시 미리보기 검수를 완료했다.

```text
Assets/Afrer_Seconds/
  01.Scenes/
    SampleScene.unity
  02.Scripts/
    A.Define/DefineAD.asmdef
    B.Simulator/SimulatorAD.asmdef
    C.System/
      SystemAD.asmdef
      Player/
        InputSystem_Actions.inputactions
        PlayerInputSystem.cs          # 보관용, 현재 입력 흐름에 사용하지 않음
        PlayerMotor.cs
        PlayerMotorSettings.cs
        PlayerLook.cs
        PlayerLookSettings.cs
        PlayerAnimationSystem.cs
    D.Ui/UI_AD.asmdef
    E.Manager/ManagerAD.asmdef
    F.Presenter/
      PresenterAD.asmdef
      Player/PlayerPresenter.cs
  03.Art/
    Candidates/VARCO/
      AS01_Crate/{Models,Textures,Materials}/
      AS05_PlayerDummy/{Models,Textures,Materials}/
      AS06_GuardDummy/{Models,Textures,Materials}/
      README.md
      source_manifest.json
      varco-import-facts.json
  04.Prefabs/                         # 현재 비어 있음
  05.Model/
    Player/
      Player_Dummy_V0.1.prefab
      Rigged/
        Models/
          PlayerDummy_Rigged_V0.2.fbx  # 사용자 변경 이름, 기존 모델 유지
          PlayerDummy_Rigged_V0.3.fbx  # 별도 하체·스킨 보정 후보
        README.md
        source_manifest.json
        unity-import-facts.json
        motion-preview-validation.json
        v03-skin-repair.json
        v03-unity-import-facts.json
        v03-motion-preview-validation.json
    Enemy/Enemy_Guard_V0.1.prefab
    Props/Props_Crate_V0.1.prefab
    Environment/                     # 현재 비어 있음
  06.Data/
    PlayerMotorSettings.asset
    PlayerLookSettings.asset
  07.Animator/
    Player/
      Clips/
        Player_Idle.fbx
        Player_Walk.fbx
        Player_Run.fbx
        Player_Jump.fbx
        Player_Land.fbx
        Player_Pickup.fbx
        Rigged_V0.3/                  # 별도 보정 리그에서 재생성한 동작
          Player_Idle.fbx
          Player_Walk.fbx
          Player_Run.fbx
          Player_Jump.fbx
          Player_Land.fbx
          Player_Pickup.fbx
      Controllers/
        Player_Animator.controller   # 기존 상태 구성 유지, V0.3 Motion 6개 연결
```

## 폴더별 사용 기준

| 폴더 | 보관할 내용 | 현재 상태 |
| --- | --- | --- |
| `01.Scenes` | 사용자가 구성하는 씬과 레벨 | SampleScene에서 사용자 배치와 플레이어 이동·시야 회전을 확인함 |
| `02.Scripts` | 책임에 따라 분리한 게임 코드와 AD | 6개 AD와 입력·이동·시야·Presenter 코드 |
| `03.Art` | **2D 이미지 전용. UI·컷씬 등 종류별 하위 폴더로 분류** | 과거 반입한 VARCO 모델·텍스처·재질·검수 기록이 아직 남아 있음 |
| `04.Prefabs` | **스크립트와 결합해 기능이 완성된 게임 에셋** | 완성 에셋은 아직 없음 |
| `05.Model` | **기준 리깅 모델·부속 재질과 조립 중인 외형 에셋** | Player·Enemy·Props·Environment로 분류하며 플레이어 기준 모델과 반입 기록은 Player/Rigged에 보관함 |
| `06.Data` | ScriptableObject 설정 에셋 | 이동·시야 설정 |
| `07.Animator` | **동작 FBX·클립 및 AnimatorController·AnimatorOverrideController·AvatarMask** | Player/Clips에 기존 동작 6종을 유지하며 Rigged_V0.3에 신규 6종을 분리함. Controller는 Player/Controllers에서 관리함 |

앞으로 `03.Art`에는 2D 이미지만 추가한다. UI 이미지는 `03.Art/UI/`, 컷씬 이미지는 `03.Art/Cutscenes/`처럼 이미지 종류별 하위 폴더로 분류한다. 필요한 종류의 폴더는 해당 이미지를 반입할 때 만든다.

앞으로 가져오는 기준 리깅 모델과 부속 재질·외형 에셋은 `05.Model`의 용도에 맞는 분류에 정리한다. 플레이어에 사용할 모델은 `05.Model/Player`에, 환경·경비·소품은 해당 분류에 둔다. 모델을 묶은 `.prefab` 형식의 파일도 이 단계에서는 `05.Model`에서 관리한다. 동작 스크립트와 필요한 설정을 연결하고 기능을 확인한 뒤, 완성된 게임 에셋을 `04.Prefabs`에서 관리한다.

동작 FBX·애니메이션 클립과 Animator 구성 리소스는 `07.Animator`에서 관리한다. 플레이어용은 `07.Animator/Player/`, 경비용은 `07.Animator/Enemy/`처럼 대상별로 나누고, 그 아래 `Clips/`에 동작 FBX·클립을, `Controllers/`에 AnimatorController(`.controller`)·AnimatorOverrideController(`.overrideController`)를 둔다. AvatarMask(`.mask`)를 사용할 때는 해당 대상의 `Masks/` 폴더를 만든다. 현재 플레이어 동작 FBX 6종은 `07.Animator/Player/Clips/`에 정리했다.

현재 `03.Art/Candidates/VARCO/`에 남아 있는 모델·텍스처·재질·검수 기록은 과거 반입 결과이며, 위의 신규 파일 분류 기준과 구분한다. 기존 `05.Model`의 모델 프리팹과 리깅 모델이 이 위치의 재질·텍스처 등을 참조하므로 이번에는 과거 파일을 일괄 이동하지 않는다. 사용자가 이름을 바꾼 기존 `PlayerDummy_Rigged_V0.2.fbx`와 반입 기록은 `05.Model/Player/Rigged`에 유지한다. `AS05_PlayerDummy_Rigged.fbx`는 당시 반입명이며 현재 파일명과 구분한다. 추후 기존 파일을 정리할 때는 Unity 안에서 파일과 `.meta`를 함께 이동해 참조를 유지한다. Plane 생성과 모델·레벨 배치는 사용자가 직접 진행한다.

## 코드 계층의 역할과 설정

| 폴더와 AD | 담당할 역할 | 현재 저장된 설정 |
| --- | --- | --- |
| `A.Define` · `DefineAD` | 식별자·값·상태·데이터 계약 | 내부 참조 없음, No Engine References 활성화 |
| `B.Simulator` · `SimulatorAD` | 시간·예약·교환 등 순수 규칙 | DefineAD 참조, No Engine References 활성화 |
| `C.System` · `SystemAD` | Unity 입력·물리·Transform·설정 데이터 연결 | Unity.InputSystem 참조 |
| `D.Ui` · `UI_AD` | 화면 표시와 UI 입력 | AD 이름만 설정 |
| `E.Manager` · `ManagerAD` | 세션 생성·종료·재시작과 기능 조립 | AD 이름만 설정 |
| `F.Presenter` · `PresenterAD` | 시스템·규칙·화면 표시 연결 | SystemAD·Unity.InputSystem 참조 |

다른 계층의 타입이 필요할 때 허용 참조표에 맞춰 AD 참조를 추가한다. 자세한 설계 제안은 [계층 분석·학습 순서](../Docs/Unity_계층_설계와_학습_순서.md)를 참고한다.

## 반입한 모델

| 모델 | 현재 위치 | 상태 |
| --- | --- | --- |
| 회색 플레이어 더미 | [05.Model/Player/Player_Dummy_V0.1.prefab](After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Player/Player_Dummy_V0.1.prefab) | V0.3 외형·Animator를 기준 프리팹에도 적용, WASD와 Idle·Walk 연결 |
| 주황 경비 더미 | [05.Model/Enemy/Enemy_Guard_V0.1.prefab](After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Enemy/Enemy_Guard_V0.1.prefab) | 정적 T포즈, 높이 💡 1.8m |
| 시료 궤짝 | [05.Model/Props/Props_Crate_V0.1.prefab](After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/Props_Crate_V0.1.prefab) | 높이 💡 1m |

위 높이와 충돌체 치수는 테스트용 가안이다. 경비 더미는 정적 T포즈이며 플레이어는 V0.3 외형·Animator와 WASD에 따른 Idle·Walk를 연결했다. 이동·시야 회전은 현재 SampleScene에서 확인했으며, 사격·경비 행동·교환 규칙은 아직이다. 세 후보 모두 8,000 triangles이며 색상·노멀 텍스처를 URP 재질에 연결했다. 자세한 상태와 출처는 [VARCO 에셋 반입 안내](After_Seconds_Build_V0.01/Assets/Afrer_Seconds/03.Art/Candidates/VARCO/README.md)를 참고한다.

2026-10-29의 기존 반입 모델은 현재 `05.Model/Player/Rigged/Models/PlayerDummy_Rigged_V0.2.fbx`, 기존 동작 FBX 6종은 `07.Animator/Player/Clips/`에 있다. 걷기는 사용자가 선택한 **좌발 전방걷기**다. 당시 Humanoid Avatar와 단위 변환을 확인했지만, 이후 하체 관절 오배치와 스킨 변형 문제가 확인되어 완성 리그로 판정하지 않는다.

손가락 본 30개를 보존한 별도 편집 리그에서 하체 관절을 바로잡고 동작 6종을 다시 적용한 V0.3 후보를 반입했다. 신규 기준 모델은 `05.Model/Player/Rigged/Models/PlayerDummy_Rigged_V0.3.fbx`, 신규 동작은 `07.Animator/Player/Clips/Rigged_V0.3/Player_*.fbx`로 분리했다. 웹 편집 저장본의 스킨 인덱스 불일치는 로컬에서 재매핑했으며, 웹 원본을 그대로 다시 받는 방식으로 대체하지 않는다. 새 7개 모두 유효한 Humanoid Avatar·매핑 52개(몸 22·손가락 30)·본과 bindpose 53개를 확인했다. 동작 6종을 임시 PreviewScene에서 9개 시점씩 총 54개 샘플로 확인했으며, 반입 검수 당시에는 기존 보호 파일 116개의 SHA-256과 사용자 씬·연결 상태를 유지했다. 이후 추가 승인으로 진행한 씬 연결은 아래 항목과 구분한다. 미세 찝힘·접지·루프·손 쥐기 품질은 추가 검수 대상이다. 파일별 출처·검증 상태·독립 발가락과 손가락의 제한은 [플레이어 리깅·애니메이션 안내](After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Player/Rigged/README.md)를 따른다.

## 현재 플레이어 연결

`PlayerInput`의 `Invoke Unity Events`로 Move → `PlayerPresenter.OnMove`, Look → `PlayerPresenter.OnLook`를 연결했다. Presenter는 매 프레임 `PlayerLook.Rotate`를 먼저 호출하고 `PlayerMotor.Move`에 입력과 경과 시간을 전달한다. 사용자 코드의 `PlayerPresenter → PlayerAnimationSystem.isMove → Animator.IsMoving`이 이동 입력 여부를 전달해 WASD와 Idle·Walk를 전환한다. 실제 위치 변화가 아닌 입력 유무를 기준으로 한다. 이동은 CharacterController, 상하 시야 회전은 CameraRoot가 담당하며 Cinemachine Virtual Camera가 CameraRoot를 따른다.

사용자가 `05.Model/Player/Player_Dummy_V0.1.prefab`에도 V0.3 외형·Animator와 현재 구성을 적용했다. SampleScene과 기준 플레이어 프리팹을 함께 관리하며, 학습 중인 입력·이동·애니메이션 구성을 조립·검증한 뒤 `04.Prefabs`의 완성 게임 에셋으로 관리한다.

SampleScene의 `Player_Dummy_V0.1/VisualRoot` 아래 `PlayerDummy_Rigged_V0.3`은 유효한 V0.3 Avatar와 기존 [Player_Animator](After_Seconds_Build_V0.01/Assets/Afrer_Seconds/07.Animator/Player/Controllers/Player_Animator.controller)를 사용하며 Apply Root Motion은 껐다. 현재 모델 로컬 Y는 `0.4`, CharacterController의 Center Y는 `0.3`, Height는 `1.8`이다. 기존 V0.2 모델 파일과 이전 동작은 비교용으로 보존한다.

최초 V0.3 연결에서는 Controller 상태 6개의 Motion만 교체하고 기존 전이·파라미터·속도를 유지했다. 당시 보호 대상 134개 중 변경은 승인한 SampleScene·Controller 2개뿐이었다. [최초 씬 연결 검수 기록](../Docs/검수/2026-10-29_Player_FullRig/scene-connection.json)은 이후의 사용자 코드·프리팹 적용·걷기 보정 전 기록으로 구분한다.

최신 Walk는 `Rigged_V0.3/Player_Walk.fbx`의 원본 프레임 `124–160`을 사용해 길이가 약 `1.2초`이며 Loop Time·Loop Pose를 켰다. Walk State는 `1.5배`여서 한 주기는 약 `0.8초`, Motor의 이동 속도는 `1.5m/s`다. 구간을 자른 뒤 Height Offset은 `0.164 → 0.227`로 다시 보정했다. 원본 FBX와 키는 그대로이며 importer의 사용 구간만 바꿨다. 이전 약 7.5초 전체 시퀀스와 과거 검수 기록은 보존한다.

실제 약 `3.30초` 동안 약 `4.13회` 반복했고 CharacterController 접지는 `51/51` 샘플이었다. 이동 속도 약 `1.5m/s`, 모델 로컬 yaw `0°`를 확인했다. 지면 대비 발바닥 높이 잔차는 약 `−0.016~+0.045m`로 남아 있어 완전한 접지·발 미끄러짐 제거 판정은 아니다. 기존 Run → Walk의 상충 조건, Land 조건, Pickup 복귀 전이는 이번 걷기 보정에서 수정하지 않았다.

`06.Data/PlayerLookSettings.asset`의 현재 감도는 좌우·상하 각각 💡 0.1, 상하 제한은 💡 -80°~80°다. C# 파일은 프로젝트 루트 `.editorconfig`의 UTF-8 BOM 설정을 기준으로 편집한다.

## 버전 관리와 다음 작업

Assets와 `.meta`, Packages, ProjectSettings를 함께 버전 관리한다. Library·Temp·Logs·Obj·UserSettings는 각 PC에서 재생성하므로 제외한다.

사용자가 직접 분석 → 의사코드 → 구현을 진행한다. **현재 WASD와 Idle·Walk 연동, 걷기 한 주기의 반복·높이·속도 보정까지 확인했다.** 다음은 점프·스프린트·상호작용과 관련 애니메이션을 의사코드로 분석한 뒤 사용자가 코드를 작성하고 검토하는 단계다. 기존 전이 조건과 발 접촉·미세 변형도 이어서 검수한다. 손가락 본 보존은 쥐기 애니메이션이나 손 상호작용 구현 완료를 뜻하지 않는다. 예약·교환 의사코드와 규칙 구현은 이후 남은 작업이며, A/B안은 프로토타입으로 비교한 뒤 결정한다.

- [집에서 이어하기](../Docs/이어하기_2026-10-26.md)
- [계층 분석·학습 순서](../Docs/Unity_계층_설계와_학습_순서.md)
