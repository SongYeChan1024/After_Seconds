using UnityEngine;
using UnityEngine.InputSystem;

#region 의사코드

/*
플레이어 이동 입력을 읽는 시스템 (퍼블릭 클래스 플레이어 인풋 시스템)

기억해둘 정보:
    이동 입력 액션의 참조 (프라이빗 인풋 액션 = 무브액션)

초기화할 때: (프라이빗 보이드 어웨이크)
    프로젝트 입력 설정에서 "Player/Move" 액션을 찾는다 (무브액션 = 인풋시스템.액션즈.파인드액션(플레이어/이동, 
    액션을 찾지 못했다면: (쓰로우이프낫파운드)

        설정 오류를 알리고 초기화를 중단한다(트루)

    찾은 액션의 참조를 보관한다(퍼블릭 벡터2 리드무브함수)

이동 입력값을 요청받으면: (무브액션.)
    보관한 액션에서 현재 입력값을 읽는다(리드밸류<Vector2>())
    읽은 값을 2차원 벡터로 반환한다 (리턴)
*/

#endregion
public class PlayerInputSystem : MonoBehaviour // 플레이어의 이동 입력을 처리하는 시스템 
{
    // InputAction 무브 액션 변수 선언
    private InputAction moveAction;

    private void Awake() // Unity가 컴포넌트를 초기화할 때 호출하며, 해당 컴포넌트의 Start()보다 먼저 실행됨
    {
        // 선언했던 변수 moveAction에 Player/Move 액션을 찾아서 할당,액션을 찾지 못하면 예외를 발생
        moveAction = InputSystem.actions.FindAction("Player/Move", throwIfNotFound: true);
    }

    public Vector2 ReadMove() // ReadMove: 이동 입력 값을 읽을 함수
    {
        // return: 읽어서 반환한다
        // moveAction.ReadValue<Vector2>(): moveAction에서 Vector2 의 값
        return moveAction.ReadValue<Vector2>();
    }
}
