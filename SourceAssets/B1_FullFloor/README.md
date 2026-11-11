# B1 전체 정적 외형 제작 원본 V0.02

현재는 [B1 용도 보수](../B1_StaffDataRevision/README.md)가 최신이다.198배치와8인 회의장, B5/B4 실험체 경계가 현행이다. 아래174배치·시험 설비 설명은 초기 제작 이력이며 초기 생성기는 재실행하지 않는다. `layout.json`만 최종 배치로 동기화했다.

작성자: 송예찬 · 2026-11-11

사용자 요청으로 `Level_B1_Circular.unity`를 새로 제작했다. 13공동·3코어·22통로, 주요 프랍174개, 계단18m와 정적 승강기, 공동별 조명·안내선·반사·가림을 포함한다. [검수 보고서](../../Docs/Review/2026-11-11_B1_FullFloor/Review.md)와 [화면](../../Docs/Review/2026-11-11_B1_FullFloor/review.html)을 우선한다.

현재 씬은 제작·보정 적용 후 상태다. **Apply/Resume/Refine/CleanApply/Layout을 다시 실행하지 않는다.** `Resume`는 최초 제작 중 누락된 반경12용 CCTV 받침 참조를 수정했던 일회성 복구 기록이다. 최종 상태에서 실행하면 사용자 후속 편집을 잃는다. 필요한 대상만 지정해 보수한다.

- `plan.json`: 현행 Decision 원본 좌표·명세와 T08 북측 곡선 진입을 기록한 초기 제작안. `layout.json`:174배치·작업 접근점·최종 조리/관제 배치가 반영된 현재 기준. `layout.py`와 `refine_plan.py`는 제작 이력이므로 재실행하지 않는다.
- `common.py`, `architecture.py`, `props.py`: Blender 제작 코드. 87개 건축 모델과12개 프랍 모델. 새 프랍은 두 LOD를 같은 FBX에 보관한다. 큰 `.blend` 사본이나 Unity YAML 메시 파생본 대신 재현 가능한 제작 코드와 작은 FBX를 보관한다.
- `textures.py`:512×256 정적 장비 화면3개. `refine_plan.py`:512×128 출입 표지16개. 공용 바닥 텍스처와 재질·설비를 참조한다.
- `seam_repair.py`:22개 복도 끝을 돔 외벽 바깥에서 맞물리게 보수하고, 계단 챌판의 디딤판 겹침을 제거한 국소 제작 이력. 원본 `architecture.py`에도 수정이 반영돼 있다.
- `local_repair_plan.py`, `CleanExport.cs`, `clean_meshes.py`, `CleanApply.cs`:공용 원본을 바꾸지 않고 B1에 보정 FBX8개를 만들어319개 렌더러에 공유 적용한 이력. 원본 노멀·UV·재질 슬롯·메시 경계와 충돌체 보존. CCTV 가스켓 간격13곳과 싱크 지지대12개도 이 단계에 보완했다.
- `geometry_scan`, `geometry_final`, `geometry_verified`:초기 후보·보수 후 후보·0.05mm 실제 평면 거리 검증. 최종 중복0·내부 겹침0·정밀 겹침0. 전체가 런타임 시각 무결성 보증이라는 뜻은 아니다.
- `Review.cs`, `Details.cs`, `Play.cs`, `LiveFrame.cs`, `Finish.Audit`:외부 검수용. Assets에 넣거나 런타임 기능으로 사용하지 않는다. 실제 입력 장치를 비활성화하지 않는다. Play는 프레임 진행·이동·새 오류를 함께 확인한다.
- `protected_before.json`:기존 씬·게임 코드·Animator·B2 VARCO/냉각 펌프 보수178파일 기준 해시. 최종 비교는 검수 폴더의 `preservation.json`.

`Finish.Reflections`는 기존16개 프로브를 갱신한다. `Finish.Occlusion`은 최초 설정 전용이며, 후속 가림 갱신은 `Finish.Rebake`를 사용한다. 검수 캡처는 임시 카메라를 만든 뒤 저장된 B1 씬으로 돌아온다.

B1의 도착/전환 마커는 기능 연결을 위한 위치 표시다. 문·CCTV·승강기 작동, 실제1F 전환, 소품 획득, 경비 AI는 미구현이며 게임 C#/Player/Animator 직접 구현 방침은 그대로다. 사용자 외형 검수 후 지정 구역만 보수한다. 커밋·push는 이번에 요청하지 않았다.
