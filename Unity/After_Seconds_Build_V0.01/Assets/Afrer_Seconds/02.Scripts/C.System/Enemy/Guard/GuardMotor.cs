using UnityEngine;
using UnityEngine.AI;

#region 의사코드
// 목표가 바뀌면 내비메시 경로를 구하고 코너에 닿을 때마다 다음 코너로 향한다.
// 방향을 돌리고 가속도와 중력을 적용해 컨트롤러를 이동한다. 수색 중에는 둘러보고 조준 중에는 표적을 겨눈다.
// 경로가 끝났거나 막혔는지 기록해 다음 판단에 전달한다.
#endregion

// NavMesh는 경로만 정한다. 실제 몸은 CharacterController 하나가 움직인다.
[RequireComponent(typeof(CharacterController))]
public sealed class GuardMotor : MonoBehaviour
{
    private CharacterController body;
    private NavMeshPath path;
    private Vector3 standingCenter;
    private float standingHeight;
    private bool sitting;
    private Vector3[] corners = System.Array.Empty<Vector3>();
    private int nextCorner;
    private Vector3 goal, velocity;
    private float stalled, fallSpeed;
    private double lastPlanTime;
    private bool hasGoal, pathComplete;
    public bool Arrived { get; private set; }
    public bool Exhausted { get; private set; }
    public float GroundSpeed { get; private set; }
    public Vector3 LookDirection { get; private set; }
    private void Awake()
    {
        body = GetComponent<CharacterController>();
        standingCenter = body.center;
        standingHeight = body.height;
        path = new NavMeshPath();
    }

    public void ClearRoute()
    {
        hasGoal = Arrived = Exhausted = false;
        corners = System.Array.Empty<Vector3>();
        nextCorner = 0;
        stalled = 0f;
        LookDirection = Vector3.zero;
    }

    public void Seek(Vector3 nextGoal, GuardSettings settings, bool retry)
    {
        float tolerance = settings.arrivalDistance;
        if (hasGoal && (nextGoal - goal).sqrMagnitude <= tolerance * tolerance &&
            !(retry && Exhausted && Time.fixedTimeAsDouble - lastPlanTime >= settings.stalledTime)) return;
        ClearRoute();
        goal = nextGoal;
        hasGoal = true;
        lastPlanTime = Time.fixedTimeAsDouble;
        float sampleRange = body.radius + body.stepOffset + tolerance;
        if (NavMesh.SamplePosition(transform.position, out var start, sampleRange, NavMesh.AllAreas) &&
            NavMesh.SamplePosition(goal, out var end, sampleRange, NavMesh.AllAreas) &&
            NavMesh.CalculatePath(start.position, end.position, NavMesh.AllAreas, path))
        {
            corners = path.corners;
            pathComplete = path.status == NavMeshPathStatus.PathComplete;
        }
        else pathComplete = false;
    }

    public void Move(GuardSettings settings, float speed, bool searching, float dt, Vector3? aimAt = null)
    {
        Vector3 pos = transform.position;
        while (nextCorner < corners.Length && Flat(corners[nextCorner] - pos).magnitude <= settings.arrivalDistance)
            nextCorner++;
        Vector3 remaining = nextCorner < corners.Length ? Flat(corners[nextCorner] - pos) : Vector3.zero;
        Vector3 direction = remaining.normalized;
        LookDirection = aimAt.HasValue ? Flat(aimAt.Value - pos) : direction;
        if (nextCorner == corners.Length - 1)
            speed = Mathf.Min(speed, Mathf.Sqrt(2f * settings.acceleration * remaining.magnitude));
        if (hasGoal && nextCorner == corners.Length)
        {
            Arrived = pathComplete && Flat(goal - pos).magnitude <= body.radius + settings.arrivalDistance &&
                      Mathf.Abs(goal.y - pos.y) <= body.stepOffset + settings.arrivalDistance;
            Exhausted = !Arrived;
        }
        if (aimAt.HasValue)
        {
            speed = 0f;
            var facingTarget = Flat(aimAt.Value - pos);
            if (facingTarget.sqrMagnitude > .0001f)
                transform.rotation = Quaternion.RotateTowards(transform.rotation, Quaternion.LookRotation(facingTarget),
                    settings.turnSpeed * dt);
        }
        else if (searching) transform.Rotate(Vector3.up, settings.turnSpeed * .5f * dt, Space.World);
        else if (direction != Vector3.zero)
            transform.rotation = Quaternion.RotateTowards(transform.rotation, Quaternion.LookRotation(direction),
                settings.turnSpeed * dt);

        float facing = Mathf.Max(0f, Vector3.Dot(transform.forward, direction));
        velocity = Vector3.MoveTowards(velocity, direction * (speed * facing), settings.acceleration * dt);
        if (body.isGrounded && fallSpeed < 0f) fallSpeed = 0f;
        fallSpeed += Physics.gravity.y * dt;
        var flags = body.Move((velocity + Vector3.up * fallSpeed) * dt);
        if ((flags & CollisionFlags.Below) != 0) fallSpeed = 0f;
        GroundSpeed = Flat(transform.position - pos).magnitude / dt;
        if (!aimAt.HasValue && direction != Vector3.zero && facing > .5f && GroundSpeed < .08f)
        {
            stalled += dt;
            if (stalled >= settings.stalledTime) { nextCorner = corners.Length; pathComplete = false; Exhausted = true; }
        }
        else stalled = 0f;
    }

    // 의자 옆 보행 지점은 그대로 두고, 앉은 동안 몸통 충돌체와 시선을 실제 좌석에 맞춘다.
    public void SitAt(Vector3 seat, Vector3 direction, GuardSettings settings, float dt)
    {
        transform.rotation = Quaternion.RotateTowards(transform.rotation, Quaternion.LookRotation(direction), settings.turnSpeed * dt);
        const float seatBodyHeight = 1.36f;
        if (!sitting) body.height = seatBodyHeight;
        Vector3 center = transform.InverseTransformPoint(seat + Vector3.up * (seatBodyHeight * .5f));
        if ((center - body.center).sqrMagnitude > .000004f) body.center = center;
        sitting = true;
        fallSpeed = GroundSpeed = 0f;
        velocity = Vector3.zero;
    }

    public void StandUp()
    {
        if (!sitting) return;
        body.height = standingHeight;
        body.center = standingCenter;
        sitting = false;
    }

    // 계단참과 층 씬 경계 사이만 제작된 디딤판 경로를 따라 이동한다.
    public bool FollowTreads(Vector3 target, GuardSettings settings, float dt)
    {
        Vector3 start = transform.position;
        Vector3 next = Vector3.MoveTowards(start, target, settings.patrolSpeed * dt);
        var delta = Flat(next - start);
        if (delta.sqrMagnitude > .000001f)
            transform.rotation = Quaternion.RotateTowards(transform.rotation, Quaternion.LookRotation(delta), settings.turnSpeed * dt);
        transform.position = next;
        GroundSpeed = delta.magnitude / dt;
        fallSpeed = 0f;
        velocity = Vector3.zero;
        return (next - target).sqrMagnitude < .0001f;
    }

    private static Vector3 Flat(Vector3 value) => new Vector3(value.x, 0f, value.z);
}
