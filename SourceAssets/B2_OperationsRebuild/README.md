# B2 설비 운영 동선 제작 원본 V0.01

작성자 송예찬 · 2026-11-10

사용자 승인 후 B2 전체12공동에 적용했다. `plan.json`은 실제186배치·4부분 데크·계단·점검 경로, `unity_as_built.json`은 저장된 Unity 위치다. `build.py`와 `bench.py`는 Blender 베벨 원본과38개 FBX/LOD/충돌을 생성한다. 기존 VARCO/Blender 프랍은 씬의 보수된 재질·LOD·맞춤 충돌을 재사용했다. 기존 정비대에서 부품 트레이를 비운 변형1종을 만들어6곳에 적용했고, 모터를0.65배 크기로 테이블 상면0.985m에 맞췄다. 신규 VARCO 생성은 추가하지 않았다.

`Apply.C02/Remaining`은 최초 적용 도구이며 현재 씬에 재실행하지 않는다. 기존 설비·데크는 비활성 보존했다. `Repair.Placements`는 현행 plan에 맞춘 범위 내 보수다. 상부 발판의 삼각형은 닫힌 바닥 충돌, 계단은 연속 경사 충돌이고 시각 그레이팅과 분리된다. 그레이팅 바닥 충돌은 향후 AI 감지용 불투명 면으로 그대로 쓰지 않는다.

`Audit`는 하부 연결/조작면·Controller·상부 왕복·렌더, `TunnelReview`는 기존19복층 통로, `Play`는 실제 플레이어 입력6구간, `Final`은 원본 보존/참조를 검사한다. C# 도구는 Assets 밖에서 일시 실행하며 게임 로직을 추가하지 않는다. 실제 Mouse/Keyboard 장치를 비활성화하지 않는다.

`Finish.Reflections/Occlusion/Complete`로 배치 이후 반사·가림을 갱신했다. `record.py`는 모든 검사가 통과한 뒤 출처·도면·검수 문서를 기록한다. 빌드/배치 재실행 전 현행 사용자 수정을 반드시 대조한다.

[검수](../../Docs/Review/2026-11-10_B2_Operations/Review.md) · [전후 화면](../../Docs/Review/2026-11-10_B2_Operations/review.html)

별도 `_LOD1.fbx`의 Unity 자동 LOD 이름 경고는 남아 있다. 씬의 명시적 LODGroup으로 연결하며 최종 참조 검사를 통과했다. 내부 노드 이름만 바꾸는 시도는 효과가 없어 원복했다. 파일 이름과 `.meta` GUID는 보존한다.

## 변경 기록

- V0.01: 12공동 운영 배치, 계단 참/난간 보수, 근접 접근과 Play 검증. 송예찬.
