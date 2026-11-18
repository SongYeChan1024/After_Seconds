using System;
using UnityEngine;

#region 의사코드 Ver 0.1 (던져진 물건이 명중을 알린다)

/*
던져진 물건에 붙어서, 무언가에 부딪혔을 때 "명중했다"고 알리는 기능
(이 물건은 "맞았다"는 사실만 알린다. 그 뒤에 무엇을 할지 — 지금은 로그, 나중에는 3초 뒤 교환 예약 —
 는 알림을 듣는 쪽이 정한다. 그래서 이 스크립트는 교환 규칙을 몰라도 된다)

기억해둘 정보:
    명중으로 치는 최소 충돌 빠르기 — minHitSpeed
    명중을 듣고 싶은 쪽이 등록해 두는 알림 — Hit
        (알릴 때 "어느 물건이", "무엇과 어떻게 부딪혔는지"를 함께 넘긴다)

던진 쪽이 준비시킬 때 — Initialize:
    최소 충돌 빠르기를 전달받아 기억한다

무언가에 부딪혔을 때 — OnCollisionEnter (Unity가 불러 준다):
    부딪힌 빠르기가 최소 충돌 빠르기보다 느리다면:
        알리지 않고 끝낸다 (바닥에서 구르는 정도는 명중이 아니다)
    등록된 쪽에 명중을 알린다
        (한 번 던진 물건이 여러 대상에 차례로 맞으면 맞을 때마다 따로 알린다 — 기획서의 연속 명중)

이 물건이 사라질 때 — OnDestroy:
    등록된 알림을 모두 비운다 (사라진 물건이 계속 연결되어 있지 않게)
*/

#endregion
[RequireComponent(typeof(Rigidbody))]
public class ThrownObject : MonoBehaviour
{
    // 명중을 듣고 싶은 쪽이 += 로 등록하는 알림이다.
    // Action<A, B>는 "A와 B를 받는 함수"를 담는 타입이다. 여기서는 (맞힌 물건, 충돌 정보)를 넘긴다.
    // event를 붙이면 밖에서는 등록(+=)과 해제(-=)만 할 수 있고, 알리는 것(Invoke)은 이 클래스만 할 수 있다.
    public event Action<ThrownObject, Collision> Hit;

    private float minHitSpeed; // 이 빠르기보다 느린 충돌은 명중으로 알리지 않는다
    private bool armed;

    // 던진 쪽(PlayerThrow)이 물건을 만든 직후에 불러서 필요한 값을 넘겨 준다.
    public void Initialize(float minimumHitSpeed)
    {
        minHitSpeed = minimumHitSpeed;
        armed = true;
    }

    // 줍거나 조용히 내려놓은 물건은 투척 명중을 발생시키지 않는다.
    public void Disarm() { armed = false; }

    // 이 물건의 충돌체가 다른 충돌체와 부딪힌 순간 Unity가 불러 준다.
    // collision에는 무엇과, 어디서, 얼마나 빠르게 부딪혔는지가 들어 있다.
    private void OnCollisionEnter(Collision collision)
    {
        // relativeVelocity는 두 물체가 서로 다가온 속도다. magnitude는 그 크기(빠르기)다.
        if (!armed || collision.relativeVelocity.magnitude < minHitSpeed) // 투척 상태가 아니거나 느리게 닿았다면
        {
            return; // 명중으로 치지 않는다
        }

        // ?. 는 "등록된 쪽이 하나도 없으면 아무것도 하지 않는다"는 뜻이다.
        Hit?.Invoke(this, collision);
    }

    private void OnDestroy()
    {
        Hit = null; // 사라지는 물건에 걸린 등록을 모두 비운다
    }
}
