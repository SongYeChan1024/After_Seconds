using UnityEngine;

[CreateAssetMenu(fileName = "PlayerMotorSettings", menuName = "After Seconds/Player Motor Settings")]
public class PlayerMotorSettings : ScriptableObject
{
    [SerializeField, Min(0f)] private float moveSpeed;
    [SerializeField, Min(0f)] private float gravity;

    [Tooltip("접지 유지를 위한 하강 속도입니다. 초기 테스트용 가안입니다.")]
    [SerializeField] private float groundedVerticalSpeed;

    public float MoveSpeed => moveSpeed;
    public float GravityAcceleration => -gravity;
    public float GroundedVerticalSpeed => groundedVerticalSpeed;
}
