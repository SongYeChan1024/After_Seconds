using System.Text;
using TMPro;
using UnityEngine;

// 의사코드: 소지품 상태를 읽어 우하단 목록과 현재 선택을 표시한다.
// 가까이 보이는 물건에만 F 안내를 표시하고, 가득 찼거나 버리기 실패하면 짧게 이유를 보여 준다.
public class PlayerInventoryView : MonoBehaviour
{
    [SerializeField] private PlayerInventory inventory;
    [SerializeField] private TMP_Text prompt;
    [SerializeField] private TMP_Text contents;
    private readonly StringBuilder text = new StringBuilder();
    private WorldItem previousCandidate;
    private string previousMessage;

    private void OnEnable()
    {
        if (inventory == null) return;
        inventory.Changed += Rebuild;
        Rebuild();
    }
    private void OnDisable() { if (inventory != null) inventory.Changed -= Rebuild; }
    private void Rebuild()
    {
        if (inventory == null || contents == null) return;
        text.Clear();text.Append("소지품  ").Append(inventory.Count).Append('/').Append(inventory.Capacity).Append('\n');
        for (int i = 0; i < inventory.Count; i++)
        {
            var item = inventory.Items[i];
            if (item == null) continue;
            text.Append(i == inventory.SelectedIndex ? "<color=#C6EBED>▶ " : "<color=#B8C3C8>  ");
            text.Append(item.Definition.DisplayName).Append(" · ").Append(item.Number.ToString("00")).Append("</color>\n");
        }
        if (inventory.Count == 0) text.Append("빈손\n");
        text.Append("<size=75%>휠 선택   Q 내려놓기</size>");
        contents.text = text.ToString();
    }
    private void LateUpdate()
    {
        if (inventory == null || prompt == null) return;
        var candidate = inventory.isActiveAndEnabled ? inventory.Candidate : null;
        string message = inventory.Message;
        if (candidate == previousCandidate && message == previousMessage) return;
        previousCandidate = candidate; previousMessage = message;
        prompt.text = !string.IsNullOrEmpty(message) ? message : candidate != null ? "[F] " + candidate.Definition.DisplayName + " 줍기" : "";
    }
}
