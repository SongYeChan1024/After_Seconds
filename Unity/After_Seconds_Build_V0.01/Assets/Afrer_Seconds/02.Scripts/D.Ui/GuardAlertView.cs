using TMPro;
using UnityEngine;

#region 의사코드
// 직접 목격 중이면 화면 안에서는 머리 위 게이지, 화면 밖에서는 방향을 향한 호를 그린다.
// 뒤쪽의 좌우는 카메라의 수평 방향으로 구한다. 엄폐 뒤에는 발각된 경비의 남은 수색 시간만 알린다.
// 의심 시작과 첫 발각에서 클립을 한 번 재생한다. 카메라를 돌리거나 수색으로 바뀌어도 재생을 반복하지 않는다.
#endregion

[RequireComponent(typeof(AudioSource))]
public sealed class GuardAlertView : MonoBehaviour
{
    [SerializeField] private UnityEngine.UI.Image fill;
    [SerializeField] private TMP_Text label;
    [SerializeField] private GuardAlertArc edgeArc;
    [Tooltip("바르코 의심 알림. 플레이어를 처음 보기 시작할 때 한 번 재생한다.")]
    [SerializeField] private AudioClip noticeSound;
    [Tooltip("바르코 발각 알림. 식별을 마치고 추격을 시작할 때 한 번 재생한다.")]
    [SerializeField] private AudioClip spottedSound;
    private RectTransform panel, canvasRect;
    private UnityEngine.UI.Image background;
    private AudioSource speaker;
    private float nextNotice;
    private bool suspecting;
    private double lastIdentification = double.NegativeInfinity;

    private void Awake()
    {
        panel = (RectTransform)transform;
        canvasRect = (RectTransform)panel.parent;
        background = GetComponent<UnityEngine.UI.Image>();
        speaker = GetComponent<AudioSource>();
    }

    public void SetAlert(float amount, bool red, bool visible, Vector3 aboveHead, Camera view, double identifiedAt)
    {
        if (!gameObject.activeSelf) gameObject.SetActive(true);
        bool suspicion = visible && !red;
        if (red && visible && identifiedAt > lastIdentification && spottedSound)
            speaker.PlayOneShot(spottedSound);
        else if (suspicion && !suspecting && Time.time >= nextNotice && noticeSound)
        {
            speaker.PlayOneShot(noticeSound);
            nextNotice = Time.time + 1f;
        }
        suspecting = suspicion;
        if (red && identifiedAt > lastIdentification) lastIdentification = identifiedAt;

        Vector2 half = canvasRect.rect.size * .5f;
        Vector2 center = new Vector2(0f, half.y - 70f - panel.rect.height * .5f);
        Vector2 edge = Vector2.zero;
        if (visible && view)
        {
            Vector3 vp = view.WorldToViewportPoint(aboveHead);
            Vector2 offset = new Vector2(vp.x * 2f - 1f, vp.y * 2f - 1f);
            if (vp.z >= view.nearClipPlane && Mathf.Abs(offset.x) <= 1f && Mathf.Abs(offset.y) <= 1f)
            {
                Vector2 limit = Vector2.Max(Vector2.zero, half - panel.rect.size * .5f - Vector2.one * 8f);
                center = Vector2.Min(limit, Vector2.Max(-limit, Vector2.Scale(offset, half)));
            }
            else
            {
                edge = EdgeDirection(view, aboveHead, offset, vp.z);
                // 타원 위에 놓으면 대각선 표시가 화면 모서리의 소지품 안내를 가리지 않는다.
                Vector2 padding = new Vector2(12f, Mathf.Max(24f, half.y * .10f));
                Vector2 limit = Vector2.Max(Vector2.one, half - edgeArc.rectTransform.rect.size * .5f - padding);
                center = Vector2.Scale(limit, edge);
                edgeArc.rectTransform.localRotation = Quaternion.Euler(0f, 0f, Vector2.SignedAngle(Vector2.up, center));
            }
        }
        // 패널의 앵커와 피벗이 모두 상단 중앙이다.
        panel.anchoredPosition = center + Vector2.up * (panel.rect.height * .5f - half.y);

        bool onEdge = edge != Vector2.zero;
        Color32 tint = red ? new Color32(255, 82, 76, 255) : new Color32(255, 206, 65, 255);
        background.enabled = !onEdge;
        if (fill.transform.parent.gameObject.activeSelf == onEdge) fill.transform.parent.gameObject.SetActive(!onEdge);
        edgeArc.enabled = onEdge;
        if (onEdge)
        {
            edgeArc.color = tint;
            edgeArc.SetAmount(amount);
        }
        else
        {
            fill.color = tint;
            Vector2 fillEnd = new Vector2(Mathf.Clamp01(amount), 1f);
            if (fill.rectTransform.anchorMax != fillEnd) fill.rectTransform.anchorMax = fillEnd;
        }
        label.enabled = !onEdge || red;
        label.color = tint;
        label.text = onEdge ? "!" : red ? (visible ? "!  발각 · 추격 중" : "수색 중") : "경계 중";
    }

    private static Vector2 EdgeDirection(Camera view, Vector3 target, Vector2 projected, float depth)
    {
        Vector3 delta = target - view.transform.position;
        Vector3 right = Vector3.ProjectOnPlane(view.transform.right, Vector3.up).normalized;
        float side = Vector3.Dot(delta, right);
        float forward = Vector3.Dot(delta, Vector3.Cross(right, Vector3.up));
        if (forward < 0f) return new Vector2(side, forward).normalized;
        if (depth > view.nearClipPlane && projected.sqrMagnitude > .0001f) return projected.normalized;
        Vector2 local = new Vector2(side, Vector3.Dot(delta, view.transform.up));
        return local.sqrMagnitude > .0001f ? local.normalized : Vector2.down;
    }

    public void Hide()
    {
        if (gameObject.activeSelf) gameObject.SetActive(false);
        suspecting = false;
        lastIdentification = double.NegativeInfinity;
    }
}
