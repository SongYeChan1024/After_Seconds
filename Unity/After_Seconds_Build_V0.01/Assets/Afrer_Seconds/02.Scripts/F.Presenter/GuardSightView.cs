using UnityEngine;

// 옆면은 눈에서 시작한다. 앞면의 동심원 표본도 각각 차폐해 벽과 낮은 엄폐물의 윤곽을 따른다.
[RequireComponent(typeof(MeshFilter), typeof(MeshRenderer))]
public sealed class GuardSightView : MonoBehaviour
{
    private const int Segments = 48;
    private const int Rings = 5;
    private const int CapCenter = 1;
    private const int FirstRing = 2;
    private const int VertexCount = FirstRing + Segments * Rings;
    private readonly Vector3[] directions = new Vector3[VertexCount];
    private readonly Vector3[] vertices = new Vector3[VertexCount];
    private readonly Color32[] colors = new Color32[VertexCount];
    private Mesh mesh;
    private MeshRenderer surface;
    private float sampledAngle;
    private int palette = -1;
    private GuardSight owner;
    private GuardSettings config;

    private void Awake()
    {
        surface = GetComponent<MeshRenderer>();
        mesh = new Mesh { name = "Guard eye cone" };
        mesh.MarkDynamic();
        mesh.vertices = vertices;
        int[] indices = new int[Segments * Rings * 2 * 6];
        int cursor = 0;
        for (int sector = 0; sector < Segments; sector++)
        {
            int next = (sector + 1) % Segments;
            int a = FirstRing + sector;
            int b = FirstRing + next;
            Triangle(indices, ref cursor, CapCenter, a, b);
            for (int ring = 1; ring < Rings; ring++)
            {
                Triangle(indices, ref cursor, a, a + Segments, b + Segments);
                Triangle(indices, ref cursor, a, b + Segments, b);
                a += Segments;
                b += Segments;
            }
            Triangle(indices, ref cursor, 0, b, a);
        }
        mesh.triangles = indices;
        GetComponent<MeshFilter>().sharedMesh = mesh;
        surface.enabled = false;
    }

    // 공유 재질의 뒷면 컬링을 유지하면서 콘 안팎 양쪽에서 읽히게 한다.
    private static void Triangle(int[] indices, ref int cursor, int a, int b, int c)
    {
        indices[cursor++] = a;
        indices[cursor++] = b;
        indices[cursor++] = c;
        indices[cursor++] = c;
        indices[cursor++] = b;
        indices[cursor++] = a;
    }

    private void SampleDirections(float angle)
    {
        sampledAngle = angle;
        directions[CapCenter] = Vector3.forward;
        for (int ring = 1; ring <= Rings; ring++)
        {
            float tilt = .5f * angle * Mathf.Deg2Rad * ring / Rings;
            float spread = Mathf.Sin(tilt);
            for (int sector = 0; sector < Segments; sector++)
            {
                float phi = 2f * Mathf.PI * sector / Segments;
                directions[FirstRing + (ring - 1) * Segments + sector] =
                    new Vector3(spread * Mathf.Cos(phi), spread * Mathf.Sin(phi), Mathf.Cos(tilt));
            }
        }
    }

    public void Draw(GuardSight sight, GuardSettings settings, CharacterController player, bool alert, float recognition)
    {
        owner = sight;
        config = settings;
        FollowEyes();
        if (sampledAngle != settings.fieldOfView) SampleDirections(settings.fieldOfView);
        Vector3 eyes = transform.position;
        Quaternion facing = transform.rotation;
        for (int i = CapCenter; i < vertices.Length; i++)
        {
            float hit = sight.FirstCoverDistance(eyes, facing * directions[i], settings.sightDistance, player, settings);
            float distance = Mathf.Min(settings.sightDistance, Mathf.Max(0f, hit - .02f));
            vertices[i] = directions[i] * distance;
        }
        mesh.vertices = vertices;
        mesh.RecalculateBounds();
        SetPalette(alert ? 2 : recognition > 0f ? 1 : 0);
        surface.enabled = true;
    }

    private void SetPalette(int value)
    {
        if (value == palette) return;
        palette = value;
        Color32 tint = value == 2 ? new Color32(255, 70, 62, 0) :
            value == 1 ? new Color32(255, 202, 55, 0) : new Color32(120, 200, 211, 0);
        for (int i = 0; i < colors.Length; i++)
        {
            tint.a = i == 0 ? (byte)32 : i >= VertexCount - Segments ? (byte)17 : (byte)6;
            colors[i] = tint;
        }
        mesh.colors32 = colors;
    }

    private void FollowEyes() => transform.SetPositionAndRotation(owner.EyePosition(config), owner.EyeRotation);
    private void LateUpdate() { if (surface.enabled && owner) FollowEyes(); }
    public void Hide() { if (surface) surface.enabled = false; }
    private void OnDestroy() { if (mesh) Destroy(mesh); }
}
