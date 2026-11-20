using UnityEngine;

#region 의사코드
// 등록된 충돌체와 발 위치를 제공한다. 들고 있는 물건이나 비활성 대상은 교환 후보에서 제외한다.
// 경비가 쓰러지면 누운 몸의 충돌체와 발 기준점을 기록하고 실제 이동 뒤 재배치 이벤트를 보낸다.
#endregion

// 월드 아이템과 경비의 루트에서 명중 판정과 교환 기준점을 제공한다.
[DisallowMultipleComponent]
public sealed class SwapTarget : MonoBehaviour
{
    [SerializeField] private Collider bodyCollider;
    private WorldItem item;
    // 주웠다가 다시 놓아도 과거의 명중 예약은 되살아나지 않는다.
    internal uint WorldRevision { get; private set; }
    private Vector3? fallenFoot;
    private Rigidbody releasedPistol, releasedDutyItem;
    internal bool IsReleasedEquipment(Collider other)
    {
        var body = other.attachedRigidbody;
        return body && (body == releasedPistol || body == releasedDutyItem);
    }
    internal Vector3 Feet
    {
        get
        {
            if (fallenFoot.HasValue) return transform.TransformPoint(fallenFoot.Value);
            Bounds b = bodyCollider.bounds;
            return new Vector3(b.center.x, b.min.y, b.center.z);
        }
    }

    internal Vector3 UseFallenBody(CharacterController standing, WorldItem pistol, WorldItem dutyItem, Vector3 desired)
    {
        releasedPistol = pistol ? pistol.GetComponent<Rigidbody>() : null;
        releasedDutyItem = dutyItem ? dutyItem.GetComponent<Rigidbody>() : null;
        Vector3 foot = standing.center - Vector3.up * (standing.height * .5f);
        float thickness = standing.radius * 1.5f;
        Vector3 size = new Vector3(standing.radius * 2f, thickness, standing.height);
        Vector3 center = new Vector3(0f, thickness * .5f, standing.height * .5f - standing.radius);
        Vector3 direction = Vector3.ProjectOnPlane(desired, Vector3.up).normalized;
        if (direction.sqrMagnitude < .01f) direction = transform.forward;
        Quaternion facing = Quaternion.LookRotation(direction);
        // 옆에 벽이 있으면 실제로 몸이 누울 수 있는 방향부터 선택한다. 표시와 충돌체가 같은 방향을 쓴다.
        foreach (float turn in FallAngles)
        {
            var candidate = Quaternion.Euler(0f, turn, 0f) * Quaternion.LookRotation(direction);
            var overlaps = Physics.OverlapBox(transform.TransformPoint(foot) + candidate * center,
                size * .5f - Vector3.one * .025f, candidate, ~0, QueryTriggerInteraction.Ignore);
            bool occupied = false;
            foreach (var c in overlaps)
                if (!c.transform.IsChildOf(transform)) { occupied = true; break; }
            if (!occupied) { facing = candidate; break; }
        }

        var shape = new GameObject("FallenBody");
        shape.layer = gameObject.layer;
        shape.transform.SetParent(transform, false);
        shape.transform.localPosition = foot;
        shape.transform.rotation = facing;
        var fallen = shape.AddComponent<BoxCollider>();
        fallen.size = size;
        fallen.center = center;
        fallenFoot = foot;
        bodyCollider = fallen;
        return facing * Vector3.forward;
    }
    private static readonly float[] FallAngles = { 0f, 45f, -45f, 90f, -90f, 180f };

    internal void EnableFallenGravity()
    {
        // 제압된 경비도 공중에서 교환되면 자신의 무게로 내려앉는다. 시각적 관절 동작은 별도로 진행한다.
        if (!fallenFoot.HasValue || bodyCollider.attachedRigidbody) return;
        var rigid = gameObject.AddComponent<Rigidbody>();
        rigid.mass = 75f;
        rigid.constraints = RigidbodyConstraints.FreezeRotation;
        rigid.collisionDetectionMode = CollisionDetectionMode.ContinuousSpeculative;
    }

    public Collider Body => bodyCollider;
    public event System.Action Relocated;
    internal void NotifyRelocated() => Relocated?.Invoke();
    public bool Available => isActiveAndEnabled && bodyCollider != null && bodyCollider.enabled &&
                             (item == null || !item.IsStored);

    private void Reset() => bodyCollider = GetComponent<Collider>();

    private void Awake()
    {
        item = GetComponent<WorldItem>();
        if (!bodyCollider) bodyCollider = GetComponent<Collider>();
    }

    private void OnDisable() => WorldRevision++;
}
