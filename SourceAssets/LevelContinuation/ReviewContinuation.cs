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
public static class ReviewContinuation {
 public static object Images(){
  if(EditorApplication.isPlaying||SceneManager.GetActiveScene().isDirty)throw new Exception("Saved Edit scene required");
  string original=SceneManager.GetActiveScene().path;var photos=new List<object>();
  try{foreach(string floor in new[]{"B5","B4","B3"}){
   EditorSceneManager.OpenScene("Assets/Afrer_Seconds/01.Scenes/Stage/Level_"+floor+"_Stealth.unity");
   float[][] shots=floor=="B5"?new[]{new[]{18.3f,1.7f,11,18.3f,4.3f,5},new[]{16.3f,9.5f,11,15,9.3f,12.25f}}:floor=="B4"?new[]{new[]{17f,1.7f,12.25f,12f,1.7f,12.25f},new[]{16.3f,1.7f,11,16.3f,-1.5f,5},new[]{22.65f,1.7f,7,22.65f,3.5f,13.6f},new[]{20.75f,8.1f,7.6f,19.5f,8,7.5f}}:new[]{new[]{22f,1.7f,7.5f,15f,1.7f,7.5f},new[]{-15.2f,1.7f,-10,-15.2f,1.7f,8},new[]{-11f,1.7f,11.8f,-10,1.3f,15},new[]{0f,1.7f,-3,5,1.4f,-7},new[]{10f,1.7f,6.2f,4,1.2f,4},new[]{18.5f,1.7f,-9,19.5f,1.5f,-5},new[]{20.75f,1.7f,8,20.75f,-1f,13.6f}};
   for(int i=0;i<shots.Length;i++){var a=shots[i];photos.Add(Capture(Out+"/"+floor+"/View"+(i+1)+".png",new Vector3(a[0],a[1],a[2]),new Vector3(a[3],a[4],a[5])));}
  }}finally{EditorSceneManager.OpenScene(original);}Write(Out+"/images.json",photos);return photos;
 }
 public static string Repo=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 public static string Out=>Path.Combine(Repo,"Docs/검수/2026-11-06_LevelContinuation");
 public static float[] V(Vector3 v)=>new[]{v.x,v.y,v.z};
 public static float[] C(Color c)=>new[]{c.r,c.g,c.b,c.a};
 public static string P(Transform t)=>t.parent?P(t.parent)+"/"+t.name:t.name;
 public static void Write(string path,object data){Directory.CreateDirectory(Path.GetDirectoryName(path));File.WriteAllText(path,JsonConvert.SerializeObject(data,Formatting.Indented));}
 public static object Capture(string path,Vector3 pos,Vector3 target){
  var main=Camera.main;var go=new GameObject("Temporary_Lab_Review"){hideFlags=HideFlags.HideAndDontSave};var cam=go.AddComponent<Camera>();if(main)cam.CopyFrom(main);cam.enabled=false;cam.transform.SetPositionAndRotation(pos,Quaternion.LookRotation(target-pos));cam.fieldOfView=65;cam.nearClipPlane=.05f;cam.farClipPlane=160;cam.allowHDR=true;
  var cd=go.AddComponent<UniversalAdditionalCameraData>();var md=main?main.GetComponent<UniversalAdditionalCameraData>():null;cd.renderPostProcessing=md&&md.renderPostProcessing;if(md)cd.volumeLayerMask=md.volumeLayerMask;cd.antialiasing=AntialiasingMode.SubpixelMorphologicalAntiAliasing;
  var rt=new RenderTexture(1280,800,24,RenderTextureFormat.ARGB32,RenderTextureReadWrite.sRGB);rt.Create();var prev=RenderTexture.active;Texture2D im=null;
  try{cam.targetTexture=rt;cam.Render();cam.Render();RenderTexture.active=rt;im=new Texture2D(1280,800,TextureFormat.RGB24,false);im.ReadPixels(new Rect(0,0,1280,800),0,0);im.Apply();Directory.CreateDirectory(Path.GetDirectoryName(path));File.WriteAllBytes(path,im.EncodeToPNG());var pixels=im.GetPixels32();double lum=pixels.Average(c=>(.2126*c.r+.7152*c.g+.0722*c.b)/255);double clipped=(double)pixels.Count(c=>c.r>250&&c.g>250&&c.b>250)/pixels.Length;return new{path,meanDisplayLuminance=lum,clippedWhiteFraction=clipped,postProcessing=cd.renderPostProcessing};}
  finally{RenderTexture.active=prev;cam.targetTexture=null;if(im)UnityEngine.Object.DestroyImmediate(im);rt.Release();UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(go);}
 }
}
