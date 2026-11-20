using UnityEngine;

#region 의사코드
// 현재 층의 레버·인계표·승인대 중 지금 쓸 수 있는 설비만 상호작용 후보로 올린다.
// 기존 F 입력으로 해당 단계의 처리를 요청한다.
#endregion
public sealed class EscapeStation : MonoBehaviour, IInteractable
{
    [SerializeField] private FloorExperience room;
    [SerializeField] private bool second;
    public string InteractionPrompt => room.ActionLabel(second);
    public int InteractionPriority => 2;
    public bool CanInteract(PlayerInventory actor) => actor && room.CanOperate(second);
    public bool Interact(PlayerInventory actor) => room.Operate(second, actor);
}
