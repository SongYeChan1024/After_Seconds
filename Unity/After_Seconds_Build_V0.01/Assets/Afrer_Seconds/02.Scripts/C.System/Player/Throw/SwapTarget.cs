using UnityEngine;

// 교환이 허용된 경비·독립 식판의 루트에만 붙인다. 몸과 발 기준점은 실제 충돌체에서 읽는다.
[DisallowMultipleComponent]
public sealed class SwapTarget : MonoBehaviour
{
    [SerializeField] private Collider bodyCollider;
    private WorldItem item;
    public Collider Body => bodyCollider;
    public event System.Action Relocated;
    internal void NotifyRelocated() => Relocated?.Invoke();
    public bool Available => isActiveAndEnabled && bodyCollider != null && bodyCollider.enabled &&
                             (item == null || !item.IsStored);

    private void Awake() => item = GetComponent<WorldItem>();
}
