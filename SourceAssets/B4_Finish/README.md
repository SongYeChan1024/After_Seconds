# B5/B4 표면과 B4 마감 제작 원본 V0.01

작성자: 송예찬 · 2026-11-09

`surfaces.py`, `walls.py`는 불규칙한 사용감 텍스처 제작 원본이다. `Surfaces.cs`, `Walls.cs`는 이미 적용했으므로 현재 씬에 재실행하지 않는다. 원본 재질과 충돌 메시를 보존하고 파생 시각 메시·재질만 연결했다.

`Lighting.cs`와 `ProbeFix.cs`는 B4 광원·정적 반사 제작, `LodExport.cs`→`lods.py`→`LodImport.cs`→`LodApply.cs`는 원본 근접 LOD를 보존한 원거리 최적화다. 기존 적용 도구는 현재 씬에 다시 실행하지 않는다.

`Verify.cs`, `WallVerify.cs`, `Walk.cs`, `Play.cs`와 각 캡처 도구는 외부 검수용이며 게임 Assets에 넣지 않는다. `before.unity`, 각 표면/벽 변경 전 씬과 JSON은 원상 비교 자료다. 게임 기능 구현과 구분한다.

[검수 결과](../../Docs/Review/2026-11-09_B4_Finish/Review.md)
