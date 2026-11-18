using UnityEngine;

#region 의사코드 Ver 0.1 (던지기 설정)

/*
플레이어 던지기에 쓰는 숫자를 보관하는 설정 에셋
(코드에 숫자를 직접 쓰지 않고, 에셋의 인스펙터에서 값을 바꾼다. PlayerMotorSettings와 같은 방식)

기억해둘 정보:
    던지는 빠르기 — throwSpeed (0 이상, m/s)
    위로 들어 올려 던지는 각도 — upwardAngle (0~80도)
        (바라보는 방향 그대로 던지면 금방 바닥에 떨어지므로 조금 위로 던진다)
    물건이 나타나는 자리 — spawnForwardOffset (0 이상, 눈 앞으로 몇 m)
    명중으로 치는 최소 충돌 빠르기 — minHitSpeed (0 이상, m/s)
        (바닥에서 구르거나 멈춰 있다가 살짝 닿는 것은 명중으로 치지 않는다)
    시험용 물건이 사라지기까지의 시간 — testItemLifetime (0 이상, 초. 0이면 사라지지 않음)
        (소지품 기능이 생기기 전까지만 쓰는 값이다)

밖에서 읽을 수 있게 공개하는 값 (읽기만 가능):
    위 값들을 그대로 돌려준다 — ThrowSpeed, UpwardAngle, SpawnForwardOffset, MinHitSpeed, TestItemLifetime
*/

#endregion

#region 의사코드 Ver 0.2 (위로/아래로 던지기, 궤적 표시 추가)

/*
(Ver 0.2: 던지는 방식을 두 가지로 나누고, 궤적을 그릴 때 쓰는 숫자를 추가한다. Ver 0.1에서 바뀐 부분만 적는다)

기억해둘 정보 — 바뀐 것:
    던지는 빠르기와 각도를 방식별로 따로 둔다
        위로 던지기(멀리, 높은 궤적) — overhandSpeed, overhandAngle
        아래로 던지기(가까이, 낮은 궤적) — underhandSpeed, underhandAngle
        (Ver 0.1의 throwSpeed, upwardAngle은 위로 던지기 값이 된다)

기억해둘 정보에 추가:
    궤적을 계산하는 시간 간격 — trajectoryTimeStep (초. 작을수록 곡선이 매끄럽다)
    궤적을 얼마나 먼 미래까지 그릴지 — trajectoryMaxTime (초)

밖에서 읽을 수 있게 공개하는 값에 추가 (읽기만 가능):
    OverhandSpeed, OverhandAngle, UnderhandSpeed, UnderhandAngle, TrajectoryTimeStep, TrajectoryMaxTime
*/

#endregion

#region 의사코드 Ver 0.3 (오른손에서 던지기)

/*
(Ver 0.3: 물건이 화면 가운데가 아니라 오른손 위치에서 나가게 한다. Ver 0.2에서 바뀐 부분만 적는다)

기억해둘 정보 — 바뀐 것:
    물건이 나타나는 자리(spawnForwardOffset, 눈 앞으로 몇 m) 대신,
    눈 위치를 기준으로 한 손의 위치를 방식별로 따로 둔다
        위로 던질 때의 손 위치 — overhandHandOffset (오른쪽, 위, 앞 순서의 m)
            (어깨 높이의 오른손: 오른쪽으로 조금, 아래로 조금, 앞으로 조금)
        아래로 던질 때의 손 위치 — underhandHandOffset
            (허리 높이의 오른손: 오른쪽으로 조금, 아래로 많이, 앞으로 조금)

밖에서 읽을 수 있게 공개하는 값 — 바뀐 것:
    SpawnForwardOffset 대신 OverhandHandOffset, UnderhandHandOffset
*/

#endregion

#region 의사코드 Ver 0.4 (궤적을 방향만 보이게 짧게)

/*
(Ver 0.4: 궤적을 끝까지 그리지 않고, 어느 쪽으로 날아가는지만 보이게 한다. Ver 0.3에서 바뀐 부분만 적는다)

기억해둘 정보에 추가:
    궤적을 손에서부터 몇 m까지 그릴지 — trajectoryLength (짧게)
    확대 조준 중일 때 몇 m까지 그릴지 — trajectoryZoomedLength (더 길게)

밖에서 읽을 수 있게 공개하는 값에 추가 (읽기만 가능):
    TrajectoryLength, TrajectoryZoomedLength
*/

#endregion

#region 의사코드 Ver 0.5 (조준점 쪽으로 모이는 거리)

/*
(Ver 0.5: 오른손에서 나간 물건이 화면 가운데 쪽으로 향하게 하는 데 쓰는 거리를 추가한다. Ver 0.4에서 바뀐 부분만 적는다)

기억해둘 정보에 추가:
    물건의 길이 화면 가운데와 만나는 거리를 방식별로 따로 둔다
        위로 던질 때 — overhandConvergeDistance (멀리)
        아래로 던질 때 — underhandConvergeDistance (가까이)
    가까운 벽을 볼 때도 이보다 짧아지지 않게 하는 최소 거리 — minConvergeDistance

밖에서 읽을 수 있게 공개하는 값에 추가 (읽기만 가능):
    OverhandConvergeDistance, UnderhandConvergeDistance, MinConvergeDistance
*/

