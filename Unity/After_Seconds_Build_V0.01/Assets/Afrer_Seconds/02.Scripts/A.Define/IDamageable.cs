#region 의사코드
// 공격자는 명중한 개체에서 이 계약을 찾는다. 현재 HP와 최대 HP는 읽기만 한다.
// 피해량을 전달하고, 대상이 피해를 받아들였을 때만 명중 후속 처리를 진행한다.
#endregion

// 명중을 받은 쪽이 자신의 상태 변화를 결정한다. 이미 쓰러진 대상은 중복 피격을 거절한다.
public interface IDamageable
{
    int MaxHP { get; }
    int CurrentHP { get; }
    bool TakeDamage(int amount);
}
