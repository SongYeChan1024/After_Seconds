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
    public ThrowShape Shape;
    public Quaternion Rotation;
}

// 투척물 루트 중심을 기준으로 실제 Collider의 크기를 월드 단위로 읽는다.
public struct ThrowShape
{
    public Vector3 HalfExtents;
    public float Radius;
    public bool IsBox => HalfExtents != Vector3.zero;
    public float Reach => IsBox ? HalfExtents.magnitude : Radius;
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
        bool valid = TryShape(prefab, out ThrowShape shape, out body);
        radius = shape.Radius;
        return valid && !shape.IsBox;
    }

    public static bool TryShape(ThrownObject prefab, out ThrowShape shape, out Rigidbody body)
    {
        shape = default;
        body = prefab != null ? prefab.GetComponent<Rigidbody>() : null;
        if (body == null || body.isKinematic || body.constraints != RigidbodyConstraints.None) return false;
        var colliders = prefab.GetComponentsInChildren<Collider>();
        if (colliders.Length != 1 || colliders[0].transform != prefab.transform ||
            colliders[0].isTrigger || !colliders[0].enabled) return false;
        Vector3 s = prefab.transform.lossyScale;
        Vector3 scale = new Vector3(Mathf.Abs(s.x), Mathf.Abs(s.y), Mathf.Abs(s.z));
        if (colliders[0] is BoxCollider box && box.center == Vector3.zero)
        {
            shape.HalfExtents = Vector3.Scale(box.size * .5f, scale);
            return Mathf.Min(shape.HalfExtents.x, shape.HalfExtents.y, shape.HalfExtents.z) > 0f;
        }
        if (colliders[0] is SphereCollider sphere && sphere.center == Vector3.zero)
            shape.Radius = sphere.radius * Mathf.Max(scale.x, scale.y, scale.z);
        return shape.Radius > 0f;
    }
}
