using UnityEngine;

[CreateAssetMenu(menuName = "After Seconds/Guard Settings")]
public sealed class GuardSettings : ScriptableObject
{
    [Min(.02f)] public float decisionInterval = .1f;
    [Min(.01f)] public float sightDistance = 15f;
    [Range(1f, 179f)] public float fieldOfView = 90f;
    [Min(.01f)] public float identifyStanding = 2.2f, identifyCrouching = 3.5f, forgetExposure = 1f;
    [Min(.1f)] public float eyeHeight = 1.6f;
    public LayerMask sightMask = ~0;
    [Min(.01f)] public float patrolSpeed = 1.5f, chaseSpeed = 6f;
    [Min(.01f)] public float turnSpeed = 240f, acceleration = 18f;
    [Min(.1f)] public float patrolWait = 2f, stalledTime = 1f;
    [Tooltip("발각 후 마지막으로 본 순간부터 빨간 게이지가 소진될 때까지의 게임 시간")]
    [Min(.1f)] public float searchTime = 6f;
    [Min(.02f)] public float arrivalDistance = .18f;
    [Min(.01f)] public float captureReach = .9f, captureWarningTime = .4f;
}
