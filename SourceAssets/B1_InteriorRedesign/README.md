# B1 전체 실내 재설계 제작 원본 V0.02

2026-11-12 후속: 최신 상판 기물은 [B1_DeskPropRefinement](../B1_DeskPropRefinement/README.md)가 우선한다. 이 폴더는 실내 구조와 가구 배치의 선행 제작 기록이며, 별도 녹음기10개의 최신 위치와51개 시각 모델은 후속 plan.json 및 Decision 현재 배치를 따른다. 이전 report.py·Apply를 현재 씬에 다시 적용하지 않는다.

이전 단계 기록:

작성자 송예찬 · 2026-11-12

현재 저장된 B1의 최신 실내 제작 원본이다. [검수](../../Docs/Review/2026-11-12_B1_Interior/Review.md) · [화면](../../Docs/Review/2026-11-12_B1_Interior/review.html).

**Apply·plan·models를 사용자 후속 편집 뒤 일괄 재실행하지 않는다.** 이 도구들은 이번 제작의 재현 기록이다. 이전 B1_FullFloor와 B1_StaffDataRevision의 Apply도 현재 씬에 실행하지 않는다. 다음은 사용자 전체 외형·공간 검수 후 지정 범위 보수다.

- plan.py / layout.json: 실제203배치,17체류 구획,103벽 구간,21부분 천장, 기존 광원44개 재배치. 이전 StaffData198배치를 참조해 만든 이번 설계 원본.
- models.py / models_environment.json: Blender 베벨·UV·삼각화, 새 BL_RI_* FBX13개. 기존 B1 재질·텍스처 재사용. structural_colliders.json은 벽·천장·기둥 충돌체.
- Apply.cs: Unity 네이티브 적용·Undo·저장, 현재 배치/보존 감사. 게임 Assets 안에 C#을 추가하지 않았다.
- Inspect.cs / before_scene.json / protected_before.json: 작업 전 기준. 중복 이름 형제도 개별 Transform 값으로 대조하며 원본을 다시 수집해 덮어쓰지 않는다.
- Review.cs / PublicReview.cs: 실제 Collider와 CharacterController 통행. 후자는 체류 구획을 제외한 공용 동선만 검사한다.
- Visual.cs: 눈높이·침실 노출/회의석 화면 시야·가림 사용/미사용 비교.
- Play.cs / run_play.py: 실제 키보드 입력·프레임 진행·새 로그 확인. 임시 설정 복구 후 Play 종료.
- geometry.py: 기존 읽기 전용 Export/분석기를 사용한 전체 B1 깊이 충돌 검사. 정밀도와 한계는 보고서를 따른다.
- Finish.cs: 반사/가림 갱신과 편집 상태 마감. maps.py / report.py는 저장 결과를 바탕으로 로컬 검수 문서를 만든다.

이전 before.unity는 이번 PC의 복구용 사본으로 Git에서 제외했다. Git 기준 시작 커밋은 f663ea07010dc1f40698a55431f9db9ccf286e12다. 원본 메시/GUID·다른 층·Player·Animator·게임 코드 보존, 커밋·push 미실시.

- V0.02 (2026-11-12): 후속 데스크·기물 원본과 녹음기 위치 기준 연결. 송예찬.
