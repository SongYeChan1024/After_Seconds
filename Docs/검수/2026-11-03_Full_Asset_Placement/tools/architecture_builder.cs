// 작성자: 송예찬 / 2026-11-03 / 임시 Editor 검수 도구
// [의사코드]
// 1. 로드된 B4~1F 씬에서 이름과 치수가 맞는 기본 Cube 건축 표면만 찾는다.
// 2. B5, 계단, 구덩이, 퍼즐 가림벽, 단상, 셔터, 난간, 불투명 관찰 배경은 제외한다.
// 3. 기존 재제작 건축 프리팹을 반복 배치하고 각 타일을 원본 Cube 내부에 정확히 맞춘다.
// 4. 새 시각 자식의 Renderer bounds가 원본과 같을 때에만 원본 Renderer를 끈다.
// 5. 원본 Transform/Collider/메시/머티리얼은 보존하고 결과를 tmp JSON에 기록한다.

// [코딩]
#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Object = UnityEngine.Object;

public static class ASArchitecturePlacementUtility
{
    private const string ModelRoot = "Assets/Afrer_Seconds/05.Model/Environment/B5/";
    private const string Marker = "AS_CurrentArchitecture_VisualOnly";
    private const float FitToleranceMetres = 0.004f;
    private static readonly Dictionary<Kind, string> PrefabNames = new Dictionary<Kind, string>
    {
        { Kind.ConcreteWall, "Env_ConcreteWall_4m.prefab" },
        { Kind.MetalWall, "Env_MetalWall_4m.prefab" },
        { Kind.Observation, "Env_ObservationWall_4m.prefab" },
        { Kind.FireDoor, "Env_FireDoorWall_3m.prefab" },
        { Kind.Floor, "Env_FloorSlab_4m.prefab" },
        { Kind.Ceiling, "Env_CeilingPanel_4m.prefab" },
    };

    private enum Kind { ConcreteWall, MetalWall, Observation, FireDoor, Floor, Ceiling }

    [Serializable]
    public sealed class Entry
    {
        public string path;
        public string category;
        public string sourcePrefab;
        public string status;
        public string reason;
        public int tiles;
        public Vector3 originalLocalPosition;
        public Vector3 originalLocalScale;
        public Quaternion originalLocalRotation;
        public Vector3 originalWorldSize;
        public Bounds originalGeometryLocalBounds;
        public Bounds originalRendererWorldBounds;
        public Bounds newRendererWorldBounds;
        public float maxWorldBoundsError;
    }

    [Serializable]
    public sealed class Report
    {
        public string scene;
        public string scenePath;
        public string generatedAtUtc;
        public string note = "Visual-only dressing. No source asset or collider modifications. Scene is not saved by this utility.";
        public int appliedSurfaces;
        public int newTiles;
        public int skippedSurfaces;
        public int failedSurfaces;
        public List<Entry> entries = new List<Entry>();
    }

    public static Report LastReport { get; private set; }

