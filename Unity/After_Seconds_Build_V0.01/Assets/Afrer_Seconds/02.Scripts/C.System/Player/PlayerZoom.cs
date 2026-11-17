using Cinemachine;
using UnityEngine;

#region 의사코드 Ver 0.1 (확대 조준)

/*
오른쪽 클릭으로 시야를 확대해 정밀하게 조준하는 기능
(던지기 자세에서도, 총을 들었을 때도 같은 확대를 쓴다. 그래서 던지기와 따로 떨어진 기능으로 만든다.
 언제 확대해도 되는지(물건을 들고 있는지 등)는 Presenter가 판단하고, 여기서는 요청받은 대로 확대만 한다)

기억해둘 정보:
    시야 설정 에셋의 참조 — settings (확대 비율·바뀌는 시간·감도 비율이 들어 있다)
    플레이어의 눈 위치 — cameraRoot (여러 가상 카메라 중 "이 플레이어를 따라가는 것"을 찾는 데 쓴다)
    플레이어를 따라가는 가상 카메라 — playerCamera
        (카메라는 프리팹 안이 아니라 각 씬에 놓여 있어서, 게임이 시작될 때 찾아 둔다)
    확대하지 않았을 때의 시야각 — baseFieldOfView (시작할 때 가상 카메라에서 읽어 둔다)
        (씬마다 시야각이 다를 수 있어서 숫자로 적지 않고 읽는다)
    지금 확대 중인지 — isZoomed, 처음에는 false
    시야각이 바뀌는 속도 — fieldOfViewVelocity (부드럽게 바꾸는 계산이 쓰는 값)

밖에서 읽을 수 있게 공개하는 값 (읽기만 가능):
    지금 확대 중인지 — IsZoomed
    지금 적용할 마우스 감도 비율 — SensitivityScale (확대 중이면 설정의 비율, 아니면 1)

시작할 때 — Start:
    설정이나 눈 위치가 연결되지 않았다면: 오류를 알리고 비활성화한다
    씬의 가상 카메라들 중 눈 위치를 따라가는 것을 찾는다
        (Awake가 아니라 Start에서 찾는 이유: 다른 오브젝트들의 준비가 끝난 뒤에 찾으려고)
    찾지 못했다면: 경고를 알리고 비활성화한다 (확대만 안 될 뿐 다른 기능은 그대로 동작한다)
    찾았다면: 지금 시야각을 "확대하지 않았을 때의 시야각"으로 기억한다

확대를 켜고 끄라는 요청 — Toggle (오른쪽 클릭):
    확대 중이면 풀고, 아니면 확대한다

확대 상태를 정하라는 요청 — SetZoomed:
    전달받은 값으로 확대 여부를 기록한다 (던진 뒤 확대를 풀 때 쓴다)

매 프레임 — Update:
    목표 시야각을 정한다: 확대 중이면 "기본 시야각 × 확대 비율", 아니면 기본 시야각
    지금 시야각을 목표 시야각 쪽으로 부드럽게 옮긴다
    옮긴 시야각을 가상 카메라에 넣는다
*/

#endregion
public class PlayerZoom : MonoBehaviour
{
    [SerializeField] private PlayerLookSettings settings; // 확대 비율·바뀌는 시간·감도 비율을 보관하는 설정 에셋

    // 플레이어의 눈 위치. 씬의 가상 카메라들 중 "이것을 따라가는 카메라"가 플레이어 카메라다.
    [SerializeField] private Transform cameraRoot;

    // 플레이어를 따라가는 가상 카메라. 실제 화면을 그리는 Main Camera는 이 가상 카메라의 설정을 따라간다.
    // 그래서 Main Camera의 시야각을 직접 바꾸면 다음 프레임에 되돌아가고, 가상 카메라의 값을 바꿔야 한다.
    private CinemachineVirtualCamera playerCamera;

    private float baseFieldOfView;     // 확대하지 않았을 때의 시야각(도). Start에서 읽어 둔다.
    private float fieldOfViewVelocity; // SmoothDamp가 부드럽게 바꾸는 데 쓰는 속도 값. 직접 고치지 않는다.
    private bool isZoomed;             // 지금 확대 중인지

