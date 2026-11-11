using System;using System.IO;using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.SceneManagement;
public static class ZFSession {
 public static object Snapshot(){var s=SceneManager.GetActiveScene();string p=Path.GetFullPath(Path.Combine(Application.dataPath,"../Temp/ZFightingReview/current_unsaved.unity"));EditorSceneManager.SaveScene(s,p,true);return new{s.path,s.isDirty,snapshot=p};}
 public static object Save(){var s=SceneManager.GetActiveScene();bool ok=EditorSceneManager.SaveScene(s);return new{ok,s.isDirty};}
}
