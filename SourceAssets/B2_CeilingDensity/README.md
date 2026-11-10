# B2 설비 규모·천장 밀도 제작 원본 V0.01

작성자 송예찬 · 2026-11-10

`plan.json`194배치와 `changes.json`, `models.json`이 이 단계의 원본이다. 사용자 레퍼런스9장은 Docs/Reference/B2에 있다. 이전 B2_SurfaceRefinement188배치에서 이어진다. 현재 씬에 과거 Apply나 prepare를 무작정 재실행하지 않는다.

`prepare.py`는 기준 배치로부터 확대/재배치안과 서비스 제작 코드를 만든다. `services.py`는 치수·회전·돔 곡률에 맞는 공정 배관/받침, `build.py`는 천장 회로12종과 S01/E03 프레임2종을 만든다. 모두 새 CD_ 접두어로 보관하며 원본 .meta/GUID는 보존했다. 제조 모서리 베벨, 플랜지/볼트, 편집용 .blend, Far LOD를 포함한다. 신규 VARCO 요청 없이 Blender로 연결 구조를 직접 제작했다.

`Apply.Import` 반입 → `Apply.Run` 최초1회 배치 → 필요한 경우 `Apply.Reposition`만 사용한다. Run 재실행은 중복 적용을 막는다. Reposition은 위치/방향만 갱신해 확대 배율을 중복 적용하지 않는다. 기존 Visual_L0 하위 회전은 보존한다. 기존 BO 배관은 비활성 보관했다.

`Audit.Ground/Upper`, `Quality`, `Verify`는 콜라이더 통행/돔 경계/참조/모델 검수다. `Play` 최초 W02 경로는 계단을 올라가는 잘못된 바닥 경로여서 실패했고 `PlayGenerator`로 발전기 서쪽 점검 통로를 재검증했다. 실패 기록도 유지했다. Mouse/Keyboard는 비활성화하지 않으며 검사 후 설정을 복원한다. 이 C#은 Assets 밖의 일시 실행 제작/검수 도구이며 런타임 게임 코드가 아니다.

`Finish.Reflections/Occlusion/Complete`는 반사/가림 마감, `Capture`와 `Audit.After`는 비교 사진, `record.py`는 검사 통과 후 문서/출처 기록이다. `inspection_*`만 임시 점검등 사진이다.

백업: C:/Users/503-26/Documents/Codex/Backups/AfterSeconds_B2_Ceiling_20261110. 작업 중 사용자 미저장 상태도 별도 사본으로 저장했다.

[검수 기록](../../Docs/Review/2026-11-10_B2_CeilingDensity/Review.md) · [비교 화면](../../Docs/Review/2026-11-10_B2_CeilingDensity/review.html)