    // 밖에서 읽기만 할 수 있게 공개한다.
    public bool IsZoomed => isZoomed;

    // 지금 적용할 마우스 감도 비율. 확대 중이면 낮추고, 아니면 1(그대로)이다.
    // Presenter가 시야 입력에 이 값을 곱해서 PlayerLook에 전달한다.
    public float SensitivityScale => (isZoomed && settings != null) ? settings.ZoomSensitivityRatio : 1f;

    private void Start()
    {
        if (settings == null || cameraRoot == null) // 연결되지 않은 것이 있다면
        {
            Debug.LogError("PlayerZoom의 Settings와 Camera Root를 연결해 주세요.", this);
            enabled = false;
            return;
        }

        // 씬에 있는 가상 카메라를 모두 찾아서, 그중 플레이어의 눈 위치를 따라가는 것을 고른다.
        // (나중에 컷씬용 가상 카메라가 생겨도 플레이어 카메라만 골라내기 위해서다)
        CinemachineVirtualCamera[] cameras = FindObjectsByType<CinemachineVirtualCamera>(FindObjectsInactive.Exclude);
        foreach (CinemachineVirtualCamera candidate in cameras)
        {
            if (candidate.Follow == cameraRoot) // 이 카메라가 내 눈 위치를 따라간다면
            {
                playerCamera = candidate;
                break; // 찾았으므로 더 보지 않는다
            }
        }

        if (playerCamera == null) // 찾지 못했다면
        {
            // 확대만 안 될 뿐 이동·던지기는 그대로 동작해야 하므로 오류가 아니라 경고로 알린다.
            Debug.LogWarning("PlayerZoom: CameraRoot를 따라가는 Cinemachine 가상 카메라를 찾지 못해 확대 조준을 쓸 수 없습니다.", this);
            enabled = false;
            return;
        }

        // 지금 시야각을 기본값으로 기억한다. 씬마다 값이 달라도 각자의 값으로 되돌릴 수 있다.
        baseFieldOfView = playerCamera.m_Lens.FieldOfView;
        isZoomed = false;
    }

    // 확대를 켜고 끈다. 오른쪽 클릭을 누른 순간 Presenter가 부른다.
    public void Toggle()
    {
        SetZoomed(!isZoomed); // 지금 상태의 반대로 바꾼다
    }

    // 확대 상태를 직접 정한다. 던진 뒤나 물건을 내려놓았을 때 확대를 풀려고 SetZoomed(false)로 부른다.
    public void SetZoomed(bool zoomed)
    {
        if (!isActiveAndEnabled) // 이 컴포넌트가 비활성화 상태라면 (가상 카메라를 찾지 못한 경우 포함)
        {
            return;              // 종료
        }

        isZoomed = zoomed;
    }

    private void Update()
    {
        // 목표 시야각: 확대 중이면 기본값에 비율을 곱해 좁히고, 아니면 기본값이다.
        float targetFieldOfView = isZoomed ? baseFieldOfView * settings.ZoomFieldOfViewRatio : baseFieldOfView;

        // SmoothDamp(지금 값, 목표 값, ref 속도, 걸리는 시간)는 지금 값을 목표 쪽으로 부드럽게 옮긴 결과를 돌려준다.
        // PlayerLook에서 앉을 때 눈 높이를 부드럽게 낮추는 데 쓴 것과 같은 함수다.
        float current = playerCamera.m_Lens.FieldOfView;
        float next = Mathf.SmoothDamp(current, targetFieldOfView, ref fieldOfViewVelocity, settings.ZoomSmoothTime);

        // m_Lens는 값을 통째로 복사해 다루는 구조체라서, 꺼내서 고친 뒤 다시 넣어야 반영된다.
        LensSettings lens = playerCamera.m_Lens;
        lens.FieldOfView = next;
        playerCamera.m_Lens = lens;
    }

    private void OnDisable()
    {
        // 꺼질 때 확대된 채로 남지 않게 기본 시야각으로 되돌린다.
        if (playerCamera != null)
        {
            LensSettings lens = playerCamera.m_Lens;
            lens.FieldOfView = baseFieldOfView;
            playerCamera.m_Lens = lens;
        }

        isZoomed = false;
    }
}
