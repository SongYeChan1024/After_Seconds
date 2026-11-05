using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEditor;
using UnityEditor.SceneManagement;
using Newtonsoft.Json;

public static class PolishB4
{
    const string Model="Assets/Afrer_Seconds/05.Model/Environment/B4/";
    public static object GroundActors()
    {
        var level=GameObject.Find("B4_Stealth_Level_V0.01");
        var actors=level.transform.Find("StaticCharacters");
        var results=new List<object>();
        foreach(Transform actor in actors) {
            var renderers=actor.GetComponentsInChildren<SkinnedMeshRenderer>();
            if(renderers.Length==0) continue;
            float minimum=float.PositiveInfinity;
            foreach(var renderer in renderers) {
                var mesh=new Mesh();
                // Include the renderer scale conversion so TransformPoint does not apply FBX scale twice.
                renderer.BakeMesh(mesh,true);
                foreach(var vertex in mesh.vertices) minimum=Mathf.Min(minimum,renderer.transform.TransformPoint(vertex).y);
                UnityEngine.Object.DestroyImmediate(mesh);
            }
            var visual=actor.GetChild(0);
            float correction=actor.position.y+0.008f-minimum;
            if(float.IsNaN(correction) || Mathf.Abs(correction)>0.75f) throw new InvalidOperationException("Unexpected grounding offset: "+actor.name+" "+correction);
            visual.position+=Vector3.up*correction;
            PrefabUtility.RecordPrefabInstancePropertyModifications(visual);
            results.Add(new{actor=actor.name,previousLowestVertex=minimum,verticalCorrection=correction,finalLowestVertex=actor.position.y+0.008f});
        }
        EditorSceneManager.MarkSceneDirty(level.scene);
        EditorSceneManager.SaveScene(level.scene);
        File.WriteAllText("C:/GitHubProjects/After_Seconds/Docs/검수/2026-11-06_B5_B4/B4/actor_grounding.json",JsonConvert.SerializeObject(results,Formatting.Indented));
        return results;
    }
    public static object StaticPoses()
    {
        var targetScene=UnityEngine.SceneManagement.SceneManager.GetActiveScene();
        var actors=GameObject.Find("B4_Stealth_Level_V0.01").transform.Find("StaticCharacters");
        var sourceScene=EditorSceneManager.OpenScene("Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Stealth.unity",OpenSceneMode.Additive);
        int copied=0;
        int disabled=0;
        try {
            var sourceTransforms=sourceScene.GetRootGameObjects().SelectMany(item=>item.GetComponentsInChildren<Transform>(true)).ToArray();
            foreach(Transform target in actors) {
                if(target.name.StartsWith("C")) continue;
                string role=target.name.StartsWith("G") ? "Guard" : "Researcher";
                var source=sourceTransforms.FirstOrDefault(item=>item.name.Contains(role) && item.GetComponentsInChildren<SkinnedMeshRenderer>().Length>0 && item.name.Contains("Visual"));
                if(!source) throw new InvalidOperationException("Missing B5 pose source: "+role);
                var bones=source.GetComponentsInChildren<SkinnedMeshRenderer>().SelectMany(renderer=>renderer.bones).Where(bone=>bone).Distinct().GroupBy(bone=>bone.name).ToDictionary(group=>group.Key,group=>group.First());
                foreach(var animator in target.GetComponentsInChildren<Animator>(true)) {animator.enabled=false;PrefabUtility.RecordPrefabInstancePropertyModifications(animator);disabled++;}
                foreach(var bone in target.GetComponentsInChildren<SkinnedMeshRenderer>().SelectMany(renderer=>renderer.bones).Where(bone=>bone).Distinct()) {
                    if(bones.TryGetValue(bone.name,out var reference)) {bone.localRotation=reference.localRotation;PrefabUtility.RecordPrefabInstancePropertyModifications(bone);copied++;}
                }
            }
        }
        finally {EditorSceneManager.CloseScene(sourceScene,true);UnityEngine.SceneManagement.SceneManager.SetActiveScene(targetScene);}
        EditorSceneManager.MarkSceneDirty(targetScene);
        EditorSceneManager.SaveScene(targetScene);
        var result=new {copiedBoneRotations=copied,disabledUncontrolledAnimators=disabled,sourceSceneSaved=false};
        File.WriteAllText("C:/GitHubProjects/After_Seconds/Docs/검수/2026-11-06_B5_B4/B4/static_poses.json",JsonConvert.SerializeObject(result,Formatting.Indented));
        return result;
    }
    public static object Finish()
    {
        var level=GameObject.Find("B4_Stealth_Level_V0.01");
        var player=level.scene.GetRootGameObjects().First(item=>item.name.StartsWith("Player"));
        player.transform.rotation=Quaternion.LookRotation(new Vector3(-2,0,-1));
        PrefabUtility.RecordPrefabInstancePropertyModifications(player.transform);
        var collision=level.transform.Find("RailCollision");
        if(!collision) {collision=new GameObject("RailCollision").transform;collision.SetParent(level.transform,false);}
        var segments=new List<Tuple<string,Vector3,Vector3>>();
        foreach(float u in new[]{27.34f,29.06f}) segments.Add(Tuple.Create("Deck_"+u,new Vector3(u,1.05f,15),new Vector3(u,3.55f,18.92f)));
        foreach(float u in new[]{45.82f,47.48f}) segments.Add(Tuple.Create("StairLower_"+u,new Vector3(u,1.05f,24.96f),new Vector3(u,4.25f,30)));
        foreach(float u in new[]{43.92f,45.58f}) segments.Add(Tuple.Create("StairUpper_"+u,new Vector3(u,4.25f,30),new Vector3(u,7.45f,24.96f)));
        segments.Add(Tuple.Create("TopWest",new Vector3(43.72f,7.45f,22.12f),new Vector3(44.88f,7.45f,22.12f)));
        segments.Add(Tuple.Create("TopEast",new Vector3(46.62f,7.45f,22.12f),new Vector3(47.78f,7.45f,22.12f)));
        foreach(var segment in segments) {
            if(collision.Find(segment.Item1)) continue;
            var item=new GameObject(segment.Item1);
            item.transform.SetParent(collision,false);
            item.transform.localPosition=(segment.Item2+segment.Item3)/2-new Vector3(24,0,16);
            item.transform.rotation=Quaternion.FromToRotation(Vector3.up,segment.Item3-segment.Item2);
            var capsule=item.AddComponent<CapsuleCollider>();
            capsule.radius=0.035f;
            capsule.height=Vector3.Distance(segment.Item2,segment.Item3)+0.07f;
            item.isStatic=true;
        }
        var lights=level.GetComponentsInChildren<Light>().Where(light=>light.type==LightType.Spot).ToArray();
        var targets=new[]{new Vector3(8,0,2),new Vector3(20.5f,0,15),new Vector3(17,0,25.5f),new Vector3(29,0,8),new Vector3(30,2.5f,18),new Vector3(7.5f,0,9),new Vector3(7.5f,0,19)};
        foreach(var target in targets) {
            var light=lights.OrderBy(item=>Vector3.SqrMagnitude(item.transform.position-(target-new Vector3(24,0,16)))).First();
            light.shadows=LightShadows.Soft;
            light.shadowStrength=0.75f;
            light.shadowBias=0.035f;
            light.shadowNormalBias=0.18f;
        }
        EditorSceneManager.MarkSceneDirty(level.scene);
        EditorSceneManager.SaveScene(level.scene);
        return new {railColliders=collision.childCount,shadowLights=lights.Count(light=>light.shadows!=LightShadows.None),spawnYaw=player.transform.eulerAngles.y};
    }
    public static object IsolateFloor()
    {
        string source=Model+"Materials/B4_Floor.mat";
        string target=Model+"Materials/B4SL_Floor.mat";
        if(!AssetDatabase.LoadAssetAtPath<Material>(target)) AssetDatabase.CopyAsset(source,target);
        var previous=AssetDatabase.LoadAssetAtPath<Material>(source);
        var replacement=AssetDatabase.LoadAssetAtPath<Material>(target);
        replacement.name="B4SL_Floor";
        var level=GameObject.Find("B4_Stealth_Level_V0.01");
        int changed=0;
        foreach(var renderer in level.GetComponentsInChildren<Renderer>()) {
            if(renderer.sharedMaterial==previous) {renderer.sharedMaterial=replacement;changed++;}
        }
        EditorUtility.SetDirty(replacement);
        AssetDatabase.SaveAssetIfDirty(replacement);
        EditorSceneManager.MarkSceneDirty(level.scene);
        EditorSceneManager.SaveScene(level.scene);
        return new {changed,newMaterial=target};
    }
    public static object Details()
    {
        var level=GameObject.Find("B4_Stealth_Level_V0.01");
        AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        string path=Model+"B4_ServiceDetails.fbx";
        var importer=(ModelImporter)AssetImporter.GetAtPath(path);
        importer.materialImportMode=ModelImporterMaterialImportMode.None;
        importer.importAnimation=false;
        importer.SaveAndReimport();
        var existing=level.transform.Find("B4_ServiceDetails");
        var details=existing ? existing.gameObject : (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(path),level.transform);
        details.name="B4_ServiceDetails";
        foreach(var renderer in details.GetComponentsInChildren<Renderer>()) {
            string materialName=renderer.name.Split('_')[2];
            renderer.sharedMaterial=AssetDatabase.LoadAssetAtPath<Material>(Model+"Materials/B4_"+materialName+".mat");
            renderer.gameObject.isStatic=true;
        }
        EditorSceneManager.MarkSceneDirty(level.scene);
        EditorSceneManager.SaveScene(level.scene);
        return new {details=details.GetComponentsInChildren<Renderer>().Length};
    }
    public static object Lighting()
    {
        var level=GameObject.Find("B4_Stealth_Level_V0.01");
        if(!level) throw new InvalidOperationException("Expected B4 scene");
        RenderSettings.ambientSkyColor=new Color(0.65f,0.72f,0.78f);
        RenderSettings.ambientEquatorColor=new Color(0.42f,0.49f,0.54f);
        RenderSettings.ambientGroundColor=new Color(0.29f,0.34f,0.38f);
        foreach(var light in level.GetComponentsInChildren<Light>()) {
            if(light.type==LightType.Spot) light.intensity=light.name=="Ceiling_D" ? 6.2f : 4.8f;
        }
        var lighting=level.transform.Find("Lighting");
        var fills=new[]{new Vector3(15.5f,2.7f,14),new Vector3(7.5f,2.7f,9),new Vector3(7.5f,2.7f,19),new Vector3(29,3.9f,18),new Vector3(29,2.7f,8),new Vector3(41.25f,2.7f,25),new Vector3(46.5f,2.7f,26),new Vector3(44.8f,6.5f,27)};
        for(int index=0;index<fills.Length;index++) {
            string name="RoomFill_"+index;
            var existing=lighting.Find(name);
            var item=existing ? existing.gameObject : new GameObject(name);
            item.transform.SetParent(lighting,false);
            item.transform.localPosition=fills[index]-new Vector3(24,0,16);
            var light=item.GetComponent<Light>();
            if(!light) light=item.AddComponent<Light>();
            light.type=LightType.Point;
            light.intensity=0.85f;
            light.range=9;
            light.color=new Color(0.74f,0.86f,1);
            light.shadows=LightShadows.None;
        }
        var material=AssetDatabase.LoadAssetAtPath<Material>(Model+"Materials/B4_Metal.mat");
        material.SetColor("_BaseColor",new Color(0.23f,0.29f,0.33f,1));
        material.SetFloat("_Metallic",0.5f);
        EditorUtility.SetDirty(material);
        EditorSceneManager.MarkSceneDirty(level.scene);
        AssetDatabase.SaveAssetIfDirty(material);
        EditorSceneManager.SaveScene(level.scene);
        return new {lights=level.GetComponentsInChildren<Light>().Length,reflectionBakeMethods=typeof(Lightmapping).GetMethods().Where(method=>method.Name.Contains("ReflectionProbe")).Select(method=>method.ToString()).ToArray()};
    }

