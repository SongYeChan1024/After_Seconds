# B5 실험동·보안관제동 안내선 V0.02

2026-11-08 계단 A 제작 후 안내 확장: 새 T02/VA 구역이 제작되어 C01청록/C02파랑에 VA녹색을 추가했다. 현재 범위는3목적지4경로이며 [현재 제작 좌표/검수](../T02_StairA/README.md)를 우선한다. 아래 두 돔만의 기록은 이전 단계다. 도달할 목적지별 안내와 새 돔 제작 시 확장이라는 사용자 방침은 유지한다. 작성자 송예찬.

이전 단계 기록:
작성자 송예찬 · 2026-11-08

사용자 확정: 각 돔에서 갈 수 있는 목적지를 기준으로 안내선을 연결한다. 현재 제작된 C01 실험동과 C02 보안관제동 사이에는 두 목적지 선만 둔다. C01행 청록 `#39C8E3`, C02행 파랑 `#4F8CFF`이며 T01에서 평행하게 연결한다. 출발 돔이 달라도 같은 목적지의 색은 유지한다. 다른 돔이 완성·연결되면 그곳으로 가는 안내를 추가한다. 이전 네 색·여섯 경로는 현재 적용 기준이 아니다.

`plan.json`이 현재 실제 좌표다. `build_plan.py` → `verify_plan.py` → `textures.py` → `TwoDomeApply.Run` 순서이며 Python은 numpy/Pillow가 있는 `%TEMP%/as_art_tools/Scripts/python.exe`를 사용한다. Unity 호출은 기존 `SourceAssets/B4_StealthLayout/unity_task.py script run <절대경로> --entry <클래스.메서드>`를 따른다. 현재 씬과 에셋을 먼저 백업하며, 이번 작업의 baseline/Prepare/Inspect는 재실행해 이전 기준을 덮어쓰지 않는다.

새 안내 그룹에는 방향 경로2개와 실험동 연결 조각1개, 두 색 바닥 안내2개가 있다. 이전 계단A/유틸리티동 경로·목적지 표기를 현재 씬에서 제외했다. 이전 메시/재질 원본은 보존한다. 실험동 내부 흰 R1 순환선과 S1/M1 국소 작업 표기는 이번 두 돔 사이의 목적지 선과 별개로 유지했다.

`Probe.cs`/`RouteWalk.cs`/`Audit.cs`가 물리 경로·Controller·보존 상태를 확인한다. `Feeds.cs`와 `refresh_feeds.py`는 정적 감시 화면4장을 갱신한다. `Capture.cs`/`LabCapture.cs`/`T01Capture.cs`로 외형을 확인한다. `RecordSource.cs`는 출처 JSON과 최종 상태를 남긴다. `record_preservation.py`는 기존 파일 SHA256을 비교한다.

메시/재질/텍스처는 `Assets/Afrer_Seconds/05.Model/Environment/B5`, 출처 기록은 `06.Data/AssetSources/B5_TwoDomeGuidance_20261108.json`이다. 이전 C01/C02/전체 층 Apply는 재실행하지 않는다. 게임 C#/Animator·Light는 바꾸지 않는다. [검수 결과](../../Docs/검수/2026-11-08_B5_TwoDomeGuidance/검수결과.md)를 따른다.
