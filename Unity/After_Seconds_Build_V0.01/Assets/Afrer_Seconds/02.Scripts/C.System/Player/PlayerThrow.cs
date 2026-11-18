using UnityEngine;

#region 의사코드 Ver 0.1 (던지기 자세, 조준, 던지기, 명중 알림 받기)

/*
플레이어가 물건을 던지는 기능
(Ver 0.1: 소지품 기능이 아직 없어서, 던지기 자세에서는 시험용 물건을 항상 들고 있는 것으로 친다.
         키를 눌렀는지는 Presenter가 받고, 여기서는 요청받은 대로 자세를 바꾸고 물건을 던진다.
         궤적 표시·위/아래 던지기 전환·확대 조준은 다음 버전에서 추가한다)

기억해둘 정보:
    던지기 설정 에셋의 참조 — settings
    던지는 기준 위치와 방향 — throwOrigin (눈 위치인 CameraRoot를 연결한다)
    던질 시험용 물건의 프리팹 — testItemPrefab
    지금 던지기 자세인지 — isInThrowStance, 처음에는 false
    지금 조준 중인지(왼쪽 클릭을 누르고 있는지) — isAiming, 처음에는 false
    플레이어 자신의 충돌체들 — ownColliders (던진 물건이 내 몸에 부딪히지 않게 하려고)

밖에서 읽을 수 있게 공개하는 값 (읽기만 가능):
    지금 던지기 자세인지 — IsInThrowStance
    지금 조준 중인지 — IsAiming

초기화할 때 — Awake:
    설정·기준 위치·시험용 물건 중 하나라도 연결되지 않았다면:
        오류를 알리고 이 컴포넌트를 비활성화한다
    플레이어와 자식 오브젝트의 충돌체를 모두 찾아 기억한다

던지기 자세를 바꾸라는 요청 — ToggleStance (E):
    던지기 자세가 아니라면: 던지기 자세로 들어간다
    던지기 자세라면: 조준 중이면 조준을 취소하고, 던지기 자세를 푼다

던지기 자세를 풀라는 요청 — ExitStance:
    조준 중이면 조준을 취소한다
    던지기 자세가 아닌 상태로 기록한다

조준을 시작하라는 요청 — BeginAim (왼쪽 클릭을 누름):
    던지기 자세가 아니라면: 아무것도 하지 않는다
    조준 중인 상태로 기록한다

조준을 취소하라는 요청 — CancelAim (조준 중 오른쪽 클릭):
    조준 중이 아닌 상태로 기록한다 (던지기 자세는 그대로 둔다. 다시 조준할 수 있게)

던지라는 요청 — ReleaseThrow (왼쪽 클릭을 뗌):
    조준 중이 아니라면: 아무것도 하지 않는다 (취소한 뒤에 손을 뗀 경우)
    조준 중이 아닌 상태로 기록한다
    물건을 던진다
    던지기 자세를 푼다 (던진 뒤에는 자동으로 풀린다)

물건을 던지는 기능 — Throw:
    바라보는 방향을 설정의 각도만큼 위로 들어 올려 던질 방향을 구한다
    눈 위치에서 바라보는 방향으로 조금 앞을 물건이 나타날 자리로 정한다
    그 자리에 시험용 물건을 만든다
    만든 물건이 플레이어 자신의 충돌체와는 부딪히지 않게 한다
    물건의 속도를 "던질 방향 × 던지는 빠르기"로 정한다
    물건에 최소 충돌 빠르기를 알려 주고, 명중 알림을 받도록 등록한다
    설정의 시간이 0보다 크면: 그 시간 뒤에 물건이 사라지게 한다

명중 알림을 받으면 — OnThrownObjectHit:
    "어느 물건이, 무엇에, 언제, 어디서 맞았는지"를 로그로 남긴다
        (지금은 로그만 남긴다. 나중에 공통 게임 시계와 예약 큐가 생기면
         여기서 "명중 시각 + 3초" 교환 예약을 요청한다)
*/

#endregion

#region 의사코드 Ver 0.2 (들고 있는 아이템, 궤적 표시, 위로/아래로 던지기)

