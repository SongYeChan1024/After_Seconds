using System;using System.IO;using System.Linq;using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.SceneManagement;using Newtonsoft.Json;
public static class CeilingRefineRibs {
 public static object Run(){
  var s=SceneManager.GetActiveScene();if(Application.isPlaying)throw new Exception("Edit required");
  var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular")).transform;
  var room=root.Find("B5_천장조명/C01_천장조명");if(room.childCount!=6)throw new Exception("One-time six-to-eight refinement");
  EditorSceneManager.SaveScene(s,Path.Combine(Path.GetTempPath(),"CeilingRibsBefore_"+DateTime.Now.ToString("yyyyMMdd_HHmmss")+".unity"),true);
  for(int i=6;i<8;i++){var g=UnityEngine.Object.Instantiate(room.GetChild(0).gameObject,room);g.name="C01_천장등_"+(i+1).ToString("00");}
  for(int i=0;i<8;i++){
   var g=room.GetChild(i);float a=(10+45*i)*Mathf.Deg2Rad;var normal=new Vector3(Mathf.Cos(a)*.55f,Mathf.Sqrt(1-.55f*.55f),Mathf.Sin(a)*.55f);var tangent=new Vector3(-Mathf.Sin(a),0,Mathf.Cos(a));
   g.SetPositionAndRotation(new Vector3(-15,-82,-10)+normal*9.765f,Quaternion.LookRotation(Vector3.Cross(tangent,normal),normal));
   g.GetComponentInChildren<Light>().intensity=9.75f;
   foreach(var t in g.GetComponentsInChildren<Transform>())if(PrefabUtility.IsPartOfPrefabInstance(t)){PrefabUtility.RecordPrefabInstancePropertyModifications(t);PrefabUtility.RecordPrefabInstancePropertyModifications(t.gameObject);}
  }
  EditorSceneManager.MarkSceneDirty(s);EditorSceneManager.SaveScene(s);AssetDatabase.SaveAssets();
  return new{fixtures=room.childCount,angle=10,step=45,intensity=9.75,totalLightCount=root.GetComponentsInChildren<Light>(true).Length};
 }
}
