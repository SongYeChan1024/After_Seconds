using System.Collections;
using UnityEngine;

#region 의사코드
// 현 층에서 호출하면 빈 승강칸을 내려 보내고 도착한 승강장 문과 칸 문을 함께 연다.
// 승객이 칸 안에서 상행을 누르면 문을 닫고, 칸과 승객을 위층 높이까지 함께 옮긴다.
// 이동 거리만큼 균형추를 반대로 움직이고 로프 길이와 도르래의 각도를 갱신한다.
// 위층에서 도착 공간을 확보하지 못하면 승객과 함께 출발 층으로 내려와 문을 다시 연다.
#endregion

public sealed class FreightLift : MonoBehaviour
{
    [SerializeField] private Transform car, counterweight, sheave, carRope, weightRope;
    [SerializeField] private Transform carAttachment, weightAttachment;
    [SerializeField] private Transform[] carDoors, lowerDoors, upperDoors;
    [SerializeField] private Transform lowerStop, upperStop;
    [SerializeField] private bool terminal;
    [SerializeField, Min(.1f)] private float travelSeconds = 3.2f, doorSeconds = .65f;
    private const float ClosedX = .655f;
    private const float OpenX = 1.98f;
    private Vector3 weightAtTop;
    private Quaternion wheelAtTop;
    private SceneFlow flow;
    private bool open, busy;
    private float level;

    public bool UpwardOpen => flow && flow.CanAscend;
    public bool CanCall => !terminal && !busy && !open && flow && flow.CanUseLift;
    public bool CanBoard(PlayerInventory actor)
    {
        if (terminal || busy || !open || !flow || !flow.CanUseLift || !actor) return false;
        var foot = car.InverseTransformPoint(actor.Body.bounds.center);
        return Mathf.Abs(foot.x) < 1.35f && Mathf.Abs(foot.z) < 1.20f && foot.y >= 0f && foot.y < 1.9f;
    }

    private void Awake()
    {
        weightAtTop = counterweight.localPosition;
        wheelAtTop = sheave.localRotation;
        Place(1f);
        SetDoors(carDoors, terminal ? 1f : 0f);
        SetDoors(upperDoors, terminal ? 1f : 0f);
        SetDoors(lowerDoors, 0f);
    }

    public void Bind(SceneFlow owner) => flow = owner;

    public bool Call()
    {
        if (!CanCall) return false;
        StartCoroutine(CallCar());
        return true;
    }

    private IEnumerator CallCar()
    {
        busy = true;
        yield return MoveTo(0f, null);
        yield return SlideDoors(lowerDoors, true);
        open = true;
        busy = false;
    }

    public bool RequestRide(PlayerInventory actor) => CanBoard(actor) && flow.BoardLift(this, actor);

    public IEnumerator Ride(CharacterController passenger, bool ascending)
    {
        busy = true;
        open = false;
        if (ascending) yield return SlideDoors(lowerDoors, false);
        yield return MoveTo(ascending ? 1f : 0f, passenger);
        if (!ascending) yield return SlideDoors(lowerDoors, true);
        open = !ascending;
        busy = false;
    }

    // 도착 씬의 칸을 먼저 맞춘 뒤 SceneFlow가 발판과 머리 공간을 검사한다.
    public void Receive()
    {
        Place(terminal ? 1f : 0f);
        SetDoors(terminal ? upperDoors : lowerDoors, 0f);
        SetDoors(carDoors, 0f);
        open = false;
    }

    public IEnumerator OpenAtArrival()
    {
        busy = true;
        yield return SlideDoors(terminal ? upperDoors : lowerDoors, true);
        open = true;
        busy = false;
    }

    private IEnumerator MoveTo(float destination, CharacterController rider)
    {
        float from = level;
        Vector3 localRider = rider ? car.InverseTransformPoint(rider.transform.position) : Vector3.zero;
        float elapsed = 0f;
        while (elapsed < travelSeconds)
        {
            elapsed += Time.deltaTime;
            Place(Mathf.SmoothStep(from, destination, elapsed / travelSeconds));
            if (rider) rider.transform.position = car.TransformPoint(localRider);
            yield return null;
        }
    }

    private void Place(float t)
    {
        level = t;
        Vector3 position = Vector3.Lerp(lowerStop.localPosition, upperStop.localPosition, t);
        float drop = upperStop.localPosition.y - position.y;
        car.localPosition = position;
        counterweight.localPosition = weightAtTop + Vector3.up * drop;
        sheave.localRotation = wheelAtTop * Quaternion.AngleAxis(-drop / 1.2f * Mathf.Rad2Deg, Vector3.forward);
        SetRope(carRope, carAttachment);
        SetRope(weightRope, weightAttachment);
    }

    private static void SetRope(Transform rope, Transform attachment)
    {
        Vector3 scale = rope.localScale;
        scale.y = Mathf.Max(.01f, rope.localPosition.y - rope.parent.InverseTransformPoint(attachment.position).y);
        rope.localScale = scale;
    }

    private IEnumerator SlideDoors(Transform[] landing, bool opening)
    {
        float elapsed = 0f;
        while (elapsed < doorSeconds)
        {
            elapsed += Time.deltaTime;
            float fraction = Mathf.SmoothStep(opening ? 0f : 1f, opening ? 1f : 0f, elapsed / doorSeconds);
            SetDoors(carDoors, fraction);
            SetDoors(landing, fraction);
            yield return null;
        }
    }

    private static void SetDoors(Transform[] pair, float fraction)
    {
        float x = Mathf.Lerp(ClosedX, OpenX, fraction);
        for (int i = 0; i < pair.Length; i++)
        {
            Vector3 p = pair[i].localPosition;
            p.x = i == 0 ? -x : x;
            pair[i].localPosition = p;
        }
    }
}
