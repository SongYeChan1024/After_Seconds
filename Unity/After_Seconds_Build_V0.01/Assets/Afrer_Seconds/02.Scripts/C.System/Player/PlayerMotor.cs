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

#region 의사코드 Ver 0.2 (달리기 속도 선택 추가)

/*
플레이어를 이동시키는 기능
(Ver 0.2: Presenter가 판단한 달리기 여부를 받아 속도를 고른다.
         달리는 중인지 "판단"은 Presenter가 하고, Motor는 받은 값대로 "속도만" 고른다)

기억해둘 정보:
    CharacterController의 참조
    이동 설정 에셋의 참조 (걷기 속도·달리기 속도·중력·접지 유지 속도)
    현재 수직 속도

초기화할 때:
    플레이어의 CharacterController를 찾아 보관한다
    현재 수직 속도를 0으로 설정한다
    설정 에셋이 연결되지 않았다면:
        오류를 알리고 이 컴포넌트를 비활성화한다

한 프레임의 이동을 요청받으면:
    이동 입력, 달리기 여부, 경과 시간을 전달받는다

    이 컴포넌트가 꺼져 있거나, CharacterController가 꺼져 있거나, 경과 시간이 0 이하라면:
        이번 이동을 하지 않고 종료한다

    이동 입력의 길이를 최대 1로 제한한다

    플레이어의 오른쪽 방향에 좌우 입력을 반영한다
    플레이어의 앞쪽 방향에 전후 입력을 반영한다
    두 방향을 합쳐 수평 이동 방향을 구한다

    달리기 여부가 true라면:
        이번 이동 속도를 달리기 속도로 정한다
    그렇지 않다면:
        이번 이동 속도를 걷기 속도로 정한다

    수평 이동 방향에 이번 이동 속도를 곱해 수평 속도를 구한다

    직전 이동에서 바닥에 닿았고, 현재 하강 중이라면:
        수직 속도를 접지 유지용 하강 속도로 조정한다

    수직 속도에 "중력 가속도 × 경과 시간"을 더한다

    수평 속도와 수직 속도를 합친다
    합친 속도에 경과 시간을 곱해 이번 이동량을 구한다

    CharacterController에 이번 이동량을 전달한다
*/

#endregion

#region 의사코드 Ver 0.3 (앉기 추가)

/*
플레이어를 이동시키는 기능
(Ver 0.3: 몸 높이를 낮춰 앉고, 머리 위 공간을 확인해 일어선다.
         앉기의 목적 — ① 낮은 통로를 지나간다 ② 나중에 경비가 "앉아 있는가"를 읽어 발견을 늦춘다
         토글 판단(C를 누를 때마다 앉기/일어서기)은 Presenter가 하고, Motor는 요청받은 대로 몸을 바꾼다)

기억해둘 정보에 추가:
    서 있을 때의 높이와 중심 — Awake에서 CharacterController로부터 읽어 둔다
        (프리팹과 씬의 Center 값이 서로 달라서, 숫자로 적지 않고 시작할 때 읽는다)
    앉았을 때의 중심 — 발바닥 위치가 그대로 있도록 계산해 둔다
    지금 앉아 있는지 — isCrouching, 처음에는 false

밖에서 읽을 수 있게 공개하는 값 (읽기만 가능):
    지금 앉아 있는지 — IsCrouching
        (나중에 경비 감지 기능이 이 값을 읽어 발견 시간을 늘린다)
    서 있을 때보다 몸이 얼마나 낮아졌는지 — CrouchHeightDrop
        (Presenter가 이 값으로 눈 높이(CameraRoot)를 같이 낮춘다)

초기화할 때 추가:
    서 있을 때의 높이와 중심을 기억한다
    앉았을 때의 중심을 계산한다:
        높이가 줄면 캡슐이 위아래에서 같이 줄어든다
        발바닥이 뜨지 않으려면 중심을 (서 있는 높이 - 앉은 높이)의 절반만큼 내린다

앉으라는 요청을 받으면 — Crouch:
    이미 앉아 있다면: 아무것도 하지 않는다
    CharacterController의 높이를 앉은 높이로, 중심을 앉았을 때의 중심으로 바꾼다
    앉아 있는 상태로 기록한다

일어서라는 요청을 받으면 — TryStandUp:
    앉아 있지 않다면: 이미 서 있으므로 성공으로 돌려준다
    머리 위에 일어설 공간이 없다면:
        앉은 채로 두고 실패로 돌려준다 (낮은 통로 안에서 C를 눌러도 천장에 끼지 않게)
    높이와 중심을 서 있을 때의 값으로 되돌린다
    서 있는 상태로 기록하고 성공으로 돌려준다

일어설 공간이 있는지 확인하는 기능 — CanStandUp:
    지금(앉은) 머리 위치부터 서 있을 때의 머리 위치까지를
    캡슐 모양으로 검사해서 다른 콜라이더가 있는지 확인한다 (Physics.OverlapCapsule)
    찾은 콜라이더 중 플레이어 자기 자신의 것은 빼고 판단한다
    하나라도 있으면 공간이 없다 / 없으면 공간이 있다

한 프레임의 이동 — 속도 고르기 수정:
    앉아 있고 달리는 중이라면: 앉아서 달리기 속도
    앉아 있다면:               앉아서 이동 속도
    달리는 중이라면:           달리기 속도
    그렇지 않다면:             걷기 속도
*/

