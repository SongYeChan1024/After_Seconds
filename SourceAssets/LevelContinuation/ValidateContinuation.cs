// B5/B4 lab art validation V0.01. External Editor tool only.
using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
using UnityEngine.Rendering;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
public static class ValidateContinuation {
 const string Root="Assets/Afrer_Seconds/";
 static string Repo=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 static string P(Transform t)=>t.parent?P(t.parent)+"/"+t.name:t.name;
 static float[] V(Vector3 p)=>new[]{p.x,p.y,p.z};
 static void Write(string name,object obj)=>File.WriteAllText(Repo+"/Docs/검수/2026-11-06_LevelContinuation/"+name+".json",JsonConvert.SerializeObject(obj,Formatting.Indented));
 static void Ready(){if(EditorApplication.isPlaying||SceneManager.GetActiveScene().isDirty)throw new Exception("Saved Edit scene required");}
 public static object Ownership(){Ready();string original=SceneManager.GetActiveScene().path;var result=new List<object>();try{foreach(string floor in new[]{"B5","B4","B3"}){var s=EditorSceneManager.OpenScene(Root+"01.Scenes/Stage/Level_"+floor+"_Stealth.unity");var all=s.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Transform>(true)).ToArray();var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith(floor+"_Stealth_Level"));var portals=root.transform.Find("TransitionDoors");Physics.SyncTransforms();var checks=new List<object>();foreach(Transform d in portals){bool open=Vector3.Distance(d.Find("Leaf_Left").localPosition,d.Find("Left_Open").localPosition)<.001f;var hits=Physics.OverlapCapsule(d.position+Vector3.up*.34f,d.position+Vector3.up*1.54f,.30f,~0,QueryTriggerInteraction.Ignore).Where(c=>!c.transform.root.name.StartsWith("Player")).ToArray();checks.Add(new{d.name,position=V(d.position),open,centerBlocked=hits.Length>0,hits=hits.Select(c=>P(c.transform)).ToArray()});}Write(floor+"_ownership",new{floor,transforms=all.Select(t=>new{path=P(t),position=V(t.localPosition),rotation=V(t.localEulerAngles),scale=V(t.localScale),active=t.gameObject.activeSelf}).ToArray(),portals=checks,lights=all.Select(t=>t.GetComponent<Light>()).Where(l=>l).Select(l=>new{path=P(l.transform),l.intensity,shadows=l.shadows.ToString()}).ToArray(),reflections=all.Select(t=>t.GetComponent<ReflectionProbe>()).Where(p=>p).Select(p=>new{p.name,p.resolution,texture=AssetDatabase.GetAssetPath(p.customBakedTexture)}).ToArray()});result.Add(new{floor,portals=checks,transforms=all.Length});}}finally{EditorSceneManager.OpenScene(original);}return result;}
 public static object Status()=>new{playing=EditorApplication.isPlaying,scene=SceneManager.GetActiveScene().path,dirty=SceneManager.GetActiveScene().isDirty,metadata=AssetDatabase.LoadAssetAtPath<TextAsset>(Root+"06.Data/AssetSources/B45_LabPolish_20261106.json")!=null};
 public static object FinalImport(){var logs=new List<string>();Application.LogCallback cb=(m,s,t)=>{if(t==LogType.Warning||t==LogType.Error||t==LogType.Exception)logs.Add(m);};Application.logMessageReceived+=cb;try{AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);foreach(string name in new[]{"Keypad","WorkLight"})AssetDatabase.ImportAsset(Root+"05.Model/Props/Common/LP_"+name+".fbx",ImportAssetOptions.ForceUpdate|ImportAssetOptions.ForceSynchronousImport);}finally{Application.logMessageReceived-=cb;}Write("final_import",new{logs});return logs;}
 public static object Check(){
  Ready();var results=new List<object>();string original=SceneManager.GetActiveScene().path;
  var routes=JObject.Parse(File.ReadAllText(Repo+"/Docs/도면/잠입_탐색/플레이어_예상이동/player_routes.json"))["routes"];
  try{foreach(string floor in new[]{"B5","B4","B3"}){
   var s=EditorSceneManager.OpenScene(Root+"01.Scenes/Stage/Level_"+floor+"_Stealth.unity");var all=s.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Transform>(true)).ToArray();var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith(floor+"_Stealth_Level"));Physics.SyncTransforms();
   var routeResults=new List<object>();
   foreach(var route in routes.Where(r=>(string)r["floor"]==floor)){
    int samples=0;var blocked=new List<object>();
    foreach(var leg in route["legs"]){var points=leg["points"].Select(p=>new Vector3((float)p[0]-24,0,(float)p[1]-16)).ToArray();for(int i=1;i<points.Length;i++){int count=Mathf.CeilToInt(Vector3.Distance(points[i-1],points[i])/.25f);for(int j=0;j<=count;j++){var p=Vector3.Lerp(points[i-1],points[i],(float)j/count);var hits=Physics.OverlapCapsule(p+Vector3.up*.34f,p+Vector3.up*1.54f,.30f,~0,QueryTriggerInteraction.Ignore).Where(c=>!c.transform.root.name.StartsWith("Player")).ToArray();samples++;if(hits.Length>0)blocked.Add(new{position=V(p),hits=hits.Select(c=>P(c.transform)).ToArray()});}}}
    routeResults.Add(new{variant=(string)route["variant"],samples,blocked});
   }
   var doors=new List<object>();foreach(Transform d in root.transform.Find("Lab_Doors")){
    var leaves=new[]{d.Find("Leaf_Left"),d.Find("Leaf_Right")};bool open=Vector3.Distance(leaves[0].localPosition,d.Find("Left_Open").localPosition)<.001f;
    int keypadCount=d.Cast<Transform>().Count(t=>t.name.StartsWith("Keypad_"));var clearance=new List<string>();
    for(int i=-3;i<=3;i++){var p=d.TransformPoint(new Vector3(0,0,i*.25f));clearance.AddRange(Physics.OverlapCapsule(p+Vector3.up*.34f,p+Vector3.up*1.54f,.30f,~0,QueryTriggerInteraction.Ignore).Where(c=>!c.transform.root.name.StartsWith("Player")).Select(c=>P(c.transform)));}
    doors.Add(new{name=d.name,open,keypadCount,correctAnchors=leaves.Select((t,i)=>Vector3.Distance(t.localPosition,d.Find((i==0?"Left":"Right")+(open?"_Open":"_Closed")).localPosition)<.001f).All(x=>x),colliders=leaves.Count(t=>t.GetComponent<BoxCollider>()),clearanceHits=clearance.Distinct().ToArray()});
   }
   var props=new List<object>();foreach(Transform prop in (root.transform.Find("Lab_Additional_Props")??root.transform.Find("Props"))){
    var c=prop.GetComponent<BoxCollider>();if(!c)throw new Exception("Missing prop collider "+prop.name);var half=Vector3.Scale(c.size*.5f,prop.lossyScale)-Vector3.one*.025f;var hits=Physics.OverlapBox(prop.TransformPoint(c.center),half,prop.rotation,~0,QueryTriggerInteraction.Ignore).Where(h=>h!=c&&!h.transform.IsChildOf(prop)&&!h.transform.root.name.StartsWith("Player")).Select(h=>P(h.transform)).ToArray();props.Add(new{name=prop.name,position=V(prop.localPosition),overlaps=hits});
   }
   var lower=new HashSet<Renderer>();foreach(var l in all.Select(t=>t.GetComponent<LODGroup>()).Where(l=>l))foreach(var lod in l.GetLODs().Skip(1))foreach(var r in lod.renderers)if(r)lower.Add(r);
   long triangles=0;var errors=new List<string>();foreach(var r in all.Select(t=>t.GetComponent<Renderer>()).Where(r=>r&&r.enabled&&r.gameObject.activeInHierarchy)){
    if(r.sharedMaterials.Any(m=>!m||!m.shader||m.shader.name=="Hidden/InternalErrorShader"))errors.Add("Missing material: "+P(r.transform));if(lower.Contains(r))continue;var mesh=r is SkinnedMeshRenderer?((SkinnedMeshRenderer)r).sharedMesh:r.GetComponent<MeshFilter>()?.sharedMesh;if(mesh)for(int sm=0;sm<mesh.subMeshCount;sm++)triangles+=(long)mesh.GetIndexCount(sm)/3;
   }
   int missing=all.Sum(t=>GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject));
   results.Add(new{floor,trianglesHighestLOD=triangles,missingScripts=missing,materialErrors=errors,colliders=all.Sum(t=>t.GetComponents<Collider>().Length),lights=all.Count(t=>t.GetComponent<Light>()),routes=routeResults,doors,props});
  }}finally{EditorSceneManager.OpenScene(original);}Write("validation",results);return results;
 }
 public static object ReflectionsB5()=>ReflectFloors(new[]{"B5"});
 public static object Reflections()=>ReflectFloors(new[]{"B5","B4","B3"});
 static object ReflectFloors(string[] floors){
  Ready();var result=new List<object>();string original=SceneManager.GetActiveScene().path;
  try{foreach(string floor in floors){
   var scene=EditorSceneManager.OpenScene(Root+"01.Scenes/Stage/Level_"+floor+"_Stealth.unity");
   if(floor=="B3"&&!scene.GetRootGameObjects().Any(g=>g.GetComponentsInChildren<ReflectionProbe>().Length>0)){
    var root=scene.GetRootGameObjects().Single(g=>g.name.StartsWith("B3_Stealth_Level"));var group=new GameObject("StaticReflections");group.transform.SetParent(root.transform,false);
    var zones=new[]{new[]{11f,14,16,20},new[]{29f,9,14,10},new[]{29f,19,14,10},new[]{43.5f,11,9,14},new[]{45.8f,25,4.4f,14},new[]{41f,25,4.4f,14},new[]{11f,29.5f,18,5},new[]{27f,29.5f,18,5},new[]{20.5f,14,3,23},new[]{37.5f,14,3,23}};
    int n=0;foreach(var z in zones){var g=new GameObject("B3_Reflection_"+n++);g.transform.SetParent(group.transform,false);g.transform.position=new Vector3(z[0]-24,1.8f,z[1]-16);var p=g.AddComponent<ReflectionProbe>();p.size=new Vector3(z[2],5,z[3]);p.center=Vector3.zero;p.boxProjection=true;p.blendDistance=.6f;p.nearClipPlane=.05f;p.farClipPlane=80;p.clearFlags=ReflectionProbeClearFlags.SolidColor;p.backgroundColor=Color.black;p.hdr=true;p.intensity=1;}
   }
   var renderers=scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Renderer>(true)).Where(r=>r is SkinnedMeshRenderer||r.transform.root.name.StartsWith("Player")||P(r.transform).Contains("/StaticCharacters/")||P(r.transform).Contains("/Actors/")).ToArray();var states=renderers.Select(r=>r.forceRenderingOff).ToArray();var rows=new List<object>();
   try{foreach(var r in renderers)r.forceRenderingOff=true;int i=0;foreach(var p in scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<ReflectionProbe>(true))){string path=Root+"05.Model/Environment/"+floor+"/Textures/LC_Reflection_"+i.ToString("D2")+".exr";p.resolution=128;bool ok=Lightmapping.BakeReflectionProbe(p,path);if(!ok)throw new Exception("Reflection bake failed: "+p.name);AssetDatabase.ImportAsset(path,ImportAssetOptions.ForceSynchronousImport);var imp=(TextureImporter)AssetImporter.GetAtPath(path);imp.sRGBTexture=false;imp.textureCompression=TextureImporterCompression.CompressedHQ;imp.SaveAndReimport();p.mode=ReflectionProbeMode.Custom;p.customBakedTexture=AssetDatabase.LoadAssetAtPath<Cubemap>(path);if(!p.customBakedTexture)throw new Exception("Missing reflection cube");rows.Add(new{p.name,path,p.resolution});i++;}}
   finally{for(int i=0;i<renderers.Length;i++)renderers[i].forceRenderingOff=states[i];}
   EditorSceneManager.MarkSceneDirty(scene);EditorSceneManager.SaveScene(scene);result.Add(new{floor,probes=rows,hiddenRenderers=renderers.Length});
  }}finally{EditorSceneManager.OpenScene(original);}Write(floors.Length==1?"reflections_B5_final":"reflections",result);return result;
 }
}
