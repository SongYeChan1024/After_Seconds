using UnityEngine;

#region 의사코드
// 손 표시기가 현재 자세에 맞는 카메라 기준 손 위치와 투척 자세를 선택할 수 있게 값을 제공한다.
// 걷기·달리기 보폭과 흔들림을 적용한 뒤 조준 중에는 진폭을 줄이고 점프·착지 오프셋을 더한다.
#endregion

// 영상 측정치가 아닌 프로젝트용 임시 포즈/흔들림 시험값이다.
[CreateAssetMenu(fileName = "PlayerHandSettings", menuName = "After Seconds/Player Hand Settings")]
public class PlayerHandSettings : ScriptableObject
{
    public Vector3 restingItem = new Vector3(0.28f, -0.17f, 0.50f);
    public Vector3 sprintOffset = new Vector3(-0.02f, -0.06f, -0.04f);
    public Vector3 crouchOffset = new Vector3(0f, 0.025f, 0f);
    public Vector3 zoomOffset = new Vector3(-0.055f, 0.07f, 0.06f);
    [Tooltip("아래 던지기 확대 시 낮은 손이 화면 밖으로 잘리지 않도록 추가로 올리는 높이(m).")]
    [Min(0f)] public float underhandZoomLift = 0.08f;
    public Vector3 aimHoldOffset = new Vector3(-0.015f, 0.025f, 0.015f);
    public Vector3 rightShoulder = new Vector3(0.19f, -0.28f, -0.015f);
    public Vector3 leftShoulder = new Vector3(-0.19f, -0.28f, -0.015f);
    [Min(0.01f)] public float poseSmoothTime = 0.10f;
    [Min(0.01f)] public float recoveryTime = 0.24f;
    [Tooltip("아래 던지기 방출 직후 손을 낮게 앞으로 미는 거리(m, 눈 기준).")]
    public Vector3 underhandFollowThrough = new Vector3(-0.03f, -0.06f, 0.18f);
    [Range(0f, 0.03f)] public float bobAmount = 0.008f;
    [Range(0f, 1f)] public float zoomMotionScale = 0.25f;
    [Range(0f, 0.02f)] public float turnSway = 0.002f;
    [Range(0f, 0.1f)] public float maxSway = 0.025f;
    [Tooltip("손목에서 물체 중심까지의 눈 기준 오프셋. 최종 쥐기 클립 반입 시 재조정한다.")]
    public Vector3 palmToItem = new Vector3(0f, 0.025f, 0.075f);

    [Header("양손 이동 동작 (미터 / 초, 시험값)")]
    public Vector3 leftRestingHand = new Vector3(-0.24f, -0.17f, 0.43f);
    public Vector3 walkSwing = new Vector3(0.012f, 0.025f, 0.045f);
    public Vector3 runSwing = new Vector3(0.025f, 0.055f, 0.09f);
    [Range(0f, 1f)] public float leftSwingScale = 0.75f;
    [Min(0.5f)] public float walkStrideLength = 2.8f;
    [Min(0.5f)] public float runStrideLength = 3.2f;
    [Range(0f, 1f)] public float aimingMotionScale = 0.15f;
    [Min(0.01f)] public float movementBlendTime = 0.14f;
    public Vector3 airborneOffset = new Vector3(0f, 0.045f, -0.025f);
    [Range(0f, 0.15f)] public float maxLandingDip = 0.08f;
}
