using UnityEngine;

public enum EscapeEncounter { Isolation, Observation, Decontamination, Pumps, Records }

#region 의사코드
// 격리층과 기록층에서는 현장 설비를 직접 조작한다. 관찰층은 감시선 아래로, 설비층은 펌프 소리에 맞춰 통과한다.
// 제염층에서는 분사 구간 안에서 세척 주기가 끝날 때까지 머문다. 중간에 나가면 주기는 멈춘다.
// 현재 층의 조건을 충족하면 두 계단 셔터와 승강기의 상행을 함께 해제한다.
#endregion
public sealed class FloorExperience : MonoBehaviour
{
    [SerializeField] private EscapeEncounter encounter;
    [SerializeField] private Transform start, end;
    [SerializeField] private Transform[] shutters;
    [SerializeField] private Renderer indicator;
    [SerializeField] private Material ready, warning;
    [SerializeField] private ParticleSystem mist;
    [SerializeField] private AudioSource siteSound;
    [SerializeField] private AudioClip pulse, cycle, latch;
    public bool Cleared { get; private set; }
    private bool entered, previousSignal;
    private float elapsed, phase, nextTripSound;
    private float[] raised, staffAccessUntil;

    private void Awake()
    {
        raised = new float[shutters.Length];
        staffAccessUntil = new float[shutters.Length];
    }

    // 직원이 사용하는 계단 셔터만 잠깐 연다. 플레이어의 상행 승인은 층 설비에서 별도로 결정한다.
    public void AllowStaffPassage(Vector3 entrance)
    {
        int nearest = -1;
        float distance = float.PositiveInfinity;
        for (int i = 0; i < shutters.Length; i++)
        {
            float d = Vector3.ProjectOnPlane(shutters[i].position - entrance, Vector3.up).sqrMagnitude;
            if (d >= distance) continue;
            nearest = i;
            distance = d;
        }
        if (nearest >= 0) staffAccessUntil[nearest] = Time.time + 5f;
    }
    private bool recorded;
    private const float Reach = 1.15f;
    public bool CanOperate(bool second) => !Cleared && (encounter == EscapeEncounter.Isolation && !second ||
        encounter == EscapeEncounter.Records && second == recorded);
    public string ActionLabel(bool second) => encounter == EscapeEncounter.Isolation ? "[F] 격리 잠금 해제" :
        second ? "[F] 상행 인계 승인" : "[F] 출입 인계표 확인";
    public string Hint
    {
        get
        {
            if (Cleared) return "상행 개방 · 계단 A / 계단 B / 화물 승강기";
            switch (encounter)
            {
                case EscapeEncounter.Isolation: return "B5 · C02 보안관제실에서 격리 잠금 해제";
                case EscapeEncounter.Observation: return entered ? "진단 감시선 아래로 낮춰 반대편까지 이동" : "B4 · C02 진단실의 청색 진입선에서 몸 낮추기";
                case EscapeEncounter.Decontamination: return entered ? "제염 분사 중 · 표시선 안에 머물기" : "B3 · C02 저온 보관실의 제염 분사대 통과";
                case EscapeEncounter.Pumps: return entered ? "펌프가 울리는 동안 반대편 표식까지 이동" : "B2 · C02 냉각 펌프 점검로에서 녹색 작업등 기다리기";
                default: return recorded ? "C02 인계실 · 맞은편 승인대에서 인계표 승인" : "B1 · C02 기록 인계실에서 출입 인계표 확인";
            }
        }
    }

    public bool PumpMasks(Vector3 point) => !Cleared && encounter == EscapeEncounter.Pumps && phase < 3.8f &&
        (point - start.position).sqrMagnitude < 6f * 6f;

    public bool Operate(bool second, PlayerInventory actor)
    {
        if (!actor || !CanOperate(second) ||
            gameObject.scene != UnityEngine.SceneManagement.SceneManager.GetActiveScene()) return false;
        if (encounter == EscapeEncounter.Records && !second)
        {
            recorded = true;
            if (siteSound && latch) siteSound.PlayOneShot(latch, .5f);
        }
        else Complete();
        return true;
    }

    public void Tick(Vector3 feet, bool crouching, bool grounded)
    {
        for (int i = 0; i < shutters.Length; i++)
        {
            var shutter = shutters[i];
            bool hold = raised[i] > 0f && Near(feet, shutter.position - Vector3.up * (raised[i] + 1f));
            float target = Cleared || Time.time < staffAccessUntil[i] || hold ? 2.45f : 0f;
            float next = Mathf.MoveTowards(raised[i], target, 2.2f * Time.deltaTime);
            if (next == raised[i]) continue;
            shutter.localPosition += Vector3.up * (next - raised[i]);
            raised[i] = next;
        }
        if (Cleared) return;
        if (encounter == EscapeEncounter.Isolation || encounter == EscapeEncounter.Records) return;
        var from = start.position;
        var to = end.position;
        bool atStart = grounded && Near(feet, from);
        bool atEnd = grounded && Near(feet, to);
        bool nearby = (feet - from).sqrMagnitude < 15f * 15f;
        if (encounter == EscapeEncounter.Decontamination)
        {
            if (entered != atStart)
            {
                entered = atStart;
                elapsed = 0f;
                if (entered)
                {
                    if (mist) mist.Play();
                    if (siteSound && cycle) siteSound.PlayOneShot(cycle);
                }
                else
                {
                    if (mist) mist.Stop();
                    if (siteSound) siteSound.Stop();
                }
            }
            SetSignal(entered);
            if (entered && (elapsed += Time.deltaTime) >= 2.8f) Complete();
            return;
        }
        phase = Mathf.Repeat(phase + Time.deltaTime, 6f);
        bool safe = encounter == EscapeEncounter.Observation ? crouching : phase < 3.8f;
        if (encounter == EscapeEncounter.Pumps && nearby && safe && !previousSignal && siteSound && pulse)
            siteSound.PlayOneShot(pulse, .8f);
        SetSignal(encounter == EscapeEncounter.Observation ? entered : safe);
        if (!safe || !grounded)
        {
            if (grounded && Near(feet, (from + to) * .5f) && Time.time >= nextTripSound)
            {
                // 광학선 경고와 조용한 철판의 발소리는 그 자리에서만 들리는 조사 단서다.
                StealthNoise.Emit(feet + Vector3.up * .25f, encounter == EscapeEncounter.Observation ? 13f : 10f, GuardNoise.Impact);
                nextTripSound = Time.time + 4f;
            }
            entered = false;
            return;
        }
        if (atStart) entered = true;
        if (!entered) return;
        var segment = to - from;
        var closest = from + segment * Mathf.Clamp01(Vector3.Dot(feet - from, segment) / segment.sqrMagnitude);
        if ((feet - closest).sqrMagnitude > 1.65f * 1.65f) entered = false;
        else if (atEnd) Complete();
    }

    private static bool Near(Vector3 p, Vector3 target)
    {
        var delta = p - target;
        return Mathf.Abs(delta.y) < .65f && delta.x * delta.x + delta.z * delta.z < Reach * Reach;
    }

    private void SetSignal(bool on)
    {
        if (on == previousSignal) return;
        previousSignal = on;
        if (indicator) indicator.sharedMaterial = on ? ready : warning;
    }

    private void Complete()
    {
        Cleared = true;
        if (indicator) indicator.sharedMaterial = ready;
        if (mist) mist.Stop();
        if (siteSound && latch) siteSound.PlayOneShot(latch);
    }
}
