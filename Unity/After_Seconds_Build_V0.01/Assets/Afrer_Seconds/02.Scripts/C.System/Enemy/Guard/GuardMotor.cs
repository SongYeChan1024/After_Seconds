using UnityEngine;
using UnityEngine.AI;

// NavMesh는 경로만 정한다. 실제 몸은 CharacterController 하나가 움직인다.
[RequireComponent(typeof(CharacterController))]
public sealed class GuardMotor : MonoBehaviour
{
    private CharacterController body;
    private NavMeshPath path;
    private Vector3[] corners = System.Array.Empty<Vector3>();
    private int nextCorner;
    private Vector3 goal, velocity;
    private float stalled, fallSpeed;
    private double lastPlanTime;
    private bool hasGoal, pathComplete;
    public bool Arrived { get; private set; }
    public bool Exhausted { get; private set; }
    public float GroundSpeed { get; private set; }
    private void Awake()
    {
        body = GetComponent<CharacterController>();
        path = new NavMeshPath();
    }

    public void ClearRoute()
    {
        hasGoal = Arrived = Exhausted = false;
        corners = System.Array.Empty<Vector3>();
        nextCorner = 0;
        stalled = 0f;
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

    public void Move(GuardSettings settings, float speed, bool searching, float dt)
    {
        Vector3 pos = transform.position;
        while (nextCorner < corners.Length && Flat(corners[nextCorner] - pos).magnitude <= settings.arrivalDistance)
            nextCorner++;
        Vector3 remaining = nextCorner < corners.Length ? Flat(corners[nextCorner] - pos) : Vector3.zero;
        Vector3 direction = remaining.normalized;
        if (nextCorner == corners.Length - 1)
            speed = Mathf.Min(speed, Mathf.Sqrt(2f * settings.acceleration * remaining.magnitude));
        if (hasGoal && nextCorner == corners.Length)
        {
            Arrived = pathComplete && Flat(goal - pos).magnitude <= body.radius + settings.arrivalDistance &&
                      Mathf.Abs(goal.y - pos.y) <= body.stepOffset + settings.arrivalDistance;
            Exhausted = !Arrived;
        }
        if (searching) transform.Rotate(Vector3.up, settings.turnSpeed * .5f * dt, Space.World);
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
        if (direction != Vector3.zero && facing > .5f && GroundSpeed < .08f)
        {
            stalled += dt;
            if (stalled >= settings.stalledTime) { nextCorner = corners.Length; pathComplete = false; Exhausted = true; }
        }
        else stalled = 0f;
    }

    private static Vector3 Flat(Vector3 value) => new Vector3(value.x, 0f, value.z);
}
