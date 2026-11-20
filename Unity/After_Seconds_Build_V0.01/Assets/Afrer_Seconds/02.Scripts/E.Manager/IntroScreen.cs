using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.SceneManagement;
using UnityEngine.Video;

#region 의사코드
// 시작 입력을 받으면 영상 슬롯을 확인한다. 영상이 있으면 준비 완료 후 재생하고 건너뛰기 안내를 띄운다.
// 슬롯이 비거나 재생이 끝나거나 오류·건너뛰기 입력이 오면 Loading 씬을 한 번만 연다.
#endregion

// 타이틀에서 시작 → 선택한 인트로 재생 → 로딩 씬. 영상 준비 중에도 건너뛸 수 있다.
public sealed class IntroScreen : MonoBehaviour
{
    [SerializeField] private GameObject titleContent;
    [SerializeField] private GameObject skipHint;
    [SerializeField] private VideoPlayer introVideo;
    private bool showingIntro, leaving;

    private void OnEnable()
    {
        introVideo.prepareCompleted += PlayIntro;
        introVideo.loopPointReached += OnVideoEnded;
        introVideo.errorReceived += OnVideoError;
    }

    private void OnDisable()
    {
        introVideo.prepareCompleted -= PlayIntro;
        introVideo.loopPointReached -= OnVideoEnded;
        introVideo.errorReceived -= OnVideoError;
    }

    private void Update()
    {
        var keyboard = Keyboard.current;
        var mouse = Mouse.current;
        if ((keyboard != null && (keyboard.enterKey.wasPressedThisFrame || keyboard.numpadEnterKey.wasPressedThisFrame)) ||
            (mouse != null && mouse.leftButton.wasPressedThisFrame))
            Advance();
    }

    public void Advance()
    {
        if (leaving) return;
        if (!showingIntro && introVideo.clip)
        {
            showingIntro = true;
            titleContent.SetActive(false);
            skipHint.SetActive(true);
            introVideo.Prepare();
            return;
        }
        BeginLoading();
    }

    private void PlayIntro(VideoPlayer video)
    {
        if (showingIntro && !leaving) video.Play();
    }

    private void OnVideoEnded(VideoPlayer video) => BeginLoading();

    private void OnVideoError(VideoPlayer video, string message)
    {
        Debug.LogWarning("인트로 영상을 재생할 수 없어 게임을 시작합니다. " + message, this);
        BeginLoading();
    }

    private void BeginLoading()
    {
        if (leaving) return;
        leaving = true;
        SceneManager.LoadSceneAsync(LoadingScreen.ScenePath, LoadSceneMode.Single);
    }
}
