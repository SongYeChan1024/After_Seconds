# After Seconds 11월 13일 작업 마감과 이어하기 V0.01

작성자 송예찬 · 2026-11-13

사용자 요청으로 오늘의 1F 폐공장 보수 전체를 커밋·push했다. 구현 커밋은 `4f4aa61bebbd7fb2a978b9e2c71f6ff25ecb55ed`이며 원격 main과 SHA 일치를 확인했다. 이 문서는 그 뒤의 마감 기록이다. 각 제작 단계 문서에 남은 ‘커밋/push 미실시’는 해당 단계 당시 상태를 뜻한다.

## 이어서 시작할 때

1. 로컬 변경을 먼저 확인한 뒤 `git pull --ff-only`로 원격 main을 받는다. 미보존 작업이 있으면 강제 reset/clean하지 않는다.
2. Unity **6000.4.0f1**로 `Unity/After_Seconds_Build_V0.01`을 연다. 자동 버전 업그레이드를 하지 않는다.
3. 최신 저장 씬은 `Assets/Afrer_Seconds/01.Scenes/Stage/Level_1F_Factory.unity`다. [최신 프랍 검수](Review/2026-11-13_1F_PropRefinement/Review.md)와 [전후 화면](Review/2026-11-13_1F_PropRefinement/review.html)을 함께 본다.
4. 사용자가 수용한 석양·태양·빛번짐을 유지하고 필요한 구역을 국소 보수한다. 첫 Apply/Before/Import와 이전 전체 제작기를 재실행하면 후속 편집을 덮어쓸 수 있다.
5. 승강기·문·엔딩 동작을 구현할 때는 [가동 부품 연결 안내](../SourceAssets/F1_RoofLiftWilderness/README.md)를 먼저 확인한다. 구조와 외형 제작을 운행 구현 완료로 해석하지 않는다.

## 오늘 저장한 작업

| 범위 | 내용과 근거 |
| --- | --- |
| 천장·창 | 코어 천장의 반복 틈 보수. 금속 지붕 9곳과 콘크리트 천장 2곳의 재질별 파손. 수정 벽 14개에서 창 개구부 비율 44.8%→19.8%. [지붕·창 검수](Review/2026-11-13_1F_WindowRoofDamage/Review.md) |
| 승강기·계단 | 고정 승강로와 객실·문·균형추·도르래·로프 분리, 레일·권상기·완충 장치 구성. VB 도착 방화문과 도착참·18m 계단 연결. [구조 검수](Review/2026-11-13_1F_RoofLiftWilderness/Review.md) |
| 벽·아이비·실내 | 벽돌 패턴을 금속 외장으로 교체. 판 이음과 국소 녹·빗물·하단 오염, 설비 연결·바닥 마모·아이비·낙엽·지붕 잔해 보강. [표면](Review/2026-11-13_1F_SurfaceDetail/Review.md) · [근접 디테일](Review/2026-11-13_1F_DetailPass/Review.md) · [환경 연결](Review/2026-11-13_1F_EnvironmentalStory/Review.md) |
| 석양 | HDRI 없는 절차적 하늘과 낮은 서쪽 태양. 태양 확대·광륜·넓은 빛번짐·Bloom 적용 후 사용자 수용. [최종 태양 검수](Review/2026-11-13_1F_FirstLight/Review.md) |
| 황야 | 바위·마른 풀·관목·자갈과 4개 지면 레이어, 출구 접근부와 낮게 겹친 원경 보수. 1F Cinemachine 렌즈 Far Clip 4,500m로 원경 표시 유지. [황야 검수](Review/2026-11-13_1F_WildernessDetail/Review.md) |
| 마지막 프랍 | 릴 3개·의자 5개·카트·지게차·프레스 각 1개, 총 5종·11배치의 곡면·기계 연결·재질별 마모 보수. 새 5FBX·17재질·3단계 LOD. [프랍 검수](Review/2026-11-13_1F_PropRefinement/Review.md) |

최신 제작 원본은 `SourceAssets/F1_PropRefinement/`, 황야는 `F1_WildernessDetail/`, 수용한 태양은 `F1_FirstLight/`다. 이전 단계의 원본도 함께 보관했으며 현재 씬을 덮어쓰는 재생성 용도로 자동 실행하지 않는다.

## 검수와 커밋 범위

- 제작 단계의 최종 프랍 검수: 통행 75/75, 실제 Play 3시점·728프레임 진행, 새 경고·오류 0. 누락 메시·재질·스크립트와 셰이더 오류 0, 대상 LOD 11/11 연결 확인.
- 황야 제작 단계: 출구부터 약 585m 구간 왕복 2/2 통과, 폭 879표본 막힘 0. 동일 치수의 임시 CharacterController 검사이며 엔딩 기능 실행 검사가 아니다.
- 최종 씬 기록은 Transform 4,834개·Collider 165개. 마지막 프랍 교체에서 기존 배치와 충돌체를 보존하고 반사 프로브 8개를 갱신했다.
- 이번 마감에서는 저장된 파일을 검사했다. JSON 158개 구문 검사 통과, 새 Unity 에셋 .meta 누락·고아 0, 변경된 기존 GUID 0, 새 GUID 충돌 0. 게임 C#·Animator·프리팹·패키지·프로젝트 설정의 변경은 없다.
- 구현 커밋은 총 1,053파일이며 제작 원본·검수·Unity 에셋과 .meta를 포함한다. 커밋 대상 중 100MiB 이상 단일 파일은 없다. 가장 큰 파일은 약 35.97MiB의 아이비 FBX다.
- 문서·제작 소스·셰이더의 Git 공백 검사 통과. Unity 직렬화 파일의 빈 필드 뒤 공백은 에디터 출력 그대로 보존했다.
- `Docs/Reference/1F/DiscordSetup.exe`와 `Install VARCOSound 1.2.1.exe`는 작업에 무관한 로컬 설치 프로그램으로 커밋에서 제외했다. 파일은 삭제하지 않았고 두 경로를 `.gitignore`에 기록했다.

승강기 운행·문 연동·층간 전환·엔딩은 사용자 후속 구현 범위다. 실제 배포 빌드의 프레임 시간과 메모리 측정도 별도로 남는다. 이번 파일 검사에서 Unity를 다시 열거나 제작기·Play 검사를 재실행하지 않았다.

## 공개 작업 기록

- [11월13일 일일개발일지](https://songyechan1024.github.io/Kasil_DevLog/posts/after-seconds-factory-detail-and-sunset-wilderness/)
- [11월13일 데일리 로그](https://songyechan1024.github.io/Kasil_DevLog/posts/daily-log-material-damage-and-first-light/)
- [261113_NCAI 수업메모](https://songyechan1024.github.io/Kasil_DevLog/posts/261113_ncai/)

블로그 `8617ba3`에 일지 2편·이미지 8장과 NCAI 정리를 반영했고, `3f40929`에 별도 수업용 Unity 프로젝트의 생명주기·컴포넌트 탐색 실습을 추가했다. 두 작업 모두 자동 검사·Jekyll 빌드·링크 검사·Pages 배포 성공과 공개 페이지 반영을 확인했다. 수업 프로젝트의 코드를 After Seconds에 옮기지 않았다.

## 변경 기록

- V0.01 (2026-11-13): 오늘 구현의 원격 저장, 검수·제외 파일과 후속 구현 범위, 공개 일지 링크를 기록함. 송예찬.
