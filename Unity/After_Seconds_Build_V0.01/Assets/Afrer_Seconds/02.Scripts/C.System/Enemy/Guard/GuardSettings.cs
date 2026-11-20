using UnityEngine;

#region 의사코드
// 경비 판단 주기마다 시야각·거리와 자세별 식별 시간을 읽어 감지 속도를 정한다.
// 상태에 맞는 이동 속도와 머무는 시간, 붙잡기·사격 예고 및 재사격 간격을 제공한다.
#endregion

[CreateAssetMenu(menuName = "After Seconds/Guard Settings")]
public sealed class GuardSettings : ScriptableObject
{
    [Min(.02f)] public float decisionInterval = .1f;
    [Min(.01f)] public float sightDistance = 15f;
    [Range(1f, 179f)] public float fieldOfView = 90f;
    [Tooltip("검수용. 경비의 실제 시야와 차폐 경계를 메시로 표시한다.")]
    public bool showDebugSightCone;
    [Min(.01f)] public float identifyStanding = 2.2f, identifyCrouching = 3.5f, forgetExposure = 1f;
    [Min(.1f)] public float eyeHeight = 1.6f;
    public LayerMask sightMask = ~0;
    [Tooltip("발각 후 피격 전 경고와 다음 경고까지의 게임 시간")]
    [Min(.1f)] public float shotWarningTime = 1.4f, shotCooldown = 2.5f;
    [Min(.01f)] public float patrolSpeed = 1.5f, chaseSpeed = 6f;
    [Min(.01f)] public float turnSpeed = 240f, acceleration = 18f;
    [Min(.1f)] public float patrolWait = 2f, stalledTime = 1f;
    [Tooltip("발각 후 마지막으로 본 순간부터 빨간 게이지가 소진될 때까지의 게임 시간")]
    [Min(.1f)] public float searchTime = 6f;
    [Min(.02f)] public float arrivalDistance = .18f;
    [Min(.01f)] public float captureReach = .9f, captureWarningTime = .4f;
}
