# T02 복도·계단 A 제작 V0.01

작성자 송예찬 · 2026-11-08

현재 T02/VA 건축과 C01–T01–C02–T02–VA 목적지 안내의 기준 원본이다. 도면은 `Docs/도면/Decision/원형공동/facility_layout.json`, 실제 계단 치수는 `geometry.json`, 안내 좌표는 `plan.json`이다. B5 -82m→B4 -66m의16m를8구간96단으로 연결하지만 B4 공간/씬 전환은 구현하지 않았다. 닫힌 상부문은 정적 외형이다.

## 제작과 적용

`build.py`는 기존 제작기의 함수 정의만 재사용해 TA_ 모델11종을 만들며 원래 제작 본문을 실행하지 않는다. 각 `.blend`에 편집용 bevel이 남고 FBX는 삼각화한 결과다. `refine_build.py`/`detail_build.py`는 이번 후속 보강 기록이다. 최종 `build.py`에 동일 보강을 반영했다. 모델11종500,152tri이며 TC PBR 텍스처3세트를 공유한다.

Unity 명령은 `python SourceAssets/B4_StealthLayout/unity_task.py script run <C# 절대경로> --entry <클래스.메서드>`를 사용한다. 먼저 현재 사용자 편집/씬/에셋을 별도 백업한다. `StairAApply.Run`은 자기 건축 그룹과 VA 셸/VA측 문3개, VA 하부 Light2개 위치만 갱신한다. 기존 문은 비활성 보관한다. 원본 전체 층이나 C01/C02/T01 제작기는 재실행하지 않는다.

`build_guides.py` → `verify_plan.py` → `textures.py` → `StairAGuideApply.Run`은 C01 청록/C02 파랑/VA 녹색의 목적지 안내를 만든다. numpy/Pillow는 `%TEMP%/as_art_tools/Scripts/python.exe`에 있다. `StairALabels.Run`으로 T02 표기4개와 T01 VA표기1개를 반영한다. `prepare_guides.py`는 초기 도구 복제 기록으로, 최종 수정된 검수/출처 코드를 덮어쓰지 않도록 재실행하지 않는다.

`StairACollarCleanup.Run`은 원본 전체 문 접합 메시에서 VA 영역만 제외한 `TA_PortalCollars_VAReplaced.asset`를 생성한다. 다른 문 장식/원본 FBX는 보존한다. 이미 적용된 씬에서 재생성하지 않는다. `CollisionFinish.cs`는 마지막에 추가한 기둥4개/보호 레일2개 Collider의 기록이며 같은 내용은 최종 Apply에 포함한다.

`Walk.cs`는 계단 전체 왕복과 세 문 접근, `GuideProbe.cs`/`GuideWalk.cs`는 안내 경로를 검사한다. `Audit.cs`는 메시·보호 Transform·기존 Light 설정·머리 위 여유를 확인한다. `Play.cs`/`run_play.py`는 기존 키보드 입력과 프레임/실제 이동으로 검증하고 설정을 복구한다. `fix_play_focus.py`는 포커스 처리 보강 기록이다. Play 도구 재생성 시 이를 반영하며 게임 C#을 바꾸지 않는다.

`Capture.cs`는 외형 검수, `Feeds.cs`/`refresh_feeds.py`는 관제 정적 화면 갱신이다. `PostPlay.cs`는 편집 상태를 백업/보존하고 임시 캡처를 정리한다. `RecordSource.cs`는 제작 좌표·모델·최종 상태 기록, `finalize_assets.py`는 기존 파일 보존 대조, `finish_documents.py`는 검수 문서 작성용이다. baseline/Prepare/Inspect는 작업 시작 기준이므로 덮어쓰지 않는다.

모델/재질/텍스처는 `Assets/Afrer_Seconds/05.Model/Environment/B5`, 출처는 `06.Data/AssetSources/T02_StairA_20261108.json`이다. 새 Light8개는 새 등기구에만 대응한다. 기존187 Light는 위치2개 외 설정을 보존했다. URP 조명 데이터8개 외 새 게임 Behaviour/Animator는 없다. 최종 조명은 B5 전체 후 조정한다.

[최신 검수](../../Docs/검수/2026-11-08_T02_StairA/검수결과.md). 로컬 저장, 이번 변경 커밋·push 미실시. 다음 후보는 T08/W01이다.
