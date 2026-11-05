using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEngine.SceneManagement;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System.Collections.Generic;

public static class ReviewLevels
{
    public static object FinalState()
    {
        var scene=SceneManager.GetActiveScene();
        if(scene.name!="Level_B4_Stealth" || EditorApplication.isPlaying) throw new InvalidOperationException("Expected B4 Edit Mode");
        UnityEditor.SceneManagement.EditorSceneManager.SaveScene(scene);
        return new {scene=scene.path,scene.isDirty,playing=EditorApplication.isPlaying,compiling=EditorApplication.isCompiling,runInBackground=Application.runInBackground,temporaryObjects=scene.GetRootGameObjects().SelectMany(item=>item.GetComponentsInChildren<Transform>(true)).Where(item=>item.name.StartsWith("Temporary")).Select(item=>item.name).ToArray()};
    }
    public static object AuditConnections()
    {
        string repository="C:/GitHubProjects/After_Seconds";
        var scene=SceneManager.GetActiveScene();
        var floor=JObject.Parse(File.ReadAllText(repository+"/Docs/도면/잠입_탐색/layout.json"))["floors"].First(item=>(string)item["floor"]=="B4");
        var doors=new List<object>();
        Physics.SyncTransforms();
        foreach(var door in floor["doors"]) {
            var center=new Vector3((float)door["x"]-24,0,(float)door["y"]-16);
            var normal=(string)door["axis"]=="H" ? Vector3.forward : Vector3.right;
            int blocked=0;
            for(int sample=-3;sample<=3;sample++) {
                var point=center+normal*(sample*0.2f);
                var hits=Physics.OverlapCapsule(point+Vector3.up*0.34f,point+Vector3.up*1.54f,0.3f,~0,QueryTriggerInteraction.Ignore).Where(item=>!item.transform.root.name.StartsWith("Player")).ToArray();
                if(hits.Length>0) blocked++;
            }
            bool expectedOpen=(string)door["state"]=="open";
            doors.Add(new {a=(string)door["a"],b=(string)door["b"],expectedOpen,blockedSamples=blocked,passed=expectedOpen ? blocked==0 : blocked>0});
        }
        var windows=new List<object>();
        foreach(float v in new[]{6.45f,11.6f,16.45f,21.6f}) {
            var left=new Vector3(-13,1.8f,v-16);
            var right=new Vector3(-11,1.8f,v-16);
            bool fromLeft=Physics.Raycast(left,Vector3.right,out var leftHit,2,~0,QueryTriggerInteraction.Ignore) && leftHit.collider.name=="ObservationGlass";
            bool fromRight=Physics.Raycast(right,Vector3.left,out var rightHit,2,~0,QueryTriggerInteraction.Ignore) && rightHit.collider.name=="ObservationGlass";
            windows.Add(new {v,fromLeft,fromRight});
        }
        var dependencies=AssetDatabase.GetDependencies(scene.path,true).Where(path=>path.StartsWith("Assets/")).ToArray();
        var output=new{doors,windows,dependencies=dependencies.Length,missingDependencies=dependencies.Where(path=>!File.Exists(path)).ToArray(),scene=scene.path};
        File.WriteAllText(repository+"/Docs/검수/2026-11-06_B5_B4/B4/connections.json",JsonConvert.SerializeObject(output,Formatting.Indented));
        return output;
    }

