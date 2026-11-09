# B3 전체 시료층 제작 원본 V0.02

2026-11-09 후속 구조·밀도 보수는 [B3_StructureRepair](../B3_StructureRepair/README.md)를 우선한다. 현재 layout.json은 T08 곡선과302배치를 반영했다. 이 폴더의 이전 전체 제작기를 다시 실행하지 않는다.

작성자: 송예찬 · 2026-11-09

최신 Decision 도면을 `plan.json`에 보존했고 실제 모델 치수와 접근 여유를 반영한 배치는 `layout.json`이다. `architecture.py`, `props.py`, `wall_controls.py`와 각 `.blend`는 건축·전용 프랍 제작 원본이다. VARCO 원본 GLB/이미지·프롬프트/노드·가공/텍스처 채널은 `varco_*` 자료에 있다.

`Apply.cs`, `Refine.cs`, `align.py`, `Align.cs`, `Finish.CCTV`, `LodApply.cs`는 현재 씬에 이미 적용했다. 전체 제작 도구를 다시 실행하면 후속 편집을 잃거나 중복될 수 있으므로 대상 보수만 한다. 특히 `layout.py`/`refine_layout.py`를 다시 실행하면 정렬 이후 배치가 바뀌므로 현재 `layout.json`을 우선한다.

`lod_plan_new.json`, `lod_catalog_new.json`, `lod_models_new.json`은 신규 감면본, 같은 이름에서 `_new`가 없는 자료는 기존 B4 검수 LOD 재사용분을 합친 최종 적용 자료다. 최종 자료로 내보내기/재임포트를 반복하지 않는다. 근접 LOD0과 충돌은 원본을 유지한다.

네이티브 임포트는 이번 단계의 명시적인 파일 접두사만 대상으로 한다. 기존 B3 텍스처를 넓게 순회했던 설정 변경은 `RestoreImporter.cs`로 복구했으며 재발 방지 필터를 반영했다. `CameraFix.cs`는 새 씬의 카메라 참조 복구 기록이다. 최초 제작기의 카메라 보존도 보완했으며 현재 씬에 다시 복구할 필요는 없다.

`Review.cs`, `Details.cs`, `Play.cs`, `LiveFrame.cs`, `Finish.Audit`는 외부 검수용이다. Assets에 복사하거나 런타임 기능으로 사용하지 않는다. 기본 소등 상태는 유지하고 `Details.Run`에서만 작업등을 임시로 켠 뒤 저장된 씬으로 돌아온다.

[검수 결과](../../Docs/Review/2026-11-09_B3_FullFloor/Review.md) · [화면](../../Docs/Review/2026-11-09_B3_FullFloor/review.html)
