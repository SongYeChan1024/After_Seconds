using System.Collections;
using UnityEngine;

// 의사코드: 포드 안에 플레이어를 세우고 배식 경비가 열린 배식구로 식판을 밀어 넣는다.
// 카메라와 양손이 식판을 따라간다. 밀려난 실제 식판이 경비 몸에 닿으면 제압과 3초 교환을 예약한다.
// 교환 뒤 포드 안에 남은 경비를 바라보고 조작을 돌려준다. 복도 짝은 발소리를 내며 배식구로 돌아온다.
public sealed class B5MealOpening : MonoBehaviour
{
    [SerializeField] private Transform insideFeet, hatch, corridorPost;
    [SerializeField] private GuardPresenter mealGuard;
    [SerializeField] private WorldItem tray;
    public GuardPresenter MealGuard => mealGuard;
    public Vector3 StartingFeet => insideFeet.position;
    public Vector3 CorridorPost => corridorPost.position;
    public bool Completed { get; private set; }

    private PlayerLook look;
    private PlayerFirstPersonHands hands;
    private PlayerSwap swap;
    private SwapTarget target;
    private ThrownObject flight;
    private Rigidbody dish;
    private Vector3 outside;
    private Transform upperArm, forearm, palm;
    private float guardReach;
    private bool hit;

    // 배식구의 정면은 포드 바깥을 향한다. 손과 식판의 동선은 이 표식을 기준으로 잡는다.
    public void Prepare(PlayerMotor actor)
    {
        var body = actor.GetComponent<CharacterController>();
        Vector3 feetOffset = actor.transform.position - new Vector3(body.bounds.center.x, body.bounds.min.y, body.bounds.center.z);
        body.enabled = false;
        actor.transform.SetPositionAndRotation(insideFeet.position + feetOffset, insideFeet.rotation);
        body.enabled = true;
        outside = hatch.forward;
        mealGuard.transform.rotation = Quaternion.LookRotation(-outside);
        Physics.SyncTransforms();
        look = actor.GetComponent<PlayerLook>();
        hands = actor.GetComponent<PlayerFirstPersonHands>();
        swap = actor.GetComponent<PlayerSwap>();
        target = mealGuard.GetComponent<SwapTarget>();
        dish = tray.GetComponent<Rigidbody>();
        flight = tray.GetComponent<ThrownObject>();
        dish.isKinematic = true;
        dish.position = ServingPosition(0f);
        dish.rotation = hatch.rotation;
        look.SetCinematicPitch(4f);
        var animator = mealGuard.GetComponentInChildren<Animator>();
        if (animator && animator.isHuman)
        {
            upperArm = animator.GetBoneTransform(HumanBodyBones.RightUpperArm);
            forearm = animator.GetBoneTransform(HumanBodyBones.RightLowerArm);
            palm = animator.GetBoneTransform(HumanBodyBones.RightHand);
        }
    }

    private Vector3 ServingPosition(float t)
    {
        return hatch.position + outside * Mathf.Lerp(.66f, -.50f, t) +
               Vector3.up * (.05f + .05f * (1f - t));
    }

