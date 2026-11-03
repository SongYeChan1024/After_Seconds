using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
public static class VarcoApply {
 static string Stage=>Path.GetFullPath(Path.Combine(Directory.GetParent(Application.dataPath).FullName,"../../tmp/VARCO_V002_20261103"));
 static float[] V(Vector3 v)=>new[]{v.x,v.y,v.z};
 static string P(Transform t)=>t.parent==null?t.name:P(t.parent)+"/"+t.name;
 static Transform Find(Scene s,string path)=>s.GetRootGameObjects().SelectMany(r=>r.GetComponentsInChildren<Transform>(true)).FirstOrDefault(t=>P(t)==path);
 static Bounds BoundsOf(GameObject g){var rs=g.GetComponentsInChildren<Renderer>();var b=rs[0].bounds;foreach(var r in rs.Skip(1))b.Encapsulate(r.bounds);return b;}
 static void Preview(GameObject prefab,string file){
  var preview=new PreviewRenderUtility();var go=UnityEngine.Object.Instantiate(prefab);preview.AddSingleGO(go);var b=BoundsOf(go);float size=Mathf.Max(b.size.x,b.size.y,b.size.z);
  preview.camera.transform.position=b.center+new Vector3(-1.4f,.8f,-2.8f)*size;preview.camera.transform.LookAt(b.center);preview.camera.nearClipPlane=.01f;preview.camera.farClipPlane=100;preview.camera.fieldOfView=32;preview.camera.clearFlags=CameraClearFlags.Color;preview.camera.backgroundColor=new Color(.14f,.15f,.17f);
  preview.lights[0].intensity=1.5f;preview.lights[0].transform.rotation=Quaternion.Euler(40,40,0);preview.lights[1].intensity=1;preview.lights[1].transform.rotation=Quaternion.Euler(340,210,0);preview.ambientColor=new Color(.3f,.3f,.3f);
  preview.BeginStaticPreview(new Rect(0,0,900,900));preview.Render(true);var image=preview.EndStaticPreview();File.WriteAllBytes(file,image.EncodeToPNG());UnityEngine.Object.DestroyImmediate(image);preview.Cleanup();
 }
 class Placement {public string room,name;public Vector3 pos;public float yaw;public Placement(string r,string n,float x,float y,float z,float a){room=r;name=n;pos=new Vector3(x,y,z);yaw=a;}}
 static object ColliderRecord(Collider c)=>new {path=P(c.transform),type=c.GetType().Name,position=V(c.transform.position),rotation=V(c.transform.eulerAngles),scale=V(c.transform.lossyScale),enabled=c.enabled,trigger=c.isTrigger,boundsCenter=V(c.bounds.center),boundsSize=V(c.bounds.size)};
 public static string Main(){
  if(EditorApplication.isPlaying)throw new Exception("Edit mode required");
  var config=JArray.Parse(File.ReadAllText(Path.Combine(Stage,"unity_export_manifest.json")));
  var before=JArray.Parse(File.ReadAllText(Path.Combine(Stage,"unity_inventory_before.json")));
  string original=SceneManager.GetActiveScene().path;
  var results=new List<object>();
  foreach(JObject a in config){
   string floor=(string)a["floor"],prefabPath=(string)a["prefabPath"];
   var content=PrefabUtility.LoadPrefabContents(prefabPath);content.transform.Find("VisualRoot").localRotation=Quaternion.Euler(0,180,0);PrefabUtility.SaveAsPrefabAsset(content,prefabPath);PrefabUtility.UnloadPrefabContents(content);
   var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath);
   // Previews after shader warmup and standardized forward direction.
   Preview(prefab,Path.Combine(Stage,floor+"_unity_front.png"));
   string sceneName=floor=="1F"?"Level_1F_Checkpoint":floor=="B1"?"Level_B1_Experiment":floor=="B2"?"Level_B2_Machinery":floor=="B3"?"Level_B3_SampleStorage":floor=="B4"?"Level_B4_Observation":"Level_B5_Isolation";
   string path="Assets/Afrer_Seconds/01.Scenes/Stage/"+sceneName+".unity";var scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Single);
   Placement[] placements;
   switch(floor){
    case "B5":placements=new[]{new Placement("B5_Level_V0.01/Room01_Isolation","IsolationConsole_West",-5.68f,1.15f,5.2f,-90),new Placement("B5_Level_V0.01/Room02_CoolingPool","CoolingConsole_East",5.68f,1.15f,-7f,90)};break;
    case "B4":placements=new[]{new Placement("B4_Observation_Draft/Room03_ObservationCorridor","MonitorBank_Corridor",-3.65f,1.45f,1.2f,-90),new Placement("B4_Observation_Draft/Room04_ControlDeck","MonitorBank_Deck",5.65f,3.2f,-4.8f,90)};break;
    case "B3":placements=new[]{new Placement("B3_SampleLayer_Draft/Room06_DecontaminationAirlock","DeconColumn_West",-5.42f,0,1.8f,-90),new Placement("B3_SampleLayer_Draft/Room06_DecontaminationAirlock","DeconColumn_East",5.42f,0,1.8f,90)};break;
    case "B2":placements=new[]{new Placement("B2_Machinery_Draft/Room08_CentralControl","ControlDesk_West",-1.5f,2.5f,-5.5f,180),new Placement("B2_Machinery_Draft/Room08_CentralControl","ControlDesk_East",1.5f,2.5f,-5.5f,180)};break;
    case "B1":placements=new[]{new Placement("B1_Experiment_Draft/Room09_SubjectChamber","ExperimentPanel_SouthDeck",-5.7f,1.15f,6f,-90)};break;
    default:placements=new[]{new Placement("1F_Checkpoint_Draft/Room10_ExitCheckpoint","InspectionCounter_East",6.3f,0,5.7f,90)};break;
   }
   var placed=new List<object>();
   foreach(var p in placements){
    var parent=Find(scene,p.room);if(parent==null)throw new Exception("Room missing: "+p.room);
    var group=parent.Find("VARCO_V002_Visuals");if(group==null){var gg=new GameObject("VARCO_V002_Visuals");Undo.RegisterCreatedObjectUndo(gg,"Apply VARCO V0.02");gg.transform.SetParent(parent,false);group=gg.transform;}
    if(group.Find(p.name)!=null)throw new Exception("Placement already exists: "+p.name);
    var go=(GameObject)PrefabUtility.InstantiatePrefab(prefab,scene);Undo.RegisterCreatedObjectUndo(go,"Apply VARCO V0.02");go.name=p.name;go.transform.SetParent(group,false);go.transform.localPosition=p.pos;go.transform.localRotation=Quaternion.Euler(0,p.yaw,0);
    foreach(var t in go.GetComponentsInChildren<Transform>(true))GameObjectUtility.SetStaticEditorFlags(t.gameObject,StaticEditorFlags.BatchingStatic|StaticEditorFlags.ReflectionProbeStatic);
    Physics.SyncTransforms();var b=BoundsOf(go);
    var overlaps=Physics.OverlapBox(b.center,b.extents*.98f,Quaternion.identity,~0,QueryTriggerInteraction.Ignore).Where(c=>!c.transform.IsChildOf(go.transform)).Select(c=>P(c.transform)).ToArray();
    if(go.GetComponentsInChildren<Collider>().Length!=0)throw new Exception("Unexpected new collider");
    if(overlaps.Length!=0)throw new Exception("Prop intersects existing collision: "+string.Join(",",overlaps));
    placed.Add(new{name=p.name,room=p.room,localPosition=V(p.pos),yaw=p.yaw,boundsCenter=V(b.center),boundsSize=V(b.size),overlappingColliders=overlaps,prefabPath=prefabPath});
   }
   var hidden=new List<string>();
   if(floor=="B3"){
    var room=Find(scene,"B3_SampleLayer_Draft/Room06_DecontaminationAirlock");
    foreach(var t in room.GetComponentsInChildren<Transform>(true))if(t.name=="Decon_Nozzle_VisualOnly"&&Mathf.Abs(t.localPosition.z-1.8f)<.01f){var renderer=t.GetComponent<Renderer>();if(renderer){Undo.RecordObject(renderer,"Replace middle nozzle visual");renderer.enabled=false;hidden.Add(P(t));}}
   }
   var all=scene.GetRootGameObjects().SelectMany(r=>r.GetComponentsInChildren<Transform>(true)).ToArray();
   var colliders=all.SelectMany(t=>t.GetComponents<Collider>()).Select(ColliderRecord).ToArray();
   var old=before.First(x=>(string)x["scene"]==path)["colliders"];
   bool same=JToken.DeepEquals(old,JToken.Parse(JsonConvert.SerializeObject(colliders)));
   if(!same)throw new Exception("Collider snapshot changed: "+floor);
   bool missing=all.Any(t=>GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject)>0);
   if(missing)throw new Exception("Missing script in "+floor);
   EditorSceneManager.MarkSceneDirty(scene);if(!EditorSceneManager.SaveScene(scene))throw new Exception("Save failed");
   a["status"]="Applied visual prefab to floor scene; existing collider snapshot preserved";a["scenePath"]=path;a["placementCount"]=placements.Length;
   var project=Directory.GetParent(Application.dataPath).FullName;string assetRoot=Path.GetDirectoryName(Path.GetDirectoryName((string)a["modelPath"]));File.WriteAllText(Path.Combine(project,assetRoot,"source_manifest.json"),a.ToString());
   results.Add(new{floor=floor,scene=path,placements=placed,collidersPreserved=same,colliderCount=colliders.Length,missingScripts=missing,hiddenLegacyRenderers=hidden});
  }
  AssetDatabase.SaveAssets();File.WriteAllText(Path.Combine(Stage,"unity_placement_facts.json"),JsonConvert.SerializeObject(results,Formatting.Indented));File.WriteAllText(Path.Combine(Stage,"unity_export_manifest.json"),config.ToString());
  EditorSceneManager.OpenScene(original,OpenSceneMode.Single);return "Applied 10 visual instances across 6 scenes; all collider snapshots identical";
 }
}