    // [의사코드] 적용 후보를 미리 고정하고 원본 치수와 충돌을 보존한 시각 자식만 추가한다.
    public static void ApplyArchitecture(Scene scene)
    {
        if (!scene.IsValid() || !scene.isLoaded)
            throw new ArgumentException("ApplyArchitecture requires a valid, loaded scene.");

        var report = new Report
        {
            scene = scene.name,
            scenePath = scene.path,
            generatedAtUtc = DateTime.UtcNow.ToString("o"),
        };
        LastReport = report;

        if (scene.name.IndexOf("B5", StringComparison.OrdinalIgnoreCase) >= 0)
        {
            report.entries.Add(new Entry { path = scene.path, status = "scene_skipped", reason = "B5 and user ceiling orientation are protected." });
            WriteReport(report);
            return;
        }
        if (!Regex.IsMatch(scene.name, @"^Level_(B4|B3|B2|B1|1F)_"))
        {
            report.entries.Add(new Entry { path = scene.path, status = "scene_skipped", reason = "Scene is outside the five approved upper floors." });
            WriteReport(report);
            return;
        }

        var sources = LoadSources();
        // 새로 생성할 프리팹의 내부 메시를 다시 후보로 순회하지 않도록 먼저 배열을 만든다.
        MeshRenderer[] candidates = scene.GetRootGameObjects()
            .SelectMany(go => go.GetComponentsInChildren<MeshRenderer>(true)).ToArray();

        foreach (MeshRenderer original in candidates)
        {
            if (!original || !original.enabled || !original.gameObject.activeInHierarchy)
                continue;
            MeshFilter filter = original.GetComponent<MeshFilter>();
            if (!filter || !IsBuiltinCube(filter.sharedMesh))
                continue;

            Kind kind;
            string reason;
            if (!Classify(original.transform, scene.name, out kind, out reason))
                continue;

            var entry = new Entry
            {
                path = HierarchyPath(original.transform),
                category = kind.ToString(),
                sourcePrefab = ModelRoot + PrefabNames[kind],
                originalLocalPosition = original.transform.localPosition,
                originalLocalScale = original.transform.localScale,
                originalLocalRotation = original.transform.localRotation,
                originalGeometryLocalBounds = filter.sharedMesh.bounds,
                originalRendererWorldBounds = original.bounds,
            };
            report.entries.Add(entry);

            GameObject group = null;
            try
            {
                if (original.transform.Find(Marker))
                {
                    Skip(entry, report, "Visual marker already exists; rerun does not duplicate geometry.");
                    continue;
                }
                if (!CanFit(original.transform, kind, out Vector3 size, out reason))
                {
                    entry.originalWorldSize = size;
                    Skip(entry, report, reason);
                    continue;
                }
                entry.originalWorldSize = size;

                int nx = 1, ny = 1, nz = 1;
                bool horizontal = kind == Kind.Floor || kind == Kind.Ceiling;
                bool wallAlongZ = !horizontal && size.z > size.x;
                bool specialWall = kind == Kind.Observation || kind == Kind.FireDoor;
                if (horizontal)
                {
                    nx = TileCount(size.x, 4f);
                    nz = TileCount(size.z, 4f);
                }
                else if (!specialWall)
                {
                    if (wallAlongZ) nz = TileCount(size.z, 4f);
                    else nx = TileCount(size.x, 4f);
                    ny = TileCount(size.y, 4f);
                }

                group = new GameObject(Marker);
                SceneManager.MoveGameObjectToScene(group, scene);
                group.transform.SetParent(original.transform, false);

                // Cube는 단위 입방체이며 중심과 크기는 실제 Mesh.bounds를 사용한다.
                Bounds hostBounds = filter.sharedMesh.bounds;
                Vector3 tileSize = new Vector3(hostBounds.size.x / nx, hostBounds.size.y / ny, hostBounds.size.z / nz);
                Quaternion facing = horizontal
                    ? Quaternion.Euler(180f, 0f, 0f)
                    : (wallAlongZ ? Quaternion.Euler(0f, 90f, 0f) : Quaternion.identity);

                for (int x = 0; x < nx; x++)
                for (int y = 0; y < ny; y++)
                for (int z = 0; z < nz; z++)
                {
                    var tile = new GameObject("Tile_" + x + "_" + y + "_" + z);
                    tile.transform.SetParent(group.transform, false);
                    var instance = (GameObject)PrefabUtility.InstantiatePrefab(sources[kind], scene);
                    instance.transform.SetParent(tile.transform, false);
                    instance.transform.localPosition = Vector3.zero;
                    instance.transform.localRotation = facing;
                    instance.transform.localScale = Vector3.one;
                    foreach (Transform child in instance.GetComponentsInChildren<Transform>(true))
                        GameObjectUtility.SetStaticEditorFlags(child.gameObject, 0);

                    Bounds sourceBounds = ActiveMeshBoundsInSpace(instance, tile.transform);
                    if (!FinitePositive(sourceBounds.size))
                        throw new InvalidOperationException("Active source mesh bounds are empty or invalid.");
                    Vector3 scale = Divide(tileSize, sourceBounds.size);
                    Vector3 centre = hostBounds.min + Vector3.Scale(tileSize, new Vector3(x + .5f, y + .5f, z + .5f));
                    tile.transform.localScale = scale;
                    tile.transform.localPosition = centre - Vector3.Scale(sourceBounds.center, scale);
                    entry.tiles++;
                }

                Bounds visualWorld = ActiveRendererWorldBounds(group);
                float error = BoundsError(original.bounds, visualWorld);
                entry.newRendererWorldBounds = visualWorld;
                entry.maxWorldBoundsError = error;
                if (error > FitToleranceMetres)
                    throw new InvalidOperationException("Visual bounds mismatch: " + error.ToString("F6") + "m.");
                if (group.GetComponentsInChildren<Collider>(true).Length != 0 || group.GetComponentsInChildren<Rigidbody>(true).Length != 0)
                    throw new InvalidOperationException("New visual contains physics components.");
                if (original.transform.localPosition != entry.originalLocalPosition ||
                    original.transform.localScale != entry.originalLocalScale ||
                    original.transform.localRotation != entry.originalLocalRotation)
                    throw new InvalidOperationException("Source Transform changed unexpectedly.");

                Undo.RegisterCreatedObjectUndo(group, "Add reused architecture visual");
                Undo.RecordObject(original, "Hide primitive architecture renderer");
                original.enabled = false;
                EditorUtility.SetDirty(original);
                entry.status = "applied";
                report.appliedSurfaces++;
                report.newTiles += entry.tiles;
            }
            catch (Exception exception)
            {
                if (group) Object.DestroyImmediate(group);
                // 원본 Renderer는 최종 검증 뒤에만 끄므로 실패 시 원본 외형이 남는다.
                entry.status = "failed_preserved_original";
                entry.reason = exception.Message;
                report.failedSurfaces++;
                Debug.LogWarning("Architecture preserved " + entry.path + ": " + exception.Message);
            }
        }

        if (report.appliedSurfaces > 0) EditorSceneManager.MarkSceneDirty(scene);
        WriteReport(report);
        Debug.Log("Architecture " + scene.name + ": " + report.appliedSurfaces + " surfaces / " + report.newTiles +
            " repeated tiles; skipped=" + report.skippedSurfaces + "; failures=" + report.failedSurfaces + ". Scene remains unsaved.");
    }

