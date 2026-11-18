using System.Collections.Generic;

// 같은 지연을 쓰므로 명중 순서가 실행 순서다. 시각은 호출자가 게임 시간으로 전달한다.
internal sealed class ThrowSwapQueue
{
    private sealed class Entry
    {
        public ThrownObject Source;
        public SwapTarget Target;
        public double Due;
        public double NextPulse;
    }

    private readonly Queue<Entry> entries = new Queue<Entry>();

    public bool Schedule(ThrownObject source, SwapTarget target, double now, float delay)
    {
        double due = now + delay;
        foreach (var entry in entries)
            if (entry.Due == due && entry.Source == source && entry.Target == target) return false;
        entries.Enqueue(new Entry { Source = source, Target = target, Due = due, NextPulse = now + 1d });
        return true;
    }

    public float TakePulse(double now)
    {
        float strongest = 0f;
        foreach (var entry in entries)
        {
            if (now < entry.NextPulse || now >= entry.Due || !entry.Target || !entry.Target.Available) continue;
            // 끊긴 프레임 사이에 지난 박자는 한 번만 재생하고 다음 게임초에 다시 맞춘다.
            entry.NextPulse += System.Math.Floor(now - entry.NextPulse) + 1d;
            strongest = System.Math.Max(strongest, entry.Due - now <= 1d ? .75f : .55f);
        }
        return strongest;
    }

    public bool TryTake(double now, out SwapTarget target)
    {
        target = null;
        if (entries.Count == 0 || entries.Peek().Due > now) return false;
        target = entries.Dequeue().Target;
        return true;
    }

    public void Clear() => entries.Clear();
}
