using UnityEngine;

#region 의사코드
// 공통 피격 처리가 HP를 줄이면 현재 게임 시각에 둔화 지속 시간을 더해 만료 시각을 정한다.
// 남은 HP를 알리고 실제 감소량을 통지한다. 만료 전에는 이동 배율을 낮추고 이후 원래 속도로 돌아간다.
#endregion

// 플레이어에게 도달한 피격을 한 번만 처리하고, 기존 HUD에 알린다.
[DisallowMultipleComponent, RequireComponent(typeof(PlayerInventory))]
public sealed class PlayerDamageReceiver : DamageReceiver
{
    [SerializeField, Min(1)] private int maxHP = 3;
    public override int MaxHP => Mathf.Max(1, maxHP);
    [SerializeField, Min(0f)] private float slowDuration = 1.25f;
    [SerializeField, Range(.1f, 1f)] private float slowSpeed = .60f;
    private float slowedUntil;
    public float MovementScale => Time.time < slowedUntil ? slowSpeed : 1f;
    private PlayerInventory inventory;
    public event System.Action<int> Damaged;
    protected override void Awake()
    {
        base.Awake();
        inventory = GetComponent<PlayerInventory>();
    }

    protected override void OnDamageTaken(int lostHP)
    {
        slowedUntil = Time.time + slowDuration;
        inventory.Tell($"피격 · HP {CurrentHP}/{MaxHP} · 이동 둔화");
        Damaged?.Invoke(lostHP);
    }
}
