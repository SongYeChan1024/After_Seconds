using UnityEngine;
using UnityEngine.InputSystem;

public class PlayerPresenter : MonoBehaviour
{
    #region 의사코드 Ver 0.1

    /*
    플레이어 입력을 이동과 시야 회전 기능에 연결하는 기능

    기억해둘 정보:
        PlayerMotor의 참조 — playerMotor
        PlayerLook의 참조 — playerLook
        현재 이동 입력값 — moveInput, 처음에는 (0, 0)
        현재 시야 입력값 — lookInput, 처음에는 (0, 0)

    초기화할 때 — Awake:
        인스펙터에서 연결한 PlayerMotor가 없다면:
            같은 게임 오브젝트에서 PlayerMotor를 찾아 보관한다

        그래도 PlayerMotor가 없다면:
            오류를 알리고 이 컴포넌트를 비활성화한다
            초기화를 중단한다

        인스펙터에서 연결한 PlayerLook이 없다면:
            같은 게임 오브젝트에서 PlayerLook을 찾아 보관한다

        그래도 PlayerLook이 없다면:
            오류를 알리고 이 컴포넌트를 비활성화한다
            초기화를 중단한다

    Move 입력 이벤트를 받으면 — OnMove:
        이 컴포넌트나 게임 오브젝트가 비활성화 상태라면:
            이번 이벤트 처리를 종료한다

        유효한 이동 입력이 발생하거나 입력값이 바뀌었다면 — performed:
            이벤트에서 2차원 입력값을 읽어 현재 이동 입력값으로 저장한다

        이동 입력이 취소되었다면 — canceled:
            현재 이동 입력값을 (0, 0)으로 바꾼다

    Look 입력 이벤트를 받으면 — OnLook:
        이 컴포넌트나 게임 오브젝트가 비활성화 상태라면:
            이번 이벤트 처리를 종료한다

        유효한 시야 입력이 발생하거나 입력값이 바뀌었다면 — performed:
            이벤트에서 2차원 입력값을 읽어 현재 시야 입력값으로 저장한다

        시야 입력이 취소되었다면 — canceled:
            현재 시야 입력값을 (0, 0)으로 바꾼다

    매 프레임 — Update:
        저장한 시야 입력값을 PlayerLook에 전달해 회전을 요청한다
            좌우 입력으로 플레이어 전체를 회전한다
            상하 입력으로 CameraRoot를 회전한다

        회전한 플레이어의 방향을 기준으로 이동하도록:
            저장한 이동 입력값과 이번 프레임의 경과 시간을
            PlayerMotor에 전달해 이동을 요청한다

        이동 입력이 (0, 0)이어도 중력 처리가 계속되도록
        이동 요청은 매 프레임 수행한다

    이 컴포넌트가 비활성화되면 — OnDisable:
        다시 활성화할 때 이전 입력값이 남지 않도록:
            현재 이동 입력값을 (0, 0)으로 초기화한다
            현재 시야 입력값을 (0, 0)으로 초기화한다
    */

    #endregion

    #region 의사코드 Ver 0.2 (애니메이션 처리)

    /*
    플레이어 입력을 이동·시야 회전·애니메이션 기능에 연결하는 기능

기억해둘 정보:
    PlayerMotor의 참조 — playerMotor
    PlayerLook의 참조 — playerLook
    PlayerAnimationSystem의 참조 — playerAnimationSystem
    현재 이동 입력값 — moveInput, 처음에는 (0, 0)
    현재 시야 입력값 — lookInput, 처음에는 (0, 0)

초기화할 때 — Awake:
    인스펙터에서 연결한 PlayerMotor가 없다면:
        같은 게임 오브젝트에서 PlayerMotor를 찾아 보관한다

    그래도 PlayerMotor가 없다면:
        오류를 알리고 이 컴포넌트를 비활성화한다
        초기화를 중단한다

    인스펙터에서 연결한 PlayerLook이 없다면:
        같은 게임 오브젝트에서 PlayerLook을 찾아 보관한다

    그래도 PlayerLook이 없다면:
        오류를 알리고 이 컴포넌트를 비활성화한다
        초기화를 중단한다

    인스펙터에서 연결한 PlayerAnimationSystem이 없다면:
        같은 게임 오브젝트에서 PlayerAnimationSystem을 찾아 보관한다

    그래도 PlayerAnimationSystem이 없다면:
        오류를 알리고 이 컴포넌트를 비활성화한다
        초기화를 중단한다

Move 입력 이벤트를 받으면 — OnMove:
    이 컴포넌트나 게임 오브젝트가 비활성화 상태라면:
        이번 이벤트 처리를 종료한다

    유효한 이동 입력이 발생하거나 입력값이 바뀌었다면 — performed:
        이벤트에서 2차원 입력값을 읽어 현재 이동 입력값으로 저장한다

    이동 입력이 취소되었다면 — canceled:
        현재 이동 입력값을 (0, 0)으로 바꾼다

Look 입력 이벤트를 받으면 — OnLook:
    이 컴포넌트나 게임 오브젝트가 비활성화 상태라면:
        이번 이벤트 처리를 종료한다

    유효한 시야 입력이 발생하거나 입력값이 바뀌었다면 — performed:
        이벤트에서 2차원 입력값을 읽어 현재 시야 입력값으로 저장한다

    시야 입력이 취소되었다면 — canceled:
        현재 시야 입력값을 (0, 0)으로 바꾼다

매 프레임 — Update:
    저장한 시야 입력값을 PlayerLook에 전달해 회전을 요청한다
        좌우 입력으로 플레이어 전체를 회전한다
        상하 입력으로 CameraRoot를 회전한다

    회전한 플레이어의 방향을 기준으로 이동하도록:
        저장한 이동 입력값과 이번 프레임의 경과 시간을
        PlayerMotor에 전달해 이동을 요청한다

    이동 입력이 (0, 0)이어도 중력 처리가 계속되도록
    이동 요청은 매 프레임 수행한다

    현재 이동 입력이 (0, 0)이 아니라면:
        이동 여부를 true로 판단한다
    그렇지 않다면:
        이동 여부를 false로 판단한다

    판단한 이동 여부를
    playerAnimationSystem의 isMove에 전달한다

이 컴포넌트가 비활성화되면 — OnDisable:
    다시 활성화할 때 이전 입력값이 남지 않도록:
        현재 이동 입력값을 (0, 0)으로 초기화한다
        현재 시야 입력값을 (0, 0)으로 초기화한다

    PlayerAnimationSystem이 연결되어 있다면:
        isMove에 false를 전달해 이동 애니메이션 상태를 초기화한다
    */

