// 작성자 송예찬 / 2026-11-03
// [의사코드]
// 1. 확대된 돔의 새 유리·충돌·양면 문 한 벌과 문 충돌 부모를 확인한다.
// 2. 닫힌 문을 바깥/안쪽에서 9점씩 쏘아 각각 가까운 문에 막히는지 확인한다.
// 3. 두 문을 세계 Y축으로 열고 같은 9점이 실제로 관통하는지 확인한다.
// 4. 개구 좌우의 유리는 계속 막혀 있는지 확인하고 모든 문/충돌 pose를 복원한다.
// 5. 검사와 복원 결과를 JSON에 남긴다. 게임 스크립트나 개폐 동작을 추가하지 않는다.

// [코딩]
#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

public static class HatchGeometryReview
{
    private const string ExteriorPivot = "DualFoodHatch_DoorExterior_Pivot";
    private const string InteriorPivot = "DualFoodHatch_DoorInterior_Pivot";
    private const string ExteriorCollider = "DualFoodHatch_DoorExterior_Collider";
    private const string InteriorCollider = "DualFoodHatch_DoorInterior_Collider";
    private const string ShellSegment = "ObservationPod_CollisionSegment_";
    private static readonly float[] GridX = { -.24f, 0f, .24f };
    private static readonly float[] GridY = { -.13f, 0f, .13f };

    [Serializable]
    public sealed class HitRecord
    {
        public string path;
        public string kind;
        public float distance;
        public Vector3 point;
    }

    [Serializable]
    public sealed class RayRecord
    {
        public string test;
        public float horizontalOffset;
        public float verticalOffset;
        public Vector3 origin;
        public Vector3 destination;
        public string expectation;
        public bool pass;
        public HitRecord[] podHits;
    }

    [Serializable]
    public sealed class DoorParts
    {
        public string path;
        public int meshFilters;
        public int renderers;
        public int materialSlots;
        public long triangles;
        public int vertices;
        public string[] materialNames;
        public Vector3 worldBoundsSize;
        public Vector3 worldHingePosition;
        public Vector3 originalLocalPosition;
        public Quaternion originalLocalRotation;
        public Vector3 originalLocalScale;
    }

    [Serializable]
    public sealed class Report
    {
        public string author = "송예찬";
        public string timestampUtc;
        public string scene;
        public string podPath;
        public Vector3 podScale;
        public Vector3 plannedHatchCenter;
        public Vector3 measuredHatchCenter;
        public float hatchCenterError;
        public float exteriorOpenAngle = -105f;
        public float interiorOpenAngle = 105f;
        public string rotationAxis = "World Y. Original local rotations are restored exactly.";
        public int activeShellColliders;
        public int inactiveShellColliders;
        public int activeHatchColliders;
        public int activeGlassRenderers;
        public string[] activeLegacyHatchRenderers;
        public bool doorCollidersParentedToPivots;
        public DoorParts exterior;
        public DoorParts interior;
        public bool identicalDoorPartCounts;
        public bool identicalDoorMaterials;
        public float doorBoundsSizeDifference;
        public string sourcePartContract = "V0.02: both faces of EACH leaf have matching steel insets, pull handles, mounts, hinges and latch finishes. Per door: one shared leaf, two insets, two pulls/four mounts, four hinge knuckles and two latch covers; one merged visual mesh with the original material slot order. The inward hardware leaves at least 0.314m empty tunnel depth. Front/back frames share one static tunnel mesh.";
        public List<RayRecord> closedExterior = new List<RayRecord>();
        public List<RayRecord> closedInterior = new List<RayRecord>();
        public List<RayRecord> openExterior = new List<RayRecord>();
        public List<RayRecord> openInterior = new List<RayRecord>();
        public List<RayRecord> sideGlassClosed = new List<RayRecord>();
        public List<RayRecord> sideGlassOpen = new List<RayRecord>();
        public bool transformsRestored;
        public bool pass;
        public List<string> errors = new List<string>();
        public string note = "Editor geometry verification only. Door opening is temporary; no gameplay component or interaction is created. Raycasts ignore objects outside the supplied pod hierarchy.";
    }

    private sealed class Pose
    {
        public Transform transform;
        public Transform parent;
        public Vector3 localPosition;
        public Quaternion localRotation;
        public Vector3 localScale;

        public Pose(Transform value)
        {
            transform = value;
            parent = value.parent;
            localPosition = value.localPosition;
            localRotation = value.localRotation;
            localScale = value.localScale;
        }

        public void Restore()
        {
            if (!transform) return;
            // Verify never reparents. A changed parent is a failure, not an instruction to alter hierarchy.
            if (transform.parent != parent)
                throw new InvalidOperationException("Parent changed during verification: " + PathOf(transform));
            transform.localPosition = localPosition;
            transform.localRotation = localRotation;
            transform.localScale = localScale;
        }