/*
(Ver 0.2: ① 시험용 프리팹 대신 "지금 들고 있는 아이템"(ItemDefinition 에셋)을 던진다
         ② 조준하는 동안 물건이 날아갈 길을 선으로 보여 준다
         ③ R로 위로 던지기 / 아래로 던지기를 바꾼다
         Ver 0.1에서 바뀐 부분만 적는다)

기억해둘 정보 — 바뀐 것:
    던질 시험용 프리팹(testItemPrefab) 대신, 지금 들고 있는 아이템 — heldItem
        (소지품 기능이 생기기 전까지는 인스펙터에서 시험용 아이템을 연결해 둔다.
         소지품 기능이 생기면 물건을 바꿀 때마다 SetHeldItem으로 알려 준다)

기억해둘 정보에 추가:
    궤적을 그리는 선 — trajectoryLine (LineRenderer)
    지금 아래로 던지기 방식인지 — isUnderhand, 처음에는 false (위로 던지기)
    궤적의 점들을 담아 두는 목록 — trajectoryPoints (매 프레임 새로 만들지 않고 다시 쓴다)

밖에서 읽을 수 있게 공개하는 값에 추가 (읽기만 가능):
    지금 물건을 들고 있는지 — HasHeldItem
    지금 아래로 던지기 방식인지 — IsUnderhand

초기화할 때 — Awake 수정:
    설정·기준 위치·궤적 선 중 하나라도 연결되지 않았다면: 오류를 알리고 비활성화한다
        (들고 있는 아이템은 비어 있을 수 있으므로 여기서 검사하지 않는다)
    궤적 선을 보이지 않게 해 둔다

들고 있는 아이템을 바꾸라는 요청 — SetHeldItem:
    지금 들고 있는 것과 같다면: 아무것도 하지 않는다
    던지기 자세를 푼다 (다른 물건으로 바꾸면 던지기 자세가 풀린다)
    새 아이템을 들고 있는 것으로 기록한다 (비어 있음도 가능)

던지기 자세를 바꾸라는 요청 — ToggleStance 수정:
    들고 있는 아이템이 없다면: 던지기 자세로 들어가지 않는다

던지는 방식을 바꾸라는 요청 — ToggleThrowMode (R):
    던지기 자세가 아니라면: 아무것도 하지 않는다
    위로 던지기 ↔ 아래로 던지기를 서로 바꾼다

던질 방향과 빠르기를 구하는 기능 — GetThrowVelocity:
    아래로 던지기 방식이면 아래로 던지기의 빠르기와 각도를, 아니면 위로 던지기의 값을 고른다
    바라보는 방향을 고른 각도만큼 위로 들어 올리고, 고른 빠르기를 곱해 돌려준다
        (실제로 던질 때와 궤적을 그릴 때 같은 기능을 써서, 보이는 궤적과 실제 궤적이 어긋나지 않게 한다)

물건이 나타날 자리를 구하는 기능 — GetSpawnPosition:
    눈 위치에서 바라보는 방향으로 조금 앞을 돌려준다 (역시 던지기와 궤적이 함께 쓴다)

물건을 던지는 기능 — Throw 수정:
    들고 있는 아이템의 세상 속 프리팹을 복사해 만든다
    속도와 자리는 위의 두 기능으로 구한다

궤적을 새로 그리라는 요청 — RefreshTrajectory (Presenter가 매 프레임 부른다):
    조준 중이 아니라면: 궤적 선을 숨기고 끝낸다
    물건이 나타날 자리와 던질 속도를 구한다
    그 자리를 궤적의 첫 점으로 넣는다
    시간 간격만큼씩 앞으로 가면서, 최대 시간이 될 때까지 반복한다:
        "지금 자리 + 속도 × 시간 간격 + 중력으로 떨어진 거리"로 다음 자리를 구한다
        속도에 "중력 × 시간 간격"을 더한다 (점점 아래로 향한다)
        지금 자리에서 다음 자리 사이에 무언가 막고 있다면:
            막힌 지점을 궤적의 마지막 점으로 넣고 반복을 끝낸다
        다음 자리를 궤적의 점으로 넣고, 지금 자리를 다음 자리로 바꾼다
    모은 점들을 궤적 선에 넣고 선을 보이게 한다
*/

#endregion

#region 의사코드 Ver 0.3 (오른손에서 던지기)

/*
(Ver 0.3: 물건과 궤적이 화면 가운데가 아니라 오른손 위치에서 나가게 한다. Ver 0.2에서 바뀐 부분만 적는다)

물건이 나타날 자리를 구하는 기능 — GetSpawnPosition 수정:
    아래로 던지기 방식이면 허리 높이 손 위치를, 아니면 어깨 높이 손 위치를 고른다
    눈 위치에서 "오른쪽·위·앞"으로 고른 만큼 옮긴 자리를 손의 위치로 구한다
        (시선을 돌리면 손 위치도 함께 돌아간다)
    눈에서 손까지의 사이가 벽 등으로 막혀 있다면:
        눈 위치를 돌려준다 (벽에 붙었을 때 물건이 벽 속에서 나오지 않게)
    그렇지 않다면: 손의 위치를 돌려준다

    (던지기와 궤적이 이 기능을 함께 쓰므로, 한 곳만 바꿔도 물건과 궤적이 같은 자리에서 나간다)
*/

