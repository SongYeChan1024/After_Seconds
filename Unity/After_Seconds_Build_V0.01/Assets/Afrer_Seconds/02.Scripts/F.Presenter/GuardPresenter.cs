using UnityEngine;
using Position = System.Numerics.Vector3;

[RequireComponent(typeof(GuardMotor), typeof(GuardSight), typeof(SwapTarget))]
public sealed class GuardPresenter : MonoBehaviour
{
    [SerializeField] private GuardSettings settings;
    [Tooltip("처음 배식 위치 기준, 두 번째 순찰 지점의 로컬 오프셋(m)")]
    [SerializeField] private Vector3 patrolOffset;
    [SerializeField] private Animator animator;
    [SerializeField] private GuardSightView sightView;
    private static readonly int Speed = Animator.StringToHash("Speed");
    private readonly GuardBrain brain = new GuardBrain();
    private GuardMotor motor;
    private GuardSight sight;
    private SwapTarget swap;
    private PlayerMotor player;
    private CharacterController playerBody, guardBody;
    private Vector3 home, patrolEnd;
    private float elapsed;
    public GuardState State => brain.State;
    public bool IsChasing => State == GuardState.Chase;
    public bool RedAlert => IsChasing || State == GuardState.Search;
    public bool HasSight { get; private set; }
    public Vector3 AlertAnchor => sight.EyePosition(settings) + Vector3.up * .35f;
    public float Recognition => brain.Recognition;
    public Vector3 LastSeen => new Vector3(brain.LastSeen.X, brain.LastSeen.Y, brain.LastSeen.Z);
    public double ObservedAt => brain.ObservedAt;
    public bool CapturePending => brain.CapturePending;
    public bool Captured { get; private set; }

    private void Awake()
    {
        motor = GetComponent<GuardMotor>();
        sight = GetComponent<GuardSight>();
        swap = GetComponent<SwapTarget>();
        guardBody = GetComponent<CharacterController>();
        home = transform.position;
        patrolEnd = transform.TransformPoint(patrolOffset);
    }
    private void OnEnable() => swap.Relocated += OnRelocated;
    private void OnDisable()
    {
        swap.Relocated -= OnRelocated;
        if (sightView) sightView.Hide();
    }
    private void OnRelocated()
    {
        motor.ClearRoute();
        brain.CancelCapture();
    }

    public void BindPlayer(PlayerMotor target)
    {
        player = target;
        if (player) playerBody = player.GetComponent<CharacterController>();
        if (!settings || !playerBody)
        {
            Debug.LogError("경비에게 이동 설정과 씬의 플레이어가 필요합니다.", this);
            enabled = false;
        }
    }

    private void FixedUpdate()
    {
        if (!playerBody || Captured) return;
        float dt = Time.fixedDeltaTime;
        elapsed += dt;
        if (elapsed + .000001f >= settings.decisionInterval)
        {
            float step = elapsed;
            elapsed = 0f;
            float exposure = sight.Exposure(playerBody, settings);
            HasSight = exposure > 0f;
            Position? observation = null;
            if (exposure > 0f)
            {
                var b = playerBody.bounds;
                observation = new Position(b.center.x, b.min.y, b.center.z);
            }
            float identify = player && player.IsCrouching ? settings.identifyCrouching : settings.identifyStanding;
            brain.Tick(Time.fixedTimeAsDouble, step, observation, exposure / identify,
                1f / settings.forgetExposure, motor.Arrived, motor.Exhausted, settings.patrolWait, settings.searchTime);
            if (sightView) sightView.Draw(sight, settings, playerBody, RedAlert, Recognition);
            if (State == GuardState.Search) motor.ClearRoute();
            else
            {
                Vector3 goal = State == GuardState.Chase ? LastSeen :
                    State == GuardState.Patrol && brain.PatrolIndex == 1 ? patrolEnd : home;
                motor.Seek(goal, settings, State == GuardState.Return || exposure > 0f);
            }
        }
        motor.Move(settings, State == GuardState.Chase ? settings.chaseSpeed : settings.patrolSpeed,
            State == GuardState.Search, dt);
        if (animator) animator.SetFloat(Speed, motor.GroundSpeed, .12f, dt);
    }

    // Update에서 성립한 교환은 먼저 예고를 지운다. 새 자리에서 다시 닿으면 처음부터 센다.
    private void LateUpdate()
    {
        if (!playerBody || Captured || Time.timeScale == 0f) return;
        bool inReach = State == GuardState.Chase && sight.CanReach(guardBody, playerBody, settings);
        Captured = brain.CheckCapture(inReach, Time.timeAsDouble, settings.captureWarningTime);
    }
}
