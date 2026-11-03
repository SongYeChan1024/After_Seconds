using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using Newtonsoft.Json;
public static class VarcoInventory {
 public static string PathOf(Transform t) { return t.parent == null ? t.name : PathOf(t.parent)+"/"+t.name; }
 public static float[] V(Vector3 v) { return new[]{v.x,v.y,v.z}; }
 public static string Main() {
  string project=Directory.GetParent(Application.dataPath).FullName;
  string outdir=Path.GetFullPath(Path.Combine(project,"../../tmp/VARCO_V002_20261103"));
  var original=UnityEngine.SceneManagement.SceneManager.GetActiveScene().path;
  if(EditorApplication.isPlaying) throw new Exception("Play mode must be stopped");
  for(int i=0;i<UnityEngine.SceneManagement.SceneManager.sceneCount;i++) if(UnityEngine.SceneManagement.SceneManager.GetSceneAt(i).isDirty) throw new Exception("Unsaved scene");
  var results=new List<object>();
  foreach(string file in Directory.GetFiles(Path.Combine(Application.dataPath,"Afrer_Seconds/01.Scenes/Stage"),"*.unity")) {
   string path="Assets"+file.Substring(Application.dataPath.Length).Replace('\\','/');
   var s=EditorSceneManager.OpenScene(path,OpenSceneMode.Single);
   var all=s.GetRootGameObjects().SelectMany(r=>r.GetComponentsInChildren<Transform>(true)).ToArray();
   var records=all.Where(t=>!PathOf(t).Contains("Dummy")&&!PathOf(t).Contains("Player")&&!PathOf(t).Contains("Guard")&&(!PathOf(t).Contains("Light")||t.parent==null)).Select(t=>new {path=PathOf(t),position=V(t.position),local=V(t.localPosition),scale=V(t.localScale),rotation=V(t.eulerAngles),renderer=t.GetComponent<Renderer>()!=null,bounds=t.GetComponent<Renderer>()!=null?V(t.GetComponent<Renderer>().bounds.size):null}).ToArray();
   var colliders=all.SelectMany(t=>t.GetComponents<Collider>()).Select(c=>new {path=PathOf(c.transform),type=c.GetType().Name,position=V(c.transform.position),rotation=V(c.transform.eulerAngles),scale=V(c.transform.lossyScale),enabled=c.enabled,trigger=c.isTrigger,boundsCenter=V(c.bounds.center),boundsSize=V(c.bounds.size)}).ToArray();
   results.Add(new {scene=path,objects=records,colliders=colliders});
  }
  EditorSceneManager.OpenScene(original,OpenSceneMode.Single);
  File.WriteAllText(Path.Combine(outdir,"unity_inventory_before.json"),JsonConvert.SerializeObject(results,Formatting.Indented));
  return "Read-only inventory saved: "+results.Count+" scenes";
 }
}
