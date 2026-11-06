// External Editor authoring only. No runtime C#, AI, Animator or UI changes.
using System;using System.IO;using System.Linq;using System.Collections.Generic;
using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.SceneManagement;using Newtonsoft.Json;using Newtonsoft.Json.Linq;
public static class ApplyWide {
 const string Root="Assets/Afrer_Seconds/",Env=Root+"05.Model/Environment/";
 static string Repo=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 static string Src=>Repo+"/SourceAssets/B345_WideInterior/";static string Out=>Repo+"/Docs/검수/2026-11-06_B345_WideInterior/";
 static float Linear(float x,float[] a,float[] b){for(int i=1;i<a.Length;i++)if(x<=a[i])return b[i-1]+(x-a[i-1])*(b[i]-b[i-1])/(a[i]-a[i-1]);return x+b[b.Length-1]-a[a.Length-1];}
 static float WideX(float u){float d=0;foreach(float a in new[]{0f,19f,36f}){if(u<a)return u+d;if(u<=a+3)return Linear(u,new[]{a,a+.75f,a+2.25f,a+3},new[]{a+d,a+d+1.35f,a+d+2.85f,a+d+4.2f});d+=1.2f;}return u+d;}
 static float WideY(float v,bool core=false)=>core?v+.8f:Linear(v,new[]{0f,.75f,3.25f,4,24,24.75f,26.25f,27},new[]{0f,1.15f,3.65f,4.8f,24.8f,26.15f,27.65f,29});
 static Vector3 Map(Vector3 p)=>MapCore(p,p.x+24>=38.99f);
 static Vector3 MapCore(Vector3 p,bool core)=>new Vector3(WideX(p.x+24)-24,p.y,WideY(p.z+16,core)-16);
 static Vector3 V(JToken p)=>new Vector3((float)p[0],(float)p[1],(float)p[2]);
 static string Scene(string f)=>Root+"01.Scenes/Stage/Level_"+f+"_Stealth.unity";
 static void Ready(){if(EditorApplication.isPlaying||SceneManager.GetActiveScene().isDirty)throw new Exception("Saved edit scene required");}
 static string P(Transform t)=>t.parent?P(t.parent)+"/"+t.name:t.name;
 static void Record(UnityEngine.Object o){EditorUtility.SetDirty(o);PrefabUtility.RecordPrefabInstancePropertyModifications(o);}
 static Dictionary<string,Mesh> Meshes(string f,string kind)=>AssetDatabase.LoadAllAssetsAtPath(Env+f+"/WC_"+f+"_"+kind+".fbx").OfType<Mesh>().ToDictionary(m=>m.name);
 static int Swap(Transform group,Dictionary<string,Mesh> mm){int count=0;foreach(var mf in group.GetComponentsInChildren<MeshFilter>(true)){string name=mf.sharedMesh?mf.sharedMesh.name:mf.name;if(!mm.TryGetValue(name,out var mesh)){if(name.StartsWith("LC_")||name.StartsWith("WS_")){mf.sharedMesh=null;mf.GetComponent<Renderer>().enabled=false;Record(mf);Record(mf.GetComponent<Renderer>());continue;}throw new Exception("Missing replacement mesh "+name);}mf.sharedMesh=mesh;Record(mf);count++;}return count;}
 static void Move(Transform t){t.position=Map(t.position);Record(t);}
 static void ColliderGroup(Transform group){foreach(Transform t in group){var c=t.GetComponent<BoxCollider>();if(!c){Move(t);continue;}var center=c.bounds.center;bool core=center.x+24>=38.99f;var oldPos=t.position;var lo=MapCore(c.bounds.min,core);var hi=MapCore(c.bounds.max,core);t.position=MapCore(oldPos,core);c.center=t.InverseTransformPoint((lo+hi)*.5f);var size=hi-lo;var local=t.InverseTransformVector(size);c.size=new Vector3(Mathf.Abs(local.x),Mathf.Abs(local.y),Mathf.Abs(local.z));Record(t);Record(c);}}
 static bool Corridor(Vector3 p,JToken rooms)=>rooms.Any(r=>(string)r["kind"]=="corridor"&&p.x+24>=(float)r["x"]-.01f&&p.x+24<=(float)r["x"]+(float)r["w"]+.01f&&p.z+16>=(float)r["y"]-.01f&&p.z+16<=(float)r["y"]+(float)r["h"]+.01f);
 static object Arches(Transform root,string f){var prev=root.Find("Arched_Interior");if(prev)UnityEngine.Object.DestroyImmediate(prev.gameObject);var g=new GameObject("Arched_Interior");g.transform.SetParent(root,false);
  var visual=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Env+f+"/WA_"+f+"_Interior.fbx"),g.transform);visual.name="Rounded_Shell";
  foreach(var r in visual.GetComponentsInChildren<Renderer>()){r.sharedMaterials=r.sharedMaterials.Select(m=>AssetDatabase.LoadAssetAtPath<Material>(Env+"Common/Materials/"+m.name+".mat")).ToArray();if(r.sharedMaterials.Any(m=>!m))throw new Exception("Arch material missing");Record(r);if(r.sharedMaterials.Any(m=>m.name=="AR_Shell")){var mc=r.gameObject.AddComponent<MeshCollider>();mc.sharedMesh=r.GetComponent<MeshFilter>().sharedMesh;}}
  var data=JObject.Parse(File.ReadAllText(Src+f+"_arches.json"));foreach(var row in data["colliders"]){var o=new GameObject((string)row["name"]);o.transform.SetParent(g.transform,false);o.transform.position=V(row["center"]);o.AddComponent<BoxCollider>().size=V(row["size"]);}
  foreach(var row in data["lights"]){var o=new GameObject((string)row["name"]);o.transform.SetParent(g.transform,false);o.transform.position=V(row["position"]);o.transform.rotation=Quaternion.Euler(90,0,0);var l=o.AddComponent<Light>();l.type=LightType.Spot;l.intensity=(float)row["intensity"];l.range=(float)row["range"];l.spotAngle=(float)row["angle"];l.innerSpotAngle=80;l.color=new Color(.96f,.98f,1f);l.shadows=LightShadows.None;}
  return new{arches=(int)data["arches"],lights=data["lights"].Count(),colliders=data["colliders"].Count()};
 }
 public static object Apply(){Ready();Directory.CreateDirectory(Out);string original=SceneManager.GetActiveScene().path;var results=new List<object>();var logs=new List<string>();Application.LogCallback cb=(m,s,t)=>{if(t==LogType.Warning||t==LogType.Error||t==LogType.Exception)logs.Add(m);};Application.logMessageReceived+=cb;
  try{AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);var plan=JObject.Parse(File.ReadAllText(Src+"layout_before.json"));
   foreach(string f in new[]{"B5","B4","B3"}){var path=Scene(f);var s=EditorSceneManager.OpenScene(path);var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith(f+"_Stealth_Level")).transform;if(root.Find("Wide_Corridor_V0.01"))throw new Exception("Already widened "+f);
    var architecture=Meshes(f,"Architecture");var walls=Meshes(f,"Walls");var details=f=="B4"?Meshes(f,"Details"):null;
    foreach(var mf in root.Find("Architecture_Sections").GetComponentsInChildren<MeshFilter>(true))if(!architecture.ContainsKey(mf.sharedMesh.name))throw new Exception("Architecture missing "+mf.sharedMesh.name);
    string backup=Path.GetFullPath(Repo+"/../Management/AfterSeconds_Wide_20261106/");Directory.CreateDirectory(backup);if(!File.Exists(backup+f+".unity"))File.Copy(Path.GetFullPath(path),backup+f+".unity");
    var rooms=plan["floors"].Single(x=>(string)x["floor"]==f)["rooms"];var disabled=new List<string>();
    foreach(Transform group in root.Cast<Transform>().ToArray()){
     if(new[]{"Architecture_Sections","Wall_Surface_Wear","Arched_Interior","Lab_Tone","B4_ServiceDetails"}.Contains(group.name))continue;
     if(group.name=="Retained_Pod_and_Habitat"){Move(group);continue;}
     if(new[]{"Architecture_Collision","StaticCollision","SectionsCollision"}.Contains(group.name)){ColliderGroup(group);continue;}
     foreach(Transform t in group){var l=t.GetComponent<Light>();if(l&&l.enabled&&(group.name=="Fixture_Lighting"||group.name=="Lighting")&&Corridor(t.position,rooms)){l.enabled=false;disabled.Add(P(t));Record(l);}
      var probe=t.GetComponent<ReflectionProbe>();if(probe){var old=t.position+probe.center;bool core=old.x+24>=38.99f;var lo=MapCore(old-probe.size*.5f,core);var hi=MapCore(old+probe.size*.5f,core);Move(t);probe.center=(lo+hi)*.5f-t.position;probe.size=hi-lo;Record(probe);}else Move(t);
     }
    }
    foreach(var go in s.GetRootGameObjects().Where(g=>g.transform!=root)){if(go.name.StartsWith("Player"))Move(go.transform);else if(go.name=="Camera")foreach(Transform c in go.transform)Move(c);}
    int meshCount=Swap(root.Find("Architecture_Sections"),architecture)+Swap(root.Find("Wall_Surface_Wear"),walls);if(details!=null)meshCount+=Swap(root.Find("B4_ServiceDetails"),details);
    var arch=Arches(root,f);var sentinel=new GameObject("Wide_Corridor_V0.01");sentinel.transform.SetParent(root,false);Physics.SyncTransforms();EditorSceneManager.MarkSceneDirty(s);EditorSceneManager.SaveScene(s);results.Add(new{floor=f,meshCount,disabledOldCorridorLights=disabled,arch});
   }
  }finally{Application.logMessageReceived-=cb;if(!SceneManager.GetActiveScene().isDirty)EditorSceneManager.OpenScene(original);}File.WriteAllText(Out+"applied.json",JsonConvert.SerializeObject(new{results,logs},Formatting.Indented));return new{results,logs};
 }
 public static object RebuildArches(){Ready();string original=SceneManager.GetActiveScene().path;var rows=new List<object>();try{AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);foreach(string f in new[]{"B5","B4","B3"}){var s=EditorSceneManager.OpenScene(Scene(f));var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith(f+"_Stealth_Level")).transform;rows.Add(new{floor=f,arch=Arches(root,f)});EditorSceneManager.MarkSceneDirty(s);EditorSceneManager.SaveScene(s);}}finally{EditorSceneManager.OpenScene(original);}return rows;}
 public static object Structure(){Ready();Directory.CreateDirectory(Out);string original=SceneManager.GetActiveScene().path;var plan=JObject.Parse(File.ReadAllText(Repo+"/Docs/도면/잠입_탐색/layout.json"));var rows=new List<object>();var logs=new List<string>();Application.LogCallback cb=(m,s,t)=>{if(t==LogType.Warning||t==LogType.Error||t==LogType.Exception)logs.Add(m);};Application.logMessageReceived+=cb;
  try{AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);foreach(string f in new[]{"B5","B4","B3"}){var s=EditorSceneManager.OpenScene(Scene(f));var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith(f+"_Stealth_Level")).transform;var data=plan["floors"].Single(p=>(string)p["floor"]==f);int models=Swap(root.Find("Architecture_Sections"),Meshes(f,"Architecture"))+Swap(root.Find("Wall_Surface_Wear"),Meshes(f,"Walls"));var removed=new List<string>();
   foreach(var c in root.GetComponentsInChildren<Collider>(true).Where(c=>c.name.StartsWith("CorridorScreen")||c.name.StartsWith("CorridorBaffle"))){c.enabled=false;Record(c);removed.Add(P(c.transform));}
   var ids=data["rooms"].Where(r=>(string)r["roof"]?["kind"]=="dome").Select(r=>(string)r["id"]).ToArray();int lights=0;foreach(var l in root.GetComponentsInChildren<Light>()){if(ids.Any(id=>l.name.StartsWith("Fixture_"+id+"_")||l.name.StartsWith("Ceiling_"+id+"_")||l.name=="Ceiling_"+id)){l.enabled=false;Record(l);lights++;}}
   var old=root.Find("Corridor_WallEquipment");if(old)UnityEngine.Object.DestroyImmediate(old.gameObject);var group=new GameObject("Corridor_WallEquipment");group.transform.SetParent(root,false);var equip=new List<object>();
   foreach(var bay in data["serviceBays"]){var asset=AssetDatabase.LoadAssetAtPath<GameObject>(Root+"05.Model/Props/Common/"+bay["prefab"]+".prefab");var g=(GameObject)PrefabUtility.InstantiatePrefab(asset,group.transform);g.name=(string)bay["id"]+"_Wall_Service_Cover";g.transform.SetPositionAndRotation(new Vector3((float)bay["x"]-24,0,(float)bay["y"]-16),Quaternion.Euler(0,(float)bay["yaw"],0));g.transform.localScale=V(bay["scale"]);Record(g.transform);equip.Add(new{g.name,pos=g.transform.position.ToString(),size=g.GetComponent<BoxCollider>().bounds.size.ToString()});}
   var arch=Arches(root,f);Physics.SyncTransforms();EditorSceneManager.MarkSceneDirty(s);EditorSceneManager.SaveScene(s);rows.Add(new{floor=f,models,removedBaffleColliders=removed,oldDomeLightsDisabled=lights,equipment=equip,arch});
  }}finally{Application.logMessageReceived-=cb;if(!SceneManager.GetActiveScene().isDirty)EditorSceneManager.OpenScene(original);}File.WriteAllText(Out+"structure.json",JsonConvert.SerializeObject(new{rows,logs},Formatting.Indented));return new{rows,logs};}
}
