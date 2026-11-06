# B5·B4 실험실 마감 제작 원본 V0.02

작성자 송예찬 · 2026-11-06

Blender 5.2.2 LTS에서 만든 문틀·좌우 슬라이딩 문짝·물리 키패드·샘플 냉장고·분석 장비·검체 카트·작업등과 파생 건축 원본이다. [검수 결과](../../Docs/검수/2026-11-06_LabPolish/검수결과.md)의 최종 상태를 우선한다.

`LP_*.blend`는 베벨·가중 노멀을 유지한 편집 원본이고 `asset_manifest.json`은 출력한 FBX와 삼각형 수다. 건축은 이전 B5 ArtRepair/B4 Architecture 원본에서 옛 문 시각 파트만 제거한 파생본이다. 그 밖의 벽·바닥·천장·계단·배관 메시를 평가한 뒤 재질/구역별로 합쳤다. Unity의 기존 정적 건축 충돌체는 유지했다.

| 도구 | 용도 |
| --- | --- |
| `build_lab_assets.py` | 외부 Blender 제작/출력. `--keypad-only`, `--worklight-only`로 해당 에셋만 출력 가능 |
| `ApplyLab.cs` | Unity 외부 Editor 명령. Import → Apply → Calibrate 순서로 최초 적용한 이력. 현재 파일의 최초 적용 기본값도 최종 보정값으로 정리 |
| `ReviewLab.cs` | 동일 시점 Before/After 및 문·키패드·프랍 근접 렌더 |
| `ValidateLab.cs` | 경로·문·프랍 충돌/참조 검사, 정적 반사 베이크, 최종 반입 로그 |

완료 씬에서 `Apply()`를 다시 실행하지 않는다. 이미 `Lab_Doors`가 있으면 중단한다. `Import()`는 프리팹을 다시 저장하므로 사용자 후속 수정을 덮어쓸 수 있다. 수정할 때는 원본/현재 씬 차이를 확인하고 필요한 메서드/에셋만 대상으로 한다. `Calibrate()`도 현재 조명/톤 값을 다시 지정하는 도구이지 무해한 조회가 아니다.

게임 `Assets`에 C#을 추가하지 않았다. 이 C# 파일은 Unity CLI `command script run <파일> --entry <클래스.메서드>`로 실행하는 제작/검수 도구다. Unity 프로젝트 경로와 `--caller plugin --skill unity-cli`를 명시한다. 실행 전 저장된 Edit Mode여야 한다. Blender 모델을 다시 출력한 뒤에는 AssetDatabase의 명시적 Refresh/Import 후 화면을 확인한다.

문 프리팹의 `Leaf_Left/Right`에 각각 BoxCollider가 있고 열림/닫힘 앵커가 있다. 키패드는 시각 에셋이다. 실제 개폐/잠금/입력·동작 코드와 Animator는 없다. 공개 Git 공유 요청이 있을 때 원본·FBX·프리팹·재질·텍스처·씬·검수 자료와 `.meta`를 함께 검토한다.

2026-11-06 후속으로 LP 프랍4개의 앞면 방향을 보정했고 ApplyLab의 최초 배치 기본값에도 반영했다. 현재 B5/B4 활성 건축은 LC 파생본이다. 최신 기준은 [층간 후속 소스](../LevelContinuation/README.md)를 따른다.
