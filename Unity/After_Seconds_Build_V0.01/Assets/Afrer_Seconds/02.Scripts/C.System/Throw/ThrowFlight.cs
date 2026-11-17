using UnityEngine;

// 의사코드: 실제 Rigidbody의 중력·저항을 읽고, 고정 간격마다 속도 → 위치 순서로 전진한다.
// 첫 충돌 이후의 반사/마찰과 움직이는 대상의 미래 위치는 예측하지 않는다.
public struct ThrowLaunch
{
    public Vector3 Position;
    public Vector3 Velocity;
    public Vector3 Gravity;
    public float Damping;
    public float Radius;
}

public static class ThrowFlight
{
    public static void Step(ref Vector3 position, ref Vector3 velocity, Vector3 gravity, float damping, float dt)
    {
        // PhysX의 자유 비행 적분 순서. 해석식의 0.5*g*t*t와 달리 고정 틱의 위치를 비교한다.
        velocity = (velocity + gravity * dt) * Mathf.Max(0f, 1f - damping * dt);
        position += velocity * dt;
    }

    public static bool TryProfile(ThrownObject prefab, out float radius, out Rigidbody body)
    {
        radius = 0f;
        body = prefab != null ? prefab.GetComponent<Rigidbody>() : null;
        if (body == null || body.isKinematic || body.constraints != RigidbodyConstraints.None) return false;
        // 현재 시험용 공은 중심이 원점인 단일 SphereCollider다.
        // 다른 형태를 정확한 구체라고 가장하지 않고, 반입 시 해당 형상의 예측을 추가하도록 거절한다.
        var colliders = prefab.GetComponentsInChildren<Collider>();
        if (colliders.Length != 1 || !(colliders[0] is SphereCollider sphere) || sphere.isTrigger || !sphere.enabled)
            return false;
        if (sphere.transform != prefab.transform || sphere.center.sqrMagnitude > 0.000001f) return false;
        Vector3 scale = sphere.transform.lossyScale;
        radius = sphere.radius * Mathf.Max(Mathf.Abs(scale.x), Mathf.Abs(scale.y), Mathf.Abs(scale.z));
        return radius > 0f;
    }
}
