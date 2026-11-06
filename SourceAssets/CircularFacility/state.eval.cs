var s=UnityEngine.SceneManagement.SceneManager.GetActiveScene();
return new {scene=s.path,dirty=s.isDirty,playing=UnityEditor.EditorApplication.isPlaying};
