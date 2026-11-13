# 1F 황야 바위와 식생 지면 보수 V0.02

작성자 송예찬 · 2026-11-13

사용자가 수용한 석양 스카이박스와 Bloom은 그대로 유지한다. 앞서 남은 황야 바위의 각진 형태, 반복되는 식생, 지면과 원경 깊이감을 보수한다. 풍화된 바위 여러 형태, 휘어진 마른 풀과 분기 관목, 접지된 자갈과 군집 식생, 흙·먼지·자갈의 지면 분포와 겹친 낮은 구릉을 제작한다.

공장·승강기·아이비·내부 기물·기존 통행로와 엔딩 위치를 보존한다. 게임 코드·Input·Animator·다른 층은 변경하지 않는다. 신규 원본은 이 폴더, 반입 위치는 `05.Model/Environment/1F`, 출처 기록은 `06.Data/AssetSources`다. SourceAssets의 C#은 제작/검수용이다. 실제 이동·화면·LOD·접지·보존 검수를 수행한다.

백업: `%LOCALAPPDATA%/Temp/AfterSeconds_WildernessDetail_20261113/before`. 이전 전체 제작기와 이번 최초 반입·백업은 후속 편집 뒤 재실행하지 않는다.

변경 기록: V0.01 — 수용한 하늘 보존과 남은 황야 보수 범위. 송예찬.


최종 파일: `WD_RockA–C`, `WD_GrassA–D`, `WD_ShrubA–C`, `WD_StonePatchA–B`와 서쪽 접근부27청크. 모두3단계 LOD다. 기존 배치의 루트 위치·스케일을 유지하고 메시를 연결했으며, 풀/작은 돌은 지면 법선에 맞춰 회전했다. 바위 Collider51개는 새 LOD1 메시를 사용한다. 신규 자갈·풀465배치에는 Collider가 없다.

표면은 `WDNaturalLit.shader`와 `WDNaturalSurface.hlsl`, 재질은 `Materials/WD_M_*`다. 표준 조명 패스는 Unity URP17.4.0에서 파생했으며 [Unity Companion License](../F1_AbandonedCamouflage/Unity-URP-LICENSE.md)를 따른다. 기존 AE 공장 셰이더와 아이비를 변경하지 않는다. `WD_Earth`, `WD_Gravel`, `WD_PaleDust`, `WD_CompactedSoil` TerrainLayer는 기존 이미지의 타일/법선/색 범위를 다르게 사용한다.

카메라 표시 거리는 Main Camera만 바꾸면 Cinemachine이 덮어쓴다. 1F 씬의 `Camera/CM_Player_1st` → Lens → Far Clip Plane4,500m가 실제 제어값이며 FOV는 유지했다. 공용 카메라 프리팹에는 적용하지 않았다.

`Apply.cs`는 최초643배치 교체/465배치 추가·지면·원경, `Refine.cs`는 접근부27청크와 경사 정렬, `CameraRig.Fix`는1F 카메라 거리의 최종 보정 이력이다. 첫 Apply/Inventory/Before/report를 재실행하지 않는다. [검수](../../Docs/Review/2026-11-13_1F_WildernessDetail/Review.md) · [전후 화면](../../Docs/Review/2026-11-13_1F_WildernessDetail/review.html).

변경 기록: V0.02 — 최종 에셋·조절점·카메라 거리·검수 연결. 송예찬.
