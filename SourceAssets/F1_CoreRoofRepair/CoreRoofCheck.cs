// 순서: 저장된 씬 확인 -> 세 지붕 참조/범위/틈 검사 -> 이전 값과 비교 -> 결과 저장.
using System;using System.IO;using System.Linq;using System.Collections.Generic;using UnityEngine;using UnityEditor;using UnityEngine.SceneManagement;using Newtonsoft.Json;
public static class CoreRoofCheck {
 static string O=Path.Combine(Path.GetTempPath(),"AfterSeconds_1F_Review_20261113");
 public static object Before()=>Inspect("before"); public static object After()=>Inspect("after");
 static float[] V(Vector3 v)=>new[]{v.x,v.y,v.z};
 static object Inspect(string phase){
 var s=SceneManager.GetActiveScene();if(s.isDirty||Application.isPlaying||!s.path.EndsWith("Level_1F_Factory.unity"))throw new Exception("Saved 1F required");
 var all=s.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Transform>(true)).ToArray();
 var state=all.Select(t=>new{path=AnimationUtility.CalculateTransformPath(t,null),p=V(t.localPosition),r=V(t.localEulerAngles),scale=V(t.localScale),active=t.gameObject.activeSelf}).ToArray();
 File.WriteAllText(Path.Combine(O,"transforms_"+phase+".json"),JsonConvert.SerializeObject(state,Formatting.Indented));
 var results=new List<object>();
 foreach(var id in new[]{"VA","VB","VL"}){
 var go=GameObject.Find("AE_"+id+"_Roof");if(!go)throw new Exception("Missing roof "+id);
 var mf=go.GetComponentInChildren<MeshFilter>();var mesh=mf.sharedMesh;var mr=mf.GetComponent<MeshRenderer>();string guid;long fileId;AssetDatabase.TryGetGUIDAndLocalFileIdentifier(mesh,out guid,out fileId);
 float x=id=="VA"?-44:44,z=id=="VB"?-28:28,h=id=="VL"?4.6f:4.2f;
 int hits=0,count=0;var temp=new GameObject("TemporaryRoofProbe"){hideFlags=HideFlags.HideAndDontSave};
 try { temp.transform.SetPositionAndRotation(mf.transform.position,mf.transform.rotation);temp.transform.localScale=mf.transform.lossyScale;var c=temp.AddComponent<MeshCollider>();c.sharedMesh=mesh;Physics.SyncTransforms();
 for(int axis=0;axis<2;axis++)for(int line=1;line<4;line++)for(int along=1;along<10;along++){float a=-5+line*2.5f,b=-5+along;var p=new Vector3(x+(axis==0?a:b),h-.5f,z+(axis==0?b:a));count++;if(c.Raycast(new Ray(p,Vector3.up),out var hit,1))hits++;}
 }finally{UnityEngine.Object.DestroyImmediate(temp);}
 results.Add(new{id,guid,fileId,boundsMin=V(mr.bounds.min),boundsMax=V(mr.bounds.max),triangles=Enumerable.Range(0,mesh.subMeshCount).Sum(i=>(long)mesh.GetIndexCount(i)/3),materials=mr.sharedMaterials.Select(m=>AssetDatabase.GetAssetPath(m)).ToArray(),mesh.isReadable,seamHits=hits,seamSamples=count,colliders=go.GetComponentsInChildren<Collider>(true).Length});
 }
 var result=new{scene=s.path,dirty=s.isDirty,transforms=all.Length,colliders=all.Sum(t=>t.GetComponents<Collider>().Length),roofs=results};
 File.WriteAllText(Path.Combine(O,"roof_"+phase+".json"),JsonConvert.SerializeObject(result,Formatting.Indented));return result;
 }
}