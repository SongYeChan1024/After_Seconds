using System;using System.IO;using System.Linq;using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.SceneManagement;using UnityEngine.Rendering.Universal;
public static class AEWeatherReview {
static string O;
 static void Shot(string file,Vector3 pos,Vector3 target,float fov=78){var go=new GameObject("F1_ReviewCamera"){hideFlags=HideFlags.HideAndDontSave};var c=go.AddComponent<Camera>();c.transform.position=pos;c.transform.LookAt(target);c.useOcclusionCulling=false;c.nearClipPlane=.03f;c.farClipPlane=400;c.fieldOfView=fov;c.GetUniversalAdditionalCameraData().renderPostProcessing=false;var rt=new RenderTexture(1600,1000,24){antiAliasing=4};var old=RenderTexture.active;Texture2D tex=null;bool asyncBefore=ShaderUtil.allowAsyncCompilation;ShaderUtil.allowAsyncCompilation=false;try{c.targetTexture=rt;c.Render();c.Render();RenderTexture.active=rt;tex=new Texture2D(1600,1000,TextureFormat.RGB24,false);tex.ReadPixels(new Rect(0,0,1600,1000),0,0);tex.Apply();File.WriteAllBytes(O+file+".jpg",tex.EncodeToJPG(92));}finally{ShaderUtil.allowAsyncCompilation=asyncBefore;RenderTexture.active=old;c.targetTexture=null;if(tex)UnityEngine.Object.DestroyImmediate(tex);UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(go);}}
public static object Before()=>Capture("texture_before");public static object After()=>Capture("texture_after");
static object Capture(string phase){var s=SceneManager.GetActiveScene();if(s.isDirty||Application.isPlaying)throw new Exception("Saved edit required");O=Path.GetFullPath(Path.Combine(Application.dataPath,"../../../Docs/Review/2026-11-12_1F_Abandoned/"))+phase+"/";Directory.CreateDirectory(O);var player=s.GetRootGameObjects().Single(g=>g.name.StartsWith("Player"));player.SetActive(false);try{
Shot("VA_wall",new Vector3(-44,1.7f,28),new Vector3(-48.8f,1.8f,30.1f),82);
Shot("VA_wide",new Vector3(-41.5f,1.7f,24.8f),new Vector3(-44,1.9f,32.8f),88);
Shot("VB_wall",new Vector3(44,1.7f,-28),new Vector3(48.8f,1.8f,-25),82);
Shot("VL_wall",new Vector3(42,1.7f,29.5f),new Vector3(48.8f,1.9f,31),82);
Shot("C01_wall",new Vector3(-18,1.7f,-8),new Vector3(-25.8f,3.2f,3),82);
Shot("C04_wall",new Vector3(-9,1.7f,21),new Vector3(-17,1.9f,31),82);
Shot("Factory_exterior",new Vector3(-44,1.7f,-7),new Vector3(-20,5,8),75);
Shot("Concrete_floor",new Vector3(-12,2,-9),new Vector3(-8,0,-4),76);
}finally{EditorSceneManager.OpenScene(s.path);}return new{phase,images=8};}}
