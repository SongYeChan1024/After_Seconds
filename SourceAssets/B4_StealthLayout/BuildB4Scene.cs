using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.Rendering;

public static class BuildB4Scene
{
    public static object ResetCopiedLighting()
    {
        var scene=UnityEngine.SceneManagement.SceneManager.GetActiveScene();
        if(scene.path!=ScenePath) throw new InvalidOperationException("Expected B4");
        string previous=AssetDatabase.GetAssetPath(Lightmapping.lightingDataAsset);
        Lightmapping.lightingDataAsset=null;
        LightmapSettings.lightmaps=new LightmapData[0];
        RenderSettings.customReflectionTexture=null;
        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene);
        EditorSceneManager.OpenScene(ScenePath,OpenSceneMode.Single);
        return new {previousLightingData=previous,currentLightingData=AssetDatabase.GetAssetPath(Lightmapping.lightingDataAsset)};
    }
    const string Repository = "C:/GitHubProjects/After_Seconds";
    const string Root = "Assets/Afrer_Seconds/";
    const string Model = Root + "05.Model/Environment/B4/";
    const string ScenePath = Root + "01.Scenes/Stage/Level_B4_Stealth.unity";
    static readonly List<object> Placements = new List<object>();
    static Transform propRoot;
    static Transform actorRoot;

    static Vector3 Vector(JToken value) => new Vector3((float)value[0], (float)value[1], (float)value[2]);
    static Vector3 Plan(float u, float height, float v) => new Vector3(u-24, height, v-16);
    static GameObject Child(string name, Transform parent)
    {
        var item = new GameObject(name);
        item.transform.SetParent(parent, false);
        return item;
    }

    static Bounds BoundsOf(GameObject item)
    {
        var renderers = item.GetComponentsInChildren<Renderer>(true);
        if (renderers.Length == 0) throw new InvalidOperationException("No renderer: " + item.name);
        var bounds = renderers[0].bounds;
        foreach (var renderer in renderers.Skip(1)) bounds.Encapsulate(renderer.bounds);
        return bounds;
    }

    static GameObject Place(string asset, string name, float u, float v, float height, float yaw=0, float floor=0, bool collision=true, bool actor=false)
    {
        string path = Root + "05.Model/" + asset + ".prefab";
        var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
        if (!prefab) throw new FileNotFoundException(path);
        var holder = Child(name, actor ? actorRoot : propRoot);
        var item = (GameObject)PrefabUtility.InstantiatePrefab(prefab, holder.transform);
        var bounds = BoundsOf(item);
        item.transform.localScale *= height/bounds.size.y;
        bounds = BoundsOf(item);
        item.transform.position -= new Vector3(bounds.center.x, bounds.min.y, bounds.center.z);
        bounds = BoundsOf(item);
        var size = bounds.size;
        holder.transform.position = Plan(u,floor,v);
        holder.transform.rotation = Quaternion.Euler(0,yaw,0);
        foreach (var collider in item.GetComponentsInChildren<Collider>(true)) collider.enabled = false;
        if (collision) {
            var collider = holder.AddComponent<BoxCollider>();
            collider.center = new Vector3(0,size.y/2,0);
            collider.size = new Vector3(Mathf.Max(0.1f,size.x*0.94f),size.y,Mathf.Max(0.1f,size.z*0.94f));
        }
        if (!actor) {
            foreach (var transform in holder.GetComponentsInChildren<Transform>(true)) transform.gameObject.isStatic = true;
        }
        Placements.Add(new {name,asset=path,u,v,height,yaw,floor,size=new[]{size.x,size.y,size.z},collision});
        return holder;
    }

    static Dictionary<string,Material> CreateMaterials(JObject manifest)
    {
        Directory.CreateDirectory(Model+"Materials");
        AssetDatabase.Refresh();
        var materials = new Dictionary<string,Material>();
        foreach (var property in ((JObject)manifest["materials"]).Properties()) {
            string name = "B4_" + property.Name;
            string path = Model + "Materials/" + (property.Name=="Floor" ? "B4SL_Floor" : name) + ".mat";
            var material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (!material) {
                material = new Material(Shader.Find("Universal Render Pipeline/Lit")) { name = name };
                AssetDatabase.CreateAsset(material,path);
            }
            var values = property.Value;
            var color = new Color((float)values[0],(float)values[1],(float)values[2],(float)values[3]);
            material.SetColor("_BaseColor",color);
            material.SetFloat("_Metallic", property.Name=="Metal" ? 0.65f : 0.12f);
            material.SetFloat("_Smoothness",property.Name=="Metal" ? 0.5f : 0.28f);
            if (property.Name=="Glass") {
                material.SetFloat("_Surface",1);
                material.SetFloat("_Blend",0);
                material.SetFloat("_SrcBlend",(float)BlendMode.SrcAlpha);
                material.SetFloat("_DstBlend",(float)BlendMode.OneMinusSrcAlpha);
                material.SetFloat("_ZWrite",0);
                material.SetFloat("_Cull",0);
                material.SetOverrideTag("RenderType","Transparent");
                material.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
                material.renderQueue = (int)RenderQueue.Transparent;
                material.SetFloat("_Smoothness",0.86f);
            }
            else if (property.Name=="Light") {
                material.EnableKeyword("_EMISSION");
                material.SetColor("_EmissionColor",color*2.4f);
                material.globalIlluminationFlags = MaterialGlobalIlluminationFlags.RealtimeEmissive;
            }
            else {
                var textureRoot = Root + "05.Model/Environment/B5/Textures/SL_Painted_";
                material.SetTexture("_BaseMap",AssetDatabase.LoadAssetAtPath<Texture2D>(textureRoot+"Base.png"));
                material.SetTexture("_BumpMap",AssetDatabase.LoadAssetAtPath<Texture2D>(textureRoot+"Normal.png"));
                material.SetFloat("_BumpScale",0.3f);
                material.EnableKeyword("_NORMALMAP");
            }
            EditorUtility.SetDirty(material);
            materials[name] = material;
        }
        return materials;
    }

    public static object Build()
    {
        if (EditorApplication.isPlaying) throw new InvalidOperationException("Exit Play Mode first");
        if (File.Exists(ScenePath)) throw new InvalidOperationException("B4 scene already exists; review it rather than overwrite");
        var manifest = JObject.Parse(File.ReadAllText(Repository+"/SourceAssets/B4_StealthLayout/architecture_manifest.json"));
        AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        var materials = CreateMaterials(manifest);
        string architecturePath = Model+"B4_Stealth_Architecture.fbx";
        var importer = (ModelImporter)AssetImporter.GetAtPath(architecturePath);
        importer.materialImportMode = ModelImporterMaterialImportMode.None;
        importer.importCameras = false;
        importer.importLights = false;
        importer.importAnimation = false;
        importer.isReadable = false;
        importer.SaveAndReimport();
        if (!AssetDatabase.CopyAsset(Root+"01.Scenes/Stage/Level_B5_Stealth.unity",ScenePath)) throw new InvalidOperationException("Could not copy player/camera scene");
        var scene = EditorSceneManager.OpenScene(ScenePath,OpenSceneMode.Single);
        Lightmapping.lightingDataAsset = null;
        LightmapSettings.lightmaps = new LightmapData[0];
        RenderSettings.customReflectionTexture = null;
        foreach (var root in scene.GetRootGameObjects().Where(root => root.name.StartsWith("B5_"))) UnityEngine.Object.DestroyImmediate(root);
        var level = new GameObject("B4_Stealth_Level_V0.01");
        var geometry = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(architecturePath),level.transform);
        geometry.name = "B4_Architecture";
        foreach (var renderer in geometry.GetComponentsInChildren<Renderer>()) {
            var materialKey = materials.Keys.OrderByDescending(key => key.Length).FirstOrDefault(key => renderer.name.Contains("_"+key.Substring(3)+"_"));
            if (materialKey==null) throw new InvalidOperationException("Unmapped material: "+renderer.name);
            renderer.sharedMaterial = materials[materialKey];
            renderer.gameObject.isStatic = true;
            if (materialKey=="B4_Glass") renderer.shadowCastingMode = ShadowCastingMode.Off;
        }
        var collisionRoot = Child("StaticCollision",level.transform).transform;
        foreach (var item in manifest["colliders"]) {
            var gameObject = Child((string)item["name"],collisionRoot);
            gameObject.transform.localPosition = Vector(item["center"]);
            gameObject.AddComponent<BoxCollider>().size = Vector(item["size"]);
            gameObject.isStatic = true;
        }
        var lightRoot = Child("Lighting",level.transform).transform;
        foreach (var item in manifest["lights"]) {
            var light = Child("Ceiling_"+(string)item["room"],lightRoot).AddComponent<Light>();
            light.transform.localPosition = Vector(item["position"]);
            light.transform.rotation = Quaternion.Euler(90,0,0);
            light.type = LightType.Spot;
            light.spotAngle = 138;
            light.innerSpotAngle = 100;
            light.range = (float)item["range"];
            light.intensity = (float)item["intensity"];
            light.color = new Color(0.78f,0.90f,1);
            light.shadows = LightShadows.None;
        }
        RenderSettings.ambientMode = AmbientMode.Trilight;
        RenderSettings.ambientSkyColor = new Color(0.34f,0.41f,0.47f);
        RenderSettings.ambientEquatorColor = new Color(0.21f,0.27f,0.30f);
        RenderSettings.ambientGroundColor = new Color(0.13f,0.17f,0.20f);
        RenderSettings.fog = false;
        propRoot = Child("Props",level.transform).transform;
        actorRoot = Child("StaticCharacters",level.transform).transform;
        string monitor = "Props/B4/B4_ObservationMonitorBank_B5_Lite";
        string cabinet = "Props/Common/P04_RecordsCabinet_B5_Lite";
        string storage = "Props/Common/P02_WallStorageCabinet_B5_Lite";
        string workbench = "Props/Common/Props_LaboratoryWorkbench_B5_Lite";
        string cart = "Props/Common/P09_LaboratoryTrolley_B5_Lite";
        string bin = "Props/Common/P07_SealedWasteBin_B5_Lite";
        Place(workbench,"AN_ExaminationBench",7.5f,6.1f,0.95f,180);
        Place(monitor,"AN_ObservationConsole",9.3f,12.3f,1.55f,0);
        Place(cabinet,"AN_Records",4.2f,12.5f,1.8f,90);
        Place(cart,"AN_MedicalCart",5.4f,6.2f,0.95f,180);
        Place(workbench,"AS_ExaminationBench",7.4f,16.1f,0.95f,180);
        Place(monitor,"AS_ObservationConsole",9.3f,22.3f,1.55f,0);
        Place(storage,"AS_EquipmentStorage",4.3f,22.4f,1.7f,90);
        Place(cart,"AS_MedicalCart",5.3f,16.3f,0.95f,90);
        Place(bin,"AS_SealedWaste",10.8f,16,0.8f);
        Place(monitor,"A_ObserverConsole",17.8f,6.5f,1.5f,270);
        Place(storage,"A_SupplyCabinet",17.8f,22.4f,1.7f,270);
        Place(monitor,"B_AnalysisConsole",26,6,1.75f,180,0,false);
        Place(monitor,"B_DataStation",33.7f,10.5f,1.65f,0);
        Place(cabinet,"B_DataArchive",23.4f,10.6f,1.8f,90);
        Place(monitor,"D_DeckConsole",32,16.2f,1.55f,180,2.52f);
        Place(monitor,"D_DeckConsoleSouth",32,18.8f,1.55f,0,2.52f);
        Place(cart,"D_InstrumentCart",23.5f,13.5f,0.95f);
        Place(workbench,"SUP1_SupportDesk",4.2f,31,0.95f,0);
        Place(cabinet,"SUP1_Storage",1.4f,28.2f,1.8f,90);
        Place(storage,"SUP2_Equipment",16.2f,31,1.7f,0);
        Place(cart,"SUP2_PreparationCart",11,28.4f,0.95f,90);
        Place(workbench,"SUP2_PreparationBench",13.6f,31,0.95f,0);
        Place(cabinet,"SUP3_RecordsWest",19.3f,31,1.8f,0);
        Place(cabinet,"SUP3_RecordsEast",24.9f,31,1.8f,0);
        Place(storage,"SUP4_Utilities",29,31,1.7f,0);
        Place(bin,"SUP4_SealedWaste",34.4f,31,0.85f,0);
        Place(storage,"HVAC_MaintenanceStorage",45.8f,2,1.7f,0);
        Place(cart,"HVAC_ToolCart",41.5f,4.5f,1.0f,90);
        Place("Props/Common/P13_LogisticsTote_B5_Lite","LIFT_TransitTote",41.8f,8,0.9f);
        Place("Props/Common/P13_LogisticsTote_B5_Lite","LIFT_TransitToteSouth",41.8f,15.7f,0.9f);
        Place("Enemy/AS_V03_Guard_HeadRepaired","G1_NorthCorridor_Visual",8,2,1.9f,90,0,false,true);
        Place("Enemy/AS_V03_Guard_HeadRepaired","G2_CentralCorridor_Visual",20.5f,15,1.9f,0,0,false,true);
        Place("Enemy/AS_V03_Guard_HeadRepaired","G3_SouthCorridor_Visual",17,25.5f,1.9f,270,0,false,true);
        Place("Enemy/AS_V03_Researcher","R1_Analysis_Visual",29,8,1.75f,180,0,false,true);
        Place("Enemy/CCTV_SecurityCamera_Articulated","C1_ObservationCorridor",15,6,0.7f,0,3.25f,false,true);
        Place("Enemy/CCTV_SecurityCamera_Articulated","C2_EastCorridor",37.5f,10,0.7f,180,3.25f,false,true);
        var markerRoot = Child("PlanMarkers_NoRuntimeLogic",level.transform).transform;
        Child("Entry_StairA",markerRoot).transform.position = Plan(41,0,26);
        Child("Exit_StairB",markerRoot).transform.position = Plan(46,0,24);
        Child("Researcher_Refuge",markerRoot).transform.position = Plan(4.5f,0,29.5f);
        var player = scene.GetRootGameObjects().First(root => root.name.StartsWith("Player"));
        player.transform.position = Plan(41,0.89f,26);
        player.transform.rotation = Quaternion.LookRotation(new Vector3(-2,0,-1));
        PrefabUtility.RecordPrefabInstancePropertyModifications(player.transform);
        string assetRecord = Root+"06.Data/AssetSources/B4_Stealth_20261106.json";
        var result = new {
            title="B4 Stealth Scene V0.01",author="송예찬",scene=ScenePath,
            architecture=architecturePath, rooms=19, doors=28, observationWindows=4,
            staticColliders=level.GetComponentsInChildren<Collider>().Length,
            lights=level.GetComponentsInChildren<Light>().Length,
            props=Placements, gameplayCodeAdded=0,
            limits="Static actors; B5/B4 and B4/B3 transitions not implemented; section heights provisional"
        };
        File.WriteAllText(assetRecord,JsonConvert.SerializeObject(result,Formatting.Indented));
        Directory.CreateDirectory(Repository+"/Docs/검수/2026-11-06_B5_B4/B4");
        File.WriteAllText(Repository+"/Docs/검수/2026-11-06_B5_B4/B4/build_result.json",JsonConvert.SerializeObject(result,Formatting.Indented));
        foreach(var material in materials.Values) AssetDatabase.SaveAssetIfDirty(material);
        AssetDatabase.Refresh();
        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene);
        return new { scene=ScenePath,props=Placements.Count,colliders=level.GetComponentsInChildren<Collider>().Length,lights=level.GetComponentsInChildren<Light>().Length };
    }
}
