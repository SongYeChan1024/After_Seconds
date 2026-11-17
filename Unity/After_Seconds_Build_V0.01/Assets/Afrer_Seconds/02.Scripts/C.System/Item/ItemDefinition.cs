using UnityEngine;

#region 의사코드 Ver 0.1 (아이템 한 종류의 정보)

/*
아이템 한 종류가 "무엇인지"를 적어 두는 설정 에셋
(식판·컵·총처럼 종류마다 에셋을 하나씩 만든다. 코드를 고치지 않고 에셋만 추가해서 아이템을 늘린다.
 지금은 던지기에 필요한 정보만 담는다. 줍기·소지품·사용 기능이 생기면 여기에 항목을 추가한다)

기억해둘 정보:
    화면에 보여 줄 이름 — displayName
    세상에 놓였을 때의 모습 — worldPrefab
        (던졌을 때 날아가는 물건, 나중에는 바닥에 놓여 있는 물건도 이 프리팹으로 만든다.
         명중을 알릴 수 있도록 ThrownObject가 붙은 프리팹이어야 한다)

밖에서 읽을 수 있게 공개하는 값 (읽기만 가능):
    이름과 프리팹을 그대로 돌려준다 — DisplayName, WorldPrefab
*/

#endregion
[CreateAssetMenu(fileName = "Item_New", menuName = "After Seconds/Item Definition")]
public class ItemDefinition : ScriptableObject
{
    // 화면과 로그에 보여 줄 이름. 예: "식판", "시험용 공"
    [Tooltip("화면과 로그에 보여 줄 아이템 이름입니다.")]
    [SerializeField] private string displayName;

    // 이 아이템이 세상에 놓였을 때의 모습. 던지면 이 프리팹을 복사해 날려 보낸다.
    [Tooltip("던졌을 때 날아가는 물건의 프리팹입니다. ThrownObject와 Rigidbody가 붙어 있어야 합니다.")]
    [SerializeField] private ThrownObject worldPrefab;

    // => 는 "이 값을 돌려준다"는 짧은 속성 문법이다. get만 있으므로 밖에서 읽기만 할 수 있다.
    public string DisplayName => displayName;
    public ThrownObject WorldPrefab => worldPrefab;
}
