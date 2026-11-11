using System;using System.IO;using System.Linq;using System.Collections.Generic;using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.SceneManagement;using Newtonsoft.Json;
public static class ZFCleanup {
 public static object Run(){if(Application.isPlaying||SceneManager.GetActiveScene().isDirty)throw new Exception("Clean edit required");
  string root=Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
  var roots=AssetDatabase.GetAllAssetPaths().Where(p=>p.StartsWith("Assets/")&&(p.EndsWith(".unity")||p.EndsWith(".prefab"))).ToArray();
  var used=new HashSet<string>(AssetDatabase.GetDependencies(roots,true));var removed=new List<string>();var moved=new List<object>();
  foreach(var file in Directory.GetFiles("Assets/Afrer_Seconds/05.Model","ZF_*.asset",SearchOption.AllDirectories)){
   string path=file.Replace('\\','/');
   if(!used.Contains(path)){if(!AssetDatabase.DeleteAsset(path))throw new Exception("Failed unused derivative cleanup");removed.Add(path);continue;}
   if(path.Contains("/BR_Meshes/")){string dest=path.Replace("/BR_Meshes/","/");string error=AssetDatabase.MoveAsset(path,dest);if(!string.IsNullOrEmpty(error))throw new Exception(error);moved.Add(new{from=path,to=dest});}
  }
  string temp="Assets/Temp/ZFightingReview/B4_initial.png";
  if(File.Exists(temp)){File.Copy(temp,root+"/Docs/Review/2026-11-11_ZFighting/before_initial_scene_view.png",true);AssetDatabase.DeleteAsset(temp);}
  if(Directory.Exists("Assets/Temp/ZFightingReview")&&!Directory.EnumerateFileSystemEntries("Assets/Temp/ZFightingReview").Any())AssetDatabase.DeleteAsset("Assets/Temp/ZFightingReview");
  AssetDatabase.SaveAssets();File.WriteAllText(root+"/SourceAssets/ZFightingReview/cleanup.json",JsonConvert.SerializeObject(new{removed,moved},Formatting.Indented));return new{unusedDerivedMeshesRemoved=removed.Count,moved=moved.Count};
 }
}
