using UnityEngine;

// 의사코드: 상대의 현재 발 위치에서 현재 모양이 들어가면 공중에서도 그대로 교환한다.
// 겹치면 계단·경사 접점을 먼저 찾고 같은 쪽의 가까운 빈자리를 검사한다.
// 깊은 틈은 출발 쪽에서 접근 가능한 가장 가까운 지점을 쓰고, 양쪽 도착 공간을 함께 확보한다.
internal sealed class SwapPlacement
{
    private static readonly float[] Radii = { .08f, .18f, .34f, .55f, .82f, 1.15f, 1.6f, 2.2f, 3.1f, 4.3f };
    private static readonly Vector3[] Directions =
    {
        Vector3.forward, Vector3.right, Vector3.left, Vector3.back,
        new Vector3(.7071f,0,.7071f), new Vector3(-.7071f,0,.7071f),
        new Vector3(.7071f,0,-.7071f), new Vector3(-.7071f,0,-.7071f)
    };
    private readonly CharacterController player;
    private readonly SwapTarget target;
    private readonly float step;
    // 한 교환의 후보들이 버퍼를 공유한다. 밀집한 구역에서 버퍼가 가득 차면 전체 결과를 검사한다.
    private readonly Collider[] contacts = new Collider[16];

    internal SwapPlacement(CharacterController player, SwapTarget target)
    {
        this.player = player;
        this.target = target;
        step = player.stepOffset + player.skinWidth;
    }

    internal bool TryPair(Vector3 playerFeet, Vector3 targetFeet, out Vector3 playerOffset, out Vector3 otherOffset)
    {
        var actor = new Shape(player);
        var other = new Shape(target.Body);
        if (Find(actor, playerFeet, targetFeet, null, out playerOffset) &&
            Find(other, targetFeet, playerFeet, actor.At(playerOffset), out otherOffset)) return true;

        // 서로 아주 가까우면 먼저 정한 보정 위치가 상대의 유일한 자리를 차지할 수 있다.
        return Find(other, targetFeet, playerFeet, null, out otherOffset) &&
               Find(actor, playerFeet, targetFeet, other.At(otherOffset), out playerOffset);
    }

    private bool Find(Shape shape, Vector3 from, Vector3 to, Bounds? reserved, out Vector3 offset)
    {
        Vector3 exact = to - from;
        offset = exact;
        if (Fits(shape, exact, reserved)) return true;
        if (Settle(shape, exact, reserved, out offset)) return true;

        Vector3 toward = Vector3.ProjectOnPlane(from - to, Vector3.up);
        Quaternion basis = toward.sqrMagnitude > .0001f ? Quaternion.LookRotation(toward) : Quaternion.identity;
        bool grounded = GroundNear(to);
        foreach (float radius in Radii)
        {
            foreach (var unit in Directions)
            {
                Vector3 shift = basis * unit * radius;
                if (!SideFits(shape, exact, to, shift, grounded, reserved)) continue;
                // 첫 빈자리가 발견된 방향에서 여유 폭만큼만 비켜 선다.
                float blocked = 0f, clear = 1f;
                for (int i = 0; i < 5; i++)
                {
                    float mid = (blocked + clear) * .5f;
                    if (SideFits(shape, exact, to, shift * mid, grounded, reserved)) clear = mid;
                    else blocked = mid;
                }
                offset = exact + shift * clear;
                return true;
            }
        }

        // 작은 물건이 긴 틈 속에 있다면 몸 전체를 출발점에서 목적지 방향으로 쓸어 입구 직전에 둔다.
        float length = exact.magnitude;
        if (length < .02f) return false;
        Vector3 direction = exact / length;
        float travel = length;
        foreach (var hit in shape.Cast(Vector3.zero, direction, length))
        {
            if (Ignored(hit.collider) || hit.distance <= 0f || Vector3.Dot(hit.normal, direction) >= -.001f) continue;
            travel = Mathf.Min(travel, hit.distance - Physics.defaultContactOffset);
        }
        if (travel < .02f) return false;
        offset = direction * travel;
        return Fits(shape, offset, reserved) && !Obstructed(from + Vector3.up * .10f, offset);
    }

    private bool SideFits(Shape shape, Vector3 exact, Vector3 to, Vector3 shift, bool grounded, Bounds? reserved)
    {
        return Fits(shape, exact + shift, reserved) && (!grounded || GroundNear(to + shift)) &&
               !Obstructed(to + Vector3.up * .10f, shift);
    }