#endregion

#region 의사코드 Ver 0.4 (궤적을 방향만 보이게 짧게, 확대 조준 때는 길게)

/*
(Ver 0.4: 궤적을 끝까지 그리지 않는다. 어느 쪽으로 날아가는지만 알 수 있게 손에서부터 정해진 길이만큼만 그리고,
         오른쪽 클릭으로 확대 조준했을 때는 더 길게 그린다. Ver 0.3에서 바뀐 부분만 적는다)

궤적을 새로 그리라는 요청 — RefreshTrajectory 수정:
    지금 확대 조준 중인지를 전달받는다 (확대 여부는 PlayerZoom이 알고 있어서 Presenter가 넘겨 준다)

    이번에 그릴 길이를 정한다: 확대 조준 중이면 긴 길이, 아니면 짧은 길이
    지금까지 그린 길이를 0으로 둔다

    한 점씩 구하는 반복 안에서:
        다음 자리를 구한다 (Ver 0.2와 같음)
        그 사이가 막혀 있다면: 다음 자리를 막힌 지점으로 바꾼다
        이번 구간의 길이를 구한다
        "지금까지 그린 길이 + 이번 구간"이 정해진 길이를 넘는다면:
            남은 길이만큼만 간 지점을 마지막 점으로 넣고 반복을 끝낸다
        다음 자리를 점으로 넣고, 그린 길이에 이번 구간을 더한다
        막혀 있었다면: 반복을 끝낸다
*/

#endregion

#region 의사코드 Ver 0.5 (오른손에서 조준점 쪽으로 모이게 던지기)

/*
(Ver 0.5: 손은 눈보다 오른쪽에 있어서, 시선과 나란히 던지면 물건이 끝까지 조준점의 오른쪽으로 날아간다.
         손에서 화면 가운데(조준점) 쪽으로 향하도록 던지는 방향을 조금 왼쪽으로 튼다. Ver 0.4에서 바뀐 부분만 적는다)

던질 방향과 빠르기를 구하는 기능 — GetThrowVelocity 수정:
    던지는 방식에 따라 빠르기·각도와 함께 "모이는 거리"도 고른다
        (모이는 거리: 물건의 길이 시선과 만나는 지점까지의 거리. 위로 던지기는 멀리, 아래로 던지기는 가까이)

    시선 방향으로 모이는 거리 안에 벽 등이 있다면:
        그 벽까지의 거리를 모이는 거리로 쓴다 (단, 최소 거리보다 짧아지지 않게 한다)

    손이 눈에서 오른쪽·앞으로 얼마나 떨어져 있는지 구한다
    손에서 "시선 위로 모이는 거리만큼 앞의 점"을 향하는 방향을 구한다:
        오른쪽으로 떨어진 만큼 왼쪽으로, 앞으로는 (모이는 거리 - 손이 앞에 있는 거리)만큼
        위아래는 넣지 않는다 (아래로 던지기가 조준점을 향해 솟구치지 않고 낮게 나가게)

    그 방향을 고른 각도만큼 위로 들어 올리고, 고른 빠르기를 곱해 돌려준다
*/

#endregion
// 의사코드 Ver 0.6:
// 손의 현재 위치/물리 프로필 → 시작 겹침과 눈~손 구체 이동 검사 → 한 번만 즉시 발사.
// 손 표시의 물건을 그 프레임에 숨기고 복귀한다. 이벤트 대기나 3초 대기는 없다.
// 선은 표시 길이에서 자르고 페이드한다. 같은 물리 경로 예측은 첫 구체 충돌/예측 한도까지 계속한다.
// 표시선이 실제 접촉 표면까지 닿을 때만 원을 표시한다. 선 너머나 거리/시간 끝에는 원을 만들지 않는다.
// 취소·비활성화·아이템 교체는 상태/선을 즉시 비운다.
[DefaultExecutionOrder(200)]
public class PlayerThrow : MonoBehaviour
{
    [SerializeField] private PlayerThrowSettings settings;
    [SerializeField] private Transform throwOrigin;
    [SerializeField] private ItemDefinition heldItem;
    [SerializeField] private LineRenderer trajectoryLine;
    [Tooltip("시험용 공을 반복 공급합니다. 끄면 성공한 투척에서 선택 물건을 비웁니다. 인벤토리는 별도입니다.")]
    [SerializeField] private bool repeatTestItem = true;