    private static Dictionary<Kind, GameObject> LoadSources()
    {
        var result = new Dictionary<Kind, GameObject>();
        foreach (var pair in PrefabNames)
        {
            string path = ModelRoot + pair.Value;
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (!prefab) throw new FileNotFoundException("Architecture prefab missing: " + path);
            if (prefab.GetComponentsInChildren<Collider>(true).Length != 0 ||
                prefab.GetComponentsInChildren<Rigidbody>(true).Length != 0 ||
                prefab.GetComponentsInChildren<MonoBehaviour>(true).Length != 0)
                throw new InvalidOperationException("Architecture source must be a visual-only model prefab: " + path);
            result.Add(pair.Key, prefab);
        }
        return result;
    }

    private static bool Classify(Transform transform, string sceneName, out Kind kind, out string reason)
    {
        string name = transform.name;
        string path = HierarchyPath(transform);
        kind = Kind.ConcreteWall;
        reason = "Name is outside conservative architecture whitelist.";
        if (path.Contains(Marker)) return false;
        // 관찰 배경의 유리화, 퍼즐 구조/발판/단상의 재해석을 하지 않는다.
        if (Regex.IsMatch(path, @"Stair|Background", RegexOptions.IgnoreCase))
            return false;
        if (Regex.IsMatch(name, @"Pit|Booth|Pen_|Retaining|Platform|Deck|Island|Shelf|Ladder|Rail|Divider|SightBlock|Shutter|Lift_|Background|LightHousing|Luminous|Identification|Reveal|Pillar|Lintel|Trim|Rib|Strip|Sign", RegexOptions.IgnoreCase))
            return false;
        // B2 원심분리기 홀 천장은 호출자가 V001 RoofPanel 최종 파생본으로 별도 배치한다.
        if (sceneName.Contains("B2") && name == "Ceiling" && path.Contains("Room07_CentrifugeHall"))
            return false;
        if (Regex.IsMatch(name, @"^(ObservationWall|ObservationWindowWall)(?:_[EWNS])?$", RegexOptions.IgnoreCase))
        { kind = Kind.Observation; return true; }
        if (Regex.IsMatch(name, @"^(FireDoorWall|FireDoor_Wall)(?:_[EWNS])?$", RegexOptions.IgnoreCase))
        { kind = Kind.FireDoor; return true; }
        if (Regex.IsMatch(name, @"^(Floor|ConnectorFloor)(?:_(NorthOfPen|SouthOfPen|EastOfPen|WestOfPen|BesidePen))?$", RegexOptions.IgnoreCase))
        { kind = Kind.Floor; return true; }
        if (Regex.IsMatch(name, @"^(Ceiling|ConnectorCeiling)(?:_[EWNS])?$", RegexOptions.IgnoreCase))
        { kind = Kind.Ceiling; return true; }
        if (Regex.IsMatch(name, @"^(Wall|SideWall|NorthWall|SouthWall|EastWall|WestWall|ConnectorWall)(?:_[EWNS])?$|^(North|South)_[EW]$", RegexOptions.IgnoreCase))
        {
            kind = sceneName.Contains("B2") || sceneName.Contains("1F") ? Kind.MetalWall : Kind.ConcreteWall;
            return true;
        }
        return false;
    }

