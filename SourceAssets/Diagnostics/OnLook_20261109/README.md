# OnLook 입력 장치 복구 기록 V0.01

작성자 송예찬 · 2026-11-09

사용자가 시점 회전이 갑자기 멈춘다고 보고했다. B3 저장 편집 씬에서 Mouse.enabled=false이며 InputDevice 플래그에 DisabledInFrontend와 DisabledInRuntime이 설정되어 있었다. 키보드는 활성 상태였다. 이것은 단순한 Game 뷰 포커스 해제와 구별되는 명시적 장치 비활성 상태다. Unity 로컬 패키지 InputDevice.cs·InputManager.cs에서 플래그 의미를 확인했다.

PlayerInput의 Look→PlayerPresenter.OnLook 이벤트, PlayerLook.enabled, cameraRoot/settings 참조와 Cinemachine Follow 연결은 정상이었다. InputSystem.EnableDevice(Mouse.current)로 활성화한 뒤 실제 Play에서 마우스 delta를 전달했다. Look performed22회,36프레임 진행,좌우6.60도·상하3.30도 회전,새 게임 오류0을 확인했다. Play 종료 후에도 Mouse.enabled=true이며 원래 B3 편집 상태·runInBackground=false로 복귀했다.

외부 이동 검수 도구가 실제 마우스를 비활성화한 뒤 종료 시 복구하는 구조였다. 이번 비활성 상태가 남은 정확한 호출/중단 시점은 로그에 없어 확정하지 못했다. 재발 경로를 제거하기 위해 B3_StructureRepair·B3_FullFloor·B4_Finish의 Play.cs에서 마우스 장치를 끄고 켜는 코드를 제거했다. 이동 검수 중 PlayerLook만 임시 중단하면 충분하다. 과거 검수 도구는 자동 재사용하지 않으며 실제 입력 장치를 비활성화하는 코드를 새 도구에 복사하지 않는다.

사용자 게임 C#·씬·프리팹은 변경하지 않았다. 복구는 에디터 입력 장치 상태에 적용됐으며 커밋·push하지 않았다. `edit_state.json`, `recovery.json`, `look_test.json`에 진단 근거를 보관한다.
