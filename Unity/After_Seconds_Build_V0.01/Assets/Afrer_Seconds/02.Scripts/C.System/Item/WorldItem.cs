using UnityEngine;
using UnityEngine.SceneManagement;

// 의사코드: 월드의 개별 물건 → 소유권 확보 → 물리를 멈추고 비활성 보관.
// 다시 내놓으면 같은 물건의 물리와 교환 판정을 되살린다. 들고 있는 동안에는 교환할 수 없다.
[DisallowMultipleComponent, RequireComponent(typeof(ThrownObject), typeof(SwapTarget))]
public class WorldItem : MonoBehaviour, IInteractable
{
    [SerializeField] private ItemDefinition definition;
    private Rigidbody body;
    private ThrownObject thrown;
    private Collider[] colliders;
    private PhysicsMaterial[] materials;
    private float linearDamping, angularDamping, maxAngularVelocity, pickupAfter;
    private Transform owner;
    private static int nextNumber;
    public ItemDefinition Definition => definition;
    public int Number { get; private set; }
    public ItemAbility Ability { get; private set; }
    public int InteractionPriority => 0;
    public string InteractionPrompt => "[F] " + definition.DisplayName + " 줍기";
    public bool CanInteract(PlayerInventory actor) => CanPickup;
    public bool Interact(PlayerInventory actor) => actor.StoreFocusedItem(this);

    public bool IsStored => owner != null;
    public bool CanPickup => isActiveAndEnabled && !IsStored && definition != null && Time.time >= pickupAfter;

    private void Awake()
    {
        body = GetComponent<Rigidbody>(); thrown = GetComponent<ThrownObject>();
        colliders = GetComponentsInChildren<Collider>(true);
        materials = new PhysicsMaterial[colliders.Length];
        for (int i = 0; i < colliders.Length; i++) materials[i] = colliders[i].sharedMaterial;
        linearDamping = body.linearDamping; angularDamping = body.angularDamping; maxAngularVelocity = body.maxAngularVelocity;
        Number = ++nextNumber;
        Ability = GetComponent<ItemAbility>();
    }

    // 경비 허리의 소품은 보이지만 월드에서 집히지 않는다. 분리한 뒤에도 같은 객체와 잔탄을 쓴다.
    internal void Wear(Transform carrier)
    {
        owner = carrier;
        body.isKinematic = true;
        foreach (var c in colliders) c.enabled = false;
    }

    internal void UnholsterToWorld(Vector3 releaseVelocity)
    {
        owner = null;
        transform.SetParent(null, true);
        foreach (var c in colliders) c.enabled = true;
        body.isKinematic = false;
        body.linearVelocity = releaseVelocity;
        body.WakeUp();
    }

    public bool TryStore(Transform newOwner)
    {
        if (!CanPickup || newOwner == null) return false;
        owner = newOwner; thrown.Disarm();
        body.linearVelocity = body.angularVelocity = Vector3.zero;
        body.isKinematic = true;
        gameObject.SetActive(false);
        transform.SetParent(owner, true);
        return true;
    }

    public ThrownObject Release(Vector3 position, Quaternion rotation, float pickupDelay)
    {
        if (!IsStored) return null;
        owner = null;
        transform.SetParent(null, true);
        // 손을 떠난 물건은 현재 층을 내릴 때 그 층의 다른 기물과 같이 정리한다.
        var floor = SceneManager.GetActiveScene();
        if (gameObject.scene != floor) SceneManager.MoveGameObjectToScene(gameObject, floor);
        transform.SetPositionAndRotation(position, rotation);
        body.linearDamping = linearDamping; body.angularDamping = angularDamping; body.maxAngularVelocity = maxAngularVelocity;
        for (int i = 0; i < colliders.Length; i++) colliders[i].sharedMaterial = materials[i];
        pickupAfter = Time.time + pickupDelay;
        gameObject.SetActive(true);
        body.isKinematic = false;
        body.linearVelocity = body.angularVelocity = Vector3.zero;
        body.WakeUp();
        return thrown;
    }
}
