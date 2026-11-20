using UnityEngine;

#region 의사코드
// 선택 중인 권총의 잔탄을 한 발 소모한다. 비었으면 빈 총 안내를 표시한다.
// 조준선의 첫 충돌 대상이 살아 있으면 피해를 준다. 바닥 아이템과 이미 쓰러진 몸도 교환을 예약한다.
#endregion

// 잔탄은 이 권총 인스턴스에 속한다. 사용자에 따라 명중한 대상의 반응과 플레이어의 교환 능력을 연결한다.
public sealed class SwapShotAbility : ItemAbility
{
    private WorldItem item;
    public int RemainingRounds { get; private set; }
    public override string StatusText => RemainingRounds > 0 ? RemainingRounds + "발" : "빈 총";
    public override string ControlHint => RemainingRounds > 0 ? "우클릭 조준 + 좌클릭 발사" : "좌클릭 눌렀다 놓아 던지기";

    private void Awake()
    {
        item = GetComponent<WorldItem>();
        RemainingRounds = item.Definition ? item.Definition.InitialRounds : 0;
    }

    internal bool TrySpendRound()
    {
        if (!item.IsStored || RemainingRounds <= 0) return false;
        RemainingRounds--;
        return true;
    }

    public override bool TryUse(PlayerInventory actor)
    {
        if (actor.Selected != item) return false;
        if (!TrySpendRound()) { actor.Tell("빈 총 · 우클릭을 놓고 던지기"); return false; }
        var eye = actor.Thrower.Origin;
        StealthNoise.Emit(eye.position, 32f, GuardNoise.Gunshot);
        if (actor.Thrower.Sweep(eye.position, eye.forward * item.Definition.SwapShotRange, 0f, out var hit) && hit.collider)
        {
            var recipient = hit.collider.GetComponentInParent<IDamageable>();
            var target = hit.collider.GetComponentInParent<SwapTarget>();
            bool hitAccepted = recipient == null || recipient.CurrentHP == 0 || (recipient is GuardLoadout guard
                ? guard.TakeHit(1, hit.point, eye.forward) : recipient.TakeDamage(1));
            if (hitAccepted && actor.Swap && actor.Swap.ScheduleSightHit(target)) return true;
        }
        actor.Tell(RemainingRounds == 0 ? "빈 총" : "교환 대상 없음");
        return true;
    }
}
