# After Seconds Unity 프로젝트 안내 V0.02

2026-10-28 · 작성자 송예찬 · 실제 저장된 폴더 구조 기준

## 프로젝트 열기

- Unity Hub에서 열 폴더: `After_Seconds_Build_V0.01` — `Assets`, `Packages`, `ProjectSettings`가 있는 폴더.
- Unity: **6000.4.0f1**
- URP: **17.4.0**
- Input System: **1.19.0**
- Cinemachine: **2.10.7**, Pipeline: **0.9.1-exp.1**
- 실제 작업 루트: `Assets/Afrer_Seconds/`. 현재 폴더명을 그대로 사용한다.

집에서는 최신 `main`을 먼저 받은 뒤 연다. CLI 설치·로그인·조회 명령은 [집 CLI 안내](../README.md#집에서-unity-cli로-이어하기)를 따른다. VARCO 브릿지는 선택 설치로 분리했으므로 학원 PC의 Downloads 경로 없이 패키지를 복원할 수 있다. 기존 FBX와 현재 SampleScene에는 브릿지가 필요하지 않다.

## 현재 폴더 구조

아래는 `After_Seconds_Build_V0.01` 안의 게임 작업 폴더다. `.meta`는 생략했다.

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
    Player/Player_Dummy_V0.1.prefab
    Enemy/Enemy_Guard_V0.1.prefab
    Props/Props_Crate_V0.1.prefab
    Environment/                     # 현재 비어 있음
  06.Data/
    PlayerMotorSettings.asset
    PlayerLookSettings.asset
```

## 폴더별 사용 기준

| 폴더 | 보관할 내용 | 현재 상태 |
| --- | --- | --- |
| `01.Scenes` | 사용자가 구성하는 씬과 레벨 | SampleScene에서 사용자 배치와 플레이어 이동·시야 회전을 확인함 |
| `02.Scripts` | 책임에 따라 분리한 게임 코드와 AD | 6개 AD와 입력·이동·시야·Presenter 코드 |
| `03.Art` | 미술 원본·텍스처·재질·후보 검수 기록 | 현재 VARCO 원본 FBX와 연결 리소스를 보관함 |
| `04.Prefabs` | **스크립트와 결합해 기능이 완성된 게임 에셋** | 완성 에셋은 아직 없음 |
| `05.Model` | **반입한 모델과 조립 중인 외형 에셋** | Player·Enemy·Props·Environment로 분류함 |
| `06.Data` | ScriptableObject 설정 에셋 | 이동·시야 설정 |

앞으로 가져오는 모델은 `05.Model`의 용도에 맞는 분류에 정리한다. 모델을 묶은 `.prefab` 형식의 파일도 이 단계에서는 `05.Model`에서 관리한다. 동작 스크립트와 필요한 설정을 연결하고 기능을 확인한 뒤, 완성된 게임 에셋을 `04.Prefabs`에서 관리한다.

현재 `05.Model`의 모델은 `03.Art/Candidates/VARCO/`의 FBX·텍스처·재질을 참조한다. Unity 안에서 파일과 `.meta`를 함께 이동해 참조를 유지한다. Plane 생성과 모델·레벨 배치는 사용자가 직접 진행한다.

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
| 회색 플레이어 더미 | [05.Model/Player/Player_Dummy_V0.1.prefab](After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Player/Player_Dummy_V0.1.prefab) | 정적 T포즈, 높이 💡 1.8m |
| 주황 경비 더미 | [05.Model/Enemy/Enemy_Guard_V0.1.prefab](After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Enemy/Enemy_Guard_V0.1.prefab) | 정적 T포즈, 높이 💡 1.8m |
| 시료 궤짝 | [05.Model/Props/Props_Crate_V0.1.prefab](After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/Props_Crate_V0.1.prefab) | 높이 💡 1m |

위 높이와 충돌체 치수는 테스트용 가안이다. 캐릭터 둘은 리깅·애니메이션이 없다. 플레이어의 이동·시야 회전은 현재 SampleScene에서 연결했으며, 사격·경비 행동·교환 규칙은 아직이다. 세 후보 모두 8,000 triangles이며 색상·노멀 텍스처를 URP 재질에 연결했다. 자세한 상태와 출처는 [VARCO 에셋 반입 안내](After_Seconds_Build_V0.01/Assets/Afrer_Seconds/03.Art/Candidates/VARCO/README.md)를 참고한다.

## 현재 플레이어 연결

`PlayerInput`의 `Invoke Unity Events`로 Move → `PlayerPresenter.OnMove`, Look → `PlayerPresenter.OnLook`를 연결했다. Presenter는 매 프레임 `PlayerLook.Rotate`를 먼저 호출하고 `PlayerMotor.Move`에 입력과 경과 시간을 전달한다. 이동은 CharacterController, 상하 시야 회전은 CameraRoot가 담당하며 Cinemachine Virtual Camera가 CameraRoot를 따른다.

`05.Model/Player/Player_Dummy_V0.1.prefab`에는 PlayerInput·CharacterController·Motor·Presenter가 일부 연결되어 있다. **CameraRoot와 PlayerLook은 현재 SampleScene에서 추가·연결한 구성**이므로 이 모델 프리팹만 새 씬에 놓아서는 전체 플레이어가 완성되지 않는다. 필요한 구성을 모두 조립·검증한 뒤 `04.Prefabs`의 완성 게임 에셋으로 관리한다.

`06.Data/PlayerLookSettings.asset`의 현재 감도는 좌우·상하 각각 💡 0.1, 상하 제한은 💡 -80°~80°다. C# 파일은 프로젝트 루트 `.editorconfig`의 UTF-8 BOM 설정을 기준으로 편집한다.

## 버전 관리와 다음 작업

Assets와 `.meta`, Packages, ProjectSettings를 함께 버전 관리한다. Library·Temp·Logs·Obj·UserSettings는 각 PC에서 재생성하므로 제외한다.

사용자가 직접 분석 → 의사코드 → 구현을 진행한다. **2026-10-29 계획은 애니메이션 연결, 점프, 달리기, 상호작용**이다. 애니메이션은 사용할 모델의 리깅 상태부터 확인한다. 예약·교환 의사코드와 규칙 구현은 이후 남은 작업이며, A/B안은 프로토타입으로 비교한 뒤 결정한다.

- [집에서 이어하기](../Docs/이어하기_2026-10-26.md)
- [계층 분석·학습 순서](../Docs/Unity_계층_설계와_학습_순서.md)