    private bool isInThrowStance, isAiming, isUnderhand;
    private PlayerFirstPersonHands hands;
    private PlayerZoom zoom;
    private WorldItem heldWorldItem;
    private bool inventoryManaged;
    private float pickupDelay;
    private readonly RaycastHit[] hits = new RaycastHit[64];
    private readonly Collider[] overlaps = new Collider[64];
    private readonly System.Collections.Generic.List<Vector3> trajectoryPoints = new System.Collections.Generic.List<Vector3>();
    private readonly Gradient lineGradient = new Gradient();
    private float lastOpacity = -1f, lastFade = -1f, lastEndOpacity = -1f;
    private LineRenderer blockedMark;
    private LineRenderer landingMarker;
    private readonly Vector3[] markerPoints = new Vector3[40];

    public bool IsInThrowStance => isInThrowStance;
    public bool IsAiming => isAiming;
    public bool IsUnderhand => isUnderhand;
    public bool HasHeldItem => heldItem != null && heldItem.WorldPrefab != null &&
        (!inventoryManaged || (heldWorldItem != null && heldWorldItem.IsStored));
    public ItemDefinition HeldItem => heldItem;
    public Transform Origin => throwOrigin;
    public Vector3 HandOffset => isUnderhand ? settings.UnderhandHandOffset : settings.OverhandHandOffset;
    public bool IsBlocked { get; private set; }
    public bool PreviewHit { get; private set; }
    public Vector3 PreviewEnd { get; private set; }
    public Vector3 PreviewContact { get; private set; }
    public Vector3 PreviewNormal { get; private set; }
    public bool LandingMarkerVisible => landingMarker != null && landingMarker.enabled;
    public int ReleaseCount { get; private set; }
    public ThrownObject LastThrown { get; private set; }
    public ThrowLaunch LastLaunch { get; private set; }
    public event System.Action<ItemDefinition, ThrownObject> Released;
    public event System.Action<ThrownObject, Collision> Hit;

    private void Awake()
    {
        if (settings == null || throwOrigin == null || trajectoryLine == null)
        {
            Debug.LogError("PlayerThrow의 Settings, Throw Origin, Trajectory Line을 연결해 주세요.", this);
            enabled = false;
            return;
        }
        hands = GetComponent<PlayerFirstPersonHands>();
        zoom = GetComponent<PlayerZoom>();
        trajectoryLine.useWorldSpace = true;
        trajectoryLine.enabled = false;
        var marker = new GameObject("ThrowBlocked");
        marker.transform.SetParent(transform, false);
        blockedMark = marker.AddComponent<LineRenderer>();
        blockedMark.sharedMaterial = trajectoryLine.sharedMaterial;
        blockedMark.useWorldSpace = true;
        blockedMark.startWidth = blockedMark.endWidth = 0.0015f;
        blockedMark.startColor = blockedMark.endColor = new Color(1f, 0.3f, 0.15f, 0.85f);
        blockedMark.positionCount = 5;
        blockedMark.enabled = false;
        var landing = new GameObject("ThrowLandingMarker");
        landing.transform.SetParent(transform, false);
        landingMarker = landing.AddComponent<LineRenderer>();
        landingMarker.sharedMaterial = trajectoryLine.sharedMaterial;
        landingMarker.useWorldSpace = true;
        landingMarker.loop = true;
        landingMarker.numCornerVertices = 2;
        landingMarker.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        landingMarker.receiveShadows = false;
        landingMarker.startColor = landingMarker.endColor = new Color(0.65f, 0.9f, 1f, 0.85f);
        landingMarker.enabled = false;
    }

    public void SetHeldItem(ItemDefinition newItem)
    {
        inventoryManaged = false; heldWorldItem = null; // 독립 투척 시험용. 실제 소지품은 SetHeldWorldItem을 사용한다.
        if (newItem == heldItem) return;
        ExitStance();
        heldItem = newItem;
        if (hands != null) hands.ResetPose();
    }

    public void SetHeldWorldItem(WorldItem item, float reacquireDelay = 0f, bool preserveReleasePose = false)
    {
        ExitStance();
        inventoryManaged = true; heldWorldItem = item; heldItem = item != null ? item.Definition : null; pickupDelay = reacquireDelay;
        if (!preserveReleasePose && hands != null) hands.ResetPose();
    }

