# B4 배치 보수 제작 원본 V0.01

작성자: 송예찬 · 2026-11-09

현재 완성 배치는 Unity의 `Level_B4_Circular.unity`, 접근 검수 기준은 이 폴더의 `layout.json`이다. [검수 기록](../../Docs/Review/2026-11-09_B4_LayoutPolish/Review.md)을 먼저 읽는다.

- `build.py`, `bay.py`, `BP_*.blend`: 21종 모델 원본. 미터 단위, Unity 전방 +Z, 제조 부품 베벨과 삼각화 후 FBX 반입.
- `Apply.cs`: 반입·1차 적용. `Run`은 중복 적용을 막는다. 기존 배치에 다시 전체 적용하지 않는다. `Import`는 BP 전용 모델·재질만 매핑한다.
- `plan.py`, `changes.json`, `layout_review.png`: **1차 배치 계산 자료**다. 이후 C04 접근 보수와 중앙 작업대 추가가 있으므로 최종 배치처럼 재실행하지 않는다.
- `Refine.cs`, `refinements.json`: C04 접근 보수와 소품 높이 정리. `Enrich.cs`, `enrichment.json`: 하부 서랍장과 양면 작업대 추가.
- `layout.json`, `final_instances.json`, `transform_changes.json`: 최종 검수 기준과 실제 배치 기록. 접근점과 씬을 함께 갱신한다.
- `Review.cs`, `Audit.cs`, `Play.cs`, `play_checks.py`, `FinalState.cs`: 검수용 외부 Editor 작업. 게임 Assets에 C#을 생성하지 않는다. Play 검수 시 기존 입력 상태를 복원하고 종료 후 background override를 해제한다.
- `before.unity`, `*_before.json`, `geometry.json`: 최초 보존본. 덮어쓰지 않는다. 기존 B4_FullFloor/ExperimentOperations 전체 Apply와 구형 배치 생성기를 실행하지 않는다.

소방 설비는 구형 12개를 비활성 보관하고 새 벽 부착형 12개로 대체했다. C04 추가 회수 랙 1개는 통행 때문에 비활성화했다. 모든 새 이름은 ASCII다. 기존 305 Light와 B5/게임 코드는 보존했다. 커밋·push는 하지 않았다.
