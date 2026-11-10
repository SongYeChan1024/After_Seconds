# B2 복층 정비 통로와 산업 조명 V0.01

작성자 송예찬 · 2026-11-10

`Level_B2_Circular.unity`의19개 통로에 하부 보행과 상부 크라우칭 정비 경로를 추가했다. T04·T06은 짧은 단층 접속부다. 공동/코어 평면과 C02의 기존3.6m 메자닌은 보존한다. Player 조작감은 사용자가 확인했고 이번 작업은 게임 코드·Animator를 바꾸지 않는다.

`Plan.md`와 `layout.json`이 단면/배치 기준이다. `build.py`는 높이2.42m 그레이팅·양 끝13단 계단·실제 체결부·베벨·별도 충돌·거리LOD, 기기 연결29배치를 만든다. `services.py`는 상부 공급/회수 배관·보조선·가스켓 플랜지·차단 밸브·압력계·지지대와 원형 보호망등/금속 갓 펜던트를 만든다. `.blend`가 제작 원본이고 모델은 Unity `05.Model/Environment/B2` 및 `Props/B2`의 `BD_` 에셋이다.

`Apply.Run`, `Services.Run`은 이미 실행한 단계별 기록이다. 현재 씬에 다시 실행하지 않는다. 최신 조명은 `B2_MachineryNetwork/B2_DetailPass/B2_ProcessLighting`이다. 초기 사각 붉은 등 배치는 비활성 보존되어 있다. `LightingBalance`는 기존69개 통로 등 중39개를 곡면 법선에 맞춰 상부로 이동한 최종 보수다. 활성 광원158개에는 약한 반사광12개가 포함되며 흰 직접 광원은0개다.

Unity 변경은 Editor API로 적용했다. `Import`는 모델 반입/재질 연결, `Finish`는LOD19그룹·반사37개·가림 베이크를 처리한다. `Review.Routes`는 상하부4,910표본 및 CharacterController76회 왕복, `Access.Access`는 기존186개 설비/문 접근, `Play`는 현재 PlayerMotor의 실제 입력과 앉기/일어서기 거부를 검증한다. 실제 Mouse/Keyboard를 비활성화하지 않는다. `before.json`은 기존2,138 Transform의 기준이며 `Audit`로 누락/이동을 검사한다.

현재 결과와 이미지, 실행 결과 JSON은 [검수 폴더](../../Docs/Review/2026-11-10_B2_DetailMezzanine/)에 있다. [복층 도면](../../Docs/도면/Decision/원형공동/B2_배관통로/B2_복층통로.png)은 Unity 좌표에 기반하며 게임 내 안내 UI가 아니다. `diagram.py`로 재생성한다. 문/승강기·AI·설비 작동·스위치와 최종 FPS 성능 목표 검증은 별도 범위다.
