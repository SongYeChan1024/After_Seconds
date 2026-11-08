using System.Linq;using UnityEngine.SceneManagement;using UnityEditor;
public static class ENInspect {public static object Run(){var g=SceneManager.GetActiveScene().GetRootGameObjects().First(x=>x.name.StartsWith("B4_"));return new{gameObject=EditorJsonUtility.ToJson(g),transform=EditorJsonUtility.ToJson(g.transform)};}}
