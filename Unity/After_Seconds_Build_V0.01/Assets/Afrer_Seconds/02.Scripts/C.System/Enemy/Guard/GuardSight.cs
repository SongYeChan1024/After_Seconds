using UnityEngine;

public sealed class GuardSight : MonoBehaviour
{
    [SerializeField] private Transform eyeAnchor;
    private readonly RaycastHit[] hits = new RaycastHit[32];
    public Quaternion EyeRotation => eyeAnchor ? eyeAnchor.rotation : transform.rotation;

    public float Exposure(CharacterController player, GuardSettings settings)
    {
        if (!player || !player.enabled || !player.gameObject.activeInHierarchy) return 0f;
        Bounds b = player.bounds;
        Vector3 eyes = EyePosition(settings);
        float head = Clear(eyes, b.center + Vector3.up * (b.extents.y * .8f), player, settings) ? .5f : 0f;
        return head + (Clear(eyes, b.center, player, settings) ? .5f : 0f);
    }

    public bool CanReach(CharacterController guard, CharacterController player, GuardSettings settings)
    {
        if (!player.enabled) return false;
        var a = guard.bounds;
        var b = player.bounds;
        // 두 직립 캡슐의 중심 선분에서 가장 가까운 두 점 사이 거리로 몸 사이 간격을 구한다.
        Vector3 from = a.center, to = b.center;
        from.y = Mathf.Clamp(to.y, a.min.y + a.extents.x, a.max.y - a.extents.x);
        to.y = Mathf.Clamp(from.y, b.min.y + b.extents.x, b.max.y - b.extents.x);
        float reach = settings.captureReach + a.extents.x + b.extents.x;
        return (to - from).sqrMagnitude <= reach * reach &&
               Clear(a.center, b.center, player, settings, false);
    }

    private bool Clear(Vector3 eyes, Vector3 point, CharacterController player, GuardSettings settings,
        bool throughGlass = true)
    {
        Vector3 ray = point - eyes;
        if (ray.sqrMagnitude > settings.sightDistance * settings.sightDistance) return false;
        // 잡기는 몸 기준 수평 도달 판정을 쓰고, 관측은 표시와 같은 눈 기준 입체각을 쓴다.
        Vector3 direction = throughGlass ? ray : Vector3.ProjectOnPlane(ray, Vector3.up);
        Vector3 forward = throughGlass ? EyeRotation * Vector3.forward : transform.forward;
        if (Vector3.Angle(forward, direction) > settings.fieldOfView * .5f) return false;
        return FirstCoverDistance(eyes, ray.normalized, ray.magnitude, player, settings, throughGlass) > ray.magnitude;
    }

    public Vector3 EyePosition(GuardSettings settings) =>
        eyeAnchor ? eyeAnchor.position : transform.position + Vector3.up * settings.eyeHeight;

    // 판정과 부채꼴이 같은 차폐층·유리 규칙을 사용한다. NonAlloc 결과의 순서는 보장되지 않는다.
    public float FirstCoverDistance(Vector3 eyes, Vector3 direction, float distance,
        CharacterController player, GuardSettings settings, bool throughGlass = true)
    {
        int count = Physics.RaycastNonAlloc(eyes, direction, hits, distance,
            settings.sightMask, QueryTriggerInteraction.Ignore);
        if (count == hits.Length) return 0f;
        float nearest = float.PositiveInfinity;
        for (int i = 0; i < count; i++)
        {
            var c = hits[i].collider;
            if (c.transform.IsChildOf(transform) || (player && c.transform.IsChildOf(player.transform)) ||
                (throughGlass && c.GetComponentInParent<SightTransparent>())) continue;
            nearest = Mathf.Min(nearest, hits[i].distance);
        }
        return nearest;
    }
}
