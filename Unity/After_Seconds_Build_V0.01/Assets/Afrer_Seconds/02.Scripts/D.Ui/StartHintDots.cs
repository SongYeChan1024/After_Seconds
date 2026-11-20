using TMPro;
using UnityEngine;

// 의사코드: 타이틀이 켜지면 점 하나부터 시작하고 실제 경과 시간에 따라 세 문구를 반복한다.
[RequireComponent(typeof(TextMeshProUGUI))]
public sealed class StartHintDots : MonoBehaviour
{
    [Tooltip("점 앞에 붙일 문구. 비워 두면 점만 표시한다.")]
    [SerializeField] private string prefix = "Click To Start";
    [Tooltip("점 개수가 바뀌는 간격(초)")]
    [SerializeField, Min(.05f)] private float interval = .4f;
    private readonly string[] frames = new string[3];
    private TMP_Text label;
    private double nextChange;
    private int frame;

    private void OnEnable()
    {
        label = GetComponent<TMP_Text>();
        for (int i = 0; i < frames.Length; i++) frames[i] = prefix + new string('.', i + 1);
        nextChange = Time.realtimeSinceStartupAsDouble + Mathf.Max(.05f, interval);
        frame = 0;
        label.text = frames[0];
    }

    private void Update()
    {
        double now = Time.realtimeSinceStartupAsDouble;
        if (now < nextChange) return;
        nextChange = now + Mathf.Max(.05f, interval);
        frame = (frame + 1) % frames.Length;
        label.text = frames[frame];
    }
}
