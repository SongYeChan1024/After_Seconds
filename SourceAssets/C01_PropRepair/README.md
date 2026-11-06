# C01 겹침·병 라벨·소품 접점 보수 V0.01

작성자 송예찬 · 2026-11-07

사용자 피드백의 실제 수정 범위와13장 근접 검수는 [검수 기록](../../Docs/검수/2026-11-07_C01_PropRepair/검수결과.md)을 따른다. C01_Perimeter/C01_InstrumentDetail/C01_PropFinish/이 폴더를 함께 보존한다.

`refine_components.py`는 기존 finish_geometry.py 마지막 단계에서 실행된다. 원통 제작 가이드와 큐브 라벨을 최종 병·밀착 라벨·얇은 인쇄물로 교체한다. 원본46병/9종, 분석기 화면 간격과 포장물 내부 배치 근거는 개별 모델 JSON에 남는다. 라벨은32각 병의 각도 샘플과 맞춘16면 반원 표면이며0.18mm만 띄운다. 큰 병은 폴리머, 작은 병은 유리+시료로 구분한다. 인쇄물 UV는 기존 투영 UV로 덮어쓰지 않는다.

재현 순서: `build_labels.py`(Pillow) → Blender의 `C01_Perimeter/build_assets.py` → `C01_InstrumentDetail/build_instruments.py` → `PropRepairImport.Run`. 기반 PBR까지 새로 반입할 때는 `PropFinishImport.Run` 뒤 `PropRepairImport.Run`을 실행한다. 기하만 바꾸면 기존 `InstrumentDetailApply.ImportGeometry`를 사용한다. **현재 씬에 배치 Apply를 다시 실행하지 않는다.** 기존 meta/GUID를 보존한다.

`prepare.py`는 최초 백업 전용이다. 현재 상태에서 기준을 다시 만들지 않는다. `Capture.cs`는 저장된 B5 편집 씬에서 전후 동일 카메라13개를 사용한다. 검수 도구는 Assets 밖의 에디터용 C#이며 게임 코드가 아니다. `FinishAudit.RestoreAfterOwnPlay`는 해당 검수기가 방금 실행한 Play만 복원할 때 사용한다. 사용자 미저장 편집 중에는 호출하지 않는다.

`finalize_records.py`는 최종 검사 JSON과 실제 파일을 대조해 보고서/보존 검사/provenance와 전후 비교 이미지를 기록한다. 이전 단계의 finalize 스크립트를 현재 기록 생성용으로 다시 실행하지 않는다. 임시 백업은 baseline.json의 로컬 경로이며 Git 전달 원본은 생성기·blend·FBX·텍스처·재질이다.

씬/30작업대/Collider/기존 리브/다른 씬/게임 코드 보존. 로컬 수정이며 커밋/push 미실시.
