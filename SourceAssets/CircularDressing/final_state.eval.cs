UnityEditor.AssetDatabase.Refresh(UnityEditor.ImportAssetOptions.ForceSynchronousImport);
var s=UnityEngine.SceneManagement.SceneManager.GetActiveScene();
return new {scene=s.path,dirty=s.isDirty,playing=UnityEditor.EditorApplication.isPlaying,scenes=UnityEditor.AssetDatabase.FindAssets("t:Scene",new[]{"Assets/Afrer_Seconds/01.Scenes"}).Select(UnityEditor.AssetDatabase.GUIDToAssetPath).ToArray()};
