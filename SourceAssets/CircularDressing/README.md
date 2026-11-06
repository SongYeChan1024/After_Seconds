# 프랍·환경 기준 구간 제작 V0.01

작성자 송예찬 · 2026-11-06

엑셀 원본145종을 유지하고 환경32종과 바닥형 보급장2종을 더했다. 신규 제작은 B5 C01·T01 기준 구간이며 전층 완성 목록이 아니다. 최신 전달 엑셀은 Docs/도면/원형공동/AfterSeconds_프랍환경_제작목록.xlsx다.

- production_plan.json: 환경 품목과 실제42배치의 공통 입력. prepare_catalog.py는 이를 생성하므로 사용자 수정 후 자동 재실행하지 않는다.
- workbook.mjs: Artifact Tool로 기존 엑셀을 확장한다. --edit일 때 전달본을 덮어쓴다. inspect_inputs.py는 시작점 원본·보호 해시를 저장하므로 재실행 금지.
- build_environment.py / build_fallback.py: Blender 환경 모듈11개 및 직접 제작 보급장. .blend에 편집용 베벨 보존. 기존 모델과 다른 CFD 접두사다.
- prepare_varco.py / varco_record.json: 지정 V0.03 flow에서 세탁물함·응급 보급장 생성/리메시, 실제 비례 유지 치수 정규화, 예각1mm 베벨, 3단계LOD, PBR 분리. 급식 전달 캐비닛은 3D 생성 실패로 Blender 제작.
- ApplyCircularDressing.cs: Assets 밖 Editor 전용 제작기. ImportEnvironment/ImportProps, Apply, Capture. Apply는 B5_Art_C01_T01만 갱신하며 기존 T01 임시 조명을 끈다. 사용자 후속 위치 수정 여부를 확인해야 한다.
- ValidateDressing.cs: 경로690표본·프랍간섭·메시·재질·LOD 검사 및 반사2개 재베이크. Play/FPS·적 시야 검증은 포함하지 않는다.
- SceneArchive.cs: 이번에 구버전7개를 Stage/Old로 이동한 기록. 기존 보관3개 포함 총10개. GUID와 내용을 보존하며 빌드 설정 활성 여부는 유지했다.
- finish.py: 보호 검증·문서 버전·출처 기록. 한 번 완료한 문서 버전 갱신을 반복하지 않는다.

현재 씬은 Level_B5_Circular와 Level_B2_MezzaninePreview다. 게임 런타임 C#·AI·문/스위치 기능은 사용자 직접 작성 범위다. 원본 외부 엑셀은 보존했다.
