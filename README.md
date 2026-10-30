# After Seconds 프로젝트 안내 V0.11

맞힌 대상과 3초 뒤 위치를 바꾸며 연구 시설을 탈출하는 1인칭 퍼즐 액션 게임.

## 프로젝트 구성

| 위치 | 용도 |
| --- | --- |
| `Docs/` | 메인 기획서, 계층 설계·학습 안내, 이어하기 기록, 도면 |
| `Prototype/Web/` | 웹 프로토타입과 설명 |
| `Unity/After_Seconds_Build_V0.01/` | 현재 Unity 게임 프로젝트 |

Unity 작업 루트는 `Assets/Afrer_Seconds/`다. 앞으로 `03.Art`에는 2D 이미지만 넣고 `UI/`, `Cutscenes/` 등 이미지 종류별 폴더로 분류. 
`05.Model`에는 기준 리깅 모델과 부속 재질·조립 중인 외형을 용도별로 보관하고, `04.Prefabs`에는 스크립트와 결합해 기능이 완성된 에셋을 둘 것. 
모델 준비 단계의 `.prefab` 파일도 `05.Model`에서 관리.

애니메이션은 `07.Animator`의 `Player/`, `Enemy/` 등 대상별 폴더에서 관리한다. 기존 플레이어 동작 FBX 6종은 `07.Animator/Player/Clips/`에, AnimatorController(`.controller`)·AnimatorOverrideController(`.overrideController`)는 `07.Animator/Player/Controllers/`에 둔다. AvatarMask(`.mask`)를 사용할 때는 해당 대상의 `Masks/` 폴더를 만든다. 기존 기준 모델은 사용자가 이름을 바꾼 `05.Model/Player/Rigged/Models/PlayerDummy_Rigged_V0.2.fbx`이며, 과거 반입명은 `AS05_PlayerDummy_Rigged.fbx`다.

2026-10-29. 손가락 본을 보존하고 하체 관절·스킨 인덱스를 보정한 별도 V0.3 후보와 동작 6종을 반입. 
신규 모델은 `05.Model/Player/Rigged/Models/PlayerDummy_Rigged_V0.3.fbx`, 동작은 `07.Animator/Player/Clips/Rigged_V0.3/`에 분리. 
새 7개 파일의 유효한 Humanoid Avatar와 동작 54개 시점의 임시 미리보기를 확인했으며, 반입 단계에서는 기존 V0.2·동작 6종·보호 대상 파일 116개를 보존. 
**웹 재생성 원본에는 스킨 인덱스 오류가 남아 있으므로 프로젝트의 보정 FBX를 기준으로 한다.** 미세 변형·접지·루프·독립 발가락·손 쥐기 품질은 추가 검수 대상. 
파일별 출처와 확인 범위는 [리깅·애니메이션 안내](Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Player/Rigged/README.md)를 따름.

현재 SampleScene과 사용자가 적용한 기준 플레이어 프리팹에 V0.3 외형과 `Player_Animator`의 동작 6종을 연결했다. 사용자 코드가 `PlayerPresenter → PlayerAnimationSystem.isMove → Animator.IsMoving`으로 이동 입력 여부를 전달해 WASD에 따라 Idle·Walk가 전환된다. Walk는 원본 FBX를 보존한 채 importer의 프레임 `124–160`만 사용하며, 클립 약 `1.2초`·State `1.5배`로 한 보행 주기 약 `0.8초`를 반복한다. 실제 이동 속도는 `1.5m/s`, 높이 오프셋은 `0.227`이며 Root Motion은 껐다. 다음은 점프·스프린트·상호작용과 관련 애니메이션을 의사코드부터 분석하고 사용자가 직접 구현하는 단계다.

현재 `03.Art/Candidates/VARCO`에 남아 있는 기존 모델·텍스처·재질·검수 기록은 과거 반입 결과. 
앞으로의 2D 이미지 분류 기준과 구분하며, 이번에는 기존 파일을 일괄 이동하지 않음.

실제 폴더 트리·계층별 역할·현재 에셋 위치는 [Unity 프로젝트 안내](Unity/README.md)에 정리.

## 주요 문서

