# B2 공동 설비·상부 연결 V0.01

작성자 송예찬 · 2026-11-10

사용자 요청에 따라 B2의 빈 내부를 용도별 설비로 보강하고 공동 메자닌을 터널 상부 정비 경로에 직접 연결했다. 현재 씬은 `Assets/Afrer_Seconds/01.Scenes/Stage/Level_B2_Circular.unity`다.

`layout.json`은 실제 적용한 97개 추가 설비와 6개 터널의 연결 끝을 기록한다. E01·E02·W02의 3.6m 원형 데크를 만들고 기존 C02 U형 메자닌에 T01 접속부를 냈다. T01·T11·T12·T14·T15·T16 총 7개 끝이 연결됐다. 터널 2.42m에서 공동 3.60m까지 계단으로 이어진다. 연결하지 않은 끝의 기존 진입 방식과 다른 통로는 유지한다.

`build.py`는 베벨을 적용한 철골·그레이팅·계단·난간과 분리된 연속 충돌, 신규 공정 장비 5종 및 LOD를 만든다. `connections.py`는 터널 헤더를 공동 공정 배관에 잇는다. Blender 원본과 64개 FBX/LOD의 명세는 이 폴더와 `models.json`에 있다. 기존 프랍을 재사용할 때 실제 씬 모델의 재질·맞춤 크기·LOD를 유지했다. Unity 에셋은 Props/B2 또는 Environment/B2에 분류했다.

`Apply.Run`은 최초 적용 기록이며 **현재 씬에 다시 실행하지 않는다**. `Repair`는 별도 기록된 후속 보수다. `plan.py`의 초안 배치를 다시 생성하면 최종 회전 보수가 사라질 수 있으므로 현재 기준은 `layout.json`이다. `routes.json`은 생성된 동선과 검수용 기존 C02 연결 동선을 포함한다.

`Review`, `TunnelReview`, `Access`, `Play`, `Audit`가 이동·접근·기존 보존·외형을 검사한다. 테스트는 외부 Editor 도구이며 Assets에 게임 코드를 추가하지 않았다. 실제 입력 장치를 비활성화하지 않으며 임시 Player 이동은 복구한다. `Finish`는 정적 반사와 가림 정보를 갱신한다. `record.py`는 출처 명세와 실배치 도면을 기록한다.

현재 결과는 [검수 기록](../../Docs/Review/2026-11-10_B2_DomeNetwork/Review.md), [변경 전후 화면](../../Docs/Review/2026-11-10_B2_DomeNetwork/review.html), [도면](../../Docs/도면/Decision/원형공동/B2_배관통로/B2_공동상부연결.png)을 따른다. 최종 외형/게임 난이도는 사용자 검수 대상이며 정적 설비의 작동·AI 감시는 이번 범위가 아니다.
