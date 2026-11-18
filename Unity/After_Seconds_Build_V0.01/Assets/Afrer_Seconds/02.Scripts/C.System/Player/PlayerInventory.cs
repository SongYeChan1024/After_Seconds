using System.Collections.Generic;
using UnityEngine;

// 의사코드: 시선 가까운 물건과 차폐 검사 → F 한 번에 한 객체 확보 → 최대5개 목록에 보관.
// 휠은 선택을 바꾸고 Q는 안전한 손 앞에 내려놓는다. 성공한 방출만 목록에서 제거한다.
// 투척이 실패하면 그대로 소지하며, 같은 물건의 재획득은 같은 WorldItem을 다시 보관한다.
[DefaultExecutionOrder(250), RequireComponent(typeof(PlayerThrow))]
public class PlayerInventory : MonoBehaviour
{
    [SerializeField] private PlayerInventorySettings settings;
    private readonly List<WorldItem> items = new List<WorldItem>();
    private readonly RaycastHit[] hits = new RaycastHit[64];
    private PlayerThrow thrower;
    private PlayerZoom zoom;
    private int selectedIndex = -1;
    private string message;
    private float messageUntil;
    public IReadOnlyList<WorldItem> Items => items;
    public int Count => items.Count;
    public int Capacity => settings.capacity;
    public int SelectedIndex => selectedIndex;
    public WorldItem Selected => selectedIndex >= 0 && selectedIndex < items.Count ? items[selectedIndex] : null;
    public WorldItem Candidate { get; private set; }
    public string Message => Time.time < messageUntil ? message : null;
    public event System.Action Changed;

    private void Awake()
    {
        thrower = GetComponent<PlayerThrow>(); zoom = GetComponent<PlayerZoom>();
        if (settings == null) { Debug.LogError("PlayerInventorySettings를 연결해 주세요.", this); enabled = false; return; }
        thrower.SetHeldWorldItem(null);
    }
    private void OnEnable() { if (thrower != null) { thrower.Released += OnReleased; SyncSelection(); } }
    private void OnDisable() { if (thrower != null) { thrower.Released -= OnReleased; thrower.SetHeldWorldItem(null); } Candidate = null; }
    private void LateUpdate()
    {
        // 외부 사건으로 소지 객체가 사라져도 유령 슬롯을 남기지 않는다.
        for (int i = items.Count - 1; i >= 0; i--)
        {
            if (items[i] != null) continue;
            items.RemoveAt(i);
            if (i < selectedIndex) selectedIndex--;
            else if (i == selectedIndex) selectedIndex = Mathf.Min(i, items.Count - 1);
            SyncSelection();
        }
        RefreshCandidate();
    }

    public void RefreshCandidate()
    {
        Candidate = null;
        if (!isActiveAndEnabled || Time.timeScale <= 0f) return;
        Transform eye = thrower.Origin;
        int count = Physics.SphereCastNonAlloc(eye.position, settings.aimAssistRadius, eye.forward, hits,
            settings.pickupDistance, settings.pickupMask, QueryTriggerInteraction.Ignore);
        if (count == hits.Length) return;
        float nearest = float.PositiveInfinity; Collider first = null;
        for (int i = 0; i < count; i++)
        {
            var collider = hits[i].collider;
            if (collider.transform.IsChildOf(transform) || hits[i].distance >= nearest) continue;
            nearest = hits[i].distance; first = collider;
        }
        if (first == null) return;
        var item = first.GetComponentInParent<WorldItem>();
        if (item == null || !item.CanPickup || !ThrowFlight.TryShape(item.Definition.WorldPrefab, out _, out _)) return;
        Vector3 toward = first.bounds.center - eye.position;
        if (Vector3.Distance(eye.position, first.ClosestPoint(eye.position)) > settings.pickupDistance) return;
        // 조준 보조 구체가 모서리 너머를 잡아도 실제 시선이 벽을 통과할 수는 없다.
        if (thrower.Sweep(eye.position, toward, 0f, out RaycastHit hit) &&
            hit.collider != null && !hit.collider.transform.IsChildOf(item.transform)) return;
        Candidate = item;
    }

    public bool TryPickup()
    {
        if (!isActiveAndEnabled || Time.timeScale <= 0f) return false;
        RefreshCandidate();
        if (Candidate == null) return false;
        if (items.Count >= Capacity) { Tell("공간이 없어"); return false; }
        WorldItem item = Candidate;
        if (items.Contains(item) || !item.TryStore(transform)) return false;
        items.Add(item); selectedIndex = items.Count - 1; Candidate = null; message = null;
        SyncSelection(); return true;
    }

    public bool SelectRelative(int direction)
    {
        if (!isActiveAndEnabled || Time.timeScale <= 0f || items.Count == 0 || direction == 0) return false;
        // -1은 소지 공간을 쓰지 않는 맨손이다. 맨손 ↔ 첫 물건 ↔ … ↔ 마지막 물건 ↔ 맨손.
        selectedIndex += direction > 0 ? 1 : -1;
        if (selectedIndex >= items.Count) selectedIndex = -1;
        else if (selectedIndex < -1) selectedIndex = items.Count - 1;
        SyncSelection(); return true;
    }

    public bool TryDrop()
    {
        if (!isActiveAndEnabled || Time.timeScale <= 0f || Selected == null) return false;
        thrower.ExitStance();
        if (!thrower.TryGetLaunch(out ThrowLaunch launch)) { Tell("내려놓을 공간이 없어"); return false; }
        WorldItem item = Selected;
        var thrown = item.Release(launch.Position, launch.Rotation, settings.pickupDelay);
        if (thrown == null) return false;
        thrown.Disarm();
        foreach (var collider in thrown.GetComponentsInChildren<Collider>())
            foreach (var self in GetComponentsInChildren<Collider>())
                if (self.GetComponentInParent<WorldItem>(true) == null) Physics.IgnoreCollision(collider, self);
        items.RemoveAt(selectedIndex); selectedIndex = Mathf.Min(selectedIndex, items.Count - 1);
        SyncSelection(); return true;
    }

    private void OnReleased(ItemDefinition definition, ThrownObject thrown)
    {
        WorldItem item = thrown.GetComponent<WorldItem>();
        if (item == null || !items.Remove(item)) return;
        selectedIndex = Mathf.Min(selectedIndex, items.Count - 1);
        SyncSelection(true);
    }
    private void SyncSelection(bool preserveReleasePose = false)
    {
        thrower.SetHeldWorldItem(Selected, settings.pickupDelay, preserveReleasePose);
        if (zoom != null) zoom.SetZoomed(false);
        Changed?.Invoke();
    }
    internal void Tell(string text) { message = text; messageUntil = Time.time + settings.messageDuration; }
}
