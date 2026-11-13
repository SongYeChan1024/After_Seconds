// 순서: 기존 반사 참조/저장 상태 확인 -> 플레이어 외형 임시 숨김 -> 코어 반사 3개만 베이크 -> 원상 복구와 저장된 씬 재열기.
using System;using System.IO;using System.Linq;using System.Collections.Generic;using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.SceneManagement;using UnityEngine.Rendering;using Newtonsoft.Json;
public static class CoreRoofReflections {
 public static object Run(){
 var scene=SceneManager.GetActiveScene();if(scene.isDirty||Application.isPlaying||!scene.path.EndsWith("Level_1F_Factory.unity"))throw new Exception("Saved 1F required");
 var temp=Path.Combine(Path.GetTempPath(),"AfterSeconds_1F_Review_20261113");var backup=Path.Combine(temp,"backup");var root=GameObject.Find("1F_AbandonedFactory");var parent=root.transform.Find("Reflections");var player=scene.GetRootGameObjects().Single(g=>g.name.StartsWith("Player"));var active=player.activeSelf;bool asyncBefore=ShaderUtil.allowAsyncCompilation;var results=new List<object>();
 try {player.SetActive(false);ShaderUtil.allowAsyncCompilation=false;
 foreach(var id in new[]{"VA","VB","VL"}){var probe=parent.Find(id).GetComponent<ReflectionProbe>();var path=AssetDatabase.GetAssetPath(probe.customBakedTexture);if(!path.EndsWith("AE_Reflection_"+id+".exr"))throw new Exception("Unexpected probe texture "+path);var filename=Path.GetFileName(path);if(File.Exists(Path.Combine(backup,filename)))throw new Exception("Already backed up "+filename);File.Copy(path,Path.Combine(backup,filename));File.Copy(path+".meta",Path.Combine(backup,filename+".meta"));var mode=probe.mode;probe.mode=ReflectionProbeMode.Baked;try{if(!Lightmapping.BakeReflectionProbe(probe,path))throw new Exception("Bake failed "+id);}finally{probe.mode=mode;}AssetDatabase.ImportAsset(path,ImportAssetOptions.ForceSynchronousImport);results.Add(new{id,texture=path,probe.resolution});}
 }finally{ShaderUtil.allowAsyncCompilation=asyncBefore;player.SetActive(active);EditorSceneManager.OpenScene(scene.path);}
 var result=new{probes=results,sceneSaved=!SceneManager.GetActiveScene().isDirty};File.WriteAllText(Path.Combine(temp,"reflections.json"),JsonConvert.SerializeObject(result,Formatting.Indented));return result;
 }
}