#endregion

#region 의사코드 Ver 0.4 (점프 추가)

/*
플레이어를 이동시키는 기능
(Ver 0.4: 바닥에 있을 때 위로 뛰어오른다. Ver 0.3에서 바뀐 부분만 적는다.
         점프 키를 눌렀는지는 Presenter가 받고, Motor는 "지금 뛸 수 있는가"를 판단해 수직 속도를 바꾼다)

기억해둘 정보에 추가:
    지금 점프로 공중에 떠 있는지 — isJumping, 처음에는 false
    (점프 시작 속도는 숫자로 적지 않고 설정 에셋에서 가져온다 — JumpForce)

밖에서 읽을 수 있게 공개하는 값에 추가 (읽기만 가능):
    지금 점프로 공중에 떠 있는지 — IsJumping
        (나중에 Presenter가 이 값을 애니메이션에 전달한다)

점프하라는 요청을 받으면 — Jump:
    바닥에 닿아 있지 않다면: 아무것도 하지 않는다
        (공중에서 다시 뛰거나, 난간에서 떨어지는 중에 뛰는 것을 막는다)

    앉아 있다면:
        일어서기를 시도한다 (TryStandUp)
        일어서지 못했다면: 아무것도 하지 않는다
            (낮은 통로 안에서는 머리 위가 막혀 있으므로 점프하지 않는다)

    현재 수직 속도를 점프 시작 속도로 정한다
        (더하지 않고 정한다. 언제 눌러도 같은 높이로 뛰게 하려고)
    점프 중인 상태로 기록한다

한 프레임의 이동 — 수정:
    (속도 고르기와 수평 속도 계산은 Ver 0.3과 같음)

    직전 이동에서 바닥에 닿았고, 현재 하강 중이라면:
        수직 속도를 접지 유지용 하강 속도로 조정한다
        점프 중이 아닌 상태로 기록한다 (착지했으므로)

    수직 속도에 "중력 가속도 × 경과 시간"을 더한다

    수평 속도와 수직 속도를 합쳐 이번 이동량을 구한다
    CharacterController에 이번 이동량을 전달하고, 어느 쪽이 부딪혔는지 결과를 받는다

    결과에 "위쪽이 부딪혔다"가 들어 있고, 현재 상승 중이라면:
        수직 속도를 0으로 바꾼다
            (천장에 머리가 닿으면 그 자리에서 떨어지기 시작하게 한다)
*/

