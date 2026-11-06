using System;using System.IO;using System.Linq;using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.SceneManagement;using Newtonsoft.Json;
public static class FinishDressing{
 public static object RestoreBackground(){if(EditorApplication.isPlaying)throw new Exception("Edit mode required");bool previous=PlayerSettings.runInBackground;PlayerSettings.runInBackground=false;AssetDatabase.SaveAssets();return new{previous,current=PlayerSettings.runInBackground,application=Application.runInBackground};}
 public static object Check(){
  if(EditorApplication.isPlaying||SceneManager.GetActiveScene().isDirty)throw new Exception("Saved edit scene required");
  AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
  EditorSceneManager.OpenScene("Assets/Afrer_Seconds/01.Scenes/Stage/Level_B3_Stealth.unity");
  var group=GameObject.Find("B3_Stealth_Level_V0.01").transform.Find("Specimen_Cases_6Patterns");
  var data=new{caseCount=group.childCount,enabledCaseColliders=group.GetComponentsInChildren<Collider>().Count(c=>c.enabled),LODGroups=group.GetComponentsInChildren<LODGroup>().Length,skins=group.Cast<Transform>().GroupBy(t=>t.name.Substring(9)).Select(g=>new{name=g.Key,count=g.Count()}).ToArray(),scene=SceneManager.GetActiveScene().path,dirty=SceneManager.GetActiveScene().isDirty,playing=EditorApplication.isPlaying,runInBackground=Application.runInBackground,metadata=AssetDatabase.LoadAssetAtPath<TextAsset>("Assets/Afrer_Seconds/06.Data/AssetSources/B345_Dressing_20261106.json")!=null};
  if(group.childCount!=288||data.enabledCaseColliders!=0||data.LODGroups!=288)throw new Exception("Case structure mismatch");
  var repo=Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));File.WriteAllText(repo+"/Docs/검수/2026-11-06_B345_Dressing/final_state.json",JsonConvert.SerializeObject(data,Formatting.Indented));return data;
 }
}
