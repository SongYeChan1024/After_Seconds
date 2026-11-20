using UnityEngine;

#region 의사코드
// 줍기 거리·마스크·조준 보조 반경으로 주변 후보를 제한한다.
// 획득 시 슬롯 한도를 확인하고 방출 후 재획득 대기와 안내 표시에는 각 지속 시간을 사용한다.
#endregion

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