    #endregion

    #region 의사코드 Ver 0.3 (스프린트 추가)

    /*
    플레이어 입력을 이동·시야 회전·애니메이션 기능에 연결하는 기능
    (Ver 0.3: 앞으로 이동할 때만 누르는 동안 달리기)

기억해둘 정보:
    PlayerMotor의 참조 — playerMotor
    PlayerLook의 참조 — playerLook
    PlayerAnimationSystem의 참조 — playerAnimationSystem
    현재 이동 입력값 — moveInput, 처음에는 (0, 0)
    현재 시야 입력값 — lookInput, 처음에는 (0, 0)
    달리기 키를 누르고 있는지 보관하는 입력값 — sprintInput, 처음에는 false

초기화할 때 — Awake:
    (Ver 0.2와 같음)

Move 입력 이벤트를 받으면 — OnMove:
    (Ver 0.2와 같음)

Look 입력 이벤트를 받으면 — OnLook:
    (Ver 0.2와 같음)

Sprint 입력 이벤트를 받으면 — OnSprint:
    이 컴포넌트나 게임 오브젝트가 비활성화 상태라면:
        이번 이벤트 처리를 종료한다

    달리기 키를 눌렀다면 — performed:
        현재 스프린트 입력값을 true로 바꾼다
        (버튼 값은 float라서 bool로 읽지 않는다. performed가 왔다는 것이 곧 눌렀다는 뜻이다)

    달리기 키를 뗐다면 — canceled:
        현재 스프린트 입력값을 false로 바꾼다

매 프레임 — Update:
    저장한 시야 입력값을 PlayerLook에 전달해 회전을 요청한다
        좌우 입력으로 플레이어 전체를 회전한다
        상하 입력으로 CameraRoot를 회전한다

    스프린트 입력이 true이고, 앞으로 가는 입력(이동 입력의 y가 0보다 큼)이라면:
        달리기 여부를 true로 판단한다
    그렇지 않다면:
        달리기 여부를 false로 판단한다
        (뒤·옆으로 가거나 멈춰 있으면 Shift를 눌러도 달리지 않는다)

    회전한 플레이어의 방향을 기준으로 이동하도록:
        저장한 이동 입력값, 판단한 달리기 여부, 이번 프레임의 경과 시간을
        PlayerMotor에 전달해 이동을 요청한다

    이동 입력이 (0, 0)이어도 중력 처리가 계속되도록
    이동 요청은 매 프레임 수행한다

    현재 이동 입력이 (0, 0)이 아니라면:
        이동 여부를 true로 판단한다
    그렇지 않다면:
        이동 여부를 false로 판단한다

    판단한 이동 여부를 playerAnimationSystem의 isMove에 전달한다
    판단한 달리기 여부를 playerAnimationSystem의 isSprint에 전달한다
        (Motor와 애니메이션이 같은 판단 결과를 쓰도록 한 곳에서 판단한다)

이 컴포넌트가 비활성화되면 — OnDisable:
    다시 활성화할 때 이전 입력값이 남지 않도록:
        현재 이동 입력값을 (0, 0)으로 초기화한다
        현재 시야 입력값을 (0, 0)으로 초기화한다
        현재 스프린트 입력값을 false로 초기화한다

    PlayerAnimationSystem이 연결되어 있다면:
        isMove에 false를 전달해 이동 애니메이션 상태를 초기화한다
        isSprint에 false를 전달해 달리기 애니메이션 상태를 초기화한다
    */

    #endregion

    #region 의사코드 Ver 0.4 (앉기 토글 추가)

    /*
    (Ver 0.4: C를 누를 때마다 앉기 ↔ 일어서기. Ver 0.3에서 바뀐 부분만 적는다)

기억해둘 정보에 추가:
    이번에 앉기 키를 눌렀는지 — crouchTogglePressed, 처음에는 false
        (토글은 "누르고 있는 동안"이 아니라 "누른 순간"이 중요하므로,
         누른 순간을 표시해 두고 Update에서 한 번만 처리한 뒤 지운다)

Crouch 입력 이벤트를 받으면 — OnCrouch:
    이 컴포넌트나 게임 오브젝트가 비활성화 상태라면:
        이번 이벤트 처리를 종료한다
    앉기 키를 눌렀다면 — performed:
        앉기 키를 눌렀다고 표시한다
    (키를 뗄 때 — canceled — 는 토글이므로 아무것도 하지 않는다)

매 프레임 — Update 수정:
    저장한 시야 입력값을 PlayerLook에 전달해 회전을 요청한다

    앉기 키를 눌렀다는 표시가 있다면:
        표시를 지운다 (한 번 누르면 한 번만 처리)
        지금 앉아 있다면:
            Motor에 일어서기를 요청한다
                (머리 위가 막혀 있으면 Motor가 거절하고 앉은 채로 남는다)
        그렇지 않다면:
            Motor에 앉기를 요청한다

    Motor가 낮아진 몸 높이만큼 눈 높이도 낮추도록 PlayerLook에 전달한다

    (이하 Ver 0.3과 같음: 달리기 판단 → 이동 요청 → 애니메이션 전달
     앉아 있을 때 달리기 키를 누르면 Motor가 "앉아서 달리기 속도"를 고른다)

이 컴포넌트가 비활성화되면 — OnDisable 추가:
    앉기 키를 눌렀다는 표시를 지운다
    (앉아 있는 몸 상태 자체는 바꾸지 않는다. 다시 켰을 때 갑자기 일어서다 천장에 끼지 않게)
    */

