using UnityEngine;

#region 의사코드
// 생성된 인스턴스의 현재 HP를 최대치로 채운다.
// 정지 중이거나 이미 쓰러졌거나 피해량이 0 이하이면 거절한다. 남은 HP만큼만 차감하고 실제 감소량을 전달한다.
#endregion

// HP는 인스턴스마다 유지한다. 새 시도를 시작해서 새로 생성될 때만 최대치로 초기화한다.
public abstract class DamageReceiver : MonoBehaviour, IDamageable
{
    public abstract int MaxHP { get; }
    public int CurrentHP { get; protected set; }

    protected virtual void Awake() => CurrentHP = MaxHP;

    public bool TakeDamage(int amount)
    {
        if (amount <= 0 || CurrentHP == 0 || !isActiveAndEnabled || Time.timeScale <= 0f) return false;
        int lostHP = Mathf.Min(amount, CurrentHP);
        CurrentHP -= lostHP;
        OnDamageTaken(lostHP);
        return true;
    }

    protected abstract void OnDamageTaken(int lostHP);
}
