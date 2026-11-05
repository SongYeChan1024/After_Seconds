# B4 잠입층 제작 원본 V0.01

작성자 송예찬 · 2026-11-06

`Docs/도면/잠입_탐색/layout.json`의 B4를 사용한다. 내부 게임 로직을 작성하는 도구가 아니라 Blender 건축 생성과 Unity 에디터 배치·검수 도구다. 이미 만든 씬은 재생성보다 현재 상태를 읽고 수정한다.

제작 순서는 `build_b4_architecture.py` → `build_b4_details.py` → `BuildB4Scene.Build` → `PolishB4.Lighting` → `PolishB4.Details` → `PolishB4.Finish` → `PolishB4.StaticPoses` → `PolishB4.GroundActors` → `PolishB4.BakeReflections`이다. Blender5.2 배치 실행을 사용하며 편집 원본과 FBX를 출력한다. 기존 B4 씬이 있으면 Build는 중단한다. StaticPoses는 B5를 읽기 전용으로 열어 정적 뼈 회전을 가져온 뒤 저장 없이 닫고, 새 B4 인물의 미연결 Animator만 끈다. GroundActors는 스킨 메시의 현재 포즈와 FBX 스케일을 반영해 발 높이를 맞춘다. 기존 원본6층과 새 B5는 수정 대상이 아니다.

`unity_task.py`는 현재 프로젝트를 명시해 Unity CLI 명령을 실행한다. 예: `python SourceAssets/B4_StealthLayout/unity_task.py script run C:/GitHubProjects/After_Seconds/SourceAssets/B4_StealthLayout/ReviewLevels.cs --entry ReviewLevels.AuditConnections`.

`ReviewLevels.cs`의 캡처는 Edit Mode의 임시 카메라 렌더다. `WalkB4`는 현재 플레이어와 같은 치수/stepOffset/skinWidth/slopeLimit를 가진 임시 CharacterController.Move 검사다. `play_review.py`/`PlayReview.cs`는 Play Mode 프레임 진행과 Input System W 이벤트를 확인하고 실제 Game View를 저장한다. 검수 결과는 `Docs/검수/2026-11-06_B5_B4/`에 있다. 캡처 도구가 반환하는 savedPath를 따른다. 현재 Pipeline은 Temp 경로도 Assets 아래로 정규화하므로 `ReviewLevels.CleanCaptureImports`로 이번 시험 전용 `Assets/Temp/B4Review`만 정리한다.

`protected_files.py`는 작업 시작 당시95개 보호 파일을 해시로 기록했다. `--verify`로 비교하며, `--restore-line-endings`는 원래 해시와 정확히 일치하는 경우에만 Unity 저장 후 줄바꿈을 복원한다.

마감 시 원본 B4/B5 씬이 `Stage/Old/`로 옮겨져, `--verify`는 해당2개만 명시적으로 보관 경로까지 확인하고 동일 바이트 여부와 relocated를 기록한다. 다른 파일의 이동·누락을 자동 허용하지 않는다. 제작 도구의 집 PC 절대경로는 다른 PC에서 사용 전 해당 로컬 경로로 맞춰야 한다.

계단A 단면과 층간 전환은 미완료이며 계단B6.4m·36단은 가안이다. 자세한 범위는 최신 이어하기를 따른다. 큰 방 설명 표지·경로선·AI·Animator Controller·UI는 추가하지 않는다.
