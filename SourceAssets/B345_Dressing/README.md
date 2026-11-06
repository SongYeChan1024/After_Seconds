# B5·B4·B3 프랍 보강 제작 원본 V0.02

후속 최신은 `SourceAssets/B345_WideInterior`와 [터널·돔 검수](../../Docs/검수/2026-11-06_B345_WideInterior/검수결과.md)다. 현재 모델은 WC/WA이며, 상자는 SW 생활 흔적 마감이다. 이 폴더의 이전 Apply를 현재 확장 씬에 덮어 실행하지 않는다.

아래 날짜별 문단은 이전 작업 이력이다.

작성자 송예찬 · 2026-11-06

사용자 요청: 제작된 B5/B4/B3 전체의 빈 공간을 채우고, B3 시료 상자에 테두리·잠금쇠·손잡이·여러 텍스처 패턴을 적용한다. 새 프랍은 지정 VARCO V0.03 플로우에서 먼저 제작하고 Blender에서 정리한다.

- VARCO: [After_Second_Env_and_Props_Ver0.03](https://3d.varco.ai/flow/8f7100a4-a7df-488b-81ee-0c2ac6ae60d8). 기존 인물 노드는 변경하지 않았다. 새 6종의 이미지→3D→리메시 결과와 ID는 varco_results.json, 다운로드 원본은 Varco 폴더다.
- 모델 6종: SpecimenCase, DiagnosticCart, CylinderTrolley, PPEStation, CentrifugeBench, MaintenanceStation. 모두 VARCO 메시를 채택했고 Blender에서 치수·노멀·1mm 각도 베벨·삼각화·3단계 LOD와 URP용 PBR 맵을 정리했다. 게임 모델은 Props/Common/SD_*에 있다.
- 상자6종 패턴은 bake_case_variants.py의 Blender 절차 재질을 원래 UV에 베이크했다. 별도 신규 문양/마감이며 기존 VARCO 상자 원본을 보존한다.
- derive_b3.py는 B3 원본에서 상자/뚜껑/잠금쇠864파트만 제외해 SD_B3_Architecture를 만든다. 랙과 벽·바닥·계단·충돌은 유지한다.
- ApplyDressing.cs는 외부 Editor 전용 도구다. Import는 파생 모델/재질/프리팹 제작, Apply는 새 배치, Clearances는 문 접근 공간 보정이다. 완료 씬에 무작정 재실행하지 않는다. 최신 좌표는 검수 폴더의 placed_B5/B4/B3.json이다.
- 씬의 Dressing_Props에 B5 30 / B4 33 / B3 38개, B3 Specimen_Cases_6Patterns에288개가 있다. 선반 상자는 기존 랙 충돌을 사용하므로 개별 Collider를 비활성화했다.
- DressingReview/ValidateDressing/DressingWalk/DressingPerformance는 검수 도구다. 게임 C#·UI·AI·문 동작은 추가하지 않았다.

검수와 전후 사진은 [검수결과](../../Docs/검수/2026-11-06_B345_Dressing/검수결과.md)를 따른다. 이번 작업은 로컬 저장 상태이며 Git 커밋/push하지 않았다.
