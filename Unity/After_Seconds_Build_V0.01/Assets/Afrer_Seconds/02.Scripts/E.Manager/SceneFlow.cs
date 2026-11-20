using System.Collections;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.SceneManagement;

#region 의사코드
// 로딩을 암전하고 시작 장면을 밝힌다. B5에서는 포드의 첫 실제 교환 뒤 경비와 조작을 연결한다.
// 계단참이나 탑승 버튼에서 목표 층을 정한다. 승강기라면 문을 닫고 승객을 위층 높이까지 옮긴다.
// 로딩 중 같은 코어의 도착 공간을 검사한다. 성공하면 기존 플레이어를 옮기고 이전 씬을 내린다. 실패하면 출발 층에서 조작을 돌려준다.
// 붙잡히거나 HP가 0이면 시간을 멈추고 재시도 입력에서 시작 층과 플레이어를 새로 준비한다.
// 층의 현장 조건을 충족해야 계단과 승강기를 허용한다. 시설 전체 경보만 다음 지하층에 전달한다.
// 도착 후 로딩 화면을 내리고 승강장 문과 칸 문을 함께 연다. 문이 끝까지 열린 뒤 조작을 재개한다.
#endregion

// 공통 씬은 플레이어·카메라·화면을 소유한다. 계단은 목적 층과 같은 코어를 지정한다.
[DefaultExecutionOrder(400)]
public sealed class SceneFlow : MonoBehaviour
{
    
    public const string RootPath = "Assets/Afrer_Seconds/01.Scenes/GameRoot.unity";
    [SerializeField] private string startingFloorPath;
    [SerializeField] private GameObject playerRigPrefab;
    private LoadingScreen loadingScreen;
    [SerializeField] private GuardAlertView guardAlert;
    private GameObject rig;
    private PlayerPresenter presenter;
    private PlayerInput input;
    private PlayerMotor player;
    private PlayerDamageReceiver playerHealth;
    private CharacterController body;
    private Camera playerCamera;
    private PlayerInventoryView hud;
    private FloorEntry entry;
    private FloorPassage lastExit;
    private double reportDue = double.PositiveInfinity;
    private int witnessScene;
    private float witnessAt;
    private Vector3 witnessPoint;
    private const float ResearchReportSeconds = 30f;

    // 신고 예약은 공통 씬이 소유한다. 동결된 게임 시간은 세지 않고, 층을 바꾸어도 원래 신고 시각을 유지한다.
    public void QueueResearchReport(FloorSecurity source, Vector3 point, float observedAt)
    {
        if (!source || !entry || source != entry.Security || attemptEnded || !double.IsPositiveInfinity(reportDue)) return;
        reportDue = observedAt + ResearchReportSeconds;
        witnessScene = source.gameObject.scene.handle;
        witnessPoint = point;
        witnessAt = observedAt;
    }

    public void UpdateResearchObservation(FloorSecurity source, Vector3 point, float observedAt)
    {
        if (!source || double.IsPositiveInfinity(reportDue) || source.gameObject.scene.handle != witnessScene) return;
        witnessPoint = point;
        witnessAt = observedAt;
    }

    private void TickResearchReport()
    {
        double remaining = reportDue - Time.timeAsDouble;
        if (remaining <= 0)
        {
            if (entry.Security) entry.Security.RaiseResearchAlarm(entry.gameObject.scene.handle == witnessScene, witnessPoint, witnessAt);
            reportDue = double.PositiveInfinity;
        }
        hud.SetReportCountdown(entry.Security && !double.IsPositiveInfinity(reportDue) ? Mathf.CeilToInt((float)remaining) : -1);
    }
    private bool loading, attemptEnded, clockPaused, exitFailed;
    private float resumeScale;
    private string stagingPath;
    private AsyncOperation preloadOperation;

