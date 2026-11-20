using UnityEngine;

#region 의사코드
// 플레이어가 보는 패널의 용도를 읽어 호출 또는 상행 안내를 표시한다.
// F 입력을 받으면 승강기의 현재 상태와 탑승 위치를 다시 확인하고 한 번만 명령을 보낸다.
#endregion

public sealed class FreightLiftButton : MonoBehaviour, IInteractable
{
    [SerializeField] private FreightLift lift;
    [SerializeField] private bool insideCar;
    public string InteractionPrompt => insideCar ? (lift.UpwardOpen ? "[F] 위층으로 이동" : "상행 잠김 · 승강장으로 나가 층 목표 확인") : "[F] 화물 승강기 호출";
    public int InteractionPriority => 2;
    public bool CanInteract(PlayerInventory actor) => insideCar ? lift.CanBoard(actor) : lift.CanCall;
    public bool Interact(PlayerInventory actor) => insideCar ? lift.RequestRide(actor) : lift.Call();
}
