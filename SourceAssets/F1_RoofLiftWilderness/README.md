# 1F 천장·승강로·계단·황야 V0.01

작성자: 송예찬 · 2026-11-13

사용자가 요청한 구조·외형·가동 부품 분리 작업이다. 승강기 운행, 문 제어, 엔딩 재생 스크립트는 추가하지 않았다. 결과는 저장된 `Level_1F_Factory`에 있다. **이 폴더의 Apply/Import/Run을 현재 씬에서 일괄 재실행하지 않는다.** 개별 보수 이력까지 반영된 씬이 최신이다.

## 작업 내용

- C01/C02 철판 지붕과 C03/C04 콘크리트 천장, T01–T07 통로 천장의 네모난 결손을 불규칙한 파손 가장자리로 바꿨다. 철판 꺾임·노출 철근·남은 골조를 표현했다. VA/VB 연속 천장 보수는 유지하고 VL 천장은 승강탑 둘레로 개구부를 만들었다.
- VL은 고정 사각 승강로, 가이드레일, 피트 완충기, 승강칸, 균형추, 권상기 모터·브레이크, 4줄 로프와 도르래를 나눴다. 전실 쪽인 -Z에서 탑승한다.
- VB는 바닥을 실제로 열고 18m 계단·도착참·난간을 연결했다. `F1_VB_ArrivalFireDoor_01`의 문짝은 별도 경첩 피벗이다. 기존 B1 에셋은 수정하지 않고 1F 접속부에 맞춘 계단 복사본을 제작했다.
- 서쪽 출구 바깥에 마른 흙·자갈·덤불·돌·넓은 골짜기와 낮은 구릉을 배치했다. 근경 지형 1,536×1,280m, 먼 배경 지형 6,144×5,120m이며, 검수한 보행 길은 출구 밖 약 585m다. 하늘과 낮은 햇빛이 진행 방향에 보인다.

## 승강기 스크립트 연결 지점

루트: `1F_AbandonedFactory/1F_VL/F1_VL_LiftAssembly`, 월드 위치 `(44, 0, 29)`. 아래 수치는 루트 기준 Unity 미터다.

| 자식 | 용도·현재 상태 |
|---|---|
| `FixedShaft` | 승강로·레일·피트·권상기 받침·1F/B1 승강장 문. 고정 |
| `Car` | 현재 `(0, 0, -0.6)`. 승강칸·슬링·롤러·승강칸 문·조명 |
| `Counterweight` | 현재 `(-2.4, -17.2, -0.6)`. 균형추 프레임·블록 |
| `Sheave` | `(-1.2, 5.55, -0.6)`. 회전 피벗은 바퀴 중심, 회전축은 로컬 Z |
| `Ropes/FixedWrap` | 도르래 위쪽 반원 로프. 바퀴와 별도 |
| `Ropes/ToCar` | 상단 고정 피벗 `(0, 5.55, -0.6)`, 아래로 1m인 원본을 Y로 확대 |
| `Ropes/ToCounterweight` | 상단 고정 피벗 `(-2.4, 5.55, -0.6)`, 아래로 1m인 원본을 Y로 확대 |
| `Stop_1F`, `Stop_B1` | 승강칸 기준 정지 위치 Y=0 / -18 |

승강칸 이동 범위는 로컬 Y `-18…0`이다. 1:1 로프 배치로 `Counterweight.localPosition.y = -17.2 - Car.localPosition.y` 관계를 사용하도록 형상을 맞췄다. 로프 부착점은 각각 `Car/RopeAttachment`(승강칸 기준 Y=3.79), `Counterweight/RopeAttachment`(균형추 기준 Y=2.96)다. 세로 로프 길이는 상단 Y=5.55에서 부착점 Y를 뺀 값이다. 로프 오브젝트의 로컬 Y 스케일을 길이로 사용하면 된다. X/Z 스케일은 1을 유지한다.

승강칸의 `DoorLeft`, `DoorRight`와 고정 승강장 문은 로컬 X 방향으로 움직이는 독립 오브젝트다. 닫힘 중심 X는 `-0.655 / +0.655`, 현재 1F 열림 중심은 `-1.98 / +1.98`이다. B1 승강장 문은 닫힌 상태로 두었다. 승강칸 문 Z=-1.78은 Car 기준이고, 승강장 문 Z=-2.86은 승강로 기준이다. 움직이는 부품에 Animator·Rigidbody·게임 MonoBehaviour를 추가하지 않았다.

상부 슬링/로프 체결부 최고점 Y=3.79, 도르래 최저점 Y≈4.315로 약 0.525m를 확보했다. 천장 아랫면 Y=6.9다. 이 문서의 관계식은 연결용 설명이며 운행·속도·정지·문 연동은 사용자 후속 구현이다.

## 계단·엔딩 위치

- `1F_VB/F1_VB_ArrivalFireDoor_01/Frame`, `DoorLeftPivot`, `DoorRightPivot`: 좌우 문짝은 열림 100° / -100°. 피벗 회전 0°가 닫힘 형상이다.
- `1F_VB/F1_VB_StairConnection`: 1F 단독 씬에서 B1 높이 Y=-18까지 내려가는 실제 계단. B1 씬과의 additive 통합은 구현하지 않았다. 나중에 통합할 때 같은 위치의 B1 계단과 중복 표시하지 않도록 선택해야 한다.
- `WildernessEnding/EndingWalkStart`, `EndingWalkMid`, `FreedomVista`: 지형 표면에 둔 빈 Transform이다. 각각 X=-82 / -285 / -590, 시선은 서쪽이다. 엔딩 트리거·카메라·자막은 연결하지 않았다.

## 제작·검수 파일

`roofs.py`, `details.py`, `stairs.py`와 `meshlib.py`는 Blender 형상 제작 원본이다. `Apply.cs`는 첫 반입/구조 배치, `StairFix.cs`는 1F 전용 도착참 수정, `Finish.Headroom`은 최종 권상부 간격 수정이다. `Wilderness.cs`, `Horizon.cs`는 지형과 건조 표면 제작 이력이다. 새 지형은 공장 밖 원거리 LOD를 사용하고 공장 내부에만 가림 볼륨을 둔다.

`Review.cs`, `Verify.cs`, `FloorWalk.cs`, `Play.cs`는 Editor에서만 실행한 검수 도구다. `Assets` 안에 넣지 않았으며 게임에 등록되지 않는다. [검수 보고서](../../Docs/Review/2026-11-13_1F_RoofLiftWilderness/Review.md)와 [화면 비교](../../Docs/Review/2026-11-13_1F_RoofLiftWilderness/review.html)를 따른다.

원본 FBX는 기존 GUID를 유지해 교체했고 추가 재질 슬롯은 기존 1F 재질로 연결했다. B1/다른 층·Player/Animator·게임 스크립트·패키지/에디터 버전은 변경하지 않았다. 기존 토양 이미지 픽셀은 복사만 했고, 새 건조용 복사본의 알파를 TextureImporter에서 무시해 거친 흙의 강한 반사를 제거했다.

기계 배치 참고: [Otis 승강기 구성 자료](https://products.otis.com/hubfs/E-book%20Spanish/Modernizaci%C3%B3n%20de%20Ascensores%20-%20Tecnolog%C3%ADa%20que%20marca%20la%20diferencia.pdf?hsLang=es-co). 게임용 외형이며 실제 설비 제작 도면이 아니다.

변경 이력: V0.01 (2026-11-13) 사용자 네 가지 외형 요청 및 스크립트 인계 지점 정리. 송예찬.
