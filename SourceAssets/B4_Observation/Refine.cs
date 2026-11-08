using System;using System.Linq;using UnityEngine;using UnityEditor;using UnityEngine.SceneManagement;using UnityEditor.SceneManagement;
public static class B4Refine {
 public static object Run(){var s=SceneManager.GetActiveScene();if(s.isDirty||Application.isPlaying||!s.path.EndsWith("Level_B4_Circular.unity"))throw new Exception("Saved B4 required");var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith("B4_")).transform;var props=root.Find("B4_C01_관측설비");
  for(int i=1;i<=2;i++){float x=i==1?-3.2f:3.2f;var desk=props.Find("B4_C01_상부관측석_"+i.ToString("00"));desk.localPosition=new Vector3(x,2.5f,7.85f);desk.localRotation=Quaternion.identity;var chair=props.Find("B4_C01_상부관측의자_"+i.ToString("00"));chair.localPosition=new Vector3(x,2.5f,8.83f);chair.localRotation=Quaternion.Euler(0,180,0);}
  foreach(var t in root.GetComponentsInChildren<Transform>(true))if(PrefabUtility.IsPartOfPrefabInstance(t)){PrefabUtility.RecordPrefabInstancePropertyModifications(t);foreach(var r in t.GetComponents<Renderer>())PrefabUtility.RecordPrefabInstancePropertyModifications(r);}
  EditorSceneManager.MarkSceneDirty(s);EditorSceneManager.SaveScene(s);var cc=s.GetRootGameObjects().Single(g=>g.name.StartsWith("Player")).GetComponent<CharacterController>();return new{facing="toward test floor",cc.radius,cc.height,cc.skinWidth,cc.stepOffset};}
}
