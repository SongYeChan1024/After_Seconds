# B5 목적지별 색 안내선 제작 V0.02

2026-11-08 두 돔 안내만 적용: 사용자는 각 돔에서 갈 수 있는 목적지를 기준으로 안내하며 현재 C01/C02 사이의 두 선만 유지한다고 확정했다. [현재 제작 기준](../B5_TwoDomeGuidance/README.md)을 우선한다. 아래 네 색/여섯 경로 및 전체 용도별 노선안은 이전 기록이며 현재 씬에 그대로 재적용하지 않는다. 다른 돔이 제작·연결되면 해당 목적지 선을 추가한다. 작성자 송예찬.

이전 단계 기록:
작성자 송예찬 · 2026-11-08

현재 C01/T01/C02/T02/VA/T05/C04의 안내선은 이 폴더의 `plan.json`과 [최신 검수](../../Docs/검수/2026-11-08_B5_DestinationColors/검수결과.md)를 우선한다. 이전 B5_WayfindingNetwork의 R1/S1/M1 전역 배치안은 참고 자료이며 현재 반영 구간 위에 그대로 적용하지 않는다.

| 목적지 | 색 | 식별 모양 |
| --- | --- | --- |
| C01 실험동 | 청록 `#39C8E3` | 원 |
| C02 보안관제동 | 파랑 `#4F8CFF` | 사각 |
| C04 유틸리티동 | 보라 `#C27FFF` | 마름모 |
| VA 계단 A | 녹색 `#70D692` | 이중 막대 |

## 원본과 실행 범위

`Survey.cs`는 기존 선·표기/포털을 읽는다. `build_plan.py`는 실제 T01 문 중심과 C02 분기를 따라 여섯 경로를 만든다. `verify_plan.py`는 선/모양/표기/S1 간격을 검사하며 numpy가 필요하다. `textures.py`는 Pillow로 목적지 스텐실4장과 바닥 색상 안내2장을 만든다. 현재 도구 환경은 `%TEMP%/as_art_tools/Scripts/python.exe`다.

Unity 호출은 `python SourceAssets/B4_StealthLayout/unity_task.py script run <C# 절대경로> --entry <클래스.메서드>`를 사용한다. `Apply.cs`의 `DestinationApply.Run`은 전용 메시·재질·안내 그룹과 명시된 기존 표기/렌더러만 갱신한다. 기존 C01 내부 순환선·S1/M1은 보존하며 이전 전체 C01/C02/층 Apply는 재실행하지 않는다. 재적용 전 현재 사용자 편집과 씬을 별도로 백업한다.

`Probe.cs`, `RouteWalk.cs`, `Audit.cs`로 물리 통행/실제 Controller/보호 상태를 검사한다. `Capture.cs`, `T01Capture.cs`, `LabCapture.cs`는 편집 카메라 검수다. `Feeds.cs` → `refresh_feeds.py`는 SC_Display_01–04의 정적 화면을 갱신한다. `RecordSource.cs`는 두 바닥 색상 안내의 프랍 간섭을 검사하고 출처 JSON을 저장한다. `record_preservation.py`는 원래 파일의 SHA256을 대조한다. `finish_documents.py`는 검수 결과를 확인한 뒤 문서를 갱신한다.

모델/재질/텍스처는 `Assets/Afrer_Seconds/05.Model/Environment/B5` 및 Materials/Textures, 출처는 `06.Data/AssetSources/B5_DestinationColors_20261108.json`이다. `prepare.py`/`Prepare.cs`와 `baseline.json`은 이번 작업 시작 시점 기록이므로 후속 작업에서 기존 기준을 덮어쓰도록 재실행하지 않는다.

적용은 네 목적지·여섯 경로에 한정된다. 나머지11목적지와 다른 복도 확장은 별도 설계/간격 검수가 필요하다. 게임 C#/Animator는 추가하지 않으며 최종 조명은 B5 전체 제작 후 조정한다.
