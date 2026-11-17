if(Application.isPlaying)throw new System.Exception("Edit mode required");
PlayerSettings.runInBackground=false;AssetDatabase.SaveAssets();
var settings=AssetDatabase.LoadAssetAtPath<PlayerThrowSettings>("Assets/Afrer_Seconds/06.Data/PlayerThrowSettings.asset");
var logs=typeof(Editor).Assembly.GetType("UnityEditor.LogEntries");object[] counts={0,0,0};logs.GetMethod("GetCountsByType",System.Reflection.BindingFlags.Static|System.Reflection.BindingFlags.Public).Invoke(null,counts);
var scene=UnityEngine.SceneManagement.SceneManager.GetActiveScene();
var report=new{scene=scene.name,scene.isDirty,Application.isPlaying,PlayerSettings.runInBackground,errors=counts[0],warnings=counts[1],
settings.ShowFullTrajectory,settings.TrajectoryLength,settings.TrajectoryZoomedLength,settings.TrajectoryOpacity,settings.FadeStart,settings.MaxPreviewDistance,settings.TrajectoryMaxTime,
settings.OverhandSpeed,settings.UnderhandSpeed,settings.UnderhandAngle,settings.LandingMarkerRadius};
System.IO.File.WriteAllText(System.IO.Path.GetFullPath(System.IO.Path.Combine(Application.dataPath,"../../../Docs/Review/2026-11-17_TrajectoryFade/audit.json")),Newtonsoft.Json.JsonConvert.SerializeObject(report,Newtonsoft.Json.Formatting.Indented));return report;
