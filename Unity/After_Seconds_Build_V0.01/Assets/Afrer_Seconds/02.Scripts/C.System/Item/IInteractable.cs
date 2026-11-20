#region 의사코드
// 플레이어가 바라보는 후보에게 지금 상호작용할 수 있는지 묻는다.
// 우선순위와 거리를 비교해 선택한 후보의 안내를 표시하고 F를 누르면 그 후보의 동작을 한 번 호출한다.
#endregion

// F 입력을 받을 수 있는 월드 개체의 계약. 장식용 Prop에는 구현하지 않는다.
public interface IInteractable
{
    string InteractionPrompt { get; }
    int InteractionPriority { get; }
    bool CanInteract(PlayerInventory actor);
    bool Interact(PlayerInventory actor);
}
