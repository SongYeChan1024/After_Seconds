using System.Collections;
using UnityEngine;

// 의사코드: 캡슐의 실제 충돌 높이와 좌우 위치로 피격 부위를 고른다.
// 살아 있으면 현재 순찰 자세에 짧은 반동을 더했다가 돌려준다.
// 제압되면 그 순간의 자세를 고정하고 피격 → 무릎 꺾임 → 바닥 접촉 → 정착을 로컬 좌표에서 이어 간다.
internal sealed class GuardImpactPose
{
    private enum Region { Head, Chest, LeftArm, RightArm, LeftLeg, RightLeg }
    private enum Joint { Chest, Head, LeftArm, LeftElbow, RightArm, RightElbow, LeftThigh, LeftShin, RightThigh, RightShin }
    private static readonly HumanBodyBones[] Map =
    {
        HumanBodyBones.Spine, HumanBodyBones.Head, HumanBodyBones.LeftUpperArm, HumanBodyBones.LeftLowerArm,
        HumanBodyBones.RightUpperArm, HumanBodyBones.RightLowerArm, HumanBodyBones.LeftUpperLeg,
        HumanBodyBones.LeftLowerLeg, HumanBodyBones.RightUpperLeg, HumanBodyBones.RightLowerLeg
    };
    private readonly Transform actor, visual;
    private readonly Animator animator;
    private readonly Transform leftFoot, rightFoot, leftHand, rightHand;
    private readonly Transform[] bones = new Transform[Map.Length];
    private readonly Quaternion[] basePose = new Quaternion[Map.Length];
    private Region region = Region.Chest;
    private Vector3 recoil = Vector3.forward;
    private float hitAt = float.NegativeInfinity;
    private bool applied;
    internal Vector3 ImpactDirection => actor.TransformDirection(recoil);

    internal GuardImpactPose(Transform actor, Transform visual)
    {
        this.actor = actor;
        this.visual = visual;
        animator = visual ? visual.GetComponent<Animator>() : null;
        if (!animator || !animator.isHuman) return;
        for (int i = 0; i < Map.Length; i++) bones[i] = animator.GetBoneTransform(Map[i]);
        leftFoot = animator.GetBoneTransform(HumanBodyBones.LeftFoot);
        rightFoot = animator.GetBoneTransform(HumanBodyBones.RightFoot);
        leftHand = animator.GetBoneTransform(HumanBodyBones.LeftHand);
        rightHand = animator.GetBoneTransform(HumanBodyBones.RightHand);
    }

    internal void Hit(CharacterController body, Vector3 point, Vector3 direction)
    {
        var bounds = body.bounds;
        float height = Mathf.InverseLerp(bounds.min.y, bounds.max.y, point.y);
        float side = Vector3.Dot(point - bounds.center, actor.right);
        if (height > .82f) region = Region.Head;
        else if (height < .48f) region = side < 0f ? Region.LeftLeg : Region.RightLeg;
        else if (height > .50f && Mathf.Abs(side) > body.radius * .55f) region = side < 0f ? Region.LeftArm : Region.RightArm;
        else region = Region.Chest;
        recoil = Vector3.ProjectOnPlane(actor.InverseTransformDirection(direction), Vector3.up).normalized;
        if (recoil.sqrMagnitude < .01f) recoil = Vector3.forward;
        hitAt = Time.time;
    }

    private void Capture()
    {
        for (int i = 0; i < bones.Length; i++) if (bones[i]) basePose[i] = bones[i].localRotation;
    }

    internal void Restore()
    {
        if (!applied) return;
        ResetBones();
        applied = false;
    }

    private void ResetBones()
    {
        for (int i = 0; i < bones.Length; i++) if (bones[i]) bones[i].localRotation = basePose[i];
    }

    internal void DrawLive()
    {
        float t = Time.time - hitAt;
        if (t < 0f || t >= .38f) return;
        Capture();
        applied = true;
        float pulse = Ramp(t, 0f, .075f) * (1f - Ramp(t, .09f, .38f));
        DrawHit(pulse);
    }