    private IEnumerator Start()
    {
        // 층 씬을 직접 재생하거나 GameRoot와 함께 열어 둔 경우 그 층을 그대로 사용한다.
        var active = SceneManager.GetActiveScene();
        var loaded = FindEntry(active);
        for (int i = 0; !loaded && i < SceneManager.sceneCount; i++)
            loaded = FindEntry(SceneManager.GetSceneAt(i));
        yield return LoadIfNeeded(LoadingScreen.ScenePath);
        var screenScene = SceneManager.GetSceneByPath(LoadingScreen.ScenePath);
        if (screenScene.isLoaded)
            foreach (var root in screenScene.GetRootGameObjects())
                if (root.TryGetComponent(out loadingScreen)) break;
        if (!loadingScreen) Debug.LogError("Loading 씬의 빌드 등록과 LoadingScreen 루트를 확인해 주세요.", this);
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
        reportDue = double.PositiveInfinity;
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
        var opening = entry.GetComponent<B5MealOpening>();
        var startPosition = opening ? opening.StartingFeet : entry.transform.position;
        rig = Instantiate(playerRigPrefab, startPosition, entry.transform.rotation, transform);
        player = rig.GetComponentInChildren<PlayerMotor>();
        playerHealth = player.GetComponent<PlayerDamageReceiver>();
        presenter = player.GetComponent<PlayerPresenter>();
        input = player.GetComponent<PlayerInput>();
        body = player.GetComponent<CharacterController>();
        playerCamera = rig.GetComponentInChildren<Camera>();
        hud = rig.GetComponentInChildren<PlayerInventoryView>();
        presenter.enabled = false;
        input.DeactivateInput();
        var inventoryCanvas = hud.GetComponent<Canvas>();
        if (opening)
        {
            if (inventoryCanvas) inventoryCanvas.enabled = false;
            opening.Prepare(player);
        }
        if (loadingScreen) yield return loadingScreen.Reveal();
        RestoreClock();
        attemptEnded = false;
        if (opening)
        {
            yield return opening.Play();
            if (inventoryCanvas) inventoryCanvas.enabled = true;
            if (!opening.Completed)
            {
                Debug.LogError("B5 배식구의 식판 충돌이나 교환 착지 공간을 확인해 주세요.", opening);
                player.GetComponent<PlayerSwap>().ClearPending();
                attemptEnded = true;
                PauseClock();
                hud.EncounterPrompt = "배식구가 막혔다 · Enter로 다시 시작";
                ShowLoading(false);
                yield break;
            }
        }
        entry.BindPlayer(player, this);
        lastExit = null;
        exitFailed = false;
        presenter.enabled = true;
        input.ActivateInput();
        ShowLoading(false);
    }

    // 상행 잠금이 풀리면 목적 층의 데이터를 읽는다. 그 층의 충돌체와 경비는 실제 이동 때 활성화한다.
    private void BeginPreload(string path)
    {
        if (preloadOperation != null || string.IsNullOrEmpty(path) || SceneManager.GetSceneByPath(path).isLoaded ||
            SceneUtility.GetBuildIndexByScenePath(path) < 0) return;
        preloadOperation = SceneManager.LoadSceneAsync(path, LoadSceneMode.Additive);
        if (preloadOperation == null) return;
        stagingPath = path;
        preloadOperation.allowSceneActivation = false;
    }

    private IEnumerator ActivatePreload()
    {
        preloadOperation.allowSceneActivation = true;
        yield return preloadOperation;
        preloadOperation = null;
        stagingPath = null;
    }

    // Unity는 활성화 대기 중인 비동기 로드를 취소할 수 없다. 재시도 전에 대기를 풀고 그 층을 회수한다.
    private IEnumerator DiscardPreload()
    {
        if (preloadOperation == null) yield break;
        string path = stagingPath;
        SceneManager.sceneLoaded += HideDiscardedFloor;
        yield return ActivatePreload();
        SceneManager.sceneLoaded -= HideDiscardedFloor;
        var unused = SceneManager.GetSceneByPath(path);
        if (unused.isLoaded) yield return SceneManager.UnloadSceneAsync(unused);
    }

    private void HideDiscardedFloor(Scene scene, LoadSceneMode mode)
    {
        if (scene.path != stagingPath) return;
        foreach (var root in scene.GetRootGameObjects()) root.SetActive(false);
    }

    private void LateUpdate()
    {
        if (!entry || !rig) return;
        if (!attemptEnded && Time.timeScale > 0f) TickResearchReport();
        if (loading) return;
        if (attemptEnded)
        {
            var keys = Keyboard.current;
            if (keys != null && (keys.enterKey.wasPressedThisFrame || keys.numpadEnterKey.wasPressedThisFrame))
                Restart();
            return;
        }
        bool captured = entry.ReadEncounter(out bool warning, out var alert);
        bool outOfHP = playerHealth && playerHealth.CurrentHP == 0;
        if (outOfHP || captured)
        {
            if (guardAlert) guardAlert.Hide();
            attemptEnded = true;
            PauseClock();
            presenter.enabled = false;
            hud.EncounterPrompt = outOfHP ? "체력 소진 · Enter로 다시 시작" : "붙잡혔다 · Enter로 다시 시작";
            return;
        }
        if (guardAlert)
        {
            if (alert) guardAlert.SetAlert(alert.Recognition, alert.RedAlert, alert.HasSight, alert.AlertAnchor, playerCamera, alert.IdentifiedAt);
            else guardAlert.Hide();
        }
        if (Time.timeScale == 0f) return;
        var feet = Feet();
        if (entry.Experience) entry.Experience.Tick(feet, player.IsCrouching, body.isGrounded);
        hud.FloorHint = entry.Experience ? entry.Experience.Hint : null;
        hud.SetFacilityLevel(entry.Security ? entry.Security.Level : -1);
        if (entry.UpwardOpen && preloadOperation == null) BeginPreload(entry.PreloadPath);
        var exit = body.isGrounded ? entry.ExitAt(feet, body.skinWidth + .03f) : null;
        if (exit != lastExit)
        {
            lastExit = exit;
            exitFailed = false;
            if (exit && entry.UpwardOpen)
            {
                StartCoroutine(Travel(exit, feet - exit.transform.position));
                return;
            }
        }
        hud.EncounterPrompt = exit && !entry.UpwardOpen ? entry.Experience.Hint : exitFailed ? "도착할 공간이 없다" : warning ? "경비의 손이 닿는다!" : entry.ShotWarning ? "경비가 겨눈다 · 엄폐!" : null;
    }

