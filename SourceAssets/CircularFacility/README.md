# 원형 공동 제작 원본 V0.02

작성자 송예찬 · 2026-11-06

사용자 요청에 따라 외부 원형 공동 설계를 대조·수정하고 B5 핵심 구역과 B2 메자닌 검토 공간을 새 Unity 씬에 제작했다. 현재 결과는 Docs/검수/2026-11-06_CircularFacility/검수결과.md를 따른다.

- `source_design.json` / `source_audit.json`: 원본 데이터 스냅샷, 원본 파일 해시·명세 분류·기존 후보 파일 확인.
- `revise_design.py`: 수정 PDF/SVG/JSON 생성. `validated_routes.json`이 있으면 실제 B5 경로를 보존한다. PDF 재생성 뒤 Poppler PNG 렌더·시각 검수가 필요하다. 사용자가 수정한 설계 데이터를 덮어쓸 수 있으므로 자동 재실행하지 않는다.
- `build_geometry.py`: Blender 전용 제작. `--mezz-only`는 메자닌/배관, `--pipes-only`는 배관만 재생성한다. 편집용 메자닌·배관의 `*_Editable.blend`에 개별 부품과 베벨을 보존했다. 기본 실행은 새 CF 모델을 모두 덮어쓰므로 변경 내용을 확인한다.
- `BuildCircular.cs`: 외부 Editor 전용 Import/BuildB5/BuildB2Preview/AddPipework/Validate/DoorValidation/Capture. `BuildB5`와 `BuildB2Preview`는 해당 새 씬을 다시 만들기 때문에 사용자의 후속 편집을 보존하려면 실행 전 비교해야 한다.
- `RefineCircular.cs`: Routes는 실제 충돌 기반 경로와 R1 표식을 갱신한다. Polish는 재질 반사·밝기, Walk는 기존 CharacterController의 계단 이동을 검사한다.
- `finalize_delivery.py`: 보호 파일·원본 보존과 검사 결과를 확인하고 전달 폴더 및 에셋 제작 기록을 갱신한다. 새 검사 후 실행한다.

현재 제작 순서는 Import → BuildB5 → Routes → BuildB2Preview → AddPipework → Polish → Validate/DoorValidation/Walk/Capture다. 완료한 결과를 단순 재개 목적으로 재실행하지 않는다. 이 파일들은 Assets 밖의 제작 도구이며 게임 런타임 코드를 추가하지 않는다.

현재 Unity 시작 씬은 `Level_B5_Circular.unity`, B2 한 공동 검토 씬은 `Level_B2_MezzaninePreview.unity`다. 기존 Stealth 씬들과 원본6씬, 기존 모델·메타를 보존한다. 좌표는 X 동쪽, v 남쪽, Unity Z=-v, 층 루트 Y는 B5 -82/B2 -34m다.

2026-11-06: 구버전 씬은 Stage/Old로 이동했다. BuildCircular의 원본 씬 참조만 이동 경로로 보정했다. 현재 B5 후속 CFD 아트는 SourceAssets/CircularDressing 소유이므로 BuildB5 재실행 시 손실될 수 있다.
