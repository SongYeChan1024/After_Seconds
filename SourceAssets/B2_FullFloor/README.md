# B2 전체 연결 제작 원본 V0.01

작성자 송예찬 · 2026-11-09

현재 씬은 Level_B2_Circular.unity. 기존 B2_C02_CoolingSector와 신규 B2_MachineryNetwork를 함께 사용한다. 공동12·코어3·통로21의 연결/정적 외형 1차를 적용했고 사용자 아트 검수가 다음이다.

layout.json과 Docs/Review/2026-11-09_B2_FullFloor/Review.md를 먼저 읽는다. Apply.cs, Repair.cs, Safety, LodApply, Probes는 일회성 적용 도구다. 현재 씬에 전체 적용을 다시 실행하지 않는다. 부분 보수는 최신 저장 씬과 실제 Transform을 기준으로 한다.

architecture.py/common.py는 원형 통로와 공동, equipment.py는 베벨을 포함한 전용 기계 설비6종을 제작한다. Blender 원본과 생성 전 GLB를 보존한다. models.json과 Equipment/models.json을 함께 참조한다. LOD는 근접 원본을 보존한 거리별 파생 모델이다.

Play.cs/Look.cs는 검수용 외부 도구다. Mouse/Keyboard를 비활성화하지 않는다. Play 종료 후 Restore를 실행하고 마우스/키보드 활성 및 runInBackground 복원을 확인한다. 게임 내부 C#/Animator는 사용자가 작성한다.