    #endregion

    #region 의사코드 Ver 0.5 (점프 추가)

    /*
    (Ver 0.5: Space를 누른 순간 한 번 점프한다. Ver 0.4에서 바뀐 부분만 적는다
             지금 뛸 수 있는지(바닥에 있는지, 일어설 수 있는지)는 Motor가 판단하고,
             Presenter는 "눌렀다"는 사실만 전달한다)

기억해둘 정보에 추가:
    이번에 점프 키를 눌렀는지 — jumpPressed, 처음에는 false
        (점프도 "누르고 있는 동안"이 아니라 "누른 순간"이 중요하므로,
         누른 순간을 표시해 두고 Update에서 한 번만 처리한 뒤 지운다)

Jump 입력 이벤트를 받으면 — OnJump:
    이 컴포넌트나 게임 오브젝트가 비활성화 상태라면:
        이번 이벤트 처리를 종료한다
    점프 키를 눌렀다면 — performed:
        점프 키를 눌렀다고 표시한다
    (키를 뗄 때 — canceled — 는 아무것도 하지 않는다)

매 프레임 — Update 수정:
    저장한 시야 입력값을 PlayerLook에 전달해 회전을 요청한다

    (앉기 토글 처리는 Ver 0.4와 같음)

    점프 키를 눌렀다는 표시가 있다면:
        표시를 지운다 (한 번 누르면 한 번만 처리)
        Motor에 점프를 요청한다
            (공중이거나 낮은 통로 안이면 Motor가 거절하고 아무 일도 일어나지 않는다)

    Motor가 낮아진 몸 높이만큼 눈 높이도 낮추도록 PlayerLook에 전달한다
        (앉은 채로 점프해 일어섰다면 눈 높이도 여기서 함께 올라간다)

    (이하 Ver 0.4와 같음: 달리기 판단 → 이동 요청 → 애니메이션 전달
     점프 요청이 이동 요청보다 먼저여야 이번 프레임의 이동에 점프 속도가 반영된다)

이 컴포넌트가 비활성화되면 — OnDisable 추가:
    점프 키를 눌렀다는 표시를 지운다
    */

    #endregion

    #region 의사코드 Ver 0.6 (던지기 연결)

    /*
    (Ver 0.6: E로 던지기 자세를 켜고 끄고, 왼쪽 클릭을 누르고 있다가 떼면 던진다.
             조준 중에 오른쪽 클릭을 누르면 던지지 않고 취소한다. Ver 0.5에서 바뀐 부분만 적는다
             자세를 바꾸고 물건을 던지는 일은 PlayerThrow가 하고, Presenter는 누른 키를 전달만 한다)

기억해둘 정보에 추가:
    PlayerThrow의 참조 — playerThrow
    이번에 던지기 자세 키(E)를 눌렀는지 — throwStancePressed, 처음에는 false
    이번에 왼쪽 클릭을 눌렀는지 — attackPressed, 처음에는 false
    이번에 왼쪽 클릭을 뗐는지 — attackReleased, 처음에는 false
    이번에 오른쪽 클릭을 눌렀는지 — aimPressed, 처음에는 false
        (점프와 같은 방식이다. 누른 순간을 표시해 두고 Update에서 한 번만 처리한 뒤 지운다)

초기화할 때 — Awake 추가:
    인스펙터에서 연결한 PlayerThrow가 없다면:
        같은 게임 오브젝트에서 PlayerThrow를 찾아 보관한다
    그래도 PlayerThrow가 없다면:
        오류를 알리고 이 컴포넌트를 비활성화한다

ThrowStance 입력 이벤트를 받으면 — OnThrowStance:
    E를 눌렀다면 — performed: 던지기 자세 키를 눌렀다고 표시한다

Attack 입력 이벤트를 받으면 — OnAttack:
    왼쪽 클릭을 눌렀다면 — performed: 왼쪽 클릭을 눌렀다고 표시한다
    왼쪽 클릭을 뗐다면 — canceled: 왼쪽 클릭을 뗐다고 표시한다
        (던지기는 "누른 순간"과 "뗀 순간"이 둘 다 필요해서 표시가 두 개다)

Aim 입력 이벤트를 받으면 — OnAim:
    오른쪽 클릭을 눌렀다면 — performed: 오른쪽 클릭을 눌렀다고 표시한다

매 프레임 — Update 끝에 추가 (이동과 애니메이션 전달 뒤):
    던지기 자세 키를 눌렀다는 표시가 있다면:
        표시를 지우고 PlayerThrow에 던지기 자세 전환을 요청한다

    오른쪽 클릭을 눌렀다는 표시가 있다면:
        표시를 지운다
        지금 조준 중이라면: PlayerThrow에 조준 취소를 요청한다
        (조준 중이 아닐 때의 오른쪽 클릭은 확대 조준이다. 다음 버전에서 추가한다)

    왼쪽 클릭을 눌렀다는 표시가 있다면:
        표시를 지우고 PlayerThrow에 조준 시작을 요청한다
        (던지기 자세가 아니면 PlayerThrow가 아무것도 하지 않는다)

    왼쪽 클릭을 뗐다는 표시가 있다면:
        표시를 지우고 PlayerThrow에 던지기를 요청한다
        (조준 중이 아니면 PlayerThrow가 아무것도 하지 않는다)

    처리 순서의 이유:
        누름 → 뗌 순서로 처리해서, 짧게 눌렀다 떼어 한 프레임에 둘 다 들어와도 바로 던져진다
        이동 뒤에 처리해서, 이번 프레임에 움직인 자리와 돌린 시선 그대로 던진다

이 컴포넌트가 비활성화되면 — OnDisable 추가:
    던지기 관련 표시 네 개를 지운다
    PlayerThrow가 연결되어 있다면: 조준을 취소한다 (다시 켰을 때 갑자기 던지지 않게)
    */

