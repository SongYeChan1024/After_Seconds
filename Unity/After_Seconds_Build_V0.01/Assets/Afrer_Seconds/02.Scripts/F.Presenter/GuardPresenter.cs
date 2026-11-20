using UnityEngine;
using Position = System.Numerics.Vector3;

#region 의사코드
// 판단 주기에 눈 위치에서 플레이어의 노출량을 읽어 인식 상태와 이동 목표를 갱신한다.
// 추격 중 유효 사선이 유지되면 예고 뒤 사격한다. 근거리에서는 붙잡기를 예고하고 성립 조건을 다시 검사한다.
// 직접 목격이 우선이다. 평시에는 지정 순찰·인계점, 소음이나 동료 발견 때는 마지막 보고 지점으로 이동한다.
// 제압되면 이동·시야 표시와 사격을 중단한다. 교환으로 자리가 바뀌면 경로와 붙잡기 예고를 비운다.
#endregion

[RequireComponent(typeof(GuardMotor), typeof(GuardSight), typeof(SwapTarget))]
public sealed class GuardPresenter : MonoBehaviour
{
    [SerializeField] private GuardSettings settings;
    [Tooltip("처음 배식 위치 기준, 두 번째 순찰 지점의 로컬 오프셋(m)")]
    [SerializeField] private Vector3 patrolOffset;
    [SerializeField] private Animator animator;
    [SerializeField] private GuardSightView sightView;
    [Tooltip("순찰·추격 발소리용 3D AudioSource. 클립은 소스에 지정한다.")]
    [SerializeField] private AudioSource footsteps;
    public bool HasFootstepClip => footsteps && footsteps.clip;
    private float stepDistance;
    private static readonly int Speed = Animator.StringToHash("Speed");
    private readonly GuardBrain brain = new GuardBrain();
    private GuardMotor motor;
    private GuardDuty duty;
    private bool scanAtPost;
    private GuardPostPose postPose;
    public GuardDuty Duty => duty;
    public GuardLoadout Equipment => loadout;
    public GuardSettings Settings => settings;
    public bool IsDown => loadout && loadout.IsDown;
    public Vector3 EyePoint => sight.EyePosition(settings);
    public bool SoundBlocked(Vector3 point)
    {
        Vector3 delta = point + Vector3.up * .15f - EyePoint;
        return sight.FirstCoverDistance(EyePoint, delta.normalized, delta.magnitude, playerBody, settings, false) < delta.magnitude - .25f;
    }
    public bool SeesFallen(GuardPresenter other) => sight.SeesFallen(other.swap, settings);
    private GuardSight sight;
    private GuardLoadout loadout;
    private IDamageable playerDamage;
    private double? shotAt;
    private double nextWarningAt;
    public bool ShotPending => shotAt.HasValue && isActiveAndEnabled;
    private SwapTarget swap;
    private PlayerMotor player;
    private CharacterController playerBody, guardBody;
    private Vector3 home, patrolEnd;
    private float elapsed;
    public GuardState State => brain.State;
    public bool IsChasing => State == GuardState.Chase;
    public bool RedAlert => IsChasing || State == GuardState.Search;
    public double IdentifiedAt { get; private set; } = double.NegativeInfinity;
    public bool HasSight { get; private set; }
    public Vector3 AlertAnchor => sight.EyePosition(settings) + Vector3.up * .35f;
    public float Recognition => brain.Recognition;
    public Vector3 LastSeen => new Vector3(brain.LastSeen.X, brain.LastSeen.Y, brain.LastSeen.Z);
    public double ObservedAt => brain.ObservedAt;
    public bool CapturePending => brain.CapturePending;
    public bool Captured { get; private set; }

    private void Awake()
    {
        duty = GetComponent<GuardDuty>();
        elapsed = Mathf.Repeat(transform.position.x * .017f, .095f);
        motor = GetComponent<GuardMotor>();
        sight = GetComponent<GuardSight>();
        loadout = GetComponent<GuardLoadout>();
        swap = GetComponent<SwapTarget>();
        guardBody = GetComponent<CharacterController>();
        home = transform.position;
        patrolEnd = transform.TransformPoint(patrolOffset);
    }
    private void OnEnable()
    {
        postPose ??= new GuardPostPose(animator);
        swap.Relocated += OnRelocated;
        if (loadout) loadout.TakenDown += OnTakenDown;
    }

    private void OnTakenDown()
    {
        // 쓰러질 때는 지금 보이는 순찰·착석 자세에서 이어서 넘어간다.
        if (loadout) loadout.SetPostOffset(Vector3.zero);
        brain.CancelCapture();
        motor.ClearRoute();
        HasSight = false;
        enabled = false;
    }
    private void OnDisable()
    {
        shotAt = null;
        swap.Relocated -= OnRelocated;
        if (loadout) loadout.TakenDown -= OnTakenDown;
        if (sightView) sightView.Hide();
    }
    private void OnRelocated()
    {
        if (duty) { duty.LeaveStairs(); duty.ClearPost(); }
        shotAt = null;
        motor.ClearRoute();
        brain.CancelCapture();
    }

    public void BindPlayer(PlayerMotor target)
    {
        duty = GetComponent<GuardDuty>();
        player = target;
        playerDamage = target ? target.GetComponent<IDamageable>() : null;
        if (player) playerBody = player.GetComponent<CharacterController>();
        if (!settings || !playerBody)
        {
            Debug.LogError("경비에게 이동 설정과 씬의 플레이어가 필요합니다.", this);
            enabled = false;
        }
    }

