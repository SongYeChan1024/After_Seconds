// Editor-only Reference_004 interior authoring. No gameplay code.
using System;using System.IO;using System.Linq;using System.Collections.Generic;
using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.SceneManagement;
using UnityEngine.Rendering;using UnityEngine.Rendering.Universal;using Newtonsoft.Json;using Newtonsoft.Json.Linq;
public static class ApplyArches {
 const string Root="Assets/Afrer_Seconds/";const string Env=Root+"05.Model/Environment/";
 static string Repo=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 static string Src=>Repo+"/SourceAssets/B345_ArchedInterior/";static string Out=>Repo+"/Docs/검수/2026-11-06_B345_ArchedInterior/";
 static void Ready(){if(EditorApplication.isPlaying||SceneManager.GetActiveScene().isDirty)throw new Exception("Saved edit scene required");}
 static Vector3 V(JToken a)=>new Vector3((float)a[0],(float)a[1],(float)a[2]);
 static string P(Transform t)=>t.parent?P(t.parent)+"/"+t.name:t.name;
 static string Scene(string f)=>Root+"01.Scenes/Stage/Level_"+f+"_Stealth.unity";
 static void Write(string n,object o){Directory.CreateDirectory(Out);File.WriteAllText(Out+n+".json",JsonConvert.SerializeObject(o,Formatting.Indented));}
 public static object Preflight(){Ready();if(!UniversalRenderPipeline.asset)throw new Exception("URP required");string original=SceneManager.GetActiveScene().path;var all=new List<object>();var blocked=new Dictionary<string,string[]>();
  try{foreach(string f in new[]{"B5","B4","B3"}){
   var s=EditorSceneManager.OpenScene(Scene(f));var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith(f+"_Stealth_Level"));var data=JObject.Parse(File.ReadAllText(Src+f+"_arches.json"));Physics.SyncTransforms();var hits=new List<object>();var bad=new HashSet<string>();
   foreach(var row in data["colliders"]){var center=V(row["center"]);var half=V(row["size"])*.5f-Vector3.one*.018f;var hh=Physics.OverlapBox(center,half,Quaternion.identity,~0,QueryTriggerInteraction.Ignore).Where(c=>!c.transform.root.name.StartsWith("Player")&&!P(c.transform).Contains("/Arched_Interior/")).ToArray();if(hh.Length>0){string name=(string)row["name"];int n=name.Contains("_Left_")?name.IndexOf("_Left_"):name.IndexOf("_Right_");bad.Add(name.Substring(0,n));hits.Add(new{name,hits=hh.Select(c=>P(c.transform)).ToArray()});}}
   blocked[f]=bad.ToArray();var cam=Camera.main;var cd=cam.GetComponent<UniversalAdditionalCameraData>();var vols=root.GetComponentsInChildren<Volume>(true);var rd=new SerializedObject(UniversalRenderPipeline.asset).FindProperty("m_RendererDataList").GetArrayElementAtIndex(0).objectReferenceValue;var serialized=new SerializedObject(rd);var pp=serialized.FindProperty("postProcessData");
   all.Add(new{floor=f,proposedArches=(int)data["arches"],blockedArches=bad.ToArray(),hits,hdr=UniversalRenderPipeline.asset.supportsHDR,cameraPostprocessing=cd.renderPostProcessing,rendererPostprocessData=pp!=null&&pp.objectReferenceValue!=null,volumes=vols.Select(v=>new{v.name,v.enabled,v.isGlobal,profile=v.sharedProfile?AssetDatabase.GetAssetPath(v.sharedProfile):null,layerIncluded=(cd.volumeLayerMask&(1<<v.gameObject.layer))!=0}).ToArray(),lights=root.GetComponentsInChildren<Light>().GroupBy(l=>new{type=l.type,intensity=l.intensity}).Select(g=>new{g.Key,count=g.Count()}).ToArray()});
  }}finally{EditorSceneManager.OpenScene(original);}File.WriteAllText(Src+"blocked_arches.json",JsonConvert.SerializeObject(blocked,Formatting.Indented));Write("preflight",all);return all;
 }
 static Material Material(string name,Color color,float metal,float smooth,string source=null){string p=Env+"Common/Materials/"+name+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(p);if(!m){m=source==null?new Material(Shader.Find("Universal Render Pipeline/Lit")):new Material(AssetDatabase.LoadAssetAtPath<Material>(Env+"Common/Materials/"+source+".mat"));AssetDatabase.CreateAsset(m,p);}m.name=name;m.enableInstancing=true;m.SetColor("_BaseColor",color);m.SetTexture("_MetallicGlossMap",null);m.DisableKeyword("_METALLICSPECGLOSSMAP");m.SetFloat("_Metallic",metal);m.SetFloat("_Smoothness",smooth);EditorUtility.SetDirty(m);return m;}
 public static object Refine(){Ready();AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);string original=SceneManager.GetActiveScene().path;var rows=new List<object>();
  var lens=AssetDatabase.LoadAssetAtPath<Material>(Env+"Common/Materials/AR_Diffuser.mat");lens.shader=Shader.Find("Universal Render Pipeline/Unlit");lens.SetColor("_BaseColor",new Color(.90f,.95f,1f)*1.15f);EditorUtility.SetDirty(lens);AssetDatabase.SaveAssetIfDirty(lens);
  try{foreach(string f in new[]{"B5","B4","B3"}){var s=EditorSceneManager.OpenScene(Scene(f));var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith(f+"_Stealth_Level"));var group=root.transform.Find("Arched_Interior");var data=JObject.Parse(File.ReadAllText(Src+f+"_arches.json"));foreach(var row in data["colliders"]){var t=group.Find((string)row["name"]);t.position=V(row["center"]);t.GetComponent<BoxCollider>().size=V(row["size"]);}EditorSceneManager.MarkSceneDirty(s);EditorSceneManager.SaveScene(s);rows.Add(new{floor=f,colliders=data["colliders"].Count(),triangles=(int)data["triangles"]});}}finally{EditorSceneManager.OpenScene(original);}Write("refined",rows);return rows;
 }
 public static object Apply(){Ready();string original=SceneManager.GetActiveScene().path;var logs=new List<string>();Application.LogCallback cb=(m,s,t)=>{if(t==LogType.Warning||t==LogType.Error||t==LogType.Exception)logs.Add(m);};Application.logMessageReceived+=cb;var rows=new List<object>();
  try{AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
   var mats=new Dictionary<string,Material>();mats["AR_Shell"]=Material("AR_Shell",new Color(.82f,.83f,.82f),.04f,.42f,"LP_Coating");mats["AR_Inset"]=Material("AR_Inset",new Color(.16f,.19f,.20f),.40f,.36f);mats["AR_Champagne"]=Material("AR_Champagne",new Color(.49f,.40f,.26f),.65f,.43f);mats["AR_Diffuser"]=Material("AR_Diffuser",new Color(.85f,.89f,.94f),0,.28f);mats["AR_Diffuser"].EnableKeyword("_EMISSION");mats["AR_Diffuser"].SetColor("_EmissionColor",new Color(.88f,.94f,1f)*1.35f);
   var ceiling=Material("AR_Ceiling",new Color(.77f,.79f,.79f),.03f,.34f,"LP_Ceiling");var floor=Material("AR_Floor",new Color(.49f,.51f,.52f),.12f,.42f,"LP_Floor");var baseTrim=Material("AR_BaseTrim",new Color(.36f,.38f,.38f),.30f,.42f,"LP_Plinth");AssetDatabase.SaveAssets();
   foreach(string f in new[]{"B5","B4","B3"}){
    string model=Env+f+"/AR_"+f+"_Interior.fbx";var im=(ModelImporter)AssetImporter.GetAtPath(model);im.importAnimation=false;im.importLights=false;im.importCameras=false;im.isReadable=false;im.SaveAndReimport();
    var s=EditorSceneManager.OpenScene(Scene(f));var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith(f+"_Stealth_Level"));if(root.transform.Find("Arched_Interior"))throw new Exception("Already applied "+f);
    var group=new GameObject("Arched_Interior");group.transform.SetParent(root.transform,false);var visual=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(model),group.transform);visual.name="Rounded_Shell";
    foreach(var r in visual.GetComponentsInChildren<Renderer>()){r.sharedMaterials=r.sharedMaterials.Select(m=>mats[m.name]).ToArray();PrefabUtility.RecordPrefabInstancePropertyModifications(r);}
    var data=JObject.Parse(File.ReadAllText(Src+f+"_arches.json"));foreach(var row in data["colliders"]){var g=new GameObject((string)row["name"]);g.transform.SetParent(group.transform,false);g.transform.position=V(row["center"]);var c=g.AddComponent<BoxCollider>();c.size=V(row["size"]);}
    foreach(var row in data["lights"]){var g=new GameObject((string)row["name"]);g.transform.SetParent(group.transform,false);g.transform.position=V(row["position"]);g.transform.rotation=Quaternion.Euler(90,0,0);var l=g.AddComponent<Light>();l.type=LightType.Spot;l.intensity=(float)row["intensity"];l.range=(float)row["range"];l.spotAngle=(float)row["angle"];l.innerSpotAngle=80;l.color=new Color(.96f,.98f,1f);l.shadows=LightShadows.None;}
    int changedMaterials=0;foreach(var r in root.transform.Find("Architecture_Sections").GetComponentsInChildren<Renderer>()){
     var mm=r.sharedMaterials;bool change=false;for(int i=0;i<mm.Length;i++){Material target=mm[i].name=="LP_Ceiling"?ceiling:mm[i].name=="LP_Floor"?floor:mm[i].name=="LP_Plinth"?baseTrim:null;
      if(mm[i].name=="LP_Teal"&&(r.name.Contains("WallTeal")||r.name.Contains("WallPlinth")))target=mats["AR_Shell"];
      if(mm[i].name=="LP_SafetyPaint"&&(r.name.Contains("Accent")||r.name.Contains("SafetyPaint")))target=mats["AR_Champagne"];
      if(target){mm[i]=target;change=true;}}
     if(change){r.sharedMaterials=mm;PrefabUtility.RecordPrefabInstancePropertyModifications(r);changedMaterials++;}
    }
    // Broad neutral ambient fill keeps white arches legible without bright bloom/exposure.
    RenderSettings.ambientMode=AmbientMode.Trilight;RenderSettings.ambientSkyColor=new Color(.66f,.68f,.70f);RenderSettings.ambientEquatorColor=new Color(.47f,.49f,.51f);RenderSettings.ambientGroundColor=new Color(.24f,.25f,.27f);RenderSettings.ambientIntensity=1;
    var tuned=new List<object>();foreach(var l in root.GetComponentsInChildren<Light>()){
     if(l.transform.IsChildOf(group.transform))continue;bool main=l.name.StartsWith("Ceiling_")||P(l.transform).Contains("/Fixture_Lighting/")||P(l.transform).Contains("/Lighting/");if(!main)continue;
     float old=l.intensity;l.color=new Color(.97f,.985f,1f);if(l.type==LightType.Point)l.intensity=Mathf.Clamp(l.intensity,2.0f,7f);else if(l.type==LightType.Spot)l.intensity=Mathf.Clamp(l.intensity,12f,30f);tuned.Add(new{l.name,before=old,after=l.intensity});
    }
    var volume=root.GetComponentsInChildren<Volume>().Single(v=>v.name=="Lab_Tone");string vp=Root+"06.Data/AR_InteriorTone_"+f+".asset";if(!AssetDatabase.LoadAssetAtPath<VolumeProfile>(vp)){if(!AssetDatabase.CopyAsset(AssetDatabase.GetAssetPath(volume.sharedProfile),vp))throw new Exception("Profile copy failed");}
    var profile=AssetDatabase.LoadAssetAtPath<VolumeProfile>(vp);profile.TryGet<Tonemapping>(out var tone);tone.mode.Override(TonemappingMode.Neutral);profile.TryGet<ColorAdjustments>(out var ca);ca.postExposure.Override(0);ca.contrast.Override(3);ca.saturation.Override(-2);ca.colorFilter.Override(Color.white);profile.TryGet<Bloom>(out var bloom);bloom.threshold.Override(1.4f);bloom.intensity.Override(.02f);bloom.scatter.Override(.30f);foreach(var c in profile.components)EditorUtility.SetDirty(c);EditorUtility.SetDirty(profile);volume.sharedProfile=profile;AssetDatabase.SaveAssetIfDirty(profile);
    EditorSceneManager.MarkSceneDirty(s);EditorSceneManager.SaveScene(s);rows.Add(new{floor=f,arches=(int)data["arches"],curvedRooms=data["roomsWithCoves"],addedColliders=data["colliders"].Count(),addedLights=data["lights"].Count(),newTriangles=(int)data["triangles"],changedMaterials,tuned});
   }
  }finally{Application.logMessageReceived-=cb;if(!SceneManager.GetActiveScene().isDirty)EditorSceneManager.OpenScene(original);}Write("applied",new{rows,logs});return new{rows,logs};
 }
}