#endregion

#region 의사코드 Ver 0.5 (공중에서 수평 속도 유지)

/*
플레이어를 이동시키는 기능
(Ver 0.5: 공중에서는 방향키로 조종할 수 없고, 발이 떨어진 순간의 수평 속도로 계속 날아간다.
         Ver 0.4에서는 매 프레임 입력으로 수평 속도를 새로 계산해서, 공중에서 키를 떼면 그 자리에서 멈췄다.
         Ver 0.4에서 바뀐 부분만 적는다)

기억해둘 정보에 추가:
    현재 수평 속도 — horizontalVelocity, 처음에는 (0, 0, 0)
        (수직 속도처럼 프레임이 끝나도 남겨 둔다. 방향과 빠르기를 함께 담는다)

한 프레임의 이동 — 수정:
    (속도 고르기는 Ver 0.3과 같음)

    직전 이동에서 바닥에 닿았다면:
        이동 방향에 고른 속도를 곱해 현재 수평 속도로 정한다
            (바닥에서는 지금까지처럼 입력대로 바로 움직이고 바로 멈춘다)
    바닥에 닿아 있지 않다면:
        현재 수평 속도를 바꾸지 않는다
            (공중에서는 키를 누르거나 떼도, 시점을 돌려도 날아가는 방향과 빠르기가 그대로다)

    (착지 처리와 중력은 Ver 0.4와 같음)

    현재 수평 속도와 수직 속도를 합쳐 이번 이동량을 구한다
    (CharacterController 전달과 천장 처리는 Ver 0.4와 같음)
*/

#endregion

#region 의사코드 Ver 0.6 (바닥에서 서서히 빨라지고 서서히 멈추기)

/*
플레이어를 이동시키는 기능
(Ver 0.6: 사람이 처음부터 최고 속도로 걷거나 뛰지 않으므로, 바닥에서 수평 속도를 조금씩 바꾼다.
         Ver 0.5에서는 바닥에 닿아 있으면 입력대로 수평 속도를 "바로 정했다".
         Ver 0.5에서 바뀐 부분만 적는다)

(빠르기 숫자는 코드에 적지 않고 설정 에셋에서 가져온다 — Acceleration, Deceleration)

한 프레임의 이동 — 수정:
    (속도 고르기는 Ver 0.3과 같음)

    직전 이동에서 바닥에 닿았다면:
        이동 방향에 고른 속도를 곱해 "원하는 수평 속도"를 구한다
            (입력이 없으면 원하는 수평 속도는 (0, 0, 0)이다)

        이동 입력이 없다면:
            이번에 쓸 빠르기를 감속도로 정한다 (키를 떼면 빨리 멈추게)
        그렇지 않다면:
            이번에 쓸 빠르기를 가속도로 정한다 (출발·방향 전환·걷기→달리기)

        현재 수평 속도를 원하는 수평 속도 쪽으로 "고른 빠르기 × 경과 시간"만큼만 옮긴다
            (Vector3.MoveTowards — 목표를 지나치지 않고, 가까우면 목표에 정확히 멈춘다)

    바닥에 닿아 있지 않다면:
        현재 수평 속도를 바꾸지 않는다 (Ver 0.5와 같음)

    (착지·중력·이동 전달·천장 처리는 Ver 0.5와 같음)
*/

#endregion

#region 의사코드 Ver 0.7 (바닥에서 반대 방향 입력으로 제동)
/*
이동 입력을 놓으면 감속도로 수평 속도를 0에 가깝게 한다.
입력이 있으면 현재 수평 속도가 새 입력 방향을 따라 얼마나 움직이는지 구한다.
    그 값이 음수면 역방향 제동으로 그 성분을 먼저 줄인다. 옆으로 가던 속도는 남는다.
    제동에 쓰고 남은 프레임 시간 동안 목표 속도를 향해 가속한다.
*/
#endregion
[RequireComponent(typeof(CharacterController))]
public class PlayerMotor : MonoBehaviour
{
    [SerializeField] private PlayerMotorSettings settings;

