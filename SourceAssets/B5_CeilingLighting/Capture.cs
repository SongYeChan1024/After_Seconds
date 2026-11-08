using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
using UnityEngine.Rendering.Universal;
using Newtonsoft.Json.Linq;

public static class CeilingCapture {
 static string Repo=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 static void Shot(string file,Vector3 pos,Vector3 target,float fov=85){
  var go=new GameObject("CeilingReview_Temporary");go.hideFlags=HideFlags.HideAndDontSave;
  var c=go.AddComponent<Camera>();c.transform.position=pos;c.transform.LookAt(target);c.useOcclusionCulling=false;c.nearClipPlane=.04f;c.farClipPlane=200;c.fieldOfView=fov;
  c.GetUniversalAdditionalCameraData().renderPostProcessing=false;
  var rt=new RenderTexture(1440,900,24){antiAliasing=4};var prev=RenderTexture.active;Texture2D tex=null;
  try{c.targetTexture=rt;c.Render();RenderTexture.active=rt;tex=new Texture2D(1440,900,TextureFormat.RGB24,false);tex.ReadPixels(new Rect(0,0,1440,900),0,0);tex.Apply();File.WriteAllBytes(file,tex.EncodeToPNG());}
  finally{RenderTexture.active=prev;c.targetTexture=null;if(tex)UnityEngine.Object.DestroyImmediate(tex);UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(go);}
 }
 public static object Before()=>Run("before");
 public static object After()=>Run("after");
 public static object C04Comparison(){
  var s=SceneManager.GetActiveScene();if(s.isDirty||Application.isPlaying)throw new Exception("Saved Edit required");
  var group=s.GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular")).transform.Find("B5_천장조명").gameObject;
  string o=Repo+"/Docs/검수/2026-11-08_B5_CeilingLighting/";
  try{group.SetActive(false);Shot(o+"before/C04_room.png",new Vector3(16,-77.8f,20),new Vector3(16,-82,22),95);group.SetActive(true);Shot(o+"after/C04_room.png",new Vector3(16,-77.8f,20),new Vector3(16,-82,22),95);}
  finally{EditorSceneManager.OpenScene(s.path);}return new{images=2};
 }
 public static object Probe(){
  var s=SceneManager.GetActiveScene();if(s.isDirty||Application.isPlaying)throw new Exception("Saved Edit required");
  string o=Repo+"/Docs/검수/2026-11-08_B5_CeilingLighting/probe/";Directory.CreateDirectory(o);
  var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular")).transform.Find("B5_천장조명");
  try{foreach(var l in root.GetComponentsInChildren<Light>()){l.GetUniversalAdditionalLightData().usePipelineSettings=false;l.shadowBias=.01f;l.shadowNormalBias=.015f;l.shadowNearPlane=.03f;}
   var p=JObject.Parse(File.ReadAllText(Repo+"/SourceAssets/B5_CorridorOnlyGuidance/plan.json"));
   foreach(string code in new[]{"C01","C03"}){var r=p["rooms"][code];var center=new Vector3((float)r["x"],-82,-(float)r["v"]);float a=(float)r["doors"][0]["angle"]*Mathf.Deg2Rad;var dir=new Vector3(Mathf.Cos(a),0,Mathf.Sin(a));var pos=center+dir*((float)r["r"]-1.5f)+Vector3.up*1.65f;Shot(o+code+"_bias.png",pos,center+Vector3.up*1.4f,92);}
  }finally{EditorSceneManager.OpenScene(s.path);}return new{images=2};
 }
 static object Run(string phase){
  var s=SceneManager.GetActiveScene();if(s.isDirty||Application.isPlaying)throw new Exception("Saved Edit scene required");
  string o=Repo+"/Docs/검수/2026-11-08_B5_CeilingLighting/"+phase+"/";Directory.CreateDirectory(o);
  var p=JObject.Parse(File.ReadAllText(Repo+"/SourceAssets/B5_CorridorOnlyGuidance/plan.json"));int count=0;
  try{
   foreach(var entry in (JObject)p["rooms"]){var r=entry.Value;if((string)r["kind"]!="cavern")continue;var center=new Vector3((float)r["x"],-82,-(float)r["v"]);float a=(float)r["doors"][0]["angle"]*Mathf.Deg2Rad;var dir=new Vector3(Mathf.Cos(a),0,Mathf.Sin(a));var pos=center+dir*((float)r["r"]-1.5f)+Vector3.up*1.65f;Shot(o+entry.Key+"_room.png",pos,center+Vector3.up*1.4f,92);count++;
    if(new[]{"C01","C02","E01","W02"}.Contains(entry.Key)){Shot(o+entry.Key+"_ceiling.png",pos,center+Vector3.up*((float)r["r"]*.72f),95);count++;}
   }
   foreach(var t in p["tunnels"]){var a=new Vector3((float)t["p"][0],-80.35f,-(float)t["p"][1]);var b=new Vector3((float)t["q"][0],-80.35f,-(float)t["q"][1]);Shot(o+(string)t["id"]+".png",a+(b-a).normalized*2.1f,b-Vector3.up*.3f,80);count++;}
  }finally{EditorSceneManager.OpenScene(s.path);}
  return new{phase,images=count,output=o};
 }
}
