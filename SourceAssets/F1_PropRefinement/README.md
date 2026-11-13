# 1F 프랍 보수 제작 원본 V0.01

작성자: 송예찬 · 2026-11-13

대상은 CableReel3·OfficeChair5·ToolCart1·Forklift1·Press1, 총11배치다. `models.py`/`mesh.py`가 현재 원본이며 Blender5.2.2 LTS에서 Unity 미터 좌표의3LOD FBX를 만든다. 기존 공용 모델은 수정하지 않았다.

- `PRProp*`: 1F 새 프랍 전용 URP Lit 확장. `Environment/1F/AEWeatheredInput.hlsl`의 기존 재질 선언을 읽지만 수정하지 않는다.
- `Apply.cs`: 최초 Native API 반입·재질17개 생성·11배치 연결. 이미 적용했으므로 재실행 금지.
- `Refresh.cs`: 이번5개 FBX만 GUID 유지 갱신하는 도구. 소스 수정 후 대상/씬 상태를 확인한 경우만 사용한다.
- `Inspect.cs`, `Check.cs`, `Walk.cs`, `PlayCheck.cs`: 외부 검수용. Assets 안의 게임 C#이 아니다. `Before`/`ResumeBefore`/`prepare.py`는 기존 기준 자료를 덮거나 재생성하지 않도록 재실행하지 않는다.
- 최초 씬 백업: `%LOCALAPPDATA%/Temp/AfterSeconds_PropRefinement_20261113/before/Level_1F_Factory.unity`.
- 1F 대상 루트/충돌체 유지. 이전 Renderer를 끄고 새 PR 자식에 LOD0/1/2를 연결했다. 이전 FD 겹침은 비활성 Renderer로 보존한다.

반입 위치: `Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/1F/PR_*`.

[검수 결과](../../Docs/Review/2026-11-13_1F_PropRefinement/Review.md) · [전후 화면](../../Docs/Review/2026-11-13_1F_PropRefinement/review.html)

## 변경 기록

- V0.01 (2026-11-13): 곡면·기계 연결·마모와 검수 원본. 송예찬.
