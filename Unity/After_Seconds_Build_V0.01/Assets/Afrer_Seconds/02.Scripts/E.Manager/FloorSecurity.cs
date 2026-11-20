using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;

#region 의사코드
// 근무 시작과 증원 때 경로에 맞는 보조 장비를 지급한다. 두 근무자가 인계점에서 만나면 경로와 장비를 함께 교환한다.
// 소음을 들으면 한 명이 원점을 확인한다. 확인 신고에는 현장 한 명과 자기 경로의 길목 한 명만 배정한다.
// 같은 사건을 다시 들어도 기존 대응을 이어 가고, 빈 역할이 없는 예비 근무자는 자기 경로를 순찰한다.
// 독립된 확인 보고 두 건이면 시설 경보를 발령한다. A2와 A3에 예비 근무자를 한 명씩 배치한다.
// 증원은 플레이어에게 보이지 않는 정해진 근무지에서만 합류한다. 같은 동료와 보고는 중복 집계하지 않는다.
#endregion
public sealed class FloorSecurity : MonoBehaviour
{
    [System.Serializable]
    public sealed class PatrolRoute
    {
        public Vector3[] points;
        public ItemDefinition dutyItem;
        [Tooltip("이 경로에 합류하는 예비조의 전용 장비. 비어 있으면 정규 근무 장비를 사용한다.")]
        public ItemDefinition reserveDutyItem;
        public ItemDefinition ReserveGear => reserveDutyItem ? reserveDutyItem : dutyItem;
    }
    [SerializeField] private DomePatrolPlan domePlan;
    [SerializeField] private SurveillanceCamera surveillance;
    [SerializeField] private ResearcherWitness researcher;
    private B5MealOpening opening;
    private NavMeshPath responsePath;
    private void Awake() => responsePath = new NavMeshPath();
    private float lastReportAt = float.NegativeInfinity;
    private bool cameraCallWaiting;
    private GuardPresenter callingOperator;
    private Vector3 cameraEvidence;
    private float cameraEvidenceAt;
    [SerializeField] private GuardPresenter[] staff;
    private readonly List<GuardPresenter> roster = new();
    private readonly List<DomeShift> shifts = new();
    private readonly float[] stairAvailable = new float[2];
    private int nextDome;
    public IReadOnlyList<GuardPresenter> Roster => roster;
    public IReadOnlyList<DomeShift> Shifts => shifts;
    [SerializeField] private PatrolRoute[] routes;
    [SerializeField] private Vector3[] handoverPosts;
    [SerializeField, Min(10f)] private float shiftSeconds = 65f;
    [SerializeField] private AudioSource radio;
    [SerializeField] private AudioClip notice, alarm;
    [SerializeField] private AudioSource[] worldSounds;
    [SerializeField] private AudioClip stepSound, impactSound, shotSound;
    private int voice;
    public static FloorSecurity Active { get; private set; }
    public int Level { get; private set; }
    public int CompletedShifts { get; private set; }
    public int Reports { get; private set; }
    private readonly HashSet<GuardPresenter> bodiesReported = new();
    private readonly HashSet<GuardPresenter> witnesses = new();
    private GuardDuty[] duties;
    private PlayerMotor player;
    private CharacterController playerBody;
    private Camera view;
    private FloorExperience encounter;
    private int deployed;
    private float nextTick, nextShift, meetingDeadline, lastEvidence, nextReserve, stride;
    private Vector3 lastFeet;
    private bool meeting, hasReport;
    private Vector3 reportedPoint;

    public void Bind(PlayerMotor actor, FloorExperience floorEncounter, bool facilityAlert, SceneFlow owner = null, B5MealOpening mealOpening = null)
    {
        opening = mealOpening;
        Active = this;
        StealthNoise.Emitted -= Hear;
        StealthNoise.Emitted += Hear;
        player = actor;
        encounter = floorEncounter;
        playerBody = actor.GetComponent<CharacterController>();
        view = Camera.main;
        if (surveillance) surveillance.Bind(this, playerBody);
        if (researcher) researcher.Bind(this, owner, playerBody);
        lastFeet = actor.transform.position;
        if (duties != null) return;
        duties = new GuardDuty[staff.Length];
        for (int i = 0; i < staff.Length; i++)
        {
            duties[i] = staff[i].GetComponent<GuardDuty>();
            int route = i % routes.Length;
            if (i < 2) Register(staff[i]);
            // 돔 근무표가 있으면 정규조 배정 또는 예비조 출동 전까지 자기 자리에서 대기한다.
            var initialRoute = domePlan ? new[] { staff[i].transform.position } : routes[route].points;
            duties[i].Assign(route, initialRoute, i < 2 ? 0 : 1);
            if (!domePlan && staff[i].isActiveAndEnabled) staff[i].GetComponent<GuardLoadout>().EquipDutyItem(routes[route].dutyItem);
        }
        deployed = 2;
        Level = facilityAlert ? 3 : 0;
        nextShift = Time.time + shiftSeconds;
        nextReserve = Time.time + 2f;
        if (domePlan)
        {
            // B5 시작 경비와 관제 경비의 기존 씬 참조·제압 가능 상태를 이어받는다.
            StartDome();
            StartDome();
        }
    }

