using UnityEngine;
using UnityEngine.Rendering;

// 의사코드: 카메라와 별개의 팔 표시만 늦은 프레임에 갱신한다.
// 이동/앉기/확대/준비 상태로 목표 손 위치 → 작은 관성/흔들림 → 벽 검사 → 팔 IK.
// 실제 방출 콜백에서 소지품 표시를 즉시 숨기고, 위/아래 별도 후속 동작 뒤 복귀한다.
// VARCO 클립에서 추출한 손 경로를 1인칭 진폭에 맞추고 IK로 표시한다. 전신 본에는 쓰지 않는다.
[DefaultExecutionOrder(100)]
public class PlayerFirstPersonHands : MonoBehaviour
{
    [SerializeField] private PlayerHandSettings settings;
    [SerializeField] private Transform rigRoot;
    [SerializeField] private Transform rightUpper, rightLower, rightHand;
    [SerializeField] private Transform leftUpper, leftLower, leftHand;
    [SerializeField] private Renderer[] bodyRenderers;
    [SerializeField] private SkinnedMeshRenderer lowerBody;
    [SerializeField] private PlayerHandAnimationSet animations;
    [SerializeField] private Animator bodyAnimator;
    private ShadowCastingMode[] originalShadows;
    private PlayerThrow thrower;
    private PlayerMotor motor;
    private PlayerZoom zoom;
    private CharacterController controller;
    private Transform itemAnchor;
    private GameObject itemVisual;
    private ItemDefinition shownItem;
    private Transform[] bones;
    private Quaternion[] restRotations;
    private Vector3[] restPositions;
    private Vector3 itemLocal, smoothVelocity, sway, previousEuler;
    private float bobPhase, recovery;
    private bool releasedUnderhand;
    private Vector3 releaseLocal;
    private Vector3 leftLocal, leftSmoothVelocity;
    private float gaitPhase, movementWeight, movementVelocity, runWeight, airWeight, landingDip, previousVerticalSpeed;
    private bool wasGrounded;
    private float preparation, recoveryDuration;
    private Vector3 leftReleaseLocal;
    private Vector3 trayGrip;
    private float trayReach;
    // 배식 때 양손을 식판의 가까운 가장자리로 뻗고, 놓은 뒤 평소 손 위치로 섞는다.
    public void ReachForTray(Vector3 position, float weight)
    {
        trayGrip = position;
        trayReach = Mathf.Clamp01(weight);
    }

    public bool Ready => isActiveAndEnabled && itemAnchor != null;
    public bool Obstructed { get; private set; }
    public Vector3 ItemPosition => itemAnchor.position;
    public bool ItemVisible => itemVisual != null && itemVisual.activeSelf;
    public Vector3 LeftHandPosition => leftHand != null ? leftHand.position : transform.position;
    public float MovementWeight => movementWeight;
    public float GaitPhase => gaitPhase;
    public bool LowerBodyVisible => lowerBody != null && lowerBody.enabled;
    public bool UsesAnimationClips => animations != null && animations.HasLocomotion && animations.HasOverhand;
    public bool UsingIronSights => thrower != null && thrower.HeldItem != null && thrower.HeldItem.HasIronSights &&
                                  zoom != null && zoom.IsZoomed && recovery <= 0f && !thrower.IsInThrowStance;
    public string Pose => recovery > 0f ? "Recover" : UsingIronSights ? "IronSights" : thrower.IsAiming ? "Aim" : thrower.IsInThrowStance ? "Prepare" : "Hold";

    private void Awake()
    {
        thrower = GetComponent<PlayerThrow>(); motor = GetComponent<PlayerMotor>();
        zoom = GetComponent<PlayerZoom>(); controller = GetComponent<CharacterController>();
        if (settings == null || rigRoot == null || rightUpper == null || rightLower == null || rightHand == null ||
            leftUpper == null || leftLower == null || leftHand == null || thrower == null)
        { Debug.LogError("1인칭 팔 리그와 설정 참조를 연결해 주세요.", this); enabled = false; return; }
        bones = rigRoot.GetComponentsInChildren<Transform>(true);
        restRotations = new Quaternion[bones.Length]; restPositions = new Vector3[bones.Length];
        for (int i = 0; i < bones.Length; i++)
        { restRotations[i] = bones[i].localRotation; restPositions[i] = bones[i].localPosition; }
        var anchor = new GameObject("HeldItemVisual"); itemAnchor = anchor.transform;
        itemAnchor.SetParent(thrower.Origin, false);
        itemLocal = settings.restingItem; itemAnchor.localPosition = itemLocal;
        leftLocal = settings.leftRestingHand;
        wasGrounded = controller != null && controller.isGrounded;
        originalShadows = new ShadowCastingMode[bodyRenderers.Length];
        for (int i = 0; i < bodyRenderers.Length; i++) if (bodyRenderers[i]) originalShadows[i] = bodyRenderers[i].shadowCastingMode;
        previousEuler = thrower.Origin.eulerAngles;
    }

