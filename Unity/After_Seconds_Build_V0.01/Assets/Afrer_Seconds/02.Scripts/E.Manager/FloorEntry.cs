using UnityEngine;
using UnityEngine.SceneManagement;

#region 의사코드
// 층이 시작하면 출구·도착 표식을 모으고 공통 씬의 플레이어를 경비와 승강기에 연결한다.
// 계단참에 발이 닿으면 해당 출구를 반환하고, 승강기는 탑승 버튼에서만 출발시킨다.
// 목적 층에서는 같은 코어의 도착 표식을 찾는다. 매 프레임 활성 경비의 붙잡기·사격 경고를 모은다.
// 층에 배치된 경비를 찾아 새 플레이어를 전달한다. 같은 층의 세 출구가 공유하는 목적 씬을 상행 개방 때 미리 준비한다.
#endregion

// 이 Transform은 층 시작 시 플레이어 루트의 위치와 방향을 나타낸다.
public sealed class FloorEntry : MonoBehaviour
{
    [Tooltip("상행이 열릴 때 미리 읽을 목적 층. 계단 A·B와 화물 승강기가 같은 층을 사용한다.")]
    [SerializeField] private FloorPassage preloadExit;
    public string PreloadPath => preloadExit && preloadExit.isActiveAndEnabled ? preloadExit.DestinationPath : null;

    [SerializeField] private FreightLift lift;
    public FreightLift Lift => lift;
    [SerializeField] private FloorExperience experience;
    [SerializeField] private FloorSecurity security;
    public FloorExperience Experience => experience;
    public FloorSecurity Security => security;
    public bool UpwardOpen => !experience || experience.Cleared;
    private GuardPresenter[] guards = System.Array.Empty<GuardPresenter>();
    private FloorPassage[] passages;

    private void Awake() => passages = GetComponentsInChildren<FloorPassage>();

    private void Start()
    {
        // 레벨 디자이너가 B5만 열고 재생할 때도 빌드와 같은 공통 씬을 사용한다.
        if (!SceneManager.GetSceneByPath(SceneFlow.RootPath).isLoaded)
            SceneManager.LoadSceneAsync(SceneFlow.RootPath, LoadSceneMode.Additive);
    }

    public void BindPlayer(PlayerMotor player, SceneFlow owner, bool facilityAlert = false)
    {
        if (lift) lift.Bind(owner);
        var placed = new System.Collections.Generic.List<GuardPresenter>();
        foreach (var root in gameObject.scene.GetRootGameObjects())
            placed.AddRange(root.GetComponentsInChildren<GuardPresenter>(true));
        guards = placed.ToArray();
        foreach (var guard in guards) if (guard.isActiveAndEnabled) guard.BindPlayer(player);
        if (security) security.Bind(player, experience, facilityAlert, owner, GetComponent<B5MealOpening>());
    }

    public FloorPassage ExitAt(Vector3 feet, float tolerance)
    {
        foreach (var passage in passages)
            if (passage.Core != FloorCore.FreightLift && passage.ContainsFeet(feet, tolerance)) return passage;
        return null;
    }

    public FloorPassage LiftExit()
    {
        foreach (var passage in passages)
            if (passage.IsExit && passage.Core == FloorCore.FreightLift) return passage;
        return null;
    }

    public FloorPassage ArrivalAt(FloorCore core)
    {
        foreach (var passage in passages)
            if (!passage.IsExit && passage.Core == core && passage.isActiveAndEnabled) return passage;
        return null;
    }

    public bool ShotWarning { get; private set; }

    public bool ReadEncounter(out bool warning, out GuardPresenter alert)
    {
        warning = false;
        ShotWarning = false;
        alert = null;
        int bestPriority = 0;
        System.Collections.Generic.IReadOnlyList<GuardPresenter> present = security ? security.Roster : guards;
        for (int i = 0; i < present.Count; i++)
        {
            var guard = present[i];
            if (!guard || !guard.isActiveAndEnabled) continue;
            if (guard.Captured) return true;
            warning |= guard.CapturePending;
            ShotWarning |= guard.ShotPending;
            if (guard.Recognition <= 0f || (!guard.HasSight && !guard.RedAlert)) continue;
            // 직접 추격, 직접 의심, 시야가 끊긴 수색 순으로 하나의 경고를 고른다.
            int priority = guard.HasSight ? (guard.RedAlert ? 3 : 2) : 1;
            if (priority > bestPriority || (priority == bestPriority &&
                (guard.Recognition > alert.Recognition ||
                 (guard.Recognition == alert.Recognition && guard.IdentifiedAt > alert.IdentifiedAt))))
            {
                bestPriority = priority;
                alert = guard;
            }
        }
        return false;
    }
}