    public void ToggleStance()
    {
        if (!isActiveAndEnabled) return;
        if (isInThrowStance) { ExitStance(); return; }
        if (!HasHeldItem) return;
        isInThrowStance = true;
        if (hands != null) hands.InterruptRecovery();
    }

    public void ExitStance()
    {
        isAiming = false;
        isInThrowStance = false;
        ClearPreview();
    }

    public void ToggleThrowMode()
    {
        if (isActiveAndEnabled && HasHeldItem) isUnderhand = !isUnderhand;
    }

    public void BeginAim()
    {
        if (!isActiveAndEnabled || !HasHeldItem) return;
        // 좌클릭만으로 준비에 들어간다. 이전 투척의 복귀 중에도 새 입력을 바로 받는다.
        if (!isInThrowStance)
        {
            isInThrowStance = true;
            if (hands != null) hands.InterruptRecovery();
        }
        isAiming = true;
    }

    public void CancelAim()
    {
        isAiming = false;
        ClearPreview();
    }

    public bool ReleaseThrow()
    {
        if (!isActiveAndEnabled || !isAiming || !HasHeldItem) return false;
        isAiming = false; // 먼저 잠근다. 같은 입력/중복 콜백은 두 번째 물체를 만들 수 없다.
        ClearPreview();
        if (!TryGetLaunch(out ThrowLaunch launch))
        {
            IsBlocked = true;
            return false; // 실패는 물건을 소비하지 않고 다시 조준할 수 있게 한다.
        }

        ItemDefinition item = heldItem;
        bool fromInventory = heldWorldItem != null;
        ThrownObject thrown = fromInventory ? heldWorldItem.Release(launch.Position, launch.Rotation, pickupDelay) :
            Instantiate(item.WorldPrefab, launch.Position, launch.Rotation);
        if (thrown == null) return false;
        var own = GetComponentsInChildren<Collider>(true);
        foreach (Collider collider in thrown.GetComponentsInChildren<Collider>())
            foreach (Collider self in own)
                if (self != null && self.GetComponentInParent<WorldItem>(true) == null) Physics.IgnoreCollision(collider, self);

        Rigidbody body = thrown.GetComponent<Rigidbody>();
        body.linearDamping = launch.Damping;
        body.linearVelocity = launch.Velocity;
        if (isUnderhand && !launch.Shape.IsBox)
        {
            if (settings.UnderhandPhysicsMaterial != null)
                thrown.GetComponent<SphereCollider>().sharedMaterial = settings.UnderhandPhysicsMaterial;
            // 구체 반지름과 전진 속도에 맞춰 굴림 회전을 준다. 이후에는 중력/접촉 마찰로 움직인다.
            Vector3 spin = Vector3.Cross(Vector3.up, Vector3.ProjectOnPlane(launch.Velocity, Vector3.up)) / launch.Radius;
            body.maxAngularVelocity = Mathf.Max(body.maxAngularVelocity, spin.magnitude);
            body.angularDamping = Mathf.Max(body.angularDamping, settings.UnderhandDamping);
            body.angularVelocity = spin;
        }
        thrown.Initialize(settings.MinHitSpeed);
        thrown.Hit -= OnThrownObjectHit; // 같은 물건을 다시 던져도 리스너를 중복 등록하지 않는다.
        thrown.Hit += OnThrownObjectHit;
        if (!fromInventory && repeatTestItem && settings.TestItemLifetime > 0f) Destroy(thrown.gameObject, settings.TestItemLifetime);
        LastThrown = thrown;
        LastLaunch = launch;
        ReleaseCount++;
        if (hands != null) hands.OnReleased(isUnderhand);
        if (fromInventory || !repeatTestItem) { heldItem = null; heldWorldItem = null; }
        ExitStance();
        Released?.Invoke(item, thrown);
        return true;
    }

    public bool TryGetLaunch(out ThrowLaunch launch)
    {
        launch = default;
        if (!HasHeldItem || settings == null || throwOrigin == null ||
            !ThrowFlight.TryShape(heldItem.WorldPrefab, out ThrowShape shape, out Rigidbody body)) return false;
        Quaternion rotation = throwOrigin.rotation;
        Vector3 position = hands != null && hands.Ready ? hands.ItemPosition :
            throwOrigin.TransformPoint(HandOffset) - rotation * heldItem.GripOffset;
        if (hands != null && hands.Ready && hands.Obstructed) return false;
        if (OverlapsWorld(position, shape, rotation, settings.SurfaceSkin)) return false;
        Vector3 toHand = position - throwOrigin.position;
        if (OverlapsWorld(throwOrigin.position, shape, rotation, 0f) ||
            Sweep(throwOrigin.position, toHand, shape, rotation, 0f, out _)) return false;

        launch.Position = position;
        launch.Velocity = GetThrowVelocity(position);
        launch.Gravity = body.useGravity ? Physics.gravity : Vector3.zero;
        launch.Damping = isUnderhand ? Mathf.Max(body.linearDamping, settings.UnderhandDamping) : body.linearDamping;
        launch.Radius = shape.Radius;
        launch.Rotation = rotation;
        launch.Shape = shape;
        IsBlocked = false;
        return true;
    }

