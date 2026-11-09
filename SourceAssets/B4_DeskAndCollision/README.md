# B4 기록대 및 B5·B4 통행 충돌 보수 V0.02

작성자 송예찬 · 2026-11-09

사용자가 지적한 `B4_E02_ProtocolTable_01`의 서류/모니터 지지대 겹침과 본체 부재, `B4_E02_TaskLightPole_13`·`B4_C02_TaskLightPole_15` 주변의 보이지 않는 충돌을 보수했다.

- `build.py` / `PD_ProtocolTable.blend`: 본체·키보드·마우스·서류함·배선·통풍구·단자·모서리 베벨이 포함된 새 정적 기록대. `Desk.cs`로 동일 모델 4곳의 시각 메시만 교체했다. 책상·의자 위치는 보존했다.
- `clean_desk.py`: 평가된 베벨에서 생긴 극미세 면을 제거한 최종 FBX 출력 단계. 최종 47,846tri, Unity 퇴화 면 0이다. 모델 재제작 시 `build.py` 다음 이 단계를 실행한다.
- `FixLights.cs`: 작업등 36개의 큰 BoxCollider를 받침·기둥·암·등기구·스위치 5개 형태로 분리했다. 원래 첫 Collider 컴포넌트는 보존했다. 현재 상태에 재실행하지 않는다.
- `CollisionSurvey.cs`: B5 762개, B4 442개 활성 충돌 오브젝트의 목록을 수집했다.
- `GhostAudit.cs`: 고유 키 큰 프랍 70종의 박스와 실제 시각 메시를 캡슐로 비교했다. 15종을 보수 대상으로 확인했다.
- `build_colliders.py` / `ApplyProxies.cs`: 원본 Blender 파트의 베벨 전 형상을 사용해 충돌 전용 FBX 15종(고유 47,340tri)을 생성하고, B5 10개·B4 45개에 정적 비볼록 MeshCollider를 적용했다. 원래 단일 박스는 비활성 보존했다. 시각 모델은 그대로다. 이후 동적 Rigidbody를 붙이는 경우 이 정적 충돌 형태를 그대로 사용하지 않는다.
- `RefineBounds.cs`와 `VerifyBounds.cs`는 중간 높이별 박스 실험 기록이다. **최종 씬은 `ApplyProxies.cs`의 충돌 메시를 사용한다. 이전 박스 실험을 재실행하지 않는다.**
- `LocalWalk.cs`: 사용자 지적 두 지점 앞과 E02 설비 사이 6방향 통행 검사. 작업등 이동은 필요하지 않았다.
- `ReviewB4.cs`·`ReviewB5.cs`: 실제 CharacterController의 기존 경로 331개·128개 재검사. `Play.cs`는 외부 임시 테스트 도구이며 게임 Assets에 들어가지 않는다.

모든 편집은 Unity 네이티브 API로 저장했다. 게임 스크립트, Player 설정, Layer Collision Matrix, 물리 전역 설정과 조명은 변경하지 않았다. 단순 통과를 위해 Collider를 통째로 제거하거나 플레이어를 작게 만들지 않았다.

최종 검수와 전후 사진은 `../../Docs/Review/2026-11-09_FloorSurfaceWear/`를 본다. 로컬 저장 상태이며 이번 작업의 커밋·push는 하지 않았다.

입력 장치 후속 보수: `input_devices.py`에 곡선 배선과 오른손 마우스, 키 배열을 담았다. `make_legends.py`로 문자 아틀라스를 생성하고 `RefreshDevices.cs`로 네이티브 적용했다. 제작 순서는 build → make_legends → clean_desk → RefreshDevices다. 이후 실험실 보강 단계에서 키 인쇄면 방향과 보고서 본문을 추가 수정한 `LB_RecordWorkstation`으로 교체했다. 현재 씬의 최신 결과는 `../B4_LabIdentity/README.md`를 따른다.