#endregion
[CreateAssetMenu(fileName = "PlayerThrowSettings", menuName = "After Seconds/Player Throw Settings")]
public class PlayerThrowSettings : ScriptableObject
{
    // 2026-11-17 사용자 정정: R 아래 던지기는 낮게 밀어 지면에서 굴리는 투척이다.
    // 같은 손 위치와 방식별 속도/각도로 미리보기와 실제 발사를 계산한다. 홀드 충전은 하지 않는다.
    // ── 위로 던지기: 멀리, 높은 궤적 ──
    [Header("위로 던지기 (멀리)")]
    [Tooltip("위로 던질 때의 빠르기(m/s)입니다. 클수록 멀리 날아갑니다.")]
    [SerializeField, Min(0f)] private float overhandSpeed = 12f;

    [Tooltip("위로 던질 때, 바라보는 방향보다 위로 들어 올리는 각도(도)입니다.")]
    [SerializeField, Range(0f, 80f)] private float overhandAngle = 8f;

    // 위로 던질 때 물건이 나가는 손의 위치. 눈(CameraRoot)을 기준으로 (오른쪽, 위, 앞) 순서의 m다.
    // 위쪽 값이 음수면 눈보다 아래라는 뜻이다. 어깨 높이의 오른손을 나타낸다.
    [Tooltip("위로 던질 때 손의 위치입니다. 눈 기준 (오른쪽, 위, 앞) m. 위쪽 값이 음수면 눈보다 아래입니다.")]
    [SerializeField] private Vector3 overhandHandOffset = new Vector3(0.3f, -0.15f, 0.45f);

    // 위로 던질 때, 오른손에서 나간 물건의 길이 시선(화면 가운데)과 만나는 지점까지의 거리.
    // 물건이 떨어질 만한 거리로 두면, 떨어지는 곳이 화면 가운데에 온다.
    [Tooltip("위로 던질 때 물건의 길이 화면 가운데와 만나는 거리(m)입니다. 물건이 떨어질 만한 거리로 둡니다.")]
    [SerializeField, Min(0.5f)] private float overhandConvergeDistance = 10f;

    // ── 아래에서 던지기: 낮게 밀고 지면에 닿으면 전진 회전으로 구른다 ──
    [Header("아래에서 던지기 (낮게 굴리기)")]
    [Tooltip("낮게 밀어 보내는 빠르기(m/s). 위 던지기보다 약하게 보냅니다.")]
    [SerializeField, Min(0f)] private float underhandSpeed = 4.5f;

    [Tooltip("시선 기준 발사각(도). 음수는 아래로 밀어 보내는 방향입니다.")]
    [SerializeField, Range(-75f, 0f)] private float underhandAngle = -12f;
    [Tooltip("위를 보더라도 이 지평선 기준 각도보다 높게 띄우지 않습니다.")]
    [SerializeField, Range(-75f, 0f)] private float underhandMaxElevation = -5f;
    [Tooltip("아래 던지기 물체의 최소 선형/회전 감쇠. 궤적과 실제 물리 양쪽에 적용합니다.")]
    [SerializeField, Min(0f)] private float underhandDamping = 0.8f;
    [Tooltip("아래 모드의 구름/반발용 물리 재질. 비어 있으면 프리팹 재질을 유지합니다.")]
    [SerializeField] private PhysicsMaterial underhandPhysicsMaterial;

    // 아래로 던질 때 손의 위치. 허리 높이의 오른손을 나타내므로 위쪽 값이 더 크게 음수다.
    [Tooltip("아래로 던질 때 손의 위치입니다. 눈 기준 (오른쪽, 위, 앞) m. 허리 높이라서 위쪽 값이 더 낮습니다.")]
    [SerializeField] private Vector3 underhandHandOffset = new Vector3(0.26f, -0.34f, 0.68f);

    // 아래로 던질 때의 모이는 거리. 가까이 던지므로 위로 던지기보다 짧게 둔다.
    [Tooltip("아래로 던질 때 물건의 길이 화면 가운데와 만나는 거리(m)입니다.")]
    [SerializeField, Min(0.5f)] private float underhandConvergeDistance = 4f;

    [Header("공통")]
    // 가까운 벽을 보고 있어도 모이는 거리가 이 값보다 짧아지지 않게 한다. 너무 짧으면 방향이 심하게 꺾인다.
    [Tooltip("가까운 벽을 볼 때도 모이는 거리가 이 값(m)보다 짧아지지 않게 합니다.")]
    [SerializeField, Min(0.5f)] private float minConvergeDistance = 2f;

    // 이 빠르기보다 느리게 부딪힌 것은 명중으로 알리지 않는다.
    [Tooltip("이 값(m/s)보다 느리게 부딪힌 것은 명중으로 치지 않습니다. 구르는 물건이 계속 명중을 알리지 않게 합니다.")]
    [SerializeField, Min(0f)] private float minHitSpeed = 1f;