    private void OnEnable()
    {
        if (rigRoot != null) rigRoot.gameObject.SetActive(true);
        if (lowerBody != null) lowerBody.enabled = true;
        if (originalShadows != null)
            foreach (var renderer in bodyRenderers) if (renderer) renderer.shadowCastingMode = ShadowCastingMode.ShadowsOnly;
    }

    public void OnReleased(bool underhand)
    {
        recoveryDuration = !underhand && animations != null && animations.HasOverhand ? animations.releaseDuration : settings.recoveryTime;
        recovery = recoveryDuration; releasedUnderhand = underhand; releaseLocal = itemLocal; leftReleaseLocal = leftLocal;
        if (itemVisual != null) itemVisual.SetActive(false); // 물리 물체가 생성된 바로 그 프레임이다.
    }

    public void InterruptRecovery() { recovery = preparation = 0f; }
    public void ResetPose()
    {
        recovery = preparation = 0f; smoothVelocity = sway = Vector3.zero;
        leftSmoothVelocity = Vector3.zero;
        movementWeight = movementVelocity = runWeight = airWeight = landingDip = 0f;
        if (settings != null) { itemLocal = settings.restingItem; leftLocal = settings.leftRestingHand; }
        if (itemVisual != null) itemVisual.SetActive(false);
        shownItem = null;
    }