    private CharacterController characterController;
    private float verticalVelocity;

    // 현재 수평 속도(방향과 빠르기). 수직 속도처럼 프레임이 끝나도 남겨 둔다.
    // 바닥에서는 입력에 따라 가속·제동하고, 공중에서는 발이 떨어진 순간의 속도를 유지한다.
    private Vector3 horizontalVelocity = Vector3.zero;

    // ── 앉기에 쓰는 정보 ──
    private float standingHeight;    // 서 있을 때 CharacterController 높이 (Awake에서 읽어 둔다)
    private Vector3 standingCenter;  // 서 있을 때 CharacterController 중심
    private Vector3 crouchingCenter; // 앉았을 때 중심 (발바닥 위치가 그대로 있도록 계산)
    private bool isCrouching;        // 지금 앉아 있는지
    private bool isJumping;

    // 지금 앉아 있는지 밖에서 읽기만 할 수 있게 공개한다.
    // 나중에 경비 감지 기능이 이 값을 읽어 "앉아 있으면 늦게 들키게" 만든다.
    public bool IsCrouching => isCrouching;

    // 지금 점프 했는지 밖에서 읽기만 할 수 있게 공개한다.
    public bool IsJumping => isJumping;

    // 서 있을 때보다 몸이 얼마나 낮아졌는지(m). 서 있으면 0이다.
    // Presenter가 이 값만큼 눈 높이(CameraRoot)를 낮추도록 PlayerLook에 전달한다.
    public float CrouchHeightDrop => standingHeight - characterController.height;

    private void Awake()
    {
        characterController = GetComponent<CharacterController>();
        verticalVelocity = 0f;

        if (settings == null)
        {
            Debug.LogError("PlayerMotor의 Settings에 이동 설정 에셋을 연결해주세요.", this);
            enabled = false;
            return; // 설정이 없으면 아래 앉기 계산도 할 수 없으므로 여기서 끝낸다.
        }

        // 서 있을 때의 높이와 중심을 숫자로 적지 않고 지금 값에서 읽어 둔다.
        // (프리팹은 Center Y 0.9, Player 씬은 0.3처럼 서로 달라도 각자 원래 값으로 되돌릴 수 있다)
        standingHeight = characterController.height;
        standingCenter = characterController.center;

        // 높이가 줄면 캡슐이 위아래에서 같이 줄어든다.
        // 발바닥이 뜨지 않게 하려면 중심을 "줄어든 높이의 절반"만큼 내려야 한다.
        float heightDrop = standingHeight - settings.CrouchHeight;
        crouchingCenter = standingCenter - Vector3.up * (heightDrop * 0.5f);

        isCrouching = false;
    }

    // 앉으라는 요청. 토글 판단은 Presenter가 하고, 여기서는 몸 크기만 바꾼다.
    public void Crouch()
    {
        if (isCrouching) // 이미 앉아 있다면
        {
            return;      // 할 일이 없다
        }

        characterController.height = settings.CrouchHeight; // 몸 높이를 낮춘다
        characterController.center = crouchingCenter;       // 발바닥 위치를 유지하도록 중심도 내린다
        isCrouching = true;
    }

    // 일어서라는 요청. 머리 위 공간이 없으면 일어서지 않고 false를 돌려준다.
    // bool을 돌려주는 이유: 부른 쪽(Presenter)이 "일어서기에 성공했는지" 알 수 있게 하려고.
    public bool TryStandUp()
    {
        if (!isCrouching) // 이미 서 있다면
        {
            return true;  // 서 있는 상태이므로 성공으로 본다
        }

        if (!CanStandUp()) // 머리 위가 막혀 있다면 (낮은 통로 안)
        {
            return false;  // 앉은 채로 둔다. 일어서면 천장에 끼기 때문이다.
        }

        characterController.height = standingHeight; // 원래 높이로
        characterController.center = standingCenter; // 원래 중심으로
        isCrouching = false;
        return true;
    }

