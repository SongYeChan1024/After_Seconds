# After Seconds — 2026-11-08 저녁 작업 마감 V0.02

작성자 송예찬 · 2026-11-08

사용자가 오늘 작업 종료와 데일리로그·일일개발일지 작성을 요청했고, 이어서 프로젝트 내부 이름을 간결한 영어로 바꾸도록 요청했다. 후속 승인에 따라 제작 커밋 `c47aade`와 블로그 `272b353`를 각각 원격 main에 push했다. 같은 날짜 새벽의 B5 마감·공개 기록과 구분한다. 이 문서를 포함한 후속 마감 기록까지 원격 main에서 받는다.

## 현재 결과

- B5 일반 돔12곳에 천장등80개, 복도 끝13개 광원 보강. 기존 등기구98개를 리브 사이로 정렬하고 외형이 없던 광원16개에 등기구 연결. 새 광원93개, 씬 Light340개. 기존247 Light 설정 보존.
- B4 전체13돔·3이동 코어·22복도 첫 외형과 실험 운용 설비 완료. 중앙2.5m 관측 데크, VA/VB17m 계단 외형. B5는 생활·격리/기본 관리, B4는 정밀 측정·발달·강화 연구층이다.
- 실험체의 인계·대기·센서 준비·시험·회복, 경비 통제, 연구원 교정·관측·판독·기록·회수로 공간을 구분했다. 설비 보강 단계 새 모델35종/사용34종, 설비210개+의자27개, 정적 화면18장+라벨2장, 실제 등기구와 연결한 광원44개.
- 한글 오브젝트 이름1,778개와 특수기호가 있던 복도 이름21개를 영어로 정리했다. 전체13씬18,776개 오브젝트 이름이 ASCII 범위다. 파일·폴더 경로는 이미 영어였고 이동하지 않았다.
- 현재 이름: `B4_ResearchFloor_V0.03` / `B4_ExperimentEquipment` / `B4_W01_Equipment` / `B4_W01_ObservationBooth_01`. B5 예시: `C01_CeilingLight_01`. 새 작업도 영어 이름을 따른다.

## 검증과 저장 상태

- 설비 단계: 기존1,317 Transform 위치·회전·크기·활성 유지, Controller320/320경로 통과, 실제 Play16구역 새 게임 경고·오류0.
- 이름 단계: 직렬화 오브젝트/컴포넌트22,473개 전후 비교에서 이름 외 차이0. 기존6,541파일 중 대상 B4/B5 씬2개만 변경하고6,539개 해시 동일. GUID·메시·재질·충돌·Light·런타임 C#·Animator 보존.
- 한글 이름 변경 뒤 B4와 B5에서 각각8초간 실제 입력 이동/프레임 진행 확인, 새 게임 경고·오류0. 마지막 복도21개 기호 정리 후에도 전체 직렬화 보존 비교 통과.
- Unity는 `Level_B4_Circular` 저장된 편집 모드. 루트 `B4_ResearchFloor_V0.03`, 플레이어 `(-17.63,-65.36,10.58)`, Y각도120.96. 백그라운드 실행false, 카메라 가림true. B4 Light305·Renderer1,136·Collider418개.
- 화면·설비는 정적 아트다. 실제 실험/강화 수치·약물·모니터 갱신·문/승강기·AI·층간 씬 연결은 구현 완료가 아니다. 출시 빌드 성능·전체 아트 최종 판정도 남는다.

## 다음 회사 작업 순서

1. 회사에서 `git pull --ff-only`하고 이 문서와 실제 코드를 대조한다. 제작 기준 커밋은 `c47aade`이며 후속 마감 문서까지 포함한 최신 main을 받는다.
2. B4 전체를 플레이어 시야로 검수한다. 각 돔의 목적, 장비 사용면 접근, 반복 프랍, 베벨/라벨/화면, 시야·밝기를 먼저 확인한다.
3. 지적한 설비와 배치만 보수한다. 승인된 B5 배치와 기존 Light 설정을 보존한다. 이동 안내선은 복도 전용으로 유지한다.
4. 사용자 외형 검수 후 B4/B5 전체 조명·색감·성능 마감을 진행한다. 런타임 게임 C#/Animator 구현은 별도 작업이다.
5. 과거 한글 이름을 쓰는 일회성 생성/Apply 스크립트를 최신 씬에 그대로 재실행하지 않는다. 영어 기준과 최신 검수 도구를 적용한다.

## 블로그 게시 결과

저장소 `C:/GitHubProjects/Kasil_DevLog`, 브랜치 `docs/2026-11-08-b4-experiment-operations`.

- `_posts/2026-11-08-daily-log-living-floor-and-experiment-floor.md` — 11월8일23:10, 생활층/실험층 역할과 설비 접근, 이름 규칙.
- `_posts/2026-11-08-after-seconds-b4-experiment-operations.md` — 11월8일23:11, B5 조명·B4 전체/설비 제작·검수·영문 이름.
- `assets/img/uploads/2026-11-08-b4-*.png`5장. 동일 날짜 새벽 글은 그대로 보존한다.
- 로컬 production Jekyll 빌드 성공. 생성된 두 글의 링크 대상과 스크린샷5장 존재 확인, 깨진 로컬 링크0. 검증 출력은 블로그 `_site-review`이며 원격 게시 결과가 아니다.
- 본문은 한국어, 프로젝트 내부 식별 이름은 영어다. 원격 커밋과 실제 공개 페이지를 각각 확인했다.

## 검수 자료

- [B5 조명](검수/2026-11-08_B5_CeilingLighting/검수결과.md)
- [B4 전체 공간](검수/2026-11-08_B4_FullFloor/review.html)
- [B4 실험 설비](검수/2026-11-08_B4_ExperimentOperations/review.html)
- [영문 이름·참조 보존](검수/2026-11-08_EnglishNaming/review.md)

- V0.01 (2026-11-08): 저녁 작업·영문 이름 전환·블로그 원고와 다음 검수 인수인계. 송예찬.


## 원격 확인

- After Seconds 제작: [`c47aade`](https://github.com/SongYeChan1024/After_Seconds/commit/c47aadee49688e67e3a4d11138a7c0e31d8b098a).
- 블로그: [`272b353`](https://github.com/SongYeChan1024/Kasil_DevLog/commit/272b353aca1d1bb6d24aa9400692c05684e3a397).
- [Build and Deploy 성공](https://github.com/SongYeChan1024/Kasil_DevLog/actions/runs/42490413170). 실제 글2편과 이미지5장 HTTP200.
- [데일리로그](https://songyechan1024.github.io/Kasil_DevLog/posts/daily-log-living-floor-and-experiment-floor/) · [일일개발일지](https://songyechan1024.github.io/Kasil_DevLog/posts/after-seconds-b4-experiment-operations/).

- V0.02 (2026-11-08): 사용자 승인에 따른 main push와 블로그 배포·실제 공개 확인. 송예찬.
