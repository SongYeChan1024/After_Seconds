# 1F 위장 폐공장 제작 원본 V0.02

작성자 송예찬 · 2026-11-12

사용자 정정에 따라 지상1층은 **사용하지 않는 위장용 폐공장**이다. 초기 운영형 초안을 대체했으며, 이어서 AE_VA_Walls의 반복 얼룩을 보수했다. 최신 결과는 [검수](../../Docs/Review/2026-11-12_1F_Abandoned/Review.md)와 [화면 비교](../../Docs/Review/2026-11-12_1F_Abandoned/review.html)를 따른다.

레퍼런스는 `Docs/Reference/1F`의01/02 외관,03/04/06/07 내부 사진,08 평면도다. 08의 주거 용도를 이식하지 않고 중정/코어 구획만 참고했다. 원본 이미지는 수정하지 않았다.

- `architecture.py`, `landscape.py`, `site_structures.py`, `growth.py`: 파손 지붕·격자창·철골·데크·배관·굴뚝·사일로와 식생·잔해/울타리 원본. `site_structures.py`는 동일 구조의 빠른 직접 메시 생성 단계다.
- `site.py`/`terrain.bin`: 513높이맵·128알파맵·건물 하부 구멍. Terrain384×320m·흙/자갈/이끼3레이어. 건물 경계 바깥 구멍 노출 방지.
- `Apply.cs` 최초 적용 후 `Complete`, `Polish.cs`, `FrameCopies.cs`: 기존55기물을 방치 상태로 유지하고 새환경191FBX 반영. 초기 정상 업무 소품30개·대체된 구조/떠 있는 초기 등기구를 포함해76오브젝트 제거. 공유 기존 파일 수정 없음.
- `clean.py`/`CleanExport.cs`/`Refresh.cs`: 정밀 겹침 제거. `QualityExport.cs`의 영면적 면 제거 포함. 새AE모델만 수정하며GUID/노멀/UV를 유지했다.
- `weather_shader.py`/`AEWeathering.hlsl`/`Weather.cs`: 벽돌·미세입자와 큰 월드 좌표 오염을 분리. 관련10재질·LOD 포함252렌더러 적용. URP17.4 Lit 기반 코드의 출처/Unity Companion License는 `weather_source.json`/`Unity-URP-LICENSE.md`. 엔진 패키지 자체는 수정하지 않았다.
- `Walk.cs`, `Play.cs`, `Look.cs`, `Review.cs`, `WeatherReview.cs`: 통행79/79·실제Play11곳·Look·같은 시점 표면 비교. 외부 검수 C#만 사용하며 게임 C#을 추가하지 않았다. 에디터 임시 카메라는 두 번 렌더해 처음 프레임의 재질 초기화를 완료한 뒤 캡처한다.
- `Finish.cs`: 반사8개·가림 베이크/선택. `ExteriorCamera.cs`: 1F 씬 카메라만 SolidColor→Skybox. `Snapshot.cs`는 현재55기물/191환경모델과 반사 참조를 저장한다.

**현재 또는 이전 제작기를 일괄 재실행하지 않는다.** 생성기를 재실행하면 정밀 면 보수가 사라지고, `Apply.Import`를 다시 실행하면 최신 표면 셰이더가 초기 재질로 바뀐다. 후속 사용자의 수정이 있을 수 있으므로 현재 씬을 조사한 뒤 지정 부분만 보수한다. `before.unity`는 초기1F 백업이며Git 제외. `before_layout.json`은 초기 기준이고 현재 배치는 검수 `snapshot.json`과 Decision `as_built_layout.json`이다.

기존Unity13171파일 보존. B1·다른 층·공유 에셋·Player 프리팹/Animator/게임 코드·빌드 설정 미변경. 층 전환·문/승강기·AI·결말은 후속 기능이다. 저장된1F 편집 모드, AE_VA_Walls 선택. 커밋/push/블로그 요청 없음.