    private void Register(GuardPresenter guard)
    {
        var collider = guard.GetComponent<CharacterController>();
        if (researcher) Physics.IgnoreCollision(collider, researcher.GetComponent<CharacterController>());
        foreach (var other in roster)
            if (other && other.gameObject.activeInHierarchy)
                Physics.IgnoreCollision(collider, other.GetComponent<CharacterController>());
        roster.Add(guard);
        guard.GetComponent<GuardDuty>().IntruderReported += ReceiveReport;
    }

    internal GuardPresenter SpawnGuard(string label, Vector3 feet, int role)
    {
        var actor = Instantiate(domePlan.guardPrefab, feet + Vector3.up * .035f, Quaternion.identity, transform);
        actor.name = label;
        if (!actor.TryGetComponent<GuardDuty>(out _)) actor.gameObject.AddComponent<GuardDuty>();
        actor.BindPlayer(player);
        Register(actor);
        actor.Equipment.EquipDutyItem(routes[role].dutyItem);
        return actor;
    }

    internal void SendHome(GuardPresenter actor)
    {
        if (!actor || actor.IsDown) return;
        actor.Duty.IntruderReported -= ReceiveReport;
        roster.Remove(actor);
        witnesses.Remove(actor);
        Destroy(actor.gameObject);
    }

    internal bool BookStair(int index)
    {
        if (Time.time < stairAvailable[index]) return false;
        stairAvailable[index] = Time.time + 3f;
        var stair = domePlan.stairs[index];
        if (encounter && !stair.fromBelow) encounter.AllowStaffPassage(stair.threshold[0]);
        return true;
    }

    internal void HandedOver() => CompletedShifts++;

    private void StartDome()
    {
        if (nextDome >= domePlan.domes.Length) return;
        var post = domePlan.domes[nextDome++];
        // B5 첫 근무조는 배식 경비와 실제 복도 순찰원을 그대로 이어 쓴다.
        bool mealPost = post.id == "C01" && opening && opening.Completed;
        var runner = mealPost ? SpawnGuard(post.id + "_Patrol", opening.CorridorPost, 1) :
            post.id == "C01" ? staff[0] : SpawnGuard(post.id + "_Patrol", post.meeting[0], 1);
        var watcher = mealPost ? opening.MealGuard :
            post.id == "C02" ? staff[1] : SpawnGuard(post.id + "_Watch", post.meeting[1], 0);
        runner.Equipment.EquipDutyItem(routes[1].dutyItem);
        watcher.Equipment.EquipDutyItem(routes[0].dutyItem);
        if (post.addChair && domePlan.dutyChair)
            Instantiate(domePlan.dutyChair, post.chairFeet, Quaternion.Euler(0f, post.watchYaw, 0f), transform);
        shifts.Add(new DomeShift(this, post, domePlan.stairs[post.stairIndex], runner, watcher));
        if (mealPost) opening.ReturnFromCorridor(runner, stepSound);
    }

    private void OnDisable() { StealthNoise.Emitted -= Hear; if (Active == this) Active = null; }
    private void ReceiveReport(GuardDuty duty, Vector3 point) => ReportIntruder(duty.GetComponent<GuardPresenter>(), point);