- [프로젝트 공통 작업 규칙](CLAUDE.md) · [Codex 작업 안내](AGENTS.md)
- [집에서 이어하기 — 2026-10-26](Docs/이어하기_2026-10-26.md)
- [메인 기획서 V0.09](Docs/AfterSeconds_메인기획서.md)
- [Unity 계층 설계와 학습 순서](Docs/Unity_계층_설계와_학습_순서.md)
- [Unity 프로젝트 안내](Unity/README.md)
- [2026-10-28 데일리 로그 — 의사코드로 배우는 과정](https://songyechan1024.github.io/Kasil_DevLog/posts/daily-log-learning-through-pseudocode/)
- [2026-10-28 기술 기록 — After Seconds 1인칭 플레이어 컨트롤러](https://songyechan1024.github.io/Kasil_DevLog/posts/after-seconds-first-person-player-controller/)

## 집에서 Unity CLI로 이어하기

2026-10-28에 **Unity 6000.4.0f1 / Unity CLI 1.0.0-beta.13 / Pipeline 0.9.1-exp.1** 조합으로 확인했다. 
아래 명령은 Windows PowerShell 기준.

집에서는 **최신 `main`을 먼저 받은 뒤** 아래 절차를 진행. 
이번 변경에는 플레이어 코드·SampleScene 연결·설정 에셋과 Pipeline·Cinemachine 패키지 설정이 함께 포함.

### 1. 저장소 받기

처음 받는다면 저장할 상위 폴더에서 실행.

```powershell
git clone https://github.com/SongYeChan1024/After_Seconds.git
Set-Location .\After_Seconds
```

이미 받은 저장소라면 그 폴더에서 현재 브랜치와 수정 파일을 먼저 확인. 
오늘 작업은 `main` 기준. 
다른 브랜치이거나 수정 파일이 있다면 기존 작업을 먼저 정리한 뒤 `main`을 갱신.

```powershell
git branch --show-current
git status --short
git pull --ff-only
```

Git으로 이어지는 것은 커밋·푸시한 프로젝트 파일과 기록. 
채팅 원문 전체가 Git으로 자동 동기화되지는 않으므로 [이어하기 기록](Docs/이어하기_2026-10-26.md)도 읽을 것.

### 2. 집 PC에 CLI 설치하고 로그인하기

먼저 `unity --version`을 실행. 
명령을 찾지 못한다면 PowerShell에서 공식 Windows 설치 명령을 실행하고 터미널을 닫았다가 다시 열 것. 
[Unity 공식 설치 안내](https://docs.unity.com/en-us/unity-cli/use-unity-cli#install-with-a-package-manager)

```powershell
winget install Unity.CLI
```

새 터미널에서 확인한 뒤 본인의 Unity 계정으로 로그인. 
`unity auth login`이 여는 브라우저에서 진행하며, 비밀번호나 토큰을 README·채팅·Git에 적지 않음.

```powershell
unity --version
unity auth login
unity auth status
```

### 3. 기존 Unity 프로젝트 열기

Unity Hub에 **6000.4.0f1**을 설치하고, 받은 저장소 안의 `Unity/After_Seconds_Build_V0.01`을 기존 프로젝트로 추가해 열기.
`Assets`, `Packages`, `ProjectSettings`가 있는 폴더가 기준이며 새 프로젝트를 만들 필요는 없음.

`Packages/manifest.json`에는 `com.unity.pipeline` **0.9.1-exp.1**과 `com.unity.cinemachine` **2.10.7**이 등록되어 있다. 최신 `main`을 받은 다음 최초 Library 생성과 Package Manager의 패키지 복원·스크립트 컴파일을 기다린다. 
`unity pipeline install`을 다시 실행하거나 다른 버전으로 덮어 설치하는 단계가 필요하지 않다. [Pipeline 연결 안내](https://docs.unity.com/en-us/unity-cli/unity-pipeline/unity-pipeline-package)

**VARCO 브릿지는 선택 설치다.** 기본 패키지 의존성에서 브릿지를 분리했으므로 학원 PC의 Downloads 경로가 집에서 필요하지 않다. 이미 반입한 FBX·텍스처·재질과 SampleScene은 브릿지 없이 사용할 수 있다. 앞으로 웹에서 `Send to Unity`를 사용할 때만 집 PC에 브릿지 v1.1.0을 준비해 직접 연결한다.

1. Unity의 `Window > Package Management > Package Manager`를 연다.
2. 설치 메뉴에서 `Install package from disk`를 선택한다.
3. 집 PC에 압축을 푼 브릿지 패키지 폴더의 **`package.json`**을 선택한다. 상위 ZIP이나 Unity 프로젝트의 manifest를 선택하지 않는다.
4. 패키지 복원을 기다린 뒤 필요할 때 `VARCO3D > Connect`를 켠다. 설치로 manifest·lock에 생기는 **PC별 절대 `file:` 경로를 공용 저장소에 다시 커밋하지 않는다.**

브릿지 설치는 기존 에셋을 중복 반입하는 단계가 아니다. 설치 메뉴의 자세한 절차는 [Unity 로컬 패키지 안내](https://docs.unity3d.com/6000.4/Documentation/Manual/upm-ui-local.html)를 참고한다.

### 4. 프로젝트 폴더에서 연결 확인하기

저장소 루트에서 PowerShell을 열고 실제 Unity 프로젝트 폴더로 이동한다. 이후 명령은 이 위치에서 실행한다.

```powershell
Set-Location .\Unity\After_Seconds_Build_V0.01
unity pipeline list
```

Unity Editor를 열어 둔 상태에서 **Running, Pipeline 설치, Server Reachable**이 모두 정상인지 확인한다. JSON 출력에서는 각각 `isRunning`, `hasPipelinePackage`, `pipelineServer.isReachable`이 `true`다. 조회를 시작할 때 Play 모드는 끄고, 패키지 복원과 컴파일이 끝나기를 기다린다. 포트 번호는 CLI가 찾으므로 학원 PC의 localhost 주소나 포트를 집에 복사할 필요가 없다.

여러 프로젝트를 열었다면 명령 뒤에 `--project-path .`을 붙여 현재 프로젝트를 지정한다. 연결이 안 되면 프로젝트 폴더·열린 Editor·패키지 오류·컴파일 오류 순서로 확인한다.

### 5. 처음 사용할 읽기 전용 명령

아래는 씬이나 설정을 바꾸지 않고 현재 상태를 읽는 예시다.

```powershell
# 열린 씬의 Hierarchy
unity command scene get_hierarchy --result-only --json

# 컴파일 상태와 Console 오류 개수
unity command console status --result-only --json

# 현재 프로젝트가 제공하는 명령 목록
unity command

# C# 조회: 현재 활성 씬 이름
unity command script eval 'return UnityEngine.SceneManagement.SceneManager.GetActiveScene().name;' --result-only --json
```

`console status`의 `groundTruth.compilationFailed`와 `compiling`이 `false`, `consoleErrors`가 `0`인지 확인한다. `counts`는 과거 캡처 로그가 남을 수 있으므로 현재 Console 상태는 `groundTruth`를 기준으로 읽는다.

확인한 CLI **beta.13**에서는 C# 실행을 `unity command script eval`로 호출한다. 위 예시처럼 값을 돌려줄 때 `return`과 세미콜론(`;`)을 포함한 C# 문장으로 쓴다. 공식 문서의 다른 버전에서 보이는 최상위 `unity eval` 예시와 혼용하지 않는다. CLI나 Pipeline 버전이 달라지면 `unity --help`, `unity command --help`, 명령 목록을 먼저 확인한다. `script eval`은 코드에 따라 프로젝트를 수정할 수도 있으므로 조회 단계에서는 위와 같은 값 읽기만 실행한다.

이 프로젝트는 **Unity CLI → Pipeline으로 직접 조회**한다. Unity AI Assistant 패키지는 제거한 상태이며, CLI 사용에 Unity AI 구독이나 MCP 클라이언트 설정은 필요하지 않다. 따라서 Assistant의 `NoSubscription` 문제를 해결하려고 구독하거나 MCP를 다시 연결할 필요도 없다. [CLI와 Unity AI의 관계](https://docs.unity.com/en-us/unity-cli/replace-mcp-server-unity-cli#unity-cli-capabilities)
