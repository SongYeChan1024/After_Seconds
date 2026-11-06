using UnityEngine;
using UnityEditor;
using UnityEngine.SceneManagement;
using Newtonsoft.Json;
using System.Linq;
public static class CircularInspect {
 public static object Run(){
  var s=SceneManager.GetActiveScene();
  var rows=new System.Collections.Generic.List<object>();
  foreach(string path in new[]{"Assets/Afrer_Seconds/05.Model/Environment/B5/CF_B5_Core.fbx","Assets/Afrer_Seconds/05.Model/Environment/Common/CF_PocketDoor_240.fbx","Assets/Afrer_Seconds/04.Prefabs/Environment/ObservationPod.prefab","Assets/Afrer_Seconds/05.Model/Props/B5/Props_CoolingPump_B5_Lite.prefab"}){
   var g=AssetDatabase.LoadAssetAtPath<GameObject>(path);if(!g){rows.Add(new{path,missing=true});continue;}
   var rs=g.GetComponentsInChildren<MeshFilter>(true);rows.Add(new{path,meshes=rs.Select(r=>new {r.name,bounds=r.sharedMesh.bounds.ToString(),rotation=r.transform.localEulerAngles.ToString(),position=r.transform.localPosition.ToString()}).Take(16).ToArray()});
  }
  return new {scene=s.path,dirty=s.isDirty,playing=EditorApplication.isPlaying,roots=s.GetRootGameObjects().Select(g=>new {g.name,position=g.transform.position.ToString(),camera=g.GetComponentsInChildren<Camera>(true).Length}).ToArray(),models=rows};
 }
}
