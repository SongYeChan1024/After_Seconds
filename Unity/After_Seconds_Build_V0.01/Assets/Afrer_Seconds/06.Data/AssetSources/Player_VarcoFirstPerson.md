# Player VARCO 1인칭 애니메이션 V0.01

2026-11-17 · 작성자 송예찬

- 서비스: VARCO 3D, 카탈로그 키 `throw_baseball`, In Place.
- Flow: `8f7100a4-a7df-488b-81ee-0c2ac6ae60d8` — After_Second_Env_and_Props_Ver0.03.
- Animate 노드: `e6950545-9a83-47c9-a220-84bf9b83000c`.
- 결과 Task: `8d421ec5-cde4-404e-9cc2-ca041536b36e`, 비용0포인트.
- 기존 리그 Task: `4838631d-f39c-455a-85cc-8d2f519eee6e`.
- 반입 클립: `Assets/Afrer_Seconds/07.Animator/Player/Clips/VarcoFirstPerson/Player_Overhand_Varco.fbx` — 메시 없이 뼈와 애니메이션만 포함, Humanoid,30fps·약3.333초.
- 화면용 손 곡선: `Assets/Afrer_Seconds/06.Data/PlayerHandAnimations.asset`.
- 연결 프리팹: `Assets/Afrer_Seconds/05.Model/Player/Player_Dummy_V0.1.prefab`의 `PlayerFirstPersonHands`.
- 기존 걷기/달리기: `07.Animator/Player/Clips/Rigged_V0.3/Player_Walk.fbx`, `Player_Run.fbx`를 재사용. 사용자 선택 클립/구간과 전신 Controller 유지.
- 전용 아래 던지기 키가 없어 기존 절차적 underhand 유지. 원본 전신 투척의 카메라 직접 재생이 아니라, 현재 리그에서 추출한 손 경로를 화면 진폭에 맞춰 IK로 적용한다.
- 사용자 후속 보정: 아래 던지기는 낮은 손(0.26,-0.34,0.68)m에서6m/s·상승35도로 띄운다. 확대 시 손 높이8cm 보정, 위 던지기는12m/s·8도 유지. 아래 방출 후 팔 상승은 절차적 동작이다.
- 저장소 루트 `SourceAssets/VarcoFirstPerson`에 원본·출처 JSON·Blender/Unity 반입기·베이크/검수 파일이 있다. `Docs/Review/2026-11-17_VarcoFirstPerson`에 결과를 기록한다.

V0.01 — VARCO 투척 신규 반입과 기존 이동 클립의1인칭 연결 출처 기록. 송예찬.
