using UnityEngine;

public class PlayerLook : MonoBehaviour
{
    #region 의사코드

    /*
    플레이어의 시야를 회전시키는 기능

기억해둘 정보:
    CameraRoot의 참조
    시야 설정의 참조
        좌우 마우스 감도
        상하 마우스 감도
        위아래로 볼 수 있는 최소·최대 각도

    현재 상하 회전 각도 — 처음에는 0도

초기화할 때:
    CameraRoot와 시야 설정이 연결되어 있는지 확인한다

    필요한 참조가 없다면:
        설정 오류를 알린다
        이 컴포넌트를 비활성화하고 초기화를 중단한다

시야 회전을 요청받으면:
    이 컴포넌트가 비활성화 상태라면:
        처리를 종료한다

    입력값의 X에 좌우 감도를 곱한다
    계산한 각도만큼 플레이어 전체를 Y축으로 회전시킨다

    입력값의 Y에 상하 감도를 곱한다
    계산한 각도를 현재 상하 회전 각도에서 뺀다
        마우스를 위로 움직이면 위를 바라보게 한다

    현재 상하 회전 각도를 최소·최대 각도 사이로 제한한다

    CameraRoot의 로컬 회전을 다음처럼 설정한다:
        X: 제한한 상하 회전 각도
        Y: 0도
        Z: 0도
    */

    #endregion

    #region 의사코드 Ver 0.2 (앉을 때 눈 높이 낮추기)

    /*
    (Ver 0.2: 몸은 Motor, 눈은 Look이 담당한다.
             앉으면 몸이 낮아진 만큼 CameraRoot의 높이도 같이 낮춘다)

    기억해둘 정보에 추가:
        서 있을 때 CameraRoot의 위치 — Awake에서 읽어 둔다

    초기화할 때 추가:
        CameraRoot의 처음 로컬 위치를 서 있을 때의 눈 위치로 기억한다

    눈 높이를 낮추라는 요청을 받으면 — SetEyeDrop:
        이 컴포넌트가 비활성화 상태라면:
            처리를 종료한다
        CameraRoot의 로컬 위치를
        "서 있을 때의 눈 위치에서 전달받은 값만큼 아래"로 설정한다
            (전달받은 값이 0이면 서 있을 때 위치로 돌아간다)
    */

    #endregion

    [SerializeField] private Transform cameraRoot; // 상하 회전에 사용할 CameraRoot의 Transform 참조
    [SerializeField] private PlayerLookSettings settings; //PlayerLookSettings의 설정값 참조

    private float pitchAngle; // 현재 상하 회전 각도

    private Vector3 standingEyeLocalPosition; // 서 있을 때 CameraRoot의 로컬 위치 (Awake에서 읽어 둔다)
    // 의사코드: 몸 높이는 Motor가 확정하고, 눈 높이만 목표까지 부드럽게 따라간다.
    // 빠르게 앉았다 일어나도 현재 높이와 속도에서 계속 보간해 순간 이동을 피한다.
    [SerializeField, Min(0f)] private float crouchEyeSmoothTime = 0.12f;
    private float currentEyeDrop;
    private float eyeDropVelocity;

    private void Awake()
    {
        if (cameraRoot == null || settings == null) // CameraRoot와 Settings 중 하나라도 연결되지 않았다면
        {
            Debug.LogError("PlayerLook의 CameraRoot와 Settings를 연결해 주세요.", this); // 설정 누락을 알린다

            enabled = false; // 이 컴포넌트를 비활성화한다. 현재 Awake의 실행을 끝내는 명령은 아니다.

            return; // 현재 Awake의 실행을 종료해 나머지 초기화를 중단한다.

        }

        pitchAngle = 0f; //현재 상하 회전 각도를 0도로 초기화한다

        // 지금 CameraRoot 위치를 서 있을 때의 눈 위치로 기억한다. 숫자로 적지 않고 읽어 두는 이유는
        // 프리팹에서 CameraRoot 위치를 바꿔도 코드를 고칠 필요가 없게 하려는 것이다.
        standingEyeLocalPosition = cameraRoot.localPosition;
    }

    // 앉았을 때 눈 높이를 낮춘다. eyeDrop은 "서 있을 때보다 몇 m 낮출지"이다. 0이면 원래 높이.
    // Presenter가 매 프레임 Motor의 CrouchHeightDrop(몸이 낮아진 만큼)을 전달한다.
    public void SetEyeDrop(float eyeDrop)
    {
        if (!isActiveAndEnabled) // 이 컴포넌트가 비활성화 상태라면
        {
            return;              // 종료
        }

        // 회전(localRotation)은 Rotate가 따로 바꾸므로, 여기서는 위치(localPosition)만 바꾼다.
        currentEyeDrop = Mathf.SmoothDamp(currentEyeDrop, eyeDrop, ref eyeDropVelocity,
            crouchEyeSmoothTime, Mathf.Infinity, Time.deltaTime);
        cameraRoot.localPosition = standingEyeLocalPosition - Vector3.up * currentEyeDrop;
    }

    public void Rotate(Vector2 lookInput) // 마우스로 시야 회전 값이 들어올 때 이 함수를 호출한다.
    {
        if (!isActiveAndEnabled) // 이 컴포넌트가 비활성화 상태라면 (일종의 예외처리)
        {
            return; // 종료
        }
        float horizontalAngle = lookInput.x * settings.HorizontalSensitivity; // 입력값의 X에 좌우 감도를 곱한다, 쉽게 풀어서 말하면 마우스가 움직인 만큼의 좌우 회전 값을 계산한다.

        float verticalAngle = lookInput.y * settings.VerticalSensitivity;// 입력값의 Y에 상하 감도를 곱한다, 쉽게 풀어서 말하면 마우스가 움직인 만큼의 상하 회전 값을 계산한다.

        transform.Rotate(Vector3.up, horizontalAngle, Space.World); // 계산한 각도만큼 플레이어 전체를 Y축으로 회전시킨다

        pitchAngle -= verticalAngle; // 계산한 각도를 현재 상하 회전 각도에서 뺀다, 마우스를 위로 움직이면 위를 바라보게 한다, 플레이어의 입력이 반대로 작용하지 않게 해주는 기능.

        pitchAngle = Mathf.Clamp(pitchAngle, settings.MinPitch, settings.MaxPitch); // 현재 상하 회전각도의 제한이 없기 때문에
                                                                                    // 세팅에서 정한 값 만큼으로 제한하기 위해서 Mathf.Clamp() 함수를 사용한다.
                                                                                    // 현재 상하 회전 각도를 최소·최대 각도 사이로 제한한다.

        cameraRoot.localRotation = Quaternion.Euler(pitchAngle, 0f, 0f); // CameraRoot의 로컬 회전을 다음처럼 설정한다: X: 제한한 상하 회전 각도, Y: 0도, Z: 0도

    }


}
