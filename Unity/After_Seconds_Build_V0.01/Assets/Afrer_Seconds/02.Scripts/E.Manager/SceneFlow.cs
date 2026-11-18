using System.Collections;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.SceneManagement;

// 공통 씬은 플레이어·카메라·화면을 소유한다. 계단은 목적 층과 같은 코어를 지정한다.
[DefaultExecutionOrder(400)]
public sealed class SceneFlow : MonoBehaviour
{
    
    public const string RootPath = "Assets/Afrer_Seconds/01.Scenes/GameRoot.unity";
    [SerializeField] private string startingFloorPath;
    [SerializeField] private GameObject playerRigPrefab;
    [SerializeField] private GameObject loadingScreen;
    [SerializeField] private GuardAlertView guardAlert;
    private GameObject rig;
    private PlayerPresenter presenter;
    private PlayerInput input;
    private PlayerMotor player;
    private CharacterController body;
    private Camera playerCamera;
    private PlayerInventoryView hud;
    private FloorEntry entry;
    private FloorPassage lastExit;
    private bool loading, caught, clockPaused, exitFailed;
    private float resumeScale;
    private Scene stagedFloor;
    private readonly System.Collections.Generic.List<GameObject> stagedRoots = new();
    private string stagingPath;
    private AsyncOperation preloadOperation;

    private IEnumerator Start()
    {
        // 층 씬을 직접 재생하거나 GameRoot와 함께 열어 둔 경우 그 층을 그대로 사용한다.
        var active = SceneManager.GetActiveScene();
        var loaded = FindEntry(active);
        for (int i = 0; !loaded && i < SceneManager.sceneCount; i++)
            loaded = FindEntry(SceneManager.GetSceneAt(i));
        yield return StartAttempt(loaded ? loaded.gameObject.scene.path : startingFloorPath);
    }

    private static FloorEntry FindEntry(Scene scene)
    {
        if (!scene.isLoaded) return null;
        foreach (var root in scene.GetRootGameObjects())
            if (root.TryGetComponent<FloorEntry>(out var found)) return found;
        return null;
    }

    private static IEnumerator LoadIfNeeded(string path)
    {
        if (!SceneManager.GetSceneByPath(path).isLoaded && SceneUtility.GetBuildIndexByScenePath(path) >= 0)
            yield return SceneManager.LoadSceneAsync(path, LoadSceneMode.Additive);
    }

    private IEnumerator StartAttempt(string path)
    {
        ShowLoading(true);
        yield return null;
        yield return LoadIfNeeded(path);
        var floor = SceneManager.GetSceneByPath(path);
        entry = FindEntry(floor);
        if (!entry || !playerRigPrefab)
        {
            Debug.LogError("시작 층의 빌드 등록·FloorEntry와 GameRoot의 플레이어 프리팹을 확인해 주세요.", this);
            ShowLoading(false);
            yield break;
        }
        SceneManager.SetActiveScene(floor);
        yield return PrepareAtEntry(entry.PreloadPath);
        rig = Instantiate(playerRigPrefab, entry.transform.position, entry.transform.rotation, transform);
        player = rig.GetComponentInChildren<PlayerMotor>();
        presenter = player.GetComponent<PlayerPresenter>();
        input = player.GetComponent<PlayerInput>();
        body = player.GetComponent<CharacterController>();
        playerCamera = rig.GetComponentInChildren<Camera>();
        hud = rig.GetComponentInChildren<PlayerInventoryView>();
        entry.BindPlayer(player);
        lastExit = null;
        exitFailed = false;
        ShowLoading(false);
    }

    private IEnumerator PrepareAtEntry(string path)
    {
        if (preloadOperation != null) yield return preloadOperation;
        if (stagedFloor.IsValid() && stagedFloor.isLoaded && stagedFloor.path != path)
        {
            yield return SceneManager.UnloadSceneAsync(stagedFloor);
            ClearStagedFloor();
        }
#if UNITY_EDITOR
        // 에디터의 텍스트 씬 역직렬화는 몇 초간 프레임을 막는다. 시작 화면에서만 앞당긴다.
        BeginPreload(path);
        if (preloadOperation != null) yield return preloadOperation;
#endif
    }

    private void BeginPreload(string path)
    {
        if (stagedFloor.IsValid() || preloadOperation != null || string.IsNullOrEmpty(path) ||
            SceneManager.GetSceneByPath(path).isLoaded || SceneUtility.GetBuildIndexByScenePath(path) < 0)
            return;

        stagingPath = path;
        SceneManager.sceneLoaded += ParkLoadedFloor;
        preloadOperation = SceneManager.LoadSceneAsync(path, LoadSceneMode.Additive);
        if (preloadOperation == null) EndPreload();
    }

    private void EndPreload()
    {
        SceneManager.sceneLoaded -= ParkLoadedFloor;
        stagingPath = null;
        preloadOperation = null;
    }

    private void ParkLoadedFloor(Scene scene, LoadSceneMode mode)
    {
        if (scene.path != stagingPath) return;
        stagedFloor = scene;
        // sceneLoaded는 Start와 첫 물리 스텝보다 먼저 온다. 원래 켜져 있던 루트만 복구한다.
        foreach (var root in scene.GetRootGameObjects())
        {
            if (!root.activeSelf) continue;
            stagedRoots.Add(root);
            root.SetActive(false);
        }
        EndPreload();
    }

