using UnityEngine;

public class PlayerAnimationSystem : MonoBehaviour
{
    #region 의사코드

    /*
    플레이어의 이동 애니메이션 상태를 전달하는 기능

    기억해둘 정보:
        새 V0.3 모델의 Animator 참조 — animator

    초기화할 때 — Awake:
        인스펙터에 Animator가 연결되어 있지 않다면:
            오류를 알린다
            이 컴포넌트를 비활성화한다
            초기화를 종료한다

        Animator의 "IsMoving"을 false로 초기화한다

    이동 상태를 전달받으면 — isMove:
        이 컴포넌트나 게임 오브젝트가 비활성화 상태라면:
            이번 요청 처리를 종료한다

        전달받은 이동 여부를
        Animator의 "IsMoving" 값으로 설정한다

    이 컴포넌트가 비활성화되면 — OnDisable:
        Animator가 연결되어 있다면:
            "IsMoving"을 false로 초기화한다
    */

    #endregion
    [SerializeField] private Animator animator; // 애니메이터 컴포넌트 참조

    private void Awake() //어웨이크
    {
        if (animator == null) //애니메이터가 없으면
        {
            animator = GetComponent<Animator>(); // 같은 오브젝트의 컴포넌트에서 Animator를 찾는다
                                                 // 근데 자식 오브젝트라서 못찾긴 한다
        }

        if (animator == null) // 그래도 애니메이터가 없으면
        {
            Debug.LogError("플레이어에 Animator 컴포넌트를 연결해야 합니다."); // 오류를 알림
            enabled = false; // 비활성화
            return; // 종료
        }
        animator.SetBool("IsMoving", false); // 애니메이터의 "IsMoving"을 false로 초기화
    }

    public void isMove(bool isMoving) // 키입력이 되서 이동 상태를 전달 받으면 실행되는 함수
    {
        if (!isActiveAndEnabled) // 이 컴포넌트나 게임 오브젝트가 비활성화 상태라면
        {
            return; // 이번 요청 처리를 종료
        }
        animator.SetBool("IsMoving", isMoving); // 전달받은 이동 여부를 Animator의 "IsMoving" 값으로 설정
    }

    private void OnDisable() // 이 컴포넌트가 비활성화되면
    {
        if (animator != null) // Animator가 연결되어 있다면
        {
            animator.SetBool("IsMoving", false); // "IsMoving"을 false로 초기화
        }
    }

}
