# 1F 사용 흔적과 환경 연결 보수 V0.02

작성자 송예찬 · 2026-11-13

사용자 승인 순서대로 바닥·설비 연결 → 위치별 벽 노후화 → 식생·지붕 파손 잔해를 보수한다. 현재 1F 저장 씬을 기준으로 추가 작업하며 앞선 제작기를 다시 실행하지 않는다.

프레스와 컨베이어의 전원 연결, 바닥 매립형 트렌치, 철거 설비의 앵커·먼지 경계, 하역 바닥의 이동 마모를 제작한다. 벽은 하단 수분·창턱 빗물·체결부 주변에 오염을 집중한다. 지붕 재질과 낙하 위치에 맞춘 잔해, 틈에서 자라 벽을 타고 분기하는 아이비와 지면 낙엽을 연결한다. 주요 통행 공간은 유지한다.

게임 C#·Player·Animator·다른 층·황야·기존 승강기 가동부 피벗은 보존한다. SourceAssets의 C#은 외부 제작·검수 도구다. 모델과 재질은 1F Environment에 분류하며 기존 아이비와 표면 에셋의 GUID를 보존한다. 검수 결과와 전후 화면은 `Docs/Review/2026-11-13_1F_EnvironmentalStory`에 기록한다.

변경 기록: V0.01 — 승인 범위와 제작 순서 기록. 송예찬.


## 최종 반입과 검수

`models.py`는 설비 연결·앵커·지붕 낙하 흔적·싹을 만든다. `surfaces.py`는 월드 위치에 맞춘 바닥 mode7과 창턱·벽 하단 마스크를 만든다. `ivy.py`는 분기 식생·낙엽을 만들고 `GroundCheck`·`LitterGround`·`ground_litter.py`는 실제 지면 높이에 맞춘다. 바닥 Renderer에는 `AE_M_Floor`가 연결되며 공용 `AE_M_Concrete`를 일괄 변경하지 않는다.

최신 씬에는 `1F_AbandonedFactory/EnvironmentalStory` 아래8개 모델을 연결했다. 기존 `AE_WallIvy`는 같은 GUID로 갱신했다. 원본 프로퍼티·충돌체165개 보존, 통행75/75와 실제Play3시점 통과. 세부 수치는 [검수 기록](../../Docs/Review/2026-11-13_1F_EnvironmentalStory/Review.md)과 [전후 화면](../../Docs/Review/2026-11-13_1F_EnvironmentalStory/review.html)을 따른다.

`Apply.Run`은 처음 반입할 당시의 절차이며 현재 씬에 다시 실행하지 않는다. `FloorBinding`, `RefineModels`, `RefineGrowth`, `Refine`는 이번 검수 중 사용한 제한 갱신이다. 재실행 전에 이후 사용자 변경과 비교해야 한다. `setup.py`도 기존 검수 기준을 덮어쓰므로 다시 실행하지 않는다. 작업 전 백업과 FBX 후보는 `%LOCALAPPDATA%/Temp/AfterSeconds_EnvironmentalStory_20261113/`에 있다.

변경 기록: V0.02 — 실제 재질 연결·접지 보정·최종 모델과 검수 경로 기록. 송예찬.