    private void SetStagedRoots(bool active)
    {
        foreach (var root in stagedRoots)
            if (root) root.SetActive(active);
    }

    private void ClearStagedFloor()
    {
        stagedRoots.Clear();
        stagedFloor = default;
    }

    private void LateUpdate()
    {
        if (loading || !entry || !rig) return;
        if (caught)
        {
            var keys = Keyboard.current;
            if (keys != null && (keys.enterKey.wasPressedThisFrame || keys.numpadEnterKey.wasPressedThisFrame))
                Restart();
            return;
        }
        if (entry.ReadEncounter(out bool warning, out var alert))
        {
            if (guardAlert) guardAlert.Hide();
            caught = true;
            PauseClock();
            presenter.enabled = false;
            hud.EncounterPrompt = "붙잡혔다 · Enter로 다시 시작";
            return;
        }
        if (guardAlert)
        {
            if (alert) guardAlert.SetAlert(alert.Recognition, alert.RedAlert, alert.HasSight, alert.AlertAnchor, playerCamera);
            else guardAlert.Hide();
        }
        if (Time.timeScale == 0f) return;
        var feet = Feet();
        var exit = body.isGrounded ? entry.ExitAt(feet, body.skinWidth + .03f) : null;
        if (exit != lastExit)
        {
            lastExit = exit;
            exitFailed = false;
            if (exit)
            {
                StartCoroutine(Travel(exit, feet - exit.transform.position));
                return;
            }
        }
        if (!stagedFloor.IsValid() && preloadOperation == null && entry.NearPreloadExit(feet))
            BeginPreload(entry.PreloadPath);
        hud.EncounterPrompt = exitFailed ? "도착할 공간이 없다" : warning ? "경비의 손이 닿는다!" : null;
    }

    private Vector3 Feet()
    {
        var bounds = body.bounds;
        return new Vector3(bounds.center.x, bounds.min.y, bounds.center.z);
    }

    private IEnumerator Travel(FloorPassage exit, Vector3 offset)
    {
        var oldFloor = entry.gameObject.scene;
        string path = exit.DestinationPath;
        if (path == oldFloor.path || SceneUtility.GetBuildIndexByScenePath(path) < 0)
        {
            exitFailed = true;
            yield break;
        }
        ShowLoading(true);
        PauseClock();
        presenter.enabled = false;
        input.DeactivateInput();
        // 현재 프레임에 전환 화면을 그린 뒤 물리·렌더 오브젝트를 전환한다.
        yield return null;
        if (preloadOperation != null) yield return preloadOperation;
        bool prepared = stagedFloor.IsValid() && stagedFloor.isLoaded && stagedFloor.path == path;
        bool alreadyLoaded = SceneManager.GetSceneByPath(path).isLoaded;
        if (prepared) SetStagedRoots(true);
        else yield return LoadIfNeeded(path);
        var destination = SceneManager.GetSceneByPath(path);
        var next = FindEntry(destination);
        var arrival = next ? next.ArrivalAt(exit.Core) : null;
        Physics.SyncTransforms();
        if (arrival && arrival.TryPlaceFeet(offset, body, out var feet))
        {
            Vector3 shift = feet - Feet();
            body.enabled = false;
            player.transform.position += shift;
            body.enabled = true;
            Physics.SyncTransforms();
            player.GetComponent<PlayerSwap>().ClearPending();
            SceneManager.SetActiveScene(destination);
            next.BindPlayer(player);
            entry = next;
            lastExit = null;
            hud.EncounterPrompt = null;
            if (prepared) ClearStagedFloor();
            yield return SceneManager.UnloadSceneAsync(oldFloor);
            yield return PrepareAtEntry(entry.PreloadPath);
        }
        else
        {
            exitFailed = true;
            if (prepared) SetStagedRoots(false);
            else if (destination.isLoaded && !alreadyLoaded) yield return SceneManager.UnloadSceneAsync(destination);
        }
        presenter.enabled = true;
        input.ActivateInput();
        RestoreClock();
        ShowLoading(false);
    }

    public void Restart()
    {
        if (caught && !loading) StartCoroutine(ReloadFloor());
    }

    private IEnumerator ReloadFloor()
    {
        ShowLoading(true);
        var floor = entry.gameObject.scene;
        rig.SetActive(false);
        Destroy(rig);
        SceneManager.SetActiveScene(gameObject.scene);
        yield return SceneManager.UnloadSceneAsync(floor);
        entry = null;
        yield return StartAttempt(startingFloorPath);
        caught = false;
        RestoreClock();
    }

    private void ShowLoading(bool visible)
    {
        loading = visible;
        if (visible && guardAlert) guardAlert.Hide();
        loadingScreen.SetActive(visible);
    }

    private void PauseClock()
    {
        if (clockPaused) return;
        resumeScale = Time.timeScale;
        Time.timeScale = 0f;
        clockPaused = true;
    }

    private void RestoreClock()
    {
        if (!clockPaused) return;
        Time.timeScale = resumeScale;
        clockPaused = false;
    }

    private void OnDestroy()
    {
        SceneManager.sceneLoaded -= ParkLoadedFloor;
        RestoreClock();
    }
}
