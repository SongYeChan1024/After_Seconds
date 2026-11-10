# B2 사용자 피드백 마감 제작 원본 V0.01

작성자 송예찬 · 2026-11-10

이 폴더가 B2 적치물·콘솔·바닥·계단 마감의 최신 후속 원본이다. `plan.json`은 기존 운영 배치186개에 윤활 설비와 모터 받침을 추가한188개, 적치물2개 위치/방향을 포함한다. 기존 전체 Apply/plan 생성기를 현재 씬에 재실행하지 않는다.

`build.py`는 Blender 콘솔·모터 받침·윤활 정비 설비3종과 거리 LOD3종, 베벨 원본을 만든다. 신규 VARCO 생성 없이 기존 품질 부족 콘솔을 수작업 교체했다. `textures.py`는 방별 실제 설비 위치에 따른 콘크리트 PBR·금속 타일·정적 화면을 생성한다. `treads.py`는 발판 중앙 마모/끝 오염 표면이다. `BR_ONLY_TILES=1`은 바닥 지도를 재생성하지 않고 공용 마감만 갱신한다.

`Apply.Import`는 초기 반입, `Apply.Run`은 한 번만 실행하는 씬 적용이다. `Refine.Run`은 LCD 발광 플래그, 오래된 C02 바닥 줄눈 제거, 카트 방향을 마감한다. `Treads.Run`은 시각 메시만 파생하고 원래 충돌을 유지한다. 현재 씬에 재실행할 경우 기존 후속 수정을 반드시 대조한다. 계단의 파생 메시를 다시 생성하지 않는다.

`Audit.Ground/Upper`와 `Play`/`PlayBay`, `Verify`가 통행·실제 프레임·참조를 검사한다. 실제 Mouse/Keyboard 장치는 비활성화하지 않는다. 외부 C#은 일시 실행용이며 게임 스크립트를 추가하지 않는다. `Finish.Reflections/Occlusion/Complete`는 최종 반사·가림 갱신이다. `Capture`의 `detail_*`만 임시 점검등이며 다른 비교 사진은 실제 조명이다.

`record.py`는 검사 통과 후 출처·실배치·최신 안내를 기록한다. 원본 씬 백업은 `C:/Users/503-26/Documents/Codex/Backups/AfterSeconds_B2_Surface_20261110/`에 있다. 기존 모델·.meta는 보존했다.

[검수](../../Docs/Review/2026-11-10_B2_SurfaceRefinement/Review.md) · [전후 비교](../../Docs/Review/2026-11-10_B2_SurfaceRefinement/review.html)
