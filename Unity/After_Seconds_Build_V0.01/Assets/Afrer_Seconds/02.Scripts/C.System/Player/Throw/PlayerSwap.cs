using UnityEngine;

#region 의사코드
// 투척 충돌이나 조준 명중에서 교환 대상과 실행 시각을 큐에 넣는다.
// 실행 시 두 대상의 현재 위치를 맞바꾼다. 겹치면 가까운 빈자리로 보정하고 두 도착 위치를 한 번에 적용한다.
// 양쪽이 완전히 막혀 있으면 예약을 유지한다. 다음 대상의 독립적인 예약도 처리한다.
#endregion

// 명중 순간에는 대상과 시각을 보관한다. 실행 순간의 자세와 위치로 교환을 계산한다.
[DisallowMultipleComponent, RequireComponent(typeof(CharacterController), typeof(PlayerThrow))]
public sealed class PlayerSwap : MonoBehaviour
{
    [SerializeField] private PlayerThrowSettings settings;
    private CharacterController player;
    private PlayerThrow thrower;
    private PlayerInventory inventory;
    private readonly ThrowSwapQueue queue = new ThrowSwapQueue();
    public event System.Action<float> Pulse;
    public event System.Action FeedbackCleared;

    private void Awake()
    {
        player = GetComponent<CharacterController>();
        thrower = GetComponent<PlayerThrow>();
        inventory = GetComponent<PlayerInventory>();
    }

    private void OnEnable() => thrower.Hit += OnHit;
    private void OnDisable()
    {
        thrower.Hit -= OnHit;
        ClearPending();
    }

    private void OnHit(ThrownObject source, Collision collision)
    {
        ScheduleImpact(source, collision);
    }

    // 배식 연출과 자유 투척은 같은 물리 충돌과 예약 시각을 사용한다.
    public float Delay => settings.SwapDelay;
    public bool HasPending(SwapTarget target) => queue.Contains(target);
    public bool ScheduleImpact(ThrownObject source, Collision collision)
    {
        var target = collision.collider.GetComponentInParent<SwapTarget>();
        if (!Schedule(source, target, Time.fixedTimeAsDouble)) return false;
        if (collision.contactCount > 0 && target.TryGetComponent<GuardLoadout>(out var guard) && !guard.IsDown)
        {
            var contact = collision.GetContact(0);
            guard.ReactToHit(contact.point, -contact.normal);
        }
        return true;
    }

    // 조준 입력은 즉시 명중을 판단하고, 투척은 충돌 시각을 기준으로 같은 교환을 예약한다.
    public bool ScheduleSightHit(SwapTarget target)
    {
        if (!isActiveAndEnabled || !settings || !target || !target.Available) return false;
        return Schedule(null, target, Time.timeAsDouble);
    }

    private bool Schedule(ThrownObject source, SwapTarget target, double now)
    {
        if (!isActiveAndEnabled || !settings || !target || !target.Available) return false;
        if (!queue.Schedule(source, target, now, settings.SwapDelay)) return false;
        inventory?.Tell("위치 교환 예약");
        return true;
    }

    private void Update()
    {
        if (Time.timeScale == 0f) return;
        double now = Time.timeAsDouble;
        float pulse = queue.TakePulse(now);
        while (queue.TryTake(now, out var reservation))
        {
            var target = reservation.Target;
            if (!reservation.StillAvailable)
            {
                inventory?.Tell("교환할 대상이 없어");
                continue;
            }
            if (!player.enabled)
            {
                queue.WaitForSpace(reservation, now);
                continue;
            }
            // 착석 경비는 좌석 옆의 실제 보행 지점에서 일어나 양쪽 직립 공간을 검사한다.
            if (target.TryGetComponent<GuardMotor>(out var guardMotor)) guardMotor.StandUp();
            Physics.SyncTransforms();
            var other = target.Body;
            Vector3 playerFeet = Feet(player), otherFeet = target.Feet;
            var placement = new SwapPlacement(player, target);
            if (!placement.TryPair(playerFeet, otherFeet, out var playerOffset, out var targetOffset))
            {
                if (!reservation.WaitingForSpace) inventory?.Tell("교환할 위치를 보정하는 중");
                queue.WaitForSpace(reservation, now);
                continue;
            }

            var body = other.attachedRigidbody;
            var otherController = other as CharacterController;
            player.enabled = false;
            if (otherController) otherController.enabled = false;
            if (body)
            {
                Vector3 destination = body.position + targetOffset;
                body.transform.position = destination;
                body.position = destination;
                if (!body.isKinematic) body.WakeUp();
            }
            else target.transform.position += targetOffset;
            transform.position += playerOffset;
            if (otherController) otherController.enabled = true;
            player.enabled = true;
            Physics.SyncTransforms();
            target.NotifyRelocated();
            pulse = 1f;
            inventory?.Tell("위치 교환");
        }
        if (pulse > 0f) Pulse?.Invoke(pulse);
    }

    public void ClearPending()
    {
        queue.Clear();
        FeedbackCleared?.Invoke();
    }

    private static Vector3 Feet(Collider c)
    {
        var b = c.bounds;
        return new Vector3(b.center.x, b.min.y, b.center.z);
    }
}
