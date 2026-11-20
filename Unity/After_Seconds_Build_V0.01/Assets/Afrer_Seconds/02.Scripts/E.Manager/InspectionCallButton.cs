using UnityEngine;

// 진단실 단말의 F 입력으로 관제석에 설비 점검을 요청한다.
// 현재 앉아 있는 담당이 관제실 점검 위치까지 걸어간다. 복귀와 CCTV 무전은 기존 근무 규칙을 따른다.
public sealed class InspectionCallButton : MonoBehaviour, IInteractable
{
    [SerializeField] private SurveillanceCamera surveillance;
    [SerializeField] private Vector3 inspectionPoint;

    public string InteractionPrompt => "[F] N01 관제 설비 점검 요청";
    public int InteractionPriority => 2;

    public bool CanInteract(PlayerInventory actor) =>
        actor && surveillance && surveillance.isActiveAndEnabled && Time.timeScale > 0f;

    public bool Interact(PlayerInventory actor)
    {
        if (!CanInteract(actor)) return false;
        var guard = surveillance.OnDutyOperator;
        if (guard)
        {
            guard.Duty.Investigate(inspectionPoint, 18f);
            actor.Tell("N01 관제 · 점검 요청 접수");
        }
        else actor.Tell("N01 관제 · 응답 없음");
        return true;
    }
}
