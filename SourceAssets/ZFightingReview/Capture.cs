using System;using System.IO;using System.Linq;using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.SceneManagement;using UnityEngine.Rendering.Universal;using Newtonsoft.Json.Linq;
public static class ZFCapture {
 static bool OnlyCircular=false;
 public static object Main(){OnlyCircular=true;return Run("after");}
 static string Root=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 public static object Run(string phase) {
  var initial=SceneManager.GetActiveScene();if(Application.isPlaying||initial.isDirty)throw new Exception("Clean edit required");string restore=initial.path;
  string output=Root+"/Docs/Review/2026-11-11_ZFighting";Directory.CreateDirectory(output);
  var shots=JArray.Parse(File.ReadAllText(Root+"/SourceAssets/ZFightingReview/shots.json"));int count=0;
  try {foreach(var shot in shots){
   string scene=(string)shot["scene"];if(OnlyCircular&&!scene.Contains("_Circular"))continue;if(SceneManager.GetActiveScene().path!=scene)EditorSceneManager.OpenScene(scene);
   var g=new GameObject("TemporaryZFightReviewCamera"){hideFlags=HideFlags.HideAndDontSave};var c=g.AddComponent<Camera>();
   Vector3 Vec(JToken v)=>new Vector3((float)v[0],(float)v[1],(float)v[2]);
   c.transform.position=Vec(shot["position"]);c.transform.LookAt(Vec(shot["target"]));c.fieldOfView=65;c.nearClipPlane=.05f;c.farClipPlane=300;c.useOcclusionCulling=false;c.GetUniversalAdditionalCameraData().renderPostProcessing=true;
   var rt=new RenderTexture(1280,900,24){antiAliasing=4};var old=RenderTexture.active;Texture2D tex=null;
   try{c.targetTexture=rt;c.Render();RenderTexture.active=rt;tex=new Texture2D(1280,900,TextureFormat.RGB24,false);tex.ReadPixels(new Rect(0,0,1280,900),0,0);tex.Apply();File.WriteAllBytes(output+"/"+phase+"_"+(string)shot["name"]+".png",tex.EncodeToPNG());count++;}
   finally{RenderTexture.active=old;c.targetTexture=null;if(tex)UnityEngine.Object.DestroyImmediate(tex);UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(g);}
  }}finally{EditorSceneManager.OpenScene(restore);}return new{count,phase};
 }
}
