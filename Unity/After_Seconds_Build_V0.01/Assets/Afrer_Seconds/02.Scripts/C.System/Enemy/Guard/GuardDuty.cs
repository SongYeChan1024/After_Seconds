using UnityEngine;
using UnityEngine.AI;

#region 의사코드
// 조사와 추격이 순찰을 끊으면 미방문 지점을 보존한다. 실제 도착한 정지점만 방문으로 센다.
// 복도 한 바퀴가 끝나면 마지막 위치에서 기다린다. 돔에서는 착석 감시·고정 감시·보행을 구역에 맞춰 반복한다.
// 출입 계단의 짧은 연결 구간 뒤에는 일반 내비메시 보행을 이용한다. 근무 인계는 두 사람의 실제 도착으로 판정한다.
#endregion
public sealed class GuardDuty : MonoBehaviour
{
    public event System.Action<GuardDuty, Vector3> IntruderReported;
    public bool Assigned => route != null;
    public bool AvailableForCall => Assigned && !changingShift && !OnStairs && !AtStairExit && !Investigating;
    public int RouteIndex { get; private set; }
    private bool reachedHandover;
    public bool AtHandover => reachedHandover && (transform.position - handover).sqrMagnitude <= .6f * .6f;
    public bool Investigating { get; private set; }
    public Vector3 InvestigatePoint { get; private set; }
    private Vector3 reportOrigin;
    private bool checkingAccess;
    // 배식구 안팎과 같은 근처에서 이어진 목격·총성은 같은 대응으로 센다.
    public static bool SameIncident(Vector3 first, Vector3 second) => (first - second).sqrMagnitude <= 10f * 10f;
    public bool RespondingTo(Vector3 point, bool access) => Investigating && checkingAccess == access && SameIncident(reportOrigin, point);
    public bool CircuitDone { get; private set; }
    public int StopIndex => stop;
    public Vector3? WatchTarget { get; private set; }
    public bool Seated { get; private set; }
    public Vector3 SeatFeet { get; private set; }
    public bool OnStairs { get; private set; }
    private Vector3 stairBend, stairEnd;
    private bool secondStairLeg, exiting;
    public bool AtStairExit { get; private set; }

    public void EnterStairs(Vector3 bend, Vector3 end, bool leaving = false)
    {
        stairBend = bend;
        stairEnd = end;
        secondStairLeg = AtStairExit = false;
        exiting = leaving;
        OnStairs = true;
        ClearPost();
    }

    public void WalkStairs(GuardMotor motor, GuardSettings settings, float dt)
    {
        if (!motor.FollowTreads(secondStairLeg ? stairEnd : stairBend, settings, dt)) return;
        if (secondStairLeg) { OnStairs = false; AtStairExit = exiting; motor.ClearRoute(); }
        secondStairLeg = true;
    }

    public void LeaveStairs() => AtStairExit = OnStairs = false;
    public float ScanAngle => Mathf.Sin(Time.time * .53f + scanPhase) * 38f;

    private Vector3[] route, accessPoints;
    private bool[] inspectionStops;
    private int stop;
    private bool changingShift, once, indoor;
    private DomeWatchMode watchMode;
    private Vector3 handover;
    private float dwell, searchUntil, expires, facingYaw, scanPhase;
    public void ReportIntruder(Vector3 point) => IntruderReported?.Invoke(this, point);

    public void Assign(int index, Vector3[] points, int first, Vector3[] entrances = null, bool[] inspections = null)
    {
        RouteIndex = index;
        route = points;
        accessPoints = entrances ?? points;
        inspectionStops = inspections != null && inspections.Length == points.Length ? inspections : null;
        stop = first % points.Length;
        changingShift = reachedHandover = once = indoor = CircuitDone = false;
        ClearPost();
        dwell = 0f;
    }

    public void BeginCircuit(Vector3[] points, Vector3[] entrances = null, bool[] inspections = null)
    {
        Assign(1, points, 0, entrances, inspections);
        once = true;
    }

