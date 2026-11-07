# 실험동 업무 안내선·출입 표식 제작 V0.01

작성자 송예찬 · 2026-11-07

사용자가 실험동 타일·조명 확인을 완료했다. 조명·색감의 최종 조정은 B5 전체 제작 이후로 미룬다. 이번 작업은 바닥 업무 안내선과 작은 출입구 시설 표식이다.

Decision/원형공동/facility_layout.json의 R1(직원·교대/흰 이중선), S1(시료 이송/청록 선·사각), M1(정비/황토 점선) 규칙을 따른다. 기존 R1 출발점에 T11 직원 인계 접근선을 합류시키고, 포드 북동쪽 S1은 T03에 연결한다. M1은 점검함 앞 접근/비움 표시만 제작하며 층 전체 정비 노선을 새로 확정하지 않는다.

plan.py/plan.json은 현 배치를 기준으로 한 표면 경로 제작 데이터다. 기존 시설 설계의 다른 공동 경로를 대체하지 않는다. 얇은 바닥 페인트, 작은 R1/S1 출입 코드·방향 표식, 문턱 가장자리 표시를 제작한다. 큰 방 이름·퍼즐 풀이 표지는 넣지 않는다. Collider와 게임 C#은 추가하지 않는다.

prepare.py로 기존 파일 해시와 씬 백업을 남긴 뒤 제작·적용·통행/가독성 검수를 진행한다. 모든 적용은 실행 중 Editor의 AssetDatabase와 씬 API로 수행한다. 이전 전체 레벨 Apply는 실행하지 않는다. 최종 제작·검수 수치는 결과 문서를 따른다.

제작·검수 완료: [검수 결과](../../Docs/검수/2026-11-07_C01_Wayfinding/검수결과.md). 메시15·재질9·텍스처7, 바닥 코드5곳·출입 명판3곳. 경로358표본·복도 왕복6회·실제 입력 Play2구간을 확인했다. 기존2001 Transform과187 Light는 동일하다.

재현 순서는 `plan.py` → `build_textures.py`(Pillow/numpy 환경) → `Probe.cs` → `Apply.cs` → `Capture.After`다. C#은 `python SourceAssets/B4_StealthLayout/unity_task.py script run <절대 파일 경로> --entry <클래스.메서드>`로 실행한다. Apply는 저장된 B5 Edit 씬에서 자체 그룹과 CW 에셋만 갱신한다. 기존 메시를 수정할 때에는 Clear/SetVertices/SetTriangles/UploadMeshData로 GPU 데이터까지 갱신한다.

`Inspect.cs`·`prepare.py`는 작업 전 기준을 만드는 도구다. 기존 before.json/baseline.json을 현재 결과로 덮어쓰지 않는다. `record_decision.py`는 이번 시작 결정 기록용이므로 다시 실행하지 않는다. `InspectAfter.cs`·`Audit.cs`는 종료 상태 확인, `Walk.cs`는 기존 CharacterController의 세 복도 양방향 통행 확인용이다. `Play.cs`의 Inside/Tunnel은 Play 모드에서 기존 키보드 W down/up을 전달하며 5초 뒤 입력 설정을 원복한다. Play 종료 후 원래 저장 씬과 Run In Background 설정을 복구한다.
