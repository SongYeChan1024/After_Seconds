# B5 남은 돔 일괄 제작 V0.02

작성자 송예찬 · 2026-11-08

사용자 요청에 따라 C03·C04·W01~03·E01~03·N01·S01의 10개 돔, VB·VL 코어, T03~T19를 제작하고 자체 검수를 마쳤다. [전체 검수 화면](../../Docs/검수/2026-11-08_B5_RemainingDomes/review.html) · [결과와 남은 범위](../../Docs/검수/2026-11-08_B5_RemainingDomes/검수결과.md).

새 FBX 103종, 프랍 174배치+의자6, 역할별 LCD18장과 천 PBR3장. 목적지15색/38경로/19복도, 자체 통행71/71 통과. 최종 사용자 외형 검수와 전체 조명 조정은 남는다. 정적 아트만 제작했으며 게임 C#/Animator는 변경하지 않았다.

## 원본과 좌표

- `plan.json`: 현재 174개 프랍과 15목적지/19복도 좌표. `models.json`: 103개 모델 및 삼각형 수.
- `build.py`, `architecture.py`, `cores.py`, `detail.py`, `finish.py`, `safety_fix.py`: Blender 제작. `RD_*.blend`: 편집 가능한 개별 원본.
- `textures.py`: 18가지 정적 화면과 천 PBR. `screen_detail_fix.py`: 서로 다른 관제 화면 6개.
- `guidance.json`: 최종 38경로와 방향 표기/범례. `guides.py`는 물리 충돌 그리드로 라인을 설계한다.
- `Apply.cs`, `CoreApply.cs`, `DetailApply.cs`, `FinishApply.cs`, `SafetyFix.cs`: 단계별 Unity 반영 이력. **전체 재실행 금지**. 이미 존재하는 구조를 유지하고 필요한 부분만 수정한다.
- `PlacementRepair.cs`: 프리팹 재임포트 좌표 보수와 174개 대조. 프리팹을 수정하면 `RecordPrefabInstancePropertyModifications`를 기록한 후 저장한다.
- `Grid.cs`, `Verify.cs`, `Walk.cs`, `Survey.cs`: 물리/메시/접촉 검수. `Play.cs`, `run_play.py`: 실제 입력과 프레임 진행 검수. `Capture.cs`: 현재 씬의 사진, `write_review.py`: 검수 문서/갤러리.
- `Occlusion.cs`: 문을 제외한 구조물의 가림 베이크. 가림 데이터는 씬 옆 `Level_B5_Circular/OcclusionCullingData.asset`이다.

`plan.py`와 `detail_plan.py`는 초기 단계 생성기이며 현재 plan.json에 재실행하면 누적 수정이 사라지거나 중복된다. `prepare_play.py`와 `fix_play_*.py` 역시 초기 제작 이력이며 현재 Play.cs 위에 재실행하지 않는다. Blender 모델은 FBX+재질을 `05.Model/{Props|Environment}/B5`로 내보내고 .blend는 이 폴더에 보관한다. 씬은 Unity Editor API로만 수정한다.

대상 씬은 `Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular.unity`, 새 그룹은 `Remaining_Domes_Art`, `Remaining_DestinationGuidance`, `B5_Occlusion_ViewVolumes`다. 이전 원형/전체 Apply를 재실행하지 않는다. 게임 구현·B4 연결과 최종 조명은 후속 범위다.
