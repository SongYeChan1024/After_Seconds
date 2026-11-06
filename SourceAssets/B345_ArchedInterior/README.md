# 레퍼런스 4번 곡면 실내 제작 원본 V0.02

후속 최신은 `SourceAssets/B345_WideInterior`와 [터널·돔 검수](../../Docs/검수/2026-11-06_B345_WideInterior/검수결과.md)다. 현재 모델은 WC/WA이며, 상자는 SW 생활 흔적 마감이다. 이 폴더의 이전 Apply를 현재 확장 씬에 덮어 실행하지 않는다.

아래 날짜별 문단은 이전 작업 이력이다.

작성자 송예찬 · 2026-11-06

`Docs/Reference/Reference_004.jpg`가 사용자가 지정한 실내 형태·색감 기준이다. 벽에서 천장까지 둥글게 이어지는 마감, 통로를 감싸는 아치 프레임, 회백색 도장과 따뜻한 금속 악센트를 적용한다. 눈부신 전체 노출 대신 확산등과 중성 주변광으로 형태를 읽게 한다.

- build_arches.py: 기존 도면 좌표에 곡면·아치·확산등 외형 제작. B5/B4/B3 각23개 아치,14/16/15구역 곡면. 편집 원본의 베벨 유지. 새 FBX는 Environment 층 폴더에 저장한다.
- excluded_arches.json: 기존 시야 차단벽과 겹친 S_Arch_05를 층마다 제외한다. blocked_arches.json은 Preflight의 최신 검사 결과이며 지속 제외 목록과 구분한다.
- 아치 발/몸통 충돌은 외형과 맞춰 각각 분리했다. 발의 벽면 기준 돌출은 약0.30m 이내이며 기존 도면의 벽을 따라 걷는 경로를 통과한다.
- ApplyArches.Preflight는 원래 Collider 간섭과 URP 후처리 연결을 조사한다. Apply는 새 레이어·재질·조명·전용 VolumeProfile을 생성한다. Refine은 최종 받침 치수와 Unlit 확산판을 반영한다. 완료 씬에는 Apply를 재실행하지 않는다.
- ArchReview/ValidateArches/ArchWalk/ArchAudit는 외부 Editor 검수 도구다. 게임 코드가 아니다. ArchAudit의 결과는 preservation.json이다.
- 실제 상태와 사진은 [검수결과](../../Docs/검수/2026-11-06_B345_ArchedInterior/검수결과.md)를 따른다. 구조·베벨 원본은 AR_B5/B4/B3_Interior.blend다.
