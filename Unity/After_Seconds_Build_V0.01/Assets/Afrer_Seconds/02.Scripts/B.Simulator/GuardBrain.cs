using System;
using System.Numerics;

// 매 판단 틱에 실제로 보인 위치만 전달받는다. 기억은 월드 좌표 값으로 보관한다.
public sealed class GuardBrain
{
    public GuardState State { get; private set; }
    public Vector3 LastSeen { get; private set; }
    public double ObservedAt { get; private set; }
    public int PatrolIndex { get; private set; }
    public float Recognition { get; private set; }
    private double dwell;
    private double? captureStarted;
    public bool CapturePending => captureStarted.HasValue;

    public bool CheckCapture(bool withinReach, double now, float warningTime)
    {
        if (State != GuardState.Chase || !withinReach)
        {
            CancelCapture();
            return false;
        }
        captureStarted ??= now;
        return now - captureStarted.Value >= warningTime;
    }

    public void CancelCapture() => captureStarted = null;

    public void Tick(double now, float dt, Vector3? visibleFeet, float detectionRate,
        float decayRate, bool arrived, bool routeExhausted, float patrolWait, float searchTime)
    {
        if (dt <= 0f) return;
        bool alert = State == GuardState.Chase || State == GuardState.Search;
        if (alert)
            Recognition = visibleFeet.HasValue ? 1f : Math.Max(0f, Recognition - dt / Math.Max(.01f, searchTime));
        else
            Recognition = Math.Min(1f, Math.Max(0f, Recognition +
                dt * (visibleFeet.HasValue ? detectionRate : -decayRate)));
        if (visibleFeet.HasValue && (alert || Recognition >= .99999f))
        {
            State = GuardState.Chase;
            Recognition = 1f;
            LastSeen = visibleFeet.Value;
            ObservedAt = now;
            dwell = 0f;
            return;
        }
        // 빨간 게이지의 시간은 마지막 목격부터 센다. 목적지에 먼저 도달해도 경계를 유지한다.
        if (alert && Recognition <= .00001f)
        {
            Recognition = 0f;
            State = GuardState.Return;
            dwell = 0f;
            CancelCapture();
            return;
        }
        switch (State)
        {
            case GuardState.Patrol:
                dwell = arrived || routeExhausted ? dwell + dt : 0f;
                if (dwell + 1e-6 >= patrolWait) { PatrolIndex = 1 - PatrolIndex; dwell = 0f; }
                break;
            case GuardState.Chase:
                if (arrived || routeExhausted)
                    State = GuardState.Search;
                break;
            case GuardState.Return:
                if (arrived) { State = GuardState.Patrol; PatrolIndex = 0; dwell = 0f; }
                break;
        }
    }
}