    public static object CleanCaptureImports()
    {
        string relative="Assets/Temp/B4Review";
        string target=Path.GetFullPath(relative);
        string allowed=Path.GetFullPath(Path.Combine(Application.dataPath,"Temp","B4Review"));
        if(!String.Equals(target,allowed,StringComparison.OrdinalIgnoreCase)) throw new InvalidOperationException("Unexpected capture folder");
        bool deleted=AssetDatabase.IsValidFolder(relative) && AssetDatabase.DeleteAsset(relative);
        if(Directory.Exists("Assets/Temp") && !Directory.EnumerateFileSystemEntries("Assets/Temp").Any()) AssetDatabase.DeleteAsset("Assets/Temp");
        return new{deleted,target};
    }
    public static object CaptureB4()
    {
        var directory = "C:/GitHubProjects/After_Seconds/Docs/검수/2026-11-06_B5_B4/B4";
        Capture(directory+"/01_Arrival.png",new Vector3(17,1.7f,10),new Vector3(12,1.7f,9));
        Capture(directory+"/02_ObservationCorridor.png",new Vector3(-10,1.7f,5.5f),new Vector3(-11.3f,1.7f,-8));
        Capture(directory+"/03_ObservationRoom.png",new Vector3(-18.8f,1.7f,-4.1f),new Vector3(-12.3f,1.6f,-9.4f));
        Capture(directory+"/04_ControlDeck.png",new Vector3(0,1.7f,6.8f),new Vector3(6,2.4f,1));
        Capture(directory+"/05_DeckStairs.png",new Vector3(3.6f,1.7f,-2.2f),new Vector3(4.3f,2.2f,2.5f));
        Capture(directory+"/06_DeckView.png",new Vector3(6.3f,4.2f,3.2f),new Vector3(3.4f,2.0f,-2.3f));
        Capture(directory+"/07_Analysis.png",new Vector3(10.5f,1.7f,-8),new Vector3(1,1.5f,-9.5f));
        Capture(directory+"/08_StairB.png",new Vector3(22.6f,1.7f,7),new Vector3(22.5f,3.5f,13.6f));
        Capture(directory+"/09_SupportRooms.png",new Vector3(-3,1.7f,13.5f),new Vector3(8,1.6f,14));
        var ceilings = UnityEngine.Object.FindObjectsByType<MeshRenderer>().Where(renderer=>renderer.name.StartsWith("B4_Ceiling_")).ToArray();
        var enabled = ceilings.Select(renderer=>renderer.enabled).ToArray();
        try {
            foreach (var renderer in ceilings) renderer.enabled=false;
            Capture(directory+"/10_Overview.png",new Vector3(0,62,9),new Vector3(0,0,0),52);
        }
        finally {
            for (int index=0;index<ceilings.Length;index++) ceilings[index].enabled=enabled[index];
        }
        return new { directory,captures=10,mode="Edit-mode offscreen camera; overview temporarily hides ceilings" };
    }

    public static object AuditScene()
    {
        var scene = SceneManager.GetActiveScene();
        var level = scene.GetRootGameObjects().First(root=>root.name.StartsWith("B4_"));
        var renderers = level.GetComponentsInChildren<Renderer>(true);
        var lowerLod = new HashSet<Renderer>(level.GetComponentsInChildren<LODGroup>().SelectMany(group=>group.GetLODs().Skip(1).SelectMany(lod=>lod.renderers)));
        long triangles=0;
        var missing = new List<string>();
        foreach (var renderer in renderers.Where(renderer=>renderer.enabled && renderer.gameObject.activeInHierarchy && !lowerLod.Contains(renderer))) {
            var filter=renderer.GetComponent<MeshFilter>();
            var mesh=renderer is SkinnedMeshRenderer skinned ? skinned.sharedMesh : filter ? filter.sharedMesh : null;
            if (mesh==null) {missing.Add(renderer.name+": mesh");continue;}
            for (int index=0;index<mesh.subMeshCount;index++) triangles+=mesh.GetIndexCount(index)/3;
            if (renderer.sharedMaterials.Any(material=>material==null || material.shader==null || material.shader.name.Contains("Error"))) missing.Add(renderer.name+": material/shader");
        }
        int scripts = level.GetComponentsInChildren<Transform>(true).Sum(item=>GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(item.gameObject));
        var output = new {scene=scene.path,highestLodTriangles=triangles,renderers=renderers.Length,lodGroups=level.GetComponentsInChildren<LODGroup>().Length,colliders=level.GetComponentsInChildren<Collider>().Length,missingAssets=missing,missingScripts=scripts,customRuntimeBehaviours=level.GetComponentsInChildren<MonoBehaviour>(true).Select(item=>item.GetType().FullName).Distinct().ToArray()};
        File.WriteAllText("C:/GitHubProjects/After_Seconds/Docs/검수/2026-11-06_B5_B4/B4/scene_audit.json",JsonConvert.SerializeObject(output,Formatting.Indented));
        return output;
    }

    static object Walk(string name, List<Vector3> points, float expectedHeight)
    {
        var probe = new GameObject("TemporaryControllerProbe") {hideFlags=HideFlags.HideAndDontSave};
        var controller=probe.AddComponent<CharacterController>();
        controller.radius=0.28f;
        controller.height=1.8f;
        controller.center=Vector3.up*0.9f;
        controller.stepOffset=0.3f;
        controller.skinWidth=0.08f;
        controller.slopeLimit=45;
        controller.minMoveDistance=0;
        probe.transform.position=points[0]+Vector3.up*0.12f;
        Physics.SyncTransforms();
        var failures=new List<object>();
        int moves=0;
        try {
            foreach (var target in points.Skip(1)) {
                int limit=Mathf.CeilToInt(Vector3.Distance(new Vector3(probe.transform.position.x,0,probe.transform.position.z),new Vector3(target.x,0,target.z))/0.035f)+80;
                bool reached=false;
                for (int step=0;step<limit;step++) {
                    var displacement=target-probe.transform.position;
                    displacement.y=0;
                    if (displacement.magnitude<0.06f) {reached=true;break;}
                    controller.Move(Vector3.ClampMagnitude(displacement,0.035f)+Vector3.down*0.045f);
                    moves++;
                }
                if (!reached) {failures.Add(new {target=target.ToString("F2"),actual=probe.transform.position.ToString("F2")});break;}
            }
            for(int step=0;step<10;step++) controller.Move(Vector3.down*0.045f);
            float height=probe.transform.position.y;
            return new {name,moves,failures,finalPosition=probe.transform.position.ToString("F3"),expectedHeight,heightError=Mathf.Abs(height-expectedHeight),passed=failures.Count==0 && Mathf.Abs(height-expectedHeight)<0.15f};
        }
        finally {UnityEngine.Object.DestroyImmediate(probe);}
    }

