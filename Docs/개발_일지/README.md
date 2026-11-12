# 개발 일지 V0.07

2026-11-12 공개 게시 완료. [오늘 작업 마감·원격 저장 결과](../WorkClose_2026-11-12.md)와 [공개 기록](2026-11-12.md)을 따른다. 다음 작업은 사용자 전체1F 검수와 지정 구역 보수다. 작성자 송예찬.

- [일일개발일지 — B1 실내 재설계와 지상 폐공장 제작](https://songyechan1024.github.io/Kasil_DevLog/posts/after-seconds-b1-redesign-and-abandoned-factory/)
- [데일리 로그 — 책상 위 배치와 폐공장의 흔적](https://songyechan1024.github.io/Kasil_DevLog/posts/daily-log-use-traces-and-texture-scale/)

이전 기록:

2026-11-08 저녁 글 게시 완료: 블로그 `272b353` main 반영과 배포 성공, 두 글 및 이미지5장 HTTP200 확인. 아래의 원고 상태는 작성 당시 기록이다.

- [데일리로그 — 생활층과 실험층을 나누고 나니 필요한 설비가 달라짐](https://songyechan1024.github.io/Kasil_DevLog/posts/daily-log-living-floor-and-experiment-floor/)
- [일일개발일지 — B4 전체 제작과 실험 운용 설비 배치](https://songyechan1024.github.io/Kasil_DevLog/posts/after-seconds-b4-experiment-operations/)

이전 기록:
작업 나열보다 문제를 어떻게 발견하고 해결했는지 기록합니다. 매일의 학습 과정은 공개 「데일리 로그」로, 프로젝트의 구현 문제와 해결 과정은 별도의 기술 글로 작성합니다.

**현재 게시 저장소는 [Kasil_DevLog](https://github.com/SongYeChan1024/Kasil_DevLog)이며 `_posts/YYYY-MM-DD-영문-슬러그.md`에서 관리합니다.** 로컬 저장소는 학원 PC 기준 `C:/Users/503-26/Desktop/Projects/02.Kasil_DevLog`, 집 기준 `C:/GitHubProjects/Kasil_DevLog`입니다. 이 폴더에는 블로그 본문을 복제하지 않고 공개 글 링크와 기존 기록·노션 링크를 보관합니다. 현재 상태는 [2026-11-06 세션 인수인계](../이어하기_2026-11-06.md), 다음 순서는 [회사 작업 목록](../회사_작업목록_2026-11-06.md)에 기록합니다.

- [2026-11-05 일일개발일지 — B5 재검수와 B4 관찰층 제작](https://songyechan1024.github.io/Kasil_DevLog/posts/after-seconds-b4-observation-floor-and-validation/)
- [2026-11-05 데일리로그 — 걸어갈 수 있는 맵과 게임에 쓸 수 있는 맵](https://songyechan1024.github.io/Kasil_DevLog/posts/daily-log-walkable-is-not-finished/)

- [2026-11-04 일일개발일지 — 소품 마감과 6개 층 건축 외형 교체](https://songyechan1024.github.io/Kasil_DevLog/posts/after-seconds-environment-finishing-and-architecture/)
- [2026-11-04 데일리로그 — 텍스처를 바꾸는 것만으로는 부족했음](https://songyechan1024.github.io/Kasil_DevLog/posts/daily-log-visual-quality-and-verification/)

- [2026-11-04 일일개발일지 — B2 배관 연결과 1층 외장 교체](https://songyechan1024.github.io/Kasil_DevLog/posts/after-seconds-b2-pipes-and-1f-facades/)
- [2026-11-04 데일리로그 — 에셋을 쓴 것과 공간을 완성한 것](https://songyechan1024.github.io/Kasil_DevLog/posts/daily-log-assets-and-connections/)

- [2026-10-28 데일리 로그 — 의사코드로 배우는 과정](https://songyechan1024.github.io/Kasil_DevLog/posts/daily-log-learning-through-pseudocode/)
- [2026-10-28 기술 기록 — After Seconds 1인칭 플레이어 컨트롤러](https://songyechan1024.github.io/Kasil_DevLog/posts/after-seconds-first-person-player-controller/)

- [2026-10-26 연구소 시안에서 Unity 계층 분리까지 — 블로그 일일개발일지](https://songyechan1024.github.io/Kasil-portfolio-pages/posts/after-seconds-unity-assembly-setup/) — 오늘 앞선 준비 작업과 집에서 진행한 6계층 asmdef 생성·Define/Simulator 설정을 합친 기록
- [2026-10-26 노션 데일리로그](https://app.notion.com/p/40536532580e81e2ab76fe7ddaa73ee1)

## 기존 저장소 일지

- [2026-10-23 컨셉 확정과 기획서 초안](2026-10-23_컨셉_확정과_기획서_초안.md) — 사후 작성. 플레이어 규칙 두 줄, 웹 프로토타입, 기획서 V0.01, 저장소·CLAUDE.md 세팅, 9장 방 도면(감방·구덩이·압력판, V0.02)
- [2026-10-25 기획서 V0.06과 A·B안 프로토타입](2026-10-25_기획서_V0.06과_AB안_프로토타입.md) — 빈칸 초안, 구글 문서 댓글 반영, A·B안 분리, 지하 층 배치와 세계관, 평면도 10장, 버전 표기, 웹 빌드 V0.01(A·B안 전환·시야 창)

- [2026-10-26 연구소 시안과 Unity 개발 준비](2026-10-26_연구소_시안과_Unity_개발_준비.md) — 전체 건물 시안, 기획서 V0.09, 바르코 후보 6종, 계층 분석·학습 순서, Unity 초기 프로젝트와 집에서 이어하기

## 기존 파일명 (보관)

`YYYY-MM-DD_주제.md`

## 기존 작성 형식 (보관)

```markdown
# YYYY-MM-DD 개발 일지

## 기록 정보

## 오늘의 목표

## 작업 내용

## 발생한 문제

## 원인

## 해결

## 검증

## 다음 작업
```

## 2026-11-08 B5 돔·안내선 작업

- [데일리로그 — 이 공간을 쓰는 사람이라면 어떻게 움직일까](https://songyechan1024.github.io/Kasil_DevLog/posts/daily-log-spaces-that-explain-their-purpose/)
- [일일개발일지 — B5 돔 구조·장비 보강과 복도 안내선 정리](https://songyechan1024.github.io/Kasil_DevLog/posts/after-seconds-b5-domes-and-corridor-guidance/)
- [비공개 프로젝트 인수인계](../작업마감_2026-11-08.md). 본문은 블로그에 보관한다. 작성자 송예찬.


## 2026-11-08 저녁 B4·영문 이름 작업 — 로컬 원고

블로그 `Kasil_DevLog`의 `docs/2026-11-08-b4-experiment-operations` 브랜치에 작성했다. 아래 두 글은 아직 커밋·push·게시하지 않았다. 새벽의 기존 공개 글을 덮어쓰지 않는다.

- 데일리로그: `_posts/2026-11-08-daily-log-living-floor-and-experiment-floor.md` — 생활층/실험층 구분, 세 역할의 동선과 설비 접근, 영문 이름 규칙.
- 일일개발일지: `_posts/2026-11-08-after-seconds-b4-experiment-operations.md` — B5 조명, B4 전체 제작·실험 설비, 검수와 이름 전환. 스크린샷5장.
- [저녁 인수인계](../WorkClose_2026-11-08_Evening.md). 본문은 블로그에만 보관한다.

- V0.05 (2026-11-08): B4 작업과 영문 이름 변경을 담은 저녁 원고 위치·로컬 상태 기록. 송예찬.

- V0.06 (2026-11-08): 저녁 글2편 공개와 배포 검증 링크. 송예찬.
