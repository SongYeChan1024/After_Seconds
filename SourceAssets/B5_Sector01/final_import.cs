UnityEditor.AssetDatabase.ImportAsset("Assets/Afrer_Seconds/06.Data/AssetSources/B5_Sector01.json",UnityEditor.ImportAssetOptions.ForceSynchronousImport);
var s=UnityEngine.SceneManagement.SceneManager.GetActiveScene();
return new{scene=s.path,dirty=s.isDirty,playing=UnityEditor.EditorApplication.isPlaying,runInBackground=UnityEngine.Application.runInBackground,recordGuid=UnityEditor.AssetDatabase.AssetPathToGUID("Assets/Afrer_Seconds/06.Data/AssetSources/B5_Sector01.json")};
