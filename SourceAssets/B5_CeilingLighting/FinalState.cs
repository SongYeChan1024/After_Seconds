using System;using System.IO;using System.Linq;using UnityEngine;using UnityEditor;using UnityEngine.SceneManagement;using Newtonsoft.Json;
public static class CeilingFinalState {
 public static object Run(){
  var s=SceneManager.GetActiveScene();if(Application.isPlaying)throw new Exception("Edit required");
  string repo=Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
  string provenance="Assets/Afrer_Seconds/06.Data/AssetSources/B5_CeilingLighting_20261108.json";
  AssetDatabase.ImportAsset(provenance,ImportAssetOptions.ForceSynchronousImport);
  // This task's capture directory only; the shared Assets/Temp folder is preserved.
  string temp="Assets/Temp/B5_CeilingLighting";
  if(Directory.Exists(temp)){
   string resolved=Path.GetFullPath(temp),expected=Path.GetFullPath(Path.Combine(Application.dataPath,"Temp/B5_CeilingLighting"));
   if(!string.Equals(resolved,expected,StringComparison.OrdinalIgnoreCase))throw new Exception("Unexpected capture path");
   AssetDatabase.DeleteAsset(temp);
  }
  if(s.isDirty){
   var copy=Path.Combine(Path.GetTempPath(),"CeilingFinalCompare_"+DateTime.Now.ToString("yyyyMMdd_HHmmss")+".unity");
   UnityEditor.SceneManagement.EditorSceneManager.SaveScene(s,copy,true);
   string disk=File.ReadAllText(s.path).TrimStart('\uFEFF').Replace("\r\n","\n"),memory=File.ReadAllText(copy).TrimStart('\uFEFF').Replace("\r\n","\n");
   if(disk!=memory)throw new Exception("Unreviewed scene edits saved as backup: "+copy);
   UnityEditor.SceneManagement.EditorSceneManager.SaveScene(s);
  }
  var roots=s.GetRootGameObjects();var player=roots.Single(g=>g.name.StartsWith("Player"));var root=roots.Single(g=>g.name.StartsWith("B5_Circular"));
  var data=new{scene=s.path,s.isDirty,Application.isPlaying,Application.runInBackground,playerRunInBackground=PlayerSettings.runInBackground,playerPosition=player.transform.position.ToString(),playerRotation=player.transform.eulerAngles.ToString(),lights=root.GetComponentsInChildren<Light>(true).Length,ceilingFixtures=root.transform.Find("B5_CeilingLights").GetComponentsInChildren<Light>(true).Length,provenanceGuid=AssetDatabase.AssetPathToGUID(provenance)};
  File.WriteAllText(repo+"/Docs/검수/2026-11-08_B5_CeilingLighting/final_state.json",JsonConvert.SerializeObject(data,Formatting.Indented));
  if(data.lights!=340||data.ceilingFixtures!=80||data.runInBackground||data.playerRunInBackground||data.isDirty)throw new Exception("Final state not restored");
  return data;
 }
}
