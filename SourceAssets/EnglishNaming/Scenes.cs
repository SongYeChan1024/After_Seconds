using System;using System.IO;using UnityEngine;using UnityEditor.SceneManagement;using UnityEngine.SceneManagement;
public static class ENScenes {
 static void Saved(){var s=SceneManager.GetActiveScene();if(Application.isPlaying)throw new Exception("Edit required");if(s.isDirty){string r=Path.GetFullPath(Path.Combine(Application.dataPath,"../../..")),p=r+"/SourceAssets/EnglishNaming/"+s.name+"_after_play.unity";EditorSceneManager.SaveScene(s,p,true);if(File.ReadAllText(p).TrimStart('\uFEFF').Replace("\r\n","\n")!=File.ReadAllText(s.path).TrimStart('\uFEFF').Replace("\r\n","\n"))throw new Exception("Unreviewed dirty scene copied "+p);EditorSceneManager.SaveScene(s);}}
 public static object B5(){Saved();var s=EditorSceneManager.OpenScene("Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular.unity");return s.path;}
 public static object B4(){Saved();var s=EditorSceneManager.OpenScene("Assets/Afrer_Seconds/01.Scenes/Stage/Level_B4_Circular.unity");return s.path;}
}
