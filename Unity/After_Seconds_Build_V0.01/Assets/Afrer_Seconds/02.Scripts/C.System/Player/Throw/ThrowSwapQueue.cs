using System.Collections.Generic;

#region 의사코드
// 명중 시 대상과 월드 등록 회차, 실행 시각을 저장한다. 한 번 보관된 아이템의 이전 예약은 취소한다.
// 유효한 예약의 다음 박자를 계산한다. 경비가 쓰러져도 같은 대상이면 지금 자세로 교환한다.
#endregion

// 같은 지연을 쓰므로 명중 순서가 실행 순서다. 시각은 호출자가 게임 시간으로 전달한다.
internal sealed class ThrowSwapQueue
{
    internal sealed class Entry
    {
        public ThrownObject Source;
        public SwapTarget Target;
        public uint WorldRevision;
        public bool StillAvailable => Target && Target.Available && Target.WorldRevision == WorldRevision;
        public double Due;
        public double NextPulse;
        public double RetryAt;
        public bool WaitingForSpace => RetryAt > 0;
    }

    private readonly List<Entry> entries = new List<Entry>();

    public bool Schedule(ThrownObject source, SwapTarget target, double now, float delay)
    {
        double due = now + delay;
        foreach (var entry in entries)
            if (entry.Due == due && entry.Source == source && entry.Target == target) return false;
        entries.Add(new Entry { Source = source, Target = target, WorldRevision = target.WorldRevision, Due = due, NextPulse = now + 1d });
        return true;
    }

    public float TakePulse(double now)
    {
        float strongest = 0f;
        foreach (var entry in entries)
        {
            if (now < entry.NextPulse || now >= entry.Due || !entry.StillAvailable) continue;
            // 끊긴 프레임 사이에 지난 박자는 한 번만 재생하고 다음 게임초에 다시 맞춘다.
            entry.NextPulse += System.Math.Floor(now - entry.NextPulse) + 1d;
            strongest = System.Math.Max(strongest, entry.Due - now <= 1d ? .85f : .70f);
        }
        return strongest;
    }

    public bool TryTake(double now, out Entry entry)
    {
        for (int i = 0; i < entries.Count; i++)
        {
            entry = entries[i];
            if (now < entry.Due || now < entry.RetryAt) continue;
            entries.RemoveAt(i);
            return true;
        }
        entry = null;
        return false;
    }

    // 밀폐된 공간이 열리면 최초 예약을 이어 간다. 대기 중인 한 건이 다른 교환을 막지 않는다.
    public void WaitForSpace(Entry entry, double now)
    {
        entry.RetryAt = now + .25d;
        entries.Add(entry);
    }

    public bool Contains(SwapTarget target)
    {
        foreach (var entry in entries)
            if (entry.Target == target && entry.StillAvailable) return true;
        return false;
    }

    public void Clear() => entries.Clear();
}