    private Vector3 GetThrowVelocity(Vector3 position)
    {
        float speed = isUnderhand ? settings.UnderhandSpeed : settings.OverhandSpeed;
        float angle = isUnderhand ? settings.UnderhandAngle : settings.OverhandAngle;
        float distance = isUnderhand ? settings.UnderhandConvergeDistance : settings.OverhandConvergeDistance;
        if (Sweep(throwOrigin.position, throwOrigin.forward * distance, 0f, out RaycastHit hit))
            distance = Mathf.Max(hit.distance, settings.MinConvergeDistance);
        Vector3 local = throwOrigin.InverseTransformPoint(position);
        // 수평만 중앙으로 수렴한다. 가까운 벽/아래 투척에서 카메라를 향해 역발사하지 않는다.
        Vector3 direction = (throwOrigin.right * -local.x +
            throwOrigin.forward * Mathf.Max(0.5f, distance - local.z)).normalized;
        direction = Quaternion.AngleAxis(-angle, throwOrigin.right) * direction;
        if (isUnderhand)
        {
            // 시선을 올려도 로브가 되지 않는다. 좌우 조준은 유지한다.
            float elevation = Mathf.Clamp(Mathf.Asin(Mathf.Clamp(direction.y, -1f, 1f)) * Mathf.Rad2Deg,
                -75f, Mathf.Clamp(settings.UnderhandMaxElevation, -75f, 0f)) * Mathf.Deg2Rad;
            Vector3 forward = Vector3.ProjectOnPlane(direction, Vector3.up);
            if (forward.sqrMagnitude < 0.0001f) forward = Vector3.ProjectOnPlane(transform.forward, Vector3.up);
            direction = forward.normalized * Mathf.Cos(elevation) + Vector3.up * Mathf.Sin(elevation);
        }
        return direction * speed;
    }

    public Vector3 ConstrainHand(Vector3 desired, out bool blocked, Transform releasedVisualException = null)
    {
        blocked = false;
        if (!HasHeldItem || !ThrowFlight.TryShape(heldItem.WorldPrefab, out ThrowShape shape, out _)) return desired;
        Vector3 delta = desired - throwOrigin.position;
        if (Sweep(throwOrigin.position, delta, shape, throwOrigin.rotation, settings.SurfaceSkin, out RaycastHit hit, releasedVisualException))
        {
            blocked = true;
            return throwOrigin.position + delta.normalized * Mathf.Max(0f, hit.distance - settings.SurfaceSkin);
        }
        blocked = OverlapsWorld(desired, shape, throwOrigin.rotation, settings.SurfaceSkin, releasedVisualException) ||
                  OverlapsWorld(throwOrigin.position, shape, throwOrigin.rotation, 0f, releasedVisualException);
        return desired;
    }

    private bool IsWorld(Collider collider, Transform excludedRoot = null) =>
        collider != null && collider.enabled && !collider.isTrigger && !collider.transform.IsChildOf(transform) &&
        (excludedRoot == null || !collider.transform.IsChildOf(excludedRoot));

    private bool OverlapsWorld(Vector3 position, ThrowShape shape, Quaternion rotation, float skin, Transform excludedRoot = null)
    {
        int count = shape.IsBox
            ? Physics.OverlapBoxNonAlloc(position, shape.HalfExtents + Vector3.one * skin, overlaps, rotation, settings.CollisionMask, QueryTriggerInteraction.Ignore)
            : Physics.OverlapSphereNonAlloc(position, shape.Radius + skin, overlaps, settings.CollisionMask, QueryTriggerInteraction.Ignore);
        if (count == overlaps.Length) return true; // 버퍼 포화는 빈 공간이라고 해석하지 않는다.
        for (int i = 0; i < count; i++) if (IsWorld(overlaps[i], excludedRoot)) return true;
        return false;
    }