    private void Update()
    {
        if (Active != this || !playerBody || !playerBody.enabled || Time.timeScale == 0f) return;
        var here = player.transform.position;
        var delta = Vector3.ProjectOnPlane(here - lastFeet, Vector3.up).magnitude;
        lastFeet = here;
        if (delta < 1f && playerBody.isGrounded)
        {
            stride += delta;
            if (stride >= (player.IsCrouching ? 1.35f : 1.8f))
            {
                stride = 0f;
                float speed = Vector3.ProjectOnPlane(playerBody.velocity, Vector3.up).magnitude;
                if (speed > .15f) Hear(here + Vector3.up * .3f,
                    player.IsCrouching ? 2f : speed > 3.7f ? 12f : 5f, GuardNoise.Footstep);
            }
        }
        else stride = 0f;
        if (domePlan && nextDome < domePlan.domes.Length) StartDome();
        if (Time.time < nextTick) return;
        nextTick = Time.time + .35f;
        CheckBodies();
        if (cameraCallWaiting) TryAssignCameraCall();
        if (domePlan)
            foreach (var shift in shifts) shift.Tick();
        else CheckShift();
        if (Level == 1 && Time.time - lastEvidence > 16f) Level = 0;
        if (Level == 2 && Time.time - lastEvidence > 40f)
        {
            Level = 1;
            Reports = 0;
            witnesses.Clear();
            lastEvidence = Time.time;
        }
        if (Level >= 2 && deployed < Mathf.Min(staff.Length, Level + 1) && Time.time >= nextReserve)
        {
            nextReserve = Time.time + 1f;
            DeployReserve();
        }
    }

    public void Hear(Vector3 point, float radius, GuardNoise kind)
    {
        if (Active != this || duties == null) return;
        if (worldSounds.Length > 0)
        {
            var source = worldSounds[voice++ % worldSounds.Length];
            source.transform.position = point;
            source.maxDistance = radius;
            source.clip = kind == GuardNoise.Footstep ? stepSound : kind == GuardNoise.Impact ? impactSound : shotSound;
            source.volume = kind == GuardNoise.Footstep ? .3f : .65f;
            if (source.clip) source.Play();
        }
        if (kind == GuardNoise.Footstep && encounter && encounter.PumpMasks(point)) radius *= .30f;
        GuardPresenter listener = null;
        bool heard = false;
        float best = float.PositiveInfinity;
        for (int i = 0; i < roster.Count; i++)
        {
            var guard = roster[i];
            if (!guard || !guard.isActiveAndEnabled || guard.IsDown) continue;
            var ear = guard.EyePoint;
            float distance = Vector3.Distance(point, ear);
            if (distance > radius) continue;
            float cover = guard.SoundBlocked(point) ? .5f : 1f;
            if (distance > radius * cover) continue;
            heard = true;
            if (!CanRespond(guard) || distance >= best) continue;
            listener = guard;
            best = distance;
        }
        if (!heard) return;
        if (listener && !HasResponder(point, false)) listener.Duty.Investigate(point, 12f);
        lastEvidence = Time.time;
        if (Level == 0) { Level = 1; Play(notice); }
        if (kind == GuardNoise.Gunshot)
        {
            RememberReport(point, Time.time);
            if (Level < 2) { Level = 2; Play(alarm); }
        }
    }

    // 관제석의 현재 근무자만 보고를 발신한다. 호출은 마지막 목격 지점에 걸어서 닿는 가용 경비 한 명에게 전달한다.
    public GuardPresenter SeatedOperator(string dome)
    {
        foreach (var shift in shifts)
        {
            if (shift.Post.id != dome) continue;
            var guard = shift.Watcher;
            if (guard && guard.isActiveAndEnabled && !guard.IsDown && !guard.RedAlert &&
                !guard.HasSight && !guard.Duty.Investigating && guard.Duty.Seated) return guard;
            break;
        }
        return null;
    }

    public void ReceiveCameraCall(GuardPresenter sender, Vector3 point, float observedAt)
    {
        if (Active != this) return;
        RememberReport(point, observedAt);
        lastEvidence = Time.time;
        Level = Mathf.Max(2, Level);
        Play(notice);
        callingOperator = sender;
        cameraEvidence = point;
        cameraEvidenceAt = observedAt;
        cameraCallWaiting = true;
        TryAssignCameraCall();
    }

    private void TryAssignCameraCall()
    {
        // 전원이 다른 사건에 응답 중이면 같은 호출을 잠시 보관한다. 오래된 위치로 새 수색을 시작하지 않는다.
        if (Time.time - cameraEvidenceAt > 12f) { cameraCallWaiting = false; return; }
        GuardPresenter nearest = null;
        float best = float.PositiveInfinity;
        if (!NavMesh.SamplePosition(cameraEvidence, out var end, 2.5f, NavMesh.AllAreas)) return;
        foreach (var guard in roster)
        {
            if (!guard || guard == callingOperator || !guard.isActiveAndEnabled || guard.IsDown || guard.RedAlert ||
                guard.HasSight || !guard.Duty.AvailableForCall) continue;
            float distance = WalkingDistance(guard.transform.position, end.position);
            if (distance >= best) continue;
            best = distance;
            nearest = guard;
        }
        if (!nearest) return;
        nearest.Duty.Investigate(end.position, Mathf.Max(12f, best / nearest.Settings.patrolSpeed + 3f));
        cameraCallWaiting = false;
    }