    private static float Ramp(float t, float a, float b) => Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(a,b,t));

    private void Bend(Joint joint, Vector3 localAxis, float degrees)
    {
        var bone = bones[(int)joint];
        if (bone) bone.rotation = Quaternion.AngleAxis(degrees, visual.TransformDirection(localAxis)) * bone.rotation;
    }

    private void DrawHit(float weight)
    {
        Vector3 axis = Vector3.Cross(Vector3.up, recoil);
        Bend(Joint.Chest, axis, weight * (region == Region.Chest ? 21f : 7f));
        switch (region)
        {
            case Region.Head:
                Bend(Joint.Head, axis, weight * 26f);
                break;
            case Region.LeftArm: case Region.RightArm:
                bool left = region == Region.LeftArm;
                Bend(left ? Joint.LeftArm : Joint.RightArm, axis + Vector3.forward * (left ? -.5f : .5f), weight * 31f);
                Bend(left ? Joint.LeftElbow : Joint.RightElbow, Vector3.right, -weight * 28f);
                break;
            case Region.LeftLeg: case Region.RightLeg:
                bool leftLeg = region == Region.LeftLeg;
                Bend(leftLeg ? Joint.LeftThigh : Joint.RightThigh, Vector3.right, -weight * 23f);
                Bend(leftLeg ? Joint.LeftShin : Joint.RightShin, Vector3.right, weight * 40f);
                break;
            default:
                Bend(Joint.Head, axis, -weight * 9f);
                Bend(Joint.LeftArm, Vector3.right, -weight * 13f);
                Bend(Joint.RightArm, Vector3.right, -weight * 17f);
                break;
        }
    }

    private void SettleArm(Joint arm, Joint elbow, Transform hand, Vector3 fall, float side, float blend)
    {
        if (!hand || blend <= 0f) return;
        Vector3 across = Vector3.Cross(Vector3.up, fall);
        // 머리 쪽으로 들린 팔이 바닥에 닿은 뒤 팔꿈치와 손목 순서로 가라앉는다.
        // 실제 어깨 배치를 사용하므로 앞·뒤·옆으로 넘어져도 양팔이 교차하지 않는다.
        var upper = bones[(int)arm];
        var lower = bones[(int)elbow];
        if (!upper || !lower) return;
        var chest = bones[(int)Joint.Chest];
        float signed = chest ? Vector3.Dot(upper.position - chest.position, across) : side;
        Vector3 outward = across * (Mathf.Abs(signed) > .025f ? Mathf.Sign(signed) : side);
        AimAtGround(upper, lower, outward * .85f - fall * .5f, actor.position.y + .10f, blend);
        AimAtGround(lower, hand, outward * .45f - fall, actor.position.y + .075f, blend);
    }

    private static void AimAtGround(Transform joint, Transform tip, Vector3 horizontal, float height, float blend)
    {
        Vector3 segment = tip.position - joint.position;
        float length = segment.magnitude;
        if (length < .001f) return;
        float y = Mathf.Clamp(height - joint.position.y, -length * .95f, length * .95f);
        Vector3 desired = horizontal.normalized * Mathf.Sqrt(length * length - y * y) + Vector3.up * y;
        var goal = Quaternion.FromToRotation(segment, desired) * joint.rotation;
        joint.rotation = Quaternion.Slerp(joint.rotation, goal, blend);
    }

    internal IEnumerator Fall(Vector3 worldDirection)
    {
        if (!visual) yield break;
        if (animator) animator.enabled = false;
        applied = false;
        Capture();
        var startPosition = visual.localPosition;
        var startRotation = visual.localRotation;
        Vector3 localDirection = visual.parent.InverseTransformDirection(worldDirection).normalized;
        Vector3 axis = Vector3.Cross(Vector3.up, localDirection);
        float elapsed = 0f;
        while (true)
        {
            float fold = Ramp(elapsed, .09f, .46f);
            float fall = Ramp(elapsed, .16f, .80f);
            float settle = Ramp(elapsed, .74f, .98f);
            float kick = Ramp(elapsed, 0f, .09f) * (1f - Ramp(elapsed, .14f, .48f));
            visual.localRotation = Quaternion.AngleAxis(fall * 94f - settle * 4f, axis) * startRotation;
            visual.localPosition = startPosition + Vector3.up * (.20f * fall - .10f * fold * (1f - fall));
            ResetBones();
            DrawHit(kick);
            float knee = fold * (1f - .78f * settle);
            bool left = region == Region.LeftLeg || region == Region.LeftArm;
            Bend(Joint.LeftThigh, Vector3.right, -knee * (left ? 41f : 28f));
            Bend(Joint.RightThigh, Vector3.right, -knee * (left ? 28f : 41f));
            Bend(Joint.LeftShin, Vector3.right, knee * (left ? 72f : 53f));
            Bend(Joint.RightShin, Vector3.right, knee * (left ? 53f : 72f));
            Bend(Joint.Chest, Vector3.right, 13f * fold * (1f - .80f * settle));
            Bend(Joint.LeftArm, Vector3.forward, -22f * fold);
            Bend(Joint.RightArm, Vector3.forward, 30f * fold);
            Bend(Joint.LeftElbow, Vector3.right, -18f * fold);
            Bend(Joint.RightElbow, Vector3.right, -30f * fold);
            if (leftFoot && rightFoot)
            {
                // 무릎이 먼저 꺾일 때 발이 떠오르는 양만큼 무게중심을 내린다.
                float ankle = Mathf.Min(leftFoot.position.y, rightFoot.position.y);
                float plant = Mathf.Clamp(actor.position.y + .085f - ankle, -.38f, .16f);
                visual.position += Vector3.up * plant * fold * (1f - Ramp(elapsed, .46f, .77f));
            }
            float rest = Ramp(elapsed, .57f, .96f);
            SettleArm(Joint.LeftArm, Joint.LeftElbow, leftHand, worldDirection, -1f, rest);
            SettleArm(Joint.RightArm, Joint.RightElbow, rightHand, worldDirection, 1f, rest);
            Bend(Joint.Head, Vector3.up, (left ? -12f : 12f) * rest);
            if (elapsed >= .98f) yield break;
            yield return null;
            elapsed += Time.deltaTime;
        }
    }
}