    private bool Settle(Shape shape, Vector3 exact, Bounds? reserved, out Vector3 offset)
    {
        Vector3 raised = exact + Vector3.up * step;
        offset = exact;
        float nearest = float.PositiveInfinity;
        foreach (var hit in shape.Cast(raised, Vector3.down, 2f * step))
        {
            if (Ignored(hit.collider) || hit.distance <= 0f || hit.distance >= nearest ||
                Vector3.Angle(hit.normal, Vector3.up) > player.slopeLimit) continue;
            // 바닥에서 살짝 들어 올리는 범위만 허용한다. 천장 윗면으로 올라가지는 않는다.
            if (hit.point.y > shape.At(exact).min.y + player.skinWidth + Physics.defaultContactOffset) continue;
            nearest = hit.distance;
        }
        if (float.IsPositiveInfinity(nearest)) return false;
        offset = raised - Vector3.up * nearest;
        return Fits(shape, offset, reserved);
    }

    private bool GroundNear(Vector3 feet)
    {
        foreach (var hit in Physics.RaycastAll(feet + Vector3.up * player.skinWidth, Vector3.down,
                     step + player.skinWidth, Physics.AllLayers, QueryTriggerInteraction.Ignore))
            if (!Ignored(hit.collider) && Vector3.Angle(hit.normal, Vector3.up) <= player.slopeLimit) return true;
        return false;
    }

    private bool Obstructed(Vector3 origin, Vector3 delta)
    {
        foreach (var hit in Physics.RaycastAll(origin, delta.normalized, delta.magnitude, Physics.AllLayers, QueryTriggerInteraction.Ignore))
            if (!Ignored(hit.collider)) return true;
        return false;
    }

    private bool Ignored(Collider other) => other.transform.IsChildOf(player.transform) ||
        other.transform.IsChildOf(target.transform) || target.IsReleasedEquipment(other);

    private bool Fits(Shape shape, Vector3 offset, Bounds? reserved)
    {
        if (reserved.HasValue && reserved.Value.Intersects(shape.At(offset))) return false;
        int n = shape.Overlap(offset, contacts);
        var hits = n == contacts.Length ? shape.AllOverlaps(offset) : contacts;
        if (hits != contacts) n = hits.Length;
        for (int i = 0; i < n; i++) if (!Ignored(hits[i])) return false;
        return true;
    }

    private readonly struct Shape
    {
        private readonly Bounds bounds;
        private readonly Quaternion rotation;
        private readonly bool box;
        private readonly Vector3 half, axis;
        private readonly float radius;

        public Shape(Collider body)
        {
            bounds = body.bounds;
            rotation = body.transform.rotation;
            box = body is BoxCollider;
            half = bounds.extents;
            float r = Mathf.Max(half.x, half.z);
            axis = Vector3.up * Mathf.Max(0f, half.y - r);
            radius = r - Mathf.Min(Physics.defaultContactOffset, r * .25f);
            if (body is BoxCollider b)
            {
                Vector3 s = b.transform.lossyScale;
                half = Vector3.Scale(b.size, new Vector3(Mathf.Abs(s.x), Mathf.Abs(s.y), Mathf.Abs(s.z))) * .5f;
                half -= Vector3.one * Mathf.Min(Physics.defaultContactOffset, .25f * Mathf.Min(half.x, half.y, half.z));
            }
        }

        public Bounds At(Vector3 offset) => new Bounds(bounds.center + offset, bounds.size);

        public int Overlap(Vector3 offset, Collider[] result)
        {
            Vector3 c = bounds.center + offset;
            return box ? Physics.OverlapBoxNonAlloc(c, half, result, rotation, ~0, QueryTriggerInteraction.Ignore)
                       : Physics.OverlapCapsuleNonAlloc(c-axis, c+axis, radius, result, ~0, QueryTriggerInteraction.Ignore);
        }

        public Collider[] AllOverlaps(Vector3 offset)
        {
            Vector3 c = bounds.center + offset;
            return box ? Physics.OverlapBox(c, half, rotation, ~0, QueryTriggerInteraction.Ignore)
                       : Physics.OverlapCapsule(c-axis, c+axis, radius, ~0, QueryTriggerInteraction.Ignore);
        }

        public RaycastHit[] Cast(Vector3 offset, Vector3 direction, float length)
        {
            Vector3 c = bounds.center + offset;
            return box ? Physics.BoxCastAll(c, half, direction, rotation, length, ~0, QueryTriggerInteraction.Ignore)
                       : Physics.CapsuleCastAll(c-axis, c+axis, radius, direction, length, ~0, QueryTriggerInteraction.Ignore);
        }
    }
}