    public static object WalkB4()
    {
        var player = UnityEngine.Object.FindObjectsByType<CharacterController>().First(controller=>controller.name.StartsWith("Player"));
        bool wasEnabled=player.enabled;
        var results=new List<object>();
        try {
            player.enabled=false;
            var routes=JObject.Parse(File.ReadAllText("C:/GitHubProjects/After_Seconds/Docs/도면/잠입_탐색/플레이어_예상이동/player_routes.json"))["routes"].Where(route=>(string)route["floor"]=="B4");
            foreach(var route in routes) {
                var points=route["legs"].SelectMany(leg=>leg["points"]).Select(point=>new Vector3((float)point[0]-24,0,(float)point[1]-16)).ToList();
                results.Add(Walk("Route_"+(string)route["variant"],points,0));
            }
            results.Add(Walk("Deck_Up",new List<Vector3>{new Vector3(4.2f,0,-1.6f),new Vector3(4.2f,0,3.4f),new Vector3(6.1f,0,3.4f)},2.5f));
            results.Add(Walk("Deck_Down",new List<Vector3>{new Vector3(6.1f,2.5f,3.4f),new Vector3(4.2f,0,3.4f),new Vector3(4.2f,0,-1.6f)},0));
            results.Add(Walk("StairB_Up",new List<Vector3>{new Vector3(22.65f,0,8.5f),new Vector3(22.65f,0,14.7f),new Vector3(20.75f,0,14.7f),new Vector3(20.75f,0,7.6f)},6.4f));
            results.Add(Walk("StairB_Down",new List<Vector3>{new Vector3(20.75f,6.4f,7.6f),new Vector3(20.75f,0,14.7f),new Vector3(22.65f,0,14.7f),new Vector3(22.65f,0,8.5f)},0));
        }
        finally {player.enabled=wasEnabled;}
        var output=new {mode="Temporary CharacterController.Move in Editor; no input/AI gameplay",settings=new {radius=0.28,height=1.8,stepOffset=0.3,skinWidth=0.08,slopeLimit=45},results};
        File.WriteAllText("C:/GitHubProjects/After_Seconds/Docs/검수/2026-11-06_B5_B4/B4/controller_audit.json",JsonConvert.SerializeObject(output,Formatting.Indented));
        return output;
    }
    public static object AuditRoutes()
    {
        var scene = SceneManager.GetActiveScene();
        var floor = scene.name.Contains("B5") ? "B5" : "B4";
        var repository = "C:/GitHubProjects/After_Seconds";
        var routes = JObject.Parse(File.ReadAllText(repository + "/Docs/도면/잠입_탐색/플레이어_예상이동/player_routes.json"))["routes"].Where(route => (string)route["floor"] == floor);
        var results = new List<object>();
        Physics.SyncTransforms();
        foreach (var route in routes) {
            int samples = 0;
            var failures = new List<object>();
            foreach (var leg in route["legs"]) {
                var points = leg["points"].ToArray();
                for (int segment = 1; segment < points.Length; segment++) {
                    var start = new Vector3((float)points[segment - 1][0] - 24, 0, (float)points[segment - 1][1] - 16);
                    var end = new Vector3((float)points[segment][0] - 24, 0, (float)points[segment][1] - 16);
                    int steps = Mathf.Max(1, Mathf.CeilToInt(Vector3.Distance(start, end) / 0.25f));
                    for (int sample = 0; sample <= steps; sample++) {
                        var position = Vector3.Lerp(start, end, (float)sample / steps);
                        var hits = Physics.OverlapCapsule(position + Vector3.up * 0.34f, position + Vector3.up * 1.54f, 0.30f, ~0, QueryTriggerInteraction.Ignore).Where(hit => !hit.transform.root.name.StartsWith("Player") && !hit.name.StartsWith("Temporary")).ToArray();
                        samples++;
                        if (hits.Length > 0) failures.Add(new { position = position.ToString("F2"), objects = hits.Select(hit => hit.name).Distinct().ToArray() });
                    }
                }
            }
            results.Add(new { variant = (string)route["variant"], samples, blockedSamples = failures.Count, failures });
        }
        var output = new { floor, scene = scene.path, capsuleDiameter = 0.6, capsuleHeight = 1.8, samplingMetres = 0.25, mode = "Static capsule overlap only", routes = results };
        var file = repository + "/Docs/검수/2026-11-06_B5_B4/" + floor + "/route_audit.json";
        Directory.CreateDirectory(Path.GetDirectoryName(file));
        File.WriteAllText(file, JsonConvert.SerializeObject(output, Formatting.Indented));
        return output;
    }
    public static object CaptureB5()
    {
        var directory = "C:/GitHubProjects/After_Seconds/Docs/검수/2026-11-06_B5_B4/B5";
        Capture(directory + "/01_Guard.png", new Vector3(3.0f, 1.65f, -6.85f), new Vector3(1.12f, 1.55f, -6.87f), 46);
        Capture(directory + "/02_NorthPump.png", new Vector3(8.9f, 1.7f, -7.8f), new Vector3(6, 0.75f, -10.2f));
        Capture(directory + "/03_SouthPumpPipes.png", new Vector3(3.4f, 1.7f, 3.7f), new Vector3(7.0f, 1.65f, 6.4f));
        Capture(directory + "/04_StairLanding.png", new Vector3(18.3f, 5.5f, 3.4f), new Vector3(16.3f, 5.6f, 6.3f));
        Capture(directory + "/05_WallJoints.png", new Vector3(13.5f, 1.7f, 13.5f), new Vector3(13.5f, 1.8f, 4));
        return new { directory, captures = 5, mode = "Edit-mode offscreen camera; not gameplay evidence" };
    }
    public static object Inspect()
    {
        var scene = SceneManager.GetActiveScene();
        var transforms = scene.GetRootGameObjects().SelectMany(root => root.GetComponentsInChildren<Transform>(true)).ToArray();
        return new {
            scene = scene.path,
            dirty = scene.isDirty,
            roots = scene.GetRootGameObjects().Select(root => new { root.name, position = root.transform.position.ToString("F2") }).ToArray(),
            targets = transforms.Where(item => item.name.Contains("G2_") || item.name.Contains("Pump") || item.name.Contains("Stair") || item.name.Contains("Player") || item.name.Contains("Camera")).Select(item => new { item.name, position = item.position.ToString("F2"), rotation = item.eulerAngles.ToString("F1"), bounds = BoundsOf(item.gameObject).ToString() }).Take(100).ToArray()
        };
    }

