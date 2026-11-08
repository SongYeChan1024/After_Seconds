using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEngine.SceneManagement;
using UnityEditor.SceneManagement;
using Newtonsoft.Json;

public static class CeilingSurvey {
 public static string Repo => Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 public static string Out => Repo+"/Docs/검수/2026-11-08_B5_CeilingLighting/";
 public static string PathOf(Transform t) => t.parent ? PathOf(t.parent)+"/"+t.name : t.name;
 static float[] V(Vector3 v)=>new[]{v.x,v.y,v.z};
 static string Id(UnityEngine.Object o)=>GlobalObjectId.GetGlobalObjectIdSlow(o).ToString();
 public static object Run()=>Snapshot("before");
 public static object After()=>Snapshot("after");
 static object Snapshot(string phase){
  var s=SceneManager.GetActiveScene();
  if(Application.isPlaying || !s.path.EndsWith("Level_B5_Circular.unity"))throw new Exception("B5 Edit required");
  Directory.CreateDirectory(Out);
  if(phase=="before"&&File.Exists(Out+"before.json"))throw new Exception("Baseline already exists");
  var backup=Path.Combine(Path.GetTempPath(),"AfterSeconds_CeilingLighting_"+DateTime.Now.ToString("yyyyMMdd_HHmmss"));Directory.CreateDirectory(backup);
  File.Copy(Path.GetFullPath(s.path),backup+"/disk_before.unity");
  bool dirty=s.isDirty;
  if(dirty && !EditorSceneManager.SaveScene(s,backup+"/unsaved_before.unity",true))throw new Exception("Backup failed");
  var roots=s.GetRootGameObjects();var ts=roots.SelectMany(g=>g.GetComponentsInChildren<Transform>(true)).ToArray();
  var rs=roots.SelectMany(g=>g.GetComponentsInChildren<Renderer>(true)).ToArray();
  var ls=roots.SelectMany(g=>g.GetComponentsInChildren<Light>(true)).ToArray();
  var data=new {scene=s.path,backup,dirty,
   hierarchy=ts.Select(t=>new{id=Id(t),path=PathOf(t),position=V(t.position),localPosition=V(t.localPosition),rotation=V(t.eulerAngles),localRotation=V(t.localEulerAngles),scale=V(t.localScale),active=t.gameObject.activeSelf}),
   renderers=rs.Select(r=>new{id=Id(r),path=PathOf(r.transform),active=r.gameObject.activeInHierarchy,r.enabled,position=V(r.transform.position),rotation=V(r.transform.eulerAngles),center=V(r.bounds.center),size=V(r.bounds.size),mesh=r.GetComponent<MeshFilter>()?AssetDatabase.GetAssetPath(r.GetComponent<MeshFilter>().sharedMesh):"",prefab=PrefabUtility.GetPrefabAssetPathOfNearestInstanceRoot(r.gameObject),materials=r.sharedMaterials.Select(m=>m?AssetDatabase.GetAssetPath(m):null)}),
   lights=ls.Select(l=>new{id=Id(l),path=PathOf(l.transform),position=V(l.transform.position),rotation=V(l.transform.eulerAngles),active=l.gameObject.activeInHierarchy,l.enabled,l.intensity,l.range,l.spotAngle,l.innerSpotAngle,color=new[]{l.color.r,l.color.g,l.color.b,l.color.a},type=l.type.ToString(),shadows=l.shadows.ToString(),json=EditorJsonUtility.ToJson(l)}),
   colliders=ts.SelectMany(t=>t.GetComponents<Collider>()).Select(c=>new{id=Id(c),path=PathOf(c.transform),type=c.GetType().Name,json=EditorJsonUtility.ToJson(c)}),
   renderPipeline=UnityEngine.Rendering.GraphicsSettings.currentRenderPipeline?AssetDatabase.GetAssetPath(UnityEngine.Rendering.GraphicsSettings.currentRenderPipeline):null,
   ambient=new{mode=RenderSettings.ambientMode.ToString(),sky=RenderSettings.ambientSkyColor.ToString(),equator=RenderSettings.ambientEquatorColor.ToString(),ground=RenderSettings.ambientGroundColor.ToString(),RenderSettings.ambientIntensity},
   quality=QualitySettings.GetQualityLevel()
  };
  File.WriteAllText(Out+phase+".json",JsonConvert.SerializeObject(data,Formatting.Indented));
  return new{scene=s.path,backup,dirty,transforms=ts.Length,renderers=rs.Length,lights=ls.Length,data.renderPipeline};
 }
}
