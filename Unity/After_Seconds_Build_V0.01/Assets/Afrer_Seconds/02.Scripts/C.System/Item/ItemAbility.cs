using UnityEngine;

#region 의사코드
// 손에 든 아이템의 능력이 제공하는 상태와 입력 안내를 읽는다.
// 사용 입력이 들어오면 실제 효과와 성공 여부는 해당 아이템의 구현에서 결정한다.
#endregion

// 개별 Item 프리팹에 붙이는 손 사용 동작. 집기와 투척은 능력 유무와 별개다.
[DisallowMultipleComponent, RequireComponent(typeof(WorldItem))]
public abstract class ItemAbility : MonoBehaviour
{
    public virtual string StatusText => "";
    public virtual string ControlHint => "우클릭 유지 + 좌클릭 사용";
    public abstract bool TryUse(PlayerInventory actor);
}