        public bool Matches()
        {
            return transform && transform.parent == parent &&
                transform.localPosition.Equals(localPosition) &&
                transform.localRotation.Equals(localRotation) &&
                transform.localScale.Equals(localScale);
        }
    }

    // 선택 호출. MeshCollider를 추가한 다음 사용하며 이미 연결된 문은 다시 바꾸지 않는다.
    public static string WireDoorColliders(Transform pod)
    {
        RequireEditMode(pod);
        int changed = 0;
        foreach (var pair in new[] { new[] { ExteriorPivot, ExteriorCollider }, new[] { InteriorPivot, InteriorCollider } })
        {
            Transform door = FindUnique(pod, pair[0]);
            Transform collision = FindUnique(pod, pair[1]);
            if (collision.IsChildOf(door)) continue;
            Vector3 position = collision.position;
            Quaternion rotation = collision.rotation;
            Vector3 scale = collision.lossyScale;
            collision.SetParent(door, true);
            if ((collision.position - position).sqrMagnitude > 1e-8f ||
                Quaternion.Angle(collision.rotation, rotation) > .01f ||
                (collision.lossyScale - scale).sqrMagnitude > 1e-8f)
                throw new InvalidOperationException("World pose changed while wiring " + collision.name);
            changed++;
        }
        Physics.SyncTransforms();
        return "Door collider parents wired with world pose preserved: " + changed;
    }