    public void Watch(Vector3[] points, DomeWatchMode mode, float yaw, Vector3 seatFeet, Vector3[] entrances = null)
    {
        Assign(0, points, 0, entrances);
        indoor = true;
        watchMode = mode;
        facingYaw = yaw;
        SeatFeet = seatFeet;
        scanPhase = Mathf.Repeat(transform.position.x + transform.position.z, 6f);
    }

    public void MeetAt(Vector3 point)
    {
        handover = point;
        changingShift = true;
        reachedHandover = false;
        ClearPost();
    }

    public void CancelMeeting() { changingShift = reachedHandover = false; }
    public void ClearPost() { Seated = false; WatchTarget = null; }

    public void Investigate(Vector3 point, float seconds)
    {
        reportOrigin = point;
        checkingAccess = false;
        InvestigatePoint = NavMesh.SamplePosition(point, out var ground, 2.5f, NavMesh.AllAreas)
            ? ground.position : new Vector3(point.x, transform.position.y, point.z);
        Investigating = true;
        searchUntil = 0f;
        expires = Time.time + seconds;
        reachedHandover = false;
        ClearPost();
    }

    public bool TryAccessPoint(Vector3 report, out Vector3 nearest)
    {
        nearest = default;
        if (!Assigned) return false;
        float best = float.PositiveInfinity;
        foreach (var point in accessPoints)
        {
            float distance = (point - report).sqrMagnitude;
            if (distance >= 6f * 6f && distance < best) { best = distance; nearest = point; }
        }
        return !float.IsPositiveInfinity(best);
    }

    public void CheckAccess(Vector3 report)
    {
        if (TryAccessPoint(report, out var post)) CheckAccess(report, post);
    }

    public void CheckAccess(Vector3 report, Vector3 post)
    {
        Investigate(post, 16f);
        reportOrigin = report;
        checkingAccess = true;
    }

    public void ClearInvestigation() => Investigating = false;

    public bool Tick(GuardMotor motor, GuardSettings settings, float step)
    {
        if (!Assigned) return false;
        ClearPost();
        if (Investigating)
        {
            if (Time.time < expires)
            {
                motor.Seek(InvestigatePoint, settings, true);
                if (!motor.Arrived && !motor.Exhausted) return false;
                if (searchUntil == 0f) searchUntil = Time.time + 2.5f;
                if (Time.time < searchUntil) return true;
            }
            Investigating = false;
        }
        if (changingShift)
        {
            motor.Seek(handover, settings, true);
            reachedHandover = motor.Arrived;
            return false;
        }
        motor.Seek(route[stop], settings, true);
        if (!motor.Arrived) { dwell = 0f; return false; }
        if (indoor && (watchMode == DomeWatchMode.Seated || watchMode == DomeWatchMode.Standing ||
            (watchMode == DomeWatchMode.Mixed && stop == 0)))
        {
            Seated = watchMode == DomeWatchMode.Seated;
            var facing = Quaternion.Euler(0f, facingYaw + (Seated ? 0f : ScanAngle), 0f) * Vector3.forward;
            WatchTarget = transform.position + facing * 3f;
            if (watchMode != DomeWatchMode.Mixed) return false;
        }
        if (CircuitDone) return false;
        // 복도 보행선의 굴곡은 계속 통과하고, 끝의 점검 지점에서는 주위를 살핀다.
        if (inspectionStops != null && !inspectionStops[stop] && !(once && stop == route.Length - 1))
        {
            stop = (stop + 1) % route.Length;
            dwell = 0f;
            motor.Seek(route[stop], settings, true);
            return false;
        }
        dwell += step;
        float wait = settings.patrolWait * (indoor && watchMode == DomeWatchMode.Mixed && stop == 0 ? 3f : 1f);
        if (dwell >= wait)
        {
            dwell = 0f;
            if (once && stop == route.Length - 1) CircuitDone = true;
            else stop = (stop + 1) % route.Length;
        }
        return !WatchTarget.HasValue;
    }
}
