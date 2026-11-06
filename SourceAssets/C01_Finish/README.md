# C01 리브 보수와 실험 소품 제작 원본 V0.01

작성자 송예찬 · 2026-11-07

현재 대상은 `Level_B5_Circular`의 `C01_Experiment_Art`다. [검수 결과](../../Docs/검수/2026-11-07_C01_Finish/검수결과.md)를 먼저 읽는다. 모든 C#은 Assets 밖의 Editor 제작·검수 도구이며 게임 코드는 아니다.

- `build_ribs.py`: Blender 5.2에서 리브 8개·받침·앵커·이음·천장 링만 재생성한다. `SourceAssets/B5_FullLayout/AF_C01_ThreePortalRibs.blend`와 기존 이름 FBX를 갱신하며 `.meta`를 보존한다.
- `ApplyRibs.cs`: 반입·전용 금속 3재질·현재 리브 MeshCollider를 반영한다. 다른 벽 재질을 수정하지 않는다. FBX 재반입 후 지연된 prefab 갱신으로 씬이 dirty가 되면 내용을 확인하고 SavePending으로 저장한다.
- `build_connections.py`: 콘솔 2곳에 맞춘 단자함과 케이블 모델을 생성한다. Blender 원본은 이 폴더의 `AF_C01_ConsoleConnections.blend`다.
- `ApplyDetails.cs`: 기존 프랍 4개와 연결 모델을 배치한다. 이미 `C01_Finish_Props`가 있으면 중단한다. 후속 배치를 지우거나 초기화하지 않는다.
- `ReviewC01.cs`: 저장된 씬의 전후 캡처. 임시 카메라/플레이어 숨김을 복구하고 저장 씬을 다시 연다. 저장되지 않은 사용자 편집이 있으면 먼저 보존한다.
- `AuditC01.cs`: 리브 연속·대칭, 주변 박스 충돌, 새 프랍 관통, 재질·삼각형을 확인한다.
- `prepare_validation.py`: 기존 검수 도구에서 보고서 경로를 이번 폴더로 바꾼 외부 C#을 만든다. 이전 검수 원문과 캡처를 덮어쓰지 않는다. WalkC01Routes는 T01/T03/T11 왕복만 검사한다.
- `PlayC01.cs`: Play의 실제 입력·프레임·오류를 5초 확인한다. 끝나면 Play 종료와 백그라운드 override 해제로 저장 위치를 복구한다.
- `prepare.py`: 수정 전 파일을 OS Temp에 백업하고 보호 파일 해시를 기록한다. 작업 중 다시 실행해 최초 기준을 바꾸지 않는다.
- `finish_record.py`: 이번 최초 작업의 결과 기록용이다. 버전·기준 문구를 확인하고 한 번 적용했으며 이후 세션에서 자동 재실행하지 않는다.

형상 수치는 `rib_geometry.json`, 배선 형상은 `connections_geometry.json`에 기록했다. 사용자 시야 승인과 남은 건축 마감은 검수 결과의 남은 범위를 따른다. 커밋·push는 이번 작업에 포함하지 않았다.
