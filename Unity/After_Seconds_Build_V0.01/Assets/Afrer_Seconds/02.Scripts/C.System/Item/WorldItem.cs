using UnityEngine;
using UnityEngine.SceneManagement;

// 의사코드: 월드의 개별 물건 → 소유권 확보 → 물리를 멈추고 비활성 보관.
// 다시 내놓을 때 같은 객체를 꺼내고 원래 물리 설정을 복원한다. 종류가 같아도 합치지 않는다.
[DisallowMultipleComponent, RequireComponent(typeof(ThrownObject))]
public class WorldItem : MonoBehaviour
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
