using System;using System.IO;using System.Linq;using UnityEngine;using UnityEditor.SceneManagement;using UnityEngine.SceneManagement;using UnityEngine.Rendering.Universal;
public static class C01WayfindingCapture {
 static string O=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../../Docs/검수/2026-11-07_C01_Wayfinding/"));
 static void Shot(string name,Vector3 pos,Vector3 target,float fov){var go=new GameObject("Wayfinding_Review_Temporary");var c=go.AddComponent<Camera>();c.transform.position=pos;c.transform.LookAt(target);c.nearClipPlane=.03f;c.farClipPlane=160;c.fieldOfView=fov;c.clearFlags=CameraClearFlags.SolidColor;c.backgroundColor=new Color(.027f,.037f,.05f);c.GetUniversalAdditionalCameraData().renderPostProcessing=false;var rt=new RenderTexture(1600,1000,24){antiAliasing=4};var prev=RenderTexture.active;Texture2D tex=null;try{c.targetTexture=rt;c.Render();RenderTexture.active=rt;tex=new Texture2D(1600,1000,TextureFormat.RGB24,false);tex.ReadPixels(new Rect(0,0,1600,1000),0,0);tex.Apply();File.WriteAllBytes(O+name+".png",tex.EncodeToPNG());}finally{RenderTexture.active=prev;c.targetTexture=null;if(tex)UnityEngine.Object.DestroyImmediate(tex);UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(go);}}
 public static object Before()=>Run("Before");public static object After()=>Run("After");
 static object Run(string prefix){var s=SceneManager.GetActiveScene();if(s.isDirty||Application.isPlaying)throw new Exception("Saved edit scene required");var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular")).transform;var room=root.Find("C01_Experiment_Art");var hidden=s.GetRootGameObjects().Where(g=>g.name.StartsWith("Player")).SelectMany(g=>g.GetComponentsInChildren<Renderer>()).ToDictionary(r=>r,r=>r.enabled);try{
  foreach(var x in hidden.Keys)x.enabled=false;
  Shot(prefix+"_NorthJunction",room.position+new Vector3(.9f,1.65f,4.2f),room.position+new Vector3(-1.7f,.25f,7.8f),80);
  Shot(prefix+"_S1_Transfer",room.position+new Vector3(3.6f,1.65f,3.5f),room.position+new Vector3(8.7f,.45f,.85f),80);
  Shot(prefix+"_R1_West",room.position+new Vector3(-4.8f,1.65f,-1.9f),room.position+new Vector3(-9.3f,.45f,-2f),78);
  Shot(prefix+"_M1_Service",room.position+new Vector3(-4.6f,1.65f,1.8f),room.position+new Vector3(-7.6f,.50f,3.9f),76);
  Shot(prefix+"_RouteOverview",room.position+new Vector3(-.5f,6.8f,6.8f),room.position+new Vector3(-.3f,0,1.2f),85);
  Shot(prefix+"_T01_Plaque",room.position+new Vector3(-1.9f,1.65f,6.2f),room.position+new Vector3(-3.65f,1.5f,8.55f),68);
 }finally{foreach(var kv in hidden)kv.Key.enabled=kv.Value;EditorSceneManager.OpenScene(s.path);}return new{prefix,images=6,output=O};}
}
