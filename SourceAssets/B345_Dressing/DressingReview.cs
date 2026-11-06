// External Editor-only art inspection. No runtime components.
using System;using System.IO;using System.Linq;using System.Collections.Generic;
using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.SceneManagement;
using UnityEngine.Rendering.Universal;using Newtonsoft.Json;
public static class DressingReview {
 public static string Repo=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 public static string Out=>Repo+"/Docs/검수/2026-11-06_B345_Dressing";
 public static string P(Transform t)=>t.parent?P(t.parent)+"/"+t.name:t.name;
 public static float[] V(Vector3 v)=>new[]{v.x,v.y,v.z};
 public static void Save(string path,object data){Directory.CreateDirectory(Path.GetDirectoryName(path));File.WriteAllText(path,JsonConvert.SerializeObject(data,Formatting.Indented));}
 public static object Before()=>Inspect("Before");
 public static object After()=>Inspect("After");
 public static object Inspect(string stage){
  if(EditorApplication.isPlaying||SceneManager.GetActiveScene().isDirty)throw new Exception("Saved edit scene required");
  string original=SceneManager.GetActiveScene().path;var result=new List<object>();
  try{foreach(string f in new[]{"B5","B4","B3"}){
   var s=EditorSceneManager.OpenScene("Assets/Afrer_Seconds/01.Scenes/Stage/Level_"+f+"_Stealth.unity");
   var rr=s.GetRootGameObjects();var root=rr.Single(g=>g.name.StartsWith(f+"_Stealth_Level"));Physics.SyncTransforms();
   Save(Out+"/"+stage+"/"+f+"_snapshot.json",new{transforms=rr.SelectMany(g=>g.GetComponentsInChildren<Transform>(true)).Select(t=>new{path=P(t),position=V(t.localPosition),rotation=V(t.localEulerAngles),scale=V(t.localScale),active=t.gameObject.activeSelf}),colliders=root.GetComponentsInChildren<Collider>().Where(c=>c.enabled).Select(c=>new{path=P(c.transform),center=V(c.bounds.center),size=V(c.bounds.size),type=c.GetType().Name}),props=root.GetComponentsInChildren<Transform>().Where(t=>t.parent&&(t.parent.name=="Props"||t.parent.name.Contains("Additional_Props")||t.parent.name=="Dressing_Props")).Select(t=>new{name=t.name,position=V(t.position),rotation=V(t.eulerAngles)})});
   float[][] shots=f=="B5"?new[]{new[]{-6f,1.7f,5,-16f,1.2f,-9},new[]{10f,1.7f,-6,0f,1.2f,-9},new[]{-12f,1.7f,12,-10f,1.4f,15},new[]{10f,1.7f,12,5f,1.2f,15},new[]{21f,1.7f,-11,16f,1.2f,-14},new[]{16f,1.7f,-8,22f,1.2f,0}}:f=="B4"?new[]{new[]{-13f,1.7f,-6,-19f,1.3f,-11},new[]{-13f,1.7f,5,-19f,1.3f,0},new[]{10f,1.7f,-5,0f,1.3f,-10},new[]{-1f,1.7f,7,7f,1.3f,5},new[]{-11f,1.7f,12,-8f,1.3f,15},new[]{10f,1.7f,12,6f,1.3f,15}}:new[]{new[]{-15.2f,1.7f,-10,-15.2f,1.7f,8},new[]{-16f,1.5f,-6,-18.2f,1.5f,-6},new[]{-12f,1.7f,12,-10f,1.3f,15},new[]{-1f,1.7f,-3,7f,1.3f,-10},new[]{10f,1.7f,6.2f,4f,1.3f,4},new[]{8f,1.7f,12,10f,1.3f,15},new[]{19f,1.7f,13,17f,1.3f,7}};
   for(int i=0;i<shots.Length;i++){var a=shots[i];Capture(Out+"/"+stage+"/"+f+"_"+i+".png",new Vector3(a[0],a[1],a[2]),new Vector3(a[3],a[4],a[5]));}
   result.Add(new{floor=f,shots=shots.Length});
  }}finally{EditorSceneManager.OpenScene(original);}return result;
 }
 public static void Capture(string path,Vector3 pos,Vector3 target){
  var main=Camera.main;var go=new GameObject("Temporary_Dressing_Review"){hideFlags=HideFlags.HideAndDontSave};var cam=go.AddComponent<Camera>();if(main)cam.CopyFrom(main);cam.enabled=false;cam.transform.SetPositionAndRotation(pos,Quaternion.LookRotation(target-pos));cam.fieldOfView=65;cam.nearClipPlane=.05f;cam.farClipPlane=160;cam.allowHDR=true;
  var cd=go.AddComponent<UniversalAdditionalCameraData>();var md=main?main.GetComponent<UniversalAdditionalCameraData>():null;cd.renderPostProcessing=md&&md.renderPostProcessing;if(md)cd.volumeLayerMask=md.volumeLayerMask;cd.antialiasing=AntialiasingMode.SubpixelMorphologicalAntiAliasing;
  var rt=new RenderTexture(1280,800,24,RenderTextureFormat.ARGB32,RenderTextureReadWrite.sRGB);rt.Create();var prev=RenderTexture.active;Texture2D im=null;
  try{cam.targetTexture=rt;cam.Render();cam.Render();RenderTexture.active=rt;im=new Texture2D(1280,800,TextureFormat.RGB24,false);im.ReadPixels(new Rect(0,0,1280,800),0,0);im.Apply();Directory.CreateDirectory(Path.GetDirectoryName(path));File.WriteAllBytes(path,im.EncodeToPNG());}
  finally{RenderTexture.active=prev;cam.targetTexture=null;if(im)UnityEngine.Object.DestroyImmediate(im);rt.Release();UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(go);}
 }
}
