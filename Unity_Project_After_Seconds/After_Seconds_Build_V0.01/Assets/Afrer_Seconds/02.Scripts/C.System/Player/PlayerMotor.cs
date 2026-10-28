using UnityEngine;

#region 의사코드

/*
플레이어를 이동시키는 기능

기억해둘 정보:
    CharacterController의 참조
    설정에서 받은 이동 속도
    중력 가속도 ? 아래 방향이므로 음수
    현재 수직 속도
    바닥 접지를 유지하기 위한 작은 하강 속도

초기화할 때:
    플레이어의 CharacterController를 찾아 보관한다
    현재 수직 속도를 0으로 설정한다

한 프레임의 이동을 요청받으면:
    이동 입력과 경과 시간을 전달받는다

    이동 입력의 길이를 최대 1로 제한한다

    플레이어의 오른쪽 방향에 좌우 입력을 반영한다
    플레이어의 앞쪽 방향에 전후 입력을 반영한다
    두 방향을 합쳐 수평 이동 방향을 구한다

    수평 이동 방향에 이동 속도를 곱해 수평 속도를 구한다

    직전 이동에서 바닥에 닿았고, 현재 하강 중이라면:
        수직 속도를 접지 유지용 하강 속도로 조정한다

    수직 속도에 "중력 가속도 × 경과 시간"을 더한다

    수평 속도와 수직 속도를 합친다
    합친 속도에 경과 시간을 곱해 이번 이동량을 구한다

    CharacterController에 이번 이동량을 전달한다
*/

#endregion
[RequireComponent(typeof(CharacterController))]
public class PlayerMotor : MonoBehaviour
{
    [SerializeField] private PlayerMotorSettings settings;

    private CharacterController characterController;
    private float verticalVelocity;

    private void Awake()
    {
        characterController = GetComponent<CharacterController>();
        verticalVelocity = 0f;

        if (settings == null)
        {
            Debug.LogError("PlayerMotor의 Settings에 이동 설정 에셋을 연결해주세요.", this);
            enabled = false;
        }
    }

    public void Move(Vector2 moveInput, float deltaTime)
    {
        if (!isActiveAndEnabled || !characterController.enabled || deltaTime <= 0f)
        {
            return;
        }

        Vector2 limitedInput = Vector2.ClampMagnitude(moveInput, 1f);
        Vector3 moveDirection = transform.right * limitedInput.x
            + transform.forward * limitedInput.y;
        Vector3 horizontalVelocity = moveDirection * settings.MoveSpeed;

        if (characterController.isGrounded && verticalVelocity < 0f)
        {
            verticalVelocity = settings.GroundedVerticalSpeed;
        }

        verticalVelocity += settings.GravityAcceleration * deltaTime;

        Vector3 velocity = horizontalVelocity + Vector3.up * verticalVelocity;
        characterController.Move(velocity * deltaTime);
    }
}