    #endregion

    #region 의사코드 Ver 0.7 (확대 조준, 던지는 방식 전환, 궤적 표시 연결)

    /*
    (Ver 0.7: 오른쪽 클릭으로 확대 조준을 켜고 끄고, R로 위로/아래로 던지기를 바꾸고,
             조준하는 동안 궤적이 보이게 한다. Ver 0.6에서 바뀐 부분만 적는다)

기억해둘 정보에 추가:
    PlayerZoom의 참조 — playerZoom
    이번에 던지는 방식 키(R)를 눌렀는지 — throwModePressed, 처음에는 false

초기화할 때 — Awake 추가:
    PlayerZoom도 PlayerThrow와 같은 방식으로 찾고, 없으면 오류를 알리고 비활성화한다

ThrowMode 입력 이벤트를 받으면 — OnThrowMode:
    R을 눌렀다면 — performed: 던지는 방식 키를 눌렀다고 표시한다

매 프레임 — Update 수정:
    시야 입력에 PlayerZoom의 감도 비율을 곱해서 PlayerLook에 전달한다
        (확대 중에는 같은 마우스 움직임에도 화면이 크게 움직이므로 감도를 낮춘다)

    오른쪽 클릭을 눌렀다는 표시가 있다면 — 수정:
        지금 조준 중이라면: 조준을 취소한다 (Ver 0.6과 같음)
        조준 중이 아니고 물건을 들고 있다면: 확대 조준을 켜거나 끈다
            (같은 오른쪽 클릭이 "왼쪽 클릭을 누르기 전에는 확대, 누르는 중에는 취소"가 된다)

    던지는 방식 키를 눌렀다는 표시가 있다면:
        표시를 지우고 PlayerThrow에 던지는 방식 전환을 요청한다
        (던지기 자세가 아니면 PlayerThrow가 아무것도 하지 않는다)

    왼쪽 클릭을 뗐다는 표시가 있다면 — 수정:
        PlayerThrow에 던지기를 요청하고, 실제로 던졌다면 확대 조준을 푼다
            (던진 물건은 손을 떠났으므로 조준을 계속할 이유가 없다)

    맨 끝에서: PlayerThrow에 궤적을 새로 그리라고 요청한다
        (위의 입력 처리가 모두 끝난 뒤의 상태로 그린다. 조준 중이 아니면 PlayerThrow가 궤적을 숨긴다)

이 컴포넌트가 비활성화되면 — OnDisable 추가:
    던지는 방식 키 표시를 지운다
    PlayerZoom이 연결되어 있다면: 확대를 푼다
    */

    #endregion

    // 이동을 담당하는 Motor의 참조. 다른 클래스에서 직접 접근하지 못하도록 private으로 둔다.
    // SerializeField는 이 필드를 저장 대상으로 만들어 인스펙터에서 연결할 수 있게 한다.
    [SerializeField] private PlayerMotor playerMotor;

    [SerializeField] private PlayerLook playerLook; // 시야 회전을 담당하는 Look의 참조. 다른 클래스에서 직접 접근하지 못하도록 private으로 둔다.

    // 현재 시야 입력값을 보관한다. 처음에는 입력이 없는 (0, 0)으로 시작한다.
    // 비활성화 시 남아 있는 입력값을 지우는 처리는 이 Presenter의 OnDisable에서 수행한다.
    // PlayerLook이 초기화하는 pitchAngle은 입력값이 아니라 현재 상하 회전 각도이다.
    private Vector2 lookInput = Vector2.zero;

    // 현재 이동 입력을 보관한다. Vector2.zero는 이동 입력이 없는 (0, 0)이다.
    private Vector2 moveInput = Vector2.zero;

    [SerializeField] private PlayerAnimationSystem playerAnimationSystem;
    // Presenter가 판단한 이동 여부를 전달받아
    // Animator의 이동 상태를 갱신하는 PlayerAnimationSystem의 참조.

    private bool sprintInput = false; // 달리기 키를 누르고 있는지 보관한다. 처음에는 누르지 않은 false로 시작한다.

    // 이번에 앉기 키(C)를 눌렀는지 표시한다. 토글이라 "누른 순간"만 필요하므로
    // OnCrouch에서 true로 표시하고, Update에서 한 번 처리한 뒤 바로 false로 지운다.
    private bool crouchTogglePressed = false;

    // 이번에 점프 키(Space)를 눌렀는지 표시한다. 점프도 "누른 순간"만 필요하므로
    // OnJump에서 true로 표시하고, Update에서 한 번 처리한 뒤 바로 false로 지운다.
    private bool jumpPressed = false;

    // 던지기를 담당하는 PlayerThrow의 참조. 자세 전환과 던지기는 PlayerThrow가 하고, 여기서는 누른 키만 전달한다.
    [SerializeField] private PlayerThrow playerThrow;

