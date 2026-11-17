# 1인칭 손 표현과 투척 검수 V0.01

작성자: 송예찬 · 2026-11-17

Claude CLI가 현황 조사 뒤 사용량 제한으로 중단한 1인칭·투척 개선을 이어서 구현했다. 기존 입력과 투척 기능 위에 팔 표시, 손의 소지품과 물리 물체 전환, 크기를 고려한 궤적을 연결했다. **동작 구현과 자동 검증은 완료했으며, 손 외형·쥐기·투척의 최종 애니메이션 품질은 임시 단계다.** 커밋·push는 하지 않았다.

[전후 화면과 동작별 화면](review.html) · [실제 물리 측정](physics_validation.txt) · [실제 입력 검증](play_validation.txt)

## 인계받은 상태

이미 있던 기능은 E 던지기 자세, 왼쪽 클릭 조준/방출, R 위·아래 전환, 오른쪽 클릭 확대/취소, 오른손 오프셋과 중앙으로 향하는 방향 보정, 일반 2.5m·확대 7m 궤적이었다. 점프·가감속 커밋 `cefb0823`과 미커밋 입력·투척 작업이 있던 상태에서 이어갔다.

새 요청의 분석 이후 실제 구현은 시작되지 않았으며, Play 진입 명령 직후 제한 메시지가 기록돼 있었다. 요청서는 `Documents/Codex/2026-11-17/gpr/outputs/AfterSeconds_ClaudeCLI_1인칭_투척_개선_프롬프트.txt`다. 영상에 관한 판단은 이 요청서의 관찰 메모에 한정했다. 이번 작업에서 영상을 직접 재생해 확인하지 않았다. FOV·힘·흔들림·포즈 수치는 영상에서 측정한 값이 아니다.

## 변경 내용

| 파일 또는 에셋 | 변경 이유와 동작 |
| --- | --- |
| `C.System/Player/PlayerThrow.cs` | 한 번의 방출, 손과 같은 시작점, SphereCast와 시작 겹침 검사, 자기 몸·트리거 제외, 즉시 취소, 선 끝 흐림과 막힘 표시. 실제 소비와 시험용 반복 공급 구분 |
| `C.System/Throw/ThrowFlight.cs` | 실제 Rigidbody 중력·linearDamping과 고정 물리 간격의 속도→위치 적분 공유 |
| `C.System/Player/PlayerFirstPersonHands.cs` | 카메라 아래 팔과 소지품 표시, 준비·조준·방출 후 복귀, 작은 이동 흔들림·회전 관성, 확대 시 흔들림 감소 |
| `C.System/Player/PlayerHandSettings.cs`와 `06.Data/PlayerHandSettings.asset` | 손 위치·보간·흔들림·복귀·쥐기 중심의 조절값 |
| `PlayerThrowSettings.cs`와 설정 에셋 | 아래 투척 손 위치 보정, 선 굵기·알파·끝 흐림·안전 여유·충돌 마스크 |
| `F.Presenter/Player/PlayerPresenter.cs` | 궤적을 손 갱신 뒤 LateUpdate에서 계산하도록 조정. 비활성화 시 자세까지 정리 |
| `05.Model/Player/Player_FirstPersonArms.asset` | 기존 V0.3 모델의 팔에 해당하는 2,348개 삼각형 재사용. 원본 모델 보존 |
| `05.Model/Player/Player_Dummy_V0.1.prefab` | `CameraRoot/FirstPersonArms_Prototype`와 팔 컴포넌트 연결. 기존 컴포넌트·참조 ID 보존 |
| `04.Prefabs/Test/ThrowTrajectory.mat` | LineRenderer의 색·알파를 쓰는 URP 투명 재질 |
| `Docs/AfterSeconds_메인기획서.md` | V0.87에 범위·의사코드·시험 수치 기록 |

새 팔은 전신 Animator와 본을 공유하지 않는다. 따라서 하체의 이동 블렌딩을 덮어쓰는 상체 레이어를 추가하지 않았다. 카메라 회전과 앉기 눈높이는 기존 PlayerLook, FOV는 기존 PlayerZoom과 Cinemachine만 제어한다. 전신은 Play 중 그림자를 유지하고 화면에서는 숨겨 얼굴 내부가 보이지 않게 한다. 팔 표시를 비활성화하면 원래 렌더링 상태로 복원한다.

방출은 왼쪽 클릭을 놓은 프레임에 즉시 실행한다. 애니메이션 이벤트·클립 완료를 기다리지 않는다. `Released` 알림과 동시에 손의 표시를 숨기고 물리 물체 하나를 만든다. 0.24초는 팔의 복귀 시험값이며 교환의 3초 대기와 관계없다. 본편 아이템 소비는 `repeatTestItem=false`에서 선택 참조를 비우는 연결 지점까지만 제공한다. 인벤토리 객체 상태·획득·교환 큐는 구현하지 않았다.

## 실행 검증

Unity 6000.4.0f1의 `Level_B5_Circular`에서 프레임 증가를 확인한 실제 Play 검증이다. 컴파일 오류·경고 0, 최종 프리팹의 누락 스크립트 0, 필수 팔 참조 누락 0이다. 실제 PlayerInput에 키보드·마우스 상태를 전달한 검사와 직접 시스템 호출 검사를 함께 수행했다.

