// External Editor authoring only. No runtime scripts or gameplay changes.
using System;using System.IO;using System.Linq;using System.Collections.Generic;
using UnityEngine;using UnityEditor;using UnityEngine.SceneManagement;using UnityEditor.SceneManagement;
using UnityEngine.Rendering;using UnityEngine.Rendering.Universal;using Newtonsoft.Json;using Newtonsoft.Json.Linq;
public static class ApplyFullLayout {
 const string A="Assets/Afrer_Seconds/",E=A+"05.Model/Environment/",P=A+"05.Model/Props/";
 static string R=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 static string O=>R+"/Docs/검수/2026-11-06_B5_FullLayout/";
 static JObject data;static JToken floor;static Transform root;static List<object> placed=new List<object>();
 static void Init(){var s=SceneManager.GetActiveScene();if(Application.isPlaying||s.isDirty||!s.path.EndsWith("Level_B5_Circular.unity"))throw new Exception("Saved B5 Edit scene required");data=JObject.Parse(File.ReadAllText(R+"/Docs/도면/Decision/원형공동/facility_layout.json"));floor=data["floors"].Single(f=>(string)f["id"]=="B5");root=s.GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular")).transform;Directory.CreateDirectory(O);}
 static void Write(string name,object value)=>File.WriteAllText(O+name,JsonConvert.SerializeObject(value,Formatting.Indented));
 static GameObject Group(string name,Transform parent){var g=new GameObject(name);g.transform.SetParent(parent,false);return g;}
 static Vector3 V(JToken p,float y=0)=>new Vector3((float)p[0],y,-(float)p[1]);
 static Bounds Bounds(GameObject g){var rs=g.GetComponentsInChildren<Renderer>(true).Where(r=>!r.name.Contains("_LOD")||r.name.EndsWith("_LOD0")).ToArray();var b=rs[0].bounds;foreach(var r in rs.Skip(1))b.Encapsulate(r.bounds);return b;}
 static GameObject Inst(string path,Transform parent,Vector3 local,float yaw=0){var asset=AssetDatabase.LoadAssetAtPath<GameObject>(path);if(!asset)throw new Exception("Missing "+path);var g=(GameObject)PrefabUtility.InstantiatePrefab(asset,parent);g.transform.localPosition=local;g.transform.localRotation=Quaternion.Euler(0,yaw,0);return g;}
 static Material MaterialFor(string original){string n=original.Split('.')[0];string p=n.StartsWith("S1_")?E+"B5/Materials/"+n+".mat":E+"Common/Materials/CF_B5_"+n.Replace("CF_","")+".mat";return AssetDatabase.LoadAssetAtPath<Material>(p);}
 static void Remap(GameObject g){foreach(var rr in g.GetComponentsInChildren<Renderer>(true)){rr.sharedMaterials=rr.sharedMaterials.Select(m=>MaterialFor(m.name)??m).ToArray();}}
 static GameObject Model(string name,Transform parent){var g=Inst(E+"B5/"+name+".fbx",parent,Vector3.zero);g.name=name;Remap(g);foreach(var mf in g.GetComponentsInChildren<MeshFilter>()){var c=mf.gameObject.AddComponent<MeshCollider>();c.sharedMesh=mf.sharedMesh;}return g;}
 static GameObject Fit(string path,string name,Transform parent,Vector3 pos,Vector3 target,float yaw){
  var holder=Group(name,parent);holder.transform.localPosition=pos;var g=Inst(path,holder.transform,Vector3.zero);float best=float.MaxValue;Quaternion selected=Quaternion.identity;
  foreach(var rot in new[]{Quaternion.identity,Quaternion.Euler(-90,0,0),Quaternion.Euler(90,0,0),Quaternion.Euler(0,0,90)}){g.transform.localRotation=rot;var b=Bounds(g);float[] ratio={Mathf.Log(b.size.x/target.x),Mathf.Log(b.size.y/target.y),Mathf.Log(b.size.z/target.z)};float mean=ratio.Average(),err=ratio.Sum(v=>(v-mean)*(v-mean));if(err<best){best=err;selected=rot;}}
  g.transform.localRotation=selected;var bb=Bounds(g);float scale=Mathf.Min(target.x/bb.size.x,target.y/bb.size.y,target.z/bb.size.z);g.transform.localScale*=scale;bb=Bounds(g);g.transform.position+=new Vector3(holder.transform.position.x-bb.center.x,holder.transform.position.y-bb.min.y,holder.transform.position.z-bb.center.z);
  foreach(var c in g.GetComponentsInChildren<Collider>(true))c.enabled=false;foreach(var l in g.GetComponentsInChildren<Light>(true))l.enabled=false;
  bb=Bounds(g);var box=holder.AddComponent<BoxCollider>();box.center=holder.transform.InverseTransformPoint(bb.center);box.size=bb.size;holder.transform.localRotation=Quaternion.Euler(0,yaw,0);
  placed.Add(new{name,path,position=holder.transform.position.ToString(),size=target.ToString()});return holder;
 }
 public static object Import(){Init();var logs=new List<string>();Application.LogCallback cb=(m,s,t)=>{if(t==LogType.Warning||t==LogType.Error||t==LogType.Exception)logs.Add(m);};Application.logMessageReceived+=cb;
  try{foreach(string n in new[]{"AF_B5_FullLayout","AF_B5_PortalCollars","AF_C01_CurvedLining","AF_C01_ThreePortalRibs","AF_C01_MeasurementRig"}){string p=E+"B5/"+n+".fbx";AssetDatabase.ImportAsset(p,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);var mi=(ModelImporter)AssetImporter.GetAtPath(p);mi.isReadable=true;mi.importAnimation=false;mi.importLights=false;mi.importCameras=false;mi.SaveAndReimport();}}finally{Application.logMessageReceived-=cb;}
  Write("import.json",logs);return new{logs};
 }
 static void SmoothDome(MeshFilter mf,JToken room){var m=UnityEngine.Object.Instantiate(mf.sharedMesh);var v=m.vertices;var n=m.normals;var center=root.TransformPoint(new Vector3((float)room["x"],0,-(float)room["v"]));float radius=(float)room["r"];
  for(int i=0;i<v.Length;i++){var d=mf.transform.TransformPoint(v[i])-center;float rad=d.magnitude;var normal=mf.transform.TransformDirection(n[i]);if(d.y>.1f&&Mathf.Abs(Vector3.Dot(normal.normalized,d.normalized))>.65f){if(Mathf.Abs(rad-radius)<.075f)n[i]=mf.transform.InverseTransformDirection(-d.normalized);else if(Mathf.Abs(rad-radius-.22f)<.075f)n[i]=mf.transform.InverseTransformDirection(d.normalized);}}
  m.normals=n;m.RecalculateTangents();m.name="AF_"+(string)room["id"]+"_Smooth";string path=E+"B5/"+m.name+".asset";var old=AssetDatabase.LoadAssetAtPath<Mesh>(path);if(old){EditorUtility.CopySerialized(m,old);UnityEngine.Object.DestroyImmediate(m);m=old;}else AssetDatabase.CreateAsset(m,path);mf.sharedMesh=m;PrefabUtility.RecordPrefabInstancePropertyModifications(mf);
 }
 public static object Apply(){Init();if(root.Find("B5_FullLayout_Implementation"))throw new Exception("Already applied; use targeted repair rather than rebuilding");placed.Clear();Undo.RegisterFullObjectHierarchyUndo(root.gameObject,"Implement full B5 layout");var state=SceneManager.GetActiveScene();
  var main=Group("B5_FullLayout_Implementation",root).transform;var architecture=Model("AF_B5_FullLayout",main);
  foreach(var mf in architecture.GetComponentsInChildren<MeshFilter>()){var room=floor["rooms"].FirstOrDefault(r=>mf.name.StartsWith("CF_B5_"+(string)r["id"]+"_Dome"));if(room!=null)SmoothDome(mf,room);}
  var oldArchitecture=root.Cast<Transform>().Single(t=>t.name=="CF_B5_Core");oldArchitecture.gameObject.SetActive(false);PrefabUtility.RecordPrefabInstancePropertyModifications(oldArchitecture.gameObject);
  Model("AF_B5_PortalCollars",main);
  var doors=root.Find("Pocket_Doors_Open");var template=doors.GetChild(0).gameObject;int addedDoors=0;
  foreach(var t in floor["tunnels"].Where(t=>int.Parse(((string)t["id"]).Substring(4))>7))foreach(string end in new[]{"p","q"}){var go=UnityEngine.Object.Instantiate(template,doors);go.name="Door_"+t["id"]+"_"+end;go.transform.localPosition=V(t[end]);go.transform.localRotation=Quaternion.LookRotation(V(t["q"])-V(t["p"]));addedDoors++;}
  // Preserve prior authored furniture but remove it from the experimental room.
  var c01=root.Find("Sector01_CompletedArt");if(!c01)throw new Exception("C01 art group missing");c01.name="C01_Experiment_Art";
  var retired=Group("Retired_C01_LivingLayout",root).transform;retired.localPosition=c01.localPosition;
  string[] living={"S1_IsolationBed","S1_SanitaryUnit","S1_PrivacyScreen","S1_PersonalLocker","S1_LivingDesk","S1_TabletopKit","S1_Slippers","S1_PersonalBox","S1_HygieneKit","S1_Mirror","S1_CallPanel","S1_HygieneShelf"};
  foreach(var t in c01.Cast<Transform>().ToArray())if(living.Any(n=>t.name.StartsWith(n)))t.SetParent(retired,false);retired.gameObject.SetActive(false);
  foreach(var t in c01.Cast<Transform>().Where(t=>new[]{"S1_VaultRibs","S1_CoveRing","S1_PortalCollars"}.Any(n=>t.name.StartsWith(n))))t.gameObject.SetActive(false);
  Model("AF_C01_CurvedLining",c01);Model("AF_C01_ThreePortalRibs",c01);Model("AF_C01_MeasurementRig",c01);
  var light=c01.Find("Living_Indirect");if(light)light.name="Measurement_Indirect";
  var clinical=Group("C01_Clinical_Stations",c01).transform;
  Fit(P+"B5/B5_IsolationMonitoringConsole_B5_Lite.prefab","Observation_Console_A",clinical,new Vector3(-5.4f,0,5.1f),new Vector3(2.3f,1.6f,1.15f),135);
  Fit(P+"B5/B5_IsolationMonitoringConsole_B5_Lite.prefab","Observation_Console_B",clinical,new Vector3(5.4f,0,-4.9f),new Vector3(2.3f,1.6f,1.15f),315);
  Fit(P+"Common/P04_RecordsCabinet_B5_Lite.prefab","Trial_Records_Cabinet",clinical,new Vector3(-6.3f,0,-4.5f),new Vector3(1.0f,1.8f,.55f),55);
  Fit(P+"Common/P07_SealedWasteBin_B5_Lite.prefab","Clinical_SealedWaste",clinical,new Vector3(4.3f,0,-6.0f),new Vector3(.55f,.9f,.55f),0);
  // Living modules use the planned W01/W02 centres and existing VARCO furniture.
  var wingProps=Group("Outer_Caverns_Props",main).transform;
  foreach(var p in data["placements"].Where(p=>(string)p["floor"]=="B5"&&(string)p["code"]=="P80")){
   var cell=Group((string)p["room"]+"_LivingModule_"+p["id"],wingProps).transform;cell.localPosition=new Vector3((float)p["x"],0,-(float)p["v"]);cell.localRotation=Quaternion.Euler(0,(float)p["yaw"],0);
   Inst(P+"B5/S1_IsolationBed.prefab",cell,new Vector3(-.85f,0,0));Inst(P+"B5/S1_LivingDesk.prefab",cell,new Vector3(.67f,0,-1.0f));Inst(P+"B5/S1_PersonalLocker.prefab",cell,new Vector3(-.85f,0,1.35f),180);Inst(P+"B5/S1_SanitaryUnit.prefab",cell,new Vector3(.8f,0,1.05f),180);
   Inst(P+"B5/S1_TabletopKit.prefab",cell,new Vector3(.67f,.769f,-1f));Inst(E+"B5/S1_PrivacyScreen.prefab",cell,new Vector3(.65f,0,.4f));
  }
  var substitutions=new Dictionary<string,string>{{"P50",P+"B5/S1_VitalMonitor.prefab"},{"P51",P+"B5/S1_IsolationBed.prefab"},{"P118",P+"B5/S1_PersonalLocker.prefab"},{"P128",P+"Common/CFD_LinenHamper.prefab"}};
  var missing=new List<string>();
  foreach(var p in data["placements"].Where(p=>(string)p["floor"]=="B5"&&(string)p["role"]=="독립 배치"&&!new[]{"C01","C02","C03","C04","VA","VB","VL"}.Contains((string)p["room"]))){string code=(string)p["code"];if(code=="P80")continue;string path=substitutions.TryGetValue(code,out var replacement)?replacement:(string)data["catalog"].Single(c=>(string)c["code"]==code)["asset"];if(string.IsNullOrEmpty(path)||!AssetDatabase.LoadAssetAtPath<GameObject>(path)){missing.Add((string)p["id"]+" "+code);continue;}
   Fit(path,(string)p["room"]+"_"+p["id"]+"_"+code,wingProps,new Vector3((float)p["x"],(float)p["base"],-(float)p["v"]),new Vector3((float)p["w"],(float)p["h"],(float)p["d"]),(float)p["yaw"]);
  }
  var lighting=Group("Outer_Caverns_Lighting",main).transform;var fixture=c01.Cast<Transform>().First(t=>t.name.StartsWith("S1_WallTaskLight")).gameObject;
  foreach(var r in floor["rooms"].Where(r=>r["wing"]!=null)){float rad=Mathf.Sqrt((float)r["r"]*(float)r["r"]-3.18f*3.18f)-.13f;int i=0;foreach(float angle in new[]{40f,140f,220f,320f}){float a=angle*Mathf.Deg2Rad;var g=UnityEngine.Object.Instantiate(fixture,lighting);g.name=(string)r["id"]+"_WallLight_"+i;g.transform.localPosition=new Vector3((float)r["x"]+Mathf.Cos(a)*rad,3.18f,-(float)r["v"]+Mathf.Sin(a)*rad);g.transform.localRotation=Quaternion.Euler(0,Mathf.Atan2(-Mathf.Cos(a),-Mathf.Sin(a))*Mathf.Rad2Deg,0);var l=g.GetComponentInChildren<Light>();l.intensity=14;l.range=(float)r["r"]+1;l.shadows=i++==0?LightShadows.Soft:LightShadows.None;}}
  var corridors=Group("Added_Corridor_Fittings",main).transform;
  foreach(var t in floor["tunnels"].Where(t=>int.Parse(((string)t["id"]).Substring(4))>7)){
   var g=Group((string)t["id"],corridors).transform;Vector3 p=V(t["p"]),q=V(t["q"]),direction=(q-p).normalized;float yaw=Mathf.Atan2(direction.x,direction.z)*Mathf.Rad2Deg;int n=Mathf.Max(1,Mathf.CeilToInt((float)t["length"]/6));
   for(int i=0;i<n;i++){var pos=Vector3.Lerp(p,q,(i+.5f)/n);Inst(E+"Common/CFD_TunnelRib.prefab",g,pos,yaw);var lamp=Inst(E+"Common/CFD_SealedLight.prefab",g,pos+Vector3.up*3.19f,yaw);foreach(var rr in lamp.GetComponentsInChildren<Renderer>())rr.shadowCastingMode=ShadowCastingMode.Off;var lg=Group("TaskLight",lamp.transform);lg.transform.localPosition=new Vector3(0,-.18f,0);var l=lg.AddComponent<Light>();l.type=LightType.Point;l.color=new Color(.79f,.87f,.95f);l.intensity=3.2f;l.range=6.2f;l.shadows=LightShadows.None;}
  }
  Physics.SyncTransforms();AssetDatabase.SaveAssets();EditorSceneManager.MarkSceneDirty(state);EditorSceneManager.SaveScene(state);
  Write("implementation.json",new{scene=state.path,caverns=12,cores=3,tunnels=19,addedDoors,totalDoors=doors.childCount,livingModules=8,missingOuterPropAssets=missing,placed,runtimeCodeAdded=false});
  var sv=SceneView.lastActiveSceneView;if(sv){sv.LookAt(new Vector3(0,-80,0),Quaternion.Euler(65,0,0),150,false,true);sv.sceneLighting=true;sv.Repaint();}return new{scene=state.path,caverns=12,cores=3,tunnels=19,totalDoors=doors.childCount,livingModules=8,missingProps=missing.Count};
 }
}
