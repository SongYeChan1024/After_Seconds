# Invector 기본 이동 애니메이션 보관 V0.01

2026-11-03 · 작성자 송예찬

사용자가 실습 중 확인한 걷기·뛰기 동작을 비교 후보로 보관한다. 기존 플레이어·씬·Animator Controller에는 연결하지 않았다.

## 보관한 클립

| 파일 | 원본 동작 | 길이 | 샘플 레이트 | 반복 |
| --- | --- | ---: | ---: | --- |
| `Invector_Walk.anim` | Walk · 전방 걷기 | 1.00초 | 30fps | 켬 |
| `Invector_Run.anim` | Run · 전방 달리기 | 약 0.66초 | 30fps | 켬 |
| `Invector_Sprint.anim` | Sprint · 전방 전력질주 | 약 0.52초 | 30fps | 켬 |

세 클립 모두 Humanoid이며 원본 곡선·키·루트 설정·반복 설정을 유지한 독립 `.anim`이다. 원본 FBX·Avatar·Invector 스크립트·Animator Controller를 함께 복사하지 않았다. 옆걸음·뒷걸음·점프는 이번 보관 범위에 포함하지 않는다.

## 출처와 추출

- 원본 프로젝트: Projects의 `Resources/Unity6.4_URPTPSControl`
- 원본 FBX: `Assets/URPTPSControl/3D Models/Animations/Basic_FreeMovement.fbx`
- 연결 확인: `Assets/URPTPSControl/Animator/Invector@BasicLocomotion.controller`의 자유 이동 Blend Tree
- 원본 GUID·클립 fileID·설정·해시·검수 결과: `source_manifest.json`

Unity 6000.4.0f1의 AssetDatabase에서 원본 AnimationClip을 복제해 직렬화했다. 클립마다 곡선 바인딩 130개, 원본과 곡선·설정 일치, 추출본의 외부 에셋 의존성 없음을 확인했다. 원본은 이동·삭제하지 않았다. 새 `.anim`의 GUID는 추출 시 생성한 값을 함께 보관한다.

## 이후 비교할 때

현재 사용하는 `Rigged_V0.3` 동작은 그대로 유지한다. 이 후보를 실제로 적용할 때는 대상 Humanoid Avatar의 유효성, 발 접지·루프·발 미끄러짐, 이동 속도와 재생 속도의 조합을 별도 검수한다. 반복 길이가 짧다고 현재 Motor에 바로 맞는 것으로 판단하지 않는다. 원본 루트 이동 설정도 보존했으므로 실제 연결 시 Apply Root Motion 정책을 확인한다.
