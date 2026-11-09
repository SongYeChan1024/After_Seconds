using System;using System.IO;using System.Linq;using UnityEngine;using UnityEditor;using UnityEngine.SceneManagement;using UnityEngine.InputSystem;using Newtonsoft.Json;
public static class B2Inspect {
 public static object Run(){var s=SceneManager.GetActiveScene();var result=new{scene=s.path,s.isDirty,playing=Application.isPlaying,mouse=Mouse.current?.enabled,keyboard=Keyboard.current?.enabled,roots=s.GetRootGameObjects().Select(g=>new{g.name,position=g.transform.position.ToString()}).ToArray()};return result;}
}
