// 순서: 저장 상태와 세 지붕 확인 -> FBX/.meta 백업 -> 후보 3개만 반입 -> 참조 확인.
using System;using System.IO;using UnityEngine;using UnityEditor;using UnityEngine.SceneManagement;
public static class CoreRoofApply {
 public static object Run(){
 var scene=SceneManager.GetActiveScene();if(scene.isDirty||Application.isPlaying||!scene.path.EndsWith("Level_1F_Factory.unity"))throw new Exception("Saved 1F required");
 var temp=Path.Combine(Path.GetTempPath(),"AfterSeconds_1F_Review_20261113");var backup=Path.Combine(temp,"backup");Directory.CreateDirectory(backup);
 const string folder="Assets/Afrer_Seconds/05.Model/Environment/1F/";
 foreach(var id in new[]{"VA","VB","VL"}){var name="AE_"+id+"_Roof.fbx";var asset=folder+name;if(!File.Exists(Path.Combine(temp,"candidate",name))||!File.Exists(asset))throw new Exception("Missing "+name);if(File.Exists(Path.Combine(backup,name)))throw new Exception("Already backed up; inspect before rerunning.");File.Copy(asset,Path.Combine(backup,name));File.Copy(asset+".meta",Path.Combine(backup,name+".meta"));}
 foreach(var id in new[]{"VA","VB","VL"}){var name="AE_"+id+"_Roof.fbx";File.Copy(Path.Combine(temp,"candidate",name),folder+name,true);AssetDatabase.ImportAsset(folder+name,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);}
 return new{applied=3,sceneDirty=scene.isDirty};
 }
}