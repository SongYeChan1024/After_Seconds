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
public static class VerifyArchitecture {
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
 public static string Main(){AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
 var baseline=JArray.Parse(File.ReadAllText(Path.Combine(Stage,"unity_inventory_before.json")));string original=SceneManager.GetActiveScene().path;var results=new List<object>();
 foreach(JObject a in baseline){string path=(string)a["scene"];var scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Single);var all=scene.GetRootGameObjects().SelectMany(r=>r.GetComponentsInChildren<Transform>(true)).ToArray();var instances=all.Where(t=>t.name=="VARCO_Batch02_Visuals").SelectMany(t=>t.Cast<Transform>()).ToArray();var colliders=all.SelectMany(t=>t.GetComponents<Collider>()).Select(CR).ToArray();bool unchanged=JToken.DeepEquals(a["colliders"],JToken.Parse(JsonConvert.SerializeObject(colliders)));var meshes=instances.SelectMany(t=>t.GetComponentsInChildren<MeshFilter>()).ToArray();bool references=meshes.All(m=>m.sharedMesh!=null)&&instances.SelectMany(t=>t.GetComponentsInChildren<Renderer>()).All(r=>r.sharedMaterials.All(m=>m!=null&&m.shader.name=="Universal Render Pipeline/Lit"&&m.GetTexture("_BaseMap")&&m.GetTexture("_BumpMap")));bool missing=all.Any(t=>GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject)>0);bool absent=instances.All(t=>t.GetComponentsInChildren<Collider>().Length==0);if(!unchanged||!references||missing||!absent)throw new Exception("Failed "+path);Physics.SyncTransforms();var overlaps=instances.Select(t=>new{t=t,b=BoundsOf(t.gameObject)}).Select(x=>new{name=x.t.name,colliders=Physics.OverlapBox(x.b.center,x.b.extents*.97f,Quaternion.identity,~0,QueryTriggerInteraction.Ignore).Select(c=>P(c.transform)).ToArray()}).Where(x=>x.colliders.Length>0).ToArray();if(overlaps.Length>0)throw new Exception("Overlaps "+JsonConvert.SerializeObject(overlaps));
 string floor=path.Contains("B5")?"B5":path.Contains("B4")?"B4":path.Contains("B3")?"B3":path.Contains("B2")?"B2":path.Contains("B1")?"B1":"1F";Vector3 pos,target;switch(floor){case "B5":pos=new Vector3(-2.4f,1.8f,6.3f);target=new Vector3(-5.68f,1.475f,4.35f);break;case "B4":pos=new Vector3(1,2,7);target=new Vector3(-2,2,1);break;case "B3":pos=new Vector3(-1.5f,1.8f,5);target=new Vector3(-4.8f,1.1f,2.5f);break;case "B2":pos=new Vector3(2.5f,2.3f,3);target=new Vector3(5.5f,2.7f,-4);break;case "B1":pos=new Vector3(1.5f,1.8f,7);target=new Vector3(4.9f,1,5.5f);break;default:pos=new Vector3(2.6f,1.8f,3);target=new Vector3(5.4f,.9f,-1);break;}Render(scene,floor,pos,target);
 var rebuilt=all.Where(t=>t.name=="RebuiltArchitectureVisual").ToArray();foreach(var t in rebuilt){if(t.GetComponentsInChildren<Collider>().Length!=0)throw new Exception("New collider");foreach(var rr in t.GetComponentsInChildren<Renderer>())if(!rr.enabled||rr.sharedMaterials.Any(m=>m==null||m.shader.name!="Universal Render Pipeline/Lit"))throw new Exception("New model ref");var legacyVisible=t.parent.GetComponentsInChildren<Renderer>().Where(rr=>!rr.transform.IsChildOf(t)&&rr.enabled).ToArray();if(legacyVisible.Length>0)throw new Exception("Old renderer still visible");} var legacy=all.SelectMany(t=>t.GetComponents<MeshFilter>()).Where(m=>m.sharedMesh!=null&&AssetDatabase.GetAssetPath(m.sharedMesh).Contains("/VARCO/")).GroupBy(m=>AssetDatabase.GetAssetPath(m.sharedMesh)).Select(g=>new{mesh=g.Key,count=g.Count(),repaired=g.Key.Contains("/Repaired/")}).ToArray();results.Add(new{floor=floor,instances=instances.Length,uniqueAssets=instances.Select(t=>t.name.Substring(0,3)).Distinct().ToArray(),existingCollidersPreserved=unchanged,materialMeshReferences=references,missingScripts=missing,newCollidersAbsent=absent,overlapCount=overlaps.Length,legacyMeshes=legacy,rebuiltInstances=rebuilt.Length});}
 EditorSceneManager.OpenScene(original,OpenSceneMode.Single);File.WriteAllText(Path.Combine(Stage,"unity_verification.json"),JsonConvert.SerializeObject(results,Formatting.Indented));return "6 scenes reloaded, references/colliders/overlaps verified, renders saved";
 }
 static Bounds BoundsOf(GameObject g){var rr=g.GetComponentsInChildren<Renderer>();var b=rr[0].bounds;foreach(var x in rr.Skip(1))b.Encapsulate(x.bounds);return b;}
}