    public static Bounds BoundsOf(GameObject target)
    {
        var renderers = target.GetComponentsInChildren<Renderer>(true);
        if (renderers.Length == 0) return new Bounds(target.transform.position, Vector3.zero);
        var bounds = renderers[0].bounds;
        foreach (var renderer in renderers.Skip(1)) bounds.Encapsulate(renderer.bounds);
        return bounds;
    }

    public static void Capture(string file, Vector3 position, Vector3 target, float fieldOfView = 65f)
    {
        var gameObject = new GameObject("TemporaryReviewCamera") { hideFlags = HideFlags.HideAndDontSave };
        var camera = gameObject.AddComponent<Camera>();
        camera.transform.position = position;
        camera.transform.LookAt(target);
        camera.fieldOfView = fieldOfView;
        camera.nearClipPlane = 0.06f;
        camera.farClipPlane = 150f;
        camera.clearFlags = CameraClearFlags.SolidColor;
        camera.backgroundColor = new Color(0.08f, 0.11f, 0.14f);
        camera.allowHDR = true;
        camera.allowMSAA = true;
        var texture = RenderTexture.GetTemporary(1440, 900, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.Default, 4);
        var previous = RenderTexture.active;
        try {
            camera.targetTexture = texture;
            camera.Render();
            camera.Render();
            RenderTexture.active = texture;
            var image = new Texture2D(1440, 900, TextureFormat.RGB24, false);
            image.ReadPixels(new Rect(0, 0, 1440, 900), 0, 0);
            image.Apply();
            Directory.CreateDirectory(Path.GetDirectoryName(file));
            File.WriteAllBytes(file, image.EncodeToPNG());
            UnityEngine.Object.DestroyImmediate(image);
        }
        finally {
            camera.targetTexture = null;
            RenderTexture.active = previous;
            RenderTexture.ReleaseTemporary(texture);
            UnityEngine.Object.DestroyImmediate(gameObject);
        }
    }
}
