# After Seconds Unity 프로젝트

- Hub에서 열 폴더: `After_Seconds_Build_V0.01`
- Unity: **6000.4.0f1**
- URP: **17.4.0**
- 현재 상태 (2026-10-26 종료): 사용자가 6계층 폴더와 asmdef를 생성함. DefineAD·SimulatorAD의 `No Engine References` 및 `SimulatorAD → DefineAD` 참조 저장 확인. 게임 로직은 작성 전이며 Unity Console·실행 결과는 별도 확인 필요.
- 실제 작업 루트: `After_Seconds_Build_V0.01/Assets/Afrer_Seconds` (현재 폴더명 그대로 기록). 씬은 `01.Scenes`, 코드는 `02.Scripts` 아래에 있음.
- [집에서 이어하기](../Docs/이어하기_2026-10-26.md)
- [계층 분석·학습 순서](../Docs/Unity_계층_설계와_학습_순서.md)

Assets와 `.meta`, Packages, ProjectSettings는 버전 관리한다. Library·Temp·Logs·Obj·UserSettings는 각 PC에서 재생성하므로 제외한다. 사용자가 직접 분석·의사코드·구현을 진행하며, Codex는 단계별 설계와 질문을 지원한다.

다음 시작점은 Define 데이터의 최소 필드 분석이다. A/B안은 프로토타입으로 비교한 뒤 결정한다.
