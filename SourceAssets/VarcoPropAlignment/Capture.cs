using System;using System.IO;using System.Linq;using System.Collections.Generic;using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.SceneManagement;using UnityEngine.Rendering.Universal;using Newtonsoft.Json.Linq;
public static class VACapture {
 static string R=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 public static object Run(string phase){var s=SceneManager.GetActiveScene();if(Application.isPlaying||(s.isDirty&&!phase.StartsWith("candidate"))||!s.path.EndsWith("Level_B2_Circular.unity"))throw new Exception("Saved B2 required");string scene=s.path;string dir=R+"/Docs/Review/2026-11-11_VarcoPropAlignment";Directory.CreateDirectory(dir);
  var data=JObject.Parse(File.ReadAllText(R+"/SourceAssets/VarcoPropAlignment/before.json"));var all=s.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Transform>(true)).ToArray();var renderers=all.Select(x=>x.GetComponent<Renderer>()).Where(x=>x).ToArray();var lights=all.Select(x=>x.GetComponent<Light>()).Where(x=>x&&x.enabled).ToArray();var layers=renderers.Select(x=>new{r=x,layer=x.gameObject.layer}).ToArray();int count=0;
  try{foreach(var l in lights)l.enabled=false;foreach(var r in renderers)if(r.gameObject.layer==31)r.gameObject.layer=0;
   foreach(var group in data["rows"].GroupBy(x=>(string)x["model"])){
    string model=group.Key;if((phase.StartsWith("candidate")||phase.StartsWith("lod"))&&!new[]{"BM_HVACUnit","B2_EmergencyGenerator","SD_CylinderTrolley"}.Contains(model))continue;var target=all.Single(x=>x.name==(string)group.First()["name"]);var rr=target.GetComponentsInChildren<MeshRenderer>().Where(x=>x.enabled).ToArray();var saved=rr.Select(x=>new{r=x,layer=x.gameObject.layer,on=x.enabled}).ToArray();var bounds=new Bounds();bool first=true;int desired=phase.StartsWith("lod")?int.Parse(phase.Substring(3)):0;
    foreach(var r in rr){var lod=target.GetComponentsInChildren<LODGroup>(true).FirstOrDefault(l=>l.GetLODs().Any(x=>x.renderers.Contains(r)));int level=lod?Mathf.Min(desired,lod.GetLODs().Length-1):0;bool high=!lod||lod.GetLODs()[level].renderers.Contains(r);if(lod)lod.ForceLOD(level);if(!high){r.enabled=false;continue;}r.gameObject.layer=31;if(first){bounds=r.bounds;first=false;}else bounds.Encapsulate(r.bounds);}
    if(first)continue;bool varco=new[]{"BM_CoolingPump","BM_HVACUnit","BM_Centrifuge","B2_EmergencyGenerator","SD_CylinderTrolley"}.Contains(model);
    foreach(int side in (varco?new[]{0,1,2}:new[]{0})){
     float size=Mathf.Max(bounds.size.x,bounds.size.y,bounds.size.z);var center=bounds.center;Vector3 direction=side==0?new Vector3(1,.65f,-1):side==1?new Vector3(-1,.65f,1):new Vector3(0,.12f,-1);
     var go=new GameObject("VA_TemporaryCamera"){hideFlags=HideFlags.HideAndDontSave};var c=go.AddComponent<Camera>();c.transform.position=center+direction.normalized*(size*2+1);c.transform.LookAt(center);c.orthographic=true;c.orthographicSize=size*.68f;c.nearClipPlane=.03f;c.farClipPlane=size*5+20;c.cullingMask=1<<31;c.clearFlags=CameraClearFlags.SolidColor;c.backgroundColor=new Color(.13f,.16f,.18f);c.useOcclusionCulling=false;c.GetUniversalAdditionalCameraData().renderPostProcessing=false;
     var lamp=go.AddComponent<Light>();lamp.type=LightType.Directional;lamp.intensity=1.5f;lamp.shadows=LightShadows.None;lamp.cullingMask=1<<31;var rt=new RenderTexture(640,640,24){antiAliasing=4};var old=RenderTexture.active;Texture2D tex=null;
     try{c.targetTexture=rt;c.Render();RenderTexture.active=rt;tex=new Texture2D(640,640,TextureFormat.RGB24,false);tex.ReadPixels(new Rect(0,0,640,640),0,0);tex.Apply();File.WriteAllBytes(dir+"/"+phase+"_"+model+"_"+side+".png",tex.EncodeToPNG());count++;}
     finally{RenderTexture.active=old;c.targetTexture=null;if(tex)UnityEngine.Object.DestroyImmediate(tex);UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(go);}
    }
    foreach(var x in saved){x.r.gameObject.layer=x.layer;x.r.enabled=x.on;}
   }
  }finally{foreach(var x in layers)if(x.r)x.r.gameObject.layer=x.layer;foreach(var l in lights)if(l)l.enabled=true;EditorSceneManager.OpenScene(scene);}
  return new{phase,images=count,sceneUnchanged=true};
 }
}