    // 시험용 물건을 몇 초 뒤에 없앨지. 0이면 없애지 않는다.
    [Tooltip("던진 물건이 사라지기까지의 시간(초)입니다. 0이면 사라지지 않습니다. 소지품 기능이 생기기 전까지만 씁니다.")]
    [SerializeField, Min(0f)] private float testItemLifetime = 20f;

    [Header("궤적 표시")]
    // 궤적을 이 시간 간격으로 한 점씩 계산한다. 작을수록 곡선이 매끄럽지만 계산이 늘어난다.
    [Tooltip("이전 버전 호환용 표시 값입니다. 현재 궤적 적분은 Time.fixedDeltaTime을 사용합니다.")]
    [SerializeField, Min(0.01f)] private float trajectoryTimeStep = 0.05f;

    // 던진 뒤 이 시간까지의 궤적만 그린다. 그 전에 무언가에 닿으면 거기서 멈춘다.
    [Tooltip("첫 접촉을 예측할 최대 시간(초)입니다. 표시선 길이와 별도로 계산합니다.")]
    [SerializeField, Min(0.1f)] private float trajectoryMaxTime = 3f;

    // 궤적은 끝까지 그리지 않고 "어느 쪽으로 날아가는지"만 알 수 있게 손에서부터 이 길이만큼만 그린다.
    [Tooltip("궤적을 손에서부터 몇 m까지 그릴지입니다. 날아가는 방향만 보이도록 짧게 둡니다.")]
    [SerializeField, Min(0.1f)] private float trajectoryLength = 2.5f;

    // 오른쪽 클릭으로 확대 조준했을 때는 궤적을 더 길게 그려서 더 멀리까지 가늠할 수 있게 한다.
    [Tooltip("확대 조준(오른쪽 클릭) 중일 때 궤적을 몇 m까지 그릴지입니다. 기본 길이보다 길게 둡니다.")]
    [SerializeField, Min(0.1f)] private float trajectoryZoomedLength = 4f;

    // => 는 "이 값을 돌려준다"는 짧은 속성 문법이다. get만 있으므로 밖에서 읽기만 할 수 있다.
    [Header("표시와 안전 여유 (시험값)")]
    [SerializeField, Min(0.001f)] private float trajectoryWidth = 0.012f;
    [SerializeField, Range(0f, 1f)] private float trajectoryOpacity = 0.30f;
    [SerializeField, Range(0.1f, 0.95f)] private float fadeStart = 0.35f;
    [SerializeField, Min(0.001f)] private float surfaceSkin = 0.005f;
    [SerializeField] private LayerMask collisionMask = ~0;
    [Header("첫 접촉 예측과 착지 위치")]
    [Tooltip("켜면 선을 예측 끝까지 표시합니다. 접촉 원은 표시선이 실제 표면까지 닿는 경우에만 나옵니다.")]
    [SerializeField] private bool showFullTrajectory = false;
    [SerializeField, Min(1f)] private float maxPreviewDistance = 60f;
    [Tooltip("예상 접촉 위치를 알려 주는 표식 반경입니다. 피해나 교환 범위가 아닙니다.")]
    [SerializeField, Range(0.05f, 0.6f)] private float landingMarkerRadius = 0.20f;
    [SerializeField, Range(0.005f, 0.05f)] private float landingMarkerWidth = 0.018f;
    public bool ShowFullTrajectory => showFullTrajectory;
    public float MaxPreviewDistance => maxPreviewDistance;
    public float LandingMarkerRadius => landingMarkerRadius;
    public float LandingMarkerWidth => landingMarkerWidth;
    public float TrajectoryWidth => trajectoryWidth;
    public float TrajectoryOpacity => trajectoryOpacity;
    public float FadeStart => fadeStart;
    public float SurfaceSkin => surfaceSkin;
    public int CollisionMask => collisionMask;

    public float OverhandSpeed => overhandSpeed;
    public float OverhandAngle => overhandAngle;
    public float UnderhandSpeed => underhandSpeed;
    public float UnderhandAngle => underhandAngle;
    public float UnderhandMaxElevation => underhandMaxElevation;
    public float UnderhandDamping => underhandDamping;
    public PhysicsMaterial UnderhandPhysicsMaterial => underhandPhysicsMaterial;
    public Vector3 OverhandHandOffset => overhandHandOffset;
    public Vector3 UnderhandHandOffset => underhandHandOffset;
    public float OverhandConvergeDistance => overhandConvergeDistance;
    public float UnderhandConvergeDistance => underhandConvergeDistance;
    public float MinConvergeDistance => minConvergeDistance;
    public float MinHitSpeed => minHitSpeed;
    public float TestItemLifetime => testItemLifetime;
    [SerializeField, Min(0f)] private float swapDelay = 3f;
    public float SwapDelay => swapDelay;
    public float TrajectoryTimeStep => trajectoryTimeStep;
    public float TrajectoryMaxTime => trajectoryMaxTime;
    public float TrajectoryLength => trajectoryLength;
    public float TrajectoryZoomedLength => trajectoryZoomedLength;
}