    // 던지기 관련 키를 "이번에 눌렀는지/뗐는지" 표시한다. 점프와 같은 방식으로
    // 입력 이벤트에서 true로 표시하고, Update에서 한 번 처리한 뒤 바로 false로 지운다.
    // 최신 의사코드(2026-11-17): 좌클릭 누름 → 자동 준비, 해제 → 즉시1회 투척.
    // E/조준 중 우클릭 취소를 먼저 처리한다. 같은 프레임의 좌클릭 시작/해제도 취소가 우선한다.
    // R은 준비 전에도 방식을 고른다. 입력 맵 비활성화에 의한 canceled는 투척으로 처리하지 않는다.
    private bool throwStancePressed = false; // E: 투척 취소(이름/기존 바인딩 유지)
    private bool attackPressed = false;      // 왼쪽 클릭을 누른 순간: 조준 시작
    private bool attackReleased = false;     // 왼쪽 클릭을 뗀 순간: 던지기
    private bool aimPressed = false;         // 오른쪽 클릭을 누른 순간: 조준 중이면 취소, 아니면 확대 조준
    private bool aimReleased;
    private bool throwModePressed = false;   // R: 위로 던지기 ↔ 아래로 던지기
    private InputAction attackAction;        // 물리 버튼 해제와 입력 맵 해제를 구분할 현재 액션
    private PlayerInventory inventory;
    private bool interactPressed, dropPressed;
    private int selectionStep;

    // 확대 조준을 담당하는 PlayerZoom의 참조. 언제 확대해도 되는지는 여기서 판단하고, 확대 자체는 PlayerZoom이 한다.
    [SerializeField] private PlayerZoom playerZoom;

    // 동작을 시작하기 전에 필요한 참조 확보와 검증을 끝내기 위해
    // Start보다 앞선 초기화 단계인 Awake에서 처리한다.
    // 다른 컴포넌트의 Awake보다 먼저 실행된다는 뜻은 아니다.
    private void Awake()
    {
        inventory = GetComponent<PlayerInventory>();
        if (playerMotor == null) // 인스펙터에서 연결한 Motor가 없다면 같은 오브젝트에서 찾는다.
        {
            playerMotor = GetComponent<PlayerMotor>(); // 찾은 컴포넌트의 참조를 보관한다.
        }

        if (playerMotor == null) // 같은 오브젝트에서도 Motor를 찾지 못했다면 갱신을 시작하지 않는다.
        {
            Debug.LogError("플레이어에 PlayerMotor 컴포넌트를 연결해야 합니다."); // 설정 누락을 알린다.
            // 이후 Update 호출을 막는다. 현재 실행 중인 함수를 즉시 끝내는 명령은 아니다.
            enabled = false;
            return; // Awake() 종료
        }

        if (playerLook == null) // 인스펙터에서 연결한 Look이 없다면 같은 오브젝트에서 찾는다.
        {
            playerLook = GetComponent<PlayerLook>(); // 찾은 컴포넌트의 참조를 보관한다.
        }

        if (playerLook == null) // 같은 오브젝트에서도 Look을 찾지 못했다면 갱신을 시작하지 않는다.
        {
            Debug.LogError("플레이어에 PlayerLook 컴포넌트를 연결해야 합니다."); // 설정 누락을 알린다.
            enabled = false; // 이후 Update 호출을 막는다. 현재 실행 중인 함수를 즉시 끝내는 명령은 아니다.
            return; // Awake() 종료
        }

        if (playerAnimationSystem == null) // 인스펙터에서 연결한 AnimationSystem이 없다면 같은 오브젝트에서 찾는다.
        {
            playerAnimationSystem = GetComponent<PlayerAnimationSystem>(); // 찾은 컴포넌트의 참조를 보관한다.
        }

        if (playerAnimationSystem == null) // 같은 오브젝트에서도 AnimationSystem을 찾지 못했다면 갱신을 시작하지 않는다.
        {
            Debug.LogError("플레이어에 PlayerAnimationSystem 컴포넌트를 연결해야 합니다."); // 설정 누락을 알린다.
            enabled = false; // 이후 Update 호출을 막는다. 현재 실행 중인 함수를 즉시 끝내는 명령은 아니다.
            return; // Awake() 종료
        }

        if (playerThrow == null) // 인스펙터에서 연결한 PlayerThrow가 없다면 같은 오브젝트에서 찾는다.
        {
            playerThrow = GetComponent<PlayerThrow>(); // 찾은 컴포넌트의 참조를 보관한다.
        }

        if (playerThrow == null) // 같은 오브젝트에서도 PlayerThrow를 찾지 못했다면 갱신을 시작하지 않는다.
        {
            Debug.LogError("플레이어에 PlayerThrow 컴포넌트를 연결해야 합니다."); // 설정 누락을 알린다.
            enabled = false; // 이후 Update 호출을 막는다.
            return; // Awake() 종료
        }

        if (playerZoom == null) // 인스펙터에서 연결한 PlayerZoom이 없다면 같은 오브젝트에서 찾는다.
        {
            playerZoom = GetComponent<PlayerZoom>(); // 찾은 컴포넌트의 참조를 보관한다.
        }

        if (playerZoom == null) // 같은 오브젝트에서도 PlayerZoom을 찾지 못했다면 갱신을 시작하지 않는다.
        {
            Debug.LogError("플레이어에 PlayerZoom 컴포넌트를 연결해야 합니다."); // 설정 누락을 알린다.
            enabled = false; // 이후 Update 호출을 막는다.
            return; // Awake() 종료
        }
    }

