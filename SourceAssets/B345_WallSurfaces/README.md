# 벽과 시료 상자 생활 흔적 제작 원본 V0.02

후속 최신은 `SourceAssets/B345_WideInterior`와 [터널·돔 검수](../../Docs/검수/2026-11-06_B345_WideInterior/검수결과.md)다. 현재 모델은 WC/WA이며, 상자는 SW 생활 흔적 마감이다. 이 폴더의 이전 Apply를 현재 확장 씬에 덮어 실행하지 않는다.

아래 날짜별 문단은 이전 작업 이력이다.

작성자 송예찬 · 2026-11-06

사용자의 ‘패턴’은 먼지·닦인 자국·손때·마모다. 색 띠나 점검판 문양을 새로 넣는 의미가 아니다. 최신 실내 기준은 Reference_004.jpg이며 후속 곡면 실내 단계의 사진을 우선한다.

- build_walls.py: 기존 벽4,174파트의 형상·베벨을 그대로 사용하고 UV와 생활 흔적 재질을 분리한다.4개 재질군, 각4개 변형을2048 PBR 아틀라스로 묶었다. 바닥 먼지는 아래 패널에만 적용하며 좌우 방향도 섞는다.
- rebake_textures.py는 맵만 다시 만든다. 벽 FBX는 기존 건축에서 분리한 시각용 레이어이며 Collider가 없다. 기존 벽 배치·삼각형 수를 비교했다.
- bake_case_wear.py: 원래 VARCO 상자 UV/노멀/베벨을 보존해6가지 사용 흔적을 Blender에서 베이크한다. 추가 장식 무늬와 규칙적인 색 띠를 제거하고 회백색 도장으로 맞췄다.
- ApplySurfaces.Cases는309개 상자에 고정 시드의 불규칙 마감을 부여한다. 1.05m 이내 가까운 상자는 같은 마감을 피한다. Transform·Collider·LOD는 바꾸지 않는다.
- 새 프리팹은 Props/Common/SW_Case_*다. 이전 SD 색 무늬 원본을 보존하지만 현재 씬은 SW 마감을 쓴다.
- preview_sources.py는 벽 텍스처를 Blender 소스에 패킹하고 상자 비교 이미지를 만든다. 원본 Blender 파일은 WS_*_Walls.blend와 SW_CaseWear.blend다.
- 최종 사진·검증: [곡면 실내와 생활 흔적 검수](../../Docs/검수/2026-11-06_B345_ArchedInterior/검수결과.md). 이 단계의 초기 After 이미지는 곡면·중성 조명 적용 전 기록이다.