    // 점프하라는 요청. 점프 키를 눌렀는지는 Presenter가 받고, 여기서는 "지금 뛸 수 있는지"를 판단한다.
    // 결과를 밖에서 쓰지 않으므로 돌려주는 값이 없는 void로 만든다.
    public void Jump()
    {
        // isGrounded는 "직전 이동에서 바닥에 닿았는지"를 알려 준다.
        if (characterController.isGrounded == false) // 바닥에 닿아 있지 않다면
        {
            return; // 공중에서 다시 뛰거나, 난간에서 떨어지는 중에 뛰지 않는다
        }

        if (isCrouching) // 앉아 있다면 먼저 일어서야 뛸 수 있다
        {
            // TryStandUp()은 일어서기에 성공하면 true, 머리 위가 막혀 실패하면 false를 돌려준다.
            if (TryStandUp() == false) // 일어서지 못했다면 (낮은 통로 안)
            {
                return; // 앉은 채로 두고 점프하지 않는다
            }
        }

        // 수직 속도를 점프 시작 속도로 정한다.
        // += 로 더하지 않고 = 로 정하는 이유: 언제 눌러도 같은 높이로 뛰게 하려고.
        verticalVelocity = settings.JumpForce;

        isJumping = true; // 점프 중인 상태로 기록한다. 착지하면 Move에서 false로 되돌린다.
    }

    // 지금 앉은 머리 위치부터 서 있을 때의 머리 위치까지 비어 있는지 확인한다.
    private bool CanStandUp()
    {
        float radius = characterController.radius;

        // 캡슐은 "위 구"와 "아래 구"의 중심 두 점으로 표현한다.
        // 아래 점: 지금(앉은) 머리 쪽 구의 중심 / 위 점: 서 있을 때 머리 쪽 구의 중심
        Vector3 crouchHeadLocal = crouchingCenter + Vector3.up * (settings.CrouchHeight * 0.5f - radius);
        Vector3 standHeadLocal = standingCenter + Vector3.up * (standingHeight * 0.5f - radius);

        // TransformPoint: 플레이어 기준(로컬) 위치를 월드 위치로 바꾼다.
        Vector3 bottom = transform.TransformPoint(crouchHeadLocal);
        Vector3 top = transform.TransformPoint(standHeadLocal);

        // 벽에 붙어 있을 때 옆벽까지 잡히지 않도록 반지름을 아주 조금 줄여서 검사한다.
        // QueryTriggerInteraction.Ignore: 트리거(통과 가능한 감지 영역)는 막힌 것으로 보지 않는다.
        Collider[] hits = Physics.OverlapCapsule(bottom, top, radius * 0.95f, ~0, QueryTriggerInteraction.Ignore);

        foreach (Collider hit in hits)
        {
            // 플레이어 자기 자신(CharacterController나 자식 오브젝트의 콜라이더)은 제외한다.
            if (hit == characterController || hit.transform.IsChildOf(transform))
            {
                continue;
            }

            return false; // 다른 물체가 하나라도 있으면 일어설 공간이 없다
        }

        return true; // 아무것도 없으면 일어설 수 있다
    }