    // Player Input의 Move 입력을 처리하기 위해 만든 전용 함수.
    // context에서 이번 입력 이벤트의 상태와 값을 읽는다.
    public void OnMove(InputAction.CallbackContext context)
    {
        // 컴포넌트나 게임 오브젝트가 비활성화 상태라면 입력을 처리하지 않는다.
        if (!isActiveAndEnabled)
        {
            return; // 이번 OnMove 호출을 즉시 종료한다.
        }

        // 현재 Move 액션에서는 입력이 시작되거나 0이 아닌 입력값이 바뀔 때 발생한다.
        // 같은 입력을 유지하는 동안 매 프레임 발생하는 것은 아니다.
        if (context.performed)
        {
            moveInput = context.ReadValue<Vector2>(); // 이번 입력값을 복사해 다음 프레임에도 사용할 수 있게 보관한다.

        }
        // 키를 놓아 입력이 0으로 돌아오거나, 진행 중인 액션이 비활성화되는 등으로 취소된 경우.
        else if (context.canceled)
        {
            moveInput = Vector2.zero; // 이후 프레임에 수평 이동을 요청하지 않도록 입력을 초기화한다.
        }
    }

    public void OnLook(InputAction.CallbackContext context) // Player Input의 Look 입력을 처리하기 위해 만든 전용 함수.
                                                            // context에서 이번 입력 이벤트의 상태와 값을 읽는다.
    {
        if (!isActiveAndEnabled) // 컴포넌트나 게임 오브젝트가 비활성화 상태라면
        {
            return; // 종료
        }

        if (context.performed) // Look 액션에 유효한 입력이 발생하거나 입력값이 바뀌면
        {
            // 이벤트의 시야 입력값을 복사해 Update에서 사용할 수 있게 보관한다.
            // 실제 회전은 Update가 호출하는 PlayerLook.Rotate에서 수행한다.
            lookInput = context.ReadValue<Vector2>();
        }

        // 시야 입력값이 0으로 돌아오거나, 진행 중인 Look 액션이 비활성화되어 취소된 경우.
        else if (context.canceled)
        {
            lookInput = Vector2.zero; // 이후 프레임에 추가 회전량이 없도록 입력을 초기화한다.
        }
    }

    public void OnSprint(InputAction.CallbackContext context) // Player Input의 Sprint 입력을 처리하기 위해 만든 전용 함수.
    {
        if (!isActiveAndEnabled) // 컴포넌트나 게임 오브젝트가 비활성화 상태라면
        {
            return; // 종료
        }

        if (context.performed) // 달리기 키를 눌렀다면
        {
            // 버튼 값은 float라서 ReadValue<bool>()로 읽으면 실행 중 오류가 난다.
            // performed가 왔다는 것 자체가 눌렀다는 뜻이므로 true를 바로 저장한다.
            sprintInput = true;
        }
        else if (context.canceled) // 달리기 키를 뗐다면
        {
            sprintInput = false; // 이후 프레임에 달리기 상태가 남지 않도록 초기화한다.
        }
    }

    public void OnCrouch(InputAction.CallbackContext context) // Player Input의 Crouch 입력을 처리하기 위해 만든 전용 함수.
    {
        if (!isActiveAndEnabled) // 컴포넌트나 게임 오브젝트가 비활성화 상태라면
        {
            return; // 종료
        }

        if (context.performed) // 앉기 키를 누른 순간
        {
            // 토글이므로 "눌렀다"는 표시만 남긴다. 앉을지 일어설지는 Update에서 정한다.
            crouchTogglePressed = true;
        }
        // 키를 뗄 때(canceled)는 토글 방식이라 아무것도 하지 않는다.
    }

    public void OnJump(InputAction.CallbackContext context) // Player Input의 Jump 입력을 처리하기 위해 만든 전용 함수.
    {
        if (!isActiveAndEnabled) // 컴포넌트나 게임 오브젝트가 비활성화 상태라면
        {
            return; // 종료
        }

        if (context.performed) // 점프 키를 누른 순간
        {
            // "눌렀다"는 표시만 남긴다. 실제로 뛸 수 있는지는 Update에서 Motor가 판단한다.
            jumpPressed = true;
        }
        // 키를 뗄 때(canceled)는 아무것도 하지 않는다.
    }

    public void OnThrowStance(InputAction.CallbackContext context) // Player Input의 ThrowStance(E) 입력을 처리하기 위해 만든 전용 함수.
    {
        if (!isActiveAndEnabled) // 컴포넌트나 게임 오브젝트가 비활성화 상태라면
        {
            return; // 종료
        }

        if (context.performed) // E를 누른 순간
        {
            throwStancePressed = true; // "취소 키를 눌렀다"는 표시만 남긴다.
        }
    }

    public void OnAttack(InputAction.CallbackContext context) // Player Input의 Attack(왼쪽 클릭) 입력을 처리하기 위해 만든 전용 함수.
    {
        if (!isActiveAndEnabled) // 컴포넌트나 게임 오브젝트가 비활성화 상태라면
        {
            return; // 종료
        }

        attackAction = context.action;
        if (context.performed) // 왼쪽 클릭을 누른 순간
        {
            attackPressed = true; // 조준 시작을 요청할 표시
        }
        else if (context.canceled) // 왼쪽 클릭에서 손을 뗀 순간
        {
            attackReleased = true; // 던지기를 요청할 표시
        }
    }

    public void OnAim(InputAction.CallbackContext context) // Player Input의 Aim(오른쪽 클릭) 입력을 처리하기 위해 만든 전용 함수.
    {
        if (!isActiveAndEnabled) // 컴포넌트나 게임 오브젝트가 비활성화 상태라면
        {
            return; // 종료
        }

        if (context.performed) // 오른쪽 클릭을 누른 순간
        {
            aimPressed = true; // 조준 중이면 취소, 아니면 확대 조준. 어느 쪽인지는 Update에서 정한다.
            aimReleased = false;
        }
        else if (context.canceled) aimReleased = true;
    }

