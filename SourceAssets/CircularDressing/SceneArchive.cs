using System;using System.IO;using System.Linq;using System.Collections.Generic;using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.SceneManagement;using Newtonsoft.Json;
public static class SceneArchive {
 const string S="Assets/Afrer_Seconds/01.Scenes/";
 static string Repo=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 static string[] Keep={S+"Stage/Level_B5_Circular.unity",S+"Stage/Level_B2_MezzaninePreview.unity"};
 public static object Inspect(){return new{active=SceneManager.GetActiveScene().path,dirty=SceneManager.GetActiveScene().isDirty,playing=EditorApplication.isPlaying,scenes=AssetDatabase.FindAssets("t:Scene",new[]{S.TrimEnd('/')}).Select(AssetDatabase.GUIDToAssetPath).ToArray(),build=EditorBuildSettings.scenes.Select(s=>new{s.path,s.enabled}).ToArray()};}
 public static object Move(){
  if(EditorApplication.isPlaying||SceneManager.GetActiveScene().isDirty)throw new Exception("Saved edit scene required");
  var paths=AssetDatabase.FindAssets("t:Scene",new[]{S.TrimEnd('/')}).Select(AssetDatabase.GUIDToAssetPath).Where(p=>!Keep.Contains(p)&&!p.Contains("/Old/")).ToArray();
  var builds=EditorBuildSettings.scenes.Select(s=>new{guid=AssetDatabase.AssetPathToGUID(s.path),s.enabled}).ToArray();
  string destFolder=S+"Stage/Old"; if(!AssetDatabase.IsValidFolder(destFolder))AssetDatabase.CreateFolder(S+"Stage","Old");
  var plans=paths.Select(p=>new{from=p,to=destFolder+"/"+Path.GetFileName(p),guid=AssetDatabase.AssetPathToGUID(p),bytes=File.ReadAllBytes(p)}).ToArray();
  string root=Path.GetFullPath(Path.Combine(Application.dataPath,"Afrer_Seconds/01.Scenes"))+Path.DirectorySeparatorChar;
  foreach(var p in plans){if(!Path.GetFullPath(p.to).StartsWith(root,StringComparison.OrdinalIgnoreCase)||File.Exists(p.to))throw new Exception("Invalid or occupied destination: "+p.to);}
  EditorSceneManager.OpenScene(Keep[0]);var done=new List<object>();
  foreach(var p in plans){string error=AssetDatabase.MoveAsset(p.from,p.to);if(!string.IsNullOrEmpty(error))throw new Exception(error);if(AssetDatabase.AssetPathToGUID(p.to)!=p.guid||!p.bytes.SequenceEqual(File.ReadAllBytes(p.to)))throw new Exception("Content/GUID mismatch "+p.to);done.Add(new{p.from,p.to,p.guid});}
  EditorBuildSettings.scenes=builds.Select(b=>new EditorBuildSettingsScene(AssetDatabase.GUIDToAssetPath(b.guid),b.enabled)).ToArray();AssetDatabase.SaveAssets();
  var result=new{moved=done,build=EditorBuildSettings.scenes.Select(s=>new{s.path,s.enabled}).ToArray(),active=SceneManager.GetActiveScene().path};
  Directory.CreateDirectory(Repo+"/Docs/검수/2026-11-06_CircularDressing");File.WriteAllText(Repo+"/Docs/검수/2026-11-06_CircularDressing/scene_archive.json",JsonConvert.SerializeObject(result,Formatting.Indented));return result;
 }
}
