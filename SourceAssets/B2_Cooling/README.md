# B2 냉각 공동 제작 원본 V0.01

작성: 송예찬 · 2026-11-09

최신 씬 `Level_B2_Circular.unity`의 C02 대표 구역 제작 기록이다. [검수/다음 작업](../../Docs/Review/2026-11-09_B2_Cooling/Review.md)을 먼저 읽는다. **Apply.Run은 최초 생성용이며 현재 씬에 재실행하지 않는다.** 기존 프리뷰는 보존했다. 전체 B2 미완성, 게임 C#/Animator 변경 없음.

- `source_design.json`, `workbook_B2.json`: Decision 도면과 엑셀 B2 행 조사 사본.
- `Plan.md`, `doors.json`, `final_layout.json`: 이번 범위·문 연결 각도·최종 실제 배치. 마지막 파일을 현재 배치 기준으로 사용한다.
- `build.py`, `props.py`, `refine_geometry.py`, `safety.py`, `.blend`: 치수/베벨을 가진 Blender 편집 원본. 최신 배관은 refine_geometry에 사용된 build.py와 common.py의 둥근 연결 처리 기준이다.
- `textures.py`, `adapt_tools.py`: 철재 표면과 실제 읽을 수 있는 정비/계기/안전 표기.
- `Apply.cs`, `Finish.cs`, `Repair.cs`: Assets 밖의 외부 Unity 제작/검수 도구. 런타임 컴포넌트가 아니다. 재질 저장은 이번 작업 에셋에 한정한다.
- `lod*`, `Lod*`: 원거리 메시 14개/9그룹. 재생성 시 `lods.py`의 퇴화 면 제거를 유지한다. adapt_tools는 초기 복사용이므로 수정된 도구 위에 다시 실행하지 않는다.
- `Review.cs`, `Access.cs`, `Play.cs`, `Look.cs`: 통행·접근·실제 입력 검사. Mouse/Keyboard DisableDevice 호출 금지. 임시 PlayerLook/focus 설정은 finally/종료 콜백에서 복구한다.
- `protected_before.json`, `final_state.json`: 사용자 코드/기존 씬 보존 및 최종 상태.

다음 범위는 사용자 C02 검수와 VL/T01 연결 제작이다. C02 문은 임시 닫힌 정적 외형이며 나머지 공간은 생성하지 않았다. 새 씬의 시작점은 중앙 남측이며 양쪽 계단을 통해 상부를 돌 수 있다.
