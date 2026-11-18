using UnityEngine;

// 명중 시 대상과 시각만 보관한다. 실행 시 양쪽 발과 자세를 다시 읽고 둘 다 들어갈 때만 옮긴다.
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
        var target = collision.collider.GetComponentInParent<SwapTarget>();
        if (!settings || !target || !target.Available) return;
        if (queue.Schedule(source, target, Time.fixedTimeAsDouble, settings.SwapDelay))
            inventory?.Tell("위치 교환 예약");
    }

    private void Update()
    {
        if (Time.timeScale == 0f) return;
        double now = Time.timeAsDouble;
        float pulse = queue.TakePulse(now);
        while (queue.TryTake(now, out var target))
        {
            if (!target || !target.Available || !player.enabled)
            {
                inventory?.Tell("교환할 대상이 없어");
                continue;
            }
            Physics.SyncTransforms();
            var other = target.Body;
            Vector3 playerFeet = Feet(player), otherFeet = Feet(other);
            if (!TrySupport(playerFeet, target, out var playerFloor) ||
                !TrySupport(otherFeet, target, out var otherFloor))
            {
                inventory?.Tell("교환할 발판이 없어");
                continue;
            }
            // 접지한 컨트롤러의 skinWidth만큼 떠 있는 공간까지 경비에게 옮기지 않는다.
            Vector3 playerOffset = otherFloor - playerFeet;
            Vector3 targetOffset = playerFloor - otherFeet;
            if (!FitsAt(player, playerOffset, target) || !FitsAt(other, targetOffset, target))
            {
                inventory?.Tell("교환할 공간이나 발판이 없어");
                continue;
            }

            var body = other.attachedRigidbody;
            var otherController = other as CharacterController;
            player.enabled = false;
            if (otherController) otherController.enabled = false;
            if (body) body.position += targetOffset;
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

    private bool Participant(Collider c, SwapTarget target) =>
        c.transform.IsChildOf(transform) || c.transform.IsChildOf(target.transform);

    private bool TrySupport(Vector3 foot, SwapTarget target, out Vector3 ground)
    {
        ground = foot;
        float probe = player.skinWidth + Physics.defaultContactOffset;
        float nearest = float.PositiveInfinity;
        foreach (var hit in Physics.RaycastAll(foot + Vector3.up * probe, Vector3.down,
                     2f * probe, ~0, QueryTriggerInteraction.Ignore))
        {
            if (Participant(hit.collider, target) || hit.distance >= nearest ||
                Vector3.Angle(hit.normal, Vector3.up) > player.slopeLimit) continue;
            ground = hit.point;
            nearest = hit.distance;
        }
        return nearest < float.PositiveInfinity;
    }

    private bool FitsAt(Collider moving, Vector3 offset, SwapTarget target)
    {
        // 접촉 오차 범위만 줄인다. 같은 MeshCollider의 바닥과 벽도 개별 형상으로 검사한다.
        float inset = Physics.defaultContactOffset;
        Collider[] contacts;
        if (moving is BoxCollider box)
        {
            var half = Vector3.Scale(box.size, box.transform.lossyScale) * .5f;
            float margin = Mathf.Min(inset, Mathf.Min(half.x, half.y, half.z) * .25f);
            contacts = Physics.OverlapBox(box.transform.TransformPoint(box.center) + offset,
                half - Vector3.one * margin, box.transform.rotation, ~0, QueryTriggerInteraction.Ignore);
        }
        else
        {
            // B5 플레이어와 직립 경비는 모두 Y축 캡슐이다.
            var b = moving.bounds;
            float radius = Mathf.Max(b.extents.x, b.extents.z);
            Vector3 axis = Vector3.up * Mathf.Max(0f, b.extents.y - radius);
            Vector3 center = b.center + offset;
            contacts = Physics.OverlapCapsule(center - axis, center + axis, radius - inset,
                ~0, QueryTriggerInteraction.Ignore);
        }
        foreach (var c in contacts) if (!Participant(c, target)) return false;
        return true;
    }
}