    public bool Sweep(Vector3 start, Vector3 delta, float radius, out RaycastHit closest, Transform excludedRoot = null)
        => Sweep(start, delta, new ThrowShape {Radius = radius}, Quaternion.identity, 0f, out closest, excludedRoot);

    private bool Sweep(Vector3 start, Vector3 delta, ThrowShape shape, Quaternion rotation, float skin,
        out RaycastHit closest, Transform excludedRoot = null)
    {
        closest = default;
        float length = delta.magnitude;
        if (length < 0.00001f) return false;
        int count = shape.IsBox
            ? Physics.BoxCastNonAlloc(start, shape.HalfExtents + Vector3.one * skin, delta / length, hits, rotation, length, settings.CollisionMask, QueryTriggerInteraction.Ignore)
            : shape.Radius + skin > 0f
            ? Physics.SphereCastNonAlloc(start, shape.Radius + skin, delta / length, hits, length, settings.CollisionMask, QueryTriggerInteraction.Ignore)
            : Physics.RaycastNonAlloc(start, delta / length, hits, length, settings.CollisionMask, QueryTriggerInteraction.Ignore);
        float nearest = float.PositiveInfinity;
        bool found = false;
        for (int i = 0; i < count; i++)
            if (IsWorld(hits[i].collider, excludedRoot) && hits[i].distance < nearest)
            { nearest = hits[i].distance; closest = hits[i]; found = true; }
        if (count == hits.Length && !found) { closest.distance = 0f; return true; }
        return found;
    }

    private void LateUpdate() => RefreshTrajectory(zoom != null && zoom.IsZoomed);

    public void RefreshTrajectory(bool isZoomed)
    {
        if (!isActiveAndEnabled || !isAiming || !HasHeldItem) { ClearPreview(); return; }
        if (!TryGetLaunch(out ThrowLaunch launch))
        {
            ClearPreview();
            IsBlocked = true;
            ShowBlocked();
            return;
        }
        blockedMark.enabled = false;
        landingMarker.enabled = false;
        PreviewContact = PreviewNormal = Vector3.zero;
        Vector3 position = launch.Position, velocity = launch.Velocity;
        float step = Time.fixedDeltaTime; // 표시 샘플 간격으로 물리 적분 간격을 바꾸지 않는다.
        float predictionLength = settings.MaxPreviewDistance;
        float visibleLength = settings.ShowFullTrajectory ? predictionLength :
            Mathf.Min(predictionLength, isZoomed ? settings.TrajectoryZoomedLength : settings.TrajectoryLength);
        float travelled = 0f;
        PreviewHit = false;
        trajectoryPoints.Clear();
        trajectoryPoints.Add(position);
        RaycastHit firstContact = default;
        int steps = Mathf.Clamp(Mathf.CeilToInt(settings.TrajectoryMaxTime / step), 1, 2048);
        for (int i = 0; i < steps; i++)
        {
            Vector3 next = position;
            ThrowFlight.Step(ref next, ref velocity, launch.Gravity, launch.Damping, step);
            Vector3 delta = next - position;
            float remaining = predictionLength - travelled;
            if (remaining <= 0.00001f) break;
            bool predictionCapped = delta.magnitude > remaining;
            if (predictionCapped) { delta = delta.normalized * remaining; next = position + delta; }
            bool hit = Sweep(position, delta, launch.Shape, launch.Rotation, 0f, out RaycastHit contact);
            if (hit) next = position + delta.normalized * contact.distance; // 선은 물체 중심의 길이다.
            float length = Vector3.Distance(position, next);
            if (travelled < visibleLength)
            {
                float fraction = Mathf.Clamp01((visibleLength - travelled) / Mathf.Max(length, 0.00001f));
                trajectoryPoints.Add(Vector3.Lerp(position, next, fraction));
            }
            travelled += length;
            position = next;
            if (hit) { PreviewHit = contact.collider != null; firstContact = contact; break; }
            if (predictionCapped) break; // 물리 예측 한계에는 접촉 표식을 만들지 않는다.
        }
        PreviewEnd = trajectoryPoints[trajectoryPoints.Count - 1];
        if (PreviewHit)
        {
            // SphereCast의 중심 경로 끝과 실제 표면 접촉점을 구분한다.
            Vector3 towardSurface = firstContact.point - position;
            if (towardSurface.sqrMagnitude > 0.000001f && firstContact.collider.Raycast(
                new Ray(position, towardSurface.normalized), out RaycastHit surface, launch.Shape.Reach + 0.05f))
                firstContact = surface;
            PreviewContact = firstContact.point;
            PreviewNormal = firstContact.normal.normalized;
            // 물체 중심은 반지름만큼 먼저 멈춘다. 실제 접촉면까지 잇는 길이도 표시 한도에 포함한다.
            float contactLength = travelled + Vector3.Distance(position, PreviewContact);
            if (PreviewNormal.sqrMagnitude > 0.5f && contactLength <= visibleLength)
            {
                trajectoryPoints[trajectoryPoints.Count - 1] = PreviewContact + PreviewNormal * 0.008f;
                PreviewEnd = trajectoryPoints[trajectoryPoints.Count - 1];
                ShowLandingMarker(firstContact.collider);
            }
        }
        float endOpacity = 0f;
        if (lastOpacity != settings.TrajectoryOpacity || lastFade != settings.FadeStart || lastEndOpacity != endOpacity)
        {
            lineGradient.SetKeys(new[] { new GradientColorKey(new Color(0.65f, 0.9f, 1f), 0f),
                new GradientColorKey(new Color(0.65f, 0.9f, 1f), 1f) },
                new[] {new GradientAlphaKey(settings.TrajectoryOpacity, 0f),
                new GradientAlphaKey(settings.TrajectoryOpacity, settings.FadeStart), new GradientAlphaKey(endOpacity, 1f)});
            trajectoryLine.colorGradient = lineGradient;
            lastOpacity = settings.TrajectoryOpacity; lastFade = settings.FadeStart; lastEndOpacity = endOpacity;
        }
        trajectoryLine.widthMultiplier = settings.TrajectoryWidth;
        trajectoryLine.positionCount = trajectoryPoints.Count;
        for (int i = 0; i < trajectoryPoints.Count; i++) trajectoryLine.SetPosition(i, trajectoryPoints[i]);
        trajectoryLine.enabled = true;
    }

