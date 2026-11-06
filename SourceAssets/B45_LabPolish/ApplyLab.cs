// B5/B4 lab art polish V0.01. Editor-only authoring, outside Unity Assets.
using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
public static class ApplyLab {
 const string Root="Assets/Afrer_Seconds/";
 const string Common=Root+"05.Model/Environment/Common/";
 const string Props=Root+"05.Model/Props/Common/";
 static string Repo=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 static readonly Dictionary<string,Material> materials=new Dictionary<string,Material>();
 static void Write(string name,object value){var p=Repo+"/Docs/검수/2026-11-06_LabPolish/"+name+".json";Directory.CreateDirectory(Path.GetDirectoryName(p));File.WriteAllText(p,JsonConvert.SerializeObject(value,Formatting.Indented));}
 static Transform Child(string name,Transform parent,Vector3 position){var g=new GameObject(name);g.transform.SetParent(parent,false);g.transform.localPosition=position;return g.transform;}
 static float[] V(Vector3 p)=>new[]{p.x,p.y,p.z};
 static Material Mat(string name,Color color,float metal,float smooth,string family="Coating",float normal=.15f,float glow=0){
  string path=Common+"Materials/LP_"+name+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);if(!m){m=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(m,path);}m.name="LP_"+name;m.SetColor("_BaseColor",color);m.SetColor("_Color",color);m.SetFloat("_Metallic",metal);m.SetFloat("_Smoothness",smooth);m.SetFloat("_BumpScale",normal);
  m.SetTexture("_MetallicGlossMap",null);m.DisableKeyword("_METALLICSPECGLOSSMAP");
  if(family!=null){m.SetTexture("_BaseMap",AssetDatabase.LoadAssetAtPath<Texture>(Common+"Textures/LP_"+family+"_Base.png"));m.SetTexture("_BumpMap",AssetDatabase.LoadAssetAtPath<Texture>(Common+"Textures/LP_"+family+"_Normal.png"));m.SetTexture("_MetallicGlossMap",AssetDatabase.LoadAssetAtPath<Texture>(Common+"Textures/LP_"+family+"_MetallicSmoothness.png"));m.SetFloat("_Smoothness",smooth/(family=="Stainless"?.48f:family=="Concrete"?.18f:.30f));m.EnableKeyword("_METALLICSPECGLOSSMAP");m.EnableKeyword("_NORMALMAP");}
  else{m.SetTexture("_BaseMap",null);m.SetTexture("_BumpMap",null);m.DisableKeyword("_NORMALMAP");}
  m.SetColor("_EmissionColor",color*glow);if(glow>0)m.EnableKeyword("_EMISSION");else m.DisableKeyword("_EMISSION");m.globalIlluminationFlags=MaterialGlobalIlluminationFlags.None;EditorUtility.SetDirty(m);AssetDatabase.SaveAssetIfDirty(m);materials[name]=m;return m;
 }
 static void Materials(){
  foreach(string file in Directory.GetFiles(Common+"Textures","LP_*.png")){var t=(TextureImporter)AssetImporter.GetAtPath(file.Replace('\\','/'));if(!t)continue;t.sRGBTexture=file.Contains("_Base");t.textureType=file.Contains("_Normal")?TextureImporterType.NormalMap:TextureImporterType.Default;t.wrapMode=TextureWrapMode.Repeat;t.anisoLevel=4;t.maxTextureSize=512;t.isReadable=false;t.SaveAndReimport();}
  Mat("Coating",new Color(.55f,.60f,.59f),0,.30f);Mat("WallClean",new Color(.62f,.67f,.64f),0,.24f);Mat("WallStaff",new Color(.53f,.59f,.57f),0,.22f);Mat("WallConcrete",new Color(.44f,.47f,.46f),0,.16f,"Concrete",.12f);Mat("WallSteel",new Color(.30f,.38f,.39f),0,.32f);Mat("Ceiling",new Color(.43f,.47f,.46f),0,.16f);Mat("Floor",new Color(.24f,.29f,.29f),0,.24f,"Concrete",.12f);Mat("Core",new Color(.13f,.17f,.18f),0,.18f);Mat("Plinth",new Color(.10f,.15f,.16f),0,.28f);Mat("Graphite",new Color(.07f,.09f,.095f),0,.30f);Mat("Teal",new Color(.07f,.27f,.26f),0,.30f);Mat("SafetyPaint",new Color(.55f,.32f,.08f),0,.30f);
  Mat("Stainless",new Color(.57f,.60f,.62f),.94f,.46f,"Stainless",.18f);Mat("Pipe",new Color(.47f,.51f,.52f),.92f,.41f,"Stainless",.12f);Mat("Rubber",new Color(.018f,.023f,.023f),0,.12f,null);Mat("Glass",new Color(.07f,.19f,.21f),.15f,.75f,null);Mat("Legend",new Color(.68f,.73f,.70f),0,.28f,null);Mat("Screen",new Color(.06f,.22f,.19f),0,.35f,null,0,.4f);Mat("Indicator",new Color(.13f,.56f,.40f),0,.35f,null,0,.55f);Mat("Amber",new Color(.62f,.28f,.04f),0,.35f,null,0,.5f);var lamp=Mat("Lamp",new Color(.58f,.70f,.65f),0,.25f,null,0,0);lamp.shader=Shader.Find("Universal Render Pipeline/Unlit");EditorUtility.SetDirty(lamp);AssetDatabase.SaveAssetIfDirty(lamp);
 }
 static Material Mapping(string name){
  name=name.Replace(" (Instance)","");if(name.StartsWith("LP_")&&materials.ContainsKey(name.Substring(3)))return materials[name.Substring(3)];
  if(name.Contains("PipeSteel"))return materials["Pipe"];if(name.Contains("PipeCoupling")||name.Contains("Handrail")||name.Contains("WallTrim"))return materials["Stainless"];
  if(name.Contains("WallSterile")||name.EndsWith("Clinical")||name.EndsWith("Panel"))return materials["WallClean"];
  if(name.Contains("WallConcrete"))return materials["WallConcrete"];if(name.Contains("WallStaff"))return materials["WallStaff"];if(name.Contains("WallSteel")||name.EndsWith("Service"))return materials["WallSteel"];
  if(name.Contains("Plinth"))return materials["Plinth"];if(name.Contains("Teal"))return materials["Teal"];if(name.EndsWith("Light"))return materials["Lamp"];if(name.EndsWith("Floor"))return materials["Floor"];if(name.EndsWith("Ceiling"))return materials["Ceiling"];if(name.EndsWith("Core"))return materials["Core"];if(name.EndsWith("Hazard")||name.EndsWith("Accent"))return materials["SafetyPaint"];if(name.EndsWith("Metal")||name.Contains("PaintedSteel")||name.Contains("Grille"))return materials["Graphite"];
  if(name=="B4_Glass")return AssetDatabase.LoadAssetAtPath<Material>(Root+"05.Model/Environment/B4/Materials/B4_Glass.mat");
  if(name=="SL_Water")return AssetDatabase.LoadAssetAtPath<Material>(Root+"05.Model/Environment/B5/Materials/SL_Water.mat");
  return null;
 }
 static void Remap(GameObject go){foreach(var r in go.GetComponentsInChildren<Renderer>(true)){var mm=r.sharedMaterials;for(int i=0;i<mm.Length;i++){var m=mm[i]?Mapping(mm[i].name):null;if(m)mm[i]=m;}r.sharedMaterials=mm;PrefabUtility.RecordPrefabInstancePropertyModifications(r);}}
 public static object Import(){
  var logs=new List<string>();Application.LogCallback capture=(m,s,t)=>{if(t==LogType.Warning||t==LogType.Error||t==LogType.Exception)logs.Add(m);};Application.logMessageReceived+=capture;
  try{AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);Materials();foreach(string floor in new[]{"B5","B4"}){string path=Root+"05.Model/Environment/"+floor+"/LP_"+floor+"_Architecture.fbx";var imp=(ModelImporter)AssetImporter.GetAtPath(path);imp.importCameras=false;imp.importLights=false;imp.importAnimation=false;imp.materialImportMode=ModelImporterMaterialImportMode.ImportStandard;imp.SaveAndReimport();}
   foreach(string name in new[]{"DoubleSlidingDoor","Keypad","SampleTrolley","SampleColdCabinet","BenchAnalyzer","WorkLight"}){
    string path=Props+"LP_"+name+".fbx";AssetDatabase.ImportAsset(path,ImportAssetOptions.ForceSynchronousImport);var imp=(ModelImporter)AssetImporter.GetAtPath(path);imp.importAnimation=false;imp.importLights=false;imp.importCameras=false;imp.SaveAndReimport();var model=AssetDatabase.LoadAssetAtPath<GameObject>(path);var root=new GameObject("LP_"+name);var visual=(GameObject)PrefabUtility.InstantiatePrefab(model,root.transform);Remap(visual);
    if(name=="DoubleSlidingDoor"){
     PrefabUtility.UnpackPrefabInstance(visual,PrefabUnpackMode.Completely,InteractionMode.AutomatedAction);
     foreach(int side in new[]{-1,1}){string key=side<0?"Left":"Right";var mesh=visual.GetComponentsInChildren<Transform>().Single(t=>t.name==(side<0?"Leaf_L":"Leaf_R"));var leaf=Child("Leaf_"+key,root.transform,new Vector3(side*.376f,0,0));mesh.SetParent(leaf,true);var c=leaf.gameObject.AddComponent<BoxCollider>();c.center=new Vector3(0,1.37f,0);c.size=new Vector3(.746f,2.72f,.095f);Child(key+"_Closed",root.transform,new Vector3(side*.376f,0,0));Child(key+"_Open",root.transform,new Vector3(side*1.126f,0,0));}
     visual.name="Fixed_Frame";
    }else if(name!="Keypad"&&name!="WorkLight"){
     var rr=visual.GetComponentsInChildren<Renderer>();var b=rr[0].bounds;foreach(var r in rr.Skip(1))b.Encapsulate(r.bounds);var c=root.AddComponent<BoxCollider>();c.center=b.center;c.size=b.size;
    }
    PrefabUtility.SaveAsPrefabAsset(root,Props+"LP_"+name+".prefab");UnityEngine.Object.DestroyImmediate(root);
   }
  }finally{Application.logMessageReceived-=capture;}Write("import",new{logs});return new{logs,materials=materials.Count};
 }
 static void LoadMaterials(){if(materials.Count==0)foreach(string guid in AssetDatabase.FindAssets("LP_ t:Material",new[]{Common+"Materials"})){var m=AssetDatabase.LoadAssetAtPath<Material>(AssetDatabase.GUIDToAssetPath(guid));if(m.name.StartsWith("LP_"))materials[m.name.Substring(3)]=m;}}
 public static object RefreshMaterials(){Materials();return new{materials=materials.Count};}
 public static object Calibrate(){
  LoadMaterials();var lamp=materials["Lamp"];lamp.shader=Shader.Find("Universal Render Pipeline/Unlit");lamp.SetColor("_BaseColor",new Color(.58f,.70f,.65f,1));lamp.SetTexture("_BaseMap",null);EditorUtility.SetDirty(lamp);AssetDatabase.SaveAssetIfDirty(lamp);
  foreach(string floor in new[]{"B5","B4"}){
   var s=EditorSceneManager.OpenScene(Root+"01.Scenes/Stage/Level_"+floor+"_Stealth.unity");var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith(floor+"_Stealth_Level"));
   var profile=AssetDatabase.LoadAssetAtPath<VolumeProfile>(Root+"06.Data/LP_LabTone_"+floor+".asset");profile.TryGet<Tonemapping>(out var tone);tone.mode.Override(TonemappingMode.Neutral);profile.TryGet<ColorAdjustments>(out var color);color.postExposure.Override(0);color.contrast.Override(0);EditorUtility.SetDirty(tone);EditorUtility.SetDirty(color);AssetDatabase.SaveAssetIfDirty(profile);
   if(floor=="B4"){RenderSettings.ambientSkyColor=new Color(.42f,.47f,.48f);RenderSettings.ambientEquatorColor=new Color(.28f,.32f,.33f);RenderSettings.ambientGroundColor=new Color(.14f,.17f,.18f);foreach(var l in root.transform.Find("Lighting").GetComponentsInChildren<Light>()){l.intensity=l.type==LightType.Point?.40f:l.name=="Ceiling_D"?5.3f:4.0f;}}
   Remap(root.transform.Find("Architecture_LabPolish").gameObject);EditorSceneManager.MarkSceneDirty(s);EditorSceneManager.SaveScene(s);
  }
  return "Neutral highlight rolloff, visible lamp diffusers, B4 fill calibrated";
 }
 static GameObject Instance(string type,string name,Transform parent,Vector3 pos,float yaw=0){var g=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Props+"LP_"+type+".prefab"),parent);g.name=name;g.transform.localPosition=pos;g.transform.localRotation=Quaternion.Euler(0,yaw,0);return g;}
 static void Tone(GameObject root,string floor){
  if(!UniversalRenderPipeline.asset||!UniversalRenderPipeline.asset.supportsHDR)throw new Exception("URP HDR required");
  string path=Root+"06.Data/LP_LabTone_"+floor+".asset";var p=AssetDatabase.LoadAssetAtPath<VolumeProfile>(path);if(!p){p=ScriptableObject.CreateInstance<VolumeProfile>();AssetDatabase.CreateAsset(p,path);var t=p.Add<Tonemapping>();t.mode.Override(TonemappingMode.Neutral);AssetDatabase.AddObjectToAsset(t,p);var c=p.Add<ColorAdjustments>();c.postExposure.Override(0);c.contrast.Override(0);c.saturation.Override(-4);AssetDatabase.AddObjectToAsset(c,p);var b=p.Add<Bloom>();b.threshold.Override(1.35f);b.intensity.Override(.025f);b.scatter.Override(.35f);AssetDatabase.AddObjectToAsset(b,p);EditorUtility.SetDirty(p);AssetDatabase.SaveAssetIfDirty(p);}
  var go=Child("Lab_Tone",root.transform,Vector3.zero).gameObject;var v=go.AddComponent<Volume>();v.isGlobal=true;v.priority=20;v.sharedProfile=p;
  foreach(var cam in root.scene.GetRootGameObjects().SelectMany(o=>o.GetComponentsInChildren<Camera>(true))){var d=cam.GetComponent<UniversalAdditionalCameraData>();if(d){d.renderPostProcessing=true;d.volumeLayerMask|=1;}}
 }
 static void Lights(GameObject root,string floor){
  RenderSettings.ambientMode=AmbientMode.Trilight;RenderSettings.ambientSkyColor=new Color(.32f,.36f,.38f);RenderSettings.ambientEquatorColor=new Color(.20f,.23f,.25f);RenderSettings.ambientGroundColor=new Color(.10f,.12f,.13f);RenderSettings.ambientIntensity=1;
  if(floor=="B4"){RenderSettings.ambientSkyColor=new Color(.42f,.47f,.48f);RenderSettings.ambientEquatorColor=new Color(.28f,.32f,.33f);RenderSettings.ambientGroundColor=new Color(.14f,.17f,.18f);}
  foreach(var l in root.GetComponentsInChildren<Light>(true)){
   if(floor=="B5")l.intensity*=l.intensity>=50?.43f:.48f;else l.intensity=l.type==LightType.Point?.40f:l.name=="Ceiling_D"?5.3f:4.0f;
   l.color=new Color(.84f,.92f,.90f);if(l.type==LightType.Spot){l.innerSpotAngle=Mathf.Min(l.innerSpotAngle,80);l.spotAngle=Mathf.Clamp(l.spotAngle,112,135);}
   if(l.type==LightType.Point)l.range=Mathf.Min(l.range,5.0f);
  }
 }
 public static object Apply(){
  if(EditorApplication.isPlaying||SceneManager.GetActiveScene().isDirty)throw new Exception("Saved Edit scene required");LoadMaterials();var plans=JObject.Parse(File.ReadAllText(Repo+"/Docs/도면/잠입_탐색/layout.json"));var reports=new List<object>();
  foreach(string floor in new[]{"B5","B4"}){
   var scene=EditorSceneManager.OpenScene(Root+"01.Scenes/Stage/Level_"+floor+"_Stealth.unity");var root=scene.GetRootGameObjects().Single(g=>g.name.StartsWith(floor+"_Stealth_Level"));if(root.transform.Find("Lab_Doors"))throw new Exception("Already applied; use targeted adjustments");
   var old=root.transform.Find(floor=="B5"?"Architecture_Blender_Bevelled":"B4_Architecture");if(!old||old.GetComponentsInChildren<Collider>(true).Length>0)throw new Exception("Unexpected architecture collision ownership");
   var arch=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Root+"05.Model/Environment/"+floor+"/LP_"+floor+"_Architecture.fbx"),root.transform);arch.name="Architecture_LabPolish";arch.transform.localPosition=old.localPosition;arch.transform.localRotation=old.localRotation;arch.transform.localScale=old.localScale;Remap(arch);UnityEngine.Object.DestroyImmediate(old.gameObject);
   // Shared fixture meshes keep their geometry; only this scene's material references change.
   foreach(var r in root.GetComponentsInChildren<Renderer>(true)){var mats=r.sharedMaterials;bool changed=false;for(int i=0;i<mats.Length;i++)if(mats[i]&&(mats[i].name=="SL_Light"||mats[i].name=="B4_Light")){mats[i]=materials["Lamp"];changed=true;}if(changed){r.sharedMaterials=mats;PrefabUtility.RecordPrefabInstancePropertyModifications(r);}}
   int removed=0;foreach(var c in root.GetComponentsInChildren<Collider>(true).Where(c=>c.name.StartsWith("LockedDoor")).ToArray()){UnityEngine.Object.DestroyImmediate(c);removed++;}
   var doorRoot=Child("Lab_Doors",root.transform,Vector3.zero);var plan=plans["floors"].Single(f=>(string)f["floor"]==floor);int index=0;var doors=new List<object>();
   foreach(var d in plan["doors"]){bool open=(string)d["state"]=="open";var pos=new Vector3((float)d["x"]-24,0,(float)d["y"]-16);var door=Instance("DoubleSlidingDoor","Door_"+index.ToString("D2")+"_"+(string)d["a"]+"_"+(string)d["b"],doorRoot,pos,(string)d["axis"]=="H"?0:90);
    foreach(string side in new[]{"Left","Right"}){var leaf=door.transform.Find("Leaf_"+side);leaf.localPosition=door.transform.Find(side+(open?"_Open":"_Closed")).localPosition;PrefabUtility.RecordPrefabInstancePropertyModifications(leaf);}
    foreach(int side in new[]{-1,1})Instance("Keypad","Keypad_"+(side<0?"Back":"Front"),door.transform,new Vector3(side*.98f,1.35f,side*.20f),side<0?180:0);
    if(!open)foreach(var r in door.GetComponentsInChildren<Renderer>()){var mm=r.sharedMaterials;for(int i=0;i<mm.Length;i++)if(mm[i]==materials["Indicator"])mm[i]=materials["Amber"];r.sharedMaterials=mm;PrefabUtility.RecordPrefabInstancePropertyModifications(r);}
    doors.Add(new{index,name=door.name,open,position=V(pos),slideTravel=.75f,keypads=2});index++;
   }
   var props=Child("Lab_Additional_Props",root.transform,Vector3.zero);var placements=new List<object>();
   Action<string,string,float,float,float> Place=(type,name,u,v,yaw)=>{var g=Instance(type,name,props,new Vector3(u-24,0,v-16),yaw);placements.Add(new{name,type,u,v,yaw});};
   if(floor=="B5"){
    Place("SampleColdCabinet","Isolation_ColdSamples",18.25f,5.3f,270);Place("BenchAnalyzer","Isolation_Analyzer",17.95f,12.2f,270);Place("SampleTrolley","Isolation_SampleCart",4.6f,21.7f,15);Place("SampleColdCabinet","Vestibule_ColdSamples",10.05f,31.15f,180);Place("BenchAnalyzer","Monitoring_Analyzer",25.9f,30.9f,180);Place("SampleTrolley","Utility_SampleCart",33.8f,28.0f,90);
   }else{
    Place("SampleColdCabinet","AN_ColdSamples",3.65f,4.9f,90);Place("BenchAnalyzer","AN_Analyzer",10.95f,5.0f,0);Place("SampleTrolley","AN_SampleCart",10.7f,11.0f,0);Place("SampleColdCabinet","AS_ColdSamples",3.65f,14.9f,90);Place("BenchAnalyzer","AS_Analyzer",10.9f,14.9f,0);Place("SampleTrolley","AS_SampleCart",10.4f,21.1f,0);Place("BenchAnalyzer","Data_Analyzer",34.9f,5.1f,270);Place("SampleColdCabinet","Preparation_ColdSamples",17.25f,28.0f,270);Place("SampleTrolley","Support_SampleCart",7.2f,31.0f,0);
   }
   foreach(Transform prop in props)foreach(var t in prop.GetComponentsInChildren<Transform>(true))t.gameObject.isStatic=true;
   Lights(root,floor);Tone(root,floor);
   var tasks=Child("Lab_Task_Lighting",root.transform,Vector3.zero);int taskCount=0;
   foreach(var analyzer in props.Cast<Transform>().Where(t=>t.name.Contains("Analyzer"))){var fixture=Instance("WorkLight","Shielded_WorkLight_"+taskCount,tasks,analyzer.localPosition+Vector3.up*2.30f,analyzer.eulerAngles.y);var light=Child("Work_Pool",fixture.transform,new Vector3(0,-.10f,.07f)).gameObject.AddComponent<Light>();light.type=LightType.Spot;light.transform.localRotation=Quaternion.Euler(90,0,0);light.intensity=2.4f;light.range=3.1f;light.spotAngle=95;light.innerSpotAngle=60;light.color=new Color(.94f,.96f,.90f);light.shadows=LightShadows.None;taskCount++;}
   EditorSceneManager.MarkSceneDirty(scene);EditorSceneManager.SaveScene(scene);reports.Add(new{floor,doors,removedFormerDoorColliders=removed,placements,newTaskLights=taskCount,lights=root.GetComponentsInChildren<Light>().Length});
  }
  Write("applied",reports);return reports;
 }
}
