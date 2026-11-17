# 줍기·투척 연결 작업 도구 V0.01

작성일 2026-11-17 · 작성자 송예찬

이 폴더는 Unity6000.4.0f1에서 B5와 기존 Player/시험용 공을 연결한 외부 작업 기록이다. 게임 실행 코드는 `Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/02.Scripts/`에 있다. 결과는 [검수 보고서](../../Docs/Review/2026-11-17_PickupLoop/Review.md)를 따른다.

## 현재 연결

- `C.System/Item/WorldItem.cs`: 개별 월드 물건의 소유권·보관·원래 물리 설정 복원.
- `C.System/Player/PlayerInventory.cs`, `PlayerInventorySettings.cs`: 획득 후보·5개 목록·선택·안전한 내려놓기.
- 기존 `PlayerThrow.cs`, `ThrownObject.cs`, `PlayerPresenter.cs`: 동일 물건 방출·명중 활성 상태·실제 입력 연결.
- `D.Ui/PlayerInventoryView.cs`: F 안내와 우하단 소지품. `UI_AD.asmdef`에 SystemAD·TMP·uGUI 참조 추가.
- 설정은 `06.Data/PlayerInventorySettings.asset`. 플레이어는 기존 `05.Model/Player/Player_Dummy_V0.1.prefab`, 공은 `04.Prefabs/Test/ThrowTestItem.prefab`. B5에 `PickupLoop_TestBall`1개 배치.
- 한글 원본 `06.Data/UI/NotoSansKR.ttf`, 라이선스 `OFL.txt`, 동적 폰트 `Pickup_Korean_SDF.asset`. 모두 Assets/Afrer_Seconds 기준 경로다.

폰트 출처는 [Google Fonts의 Noto Sans KR](https://github.com/google/fonts/tree/main/ofl/notosanskr)이며 SIL Open Font License를 동봉했다. TMP 기본 리소스는 설치된 `com.unity.ugui`의 TMP Essential Resources에서 가져왔고 `Assets/TextMesh Pro/`의 Unity 표준 경로를 유지한다. 프로젝트 전용 폰트와 기본 리소스의 경로를 혼동하지 않는다. 기본 폴더 이동 실패를 강제 파일 이동으로 우회하지 않았다.

## 도구

`unity command script eval_file --project-path <Unity프로젝트> --caller plugin --skill unity-cli --format json -- --file <절대경로>`로 실행한 C# 조각이다. 외부 파일이므로 Unity 런타임 어셈블리에 포함되지 않는다.

| 파일 | 용도와 조건 |
| --- | --- |
| `Inspect.cs` | 현재 씬·프리팹·입력 바인딩 읽기 |
| `Apply.cs` | 최초 연결·프리팹 변경·B5 공 배치. 이미 적용 완료했으므로 후속 편집 위에 일괄 재실행하지 않는다 |
| `ImportTMP.cs` | 기본 TMP 리소스 최초 반입 기록. 이미 반입 완료 |
| `BuildUI.cs` | 최초 한글 폰트·HUD 작성. 중복 HUD가 있으면 중단하며 재실행 대상이 아니다 |
| `OrganizeUI.cs` | TMP 기본 경로 유지, 반입 창 정리·저장. 실패했던 폴더 이동 코드는 제거함 |
| `Validate.cs` | Play 모드에서 실제 입력36개 검증. 저장된 B5의 빈손 시작 상태 필요. 임시 입력 설정·격리 바닥·추가 공을 사용한 뒤 복원하며 검수 후 Play 종료 필수 |
| `State.cs` | 런타임 방출/물리 상태 읽기 |
| `Finish.cs` | 저장된 B5 편집 모드에서 참조·설정 확인, 백그라운드 설정 복원·결과 기록 |

검수 전후 `script recompile_status` 완료와 실제 프레임 증가를 확인했다. 검수용 임시 바닥·공은 저장하지 않는다. 사용자 투척 설정은 위15m/s·아래10m/s이며, 이전 작업의12/4.5m/s로 덮어쓰지 않는다.

## 변경 기록

- V0.01 (2026-11-17): 최초 연결 도구·폰트 출처·36개 검수와 안전한 재실행 조건 기록. 송예찬.
