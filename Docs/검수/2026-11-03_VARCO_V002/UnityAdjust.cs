using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
using Newtonsoft.Json.Linq;
public static class VarcoAdjust{
 public static string Main(){
  string stage=Path.GetFullPath(Path.Combine(Directory.GetParent(Application.dataPath).FullName,"../../tmp/VARCO_V002_20261103"));string original=SceneManager.GetActiveScene().path;
  var config=JArray.Parse(File.ReadAllText(Path.Combine(stage,"unity_export_manifest.json")));
  foreach(var a in config){var mat=AssetDatabase.LoadAssetAtPath<Material>((string)a["materialPath"]);mat.SetFloat("_BumpScale",.35f);EditorUtility.SetDirty(mat);}
  var scene=EditorSceneManager.OpenScene("Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Isolation.unity",OpenSceneMode.Single);
  var console=scene.GetRootGameObjects().SelectMany(r=>r.GetComponentsInChildren<Transform>(true)).Single(t=>t.name=="IsolationConsole_West");Undo.RecordObject(console,"Clear security door visual");var pos=console.localPosition;pos.z=4.35f;console.localPosition=pos;Physics.SyncTransforms();EditorSceneManager.MarkSceneDirty(scene);EditorSceneManager.SaveScene(scene);AssetDatabase.SaveAssets();
  var facts=JArray.Parse(File.ReadAllText(Path.Combine(stage,"unity_placement_facts.json")));var item=facts.First(f=>(string)f["floor"]=="B5")["placements"].First(p=>(string)p["name"]=="IsolationConsole_West");item["localPosition"]=new JArray(pos.x,pos.y,pos.z);var b=console.GetComponentsInChildren<Renderer>()[0].bounds;item["boundsCenter"]=new JArray(b.center.x,b.center.y,b.center.z);File.WriteAllText(Path.Combine(stage,"unity_placement_facts.json"),facts.ToString());
  EditorSceneManager.OpenScene(original,OpenSceneMode.Single);return "B5 console moved clear of door; new material normal scale 0.35";
 }
}
