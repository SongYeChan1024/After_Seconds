// Lab art review V0.01. External Editor-only tool; no runtime behaviour.
using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Newtonsoft.Json;
public static class ReviewLab {
 public static string Repo=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 public static string Out=>Path.Combine(Repo,"Docs/검수/2026-11-06_LabPolish");
 public static float[] V(Vector3 v)=>new[]{v.x,v.y,v.z};
 public static float[] C(Color c)=>new[]{c.r,c.g,c.b,c.a};
 public static string P(Transform t)=>t.parent?P(t.parent)+"/"+t.name:t.name;
 public static void Write(string path,object data){Directory.CreateDirectory(Path.GetDirectoryName(path));File.WriteAllText(path,JsonConvert.SerializeObject(data,Formatting.Indented));}
 public static object Before()=>Both("Before");
 public static object After()=>Both("After");
 public static object Details(){
  string original=SceneManager.GetActiveScene().path;var result=new List<object>();
  try{foreach(string floor in new[]{"B5","B4"}){
   var s=EditorSceneManager.OpenScene("Assets/Afrer_Seconds/01.Scenes/Stage/Level_"+floor+"_Stealth.unity");var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith(floor+"_Stealth_Level"));var doors=root.transform.Find("Lab_Doors");
   var closed=floor=="B5"?doors.Cast<Transform>().Single(d=>d.name.Contains("EN_LIFT")):doors.Cast<Transform>().First(d=>Mathf.Abs(d.Find("Leaf_Left").localPosition.x)<.5f);
   result.Add(Capture(Out+"/After/"+floor+"/Door_Closed.png",closed.TransformPoint(new Vector3(-.35f,1.7f,2.8f)),closed.TransformPoint(new Vector3(0,1.5f,0))));
   var pad=closed.Find("Keypad_Front");result.Add(Capture(Out+"/After/"+floor+"/Keypad.png",pad.TransformPoint(new Vector3(.12f,.04f,.4f)),pad.position));
   var prop=root.transform.Find("Lab_Additional_Props").Cast<Transform>().First(t=>t.name.Contains("Analyzer"));
   result.Add(Capture(Out+"/After/"+floor+"/Analyzer.png",prop.TransformPoint(new Vector3(1.7f,1.7f,2.5f)),prop.TransformPoint(new Vector3(0,1.2f,0))));
   var cart=root.transform.Find("Lab_Additional_Props").Cast<Transform>().First(t=>t.name.Contains("Cart"));
   result.Add(Capture(Out+"/After/"+floor+"/Trolley.png",cart.TransformPoint(new Vector3(1.3f,1.5f,1.5f)),cart.TransformPoint(new Vector3(0,.6f,0))));
  }}finally{EditorSceneManager.OpenScene(original);}Write(Out+"/detail_images.json",result);return result;
 }
 public static object Both(string phase){
  if(EditorApplication.isPlaying||SceneManager.GetActiveScene().isDirty)throw new Exception("Expected saved Edit scene");
  string original=SceneManager.GetActiveScene().path;var summaries=new List<object>();
  try { foreach(string floor in new[]{"B5","B4"}){
   var scene=EditorSceneManager.OpenScene("Assets/Afrer_Seconds/01.Scenes/Stage/Level_"+floor+"_Stealth.unity");
   var all=scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Transform>(true)).ToArray();
   var lights=all.Select(t=>t.GetComponent<Light>()).Where(l=>l).ToArray();
   var renderers=all.Select(t=>t.GetComponent<Renderer>()).Where(r=>r).ToArray();
   var mats=renderers.SelectMany(r=>r.sharedMaterials).Where(m=>m).Distinct().ToArray();
   var volumes=all.Select(t=>t.GetComponent<Volume>()).Where(v=>v).ToArray();
   var data=new{floor,scene=scene.path,ambient=new{mode=RenderSettings.ambientMode.ToString(),sky=C(RenderSettings.ambientSkyColor),equator=C(RenderSettings.ambientEquatorColor),ground=C(RenderSettings.ambientGroundColor),intensity=RenderSettings.ambientIntensity},hdr=UniversalRenderPipeline.asset.supportsHDR,
    lights=lights.Select(l=>new{path=P(l.transform),type=l.type.ToString(),l.enabled,l.intensity,l.range,l.spotAngle,position=V(l.transform.position),color=C(l.color),shadows=l.shadows.ToString()}).ToArray(),
    materials=mats.Select(m=>new{m.name,path=AssetDatabase.GetAssetPath(m),shader=m.shader.name,color=C(m.HasProperty("_BaseColor")?m.GetColor("_BaseColor"):Color.white),metallic=m.HasProperty("_Metallic")?m.GetFloat("_Metallic"):0,smoothness=m.HasProperty("_Smoothness")?m.GetFloat("_Smoothness"):0,bumpScale=m.HasProperty("_BumpScale")?m.GetFloat("_BumpScale"):0,emission=C(m.HasProperty("_EmissionColor")?m.GetColor("_EmissionColor"):Color.black),textures=m.GetTexturePropertyNames().Where(n=>m.GetTexture(n)).Select(n=>new{name=n,path=AssetDatabase.GetAssetPath(m.GetTexture(n)),scale=new[]{m.GetTextureScale(n).x,m.GetTextureScale(n).y}}).ToArray()}).ToArray(),
    volumes=volumes.Select(v=>new{path=P(v.transform),v.enabled,v.isGlobal,v.weight,v.priority,layer=v.gameObject.layer,profile=AssetDatabase.GetAssetPath(v.sharedProfile),components=v.sharedProfile?v.sharedProfile.components.Select(c=>new{name=c.name,json=EditorJsonUtility.ToJson(c)}).ToArray():null}).ToArray(),
    transforms=all.Select(t=>new{path=P(t),position=V(t.localPosition),rotation=V(t.localEulerAngles),scale=V(t.localScale),active=t.gameObject.activeSelf}).ToArray(),
    renderers=renderers.Select(r=>new{path=P(r.transform),r.enabled,center=V(r.bounds.center),size=V(r.bounds.size),materials=r.sharedMaterials.Select(AssetDatabase.GetAssetPath).ToArray()}).ToArray(),
    colliders=all.SelectMany(t=>t.GetComponents<Collider>()).Select(c=>new{path=P(c.transform),type=c.GetType().Name,c.enabled,c.isTrigger,json=EditorJsonUtility.ToJson(c)}).ToArray()};
   Write(Out+"/"+phase+"/"+floor+"/audit.json",data);
   var shots=floor=="B4"?new[]{new[]{17f,1.7f,10,12,1.7f,9},new[]{-10f,1.7f,5.5f,-11.3f,1.7f,-8},new[]{10.5f,1.7f,-8,1,1.5f,-9.5f},new[]{0f,1.7f,6.8f,6,2.4f,1},new[]{-18.8f,1.7f,-4.1f,-12.3f,1.6f,-9.4f}}:new[]{new[]{-7f,1.7f,-6,-13,1.7f,-8},new[]{6f,2.3f,2,9,2.8f,-7},new[]{18.25f,2,10,18.25f,4.2f,5},new[]{-17.5f,1.8f,-14,-16.4f,1.8f,-15.84f},new[]{-3f,1.7f,13.5f,8,1.6f,14}};
   var photos=new List<object>();for(int i=0;i<shots.Length;i++){var a=shots[i];photos.Add(Capture(Out+"/"+phase+"/"+floor+"/View"+(i+1)+".png",new Vector3(a[0],a[1],a[2]),new Vector3(a[3],a[4],a[5])));}
   Write(Out+"/"+phase+"/"+floor+"/images.json",photos);summaries.Add(new{floor,lights=lights.Length,materials=mats.Length,volumeCount=volumes.Length,photos});
  }}finally{EditorSceneManager.OpenScene(original);}
  return summaries;
 }
 public static object Capture(string path,Vector3 pos,Vector3 target){
  var main=Camera.main;var go=new GameObject("Temporary_Lab_Review"){hideFlags=HideFlags.HideAndDontSave};var cam=go.AddComponent<Camera>();if(main)cam.CopyFrom(main);cam.enabled=false;cam.transform.SetPositionAndRotation(pos,Quaternion.LookRotation(target-pos));cam.fieldOfView=65;cam.nearClipPlane=.05f;cam.farClipPlane=160;cam.allowHDR=true;
  var cd=go.AddComponent<UniversalAdditionalCameraData>();var md=main?main.GetComponent<UniversalAdditionalCameraData>():null;cd.renderPostProcessing=md&&md.renderPostProcessing;if(md)cd.volumeLayerMask=md.volumeLayerMask;cd.antialiasing=AntialiasingMode.SubpixelMorphologicalAntiAliasing;
  var rt=new RenderTexture(1280,800,24,RenderTextureFormat.ARGB32,RenderTextureReadWrite.sRGB);rt.Create();var prev=RenderTexture.active;Texture2D im=null;
  try{cam.targetTexture=rt;cam.Render();cam.Render();RenderTexture.active=rt;im=new Texture2D(1280,800,TextureFormat.RGB24,false);im.ReadPixels(new Rect(0,0,1280,800),0,0);im.Apply();Directory.CreateDirectory(Path.GetDirectoryName(path));File.WriteAllBytes(path,im.EncodeToPNG());var pixels=im.GetPixels32();double lum=pixels.Average(c=>(.2126*c.r+.7152*c.g+.0722*c.b)/255);double clipped=(double)pixels.Count(c=>c.r>250&&c.g>250&&c.b>250)/pixels.Length;return new{path,meanDisplayLuminance=lum,clippedWhiteFraction=clipped,postProcessing=cd.renderPostProcessing};}
  finally{RenderTexture.active=prev;cam.targetTexture=null;if(im)UnityEngine.Object.DestroyImmediate(im);rt.Release();UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(go);}
 }
}