    public void OnThrowMode(InputAction.CallbackContext context) // Player Input의 ThrowMode(R) 입력을 처리하기 위해 만든 전용 함수.
    {
        if (!isActiveAndEnabled) // 컴포넌트나 게임 오브젝트가 비활성화 상태라면
        {
            return; // 종료
        }

        if (context.performed) // R을 누른 순간
        {
            throwModePressed = true; // "눌렀다"는 표시만 남긴다. 던지기 자세인지는 PlayerThrow가 판단한다.
        }
    }

    // 의사코드: F/Q/휠 입력을 한 번 기록 → Update에서 소지품 처리 → 같은 프레임 투척 취소 우선.
    public void OnInteract(InputAction.CallbackContext context) { if (isActiveAndEnabled && context.performed) interactPressed = true; }
    public void OnDrop(InputAction.CallbackContext context) { if (isActiveAndEnabled && context.performed) dropPressed = true; }
    public void OnPrevious(InputAction.CallbackContext context) { if (isActiveAndEnabled && context.performed) selectionStep--; }
    public void OnNext(InputAction.CallbackContext context) { if (isActiveAndEnabled && context.performed) selectionStep++; }

    // 활성화된 동안 매 프레임 저장된 입력으로 시야 회전과 이동을 요청한다.
    // 성능은 변수 개수보다 매 프레임 실제로 수행하는 연산, 검색, 메모리 할당 등의 비용에 좌우된다.

    private void Update()
    {
        // 좌우 입력으로 플레이어 전체를, 상하 입력으로 CameraRoot를 먼저 회전한다.
        // Motor는 이번 프레임에 회전한 플레이어의 방향을 기준으로 이동한다.
        // 확대 조준 중에는 같은 마우스 움직임에도 화면이 크게 움직이므로, 감도 비율을 곱해 낮춘다.
        // 확대하지 않았을 때는 비율이 1이라 입력이 그대로 전달된다.
        playerLook.Rotate(lookInput * playerZoom.SensitivityScale);

        // 앉기 토글: C를 누른 순간 한 번만 처리한다.
        if (crouchTogglePressed)
        {
            crouchTogglePressed = false; // 표시를 지워서 다음 프레임에 또 처리되지 않게 한다.

            if (playerMotor.IsCrouching) // 앉아 있다면 일어서기를 요청한다.
            {
                // 머리 위가 막혀 있으면 Motor가 false를 돌려주고 앉은 채로 남는다.
                // (지금은 실패해도 따로 할 일이 없어서 결과를 쓰지 않는다)
                playerMotor.TryStandUp();
            }
            else // 서 있다면 앉기를 요청한다.
            {
                playerMotor.Crouch();
            }
        }

        // 점프: Space를 누른 순간 한 번만 처리한다.
        // 앉기 토글 뒤에 두어, 같은 프레임에 C와 Space를 함께 눌러도 자세가 먼저 정해진 뒤 점프를 판단한다.
        if (jumpPressed)
        {
            jumpPressed = false; // 표시를 지워서 다음 프레임에 또 처리되지 않게 한다.

            // 공중이거나 낮은 통로 안이면 Motor가 거절하고 아무 일도 일어나지 않는다.
            // 아래의 Move보다 먼저 불러야 이번 프레임의 이동에 점프 속도가 반영된다.
            playerMotor.Jump();
        }

        // 몸이 낮아진 만큼 눈 높이(CameraRoot)도 낮춘다. 서 있으면 0이라 원래 높이로 돌아간다.
        // 앉은 채로 점프해 일어섰다면 눈 높이도 여기서 함께 올라간다.
        playerLook.SetEyeDrop(playerMotor.CrouchHeightDrop);

        // 달리기 키를 누르고 있고, 앞으로 가는 입력(y > 0)일 때만 달리기로 판단한다.
        // 뒤·옆으로 가거나 멈춰 있으면 false가 된다.
        // Motor와 애니메이션이 같은 결과를 쓰도록 여기서 한 번만 판단한다.
        bool isSprinting = sprintInput && moveInput.y > 0f;

        // 경과 시간은 그대로 전달한다. 속도에 시간을 곱해 이동량으로 바꾸는 계산은 Motor가 담당한다.
        // 달리기 여부에 따라 어떤 속도를 쓸지도 Motor가 고른다.
        playerMotor.Move(moveInput, isSprinting, Time.deltaTime);

        // 입력 → Motor에서 자세 확정 → 같은 자세/달리기 결과를 Animator에 전달한다.
        // 천장에 막혀 일어서지 못하면 IsCrouching은 true이므로 애니메이션도 앉아 있는다.
        playerAnimationSystem.SetLocomotion(moveInput, isSprinting, playerMotor.IsCrouching, Time.deltaTime);

        // ── 던지기 ──
        // 이동과 시선 회전이 끝난 뒤에 처리해서, 이번 프레임에 움직인 자리와 돌린 시선 그대로 던진다.

        // E는 취소만 한다. 액션 맵 해제로 발생한 canceled도 물리적인 버튼 해제 투척과 구분한다.
        bool inventoryInput = interactPressed || dropPressed || selectionStep != 0;
        if (inventory != null && inventory.isActiveAndEnabled && inventoryInput)
        {
            playerThrow.ExitStance();
            if (dropPressed) inventory.TryDrop();
            else if (interactPressed) inventory.TryPickup();
            else inventory.SelectRelative(selectionStep);
            playerZoom.SetZoomed(false);
        }
        interactPressed = dropPressed = false; selectionStep = 0;
        bool cancelThrowThisFrame = inventoryInput || throwStancePressed || (attackAction != null && !attackAction.enabled);
        throwStancePressed = false;
        if (cancelThrowThisFrame) playerThrow.ExitStance();

        // 오른쪽 클릭: 왼쪽 클릭을 누르고 조준하는 중이라면 던지지 않고 취소한다.
        // 가늠자가 있는 물건: 우클릭 동안만 자세를 유지한다. 조준 중 좌클릭이 투척으로 이어지지 않게 한다.
        bool hasSights = playerThrow.HeldItem != null && (playerThrow.HeldItem.HasIronSights ||
            (inventory && inventory.Selected && inventory.Selected.Ability));
        bool sightInput = hasSights && (aimPressed || playerZoom.IsZoomed);
        if (hasSights)
        {
            if (aimPressed && !cancelThrowThisFrame)
            {
                playerThrow.ExitStance();
                playerZoom.SetZoomed(true);
            }
            if (attackPressed && !cancelThrowThisFrame && playerZoom.IsZoomed && inventory != null)
                inventory.UseAimedItem();
            if (aimReleased) playerZoom.SetZoomed(false);
            cancelThrowThisFrame |= sightInput;
            aimPressed = false;
        }
        else if (aimPressed)
        {
            aimPressed = false;

            if (playerThrow.IsAiming || attackPressed) // 같은 프레임의 좌클릭 누름도 취소 우선
            {
                cancelThrowThisFrame = true;
                playerThrow.ExitStance(); // 새 좌클릭 전까지 다시 준비하지 않는다.
            }
            else if (playerThrow.HasHeldItem) // 조준 중이 아니고, 물건을 들고 있다면
            {
                // 확대 조준을 켜거나 끈다. 던지기 자세가 아니어도 물건을 들고 있으면 된다.
                playerZoom.Toggle();
            }
        }
        aimReleased = false;

        // R: 물건을 들고 있으면 준비 전에도 위/아래 방식을 고를 수 있다.
        if (throwModePressed)
        {
            throwModePressed = false;
            playerThrow.ToggleThrowMode();
        }

        // 왼쪽 클릭을 누른 순간: E 없이 자동으로 준비하고 조준을 시작한다.
        if (attackPressed)
        {
            attackPressed = false;
            if (!cancelThrowThisFrame) playerThrow.BeginAim();
        }

        // 왼쪽 클릭을 뗀 순간: 던진다. 조준 중이 아니면(취소했다면) PlayerThrow가 아무것도 하지 않는다.
        // "누름"을 "뗌"보다 먼저 처리하므로, 짧게 눌렀다 떼어 한 프레임에 둘 다 들어와도 바로 던져진다.
        if (attackReleased)
        {
            attackReleased = false;

            // ReleaseThrow는 실제로 던졌으면 true를 돌려준다.
            if (!cancelThrowThisFrame && playerThrow.ReleaseThrow())
            {
                playerZoom.SetZoomed(false); // 던진 물건은 손을 떠났으므로 확대 조준을 푼다.
            }
        }

        // 위의 입력 처리가 모두 끝난 뒤의 상태로 궤적을 그린다.
        // 조준 중이면 지금 시선 방향의 궤적을 보여 주고, 아니면 PlayerThrow가 궤적을 숨긴다.
        // 궤적은 손 표시가 갱신된 뒤 PlayerThrow.LateUpdate에서 그린다.
    }