    private void RememberReport(Vector3 point, float observedAt)
    {
        if (observedAt < lastReportAt) return;
        reportedPoint = point;
        lastReportAt = observedAt;
        hasReport = true;
    }

    public void RaiseResearchAlarm(bool sameFloor, Vector3 observed, float observedAt)
    {
        if (sameFloor) RememberReport(observed, observedAt);
        if (Level < 3) Play(alarm);
        Level = 3;
        lastEvidence = Time.time;
    }

    public void ReportIntruder(GuardPresenter source, Vector3 seen)
    {
        if (Active != this || !witnesses.Add(source)) return;
        Confirm(source, seen);
    }

    private void CheckBodies()
    {
        for (int j = 0; j < roster.Count; j++)
        {
            var fallen = roster[j];
            if (!fallen.IsDown || bodiesReported.Contains(fallen)) continue;
            for (int i = 0; i < roster.Count; i++)
            {
                var witness = roster[i];
                if (!witness.isActiveAndEnabled || !witness.SeesFallen(fallen)) continue;
                bodiesReported.Add(fallen);
                Confirm(witness, fallen.transform.position);
                break;
            }
        }
    }

    private void Confirm(GuardPresenter witness, Vector3 point)
    {
        lastEvidence = Time.time;
        RememberReport(point, Time.time);
        Reports++;
        int before = Level;
        Level = Mathf.Max(Level, Reports >= 2 ? 3 : 2);
        if (Level != before) Play(alarm);
        // 직접 발견한 경비가 현장을 맡는다. 이미 추격하거나 다른 근무자가 도착 중이면 중복 호출하지 않는다.
        if (!witness.RedAlert && !witness.HasSight && witness.Duty.RespondingTo(point, false))
            witness.Duty.Investigate(point, 16f);
        else if (!HasResponder(point, false))
        {
            var investigator = CanRespond(witness) ? witness : NearestResponder(point, false, out _);
            if (investigator) investigator.Duty.Investigate(point, 16f);
        }
        if (!HasResponder(point, true))
        {
            var support = NearestResponder(point, true, out var post);
            if (support) support.Duty.CheckAccess(point, post);
        }
    }

    private static bool CanRespond(GuardPresenter guard) => guard && guard.isActiveAndEnabled &&
        !guard.IsDown && !guard.RedAlert && !guard.HasSight && guard.Duty.AvailableForCall;

    private bool HasResponder(Vector3 point, bool access)
    {
        foreach (var guard in roster)
        {
            if (!guard || !guard.isActiveAndEnabled || guard.IsDown) continue;
            if (guard.Duty.RespondingTo(point, access)) return true;
            if (!access && guard.RedAlert && GuardDuty.SameIncident(guard.LastSeen, point)) return true;
        }
        return false;
    }

    private GuardPresenter NearestResponder(Vector3 point, bool access, out Vector3 post)
    {
        post = point;
        GuardPresenter nearest = null;
        float best = float.PositiveInfinity;
        foreach (var guard in roster)
        {
            if (!CanRespond(guard) || (guard.transform.position - point).sqrMagnitude > 32f * 32f) continue;
            var destination = point;
            if (access && !guard.Duty.TryAccessPoint(point, out destination)) continue;
            float distance = WalkingDistance(guard.transform.position, destination) + Vector3.Distance(destination, point);
            if (distance >= best) continue;
            best = distance;
            nearest = guard;
            post = destination;
        }
        return nearest;
    }

    private float WalkingDistance(Vector3 from, Vector3 to)
    {
        if (!NavMesh.SamplePosition(from, out var start, 1.5f, NavMesh.AllAreas) ||
            !NavMesh.SamplePosition(to, out var end, 2.5f, NavMesh.AllAreas) ||
            !NavMesh.CalculatePath(start.position, end.position, NavMesh.AllAreas, responsePath) ||
            responsePath.status != NavMeshPathStatus.PathComplete) return float.PositiveInfinity;
        var corners = responsePath.corners;
        float length = 0f;
        for (int i = 1; i < corners.Length; i++) length += Vector3.Distance(corners[i - 1], corners[i]);
        return length;
    }

