using System.Linq;using UnityEngine;using UnityEngine.SceneManagement;
public static class C02State { public static object Run(){var s=SceneManager.GetActiveScene();return new{scene=s.path,dirty=s.isDirty,playing=Application.isPlaying,root=s.GetRootGameObjects().Select(g=>g.name).ToArray()};}}