    private Vector3 Feet()
    {
        var bounds = body.bounds;
        return new Vector3(bounds.center.x, bounds.min.y, bounds.center.z);
    }

    public bool CanAscend => entry && entry.UpwardOpen;
    public bool CanUseLift => !loading && !attemptEnded && Time.timeScale > 0f;

    public bool BoardLift(FreightLift lift, PlayerInventory actor)
    {
        if (!CanUseLift || !CanAscend || lift != entry.Lift || actor.Body != body) return false;
        var exit = entry.LiftExit();
        if (!exit || SceneUtility.GetBuildIndexByScenePath(exit.DestinationPath) < 0) return false;
        StartCoroutine(Travel(exit, Feet() - exit.transform.position, lift));
        return true;
    }

    private IEnumerator Travel(FloorPassage exit, Vector3 offset, FreightLift lift = null)
    {
        var oldFloor = entry.gameObject.scene;
        string path = exit.DestinationPath;
        if (!entry.UpwardOpen || path == oldFloor.path || SceneUtility.GetBuildIndexByScenePath(path) < 0)
        {
            exitFailed = true;
            yield break;
        }
        loading = true;
        BeginPreload(path);
        presenter.enabled = false;
        input.DeactivateInput();
        if (lift)
        {
            hud.EncounterPrompt = "승강기 상행 중";
            player.GetComponent<PlayerSwap>().ClearPending();
            body.enabled = false;
            yield return lift.Ride(body, true);
            body.enabled = true;
        }
        ShowLoading(true);
        PauseClock();
        // 현재 프레임에 전환 화면을 그린 뒤 물리·렌더 오브젝트를 전환한다.
        yield return null;
        if (preloadOperation != null && stagingPath != path) yield return DiscardPreload();
        bool alreadyLoaded = SceneManager.GetSceneByPath(path).isLoaded;
        if (preloadOperation != null) yield return ActivatePreload();
        else yield return LoadIfNeeded(path);
        var destination = SceneManager.GetSceneByPath(path);
        var next = FindEntry(destination);
        var arrival = next ? next.ArrivalAt(exit.Core) : null;
        var arrivalLift = lift && next ? next.Lift : null;
        if (arrivalLift) arrivalLift.Receive();
        Physics.SyncTransforms();
        if ((!lift || arrivalLift) && arrival && arrival.TryPlaceFeet(offset, body, out var feet))
        {
            Vector3 shift = feet - Feet();
            body.enabled = false;
            player.transform.position += shift;
            body.enabled = true;
            Physics.SyncTransforms();
            player.GetComponent<PlayerSwap>().ClearPending();
            SceneManager.SetActiveScene(destination);
            next.BindPlayer(player, this, entry.Security && entry.Security.Level == 3);
            entry = next;
            lastExit = null;
            hud.EncounterPrompt = null;
            yield return SceneManager.UnloadSceneAsync(oldFloor);
            // 이전 층 전용 리소스는 여기서 회수한다. 다음 상행 잠금이 열릴 때까지 다른 층을 읽지 않는다.
            yield return Resources.UnloadUnusedAssets();
            if (loadingScreen) yield return loadingScreen.Reveal();
            if (arrivalLift)
            {
                RestoreClock();
                hud.EncounterPrompt = "승강기 도착";
                yield return arrivalLift.OpenAtArrival();
                hud.EncounterPrompt = null;
            }
        }
        else
        {
            exitFailed = true;
            if (destination.isLoaded && !alreadyLoaded) yield return SceneManager.UnloadSceneAsync(destination);
            if (loadingScreen) yield return loadingScreen.Reveal();
            if (lift)
            {
                RestoreClock();
                hud.EncounterPrompt = "도착할 공간이 없어 복귀 중";
                body.enabled = false;
                yield return lift.Ride(body, false);
                body.enabled = true;
            }
        }
        presenter.enabled = true;
        input.ActivateInput();
        RestoreClock();
        ShowLoading(false);
    }

    public void Restart()
    {
        if (attemptEnded && !loading) StartCoroutine(ReloadFloor());
    }

    private IEnumerator ReloadFloor()
    {
        ShowLoading(true);
        yield return DiscardPreload();
        var floor = entry.gameObject.scene;
        rig.SetActive(false);
        Destroy(rig);
        SceneManager.SetActiveScene(gameObject.scene);
        yield return SceneManager.UnloadSceneAsync(floor);
        entry = null;
        yield return StartAttempt(startingFloorPath);
    }

    private void ShowLoading(bool visible)
    {
        loading = visible;
        if (visible && guardAlert) guardAlert.Hide();
        if (loadingScreen) loadingScreen.SetVisible(visible);
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
        SceneManager.sceneLoaded -= HideDiscardedFloor;
        if (preloadOperation != null) preloadOperation.allowSceneActivation = true;
        RestoreClock();
    }
}