    private void ShowLandingMarker(Collider surface)
    {
        Vector3 normal = PreviewNormal;
        Vector3 tangent = Vector3.Cross(normal, Mathf.Abs(normal.y) < 0.9f ? Vector3.up : Vector3.forward).normalized;
        Vector3 bitangent = Vector3.Cross(normal, tangent);
        float radius = settings.LandingMarkerRadius;
        // 좁은 모서리에서는 원을 줄인다. 빈 공간 위에 떠 있는 원이나 벽을 넘는 원을 그리지 않는다.
        for (int attempt = 0; attempt < 3; attempt++, radius *= 0.5f)
        {
            bool supported = true;
            for (int i = 0; i < markerPoints.Length; i++)
            {
                float angle = i * Mathf.PI * 2f / markerPoints.Length;
                Vector3 point = PreviewContact + (tangent * Mathf.Cos(angle) + bitangent * Mathf.Sin(angle)) * radius;
                if (!surface.Raycast(new Ray(point + normal * 0.1f, -normal), out RaycastHit hit, 0.2f) ||
                    Vector3.Dot(hit.normal, normal) < 0.7f)
                { supported = false; break; }
                markerPoints[i] = hit.point + hit.normal * 0.008f;
            }
            if (!supported) continue;
            landingMarker.widthMultiplier = settings.LandingMarkerWidth;
            landingMarker.positionCount = markerPoints.Length;
            landingMarker.SetPositions(markerPoints);
            landingMarker.enabled = true;
            return;
        }
    }

    private void ShowBlocked()
    {
        if (blockedMark == null) return;
        Vector3 c = throwOrigin.TransformPoint(new Vector3(0f, -0.04f, 0.25f));
        Vector3 x = throwOrigin.right * 0.0035f, y = throwOrigin.up * 0.0035f;
        blockedMark.SetPosition(0, c - x - y); blockedMark.SetPosition(1, c + x + y);
        blockedMark.SetPosition(2, c); blockedMark.SetPosition(3, c - x + y);
        blockedMark.SetPosition(4, c + x - y); blockedMark.enabled = true;
    }

    private void ClearPreview()
    {
        if (trajectoryLine != null) { trajectoryLine.enabled = false; trajectoryLine.positionCount = 0; }
        if (blockedMark != null) blockedMark.enabled = false;
        if (landingMarker != null) landingMarker.enabled = false;
        PreviewHit = false;
        PreviewEnd = PreviewContact = PreviewNormal = Vector3.zero;
    }

    private void OnThrownObjectHit(ThrownObject thrown, Collision collision)
    {
        if (isActiveAndEnabled) Hit?.Invoke(thrown, collision);
    }

    private void OnDisable() { ExitStance(); IsBlocked = false; }
}
