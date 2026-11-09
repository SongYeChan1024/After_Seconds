from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[2]
start='mouse=Mouse.current;mouseWasEnabled=mouse!=null&&mouse.enabled;if(mouseWasEnabled)InputSystem.DisableDevice(mouse);'
end='if(mouseWasEnabled&&mouse!=null)InputSystem.EnableDevice(mouse);'
files=['SourceAssets/B3_StructureRepair/Play.cs','SourceAssets/B3_FullFloor/Play.cs','SourceAssets/B4_Finish/Play.cs']
for rel in files:
 p=R/rel;s=p.read_text(encoding='utf-8');assert s.count(start)==1 and s.count(end)==1,rel
 s=s.replace(start,'').replace(end,'').replace('static Mouse mouse;static bool mouseWasEnabled;','')
 s=s.replace('temporary mouse/look/focus settings restored','native mouse left enabled; temporary look/focus settings restored')
 # The existing PlayerLook component is temporarily disabled during movement checks;
 # there is no need to disable the shared native mouse device as well.
 p.write_text(s,encoding='utf-8')
 assert 'DisableDevice(mouse)' not in s and 'EnableDevice(mouse)' not in s
print('Removed native mouse toggling from:',files)
note='''2026-11-09 OnLook 후속 복구: Unity Input System의 실제 Mouse 장치에 DisabledInFrontend·DisabledInRuntime이 남아 입력이 차단된 것을 확인했다. OnLook 이벤트와 PlayerLook/CameraRoot 연결은 정상이었다. 장치를 활성화하고 Look 입력22회·좌우6.60도/상하3.30도 실제 회전,새 게임 오류0을 확인했다. 검수 도구의 마우스 임시 비활성화 복구 누락 가능성을 고려해 B3_StructureRepair/B3_FullFloor/B4_Finish의 Play.cs에서 마우스 장치 토글을 제거했다. 이후 검수에서 실제 Mouse/Keyboard 장치를 비활성화하지 말고, 종료 후 입력 장치와 시점 회전을 확인한다. 게임 C#·씬은 수정하지 않았으며 현재 사용자가 열어 둔 B3 저장 편집 상태를 유지한다. [진단 기록](SourceAssets/Diagnostics/OnLook_20261109/README.md). 작성자 송예찬.'''
for rel in ['AGENTS.md','CLAUDE.md']:
 p=R/rel;s=p.read_text(encoding='utf-8');title,rest=s.split('\n',1);assert 'V0.73' in title;p.write_text(title.replace('V0.73','V0.74')+'\n\n'+note+'\n'+rest+'\n- V0.74 (2026-11-09): OnLook 입력 장치 복구와 검수 도구의 마우스 비활성화 제거. 송예찬.\n',encoding='utf-8')
p=R/'SourceAssets/B3_StructureRepair/README.md';s=p.read_text(encoding='utf-8');title,rest=s.split('\n',1);p.write_text(title.replace('V0.02','V0.03')+'\n\nOnLook 후속: 검수 후 마우스 장치 비활성 상태가 발견되어 활성화하고 실제 회전을 검증했다. Play.cs는 실제 마우스 장치를 끄지 않도록 보수했다. 기존 검사 결과의 기기 복구 문구만으로 입력 정상 여부를 판단하지 않는다. [진단](../Diagnostics/OnLook_20261109/README.md).\n'+rest+'\n- V0.03: 마우스 입력 복구·외부 검수 도구 보수.\n',encoding='utf-8')
(H/'README.md').write_text('''# OnLook 입력 장치 복구 기록 V0.01

작성자 송예찬 · 2026-11-09

사용자가 시점 회전이 갑자기 멈춘다고 보고했다. B3 저장 편집 씬에서 Mouse.enabled=false이며 InputDevice 플래그에 DisabledInFrontend와 DisabledInRuntime이 설정되어 있었다. 키보드는 활성 상태였다. 이것은 단순한 Game 뷰 포커스 해제와 구별되는 명시적 장치 비활성 상태다. Unity 로컬 패키지 InputDevice.cs·InputManager.cs에서 플래그 의미를 확인했다.

PlayerInput의 Look→PlayerPresenter.OnLook 이벤트, PlayerLook.enabled, cameraRoot/settings 참조와 Cinemachine Follow 연결은 정상이었다. InputSystem.EnableDevice(Mouse.current)로 활성화한 뒤 실제 Play에서 마우스 delta를 전달했다. Look performed22회,36프레임 진행,좌우6.60도·상하3.30도 회전,새 게임 오류0을 확인했다. Play 종료 후에도 Mouse.enabled=true이며 원래 B3 편집 상태·runInBackground=false로 복귀했다.

외부 이동 검수 도구가 실제 마우스를 비활성화한 뒤 종료 시 복구하는 구조였다. 이번 비활성 상태가 남은 정확한 호출/중단 시점은 로그에 없어 확정하지 못했다. 재발 경로를 제거하기 위해 B3_StructureRepair·B3_FullFloor·B4_Finish의 Play.cs에서 마우스 장치를 끄고 켜는 코드를 제거했다. 이동 검수 중 PlayerLook만 임시 중단하면 충분하다. 과거 검수 도구는 자동 재사용하지 않으며 실제 입력 장치를 비활성화하는 코드를 새 도구에 복사하지 않는다.

사용자 게임 C#·씬·프리팹은 변경하지 않았다. 복구는 에디터 입력 장치 상태에 적용됐으며 커밋·push하지 않았다. `edit_state.json`, `recovery.json`, `look_test.json`에 진단 근거를 보관한다.
''',encoding='utf-8')
