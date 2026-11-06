using System;using System.IO;using System.Linq;using System.Collections.Generic;using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.SceneManagement;using UnityEngine.Rendering;using UnityEngine.Rendering.Universal;using Newtonsoft.Json;using Newtonsoft.Json.Linq;
public static class ApplySector {
 const string A="Assets/Afrer_Seconds/",E=A+"05.Model/Environment/B5/",P=A+"05.Model/Props/B5/";
 static string R=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));static string S=>R+"/SourceAssets/B5_Sector01/";static string O=>R+"/Docs/검수/2026-11-06_B5_Sector01/";
 static Color C(string h){Color c;ColorUtility.TryParseHtmlString(h,out c);return c;}
 static void Ready(){if(EditorApplication.isPlaying||SceneManager.GetActiveScene().isDirty)throw new Exception("Saved edit scene required");Directory.CreateDirectory(O);}
 static Material Mat(string kind){string path=E+"Materials/S1_"+kind+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);if(!m){m=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(m,path);}
 var defs=new Dictionary<string,string>{{"Coat","#B6C5CB"},{"Steel","#76838C"},{"Dark","#26313A"},{"Lamp","#C4DDEB"},{"Floor","#67757E"},{"Linen","#B7C3C9"},{"Paper","#D0D0C5"},{"Screen","#183B42"},{"Mirror","#B6CBD4"},{"Shell","#B8C4CA"}};
 m.SetColor("_BaseColor",C(defs[kind]));m.SetFloat("_Metallic",kind=="Steel"||kind=="Mirror"?.92f:.04f);m.SetFloat("_Smoothness",kind=="Steel"?.43f:kind=="Mirror"?.84f:kind=="Linen"?.07f:.29f);
 string family=kind=="Floor"?"Floor":kind=="Linen"?"Linen":"Coat";
 if(new[]{"Coat","Shell","Floor","Linen"}.Contains(kind)){m.SetTexture("_BaseMap",AssetDatabase.LoadAssetAtPath<Texture>(E+"Textures/S1_"+family+"_Base.png"));m.SetTexture("_MetallicGlossMap",AssetDatabase.LoadAssetAtPath<Texture>(E+"Textures/S1_"+family+"_MetallicSmoothness.png"));m.SetFloat("_Smoothness",1);m.EnableKeyword("_METALLICSPECGLOSSMAP");}
 if(kind=="Steel"){string ec=A+"05.Model/Environment/Common/Textures/";m.SetTexture("_BaseMap",AssetDatabase.LoadAssetAtPath<Texture>(ec+"CFD_Steel_Base.png"));m.SetTexture("_MetallicGlossMap",AssetDatabase.LoadAssetAtPath<Texture>(ec+"CFD_Steel_MetallicSmoothness.png"));m.EnableKeyword("_METALLICSPECGLOSSMAP");m.SetFloat("_Smoothness",.88f);}
 if(kind!="Lamp"&&kind!="Mirror"){m.SetTexture("_BumpMap",AssetDatabase.LoadAssetAtPath<Texture>(E+"Textures/S1_Micro_Normal.png"));m.EnableKeyword("_NORMALMAP");m.SetFloat("_BumpScale",.16f);}
 if(kind=="Lamp"){m.EnableKeyword("_EMISSION");m.SetColor("_EmissionColor",C("#BED3DE")*.3f);}EditorUtility.SetDirty(m);return m;
 }
 static Bounds Bounds(GameObject g){var rr=g.GetComponentsInChildren<Renderer>(true).Where(r=>!r.name.Contains("_LOD")||r.name.EndsWith("_LOD0")).ToArray();var b=rr[0].bounds;foreach(var x in rr.Skip(1))b.Encapsulate(x.bounds);return b;}
 public static object Import(){Ready();Directory.CreateDirectory(Path.Combine(Path.GetDirectoryName(Application.dataPath),E+"Materials"));AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);var logs=new List<string>();Application.LogCallback log=(m,s,t)=>{if(t==LogType.Warning||t==LogType.Error||t==LogType.Exception)logs.Add(m);};Application.logMessageReceived+=log;
 try{
 foreach(string guid in AssetDatabase.FindAssets("S1_ t:Texture2D",new[]{E+"Textures",P+"Textures"})){string path=AssetDatabase.GUIDToAssetPath(guid);var t=(TextureImporter)AssetImporter.GetAtPath(path);t.sRGBTexture=!path.Contains("Normal")&&!path.Contains("MetallicSmoothness")&&!path.Contains("ORM");if(path.Contains("Normal"))t.textureType=TextureImporterType.NormalMap;t.maxTextureSize=path.Contains("Albedo")?2048:1024;t.SaveAndReimport();}
 var mats=new Dictionary<string,Material>();foreach(string k in new[]{"Coat","Steel","Dark","Lamp","Floor","Linen","Paper","Screen","Mirror","Shell"})mats["S1_"+k]=Mat(k);
 var man=JObject.Parse(File.ReadAllText(S+"detail_manifest.json"));foreach(var row in man){string path=((bool)row.Value["props"]?P:E)+row.Key+".fbx";var imp=AssetImporter.GetAtPath(path) as ModelImporter;imp.importAnimation=false;imp.importCameras=false;imp.importLights=false;imp.isReadable=true;imp.SaveAndReimport();var g=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(path));g.name=row.Key;
  foreach(var rr in g.GetComponentsInChildren<Renderer>())rr.sharedMaterials=rr.sharedMaterials.Select(m=>mats.TryGetValue(m.name.Split('.')[0],out var found)?found:m).ToArray();
  if((bool)row.Value["collide"])foreach(var mf in g.GetComponentsInChildren<MeshFilter>()){var co=mf.gameObject.AddComponent<MeshCollider>();co.sharedMesh=mf.sharedMesh;}
  PrefabUtility.SaveAsPrefabAsset(g,path.Replace(".fbx",".prefab"));UnityEngine.Object.DestroyImmediate(g);
 }
 foreach(var name in new[]{"IsolationBed","SanitaryUnit","VitalMonitor"}){
  var materialrows=JObject.Parse(File.ReadAllText(S+name+"_manifest.json"))["materials"];var propmats=new Dictionary<string,Material>();foreach(var row in materialrows){string key=(string)row["name"],mp=P+"Materials/"+key+".mat";var mat=AssetDatabase.LoadAssetAtPath<Material>(mp);if(!mat){mat=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(mat,mp);}mat.SetColor("_BaseColor",Color.white);mat.SetFloat("_Smoothness",1);
   foreach(var kv in new[]{new[]{"Albedo","_BaseMap"},new[]{"MetallicSmoothness","_MetallicGlossMap"},new[]{"Normal","_BumpMap"}})mat.SetTexture(kv[1],AssetDatabase.LoadAssetAtPath<Texture>(P+"Textures/"+(string)row[kv[0]]));mat.EnableKeyword("_NORMALMAP");mat.EnableKeyword("_METALLICSPECGLOSSMAP");mat.SetFloat("_BumpScale",.42f);EditorUtility.SetDirty(mat);propmats[key]=mat;}
  string path=P+"S1_"+name+".fbx";var imp=AssetImporter.GetAtPath(path) as ModelImporter;imp.importAnimation=false;imp.importCameras=false;imp.importLights=false;imp.isReadable=true;imp.SaveAndReimport();var g=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(path));g.name="S1_"+name;foreach(var rr in g.GetComponentsInChildren<Renderer>())rr.sharedMaterials=rr.sharedMaterials.Select(m=>propmats.TryGetValue(m.name,out var found)?found:m).ToArray();
  var lod=g.GetComponent<LODGroup>()??g.AddComponent<LODGroup>();var rend=g.GetComponentsInChildren<Renderer>();lod.SetLODs(new[]{new LOD(.23f,rend.Where(r=>r.name.EndsWith("_LOD0")).ToArray()),new LOD(.075f,rend.Where(r=>r.name.EndsWith("_LOD1")).ToArray()),new LOD(.012f,rend.Where(r=>r.name.EndsWith("_LOD2")).ToArray())});lod.RecalculateBounds();
  var b=Bounds(g);var co=g.AddComponent<BoxCollider>();co.center=g.transform.InverseTransformPoint(b.center);co.size=b.size;PrefabUtility.SaveAsPrefabAsset(g,path.Replace(".fbx",".prefab"));UnityEngine.Object.DestroyImmediate(g);
 }AssetDatabase.SaveAssets();}finally{Application.logMessageReceived-=log;}File.WriteAllText(O+"import.json",JsonConvert.SerializeObject(logs,Formatting.Indented));return new{logs};}
 static Transform root,group;static List<object> placed;
 static GameObject Group(string n,Transform p){var g=new GameObject(n);g.transform.SetParent(p,false);return g;}
 static GameObject Inst(string name,Vector3 local,float yaw=0,bool prop=false){string path=(prop?P:E)+name+".prefab";var a=AssetDatabase.LoadAssetAtPath<GameObject>(path);if(!a)throw new Exception("Missing "+path);var g=(GameObject)PrefabUtility.InstantiatePrefab(a,group);g.name=name+"_"+placed.Count.ToString("D2");g.transform.localPosition=local;g.transform.localRotation=Quaternion.Euler(0,yaw,0);placed.Add(new{g.name,asset=path,local=new[]{local.x,local.y,local.z},yaw});return g;}
 static void MoveOld(string name,Vector3 pos,float yaw){var t=root.Find("Existing_Props_FirstPass/"+name);if(!t)throw new Exception(name);t.localPosition=pos;t.localRotation=Quaternion.Euler(0,yaw,0);}
 static void Light(Transform parent,string name,Vector3 local,float intensity,float range,bool shadows=false){var g=Group(name,parent);g.transform.localPosition=local;var l=g.AddComponent<Light>();l.type=LightType.Point;l.color=C("#CEDDE6");l.intensity=intensity;l.range=range;l.shadows=shadows?LightShadows.Soft:LightShadows.None;l.shadowBias=.02f;l.shadowNormalBias=.12f;}
 public static object Apply(){Ready();var scene=SceneManager.GetActiveScene();if(!scene.path.EndsWith("Level_B5_Circular.unity"))throw new Exception(scene.path);root=scene.GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular")).transform;
 var previous=root.Find("Sector01_CompletedArt");if(previous)UnityEngine.Object.DestroyImmediate(previous.gameObject);group=Group("Sector01_CompletedArt",root).transform;group.localPosition=new Vector3(-15,0,-10);placed=new List<object>();
 Inst("S1_VaultRibs",Vector3.zero);Inst("S1_CoveRing",Vector3.zero);Inst("S1_FloorFinish",Vector3.zero);
 var shell=root.GetComponentsInChildren<Renderer>().Single(r=>r.name.StartsWith("CF_B5_C01_Dome"));shell.sharedMaterial=Mat("Shell");PrefabUtility.RecordPrefabInstancePropertyModifications(shell);
 foreach(Transform t in root.Find("B5_Art_C01_T01"))if(t.name.Contains("CFD_CovePanel"))t.gameObject.SetActive(false);
 foreach(var l in root.GetComponentsInChildren<Light>())if(l.name.StartsWith("C01_Work_"))l.enabled=false;
 foreach(float a0 in new[]{40f,140f,220f,320f}){float a=a0*Mathf.Deg2Rad;var p=new Vector3(Mathf.Cos(a)*9.34f,3.18f,Mathf.Sin(a)*9.34f);float yaw=Mathf.Atan2(-Mathf.Cos(a),-Mathf.Sin(a))*Mathf.Rad2Deg;var g=Inst("S1_WallTaskLight",p,yaw);Light(g.transform,"Wall_Worklight",new Vector3(0,-.16f,.83f),1.65f,7.2f,true);}
 // Living furnishing belongs inside the existing observation pod. Keep the pod's dimensions.
 Inst("S1_IsolationBed",new Vector3(-2.28f,0,-.45f),0,true);
 Inst("S1_SanitaryUnit",new Vector3(-.52f,0,2.68f),180,true);
 Inst("S1_PrivacyScreen",new Vector3(-.68f,0,1.48f),180);
 Inst("S1_PersonalLocker",new Vector3(1.82f,0,1.85f),220,true);
 MoveOld("B5-03_P03",new Vector3(-12.65f,0,-10.75f),270);
 root.Find("Existing_Props_FirstPass/B5-02_P02").gameObject.SetActive(false);
 root.Find("Existing_Props_FirstPass/B5-04_P04").gameObject.SetActive(false);
 Inst("S1_TabletopKit",new Vector3(2.45f,.762f,-.73f),270,true);
 Inst("S1_Slippers",new Vector3(-1.45f,.007f,-.8f),15,true);
 Inst("S1_PersonalBox",new Vector3(-2.15f,.01f,-1.88f),0,true);
 Inst("S1_HygieneKit",new Vector3(.02f,.88f,2.62f),180,true);
 Inst("S1_Mirror",new Vector3(.025f,.83f,1.92f),270);
 Inst("S1_CallPanel",new Vector3(-.68f,.88f,1.53f),0);
 Inst("S1_SpecimenPlate",new Vector3(.92f,.8f,-3.95f),180);
 // Staff-side diagnostic and provisioning arc, leaving the annular passage open.
 MoveOld("B5-06_P09",new Vector3(-12.15f,0,-16.35f),25);
 MoveOld("B5-07_P13",new Vector3(-15.0f,0,-18.5f),0);
 Inst("S1_VitalMonitor",new Vector3(-2.7f,0,-5.55f),-25,true);
 Inst("S1_RecordBoard",new Vector3(-.23f,1.25f,-8.17f),0);
 Inst("S1_Clock",new Vector3(-.02f,1.72f,-8.40f),0);
 Inst("S1_ServiceRiser",new Vector3(5.7f,.03f,-6.35f),-35);
 // Overhead pod task lights attach to existing crown; no floating floor-level light points.
 Light(group,"Pod_Interior_Task",new Vector3(0,5.9f,0),2.4f,7.2f,false);
 Light(group,"Living_Indirect",new Vector3(-1,2.8f,.3f),.30f,4.5f,false);
 // The laboratory glass should expose the living interior without a mirror-like glare.
 var glass=root.GetComponentsInChildren<Renderer>(true).Single(r=>r.name=="ObservationPod_GlassShell");string gp=E+"Materials/S1_PodGlass.mat";var gm=AssetDatabase.LoadAssetAtPath<Material>(gp);if(!gm){gm=new Material(glass.sharedMaterial);AssetDatabase.CreateAsset(gm,gp);}gm.SetColor("_BaseColor",new Color(.82f,.90f,.95f,.075f));gm.SetFloat("_Smoothness",.77f);glass.sharedMaterial=gm;PrefabUtility.RecordPrefabInstancePropertyModifications(glass);EditorUtility.SetDirty(gm);
 // Articulated surveillance mesh stays in Enemy and is static here.
 var cctv=AssetDatabase.LoadAssetAtPath<GameObject>(A+"05.Model/Enemy/CCTV_SecurityCamera_Articulated.prefab");var cg=(GameObject)PrefabUtility.InstantiatePrefab(cctv,group);cg.name="S1_CCTV_Static";cg.transform.localPosition=new Vector3(4.7f,2.7f,6.8f);cg.transform.localRotation=Quaternion.Euler(0,215,0);var cb=Bounds(cg);float scale=.58f/Mathf.Max(cb.size.x,cb.size.y,cb.size.z);cg.transform.localScale*=scale;
 // Fixed-base mounting post is supplied by an authored service riser.
 Inst("S1_ServiceRiser",new Vector3(4.7f,.02f,6.8f),215);
 Physics.SyncTransforms();AssetDatabase.SaveAssets();EditorSceneManager.MarkSceneDirty(scene);EditorSceneManager.SaveScene(scene);
 File.WriteAllText(O+"placements.json",JsonConvert.SerializeObject(placed,Formatting.Indented));var sv=SceneView.lastActiveSceneView;if(sv){sv.LookAt(new Vector3(-15,-79.5f,-10),Quaternion.Euler(18,145,0),13,false,true);sv.Repaint();}
 return new{newInstances=placed.Count,group=group.name,scene=scene.path};}
 public static object Bake(){Ready();var scene=SceneManager.GetActiveScene();var rr=scene.GetRootGameObjects().Where(g=>g.name.StartsWith("Player")).SelectMany(g=>g.GetComponentsInChildren<Renderer>(true)).ToArray();var states=rr.Select(r=>r.enabled).ToArray();foreach(var r in rr)r.enabled=false;int count=0;
 try{foreach(var p in scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<ReflectionProbe>()).Where(p=>p.name.Contains("C01"))){var file=E+"Textures/S1_Reflection_"+p.name+".exr";if(!Lightmapping.BakeReflectionProbe(p,file))throw new Exception("Bake failed "+p.name);AssetDatabase.ImportAsset(file,ImportAssetOptions.ForceSynchronousImport);p.customBakedTexture=AssetDatabase.LoadAssetAtPath<Cubemap>(file);count++;}}finally{for(int i=0;i<rr.Length;i++)rr[i].enabled=states[i];}EditorSceneManager.SaveScene(scene);return new{baked=count};}
 public static object Capture(){Ready();var s=SceneManager.GetActiveScene();var rr=s.GetRootGameObjects().Where(g=>g.name.StartsWith("Player")).SelectMany(g=>g.GetComponentsInChildren<Renderer>(true)).ToArray();var was=rr.Select(r=>r.enabled).ToArray();foreach(var r in rr)r.enabled=false;
 var shots=new[]{new{name="S1_Entrance",p=new Vector3(-17.2f,-80.35f,-1.3f),t=new Vector3(-14.5f,-80.1f,-11.8f)},new{name="S1_Inside_Living",p=new Vector3(-14.4f,-80.35f,-12.9f),t=new Vector3(-16,-80.9f,-8.5f)},new{name="S1_Inside_Desk",p=new Vector3(-16.5f,-80.35f,-10.5f),t=new Vector3(-12.5f,-81.05f,-10.5f)},new{name="S1_Staff_Arc",p=new Vector3(-20.6f,-80.35f,-15.4f),t=new Vector3(-13,-80.9f,-16.5f)},new{name="S1_Overview",p=new Vector3(-21.4f,-77.9f,-5.5f),t=new Vector3(-13,-80,-11)},new{name="S1_Structure",p=new Vector3(-8.2f,-80.35f,-6),t=new Vector3(-20,-76,-12)},new{name="S1_Hygiene",p=new Vector3(-13.9f,-80.6f,-6.65f),t=new Vector3(-15.6f,-81.2f,-7.65f)},new{name="S1_Hatch",p=new Vector3(-13.2f,-80.6f,-16.2f),t=new Vector3(-14.8f,-80.85f,-14.05f)}};
 try{foreach(var q in shots){var go=new GameObject("S1ReviewCamera");var cam=go.AddComponent<Camera>();cam.transform.position=q.p;cam.transform.LookAt(q.t);cam.fieldOfView=70;cam.nearClipPlane=.03f;cam.farClipPlane=200;cam.clearFlags=CameraClearFlags.SolidColor;cam.backgroundColor=C("#0B1118");cam.GetUniversalAdditionalCameraData().renderPostProcessing=false;var rt=new RenderTexture(1600,1000,24);cam.targetTexture=rt;cam.Render();var prev=RenderTexture.active;RenderTexture.active=rt;var tex=new Texture2D(1600,1000,TextureFormat.RGB24,false);tex.ReadPixels(new Rect(0,0,1600,1000),0,0);tex.Apply();File.WriteAllBytes(O+q.name+".png",tex.EncodeToPNG());RenderTexture.active=prev;cam.targetTexture=null;UnityEngine.Object.DestroyImmediate(tex);UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(go);}}
 finally{for(int i=0;i<rr.Length;i++)rr[i].enabled=was[i];EditorSceneManager.OpenScene(s.path);}return shots.Length;}
}
