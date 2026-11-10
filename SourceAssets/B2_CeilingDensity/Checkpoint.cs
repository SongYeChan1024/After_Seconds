using System;using System.IO;using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.SceneManagement;
public static class CDCheckpoint {
 public static object Save(){var s=SceneManager.GetActiveScene();if(Application.isPlaying||!s.path.EndsWith("Level_B2_Circular.unity"))throw new Exception("B2 edit required");string dir="C:/Users/503-26/Documents/Codex/Backups/AfterSeconds_B2_Ceiling_20261110";Directory.CreateDirectory(dir);bool dirty=s.isDirty;string copy=dir+"/Level_B2_Circular.user_state_"+DateTime.Now.ToString("HHmmss")+".unity";if(!EditorSceneManager.SaveScene(s,copy,true))throw new Exception("Copy failed");if(!EditorSceneManager.SaveScene(s))throw new Exception("Save failed");return new{preservedUnsaved=dirty,copy,saved=!s.isDirty};}
}
