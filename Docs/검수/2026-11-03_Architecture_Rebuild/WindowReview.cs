using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
using UnityEngine.Rendering.Universal;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
public static class WindowReview {
 static string Stage=>Path.GetFullPath(Path.Combine(Directory.GetParent(Application.dataPath).FullName,"../../tmp/Architecture_Rebuild_20261103"));
 static float[] V(Vector3 v)=>new[]{v.x,v.y,v.z};
 static string P(Transform t)=>t.parent==null?t.name:P(t.parent)+"/"+t.name;
 static object CR(Collider c)=>new{path=P(c.transform),type=c.GetType().Name,position=V(c.transform.position),rotation=V(c.transform.eulerAngles),scale=V(c.transform.lossyScale),enabled=c.enabled,trigger=c.isTrigger,boundsCenter=V(c.bounds.center),boundsSize=V(c.bounds.size)};
 static void Render(Scene s,string floor,Vector3 pos,Vector3 target){
  var go=new GameObject("VARCO_TemporaryReviewCamera");go.hideFlags=HideFlags.HideAndDontSave;var camera=go.AddComponent<Camera>();camera.enabled=false;camera.transform.position=pos;camera.transform.LookAt(target);camera.fieldOfView=56;camera.nearClipPlane=.05f;camera.farClipPlane=100;camera.clearFlags=CameraClearFlags.Skybox;camera.useOcclusionCulling=true;camera.allowHDR=true;camera.allowMSAA=true;
  var data=camera.GetUniversalAdditionalCameraData();data.renderPostProcessing=true;data.volumeLayerMask=~0;
  var previous=RenderTexture.active;var rt=new RenderTexture(1280,720,24,RenderTextureFormat.ARGB32);camera.targetTexture=rt;
  try{camera.Render();camera.Render();camera.Render();RenderTexture.active=rt;var image=new Texture2D(1280,720,TextureFormat.RGB24,false);image.ReadPixels(new Rect(0,0,1280,720),0,0);image.Apply();File.WriteAllBytes(Path.Combine(Stage,floor+"_scene_applied.png"),image.EncodeToPNG());UnityEngine.Object.DestroyImmediate(image);}
  finally{camera.targetTexture=null;RenderTexture.active=previous;rt.Release();UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(go);}
 }
 public static string Main(){var original=SceneManager.GetActiveScene().path;var scene=EditorSceneManager.OpenScene("Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Isolation.unity",OpenSceneMode.Single);Render(scene,"ObservationWindow",new Vector3(3.2f,1.9f,8.2f),new Vector3(6.02f,2.05f,8));Render(scene,"CoolingObservationWindow",new Vector3(7.2f,1.9f,-18.2f),new Vector3(10.02f,2.05f,-18));EditorSceneManager.OpenScene(original,OpenSceneMode.Single);return "Window rendered";}}

