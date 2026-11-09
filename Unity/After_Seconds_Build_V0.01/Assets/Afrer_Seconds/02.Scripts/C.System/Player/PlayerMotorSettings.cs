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

밖에서 읽을 수 있게 공개하는 값 (읽기만 가능, 바꾸기는 불가):
    걷기 이동 속도를 그대로 돌려준다 — MoveSpeed
    달리기 이동 속도를 그대로 돌려준다 — SprintSpeed
    중력은 아래 방향이므로 음수로 바꿔서 돌려준다 — GravityAcceleration
    접지 유지용 하강 속도를 그대로 돌려준다 — GroundedVerticalSpeed
    앉았을 때 이동속도를 그대로 돌려준다 - CrouchSpeed
    앉았을 때 달리기 이동속도를 그대로 돌려준다 - CrouchSprintSpeed
    앉았을 때 몸의 높이를 그대로 돌려준다 - CrouchHeight
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

    // => 는 "이 값을 돌려준다"는 짧은 속성 문법이다. get만 있으므로 밖에서 읽기만 할 수 있다(캡슐화).
    public float MoveSpeed => moveSpeed;
    public float SprintSpeed => sprintSpeed;
    public float GravityAcceleration => -gravity;
    public float GroundedVerticalSpeed => groundedVerticalSpeed;
    public float CrouchSpeed => crouchSpeed; // 앉았을 때 이동속도를 그대로 돌려준다
    public float CrouchSprintSpeed => crouchSprintSpeed; // 앉았을 때 달리기 이동속도를 그대로 돌려준다
    public float CrouchHeight => crouchHeight; // 앉았을 때 몸의 높이를 그대로 돌려준다
}
