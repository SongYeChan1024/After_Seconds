// Editor-only production tool outside Assets. No gameplay implementation.
using System;using System.IO;using System.Linq;using System.Collections.Generic;
using UnityEngine;using UnityEditor;using UnityEngine.SceneManagement;using UnityEditor.SceneManagement;
using UnityEngine.Rendering;using UnityEngine.Rendering.Universal;using Newtonsoft.Json;using Newtonsoft.Json.Linq;
public static class BuildCircular {
 const string A="Assets/Afrer_Seconds/";const string E=A+"05.Model/Environment/";
 static string Repo=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 static string Source=>Repo+"/SourceAssets/CircularFacility/";
 static string Report=>Repo+"/Docs/검수/2026-11-06_CircularFacility/";
 static JObject data;static Dictionary<string,Material> mats=new Dictionary<string,Material>();static List<object> placed=new List<object>();
 static void Init(){data=JObject.Parse(File.ReadAllText(Repo+"/Docs/도면/원형공동/facility_layout.json"));Directory.CreateDirectory(Report);}
 static void Write(string file,object obj){Directory.CreateDirectory(Path.GetDirectoryName(Report+file));File.WriteAllText(Report+file,JsonConvert.SerializeObject(obj,Formatting.Indented));}
 static Vector3 P(float x,float h,float v)=>new Vector3(x,h,-v);
 static float N(JToken t,string k)=>(float)t[k];
 static GameObject Group(string name,Transform parent=null){var g=new GameObject(name);if(parent)g.transform.SetParent(parent,false);return g;}
 static Color Col(string hex){Color c;ColorUtility.TryParseHtmlString(hex,out c);return c;}
 static Material Mat(string floor,string kind,string hex,float metal,float smooth){
  string path=E+"Common/Materials/CF_"+floor+"_"+kind+".mat";Directory.CreateDirectory(Path.GetDirectoryName(Path.Combine(Path.GetDirectoryName(Application.dataPath),path)));
  var m=AssetDatabase.LoadAssetAtPath<Material>(path);if(!m){m=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(m,path);}
  m.SetColor("_BaseColor",Col(hex));m.SetFloat("_Metallic",metal);m.SetFloat("_Smoothness",smooth);m.SetFloat("_Cull",0);
  string family=kind=="Floor"?"Concrete":kind=="Steel"?"Stainless":"Coating";
  if(kind!="Lamp"&&kind!="Guide"){
   m.SetTexture("_BaseMap",AssetDatabase.LoadAssetAtPath<Texture>(E+"Common/Textures/LP_"+family+"_Base.png"));
   m.SetTexture("_BumpMap",AssetDatabase.LoadAssetAtPath<Texture>(E+"Common/Textures/LP_"+family+"_Normal.png"));m.EnableKeyword("_NORMALMAP");m.SetFloat("_BumpScale",.12f);
  }
  if(kind=="Lamp"){m.EnableKeyword("_EMISSION");m.SetColor("_EmissionColor",Col(hex)*.5f);}
  EditorUtility.SetDirty(m);AssetDatabase.SaveAssetIfDirty(m);return m;
 }
 static void Materials(string fid){var st=data["floor_art_direction"][fid];mats.Clear();
  mats["Shell"]=Mat(fid,"Shell",(string)st["wall"],.05f,.30f);mats["Floor"]=Mat(fid,"Floor",(string)st["floor"],.1f,.24f);
  mats["Steel"]=Mat(fid,"Steel",(string)st["metal"],.84f,.40f);mats["Inset"]=Mat(fid,"Inset","#1B252E",.1f,.24f);
  mats["Glass"]=Mat(fid,"Glass","#384D5D",.3f,.6f);mats["Lamp"]=Mat(fid,"Lamp",(string)st["light"],0,.2f);mats["Guide"]=Mat(fid,"Guide","#CFDAE2",0,.23f);
 }
 static void Remap(GameObject g){foreach(var r in g.GetComponentsInChildren<Renderer>(true)){
  r.sharedMaterials=r.sharedMaterials.Select(m=>{if(!m)return mats["Shell"];string k=m.name.Replace("CF_","").Split('.')[0];return mats.ContainsKey(k)?mats[k]:m;}).ToArray();
 }}
 static GameObject Model(string path,Transform parent,bool collide=true){
  var a=AssetDatabase.LoadAssetAtPath<GameObject>(path);if(!a)throw new Exception("Missing model "+path);
  var g=(GameObject)PrefabUtility.InstantiatePrefab(a,parent);g.transform.localPosition=Vector3.zero;g.transform.localRotation=Quaternion.identity;Remap(g);
  if(collide)foreach(var m in g.GetComponentsInChildren<MeshFilter>()){var c=m.gameObject.AddComponent<MeshCollider>();c.sharedMesh=m.sharedMesh;}
  return g;
 }
 static Bounds Bounds(GameObject g){var rr=g.GetComponentsInChildren<Renderer>().Where(r=>!(r is ParticleSystemRenderer)).ToArray();if(rr.Length==0)return new Bounds(g.transform.position,Vector3.zero);var b=rr[0].bounds;foreach(var r in rr.Skip(1))b.Encapsulate(r.bounds);return b;}
 static void Lamp(Transform parent,string name,Vector3 pos,Color color,float power,float range,bool shadow=false){
  var g=Group(name,parent);g.transform.localPosition=pos;var l=g.AddComponent<Light>();l.type=LightType.Point;l.color=color;l.intensity=power;l.range=range;l.shadows=shadow?LightShadows.Soft:LightShadows.None;l.shadowBias=.025f;l.shadowNormalBias=.12f;
 }
 static void Tone(string fid){var s=data["floor_art_direction"][fid];RenderSettings.skybox=null;RenderSettings.ambientMode=AmbientMode.Trilight;float a=N(s,"ambient");RenderSettings.ambientSkyColor=new Color(a,a*1.04f,a*1.1f);RenderSettings.ambientEquatorColor=new Color(a*.65f,a*.7f,a*.8f);RenderSettings.ambientGroundColor=new Color(a*.35f,a*.38f,a*.45f);RenderSettings.fog=false;RenderSettings.defaultReflectionMode=DefaultReflectionMode.Custom;RenderSettings.customReflectionTexture=null;
 }
 static void NewCopy(string src,string dest){
  var current=SceneManager.GetActiveScene();if(current.isDirty||EditorApplication.isPlaying)throw new Exception("Saved edit scene required");
  if(current.path!=src)current=EditorSceneManager.OpenScene(src);
  EditorSceneManager.SaveScene(current,dest,true);var s=EditorSceneManager.OpenScene(dest);
  foreach(var g in s.GetRootGameObjects())if(g.name!="Player_Dummy_V0.1"&&g.name!="Camera")UnityEngine.Object.DestroyImmediate(g);
 }
 static void Player(float y,Vector3 local){var p=SceneManager.GetActiveScene().GetRootGameObjects().Single(g=>g.name=="Player_Dummy_V0.1");var cc=p.GetComponent<CharacterController>();p.transform.position=local+Vector3.up*(y+(cc?cc.height*.5f-cc.center.y:.9f)+.04f);p.transform.rotation=Quaternion.Euler(0,0,0);
  foreach(var c in SceneManager.GetActiveScene().GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Camera>(true))){c.clearFlags=CameraClearFlags.SolidColor;c.backgroundColor=new Color(.025f,.035f,.045f);c.farClipPlane=350;}
 }
 static void Door(JToken t,JToken point,Transform parent){
  float dx=(float)t["q"][0]-(float)t["p"][0],dv=(float)t["q"][1]-(float)t["p"][1];
  var root=Group("Door_"+t["id"]+"_"+parent.childCount,parent);root.transform.localPosition=P((float)point[0],0,(float)point[1]);root.transform.localRotation=Quaternion.LookRotation(new Vector3(dx,0,-dv));
  var g=Model(E+"Common/CF_PocketDoor_240.fbx",root.transform,false);PrefabUtility.UnpackPrefabInstance(g,PrefabUnpackMode.Completely,InteractionMode.AutomatedAction);
  foreach(var mf in g.GetComponentsInChildren<MeshFilter>()){
   bool leaf=mf.name.StartsWith("Leaf_");bool seal=mf.name.StartsWith("Seal_");
   if(leaf||seal){float side=Mathf.Sign(root.transform.InverseTransformPoint(mf.GetComponent<Renderer>().bounds.center).x);if(side==0)side=mf.name.Contains("-1")?-1:1;mf.transform.position+=root.transform.right*side*1.22f;}
   var c=mf.gameObject.AddComponent<MeshCollider>();c.sharedMesh=mf.sharedMesh;
  }
  // Door leaves are parked inside enclosed pockets. No animation or interaction code.
  foreach(float side in new[]{-1f,1f}){var marker=Group(side<0?"Left_ClosedPosition":"Right_ClosedPosition",root.transform);marker.transform.localPosition=new Vector3(side*.602f,0,0);}
  var kp=AssetDatabase.LoadAssetAtPath<GameObject>(A+"05.Model/Props/Common/LP_Keypad.prefab");
  if(kp)foreach(float face in new[]{-1f,1f}){var k=(GameObject)PrefabUtility.InstantiatePrefab(kp,root.transform);k.name="Keypad_"+face;k.transform.localPosition=new Vector3(1.38f,1.25f,face*.27f);k.transform.localRotation=Quaternion.Euler(0,face<0?180:0,0);}
 }
 static void Prop(JToken p,Transform parent){
  string code=(string)p["code"];var cat=data["catalog"].Single(c=>(string)c["code"]==code);string path=(string)cat["asset"];if(string.IsNullOrEmpty(path))return;
  var a=AssetDatabase.LoadAssetAtPath<GameObject>(path);if(!a)return;
  var holder=Group((string)p["id"]+"_"+code,parent);holder.transform.localPosition=P(N(p,"x"),N(p,"base"),N(p,"v"));holder.transform.localRotation=Quaternion.Euler(0,N(p,"yaw"),0);
  var g=(GameObject)PrefabUtility.InstantiatePrefab(a,holder.transform);g.transform.localPosition=Vector3.zero;
  float yaw=N(p,"yaw");holder.transform.localRotation=Quaternion.identity;
  if(code=="P19")g.transform.localRotation=Quaternion.Euler(-90,0,0);
  else if(code!="P01"){
   float best=float.MaxValue;Quaternion chosen=Quaternion.identity;
   foreach(var rot in new[]{Quaternion.identity,Quaternion.Euler(-90,0,0),Quaternion.Euler(90,0,0),Quaternion.Euler(0,0,90)}){
    g.transform.localRotation=rot;var sz=Bounds(g).size;var ratio=new[]{Mathf.Log(Mathf.Max(.001f,sz.x)/N(p,"w")),Mathf.Log(Mathf.Max(.001f,sz.y)/N(p,"h")),Mathf.Log(Mathf.Max(.001f,sz.z)/N(p,"d"))};float avg=ratio.Average();float e=ratio.Sum(v=>(v-avg)*(v-avg));if(e<best){best=e;chosen=rot;}
   }g.transform.localRotation=chosen;
  }else g.transform.localRotation=Quaternion.identity;
  if(code=="P01")g.transform.localScale=new Vector3(3,2,3);
  else {var b0=Bounds(g);float scale=Mathf.Min(N(p,"w")/Mathf.Max(.01f,b0.size.x),N(p,"h")/Mathf.Max(.01f,b0.size.y),N(p,"d")/Mathf.Max(.01f,b0.size.z));g.transform.localScale*=Mathf.Clamp(scale,.05f,15f);}
  var b=Bounds(g);g.transform.position+=new Vector3(holder.transform.position.x-b.center.x,holder.transform.position.y-b.min.y,holder.transform.position.z-b.center.z);holder.transform.localRotation=Quaternion.Euler(0,yaw,0);
  // Existing generated emissions cannot overwhelm this floor's lighting.
  foreach(var l in g.GetComponentsInChildren<Light>(true))l.enabled=false;
  if(code!="P01"){
   foreach(var col in g.GetComponentsInChildren<Collider>(true))col.enabled=false;
   b=Bounds(g);var co=holder.AddComponent<BoxCollider>();co.center=holder.transform.InverseTransformPoint(b.center);co.size=new Vector3(N(p,"w"),b.size.y,N(p,"d"));
  }
  placed.Add(new{id=(string)p["id"],code,asset=path,position=holder.transform.position.ToString(),bounds=Bounds(g).ToString()});
 }
 static void Guides(JToken f,Transform root){
  var grp=Group("Facility_Floor_Guidance_R1",root);var pts=f["route"].ToArray();
  for(int i=1;i<pts.Length;i++){
   Vector3 a=P((float)pts[i-1][0],.012f,(float)pts[i-1][1]),b=P((float)pts[i][0],.012f,(float)pts[i][1]);if(Vector3.Distance(a,b)<.05f)continue;
   var dir=(b-a).normalized;var side=Vector3.Cross(Vector3.up,dir);
   foreach(float offset in new[]{-.12f,.12f}){
    Vector3 l=a+side*offset,r=b+side*offset;var mesh=new Mesh();mesh.name="R1_Strip";mesh.vertices=new[]{l-side*.025f,l+side*.025f,r+side*.025f,r-side*.025f};mesh.triangles=new[]{0,2,1,0,3,2};mesh.RecalculateNormals();
    string path=E+"B5/CF_R1_"+i+"_"+(offset<0?"L":"R")+".asset";var existing=AssetDatabase.LoadAssetAtPath<Mesh>(path);if(existing){EditorUtility.CopySerialized(mesh,existing);UnityEngine.Object.DestroyImmediate(mesh);mesh=existing;}else AssetDatabase.CreateAsset(mesh,path);
    var g=Group("R1_"+i,grp.transform);g.AddComponent<MeshFilter>().sharedMesh=mesh;g.AddComponent<MeshRenderer>().sharedMaterial=mats["Guide"];
   }
  }
 }
 public static object Import(){Init();var logs=new List<string>();Application.LogCallback cb=(m,s,t)=>{if(t==LogType.Warning||t==LogType.Error||t==LogType.Exception)logs.Add(m);};Application.logMessageReceived+=cb;
  try{AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);foreach(string path in new[]{E+"B5/CF_B5_Core.fbx",E+"Common/CF_PocketDoor_240.fbx",E+"B2/CF_B2_C02_Preview.fbx",E+"B2/CF_B2_Mezzanine.fbx"}){
   var imp=AssetImporter.GetAtPath(path) as ModelImporter;if(!imp)throw new Exception(path);imp.importAnimation=false;imp.importCameras=false;imp.importLights=false;imp.materialImportMode=ModelImporterMaterialImportMode.ImportStandard;imp.SaveAndReimport();
  }}finally{Application.logMessageReceived-=cb;}Write("import.json",logs);return new{logs};
 }
 public static object BuildB5(){Init();placed.Clear();NewCopy(A+"01.Scenes/Stage/Old/Level_B5_Stealth.unity",A+"01.Scenes/Stage/Level_B5_Circular.unity");Materials("B5");Tone("B5");var f=data["floors"].Single(x=>(string)x["id"]=="B5");float y=N(f,"z");var root=Group("B5_Circular_Core_V0.03");root.transform.position=new Vector3(0,y,0);Model(E+"B5/CF_B5_Core.fbx",root.transform);
  var ids=new HashSet<string>(f["rooms"].Where(r=>r["wing"]==null).Select(r=>(string)r["id"]));var dp=Group("Pocket_Doors_Open",root.transform);
  foreach(var t in f["tunnels"].Where(t=>ids.Contains((string)t["a"])&&ids.Contains((string)t["b"]))){Door(t,t["p"],dp.transform);Door(t,t["q"],dp.transform);}
  var pp=Group("Existing_Props_FirstPass",root.transform);
  foreach(var p in data["placements"].Where(p=>(string)p["floor"]=="B5"&&ids.Contains((string)p["room"])&&(string)p["role"]=="독립 배치"))Prop(p,pp.transform);
  var lights=Group("Lighting",root.transform);Color lc=Col((string)data["floor_art_direction"]["B5"]["light"]);
  foreach(var r in f["rooms"].Where(r=>ids.Contains((string)r["id"])))for(int i=0;i<4;i++){float a=i*Mathf.PI/2;float radius=N(r,"r")*.52f;Lamp(lights.transform,(string)r["id"]+"_Work_"+i,P(N(r,"x")+Mathf.Cos(a)*radius,3.2f,N(r,"v")+Mathf.Sin(a)*radius),lc,2.2f,8.5f,i==0);}
  foreach(var t in f["tunnels"].Where(t=>ids.Contains((string)t["a"])&&ids.Contains((string)t["b"])))for(int i=0;i<Mathf.CeilToInt(N(t,"length")/7f);i++){int count=Mathf.CeilToInt(N(t,"length")/7f);float a=(i+.5f)/count;Lamp(lights.transform,(string)t["id"]+"_"+i,P(Mathf.Lerp((float)t["p"][0],(float)t["q"][0],a),2.85f,Mathf.Lerp((float)t["p"][1],(float)t["q"][1],a)),lc,1.2f,5f);}
  Guides(f,root.transform);Player(y,P(-9.2f,0,10));Physics.SyncTransforms();EditorSceneManager.MarkSceneDirty(SceneManager.GetActiveScene());EditorSceneManager.SaveScene(SceneManager.GetActiveScene());Write("B5_placement.json",placed);return new{scene=SceneManager.GetActiveScene().path,props=placed.Count,doors=dp.transform.childCount,lights=lights.GetComponentsInChildren<Light>().Length};
 }
 public static object BuildB2Preview(){Init();placed.Clear();NewCopy(A+"01.Scenes/Stage/Level_B5_Circular.unity",A+"01.Scenes/Stage/Level_B2_MezzaninePreview.unity");Materials("B2");Tone("B2");var root=Group("B2_C02_Mezzanine_Study_V0.03");root.transform.position=new Vector3(0,-34,0);Model(E+"B2/CF_B2_C02_Preview.fbx",root.transform);Model(E+"B2/CF_B2_Mezzanine.fbx",root.transform);
  var pp=Group("Cooling_Equipment",root.transform);int index=0;
  foreach(var r in data["mezzanines"][0]["lower_props"]){var cat=data["catalog"].Single(c=>(string)c["code"]==(string)r["code"]);var p=new JObject{{"id","B2_Preview_"+(index++)},{"code",r["code"]},{"x",r["x"]},{"v",r["v"]},{"base",0},{"yaw",0},{"w",cat["w"]},{"d",cat["d"]},{"h",cat["h"]}};Prop(p,pp.transform);}
  var lights=Group("Red_Accent_And_Neutral_Worklights",root.transform);
  Lamp(lights.transform,"Red_West",P(11.5f,2,-1),new Color(1,.1f,.06f),2.4f,8);
  Lamp(lights.transform,"Red_East",P(26.5f,2,-1),new Color(1,.1f,.06f),2.4f,8);
  foreach(float x in new[]{12.8f,25.2f}){Lamp(lights.transform,"Stair_Worklight",P(x,3.2f,6),new Color(.84f,.9f,1),2,6,true);Lamp(lights.transform,"Deck_Worklight",P(x,6,-2),new Color(.84f,.9f,1),2,6,true);}
  Lamp(lights.transform,"Central_Maintenance",P(19,5,2),new Color(.8f,.85f,.9f),2.4f,9,true);
  Player(-34,P(19,0,8));Physics.SyncTransforms();EditorSceneManager.SaveScene(SceneManager.GetActiveScene());Write("B2_placement.json",placed);return new{scene=SceneManager.GetActiveScene().path,props=placed.Count};
 }
 public static object Capture(){Init();var current=SceneManager.GetActiveScene().path;var shots=new[]{new{scene="Level_B5_Circular",name="B5_Entry",p=new Vector3(-9.2f,-80.35f,-10),t=new Vector3(-15,-80,-10)},new{scene="Level_B5_Circular",name="B5_Tunnel",p=new Vector3(-16,-80.35f,-4),t=new Vector3(-22,-80.35f,18)},new{scene="Level_B5_Circular",name="B5_Cooling",p=new Vector3(17,-80.35f,0),t=new Vector3(17,-80.2f,-10)},new{scene="Level_B2_MezzaninePreview",name="B2_Lower",p=new Vector3(19,-32.35f,-8),t=new Vector3(19,-30.3f,3)},new{scene="Level_B2_MezzaninePreview",name="B2_Upper",p=new Vector3(12.8f,-28.75f,2),t=new Vector3(21,-32.5f,-2)}};
  foreach(var s in shots){EditorSceneManager.OpenScene(A+"01.Scenes/Stage/"+s.scene+".unity");foreach(var actor in SceneManager.GetActiveScene().GetRootGameObjects().Where(o=>o.name.StartsWith("Player")))foreach(var rr in actor.GetComponentsInChildren<Renderer>())rr.enabled=false;var g=new GameObject("ReviewCamera");var cam=g.AddComponent<Camera>();cam.transform.position=s.p;cam.transform.LookAt(s.t);cam.fieldOfView=72;cam.nearClipPlane=.05f;cam.farClipPlane=300;cam.clearFlags=CameraClearFlags.SolidColor;cam.backgroundColor=new Color(.02f,.03f,.04f);cam.allowHDR=true;cam.GetUniversalAdditionalCameraData().renderPostProcessing=false;
   var rt=new RenderTexture(1440,900,24,RenderTextureFormat.ARGB32);cam.targetTexture=rt;cam.Render();var old=RenderTexture.active;RenderTexture.active=rt;var tex=new Texture2D(1440,900,TextureFormat.RGB24,false);tex.ReadPixels(new Rect(0,0,1440,900),0,0);tex.Apply();File.WriteAllBytes(Report+s.name+".png",tex.EncodeToPNG());RenderTexture.active=old;cam.targetTexture=null;UnityEngine.Object.DestroyImmediate(tex);UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(g);
  }EditorSceneManager.OpenScene(current);return new{shots=shots.Length};
 }
 public static object AddPipework(){Init();AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);EditorSceneManager.OpenScene(A+"01.Scenes/Stage/Level_B2_MezzaninePreview.unity");Materials("B2");var r=SceneManager.GetActiveScene().GetRootGameObjects().Single(g=>g.name.StartsWith("B2_"));var old=r.transform.Find("Process_Pipework");if(old)UnityEngine.Object.DestroyImmediate(old.gameObject);var p=Model(E+"B2/CF_B2_ProcessPipework.fbx",r.transform);p.name="Process_Pipework";EditorSceneManager.SaveScene(SceneManager.GetActiveScene());EditorSceneManager.OpenScene(A+"01.Scenes/Stage/Level_B5_Circular.unity");
  int removed=0;foreach(string guid in AssetDatabase.FindAssets("CF_R1_ t:Mesh",new[]{E+"B5"})){string path=AssetDatabase.GUIDToAssetPath(guid);if(Path.GetFileName(path).StartsWith("CF_R1_")&&!path.Contains("Continuous")&&path.EndsWith(".asset")){AssetDatabase.DeleteAsset(path);removed++;}}
  return new{pipework=true,obsoleteGeneratedStripsRemoved=removed};
 }
 public static object DoorValidation(){Init();EditorSceneManager.OpenScene(A+"01.Scenes/Stage/Level_B5_Circular.unity");var root=SceneManager.GetActiveScene().GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular"));var doors=root.transform.Find("Pocket_Doors_Open");var checks=new List<object>();Physics.SyncTransforms();
  foreach(Transform door in doors){Vector3 p=door.position;Func<Collider[]> hits=()=>Physics.OverlapCapsule(p+Vector3.up*.34f,p+Vector3.up*1.48f,.28f,~0,QueryTriggerInteraction.Ignore).Where(c=>c.transform.IsChildOf(door)&&!c.name.Contains("Threshold")).ToArray();bool openClear=hits().Length==0;var moved=new Dictionary<Transform,Vector3>();
   foreach(var mf in door.GetComponentsInChildren<MeshFilter>())if(mf.name.StartsWith("Leaf_")||mf.name.StartsWith("Seal_")){var t=mf.transform;moved[t]=t.position;float side=Mathf.Sign(door.InverseTransformPoint(mf.GetComponent<Renderer>().bounds.center).x);t.position-=door.right*side*1.22f;}
   Physics.SyncTransforms();bool closedBlocks=hits().Length>0;foreach(var m in moved)m.Key.position=m.Value;Physics.SyncTransforms();checks.Add(new{name=door.name,openClear,closedBlocks});
  }File.WriteAllText(Report+"door_validation.json",JsonConvert.SerializeObject(checks,Formatting.Indented));EditorSceneManager.OpenScene(A+"01.Scenes/Stage/Level_B5_Circular.unity");return checks;
 }
 public static object Validate(){Init();var start=SceneManager.GetActiveScene().path;var results=new List<object>();
  foreach(string fid in new[]{"B5","B2"}){
   string scene=fid=="B5"?"Level_B5_Circular":"Level_B2_MezzaninePreview";EditorSceneManager.OpenScene(A+"01.Scenes/Stage/"+scene+".unity");Physics.SyncTransforms();var root=SceneManager.GetActiveScene().GetRootGameObjects().Single(g=>g.name.StartsWith(fid+"_"));
   var paths=fid=="B5"?new[]{data["floors"].Single(f=>(string)f["id"]==fid)["route"],data["floors"].Single(f=>(string)f["id"]==fid)["alternate"]}:new[]{data["mezzanines"][0]["route3d"]};var blocked=new List<object>();int samples=0;float floorY=fid=="B5"?-82:-34;
   foreach(var path in paths){var p=path.ToArray();for(int i=1;i<p.Length;i++){
    Func<JToken,Vector3> pos=x=>fid=="B5"?P((float)x[0],floorY,(float)x[1]):P((float)x[0],floorY+(float)x[1],(float)x[2]);Vector3 a=pos(p[i-1]),b=pos(p[i]);if(fid=="B2"&&Mathf.Abs(a.y-b.y)>.1f)continue;int n=Mathf.Max(1,Mathf.CeilToInt(Vector3.Distance(a,b)/.25f));
    for(int k=0;k<=n;k++){Vector3 q=Vector3.Lerp(a,b,(float)k/n);samples++;var hits=Physics.OverlapCapsule(q+Vector3.up*.34f,q+Vector3.up*1.48f,.27f,~0,QueryTriggerInteraction.Ignore).Where(c=>c.transform.IsChildOf(root.transform)&&!c.name.Contains("Floor")&&!c.name.Contains("Threshold")).ToArray();if(hits.Length>0)blocked.Add(new{position=q.ToString(),hits=hits.Select(h=>h.name).Distinct().ToArray()});}
   }}
   results.Add(new{floor=fid,scene,samples,blocked,meshCount=root.GetComponentsInChildren<MeshFilter>().Length,triangles=root.GetComponentsInChildren<MeshFilter>().Sum(m=>m.sharedMesh.triangles.Length/3),bounds=Bounds(root).ToString(),missingMeshes=root.GetComponentsInChildren<MeshFilter>().Count(m=>!m.sharedMesh)});
  }EditorSceneManager.OpenScene(start);Write("validation.json",results);return results.Select(r=>r).ToArray();
 }
}
