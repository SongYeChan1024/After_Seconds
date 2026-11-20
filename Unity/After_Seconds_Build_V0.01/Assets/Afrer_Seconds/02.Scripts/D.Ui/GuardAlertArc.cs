using UnityEngine;

// 의사코드: 경비 쪽을 향한 호의 바탕을 그리고, 중앙에서 양쪽으로 현재 인식량만큼 채운다.
public sealed class GuardAlertArc : UnityEngine.UI.MaskableGraphic
{
    private float amount;

    public void SetAmount(float value)
    {
        value = Mathf.Clamp01(value);
        if (amount == value) return;
        amount = value;
        SetVerticesDirty();
    }

    protected override void OnPopulateMesh(UnityEngine.UI.VertexHelper mesh)
    {
        mesh.Clear();
        Rect rect = rectTransform.rect;
        float radius = Mathf.Min(rect.width, rect.height) * .5f;
        AddBand(mesh, rect.center, radius, 8f, 64f, new Color32(22, 22, 26, 220));
        Color track = color;
        track.a *= .38f;
        AddBand(mesh, rect.center, radius - 1f, 6f, 62f, track);
        if (amount > 0f) AddBand(mesh, rect.center, radius - 1f, 6f, 62f * amount, color);
    }

    private static void AddBand(UnityEngine.UI.VertexHelper mesh, Vector2 center, float radius,
        float width, float halfAngle, Color32 tint)
    {
        int steps = Mathf.Max(1, Mathf.CeilToInt(halfAngle / 4f));
        for (int i = 0; i <= steps; i++)
        {
            float angle = Mathf.Lerp(-halfAngle, halfAngle, (float)i / steps) * Mathf.Deg2Rad;
            Vector2 dir = new Vector2(Mathf.Sin(angle), Mathf.Cos(angle));
            int index = mesh.currentVertCount;
            mesh.AddVert(center + dir * radius, tint, Vector2.zero);
            mesh.AddVert(center + dir * (radius - width), tint, Vector2.zero);
            if (i == 0) continue;
            mesh.AddTriangle(index - 2, index, index - 1);
            mesh.AddTriangle(index - 1, index, index + 1);
        }
    }
}
