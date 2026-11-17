using UnityEngine;

[CreateAssetMenu(fileName = "PlayerInventorySettings", menuName = "After Seconds/Player Inventory Settings")]
public class PlayerInventorySettings : ScriptableObject
{
    [Min(1)] public int capacity = 5;
    [Min(0.1f)] public float pickupDistance = 2.2f;
    [Min(0f)] public float aimAssistRadius = 0.08f;
    [Min(0f)] public float pickupDelay = 0.25f;
    [Min(0.1f)] public float messageDuration = 1.5f;
    public LayerMask pickupMask = ~0;
}
