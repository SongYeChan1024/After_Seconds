using UnityEngine;
using UnityEngine.InputSystem;

public class PlayerPresenter : MonoBehaviour
{
    #region 의사코드

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

    // 동작을 시작하기 전에 필요한 참조 확보와 검증을 끝내기 위해
    // Start보다 앞선 초기화 단계인 Awake에서 처리한다.
    // 다른 컴포넌트의 Awake보다 먼저 실행된다는 뜻은 아니다.
    private void Awake()
    {
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


    // 활성화된 동안 매 프레임 저장된 입력으로 시야 회전과 이동을 요청한다.
    // 성능은 변수 개수보다 매 프레임 실제로 수행하는 연산, 검색, 메모리 할당 등의 비용에 좌우된다.
    private void Update()
    {
        // 좌우 입력으로 플레이어 전체를, 상하 입력으로 CameraRoot를 먼저 회전한다.
        // Motor는 이번 프레임에 회전한 플레이어의 방향을 기준으로 이동한다.
        playerLook.Rotate(lookInput);

        // 경과 시간은 그대로 전달한다. 속도에 시간을 곱해 이동량으로 바꾸는 계산은 Motor가 담당한다.
        playerMotor.Move(moveInput, Time.deltaTime);
    }

    // 이 컴포넌트나 게임 오브젝트가 비활성화될 때 호출된다. 씬 언로드로 제거될 때도 호출된다.
    // 일시정지, 사망, 컷씬 자체가 호출 조건은 아니다. 그 처리에서 실제로 비활성화해야 호출된다.
    // canceled는 입력 액션의 취소를 처리하고, 이 함수는 컴포넌트가 꺼지는 시점의 정리를 담당한다.
    private void OnDisable()
    {
        moveInput = Vector2.zero; // 재활성화할 때 이전 입력이 남지 않도록 초기화한다.
        lookInput = Vector2.zero; // 재활성화할 때 이전 입력이 남지 않도록 초기화한다.
    }
}