    public static object BakeReflections()
    {
        var level=GameObject.Find("B4_Stealth_Level_V0.01");
        var root=level.transform.Find("Reflections");
        if(!root) {
            root=new GameObject("Reflections").transform;
            root.SetParent(level.transform,false);
        }
        Directory.CreateDirectory(Model+"Textures");
        AssetDatabase.Refresh();
        var definitions=new[]{
            new {name="ObservationNorth",center=new Vector3(7.5f,2,9),size=new Vector3(9,4,10)},
            new {name="ObservationSouth",center=new Vector3(7.5f,2,19),size=new Vector3(9,4,10)},
            new {name="ObservationCorridor",center=new Vector3(15.5f,2,14),size=new Vector3(7,4,20)},
            new {name="Analysis",center=new Vector3(29,2,8),size=new Vector3(14,4,8)},
            new {name="Deck",center=new Vector3(30,3,18),size=new Vector3(14,6,12)},
            new {name="StairA",center=new Vector3(41.25f,2,25),size=new Vector3(4.5f,4,14)},
            new {name="StairB",center=new Vector3(45.75f,4.5f,25),size=new Vector3(4.5f,9,14)},
            new {name="Support",center=new Vector3(22.5f,2,29.5f),size=new Vector3(36,4,5)}
        };
        var results=new List<object>();
        foreach(var definition in definitions) {
            var transform=root.Find(definition.name);
            var item=transform ? transform.gameObject : new GameObject(definition.name);
            item.transform.SetParent(root,false);
            item.transform.localPosition=definition.center-new Vector3(24,0,16);
            var probe=item.GetComponent<ReflectionProbe>();
            if(!probe) probe=item.AddComponent<ReflectionProbe>();
            probe.mode=ReflectionProbeMode.Baked;
            probe.resolution=128;
            probe.size=definition.size;
            probe.center=Vector3.zero;
            probe.boxProjection=true;
            probe.blendDistance=0.6f;
            probe.intensity=0.8f;
            probe.clearFlags=ReflectionProbeClearFlags.SolidColor;
            probe.backgroundColor=new Color(0.22f,0.28f,0.32f);
            string file=Model+"Textures/B4_Reflection_"+definition.name+".exr";
            bool success=Lightmapping.BakeReflectionProbe(probe,file);
            AssetDatabase.ImportAsset(file,ImportAssetOptions.ForceSynchronousImport);
            probe.bakedTexture=AssetDatabase.LoadAssetAtPath<Texture>(file);
            results.Add(new {definition.name,success,texture=probe.bakedTexture ? probe.bakedTexture.name : null});
        }
        EditorSceneManager.MarkSceneDirty(level.scene);
        EditorSceneManager.SaveScene(level.scene);
        File.WriteAllText("C:/GitHubProjects/After_Seconds/Docs/검수/2026-11-06_B5_B4/B4/reflections.json",JsonConvert.SerializeObject(results,Formatting.Indented));
        return results;
    }
}