    private static bool CanFit(Transform transform, Kind kind, out Vector3 size, out string reason)
    {
        size = Abs(transform.lossyScale);
        reason = "";
        BoxCollider collider = transform.GetComponent<BoxCollider>();
        if (!collider || !collider.enabled || collider.isTrigger)
        { reason = "No original solid BoxCollider; visual-only ornaments are excluded."; return false; }
        for (Transform current = transform; current; current = current.parent)
            if (current.localScale.x <= 0 || current.localScale.y <= 0 || current.localScale.z <= 0)
            { reason = "Mirrored or degenerate source transform is not normalized."; return false; }
        Matrix4x4 matrix = transform.localToWorldMatrix;
        Vector3 a = matrix.MultiplyVector(Vector3.right).normalized;
        Vector3 b = matrix.MultiplyVector(Vector3.up).normalized;
        Vector3 c = matrix.MultiplyVector(Vector3.forward).normalized;
        if (Mathf.Abs(Vector3.Dot(a, b)) > .001f || Mathf.Abs(Vector3.Dot(a, c)) > .001f || Mathf.Abs(Vector3.Dot(b, c)) > .001f ||
            Mathf.Abs(Vector3.Dot(b, Vector3.up)) < .999f)
        { reason = "Sheared or non-upright geometry is preserved."; return false; }
        bool horizontal = kind == Kind.Floor || kind == Kind.Ceiling;
        if (horizontal)
        {
            if (size.y < .08f || size.y > .36f || size.x < 1.75f || size.z < 1.75f || size.x > 40f || size.z > 40f)
            { reason = "Slab dimensions are outside safe rectangular module range."; return false; }
            return true;
        }
        float width = Mathf.Max(size.x, size.z);
        float thickness = Mathf.Min(size.x, size.z);
        if (thickness < .1f || thickness > .4f || size.y < 2.8f || size.y > 8.1f || width < 2.5f || width > 40f)
        { reason = "Wall dimensions are outside safe upright module range."; return false; }
        if (kind == Kind.FireDoor || kind == Kind.Observation)
        {
            float expectedWidth = kind == Kind.FireDoor ? 3f : 4f;
            if (Mathf.Abs(width / expectedWidth - 1f) > .1f || Mathf.Abs(size.y / 4f - 1f) > .1f)
            { reason = "Special wall requires near-authored dimensions; window/door is not stretched or repeated."; return false; }
        }
        else if (!SafeModuleRatio(width, 4f, .6f) || !SafeModuleRatio(size.y, 4f, .6f))
        { reason = "Wall tiling would deform module proportions too much."; return false; }
        return true;
    }

    private static bool SafeModuleRatio(float length, float standard, float minimum)
    {
        float ratio = length / TileCount(length, standard) / standard;
        return ratio >= minimum && ratio <= 1.3f;
    }
    private static int TileCount(float length, float standard) { return Mathf.Max(1, Mathf.RoundToInt(length / standard)); }
    private static Vector3 Abs(Vector3 v) { return new Vector3(Mathf.Abs(v.x), Mathf.Abs(v.y), Mathf.Abs(v.z)); }
    private static Vector3 Divide(Vector3 a, Vector3 b) { return new Vector3(a.x / b.x, a.y / b.y, a.z / b.z); }
    private static bool FinitePositive(Vector3 v)
    { return v.x > .000001f && v.y > .000001f && v.z > .000001f && !float.IsNaN(v.x + v.y + v.z) && !float.IsInfinity(v.x + v.y + v.z); }

