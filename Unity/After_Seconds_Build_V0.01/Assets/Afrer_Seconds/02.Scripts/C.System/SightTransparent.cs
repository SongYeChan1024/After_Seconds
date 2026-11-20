using UnityEngine;

#region 의사코드
// 시야 검사 중 이 표식을 가진 표면을 만나면 시선이 지나갈 수 있다.
// 잡기와 사격의 차폐 검사에서는 같은 표면도 장애물로 취급한다.
#endregion

// 투척과 보행을 막되 경비의 시선은 통과시키는 충돌체 그룹.
public sealed class SightTransparent : MonoBehaviour { }