- 동작 검사 **36/36 통과**. E·왼쪽 클릭·R·오른쪽 클릭, 취소 후 놓기, 확대 해제, 걷기·달리기·앉기·점프, 이동 중/앉은 상태 투척, 급격한 시야 회전, 비활성화, 시작 겹침과 트리거 제외를 확인했다.
- **7회 방출에서 이벤트 7회**, 물리 물체 생성 프레임에 손의 복제본 표시 0회. 손의 물체 중심과 실제 생성 중심의 최대 차이 **0.0000000m**.
- 자유 비행은 고정 간격 0.01·0.02·0.033333초와 damping 0·0.5 조합 **6/6 통과**. 1초 동안 매 틱 실제 Rigidbody와 예측 위치의 차이는 출력 정밀도에서 **0.0000000m**였다.
- 평지·높은 곳·경사·낮은 천장·가까운 벽·문틀·좁은 창문·통과 가능한 창문 **8/8 통과**. 첫 충돌 틱 차이 최대 1틱(0.02초). 충돌 후 solver 위치와 예상 접촉 중심의 차이는 0~0.21544m였다. 이는 충돌 뒤 남은 틱의 이동까지 포함한 비교이며, 접촉 순간 위치 오차가 0이라는 의미는 아니다.
- 목표 프레임레이트 30·60·144에서 각각 단일 방출을 확인했다. 각 6프레임 구간은 0.187·0.098·0.087초였다. 마지막 설정에서도 실제 144fps를 유지한 것은 아니므로 144fps 실측 검증으로 표시하지 않는다.

물리 검사는 고정된 발사 위치·초기 속도·정적 표적을 사용하는 독립 물리 씬에서 수행했다. 현재 정확한 물리 프로필 지원 대상은 **원점 중심의 단일 SphereCollider 투척물**이다. 시험용 공은 반지름 0.06m, 질량 0.3kg, linearDamping 0, 중력 사용, Continuous Dynamic이다. 다른 형상·물리 제약이 있는 아이템은 지금의 구체 예측이 정확하다고 처리하지 않고 발사를 거절한다. 해당 아이템용 충돌 형상과 손 표시를 연결한 뒤 확장해야 한다. 반사 이후와 움직이는 표적의 미래 충돌은 예측하지 않는다.

## Inspector 조절

| 대상 | 항목 | 현재 값 또는 용도 |
| --- | --- | --- |
| PlayerThrowSettings | Overhand / Underhand Speed·Angle | 기존 12m/s·8도 / 7m/s·5도 유지 |
| PlayerThrowSettings | Hand Offset | 위 (0.30,-0.15,0.45), 아래 (0.26,-0.24,0.55)m |
| PlayerThrowSettings | Trajectory Length / Zoomed Length | 2.5 / 7m |
| PlayerThrowSettings | Width / Opacity / Fade Start | 0.012m / 0.35 / 0.65 |
| PlayerThrowSettings | Surface Skin / Collision Mask | 0.005m / 전체 레이어, 자기 몸·트리거는 코드에서 제외 |
| PlayerHandSettings | Resting Item / Aim Hold Offset / Zoom Offset | 손의 기본·조준·확대 위치 |
| PlayerHandSettings | Pose Smooth Time / Recovery Time | 0.10 / 0.24초 |
| PlayerHandSettings | Bob Amount / Turn Sway / Max Sway | 0.008m / 0.002 / 0.025m |
| PlayerHandSettings | Zoom Motion Scale | 확대 시 흔들림 25% |
| PlayerHandSettings | Palm To Item / Shoulder | 손목과 물체 중심·팔 IK 기준점 |
| PlayerThrow 컴포넌트 | Repeat Test Item | 현재 켬. 시험 공 반복 공급 및 20초 뒤 정리. 끄면 성공한 투척에서 선택 참조 소비 |

`Trajectory Time Step`은 기존 직렬화 호환용이다. 실제 계산은 `Time.fixedDeltaTime`을 사용하므로 이 이전 필드로 궤적의 물리 간격을 바꾸지 않는다.

## 남은 에셋 작업과 검수 범위

🟡 기존 더미 손은 가까이서 보는 전용 손 모델 수준의 손가락·손바닥 변형을 갖추지 못했다. 현재 쥐기는 구체 중심을 향하는 임시 본 회전이다. 물건 종류별 쥐기 포즈, 위/아래 준비·유지·방출·복귀 클립, 전환 블렌딩을 제작해 교체해야 한다. 영상과 같은 최종 애니메이션 품질을 완성했다고 보지 않는다.

🟡 플레이어 전신의 기존 점프 애니메이션 미연결 상태는 그대로다. 실제 점프 이동과 시야는 검증했으며, 이 작업에서 사용자가 작성한 `PlayerAnimationSystem`을 변경하지 않았다. 게임패드, 다른 종횡비, 전체 층 플레이, 움직이는 표적과 복합 형상 아이템은 이번 검증 범위 밖이다.

기존 미커밋 입력 에셋·PlayerAnimationSystem·PlayerLookSettings·SystemAD·ItemDefinition·ThrownObject·PlayerZoom은 인계 시점 백업과 해시가 같다. 기존 프리팹 22개 직렬화 객체의 ID를 전부 보존했다. 기존 객체 변경은 팔 컴포넌트/자식 추가, 반복 시험 설정 직렬화, 궤적 굵기뿐이다. 레벨·조명·카메라 컷씬·패키지 버전은 변경하지 않았다.

검증 도구는 `SourceAssets/FirstPersonThrow/`에 있다. `BuildFirstPerson.cs`는 이미 연결된 프리팹에 중복 적용을 거절한다. 검증 후 Play를 종료했고 현재 B5 씬은 저장 변경이 없는 편집 모드다. 임시 검증 오브젝트와 테스트 물리 씬은 Play 종료로 정리했다.

## 변경 기록

- V0.01 (2026-11-17): Claude CLI 중단 작업 인계, 임시 1인칭 팔·투척 연결, 14개 물리 검사와 36개 동작 검사, 전후 화면과 한계 기록. 송예찬.