    // 이 컴포넌트나 게임 오브젝트가 비활성화될 때 호출된다. 씬 언로드로 제거될 때도 호출된다.
    // 일시정지, 사망, 컷씬 자체가 호출 조건은 아니다. 그 처리에서 실제로 비활성화해야 호출된다.
    // canceled는 입력 액션의 취소를 처리하고, 이 함수는 컴포넌트가 꺼지는 시점의 정리를 담당한다.
    private void OnDisable()
    {
        moveInput = Vector2.zero; // 재활성화할 때 이전 입력이 남지 않도록 초기화한다.
        lookInput = Vector2.zero; // 재활성화할 때 이전 입력이 남지 않도록 초기화한다.
        sprintInput = false;      // 재활성화할 때 달리기 입력이 남지 않도록 초기화한다.
        crouchTogglePressed = false; // 처리하지 못한 앉기 키 표시를 지운다. 앉아 있는 몸 상태는 그대로 둔다.
        jumpPressed = false;         // 처리하지 못한 점프 키 표시를 지운다. 다시 켰을 때 갑자기 뛰지 않게 한다.

        // 처리하지 못한 던지기 관련 표시를 지운다.
        throwStancePressed = false;
        attackPressed = false;
        attackReleased = false;
        attackAction = null;
        interactPressed = dropPressed = false; selectionStep = 0;
        aimPressed = false;
        aimReleased = false;

        if (playerThrow != null) // PlayerThrow가 연결되어 있다면
        {
            playerThrow.ExitStance(); // 재활성화 뒤 조준/자세가 남지 않게 한다.
            playerThrow.RefreshTrajectory(false); // 조준이 취소됐으므로 화면에 남은 궤적을 숨긴다.
        }

        throwModePressed = false; // 처리하지 못한 던지는 방식 키 표시를 지운다.

        if (playerZoom != null) // PlayerZoom이 연결되어 있다면
        {
            playerZoom.SetZoomed(false); // 확대된 채로 남지 않게 푼다.
        }

        if (playerAnimationSystem != null) // AnimationSystem이 연결되어 있다면
        {
            playerAnimationSystem.ResetLocomotion(); // 자세를 유지하고 이동·달리기와 보간값을 초기화한다.
        }
    }
}
