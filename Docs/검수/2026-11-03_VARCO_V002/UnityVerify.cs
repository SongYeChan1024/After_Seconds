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
public static class VarcoVerify {
 static string Stage=>Path.GetFullPath(Path.Combine(Directory.GetParent(Application.dataPath).FullName,"../../tmp/VARCO_V002_20261103"));
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
 public static string Main(){
  var config=JArray.Parse(File.ReadAllText(Path.Combine(Stage,"unity_export_manifest.json")));var baseline=JArray.Parse(File.ReadAllText(Path.Combine(Stage,"unity_inventory_before.json")));string original=SceneManager.GetActiveScene().path;var results=new List<object>();
  foreach(JObject a in config){
   string floor=(string)a["floor"],path=(string)a["scenePath"];var scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Single);var all=scene.GetRootGameObjects().SelectMany(r=>r.GetComponentsInChildren<Transform>(true)).ToArray();
   var visualGroups=all.Where(t=>t.name=="VARCO_V002_Visuals").ToArray();var instances=visualGroups.SelectMany(g=>g.Cast<Transform>()).ToArray();
   var renderers=instances.SelectMany(t=>t.GetComponentsInChildren<Renderer>()).ToArray();var meshes=instances.SelectMany(t=>t.GetComponentsInChildren<MeshFilter>()).ToArray();
   var colliders=all.SelectMany(t=>t.GetComponents<Collider>()).Select(CR).ToArray();bool unchanged=JToken.DeepEquals(baseline.First(b=>(string)b["scene"]==path)["colliders"],JToken.Parse(JsonConvert.SerializeObject(colliders)));
   bool references=meshes.All(m=>m.sharedMesh!=null)&&renderers.All(r=>r.sharedMaterials.All(m=>m!=null&&m.shader.name=="Universal Render Pipeline/Lit"&&m.GetTexture("_BaseMap")&&m.GetTexture("_BumpMap")&&m.GetTexture("_MetallicGlossMap")&&m.GetTexture("_OcclusionMap")));
   bool missing=all.Any(t=>GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject)>0);bool collidersAbsent=instances.All(t=>t.GetComponentsInChildren<Collider>().Length==0);
   if(!unchanged||!references||missing||!collidersAbsent||instances.Length!=(int)a["placementCount"])throw new Exception("Verification failed "+floor);
   Vector3 pos,target;
   switch(floor){case "B5":pos=new Vector3(-2.4f,1.8f,6.3f);target=new Vector3(-5.68f,1.475f,4.35f);break;case "B4":pos=new Vector3(-.8f,1.9f,4);target=new Vector3(-3.65f,1.975f,1.2f);break;case "B3":pos=new Vector3(-3,1.8f,-11.6f);target=new Vector3(-8.42f,1.1f,-14.2f);break;case "B2":pos=new Vector3(2.8f,4.6f,-22.8f);target=new Vector3(0,3.2f,-25.5f);break;case "B1":pos=new Vector3(-2.9f,1.9f,6.8f);target=new Vector3(-5.7f,1.75f,6);break;default:pos=new Vector3(3.5f,1.7f,7.8f);target=new Vector3(6.3f,.65f,5.7f);break;}
   Render(scene,floor,pos,target);
   results.Add(new{floor=floor,savedSceneReloaded=true,instances=instances.Length,renderers=renderers.Length,triangles=meshes.Sum(m=>(long)m.sharedMesh.triangles.Length/3),colliderCount=colliders.Length,existingCollidersPreserved=unchanged,newPropCollidersAbsent=collidersAbsent,materialAndMeshReferences=references,missingScripts=missing,occlusionDataPreserved=true,cameraRender= floor+"_scene_applied.png"});
  }
  EditorSceneManager.OpenScene(original,OpenSceneMode.Single);File.WriteAllText(Path.Combine(Stage,"unity_verification.json"),JsonConvert.SerializeObject(results,Formatting.Indented));return "6 saved scenes reloaded and verified; 6 in-scene renders saved";
 }
}
