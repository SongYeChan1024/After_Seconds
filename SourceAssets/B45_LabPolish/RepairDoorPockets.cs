// Door pocket correction V0.01. External Editor-only authoring/inspection.
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
public static class RepairDoorPockets {
 const string Root="Assets/Afrer_Seconds/";
 static string Repo=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 static float[] V(Vector3 p)=>new[]{p.x,p.y,p.z};
 static object BoundsIn(Transform root,MeshFilter mf){var b=mf.sharedMesh.bounds;var points=new List<Vector3>();foreach(int x in new[]{-1,1})foreach(int y in new[]{-1,1})foreach(int z in new[]{-1,1})points.Add(root.InverseTransformPoint(mf.transform.TransformPoint(b.center+Vector3.Scale(b.extents,new Vector3(x,y,z)))));var bounds=new Bounds(points[0],Vector3.zero);foreach(var p in points)bounds.Encapsulate(p);return new{min=V(bounds.min),max=V(bounds.max)};}
 public static object Inspect(){var s=SceneManager.GetActiveScene();var doors=s.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Transform>(true)).Where(t=>t.name.StartsWith("Door_")&&t.Find("Leaf_Left")).ToArray();var report=new{scene=s.path,playing=EditorApplication.isPlaying,dirty=s.isDirty,doors=doors.Take(2).Select(d=>new{name=d.name,position=V(d.position),meshes=d.GetComponentsInChildren<MeshFilter>().Select(m=>new{m.name,parent=m.transform.parent.name,localPosition=V(m.transform.localPosition),bounds=BoundsIn(d,m)}).ToArray(),leaves=new[]{"Left","Right"}.Select(side=>new{side,position=V(d.Find("Leaf_"+side).localPosition),closed=V(d.Find(side+"_Closed").localPosition),open=V(d.Find(side+"_Open").localPosition)}).ToArray()}).ToArray()};Directory.CreateDirectory(Repo+"/Docs/검수/2026-11-06_LabPolish/DoorPocketFix");File.WriteAllText(Repo+"/Docs/검수/2026-11-06_LabPolish/DoorPocketFix/before.json",JsonConvert.SerializeObject(report,Formatting.Indented));return report;}
 public static object Compare(){
  var s=SceneManager.GetActiveScene();if(EditorApplication.isPlaying||s.isDirty)throw new Exception("Saved Edit scene required");
  var d=s.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Transform>(true)).Single(t=>t.name=="Door_01_N_M"&&t.Find("Leaf_Left"));
  var leaves=new[]{d.Find("Leaf_Left"),d.Find("Leaf_Right")};var saved=leaves.Select(t=>t.localPosition).ToArray();var files=new List<string>();
  try{foreach(string state in new[]{"Open","Closed"}){for(int i=0;i<2;i++)leaves[i].localPosition=d.Find((i==0?"Left":"Right")+"_"+state).localPosition;
   string path=Repo+"/Docs/검수/2026-11-06_LabPolish/DoorPocketFix/B4_"+state+".png";Capture(path,d.TransformPoint(new Vector3(-.35f,1.7f,3.1f)),d.TransformPoint(new Vector3(0,1.51f,0)));files.Add(path);
  }}finally{for(int i=0;i<2;i++)leaves[i].localPosition=saved[i];if(s.isDirty)EditorSceneManager.OpenScene(s.path);}
  return new{door=d.name,files,sceneSaved=false};
 }
 static void Capture(string path,Vector3 pos,Vector3 target){
  var go=new GameObject("Temporary_Door_Compare"){hideFlags=HideFlags.HideAndDontSave};var cam=go.AddComponent<Camera>();if(Camera.main)cam.CopyFrom(Camera.main);cam.enabled=false;cam.transform.SetPositionAndRotation(pos,Quaternion.LookRotation(target-pos));cam.fieldOfView=60;cam.nearClipPlane=.03f;cam.allowHDR=true;
  var data=go.AddComponent<UniversalAdditionalCameraData>();data.renderPostProcessing=true;data.volumeLayerMask=1;data.antialiasing=AntialiasingMode.SubpixelMorphologicalAntiAliasing;
  var rt=new RenderTexture(1280,800,24,RenderTextureFormat.ARGB32,RenderTextureReadWrite.sRGB);rt.Create();var previous=RenderTexture.active;Texture2D image=null;
  try{cam.targetTexture=rt;cam.Render();cam.Render();RenderTexture.active=rt;image=new Texture2D(1280,800,TextureFormat.RGB24,false);image.ReadPixels(new Rect(0,0,1280,800),0,0);image.Apply();File.WriteAllBytes(path,image.EncodeToPNG());}
  finally{RenderTexture.active=previous;cam.targetTexture=null;rt.Release();UnityEngine.Object.DestroyImmediate(rt);if(image)UnityEngine.Object.DestroyImmediate(image);UnityEngine.Object.DestroyImmediate(go);}
 }
}
