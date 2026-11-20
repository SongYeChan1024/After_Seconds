using UnityEngine;

#region 의사코드
// 시점 갱신 시 가로·세로 감도를 읽고 상하 회전을 허용 각도 안으로 제한한다.
// 확대 조준 중에는 설정된 감도·시야각 배율과 보간 시간을 사용한다.
#endregion

[CreateAssetMenu(
    fileName = "PlayerLookSettings",
    menuName = "After Seconds/Player Look Settings")]
public class PlayerLookSettings : ScriptableObject
{
    [SerializeField, Min(0f)] private float horizontalSensitivity;
    [SerializeField, Min(0f)] private float verticalSensitivity;

    [SerializeField, Range(-89f, 0f)] private float minPitch;
    [SerializeField, Range(0f, 89f)] private float maxPitch;

    // ── 확대 조준(오른쪽 클릭)에 쓰는 값 ──
    // 확대했을 때의 시야각 비율. 0.55면 원래 시야각의 55%로 좁혀서 그만큼 크게 보인다.
    [Tooltip("확대 조준 때 시야각을 원래의 몇 배로 좁힐지입니다. 작을수록 더 크게 확대됩니다.")]
    [SerializeField, Range(0.2f, 1f)] private float zoomFieldOfViewRatio = 0.55f;

    // 확대·해제가 부드럽게 바뀌는 데 걸리는 대략의 시간(초).
    [Tooltip("확대하거나 풀 때 시야가 바뀌는 데 걸리는 시간(초)입니다. 0이면 즉시 바뀝니다.")]
    [SerializeField, Min(0f)] private float zoomSmoothTime = 0.1f;

    // 확대했을 때의 마우스 감도 비율. 확대하면 같은 움직임에도 화면이 크게 움직이므로 감도를 낮춘다.
    [Tooltip("확대 조준 때 마우스 감도를 원래의 몇 배로 낮출지입니다.")]
    [SerializeField, Range(0.1f, 1f)] private float zoomSensitivityRatio = 0.55f;

    public float ZoomFieldOfViewRatio => zoomFieldOfViewRatio;
    public float ZoomSmoothTime => zoomSmoothTime;
    public float ZoomSensitivityRatio => zoomSensitivityRatio;

    public float HorizontalSensitivity => horizontalSensitivity;
    public float VerticalSensitivity => verticalSensitivity;

    public float MinPitch => minPitch;
    public float MaxPitch => maxPitch;
}