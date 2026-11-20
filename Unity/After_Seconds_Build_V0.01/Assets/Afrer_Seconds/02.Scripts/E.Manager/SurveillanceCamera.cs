using UnityEngine;

// 렌즈와 같은 방향에서 노출을 누적한다. 한 번 확인한 목격의 좌표와 시각만 관제에 보낸다.
// 관제 담당이 발신 전 자리를 비우면 대기 보고를 버린다. 발신 뒤에는 수신 경비의 조사까지 전달한다.
public sealed class SurveillanceCamera : MonoBehaviour
{
    [SerializeField] private Transform pan, head;
    [SerializeField] private GuardSight optics;
    [SerializeField] private GuardSettings sightSettings;
    [SerializeField] private Renderer statusLamp;
    [SerializeField] private string controlDome = "C02";
    [SerializeField, Min(.1f)] private float identifySeconds = 1.3f, uplinkSeconds = .55f, reviewSeconds = 1.5f, radioSeconds = .35f;
    [SerializeField, Range(1f, 85f)] private float scanArc = 32f;
    [SerializeField, Min(1f)] private float turnSpeed = 48f;
    private enum Relay { Idle, Uplink, Review, Sent }
    private Relay relay;
    private CharacterController player;
    private FloorSecurity floor;
    private GuardPresenter operatorAtConfirmation, lastOperator;
    private Quaternion panRest, headRest;
    private float yaw, pitch, scanPhase, exposure, lostAt, deadline, nextSample, sampledAt;
    private bool identified, sentThisSighting;
    private Vector3 lastVisible, reportPoint;
    private float seenAt, reportAt;
    private MaterialPropertyBlock lampBlock;
    private int lampState = -1;

    public GuardPresenter OnDutyOperator => floor && FloorSecurity.Active == floor ? floor.SeatedOperator(controlDome) : null;

    public void Bind(FloorSecurity security, CharacterController target)
    {
        floor = security;
        player = target;
    }

    private void Awake()
    {
        panRest = pan.localRotation;
        headRest = head.localRotation;
        lampBlock = new MaterialPropertyBlock();
        SetLamp(0);
    }

    private void OnDisable()
    {
        relay = Relay.Idle;
        operatorAtConfirmation = lastOperator = null;
        exposure = 0f;
        identified = sentThisSighting = false;
        if (lampBlock != null) SetLamp(0);
    }

    private void Update()
    {
        if (!floor || FloorSecurity.Active != floor || !player || !player.enabled || Time.deltaTime <= 0f) return;
        float now = Time.time;
        Steer(now);
        if (now < nextSample) return;
        float dt = Mathf.Min(now - sampledAt, .2f);
        sampledAt = now;
        nextSample = now + .1f;
        GuardPresenter attendant = OnDutyOperator;
        if (relay == Relay.Uplink || relay == Relay.Review)
        {
            if (!attendant || attendant != operatorAtConfirmation) relay = Relay.Idle;
        }
        if (attendant && attendant != lastOperator && !sentThisSighting && relay != Relay.Sent)
        {
            exposure = 0f;
            identified = false;
        }
        lastOperator = attendant;
        float visible = optics.Exposure(player, sightSettings);
        if (visible > 0f)
        {
            Bounds bounds = player.bounds;
            lastVisible = new Vector3(bounds.center.x, bounds.min.y, bounds.center.z);
            seenAt = now;
            lostAt = now;
            exposure = Mathf.Min(1f, exposure + visible * dt / identifySeconds);
            if (exposure >= 1f) identified = true;
            if (identified && !sentThisSighting && attendant && relay == Relay.Idle)
            {
                operatorAtConfirmation = attendant;
                relay = Relay.Uplink;
                deadline = now + uplinkSeconds;
            }
        }
        else
        {
            exposure = Mathf.Max(0f, exposure - dt / .8f);
            if (now - lostAt >= 1.6f && relay == Relay.Idle)
                identified = sentThisSighting = false;
        }
        if (relay != Relay.Idle && now >= deadline)
        {
            switch (relay)
            {
                case Relay.Uplink:
                    relay = Relay.Review;
                    deadline = now + reviewSeconds;
                    break;
                case Relay.Review:
                    reportPoint = lastVisible;
                    reportAt = seenAt;
                    sentThisSighting = true;
                    relay = Relay.Sent;
                    deadline = now + radioSeconds;
                    break;
                case Relay.Sent:
                    floor.ReceiveCameraCall(operatorAtConfirmation, reportPoint, reportAt);
                    relay = Relay.Idle;
                    break;
            }
        }
        SetLamp(identified || relay != Relay.Idle ? 2 : exposure > 0f ? 1 : 0);
    }

    private void Steer(float now)
    {
        float targetYaw, targetPitch;
        if ((exposure > 0f || identified) && now - lostAt < 1.6f)
        {
            Vector3 aim = Quaternion.Inverse(pan.parent.rotation * panRest) *
                          (lastVisible + Vector3.up - head.position);
            targetYaw = Mathf.Clamp(Mathf.Atan2(aim.x, aim.z) * Mathf.Rad2Deg, -scanArc, scanArc);
            targetPitch = Mathf.Clamp(-Mathf.Atan2(aim.y, new Vector2(aim.x, aim.z).magnitude) * Mathf.Rad2Deg, -8f, 30f);
        }
        else
        {
            scanPhase += Time.deltaTime * .52f;
            targetYaw = Mathf.Sin(scanPhase) * scanArc;
            targetPitch = 12f;
        }
        yaw = Mathf.MoveTowards(yaw, targetYaw, turnSpeed * Time.deltaTime);
        pitch = Mathf.MoveTowards(pitch, targetPitch, turnSpeed * Time.deltaTime);
        pan.localRotation = panRest * Quaternion.Euler(0f, yaw, 0f);
        head.localRotation = headRest * Quaternion.Euler(pitch, 0f, 0f);
    }

    private void SetLamp(int state)
    {
        if (lampState == state) return;
        lampState = state;
        Color color = state == 0 ? new Color(.12f,.8f,.66f) : state == 1 ? new Color(1f,.72f,.1f) : new Color(1f,.09f,.035f);
        statusLamp.GetPropertyBlock(lampBlock);
        lampBlock.SetColor("_BaseColor", color);
        lampBlock.SetColor("_EmissionColor", color * 2f);
        statusLamp.SetPropertyBlock(lampBlock);
    }
}
