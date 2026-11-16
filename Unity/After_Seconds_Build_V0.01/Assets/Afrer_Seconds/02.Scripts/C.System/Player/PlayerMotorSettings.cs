using UnityEngine;

#region 의사코드 Ver 0.3 (달리기 속도, 앉기 속도·높이 추가)

/*
플레이어 이동에 쓰는 숫자를 보관하는 설정 에셋
(코드에 숫자를 직접 쓰지 않고, 에셋의 인스펙터에서 값을 바꾼다)

기억해둘 정보:
    걷기 이동 속도 — moveSpeed (0 이상)
    달리기 이동 속도 — sprintSpeed (0 이상)
    중력 크기 — gravity (0 이상, 양수로 입력)
    바닥 접지를 유지하기 위한 작은 하강 속도 — groundedVerticalSpeed
    앉았을 때 이동속도 — crouchSpeed (0 이상)
    앉았을 때 달리기 이동속도 — crouchSprintSpeed (0 이상)
    앉았을 때 몸(CharacterController)의 높이 — crouchHeight (0.6 이상, 캡슐 지름보다 커야 함)
        (서 있는 높이는 숫자로 적지 않고, 게임이 시작될 때 CharacterController에서 읽어 둔다)
    점프하는 강도 - jumpForce (0이상)

밖에서 읽을 수 있게 공개하는 값 (읽기만 가능, 바꾸기는 불가):
    걷기 이동 속도를 그대로 돌려준다 — MoveSpeed
    달리기 이동 속도를 그대로 돌려준다 — SprintSpeed
    중력은 아래 방향이므로 음수로 바꿔서 돌려준다 — GravityAcceleration
    접지 유지용 하강 속도를 그대로 돌려준다 — GroundedVerticalSpeed
    앉았을 때 이동속도를 그대로 돌려준다 - CrouchSpeed
    앉았을 때 달리기 이동속도를 그대로 돌려준다 - CrouchSprintSpeed
    앉았을 때 몸의 높이를 그대로 돌려준다 - CrouchHeight
    점프 했을 때의 힘의 값 - JumpForce
*/

#endregion

#region 의사코드 Ver 0.5 (가속도·감속도 추가)

/*
(Ver 0.5: 걷기·달리기를 처음부터 최고 속도로 시작하지 않고 서서히 빨라지고 서서히 멈추게 한다.
         Ver 0.3~0.4에서 바뀐 부분만 적는다)

기억해둘 정보에 추가:
    바닥에서 속도를 올리는 빠르기 — acceleration (0 이상, 1초에 속도가 얼마나 바뀌는가 m/s²)
        (이동 입력이 있을 때 쓴다. 방향을 바꾸거나 걷기에서 달리기로 넘어갈 때도 이 값을 쓴다)
    바닥에서 속도를 줄이는 빠르기 — deceleration (0 이상, m/s²)
        (이동 입력이 없을 때 쓴다. 난간 앞에서 미끄러지지 않도록 가속도보다 크게 둔다)

밖에서 읽을 수 있게 공개하는 값에 추가 (읽기만 가능):
    속도를 올리는 빠르기를 그대로 돌려준다 — Acceleration
    속도를 줄이는 빠르기를 그대로 돌려준다 — Deceleration
*/

#endregion
[CreateAssetMenu(fileName = "PlayerMotorSettings", menuName = "After Seconds/Player Motor Settings")]
public class PlayerMotorSettings : ScriptableObject
{
    // 걷기 이동 속도(m/s). Min(0f)는 인스펙터에서 0보다 작은 값을 넣지 못하게 막는다.
    [SerializeField, Min(0f)] private float moveSpeed;

    // 달리기 이동 속도(m/s). 앞으로 이동하면서 달리기 키를 누르고 있을 때 Motor가 이 값을 쓴다.
    [SerializeField, Min(0f)] private float sprintSpeed;

    // 중력의 크기. 인스펙터에는 양수로 넣고, 아래 방향 부호는 GravityAcceleration에서 붙인다.
    [SerializeField, Min(0f)] private float gravity;

    [SerializeField] private float groundedVerticalSpeed;

    [SerializeField, Min(0f)] private float crouchSpeed; // 앉았을 때 이동속도
    [SerializeField, Min(0f)] private float crouchSprintSpeed; // 앉았을 때 달리기 이동속도

    // 앉았을 때 CharacterController의 높이(m). 서 있는 높이(1.8)보다 낮아야 낮은 통로를 지나갈 수 있다.
    // 캡슐 높이는 지름(반지름 0.28 × 2 = 0.56)보다 커야 모양이 유지되므로 최소 0.6으로 막는다.
    [Tooltip("앉았을 때 몸 높이(m)입니다. 앉아야만 지나가는 통로는 이 값보다 높고 서 있는 높이보다 낮게 만듭니다.")]
    [SerializeField, Min(0.6f)] private float crouchHeight = 1.2f;

    [SerializeField, Min(0.0f)] private float jumpForce = 10f;

    // 바닥에서 속도를 올리는 빠르기(m/s²). "1초에 속도가 얼마나 바뀌는가"를 뜻한다.
    // 걷기 속도 5에 가속도 30이면 5 ÷ 30 ≈ 0.17초 만에 걷기 속도에 도달한다.
    [Tooltip("이동 입력이 있을 때 속도가 바뀌는 빠르기(m/s²)입니다. 클수록 즉시 반응하고, 작을수록 서서히 빨라집니다.")]
    [SerializeField, Min(0f)] private float acceleration = 30f;

    // 바닥에서 속도를 줄이는 빠르기(m/s²). 키를 뗐을 때 쓴다.
    // 난간 앞에서 미끄러져 떨어지지 않도록 가속도보다 크게 둔다.
    [Tooltip("이동 입력이 없을 때 속도가 줄어드는 빠르기(m/s²)입니다. 클수록 빨리 멈춥니다.")]
    [SerializeField, Min(0f)] private float deceleration = 40f;

    // => 는 "이 값을 돌려준다"는 짧은 속성 문법이다. get만 있으므로 밖에서 읽기만 할 수 있다(캡슐화).
    public float MoveSpeed => moveSpeed;
    public float SprintSpeed => sprintSpeed;
    public float GravityAcceleration => -gravity;
    public float GroundedVerticalSpeed => groundedVerticalSpeed;
    public float CrouchSpeed => crouchSpeed; // 앉았을 때 이동속도를 그대로 돌려준다
    public float CrouchSprintSpeed => crouchSprintSpeed; // 앉았을 때 달리기 이동속도를 그대로 돌려준다
    public float CrouchHeight => crouchHeight; // 앉았을 때 몸의 높이를 그대로 돌려준다

    public float JumpForce => jumpForce; // 점프 했을 때의 값을 그대로 돌려준다

    public float Acceleration => acceleration; // 속도를 올리는 빠르기를 그대로 돌려준다
    public float Deceleration => deceleration; // 속도를 줄이는 빠르기를 그대로 돌려준다
}
