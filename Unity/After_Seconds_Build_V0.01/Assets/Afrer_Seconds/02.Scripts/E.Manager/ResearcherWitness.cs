using UnityEngine;
using UnityEngine.AI;

// 업무 중 머리·몸통이 보이는 시간을 누적한다. 도주 시작 때 한 번만 신고를 예약한다.
// 실제로 본 위협에서 먼 대피처를 골라 걸어서 이동한다. 막히면 다른 대피처를 구하고 신고 시각은 유지한다.
[RequireComponent(typeof(GuardMotor), typeof(GuardSight))]
public sealed class ResearcherWitness : MonoBehaviour
{
    [SerializeField] private GuardSettings settings;
    [SerializeField] private Animator animator;
    [SerializeField] private Vector3[] shelterPoints;
    [SerializeField, Min(.1f)] private float identifySeconds = 1.1f, runSpeed = 3.6f;
    private enum Activity { Work, Flee, Shelter }
    private Activity state;
    private GuardMotor motor;
    private GuardSight sight;
    private SceneFlow flow;
    private FloorSecurity floor;
    private CharacterController player;
    private NavMeshPath path;
    private int shelter = -1;
    private float exposure, nextLook, retryAt;
    private Vector3 threat;
    private static readonly int Speed = Animator.StringToHash("Speed");

    private void Awake()
    {
        path = new NavMeshPath();
        motor = GetComponent<GuardMotor>();
        sight = GetComponent<GuardSight>();
    }

    public void Bind(FloorSecurity security, SceneFlow owner, CharacterController target)
    {
        floor = security;
        flow = owner;
        player = target;
    }

    private void FixedUpdate()
    {
        if (!flow || FloorSecurity.Active != floor || !player || !player.enabled) return;
        float now = Time.fixedTime;
        if (now >= nextLook)
        {
            nextLook = now + .1f;
            float visible = sight.Exposure(player, settings);
            exposure = Mathf.Clamp01(exposure + (visible > 0f ? visible / identifySeconds : -1.5f) * .1f);
            if (visible > 0f && exposure >= 1f)
            {
                var bounds = player.bounds;
                threat = new Vector3(bounds.center.x, bounds.min.y, bounds.center.z);
                if (state == Activity.Work)
                {
                    flow.QueueResearchReport(floor, threat, now);
                    state = Activity.Flee;
                    ChooseShelter();
                }
                else
                {
                    flow.UpdateResearchObservation(floor, threat, now);
                    if (state == Activity.Shelter && now >= retryAt) ChooseShelter();
                }
            }
        }
        if (state != Activity.Flee) return;
        if (shelter >= 0)
        {
            motor.Seek(shelterPoints[shelter], settings, true);
            motor.Move(settings, runSpeed, false, Time.fixedDeltaTime);
            animator.SetFloat(Speed, motor.GroundSpeed, .12f, Time.fixedDeltaTime);
            if (motor.Arrived)
            {
                state = Activity.Shelter;
                animator.SetFloat(Speed, 0f);
                retryAt = now + 2f;
            }
        }
        if ((shelter < 0 || motor.Exhausted) && now >= retryAt) ChooseShelter();
    }

    private void ChooseShelter()
    {
        int selected = -1;
        float best = float.NegativeInfinity;
        for (int i = 0; i < shelterPoints.Length; i++)
        {
            var point = shelterPoints[i];
            if (i == shelter || !NavMesh.CalculatePath(transform.position, point, NavMesh.AllAreas, path) ||
                path.status != NavMeshPathStatus.PathComplete) continue;
            float distance = Vector3.Distance(point, threat);
            if (distance <= best) continue;
            best = distance;
            selected = i;
        }
        if (selected >= 0)
        {
            motor.ClearRoute();
            shelter = selected;
            state = Activity.Flee;
        }
        retryAt = Time.fixedTime + 2f;
    }
}
