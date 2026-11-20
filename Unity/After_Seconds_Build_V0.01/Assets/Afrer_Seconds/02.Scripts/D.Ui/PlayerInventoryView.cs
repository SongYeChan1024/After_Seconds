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
    [SerializeField] private RectTransform backing;
    private readonly StringBuilder text = new StringBuilder();
    private IInteractable previousFocus;
    private string previousMessage;
    public string EncounterPrompt { get; set; }
    public string FloorHint { get; set; }
    private int facilityLevel = -1;
    private int reportCountdown = -1;
    public void SetReportCountdown(int seconds)
    {
        if (reportCountdown == seconds) return;
        reportCountdown = seconds;
        Rebuild();
    }
    private static readonly string[] AlertNames = { "정상", "소음 조사", "구역 비상", "시설 전체 경보" };
    public void SetFacilityLevel(int level)
    {
        if (facilityLevel == level) return;
        facilityLevel = level;
        Rebuild();
    }

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
        text.Clear();
        if (facilityLevel >= 0) text.Append("경보 A").Append(facilityLevel).Append(" · ").Append(AlertNames[facilityLevel]).Append('\n');
        if (reportCountdown >= 0) text.Append("연구원 신고까지 ").Append(reportCountdown).Append("초\n");
        text.Append("소지품  ").Append(inventory.Count).Append('/').Append(inventory.Capacity).Append('\n');
        text.Append(inventory.SelectedIndex < 0 ? "<color=#C6EBED>▶ 빈손</color>\n" : "<color=#B8C3C8>  빈손</color>\n");
        for (int i = 0; i < inventory.Count; i++)
        {
            var item = inventory.Items[i];
            if (item == null) continue;
            text.Append(i == inventory.SelectedIndex ? "<color=#C6EBED>▶ " : "<color=#B8C3C8>  ");
            text.Append(item.Definition.DisplayName).Append(" · ").Append(item.Number.ToString("00"));
            string status = item.Ability ? item.Ability.StatusText : null;
            if (!string.IsNullOrEmpty(status)) text.Append(" · ").Append(status);
            text.Append("</color>\n");
        }
        text.Append("<size=75%>휠 선택   Q 내려놓기");
        var selected = inventory.Selected;
        if (selected && selected.Ability) text.Append('\n').Append(selected.Ability.ControlHint);
        text.Append("</size>");
        contents.text = text.ToString();
        if (backing)
        {
            float height = Mathf.Ceil(contents.preferredHeight);
            contents.rectTransform.SetSizeWithCurrentAnchors(RectTransform.Axis.Vertical, height);
            backing.SetSizeWithCurrentAnchors(RectTransform.Axis.Vertical, height + 32f);
        }
    }
    private void LateUpdate()
    {
        if (inventory == null || prompt == null) return;
        var focus = inventory.isActiveAndEnabled ? inventory.Focused : null;
        string message = EncounterPrompt ?? inventory.Message ?? (focus == null ? FloorHint : null);
        if (ReferenceEquals(focus, previousFocus) && message == previousMessage) return;
        previousFocus = focus;
        previousMessage = message;
        prompt.text = !string.IsNullOrEmpty(message) ? message : focus?.InteractionPrompt ?? "";
    }
}