    private static bool IsBuiltinCube(Mesh mesh)
    {
        if (!mesh || mesh.name != "Cube") return false;
        string path = AssetDatabase.GetAssetPath(mesh);
        if (!(string.IsNullOrEmpty(path) || path.Contains("unity default resources") || path.Contains("unity_builtin_extra"))) return false;
        return (mesh.bounds.size - Vector3.one).sqrMagnitude < .000001f && mesh.bounds.center.sqrMagnitude < .000001f;
    }

    private static Bounds ActiveMeshBoundsInSpace(GameObject instance, Transform space)
    {
        bool any = false;
        Bounds result = new Bounds();
        foreach (MeshRenderer renderer in instance.GetComponentsInChildren<MeshRenderer>(true))
        {
            if (!renderer.enabled || !renderer.gameObject.activeInHierarchy) continue;
            MeshFilter filter = renderer.GetComponent<MeshFilter>();
            if (!filter || !filter.sharedMesh) throw new InvalidOperationException("Active architecture renderer has no mesh.");
            if (renderer.sharedMaterials.Length == 0 || renderer.sharedMaterials.Any(m => !m || !m.shader))
                throw new InvalidOperationException("Active architecture renderer has a missing material/shader.");
            Bounds bounds = filter.sharedMesh.bounds;
            Matrix4x4 matrix = space.worldToLocalMatrix * renderer.transform.localToWorldMatrix;
            for (int x = 0; x < 2; x++)
            for (int y = 0; y < 2; y++)
            for (int z = 0; z < 2; z++)
            {
                Vector3 point = matrix.MultiplyPoint3x4(bounds.center + Vector3.Scale(bounds.extents, new Vector3(x == 0 ? -1 : 1, y == 0 ? -1 : 1, z == 0 ? -1 : 1)));
                if (!any) { result = new Bounds(point, Vector3.zero); any = true; }
                else result.Encapsulate(point);
            }
        }
        if (!any) throw new InvalidOperationException("Architecture prefab has no enabled mesh renderer.");
        return result;
    }

    private static Bounds ActiveRendererWorldBounds(GameObject root)
    {
        Renderer[] renderers = root.GetComponentsInChildren<Renderer>(true).Where(r => r.enabled && r.gameObject.activeInHierarchy).ToArray();
        if (renderers.Length == 0) throw new InvalidOperationException("New architecture has no enabled Renderer.");
        Bounds result = renderers[0].bounds;
        for (int index = 1; index < renderers.Length; index++) result.Encapsulate(renderers[index].bounds);
        return result;
    }
    private static float BoundsError(Bounds a, Bounds b)
    {
        Vector3 min = Abs(a.min - b.min), max = Abs(a.max - b.max);
        return Mathf.Max(Mathf.Max(min.x, min.y, min.z), Mathf.Max(max.x, max.y, max.z));
    }
    private static string HierarchyPath(Transform transform)
    {
        var names = new List<string>();
        for (Transform current = transform; current; current = current.parent) names.Add(current.name);
        names.Reverse();
        return string.Join("/", names);
    }
    private static void Skip(Entry entry, Report report, string reason)
    { entry.status = "skipped_preserved_original"; entry.reason = reason; report.skippedSurfaces++; }
    private static void WriteReport(Report report)
    {
        string folder = Path.GetFullPath(Path.Combine(Application.dataPath, "../../..", "tmp/Asset_Placement_20261103/ArchitectureReports"));
        Directory.CreateDirectory(folder);
        File.WriteAllText(Path.Combine(folder, report.scene + "_architecture.json"), JsonUtility.ToJson(report, true));
    }
}
#endif

// [주석]
// - 반복 타일의 합집합은 기존 Cube의 bounds와 일치하며 새 충돌/기능/재질을 만들지 않는다.
// - 벽은 두께가 얇은 축을 법선으로 삼는다. 측면 벽은 모델 자식만 Y 90도로 돌린다.
// - 재제작 원본은 바닥의 상세가 아랫면, 천장의 상세가 윗면에 있다. 새 바닥/천장
//   visual 자식만 X 180도로 돌려 각각 위/아래에서 패턴을 보이게 한다. B5는 제외한다.
// - 관찰 배경은 기존 불투명 의도를 유지한다. 근사 치수의 특별 벽만 개별 교체한다.
// - 원본 Renderer는 최종 bounds 검증 후 꺼진다. 저장·실제 시점 검수는 호출자가 한다.
