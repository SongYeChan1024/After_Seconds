using TMPro;
using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(AudioSource))]
public sealed class GuardAlertView : MonoBehaviour
{
    [SerializeField] private Image fill;
    [SerializeField] private TMP_Text label;
    [SerializeField] private AudioClip noticeSound, spottedSound;
    private RectTransform panel, canvasRect;
    private AudioSource speaker;
    private float nextNotice, lastAmount = -1f;
    private bool lastRed, lastVisible;

    private void Awake()
    {
        panel = (RectTransform)transform;
        canvasRect = (RectTransform)panel.parent;
        speaker = GetComponent<AudioSource>();
    }

    public void SetAlert(float amount, bool red, bool visible, Vector3 aboveHead, Camera view)
    {
        if (!gameObject.activeSelf) gameObject.SetActive(true);
        if (red && !lastRed && spottedSound) speaker.PlayOneShot(spottedSound);
        else if (!red && lastAmount < 0f && Time.time >= nextNotice && noticeSound)
        {
            speaker.PlayOneShot(noticeSound);
            nextNotice = Time.time + 1f;
        }
        if (amount != lastAmount)
            fill.rectTransform.anchorMax = new Vector2(Mathf.Clamp01(amount), 1f);
        if (lastAmount < 0f || lastRed != red || lastVisible != visible)
        {
            Color32 color = red ? new Color32(255, 82, 76, 255) : new Color32(255, 206, 65, 255);
            fill.color = color;
            label.color = color;
            label.text = red ? (visible ? "!  발각 · 추격 중" : "!  수색 중") : "경계 중";
        }
        Position(visible && view, aboveHead, view);
        lastAmount = amount;
        lastRed = red;
        lastVisible = visible;
    }

    private void Position(bool showDirection, Vector3 target, Camera view)
    {
        // 시선이 끊기면 화면 위에서 남은 시간만 알린다. 엄폐물 너머 경비의 위치는 숨긴다.
        Vector2 size = canvasRect.rect.size;
        Vector2 half = size * .5f;
        Vector2 pos = new Vector2(0f, half.y - 70f);
        if (showDirection)
        {
            Vector3 viewport = view.WorldToViewportPoint(target);
            Vector2 offset = Vector2.Scale(new Vector2(viewport.x - .5f, viewport.y - .5f), size);
            if (viewport.z <= 0f)
            {
                offset = -offset;
                if (offset.sqrMagnitude < .01f) offset = Vector2.down;
            }
            Vector2 limit = Vector2.Max(Vector2.one, half - panel.rect.size * .5f - Vector2.one * 8f);
            float ratio = Mathf.Max(Mathf.Abs(offset.x) / limit.x, Mathf.Abs(offset.y) / limit.y);
            if (ratio > 1f || viewport.z <= 0f) offset /= Mathf.Max(ratio, .0001f);
            pos = offset + Vector2.up * panel.rect.height * .5f;
        }
        // 패널의 기준점은 캔버스 맨 위 중앙, 피벗은 패널 맨 위 중앙이다.
        panel.anchoredPosition = pos - Vector2.up * half.y;
    }

    public void Hide()
    {
        if (gameObject.activeSelf) gameObject.SetActive(false);
        lastAmount = -1f;
        lastRed = false;
    }
}
