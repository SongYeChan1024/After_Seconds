using UnityEngine;

[CreateAssetMenu(
    fileName = "PlayerLookSettings",
    menuName = "After Seconds/Player Look Settings")]
public class PlayerLookSettings : ScriptableObject
{
    [SerializeField, Min(0f)] private float horizontalSensitivity;
    [SerializeField, Min(0f)] private float verticalSensitivity;

    [SerializeField, Range(-89f, 0f)] private float minPitch;
    [SerializeField, Range(0f, 89f)] private float maxPitch;

    public float HorizontalSensitivity => horizontalSensitivity;
    public float VerticalSensitivity => verticalSensitivity;

    public float MinPitch => minPitch;
    public float MaxPitch => maxPitch;
}