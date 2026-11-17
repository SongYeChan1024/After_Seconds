if(Application.isPlaying)throw new System.Exception("Edit mode required");
PlayerSettings.runInBackground=false;
AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);AssetDatabase.SaveAssets();
return new{PlayerSettings.runInBackground,scene=UnityEngine.SceneManagement.SceneManager.GetActiveScene().name,dirty=UnityEngine.SceneManagement.SceneManager.GetActiveScene().isDirty};
