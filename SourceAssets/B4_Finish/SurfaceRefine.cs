using System;using System.IO;using System.Linq;using UnityEngine;using UnityEditor;using UnityEngine.SceneManagement;
public static class FinishSurfaceRefine {
 public static object Run(){if(Application.isPlaying||SceneManager.GetActiveScene().isDirty)throw new Exception("Saved edit required");AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);int n=0;foreach(var g in AssetDatabase.FindAssets("FM_FW_ t:Material")){var m=AssetDatabase.LoadAssetAtPath<Material>(AssetDatabase.GUIDToAssetPath(g));if(!m||!m.name.StartsWith("FM_FW_"))continue;m.SetFloat("_BumpScale",.55f);EditorUtility.SetDirty(m);n++;}AssetDatabase.SaveAssets();return new {materials=n};}
}
