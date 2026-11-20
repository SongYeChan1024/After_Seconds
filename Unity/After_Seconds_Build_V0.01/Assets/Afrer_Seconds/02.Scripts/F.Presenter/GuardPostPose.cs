using UnityEngine;

// 의사코드: 애니메이션의 원래 자세를 기억한다. 착석 동안 골반을 좌판에 맞추고 무릎과 팔꿈치를 굽히고 고개를 돌린다.
// 서서 순찰할 때는 다음 코너를 향해 머리가 먼저 돌아가고 가슴이 살짝 따른다.
// 다음 애니메이션 평가 전에 원래 뼈 자세를 돌려준다. 시야 판정도 같은 머리뼈의 눈을 사용한다.
internal sealed class GuardPostPose
{
    private readonly Transform hips, head, chest;
    private readonly Transform[] limbs = new Transform[12];
    private readonly Quaternion[] localLimbs = new Quaternion[12];
    private Vector3 localHips;
    private Quaternion localHead;
    private bool applied;
    private float blend;
    private float lookYaw;
    private bool looking;
    private Quaternion previousChest, previousHead;

    public GuardPostPose(Animator animator)
    {
        if (!animator || !animator.isHuman) return;
        hips = animator.GetBoneTransform(HumanBodyBones.Hips);
        head = animator.GetBoneTransform(HumanBodyBones.Head);
        chest = animator.GetBoneTransform(HumanBodyBones.Chest);
        var bones = new[] { HumanBodyBones.LeftUpperLeg, HumanBodyBones.LeftLowerLeg, HumanBodyBones.LeftFoot,
            HumanBodyBones.RightUpperLeg, HumanBodyBones.RightLowerLeg, HumanBodyBones.RightFoot,
            HumanBodyBones.LeftUpperArm, HumanBodyBones.LeftLowerArm, HumanBodyBones.LeftHand,
            HumanBodyBones.RightUpperArm, HumanBodyBones.RightLowerArm, HumanBodyBones.RightHand };
        for (int i = 0; i < bones.Length; i++)
        {
            limbs[i] = animator.GetBoneTransform(bones[i]);
            if (!limbs[i]) { hips = null; return; }
        }
    }

    public void Restore()
    {
        if (looking)
        {
            if (chest) chest.localRotation = previousChest;
            head.localRotation = previousHead;
            looking = false;
        }
        if (!applied) return;
        hips.localPosition = localHips;
        head.localRotation = localHead;
        for (int i = 0; i < limbs.Length; i++) limbs[i].localRotation = localLimbs[i];
        applied = false;
    }

    public void LookAhead(Transform actor, Vector3 direction)
    {
        if (!head || blend > 0f) { lookYaw = 0f; return; }
        float target = direction.sqrMagnitude > .0001f ?
            Mathf.Clamp(Vector3.SignedAngle(actor.forward, direction, Vector3.up), -32f, 32f) : 0f;
        lookYaw = Mathf.MoveTowards(lookYaw, target, 280f * Time.deltaTime);
        if (Mathf.Abs(lookYaw) < .01f) return;
        previousHead = head.localRotation;
        if (chest)
        {
            previousChest = chest.localRotation;
            chest.rotation = Quaternion.AngleAxis(lookYaw * .22f, Vector3.up) * chest.rotation;
        }
        head.rotation = Quaternion.AngleAxis(chest ? lookYaw * .78f : lookYaw, Vector3.up) * head.rotation;
        looking = true;
    }

    public Vector3 Draw(Transform actor, GuardDuty duty, bool sitting)
    {
        blend = Mathf.MoveTowards(blend, sitting ? 1f : 0f, Time.deltaTime * 3.5f);
        if (!hips || !head || blend <= 0f || !duty) return Vector3.zero;
        localHips = hips.localPosition;
        localHead = head.localRotation;
        for (int i = 0; i < limbs.Length; i++) localLimbs[i] = limbs[i].localRotation;
        applied = true;
        Vector3 shift = Vector3.ClampMagnitude(duty.SeatFeet + Vector3.up * .57f - hips.position, 1.8f) * blend;
        hips.position += shift;
        for (int i = 0; i < 6; i += 3)
        {
            var thigh = limbs[i]; var shin = limbs[i + 1]; var foot = limbs[i + 2];
            Quaternion footRotation = foot.rotation;
            TurnBone(thigh, shin, actor.forward - Vector3.up * .14f);
            TurnBone(shin, foot, Vector3.down - actor.forward * .09f);
            foot.rotation = Quaternion.Slerp(foot.rotation, footRotation, blend);
        }
        for (int i = 6; i < limbs.Length; i += 3)
        {
            Vector3 outward = i == 6 ? -actor.right : actor.right;
            TurnBone(limbs[i], limbs[i + 1], Vector3.down + actor.forward * .24f + outward * .16f);
            TurnBone(limbs[i + 1], limbs[i + 2], actor.forward - Vector3.up * .23f - outward * .28f);
        }
        head.rotation = Quaternion.AngleAxis(duty.ScanAngle * blend, Vector3.up) * head.rotation;
        return shift;
    }

    private void TurnBone(Transform bone, Transform end, Vector3 direction)
    {
        var target = Quaternion.FromToRotation(end.position - bone.position, direction) * bone.rotation;
        bone.rotation = Quaternion.Slerp(bone.rotation, target, blend);
    }
}