    public static string Verify(Transform pod, string outputDir)
    {
        RequireEditMode(pod);
        if (string.IsNullOrWhiteSpace(outputDir)) throw new ArgumentException("Output directory required.");
        Directory.CreateDirectory(outputDir);
        var report = new Report
        {
            timestampUtc = DateTime.UtcNow.ToString("o"),
            scene = pod.gameObject.scene.path,
            podPath = PathOf(pod),
            podScale = pod.lossyScale,
            plannedHatchCenter = pod.position + pod.rotation * new Vector3(0, 1.05f, -3.975f),
        };
        var poses = new List<Pose>();
        try
        {
            Check(report, (pod.lossyScale - new Vector3(3, 2, 3)).sqrMagnitude < .0001f,
                "Expected preserved pod world scale (3,2,3).");
            Check(report, Vector3.Dot(pod.up, Vector3.up) > .999f, "Pod must remain upright.");
            Transform exterior = FindUnique(pod, ExteriorPivot);
            Transform interior = FindUnique(pod, InteriorPivot);
            Transform exteriorCollision = FindUnique(pod, ExteriorCollider);
            Transform interiorCollision = FindUnique(pod, InteriorCollider);
            foreach (var t in new[] { exterior, interior, exteriorCollision, interiorCollision }.Distinct())
                poses.Add(new Pose(t));

            report.doorCollidersParentedToPivots = exteriorCollision.IsChildOf(exterior) && interiorCollision.IsChildOf(interior);
            Check(report, report.doorCollidersParentedToPivots, "Door Collider transforms must be children of their matching door pivots. Call WireDoorColliders first.");
            report.exterior = Parts(exterior);
            report.interior = Parts(interior);
            report.identicalDoorPartCounts = report.exterior.meshFilters == report.interior.meshFilters &&
                report.exterior.renderers == report.interior.renderers &&
                report.exterior.materialSlots == report.interior.materialSlots &&
                report.exterior.triangles == report.interior.triangles;
            report.identicalDoorMaterials = report.exterior.materialNames.SequenceEqual(report.interior.materialNames);
            report.doorBoundsSizeDifference = (report.exterior.worldBoundsSize - report.interior.worldBoundsSize).magnitude;
            Check(report, report.identicalDoorPartCounts && report.identicalDoorMaterials,
                "Interior/exterior door mesh, index or material counts differ.");
            Check(report, report.doorBoundsSizeDifference < .005f, "Interior/exterior door world bounds differ.");
            report.measuredHatchCenter = (exterior.position + interior.position) * .5f;
            report.hatchCenterError = (report.measuredHatchCenter - report.plannedHatchCenter).magnitude;
            Check(report, report.hatchCenterError < .035f, "Hatch pivots do not match the planned opening center.");

            Collider[] colliders = pod.GetComponentsInChildren<Collider>(true);
            report.activeShellColliders = colliders.Count(c => IsShell(c) && Active(c));
            report.inactiveShellColliders = colliders.Count(c => IsShell(c) && !Active(c));
            report.activeHatchColliders = colliders.Count(c => c.name.StartsWith("DualFoodHatch_", StringComparison.Ordinal) && Active(c));
            report.activeGlassRenderers = pod.GetComponentsInChildren<Renderer>(true)
                .Count(r => r.name == "ObservationPod_GlassShell" && r.enabled && r.gameObject.activeInHierarchy);
            report.activeLegacyHatchRenderers = pod.GetComponentsInChildren<Renderer>(true)
                .Where(r => r.enabled && r.gameObject.activeInHierarchy &&
                    (r.name.StartsWith("ObservationPod_Hatch", StringComparison.Ordinal) || r.name == "ObservationPod_FoodHatch_Closed"))
                .Select(r => PathOf(r.transform)).ToArray();
            Check(report, report.activeShellColliders == 24, "Expected exactly one active shell Collider set (24 panels).");
            Check(report, report.activeHatchColliders == 6, "Expected exactly six active hatch Colliders (two doors and four tunnel walls).");
            Check(report, report.activeGlassRenderers == 1 && report.activeLegacyHatchRenderers.Length == 0,
                "Legacy hatch or duplicate glass Renderer is still active.");
            Check(report, exteriorCollision.GetComponentsInChildren<Collider>().Any(Active) &&
                interiorCollision.GetComponentsInChildren<Collider>().Any(Active), "A door Collider is missing or disabled.");

            Physics.SyncTransforms();
            CheckGrid(report, pod, exterior, interior, false, report.closedExterior, report.closedInterior);
            CheckSideGlass(report, pod, "closed", report.sideGlassClosed);

            // 세계 Y축으로 회전해 FBX 내부 X90 좌표 보정에 의존하지 않는다.
            Quaternion exteriorOriginalWorld = exterior.rotation;
            Quaternion interiorOriginalWorld = interior.rotation;
            exterior.rotation = Quaternion.AngleAxis(report.exteriorOpenAngle, Vector3.up) * exteriorOriginalWorld;
            interior.rotation = Quaternion.AngleAxis(report.interiorOpenAngle, Vector3.up) * interiorOriginalWorld;
            Physics.SyncTransforms();
            CheckGrid(report, pod, exterior, interior, true, report.openExterior, report.openInterior);
            CheckSideGlass(report, pod, "open", report.sideGlassOpen);
        }
        catch (Exception exception)
        {
            report.errors.Add(exception.GetType().Name + ": " + exception.Message);
        }
        finally
        {
            // Restore parent door first and then the exact original child Collider poses.
            foreach (Pose pose in poses)
            {
                try { pose.Restore(); }
                catch (Exception exception) { report.errors.Add("Restore failed: " + exception.Message); }
            }
            Physics.SyncTransforms();
            report.transformsRestored = poses.All(p => p.Matches());
            Check(report, report.transformsRestored, "Door/Collider local transforms were not restored exactly.");
            report.pass = report.errors.Count == 0;
            File.WriteAllText(System.IO.Path.Combine(outputDir, "Unity_Hatch_Geometry_Verification.json"), JsonUtility.ToJson(report, true));
        }
        if (!report.pass) throw new InvalidOperationException("Hatch geometry verification failed: " + string.Join(" | ", report.errors));
        return "Hatch verified: closed 18/18 blocked, open 18/18 clear, side glass 12/12 blocked; door/Collider poses restored.";
    }

    private static void CheckGrid(Report report, Transform pod, Transform exterior, Transform interior, bool open,
        List<RayRecord> exteriorResults, List<RayRecord> interiorResults)
    {
        Vector3 center = report.plannedHatchCenter;
        Vector3 front = -pod.forward.normalized;
        foreach (float x in GridX)
        foreach (float y in GridY)
        {
            Vector3 sample = center + pod.right.normalized * x + Vector3.up * y;
            var outside = Cast(pod, sample + front * .7f, sample - front * .7f,
                (open ? "open" : "closed") + "_exterior", x, y, open ? null : exterior, false);
            var inside = Cast(pod, sample - front * .7f, sample + front * .7f,
                (open ? "open" : "closed") + "_interior", x, y, open ? null : interior, false);
            exteriorResults.Add(outside);
            interiorResults.Add(inside);
            Check(report, outside.pass, outside.test + " ray failed at " + x + "," + y);
            Check(report, inside.pass, inside.test + " ray failed at " + x + "," + y);
        }
    }

    private static void CheckSideGlass(Report report, Transform pod, string stage, List<RayRecord> results)
    {
        Vector3 front = -pod.forward.normalized;
        foreach (float x in new[] { -.65f, .65f })
        foreach (float y in GridY)
        {
            Vector3 sample = report.plannedHatchCenter + pod.right.normalized * x + Vector3.up * y;
            var ray = Cast(pod, sample + front * .7f, sample - front * .7f, stage + "_side_glass", x, y, null, true);
            results.Add(ray);
            Check(report, ray.pass, ray.test + " is not blocked by shell at " + x + "," + y);
        }
    }