    private void LateUpdate()
    {
        if (!Ready) return;
        Transform eye = thrower.Origin;
        foreach (var renderer in bodyRenderers) if (renderer) renderer.shadowCastingMode = ShadowCastingMode.ShadowsOnly;
        if (shownItem != thrower.HeldItem) BuildItemVisual();
        float dt = Time.deltaTime;
        if (dt <= 0f) return;
        float speed = controller != null ? new Vector2(controller.velocity.x, controller.velocity.z).magnitude : 0f;
        bool grounded = controller != null && controller.isGrounded;
        float zoomScale = zoom != null && zoom.IsZoomed ? settings.zoomMotionScale : 1f;
        bool crouching = motor != null && motor.IsCrouching;
        float motionScale = zoomScale * (thrower.IsAiming ? settings.aimingMotionScale : 1f);
        // 실제 이동 속도로 걸음 박자를 만든다. 벽을 향해 키만 누르면 팔이 달리지 않는다.
        movementWeight = Mathf.SmoothDamp(movementWeight, grounded ? Mathf.Clamp01(speed / 3f) : 0f,
            ref movementVelocity, settings.movementBlendTime, Mathf.Infinity, dt);
        runWeight = Mathf.MoveTowards(runWeight, crouching ? 0f : Mathf.InverseLerp(5f, 7.5f, speed), dt * 6f);
        float stride = Mathf.Lerp(settings.walkStrideLength, settings.runStrideLength, runWeight);
        if (grounded) gaitPhase = (gaitPhase + speed * dt * Mathf.PI * 2f / Mathf.Max(0.5f, stride)) % (Mathf.PI * 2f);
        float wave = Mathf.Sin(gaitPhase);
        Vector3 amplitude = Vector3.Lerp(settings.walkSwing, settings.runSwing, runWeight);
        float gaitScale = movementWeight * motionScale * (crouching ? 0.45f : 1f);
        Vector3 rightSwing = new Vector3(Mathf.Cos(gaitPhase) * amplitude.x, wave * amplitude.y, wave * amplitude.z) * gaitScale;
        Vector3 leftSwing = new Vector3(-Mathf.Cos(gaitPhase) * amplitude.x, -wave * amplitude.y, -wave * amplitude.z) * gaitScale * settings.leftSwingScale;
        if (animations != null && animations.HasLocomotion && bodyAnimator != null && !crouching)
        {
            // 같은 보행 클립을 사용하는 발과 위상을 맞춘다. 실제 속도가 0이면 진폭도 줄인다.
            float phase = Mathf.Repeat(bodyAnimator.GetCurrentAnimatorStateInfo(0).normalizedTime, 1f);
            Vector3 rightPose = Vector3.Lerp(animations.walkRight.Evaluate(phase), animations.runRight.Evaluate(phase), runWeight);
            Vector3 leftPose = Vector3.Lerp(animations.walkLeft.Evaluate(phase), animations.runLeft.Evaluate(phase), runWeight);
            rightSwing = Vector3.Scale(rightPose, amplitude) * gaitScale;
            leftSwing = Vector3.Scale(leftPose, amplitude) * gaitScale * settings.leftSwingScale;
            wave = rightPose.z;
        }
        bobPhase = gaitPhase * 2f;
        Vector3 bob = Vector3.up * Mathf.Sin(bobPhase) * settings.bobAmount * gaitScale;
        if (grounded && !wasGrounded)
            landingDip = Mathf.Min(settings.maxLandingDip, Mathf.Max(0f, -previousVerticalSpeed) * 0.009f);
        landingDip = Mathf.MoveTowards(landingDip, 0f, dt * 0.28f);
        airWeight = Mathf.MoveTowards(airWeight, grounded ? 0f : 1f, dt * 8f);
        Vector3 jumpMotion = (settings.airborneOffset * airWeight - Vector3.up * landingDip) * zoomScale;
        previousVerticalSpeed = controller != null ? controller.velocity.y : 0f;
        wasGrounded = grounded;
        Vector3 angles = eye.eulerAngles;
        Vector3 targetSway = new Vector3(-Mathf.DeltaAngle(previousEuler.y, angles.y), Mathf.DeltaAngle(previousEuler.x, angles.x), 0f)
            * settings.turnSway * zoomScale;
        previousEuler = angles;
        sway = Vector3.Lerp(sway, Vector3.ClampMagnitude(targetSway, settings.maxSway), 1f - Mathf.Exp(-15f * dt));
        Vector3 target = thrower.IsInThrowStance ? thrower.HandOffset : settings.restingItem;
        if (thrower.IsAiming) target += settings.aimHoldOffset;
        if (!thrower.IsInThrowStance) target += settings.sprintOffset * runWeight;
        if (crouching) target += settings.crouchOffset;
        if (zoom != null && zoom.IsZoomed)
        {
            target += settings.zoomOffset;
            if (thrower.IsInThrowStance && thrower.IsUnderhand) target += Vector3.up * settings.underhandZoomLift;
        }
        target += bob + sway + rightSwing + jumpMotion;
        bool clipOverhand = animations != null && animations.HasOverhand && !thrower.IsUnderhand;
        preparation = Mathf.MoveTowards(preparation, thrower.IsAiming && clipOverhand ? 1f : 0f,
            dt / (animations != null ? Mathf.Max(0.05f, animations.prepareDuration) : 0.18f));
        if (clipOverhand && recovery <= 0f) target += animations.prepareRight.Evaluate(preparation);
        Vector3 leftRecovery = Vector3.zero;
        float releasePhase = 1f;
        if (recovery > 0f)
        {
            recovery = Mathf.Max(0f, recovery - dt);
            releasePhase = 1f - recovery / Mathf.Max(0.01f, recoveryDuration);
            if (!releasedUnderhand && animations != null && animations.HasOverhand)
            {
                float blend = Mathf.SmoothStep(0f, 1f, releasePhase);
                target = Vector3.Lerp(releaseLocal, target, blend) + animations.releaseRight.Evaluate(releasePhase);
                leftRecovery = animations.releaseLeft.Evaluate(releasePhase);
            }
            else
            {
                // 낮게 앞으로 민 뒤 복귀한다. 물체는 입력 해제 순간 이미 방출됐다.
                Vector3 followThrough = releasedUnderhand ? settings.underhandFollowThrough : new Vector3(-0.09f, -0.10f, 0.18f);
                float returnBlend = releasedUnderhand ? Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.55f, 1f, releasePhase)) : releasePhase;
                target = Vector3.Lerp(releaseLocal + followThrough * Mathf.Sin(releasePhase * Mathf.PI), target, returnBlend);
            }
        }
        // 소지품 기준점에서 뒤 홈이 시선 중앙에 오도록 손을 옮긴다. 벽 검사는 일반 자세와 공유한다.
        bool sightPose = UsingIronSights;
        if (sightPose) target = thrower.HeldItem.AimedGripLocal;
        itemLocal = Vector3.SmoothDamp(itemLocal, target, ref smoothVelocity, settings.poseSmoothTime, Mathf.Infinity, dt);
        Vector3 leftTargetLocal = settings.leftRestingHand + leftSwing + bob + jumpMotion + sway * 0.6f;
        if (crouching) leftTargetLocal += settings.crouchOffset;
        if (thrower.IsInThrowStance) leftTargetLocal += new Vector3(0.025f, 0.025f, 0.025f);
        if (zoom != null && zoom.IsZoomed)
            leftTargetLocal += new Vector3(-settings.zoomOffset.x, settings.zoomOffset.y, settings.zoomOffset.z);
        if (clipOverhand && recovery <= 0f) leftTargetLocal += animations.prepareLeft.Evaluate(preparation);
        if (recovery > 0f && !releasedUnderhand && animations != null && animations.HasOverhand)
            leftTargetLocal = Vector3.Lerp(leftReleaseLocal, leftTargetLocal, Mathf.SmoothStep(0f, 1f, releasePhase)) + leftRecovery;
        if (sightPose) leftTargetLocal = target + new Vector3(-0.070f, -0.046f, -0.038f);
        leftLocal = Vector3.SmoothDamp(leftLocal, leftTargetLocal, ref leftSmoothVelocity, settings.poseSmoothTime, Mathf.Infinity, dt);
        // 방금 놓은 공이 손 후속 동작을 가려 양팔이 사라지지 않게 한다. 실제 투척 검사는 예외 없이 유지한다.
        Transform releasedVisualException = recovery > 0f && thrower.LastThrown != null ? thrower.LastThrown.transform : null;
        Vector3 gripOffset = thrower.HeldItem != null ? eye.rotation * thrower.HeldItem.GripOffset : Vector3.zero;
        Vector3 safe = thrower.ConstrainHand(eye.TransformPoint(itemLocal) - gripOffset, out bool blocked, releasedVisualException);
        Obstructed = blocked;
        itemAnchor.position = safe; itemAnchor.rotation = eye.rotation;
        // 손까지의 공간이 막히면 표시를 숨긴다. 별도의 시작 겹침/구체 이동 검사도 발사를 거절한다.
        bool visible = !blocked && (safe - eye.position).magnitude > 0.18f;
        rigRoot.gameObject.SetActive(visible);
        if (lowerBody != null) lowerBody.enabled = true; // 하체는 카메라의 피치 대신 기존 전신 애니메이션을 따른다.
        if (itemVisual != null) itemVisual.SetActive(visible && recovery <= 0f && thrower.HasHeldItem);
        if (!visible) return;
        for (int i = 0; i < bones.Length; i++)
        { bones[i].localRotation = restRotations[i]; bones[i].localPosition = restPositions[i]; }
        Vector3 grip = safe + gripOffset;
        Vector3 wrist = grip - eye.TransformVector(settings.palmToItem);
        wrist = Vector3.Lerp(wrist, trayGrip + eye.right * .16f, trayReach);
        SolveArm(rightUpper, rightLower, rightHand, eye.TransformPoint(settings.rightShoulder), wrist,
            eye.TransformPoint(new Vector3(0.38f, -0.38f, 0.12f)));
        Vector3 leftTarget = Vector3.Lerp(eye.TransformPoint(leftLocal), trayGrip - eye.right * .16f, trayReach);
        SolveArm(leftUpper, leftLower, leftHand, eye.TransformPoint(settings.leftShoulder), leftTarget,
            eye.TransformPoint(new Vector3(-0.38f, -0.38f, 0.12f)));
        rightHand.rotation = Quaternion.AngleAxis(wave * 9f * gaitScale, eye.forward) * rightHand.rotation;
        leftHand.rotation = Quaternion.AngleAxis(-wave * 9f * gaitScale, eye.forward) * leftHand.rotation;
        // 손가락 포즈는 임시다. 손끝을 구체 중심 주위로 굽혀서 소지품과 연결한다.
        if (recovery <= 0f && thrower.HasHeldItem) CurlFingers(rightHand, grip);
        Vector3 leftPalmTarget = sightPose ? grip - eye.right * .014f - eye.up * .012f
                                          : leftTarget + eye.forward * .07f - eye.up * .025f;
        CurlFingers(leftHand, leftPalmTarget, sightPose ? .50f : .30f);
    }

    private static void SolveArm(Transform upper, Transform lower, Transform hand, Vector3 shoulder, Vector3 target, Vector3 hint)
    {
        float a = Vector3.Distance(upper.position, lower.position), b = Vector3.Distance(lower.position, hand.position);
        upper.position = shoulder;
        Vector3 toTarget = target - shoulder;
        float distance = Mathf.Clamp(toTarget.magnitude, Mathf.Abs(a - b) + 0.001f, a + b - 0.001f);
        Vector3 direction = toTarget.normalized;
        Vector3 bend = Vector3.ProjectOnPlane(hint - shoulder, direction).normalized;
        float along = (a * a - b * b + distance * distance) / (2f * distance);
        Vector3 elbow = shoulder + direction * along + bend * Mathf.Sqrt(Mathf.Max(0f, a * a - along * along));
        upper.rotation = Quaternion.FromToRotation(lower.position - upper.position, elbow - shoulder) * upper.rotation;
        lower.rotation = Quaternion.FromToRotation(hand.position - lower.position, target - lower.position) * lower.rotation;
    }

    private static void CurlFingers(Transform hand, Vector3 center, float amount = 0.55f)
    {
        foreach (Transform finger in hand)
        {
            Transform joint = finger;
            for (int i = 0; i < 3 && joint.childCount > 0; i++)
            {
                Transform next = joint.GetChild(0);
                Vector3 toward = center - joint.position;
                if (toward.sqrMagnitude > 0.00001f)
                    joint.rotation = Quaternion.Slerp(joint.rotation,
                        Quaternion.FromToRotation(next.position - joint.position, toward) * joint.rotation, amount);
                joint = next;
            }
        }
    }

    private void BuildItemVisual()
    {
        if (itemVisual != null) { itemVisual.SetActive(false); Destroy(itemVisual); }
        shownItem = thrower.HeldItem;
        if (shownItem == null || shownItem.WorldPrefab == null) return;
        itemVisual = new GameObject("Held_" + shownItem.DisplayName);
        itemVisual.transform.SetParent(itemAnchor, false);
        Transform source = shownItem.WorldPrefab.transform;
        // 렌더링만 복사한다. 소지품 표시에는 물리/ThrownObject/Collider가 생기지 않는다.
        foreach (var filter in source.GetComponentsInChildren<MeshFilter>())
        {
            var renderer = filter.GetComponent<MeshRenderer>();
            if (renderer == null) continue;
            var go = new GameObject(filter.name); go.transform.SetParent(itemVisual.transform, false);
            go.transform.localPosition = Vector3.Scale(source.InverseTransformPoint(filter.transform.position), source.localScale);
            go.transform.localRotation = Quaternion.Inverse(source.rotation) * filter.transform.rotation;
            go.transform.localScale = filter.transform.lossyScale;
            go.AddComponent<MeshFilter>().sharedMesh = filter.sharedMesh;
            var copy = go.AddComponent<MeshRenderer>(); copy.sharedMaterials = renderer.sharedMaterials;
            copy.shadowCastingMode = ShadowCastingMode.Off;
        }
    }

    private void OnDisable()
    {
        if (thrower != null) thrower.CancelAim();
        if (rigRoot != null) rigRoot.gameObject.SetActive(false);
        if (lowerBody != null) lowerBody.enabled = false;
        if (itemVisual != null) itemVisual.SetActive(false);
        recovery = preparation = 0f; Obstructed = false;
        if (originalShadows != null)
            for (int i = 0; i < bodyRenderers.Length; i++) if (bodyRenderers[i]) bodyRenderers[i].shadowCastingMode = originalShadows[i];
    }
}
