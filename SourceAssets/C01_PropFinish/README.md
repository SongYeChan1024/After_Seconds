# C01 프랍 제조 디테일·PBR 제작 V0.02

최신 병·라벨·간섭 보수는 [C01_PropRepair](../C01_PropRepair/README.md)를 따른다. 현재 제작기는 refine_components.py도 참조하며 새 PR_ 재질은 ImportRepair를 마지막에 반입한다.

작성자 송예찬 · 2026-11-07

승인된 C01 배치의 CP_/ID_ 모델37종을 갱신한다. 결과와 범위는 [검수 기록](../../Docs/검수/2026-11-07_C01_PropFinish/검수결과.md)을 따른다. `C01_Perimeter`, `C01_InstrumentDetail`, 이 폴더를 함께 보존한다.

## 파일과 재제작

1. `build_pbr.py`: Pillow/numpy를 사용하는 로컬 표면 맵 제작기. 별도 제작 환경은 `%TEMP%/as_art_tools`이며 게임 의존성이 아니다. 런타임 맵30장은 Props/B5/Textures, 거칠기 원본6장은 이 폴더에 둔다.
2. `C01_Perimeter/build_assets.py` → `C01_Perimeter/repair_vital.py` → `C01_InstrumentDetail/build_instruments.py`를 Blender5.2에서 실행한다. 세 제작기가 `finish_geometry.py`를 참조한다. 같은 이름 FBX를 교체하므로 meta/GUID를 보존해야 한다. 장면 배치 도구를 다시 실행하지 않는다.
3. `ImportFinish.cs`의 `PropFinishImport.Run`: 재질/텍스처 설정과 CP_/ID_ 모델의 기존 GUID를 유지한 반입. 이후 기하 수정만 있으면 `InstrumentDetailApply.ImportGeometry`를 사용한다.
4. `FinalAudit.cs`, `Audit.cs`, `VerifyC01Routes.cs`, `Capture.cs`, `PlayC01.cs`, `FinishAudit.cs`: Assets 밖에서 실행하는 에디터 검수 도구. 게임 내부 C#이 아니다. Play 전 저장/편집 상태를 확인한다. `RestoreAfterOwnPlay`는 이 검수기가 방금 실행한 Play 잔여 dirty 상태를 복원할 때만 사용하며 사용자 편집 중에는 실행하지 않는다.

`finish_geometry.py`는 기구별 기능 부품을 더한 뒤 노멀을 정리한다. 최종 evaluated mesh를 무조건 BMesh로 왕복하면 custom normal을 잃을 수 있으므로 삼각분할 후 정상 메시의 노멀을 유지한다. Boolean에서 생긴5e-9㎡ 미만 삼각형만 UV·material index·split normal을 복사해 정리한다. display_uv가 있는 LCD/라벨은 투영 UV 재생성에서 제외한다.

PBR은 6종 공용 표면(Base/Normal/MOS)이며 MOS의 R=metallic, A=smoothness, G=1, B=0이다. 고해상도 개별 에셋 AO 베이크로 해석하지 않는다. Normal은 tangent +Y, Base는 sRGB, Normal/MOS는 선형. 공통 타일링5, Normal strength 도장0.25/Steel0.38. URP 키워드와 텍스처 연결은 state.json에 남긴다.

`baseline.json`의 작업 전 백업은 로컬 임시 폴더다. 백업 자체는 Git 전송 대상이 아니며 `.blend`, 생성기, 최종 FBX/텍스처/재질과 검수 기록이 전달 원본이다. `prepare.py`는 최초 백업 전용이므로 현재 상태에서 다시 실행해 기준을 덮어쓰지 않는다. `prepare_checks.py`도 검수 도구 복사 초기화용이다. `finalize_records.py`는 최종 검사 후 로컬 기록과 provenance를 갱신한다.

게임 C#·Animator·다른 씬·리브·플레이어 시작 위치는 보호한다. 이번 단계에서는 씬 저장 파일 자체도 변경하지 않았으며 외부 생성/업로드/커밋/push를 하지 않았다.
