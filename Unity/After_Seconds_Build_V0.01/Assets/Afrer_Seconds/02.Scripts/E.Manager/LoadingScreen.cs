using System.Collections;
using UnityEngine;
using UnityEngine.SceneManagement;

#region 의사코드
// Loading만 열린 상태에서 시작하면 공통 GameRoot를 추가로 연다.
// 요청에 따라 화면을 켜거나 숨긴다. 화면이 보이는 동안 실제 경과 시간으로 활동 막대를 왕복시킨다.
#endregion

// 첫 진입에서는 GameRoot를 불러온다. 이후 같은 화면을 층 이동과 재시도에 다시 쓴다.
public sealed class LoadingScreen : MonoBehaviour
{
    public const string ScenePath = "Assets/Afrer_Seconds/01.Scenes/Loading.unity";
    [SerializeField] private GameObject presentation;
    [SerializeField] private RectTransform activity;
    [SerializeField] private CanvasGroup blackout;
    [SerializeField, Min(0f)] private float fadeToBlack = .16f, revealScene = .52f;
    private float shownAt;

    // 실제 시간으로 로딩 그림을 암전한 뒤, 검은 막 아래에서 게임 카메라로 전환하고 장면을 밝힌다.
    public IEnumerator Reveal()
    {
        if (!blackout) { SetVisible(false); yield break; }
        blackout.gameObject.SetActive(true);
        yield return Fade(0f, 1f, fadeToBlack);
        presentation.SetActive(false);
        yield return Fade(1f, 0f, revealScene);
        blackout.gameObject.SetActive(false);
    }

    private IEnumerator Fade(float from, float to, float seconds)
    {
        blackout.alpha = from;
        // 로드 직후 긴 한 프레임이 보간 전체를 건너뛰지 않게 실제로 그릴 프레임을 남긴다.
        float elapsed = 0f;
        while (elapsed < seconds)
        {
            yield return null;
            elapsed += Mathf.Min(Time.unscaledDeltaTime, .05f);
            blackout.alpha = Mathf.SmoothStep(from, to, elapsed / seconds);
        }
        blackout.alpha = to;
    }

    private void Start()
    {
        if (SceneManager.sceneCount == 1 && SceneManager.GetActiveScene() == gameObject.scene)
            SceneManager.LoadSceneAsync(SceneFlow.RootPath, LoadSceneMode.Additive);
    }

    public void SetVisible(bool visible)
    {
        if (visible) shownAt = Time.unscaledTime;
        if (blackout) blackout.gameObject.SetActive(false);
        presentation.SetActive(visible);
    }

    private void Update()
    {
        if (!presentation.activeSelf) return;
        float x = Mathf.PingPong((Time.unscaledTime - shownAt) * .50f, .78f);
        activity.anchorMin = new Vector2(x, 0f);
        activity.anchorMax = new Vector2(x + .22f, 1f);
    }
}