    private static RayRecord Cast(Transform pod, Vector3 origin, Vector3 destination, string test,
        float x, float y, Transform expectedDoor, bool shellExpected)
    {
        Vector3 delta = destination - origin;
        RaycastHit[] hits = Physics.RaycastAll(origin, delta.normalized, delta.magnitude, ~0, QueryTriggerInteraction.Ignore)
            .Where(h => Active(h.collider) && h.collider.transform.IsChildOf(pod)).OrderBy(h => h.distance).ToArray();
        bool passed = shellExpected ? hits.Length > 0 && IsShell(hits[0].collider) :
            expectedDoor ? hits.Length > 0 && hits[0].collider.transform.IsChildOf(expectedDoor) : hits.Length == 0;
        return new RayRecord
        {
            test = test, horizontalOffset = x, verticalOffset = y, origin = origin, destination = destination,
            expectation = shellExpected ? "First pod hit is a shell panel" : expectedDoor ? "First pod hit is " + expectedDoor.name : "No pod Collider hit across the open transfer cavity",
            pass = passed,
            podHits = hits.Select(h => new HitRecord { path = PathOf(h.transform), kind = IsShell(h.collider) ? "shell" : "pod", distance = h.distance, point = h.point }).ToArray(),
        };
    }

    private static DoorParts Parts(Transform door)
    {
        var filters = door.GetComponentsInChildren<MeshFilter>(true).Where(f => f.sharedMesh).ToArray();
        var renderers = door.GetComponentsInChildren<Renderer>(true).Where(r => r.enabled && r.gameObject.activeInHierarchy).ToArray();
        // Collider FBX may retain disabled MeshRenderers/MeshFilters. Only count the visual branches.
        filters = filters.Where(f => f.GetComponent<Renderer>() && f.GetComponent<Renderer>().enabled && f.gameObject.activeInHierarchy).ToArray();
        Bounds bounds = renderers.Length > 0 ? renderers[0].bounds : new Bounds(door.position, Vector3.zero);
        foreach (Renderer renderer in renderers.Skip(1)) bounds.Encapsulate(renderer.bounds);
        long triangles = 0;
        foreach (MeshFilter filter in filters)
            for (int sub = 0; sub < filter.sharedMesh.subMeshCount; sub++)
                triangles += (long)filter.sharedMesh.GetIndexCount(sub) / 3L;
        return new DoorParts
        {
            path = PathOf(door), meshFilters = filters.Length, renderers = renderers.Length,
            materialSlots = renderers.Sum(r => r.sharedMaterials.Length),
            materialNames = renderers.SelectMany(r => r.sharedMaterials).Select(m => m ? m.name : "MISSING").OrderBy(n => n, StringComparer.Ordinal).ToArray(),
            triangles = triangles, vertices = filters.Sum(f => f.sharedMesh.vertexCount), worldBoundsSize = bounds.size,
            worldHingePosition = door.position, originalLocalPosition = door.localPosition,
            originalLocalRotation = door.localRotation, originalLocalScale = door.localScale,
        };
    }

    private static Transform FindUnique(Transform pod, string name)
    {
        Transform[] values = pod.GetComponentsInChildren<Transform>(true)
            .Where(t => t.name == name && t.gameObject.activeInHierarchy).ToArray();
        if (values.Length != 1) throw new InvalidOperationException("Expected one active " + name + ", found " + values.Length);
        return values[0];
    }
    private static bool IsShell(Collider value) { return value && value.name.StartsWith(ShellSegment, StringComparison.Ordinal); }
    private static bool Active(Collider value) { return value && value.enabled && value.gameObject.activeInHierarchy; }
    private static void Check(Report report, bool condition, string error) { if (!condition) report.errors.Add(error); }
    private static string PathOf(Transform value) { return value.parent ? PathOf(value.parent) + "/" + value.name : value.name; }
    private static void RequireEditMode(Transform pod)
    {
        if (!pod) throw new ArgumentNullException("pod");
        if (EditorApplication.isPlayingOrWillChangePlaymode) throw new InvalidOperationException("Hatch review requires edit mode.");
    }
}
#endif

// [주석]
// 닫힌 문을 검사한 뒤 세계 Y축으로 열기 때문에 FBX의 내부 축 보정과 무관하게 수직 힌지가 된다.
// 문과 문 자식 충돌체의 로컬 pose를 finally에서 원래 값 그대로 복원한다. Collider를 숨기거나 삭제하지 않는다.
// 실제 사용 시 모델 생성·MeshCollider 연결·WireDoorColliders 순서 뒤 Verify를 호출한다.
