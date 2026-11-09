using UnityEngine;

public class PlayerAnimationSystem : MonoBehaviour
{
    #region 의사코드

    /*
    플레이어의 이동 애니메이션 상태를 전달하는 기능

    기억해둘 정보:
        새 V0.3 모델의 Animator 참조 — animator

    초기화할 때 — Awake:
        인스펙터에 Animator가 연결되어 있지 않다면:
            오류를 알린다
            이 컴포넌트를 비활성화한다
            초기화를 종료한다

        Animator의 "IsMoving"을 false로 초기화한다
        Animator의 "IsSprint"를 false로 초기화한다
            (이름은 Player_Animator의 파라미터 이름과 글자까지 같아야 한다)

    이동 상태를 전달받으면 — isMove:
        이 컴포넌트나 게임 오브젝트가 비활성화 상태라면:
            이번 요청 처리를 종료한다

        전달받은 이동 여부를
        Animator의 "IsMoving" 값으로 설정한다

    달리기 상태를 전달받으면 — isSprint:
        이 컴포넌트나 게임 오브젝트가 비활성화 상태라면:
            이번 요청 처리를 종료한다

        전달받은 달리기 여부를
        Animator의 "IsSprint" 값으로 설정한다
            (달리는 중인지 판단은 Presenter가 하고, 여기서는 받은 값을 그대로 넣기만 한다)

    이 컴포넌트가 비활성화되면 — OnDisable:
        Animator가 연결되어 있다면:
            "IsMoving"을 false로 초기화한다
            "IsSprint"를 false로 초기화한다
    */

    #endregion
    #region 의사코드 Ver 0.2 (두 이동 Blend Tree 연결)
    /*
    Presenter에게 이동 입력, 확정된 달리기 여부, Motor의 실제 앉기 상태를 받는다.
    입력 길이는 0~1로 제한하고, 걷기는 0~1, 달리기는 0~2의 Speed로 전달한다.
        Speed는 m/s가 아니라 Blend Tree의 대기(0)·걷기(1)·달리기(2) 기준값이다.
    Speed와 방향은 짧은 시간에 걸쳐 보간한다. 자세 전환은 Animator가 블렌딩한다.
    Motor가 천장 때문에 일어서기를 거부했다면 IsCrouch도 true를 유지한다.
    비활성화 시 이동값만 초기화한다. 앉은 몸을 임의로 선 자세로 바꾸지 않는다.
    */
    #endregion
    [SerializeField] private Animator animator; // 애니메이터 컴포넌트 참조
    [SerializeField, Min(0f)] private float locomotionDampTime = 0.12f;
    [SerializeField, Min(0f)] private float directionDampTime = 0.1f;

    private static readonly int SpeedId = Animator.StringToHash("Speed");
    private static readonly int MoveXId = Animator.StringToHash("MoveX");
    private static readonly int MoveYId = Animator.StringToHash("MoveY");
    private static readonly int IsCrouchId = Animator.StringToHash("IsCrouch");
    private bool hasSpeedParameter; // Old 씬의 이전 컨트롤러는 기존 bool 전달을 계속 지원한다.

    private void Awake() //어웨이크
    {
        if (animator == null) //애니메이터가 없으면
        {
            animator = GetComponent<Animator>(); // 같은 오브젝트의 컴포넌트에서 Animator를 찾는다
                                                 // 근데 자식 오브젝트라서 못찾긴 한다
        }

        if (animator == null) // 그래도 애니메이터가 없으면
        {
            Debug.LogError("플레이어에 Animator 컴포넌트를 연결해야 합니다."); // 오류를 알림
            enabled = false; // 비활성화
            return; // 종료
        }
        animator.SetBool("IsMoving", false); // 애니메이터의 "IsMoving"을 false로 초기화
        animator.SetBool("IsSprint", false); // 애니메이터의 "IsSprint"를 false로 초기화
                                             // 문자열은 오타가 나도 컴파일 오류가 없으니 Animator 파라미터 이름과 똑같이 쓴다
        foreach (AnimatorControllerParameter parameter in animator.parameters)
        {
            if (parameter.nameHash == SpeedId && parameter.type == AnimatorControllerParameterType.Float)
                hasSpeedParameter = true;
        }
        if (hasSpeedParameter) animator.SetFloat(SpeedId, 0f);
        animator.SetFloat(MoveXId, 0f);
        animator.SetFloat(MoveYId, 0f);
    }

    public void SetLocomotion(Vector2 moveInput, bool isSprinting, bool isCrouching, float deltaTime)
    {
        if (!isActiveAndEnabled || animator == null || deltaTime <= 0f)
        {
            return;
        }

        Vector2 limitedInput = Vector2.ClampMagnitude(moveInput, 1f);
        float targetSpeed = limitedInput.magnitude * (isSprinting ? 2f : 1f);
        // 방향은 단위 벡터로 전달한다. 입력 세기는 Speed가 담당하므로 중복해서 줄이지 않는다.
        Vector2 direction = limitedInput.sqrMagnitude > 0f ? limitedInput.normalized : Vector2.zero;
        if (hasSpeedParameter) animator.SetFloat(SpeedId, targetSpeed, locomotionDampTime, deltaTime);
        animator.SetFloat(MoveXId, direction.x, directionDampTime, deltaTime);
        animator.SetFloat(MoveYId, direction.y, directionDampTime, deltaTime);
        animator.SetBool(IsCrouchId, isCrouching);
        isMove(limitedInput.sqrMagnitude > 0f);
        isSprint(isSprinting);
    }

    public void ResetLocomotion()
    {
        if (animator == null) return;
        if (hasSpeedParameter) animator.SetFloat(SpeedId, 0f);
        animator.SetFloat(MoveXId, 0f);
        animator.SetFloat(MoveYId, 0f);
        animator.SetBool("IsMoving", false);
        animator.SetBool("IsSprint", false);
    }

    public void isMove(bool isMoving) // 키입력이 되서 이동 상태를 전달 받으면 실행되는 함수
    {
        if (!isActiveAndEnabled) // 이 컴포넌트나 게임 오브젝트가 비활성화 상태라면
        {
            return; // 이번 요청 처리를 종료
        }
        animator.SetBool("IsMoving", isMoving); // 전달받은 이동 여부를 Animator의 "IsMoving" 값으로 설정
    }

    public void isSprint(bool isSprinting) // 달리기 여부를 전달받으면 실행되는 함수
    {
        if (!isActiveAndEnabled) // 이 컴포넌트나 게임 오브젝트가 비활성화 상태라면
        {
            return; // 이번 요청 처리를 종료
        }
        animator.SetBool("IsSprint", isSprinting); // 전달받은 달리기 여부를 Animator의 "IsSprint" 값으로 설정
    }

    private void OnDisable() // 이 컴포넌트가 비활성화되면
    {
        ResetLocomotion();
    }

}
