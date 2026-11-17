# 아래 투척 굴림 보수 도구 V0.01

2026-11-17 · 작성자 송예찬

사용자가 아래 투척은 띄우기보다 굴리는 느낌이라고 정정했다. 메인 기획서 V0.94를 먼저 갱신하고 PlayerThrow/PlayerFirstPersonHands 및 두 설정 클래스·에셋을 보수했다. 위 투척의 속도·클립·물리 재질은 유지한다.

- `Apply.cs`: 편집 상태에서 아래 설정과 전용 `UnderhandRoll.physicMaterial`만 Unity AssetDatabase로 반영한다. 기존 GUID를 보존한다.
- `Validate.cs`: Play에서 실제 InputSystem 좌클릭/R 입력, 낮은 발사·손 후속 동작, 실제 접촉/회전/이동/감속, 위 방식·막힌 손·표시선 보존을 확인한다. 임시 바닥·설정·투척물은 복원/제거한다.
- `Probe.cs`: 착지 직후 속도 손실의 원인을 조사한 독립 물리 실험. 최종은 ContinuousDynamic·마찰0.2 Minimum이다. 프로젝트 전역 물리 설정은 바꾸지 않는다.
- `Finish.cs`: 편집 상태에서 검수용 백그라운드 설정을 복원하고 콘솔/씬/참조를 기록한다.

`.cs` 파일은 Unity CLI `script eval_file`로 실행하며 Assets 안에 복사하지 않는다. 이전 단계 전체 제작기를 재실행하지 않는다. 원본 백업: `%TEMP%/AfterSeconds_UnderhandRoll_20261117_161400`.

[실측과 화면](../../Docs/Review/2026-11-17_UnderhandRoll/Review.md). 이전 DirectThrow 검수의 아래 속도6m/s는 당시 수치이며 현재4.5m/s다.
