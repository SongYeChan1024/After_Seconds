using UnityEngine;
using UnityEngine.SceneManagement;

// 이 Transform은 층 시작 시 플레이어 루트의 위치와 방향을 나타낸다.
public sealed class FloorEntry : MonoBehaviour
{
    [Tooltip("미리 준비할 인접 층의 출구. 빌드에서는 계단에 접근할 때, 에디터에서는 시작 로딩 중에 준비한다.")]
    [SerializeField] private FloorPassage preloadExit;
    [Tooltip("선로딩을 시작할 계단 코어의 수평 반경과 계단참까지의 높이 차이(m)")]
    [SerializeField] private Vector2 preloadRange = new Vector2(8f, 19f);
    public string PreloadPath => preloadExit && preloadExit.isActiveAndEnabled ? preloadExit.DestinationPath : null;

    private GuardPresenter[] guards = System.Array.Empty<GuardPresenter>();
    private FloorPassage[] passages;

    private void Awake() => passages = GetComponentsInChildren<FloorPassage>();

    private void Start()
    {
        // 레벨 디자이너가 B5만 열고 재생할 때도 빌드와 같은 공통 씬을 사용한다.
        if (!SceneManager.GetSceneByPath(SceneFlow.RootPath).isLoaded)
            SceneManager.LoadSceneAsync(SceneFlow.RootPath, LoadSceneMode.Additive);
    }

    public void BindPlayer(PlayerMotor player)
    {
        var placed = new System.Collections.Generic.List<GuardPresenter>();
        foreach (var root in gameObject.scene.GetRootGameObjects())
            placed.AddRange(root.GetComponentsInChildren<GuardPresenter>(true));
        guards = placed.ToArray();
        foreach (var guard in guards) guard.BindPlayer(player);
    }

    public bool NearPreloadExit(Vector3 feet)
    {
        if (!preloadExit || !preloadExit.isActiveAndEnabled || !preloadExit.IsExit) return false;
        var offset = feet - preloadExit.transform.position;
        return Mathf.Abs(offset.y) <= preloadRange.y &&
               offset.x * offset.x + offset.z * offset.z <= preloadRange.x * preloadRange.x;
    }

    public FloorPassage ExitAt(Vector3 feet, float tolerance)
    {
        foreach (var passage in passages)
            if (passage.ContainsFeet(feet, tolerance)) return passage;
        return null;
    }

    public FloorPassage ArrivalAt(FloorCore core)
    {
        foreach (var passage in passages)
            if (!passage.IsExit && passage.Core == core && passage.isActiveAndEnabled) return passage;
        return null;
    }

    public bool ReadEncounter(out bool warning, out GuardPresenter alert)
    {
        warning = false;
        alert = null;
        foreach (var guard in guards)
        {
            if (!guard || !guard.isActiveAndEnabled) continue;
            if (guard.Captured) return true;
            warning |= guard.CapturePending;
            if (guard.Recognition <= 0f) continue;
            if (!alert || (guard.RedAlert && !alert.RedAlert) ||
                (guard.RedAlert == alert.RedAlert && guard.Recognition > alert.Recognition))
                alert = guard;
        }
        return false;
    }
}