    // 한 프레임의 이동을 처리한다. Presenter가 매 프레임 호출한다.
    // 매개변수 순서는 Presenter의 호출 순서와 같아야 한다: (이동 입력, 달리기 여부, 경과 시간)
    // isSprinting은 Presenter가 "달리기 키를 누르고 있고 앞으로 가는 중"인지 판단한 결과다.
    public void Move(Vector2 moveInput, bool isSprinting, float deltaTime)
    {
        if (!isActiveAndEnabled || !characterController.enabled || deltaTime <= 0f)
        {
            return;
        }

        Vector2 limitedInput = Vector2.ClampMagnitude(moveInput, 1f);
        Vector3 moveDirection = transform.right * limitedInput.x
            + transform.forward * limitedInput.y;

        // 앉기·달리기 상태에 따라 속도를 고른다. 위에서부터 먼저 맞는 조건 하나만 쓴다.
        // 숫자는 코드에 쓰지 않고 설정 에셋(settings)에서 가져온다.
        float currentSpeed;
        if (isCrouching && isSprinting)      // 앉은 채로 달리기
        {
            currentSpeed = settings.CrouchSprintSpeed;
        }
        else if (isCrouching)                // 앉아서 이동
        {
            currentSpeed = settings.CrouchSpeed;
        }
        else if (isSprinting)                // 서서 달리기
        {
            currentSpeed = settings.SprintSpeed;
        }
        else                                 // 서서 걷기
        {
            currentSpeed = settings.MoveSpeed;
        }

        // 바닥에 닿아 있을 때만 입력으로 수평 속도를 바꾼다.
        // 공중에서는 이 블록을 건너뛰므로, 발이 떨어진 순간의 수평 속도가 그대로 남는다.
        // (isGrounded는 "직전 이동에서 바닥에 닿았는지"라서, 점프한 프레임에는 아직 true다.
        //  그래서 뛰는 순간의 입력까지는 반영되고, 그다음 프레임부터 고정된다)
        if (characterController.isGrounded)
        {
            UpdateGroundVelocity(moveDirection * currentSpeed, deltaTime);
        }

        if (characterController.isGrounded && verticalVelocity < 0f)
        {
            verticalVelocity = settings.GroundedVerticalSpeed;
            isJumping = false;
        }

        verticalVelocity += settings.GravityAcceleration * deltaTime;

        Vector3 velocity = horizontalVelocity + Vector3.up * verticalVelocity;

        // Move는 몸을 움직인 뒤 "이번 이동에서 어느 쪽이 부딪혔는지"를 CollisionFlags로 돌려준다.
        // 충돌을 감지하는 것은 Move이고, flags는 그 결과를 담아 두는 변수다.
        CollisionFlags flags = characterController.Move(velocity * deltaTime);

        // 위쪽(천장)이 부딪혔고, 지금 올라가는 중이라면 상승을 멈춘다.
        // 벽과 천장에 동시에 닿을 수 있어서 == 로 비교하지 않고, & 로 "위쪽 표시가 들어 있는지"만 골라 확인한다.
        // 올라가는 중일 때만 바꾸는 이유: 낮은 통로에서 머리가 스치기만 할 때 하강 속도를 건드리지 않으려고.
        if ((flags & CollisionFlags.Above) != 0 && verticalVelocity > 0f)
        {
            verticalVelocity = 0f; // 천장에 붙어 있지 않고 그 자리에서 바로 떨어지기 시작한다
        }
    }

    private void UpdateGroundVelocity(Vector3 targetVelocity, float deltaTime)
    {
        if (targetVelocity == Vector3.zero)
        {
            horizontalVelocity = Vector3.MoveTowards(horizontalVelocity, Vector3.zero, settings.Deceleration * deltaTime);
            return;
        }

        Vector3 inputDirection = targetVelocity.normalized;
        float speedAlongInput = Vector3.Dot(horizontalVelocity, inputDirection);
        if (speedAlongInput < 0f && settings.ReverseBraking > 0f)
        {
            // 새 입력을 거스르는 속도가 0이 될 때까지만 제동한다.
            float brakingTime = Mathf.Min(deltaTime, -speedAlongInput / settings.ReverseBraking);
            horizontalVelocity += inputDirection * (settings.ReverseBraking * brakingTime);
            deltaTime -= brakingTime;
        }

        // 한 프레임 안에서 제동이 끝났다면 남은 시간으로 바로 새 방향에 가속한다.
        horizontalVelocity = Vector3.MoveTowards(horizontalVelocity, targetVelocity, settings.Acceleration * deltaTime);
    }
}
