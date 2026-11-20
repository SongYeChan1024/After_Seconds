using UnityEngine;
using UnityEngine.SceneManagement;

#region 의사코드
// 실험체는 자기 자리에서 주변을 살핀다. 근처에서 투척 충돌이나 사격이 들리면 잠시 소리가 난 쪽을 바라본다.
// 실험체는 경비의 신고 체계에 참여하지 않는다.
#endregion
public sealed class SubjectPresence : MonoBehaviour
{
    [SerializeField] private Transform head;
    [SerializeField, Range(0f, 1f)] private float idlePhase;
    private Quaternion resting;
    private float yaw, heardYaw, listenUntil;

    private void Awake()
    {
        if (head) resting = head.localRotation;
    }

    private void OnEnable() => StealthNoise.Emitted += Listen;
    private void OnDisable()
    {
        StealthNoise.Emitted -= Listen;
        if (head) head.localRotation = resting;
        yaw = listenUntil = 0f;
    }

    private void Listen(Vector3 position, float radius, GuardNoise kind)
    {
        if (SceneManager.GetActiveScene() != gameObject.scene || kind == GuardNoise.Footstep) return;
        Vector3 direction = position - transform.position;
        float range = Mathf.Min(9f, radius);
        if (direction.sqrMagnitude > range * range) return;
        heardYaw = Mathf.Clamp(Vector3.SignedAngle(transform.forward,
            Vector3.ProjectOnPlane(direction, Vector3.up), Vector3.up), -32f, 32f);
        listenUntil = Time.time + 2.4f;
    }

    private void Update()
    {
        if (!head || Time.deltaTime <= 0f) return;
        float phase = Time.time * .55f + idlePhase * Mathf.PI * 2f;
        float target = Time.time < listenUntil ? heardYaw : Mathf.Sin(phase) * 6f;
        yaw = Mathf.MoveTowards(yaw, target, 34f * Time.deltaTime);
        var localUp = head.parent.InverseTransformDirection(transform.up);
        head.localRotation = Quaternion.AngleAxis(yaw, localUp) * resting;
    }
}