    private void FixedUpdate()
    {
        if (!playerBody || !playerBody.enabled || Captured) return;
        float dt = Time.fixedDeltaTime;
        elapsed += dt;
        if (elapsed + .000001f >= settings.decisionInterval)
        {
            float step = elapsed;
            elapsed = 0f;
            float exposure = sight.Exposure(playerBody, settings);
            HasSight = exposure > 0f;
            if (loadout) loadout.InteractionBlocked = HasSight || Captured;
            Position? observation = null;
            if (exposure > 0f)
            {
                var b = playerBody.bounds;
                observation = new Position(b.center.x, b.min.y, b.center.z);
            }
            float identify = player && player.IsCrouching ? settings.identifyCrouching : settings.identifyStanding;
            bool wasRed = RedAlert;
            brain.Tick(Time.fixedTimeAsDouble, step, observation, exposure / identify,
                1f / settings.forgetExposure, motor.Arrived, motor.Exhausted, settings.patrolWait, settings.searchTime);
            if (!wasRed && RedAlert)
            {
                IdentifiedAt = brain.ObservedAt;
                if (duty && duty.Assigned) duty.ReportIntruder(LastSeen);
            }
            if (RedAlert && duty) duty.ClearInvestigation();
            UpdateShot();
            if (sightView)
            {
                float displayRange = settings.sightDistance * 2f;
                if (settings.showDebugSightCone && (transform.position - player.transform.position).sqrMagnitude <= displayRange * displayRange)
                    sightView.Draw(sight, settings, playerBody, RedAlert, Recognition);
                else sightView.Hide();
            }
            if (RedAlert && duty) duty.ClearPost();
            scanAtPost = false;
            if (State == GuardState.Search) motor.ClearRoute();
            else if (!IsChasing && duty && duty.Assigned) scanAtPost = duty.Tick(motor, settings, step);
            else
            {
                Vector3 goal = State == GuardState.Chase ? LastSeen :
                    State == GuardState.Patrol && brain.PatrolIndex == 1 ? patrolEnd : home;
                motor.Seek(goal, settings, State == GuardState.Return || exposure > 0f);
            }
        }
        if (duty && duty.Seated && duty.WatchTarget.HasValue && !RedAlert && !duty.Investigating)
        {
            motor.SitAt(duty.SeatFeet, duty.WatchTarget.Value - transform.position, settings, dt);
            if (animator) animator.SetFloat(Speed, 0f, .12f, dt);
            return;
        }
        motor.StandUp();
        if (duty && duty.AtStairExit)
        {
            if (!RedAlert) { if (animator) animator.SetFloat(Speed, 0f); return; }
            duty.LeaveStairs();
        }
        if (duty && duty.OnStairs)
            duty.WalkStairs(motor, settings, dt);
        else motor.Move(settings, State == GuardState.Chase ? settings.chaseSpeed : settings.patrolSpeed,
            State == GuardState.Search || scanAtPost, dt, ShotPending ? playerBody.bounds.center : duty?.WatchTarget);
        if (animator) animator.SetFloat(Speed, motor.GroundSpeed, .12f, dt);
        // 실제 이동한 거리로 걸음 박자를 맞춘다. 동료의 소음 조사에는 전달하지 않는다.
        if (HasFootstepClip && motor.GroundSpeed > .1f)
        {
            stepDistance += motor.GroundSpeed * dt;
            float stride = IsChasing ? 1.5f : .8f;
            if (stepDistance >= stride)
            {
                stepDistance %= stride;
                if ((player.transform.position - transform.position).sqrMagnitude <= footsteps.maxDistance * footsteps.maxDistance)
                    footsteps.PlayOneShot(footsteps.clip);
            }
        }
    }

    private void UpdateShot()
    {
        if (!IsChasing || !HasSight || !loadout || !loadout.HasLoadedPistol || playerDamage == null || playerDamage.CurrentHP == 0 ||
            sight.CanReach(guardBody, playerBody, settings))
        {
            shotAt = null;
            return;
        }
        var origin = sight.EyePosition(settings);
        var path = playerBody.bounds.center - origin;
        if (sight.FirstCoverDistance(origin, path.normalized, path.magnitude, playerBody, settings, false) <= path.magnitude)
        {
            shotAt = null;
            return;
        }
        double now = Time.fixedTimeAsDouble;
        if (now < nextWarningAt) return;
        shotAt ??= now + settings.shotWarningTime;
        if (now < shotAt.Value) return;
        if (loadout.TryFireAt(playerDamage)) StealthNoise.Emit(EyePoint, 30f, GuardNoise.Gunshot);
        shotAt = null;
        nextWarningAt = now + settings.shotCooldown;
    }

    // Update에서 성립한 교환은 먼저 예고를 지운다. 새 자리에서 다시 닿으면 처음부터 센다.
    private void Update()
    {
        if (loadout) loadout.RestoreHitPose();
        postPose?.Restore();
    }

    private void LateUpdate()
    {
        if (duty && loadout)
            loadout.SetPostOffset(transform.InverseTransformVector(postPose.Draw(transform, duty, duty.Seated && !RedAlert && !duty.Investigating)));
        bool readingRoute = State == GuardState.Patrol && (!duty || (!duty.Seated && !duty.OnStairs && !duty.Investigating));
        postPose?.LookAhead(transform, readingRoute ? motor.LookDirection : Vector3.zero);
        if (loadout) loadout.DrawHitPose();
        if (!playerBody || Captured || Time.timeScale == 0f) return;
        bool inReach = State == GuardState.Chase && sight.CanReach(guardBody, playerBody, settings);
        Captured = brain.CheckCapture(inReach, Time.timeAsDouble, settings.captureWarningTime);
    }
}
