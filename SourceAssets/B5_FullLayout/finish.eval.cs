var scene=UnityEngine.SceneManagement.SceneManager.GetActiveScene();
if(UnityEditor.EditorApplication.isPlaying||scene.isDirty)throw new System.Exception("Saved edit scene required");
var repo=System.IO.Path.GetFullPath(System.IO.Path.Combine(UnityEngine.Application.dataPath,"../../.."));
var output=repo+"/Docs/검수/2026-11-06_B5_FullLayout/";
foreach(var name in new[]{"B5_Full_Play_C01","B5_Full_Play_Tunnel"}){
 string path="Assets/Temp/"+name+".png";
 if(System.IO.File.Exists(path)){System.IO.File.Copy(path,output+name+".png",true);UnityEditor.AssetDatabase.DeleteAsset(path);}
}
UnityEditor.AssetDatabase.ImportAsset("Assets/Afrer_Seconds/06.Data/AssetSources/B5_FullLayout.json",UnityEditor.ImportAssetOptions.ForceSynchronousImport);
var root=scene.GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular")).transform;
UnityEditor.Selection.activeGameObject=root.Find("C01_Experiment_Art").gameObject;
var sv=UnityEditor.SceneView.lastActiveSceneView;
if(sv){var target=new UnityEngine.Vector3(-15.5f,-80.4f,-9.5f);var pos=new UnityEngine.Vector3(-14.4f,-80.35f,-12.9f);sv.LookAt(target,UnityEngine.Quaternion.LookRotation(target-pos),2.1f,false,true);sv.sceneLighting=true;sv.Repaint();}
var result=new{scene=scene.path,dirty=scene.isDirty,playing=UnityEditor.EditorApplication.isPlaying,player=scene.GetRootGameObjects().Single(g=>g.name.StartsWith("Player")).transform.position.ToString(),background=UnityEngine.Application.runInBackground,selected=UnityEditor.Selection.activeGameObject.name};
System.IO.File.WriteAllText(output+"final_editor_state.json",Newtonsoft.Json.JsonConvert.SerializeObject(result,Newtonsoft.Json.Formatting.Indented));
return result;
