using System;
using UnityEngine;

#region 의사코드
// 생성 시 이 경비가 가진 권총 한 자루를 장착한다. 발사하면 그 인스턴스의 잔탄을 차감한다.
// 근무 시작 때 담당 경로의 보조 장비를 차고, 인계점에서는 다른 근무자와 실제 장비를 교환한다.
// 경비가 쓰러지면 자기 권총과 현재 차고 있는 보조 장비를 양쪽으로 떨어뜨린다.
// 제압 방식과 관계없이 누운 몸을 다음 투척과 조준 사격의 교환 대상으로 남긴다.
#endregion

// 제압 후에도 권총별 잔탄과 보조 장비의 인스턴스를 보존한다.
[DisallowMultipleComponent, RequireComponent(typeof(CharacterController), typeof(SwapTarget))]
public sealed class GuardLoadout : DamageReceiver, IInteractable
{
    [SerializeField, Min(1)] private int maxHP = 1;
    public override int MaxHP => Mathf.Max(1, maxHP);
    [SerializeField] private ItemDefinition carriedItem;
    [SerializeField] private Transform characterVisual;
    [SerializeField, Min(0f)] private float interactionReach = 1.2f;
    private CharacterController body;
    private WorldItem carried;
    private WorldItem dutyItem;
    public bool InteractionBlocked { private get; set; }
    public bool IsDown => CurrentHP == 0;
    public event Action TakenDown;
    private GuardImpactPose impact;
    private bool takingContactHit;

    public void ReactToHit(Vector3 point, Vector3 direction)
    {
        if (IsDown || !characterVisual) return;
        impact ??= new GuardImpactPose(transform, characterVisual);
        impact.Hit(body, point, direction);
    }

    // 피부 충돌체를 추가하지 않고 실제 명중 위치와 방향을 기존 HP 처리에 함께 전달한다.
    public bool TakeHit(int amount, Vector3 point, Vector3 direction)
    {
        if (amount <= 0 || !isActiveAndEnabled || IsDown || Time.timeScale <= 0f) return false;
        ReactToHit(point, direction);
        takingContactHit = true;
        try { return TakeDamage(amount); }
        finally { takingContactHit = false; }
    }

    public void RestoreHitPose() => impact?.Restore();
    public void DrawHitPose() => impact?.DrawLive();

    protected override void Awake()
    {
        base.Awake();
        body = GetComponent<CharacterController>();
        if (!carriedItem || !carriedItem.WorldPrefab) return;
        carried = Instantiate(carriedItem.WorldPrefab, transform).GetComponent<WorldItem>();
        carried.transform.localPosition = new Vector3(.25f,.91f,.04f);
        carried.transform.localRotation = Quaternion.Euler(75f,0f,0f);
        carried.Wear(transform);
    }

    public void EquipDutyItem(ItemDefinition definition)
    {
        if (IsDown || dutyItem || !definition || !definition.WorldPrefab) return;
        var item = Instantiate(definition.WorldPrefab, transform).GetComponent<WorldItem>();
        WearDutyItem(item);
    }

    private void WearDutyItem(WorldItem item)
    {
        dutyItem = item;
        if (!item) return;
        item.transform.SetParent(transform, false);
        item.transform.localPosition = new Vector3(-.24f, .98f, .08f) + postOffset;
        item.transform.localRotation = Quaternion.Euler(80f, 0f, 0f);
        item.Wear(transform);
    }

    public void ExchangeDutyItems(GuardLoadout partner)
    {
        if (!partner || IsDown || partner.IsDown) return;
        var previous = dutyItem;
        WearDutyItem(partner.dutyItem);
        partner.WearDutyItem(previous);
    }

    private Vector3 postOffset;
    public void SetPostOffset(Vector3 offset)
    {
        if ((postOffset - offset).sqrMagnitude < .000001f) return;
        postOffset = offset;
        if (carried) carried.transform.localPosition = new Vector3(.25f, .91f, .04f) + offset;
        if (dutyItem) dutyItem.transform.localPosition = new Vector3(-.24f, .98f, .08f) + offset;
    }

    public bool HasLoadedPistol => carried && carried.Ability is SwapShotAbility shot && shot.RemainingRounds > 0;

    public bool TryFireAt(IDamageable recipient)
    {
        if (IsDown || recipient == null || recipient.CurrentHP == 0 || !carried || !(carried.Ability is SwapShotAbility shot) || !shot.TrySpendRound())
            return false;
        recipient.TakeDamage(1);
        return true;
    }

    public int InteractionPriority => 1;
    public string InteractionPrompt => "[F] 경비 제압";
    public bool CanInteract(PlayerInventory actor) => CanInteract(actor.Body);
    public bool Interact(PlayerInventory actor)
    {
        if (!TryInteract(actor.Body)) return false;
        actor.Tell("경비 제압");
        return true;
    }

    public bool CanInteract(CharacterController player)
    {
        if (!isActiveAndEnabled || !player || !body.enabled || IsDown || InteractionBlocked || !carried) return false;
        var other = player.bounds;
        if (Mathf.Abs(body.bounds.min.y - other.min.y) > .55f) return false;
        Vector3 toward = Vector3.ProjectOnPlane(other.center - body.bounds.center, Vector3.up);
        return Vector3.Dot(transform.forward, toward.normalized) <= -.5f &&
               Vector3.Distance(body.bounds.ClosestPoint(other.center), other.ClosestPoint(body.bounds.center)) <= interactionReach;
    }

    public bool TryInteract(CharacterController player)
    {
        if (!CanInteract(player)) return false;
        ReactToHit(body.bounds.center, transform.position - player.transform.position);
        Fall();
        return true;
    }

    // 피해와 직접 제압은 같은 쓰러짐 처리를 공유한다.
    protected override void OnDamageTaken(int lostHP)
    {
        if (!takingContactHit && characterVisual)
        {
            impact ??= new GuardImpactPose(transform, characterVisual);
            impact.Hit(body, body.bounds.center, transform.forward);
        }
        if (CurrentHP == 0) Fall();
    }

    private void Fall()
    {
        GetComponent<GuardMotor>()?.StandUp();
        var swap = GetComponent<SwapTarget>();
        var direction = swap.UseFallenBody(body, carried, dutyItem, impact?.ImpactDirection ?? transform.forward);
        CurrentHP = 0;
        TakenDown?.Invoke();
        body.enabled = false;
        // 권총이 누운 몸 아래에 묻히지 않도록 허리 바깥쪽으로 떨어뜨린다.
        if (carried) carried.UnholsterToWorld(transform.right * 1.25f);
        if (dutyItem) dutyItem.UnholsterToWorld(-transform.right * 1.25f);
        carried = null;
        dutyItem = null;
        swap.EnableFallenGravity();
        if (impact != null) StartCoroutine(impact.Fall(direction));
    }
}