    public IEnumerator Play()
    {
        // 경비가 내밀고 잠깐 멈춘 뒤 두 손이 가까운 테두리를 밀어낸다.
        for (float elapsed = 0f; elapsed < 2.4f; elapsed += Time.deltaTime)
        {
            float offer = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(.25f, 1.65f, elapsed));
            guardReach = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0f,.55f,elapsed)) *
                         (1f - Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(1.3f, 1.85f, elapsed)));
            Vector3 point = ServingPosition(offer);
            dish.position = point;
            look.SetCinematicPitch(Mathf.Lerp(4f, 22f, offer));
            look.SetEyeDrop(Mathf.Lerp(.10f, .62f, offer));
            hands.ReachForTray(point - outside * .15f, Mathf.InverseLerp(1.32f, 2f, elapsed));
            yield return null;
        }

        guardReach = 0f;
        flight.Hit += OnImpact;
        target.Relocated += OnSwap;
        try
        {
            dish.position = ServingPosition(1f);
            dish.isKinematic = false;
            dish.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;
            dish.linearVelocity = outside * 4.8f + Vector3.up * .60f;
            flight.Initialize(.35f);
            float launch = Time.time;
            while (!hit && Time.time - launch < 1.25f)
            {
                hands.ReachForTray(ServingPosition(1f) + outside * .20f, 1f - Mathf.InverseLerp(.13f,.50f,Time.time-launch));
                yield return null;
            }
            hands.ReachForTray(Vector3.zero, 0f);
            if (!hit) yield break;
            float impact = Time.time;
            // 보정 대기 역시 같은 예약이다. 실제 교환 또는 대상 소실까지 도입을 이어 간다.
            while (!Completed && swap.HasPending(target))
            {
                look.SetCinematicPitch(Mathf.Lerp(22f, 10f, Mathf.SmoothStep(0f,1f,(Time.time-impact)/.5f)));
                yield return null;
            }
            if (Completed)
            {
                // 같은 1인칭 카메라에서 교환 직후 유리 안에 남은 경비가 보인다.
                swap.transform.rotation = Quaternion.LookRotation(-outside);
                look.SetCinematicPitch(26f);
                for (float t = 0f; t < .45f; t += Time.deltaTime)
                {
                    look.SetEyeDrop(0f);
                    yield return null;
                }
            }
        }
        finally
        {
            flight.Hit -= OnImpact;
            flight.Disarm();
            target.Relocated -= OnSwap;
            hands.ReachForTray(Vector3.zero, 0f);
        }
    }

    private void LateUpdate()
    {
        if (!palm || guardReach <= 0f) return;
        Vector3 grip = dish.position + outside * .14f + Vector3.down * .025f;
        Vector3 reach = Vector3.Lerp(palm.position, grip, guardReach);
        upperArm.rotation = Quaternion.FromToRotation(palm.position - upperArm.position, reach - upperArm.position) * upperArm.rotation;
        forearm.rotation = Quaternion.FromToRotation(palm.position - forearm.position, reach - forearm.position) * forearm.rotation;
    }

    private void OnImpact(ThrownObject source, Collision collision)
    {
        if (hit || collision.collider.GetComponentInParent<SwapTarget>() != target || !swap.ScheduleImpact(source, collision)) return;
        hit = true;
        flight.Disarm();
        var contact = collision.GetContact(0);
        mealGuard.Equipment.TakeHit(mealGuard.Equipment.MaxHP, contact.point, -contact.normal);
        // 부딪힌 식판은 경비 옆으로 튕겨 월드 아이템으로 남는다.
        dish.linearVelocity = hatch.right * 1.8f - outside * .35f;
    }

    private void OnSwap() => Completed = true;

    public void ReturnFromCorridor(GuardPresenter partner, AudioClip footstep)
    {
        partner.Duty.Investigate(hatch.position + outside * 1.05f, 22f);
        if (footstep && !partner.HasFootstepClip) StartCoroutine(ReturnSteps(partner, footstep));
    }

    private static IEnumerator ReturnSteps(GuardPresenter partner, AudioClip clip)
    {
        var sound = partner.gameObject.AddComponent<AudioSource>();
        sound.playOnAwake = false;
        sound.spatialBlend = 1f;
        sound.rolloffMode = AudioRolloffMode.Linear;
        sound.minDistance = 2f;
        sound.maxDistance = 27f;
        Vector3 last = partner.transform.position;
        float distance = .55f;
        while (partner && partner.isActiveAndEnabled && partner.Duty.Investigating)
        {
            Vector3 here = partner.transform.position;
            distance += Vector3.ProjectOnPlane(here - last, Vector3.up).magnitude;
            last = here;
            if (distance >= .80f)
            {
                sound.PlayOneShot(clip, .65f);
                distance = 0f;
            }
            yield return null;
        }
        if (sound) Destroy(sound);
    }
}