    private void AssignReservePatrol(GuardDuty duty)
    {
        if (!domePlan) return;
        DomePost nearest = null;
        float best = float.PositiveInfinity;
        foreach (var post in domePlan.domes)
        {
            float distance = WalkingDistance(duty.transform.position, post.meeting[0]);
            if (distance >= best) continue;
            best = distance;
            nearest = post;
        }
        // 마지막 지점이 인계점이다. 예비 경비는 자기 돔에 합류한 뒤 첫 복도부터 반복 순찰한다.
        if (nearest != null) duty.Assign(duty.RouteIndex, nearest.circuit, nearest.circuit.Length - 1, nearest.Entrances, nearest.inspectionStops);
    }

    private void DeployReserve()
    {
        for (int i = deployed; i < staff.Length; i++)
        {
            var candidate = staff[i];
            var point = candidate.transform.position + Vector3.up;
            if (Vector3.Distance(point, player.transform.position) < 14f) continue;
            if (view)
            {
                var screen = view.WorldToViewportPoint(point);
                if (screen.z > 0 && screen.x > -.1f && screen.x < 1.1f && screen.y > -.1f && screen.y < 1.1f &&
                    !Physics.Linecast(view.transform.position, point, Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore)) continue;
            }
            (staff[i], staff[deployed]) = (staff[deployed], staff[i]);
            (duties[i], duties[deployed]) = (duties[deployed], duties[i]);
            candidate.gameObject.SetActive(true);
            candidate.GetComponent<GuardLoadout>().EquipDutyItem(routes[duties[deployed].RouteIndex].ReserveGear);
            candidate.BindPlayer(player);
            AssignReservePatrol(duties[deployed]);
            Register(candidate);
            if (hasReport && Time.time - lastReportAt < 26f &&
                (candidate.transform.position - reportedPoint).sqrMagnitude <= 32f * 32f && !HasResponder(reportedPoint, true))
                duties[deployed].CheckAccess(reportedPoint);
            deployed++;
            nextReserve = Time.time + 3f;
            return;
        }
    }

    private void CheckShift()
    {
        bool available = staff[0].isActiveAndEnabled && staff[1].isActiveAndEnabled &&
            !staff[0].HasSight && !staff[1].HasSight && !staff[0].RedAlert && !staff[1].RedAlert && !duties[0].Investigating && !duties[1].Investigating;
        if (meeting && (!available || Time.time > meetingDeadline))
        {
            duties[0].CancelMeeting(); duties[1].CancelMeeting();
            meeting = false;
            nextShift = Time.time + shiftSeconds;
        }
        if (!available) return;
        if (!meeting && Time.time >= nextShift)
        {
            meeting = true;
            meetingDeadline = Time.time + 110f;
            for (int i = 0; i < 2; i++) duties[i].MeetAt(handoverPosts[i]);
        }
        if (!meeting || !duties[0].AtHandover || !duties[1].AtHandover) return;
        int first = duties[0].RouteIndex, second = duties[1].RouteIndex;
        duties[0].Assign(second, routes[second].points, 1);
        duties[1].Assign(first, routes[first].points, 1);
        staff[0].GetComponent<GuardLoadout>().ExchangeDutyItems(staff[1].GetComponent<GuardLoadout>());
        CompletedShifts++;
        meeting = false;
        nextShift = Time.time + shiftSeconds;
    }

    private void OnDrawGizmosSelected()
    {
        if (domePlan)
        {
            foreach (var dome in domePlan.domes)
            {
                Gizmos.color = Color.yellow;
                foreach (var point in dome.circuit) Gizmos.DrawSphere(point + Vector3.up * .2f, .18f);
                Gizmos.color = Color.cyan;
                foreach (var point in dome.indoor) Gizmos.DrawWireSphere(point + Vector3.up * .2f, .35f);
                Gizmos.color = Color.white;
                foreach (var point in dome.meeting) Gizmos.DrawWireSphere(point, .45f);
            }
            return;
        }
        if (routes == null) return;
        for (int i = 0; i < routes.Length; i++)
        {
            var points = routes[i]?.points;
            if (points == null || points.Length == 0) continue;
            Gizmos.color = i == 0 ? Color.cyan : Color.yellow;
            for (int j = 0; j < points.Length; j++)
            {
                Gizmos.DrawSphere(points[j] + Vector3.up * .2f, .18f);
                Gizmos.DrawLine(points[j] + Vector3.up * .2f, points[(j + 1) % points.Length] + Vector3.up * .2f);
            }
        }
        Gizmos.color = Color.white;
        if (handoverPosts != null) foreach (var post in handoverPosts) Gizmos.DrawWireSphere(post, .6f);
    }

    private void Play(AudioClip clip) { if (radio && clip) radio.PlayOneShot(clip, .48f); }
}
