using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEngine.SceneManagement;
using UnityEditor.SceneManagement;
using UnityEngine.Rendering.Universal;
public static class CeilingFinish {
 public static object Run(){
  if(Application.isPlaying)throw new Exception("Edit required");
  string path="Assets/Afrer_Seconds/05.Model/Environment/B5/Materials/DL_CeilingDiffuser.mat";
  var m=AssetDatabase.LoadAssetAtPath<Material>(path);m.globalIlluminationFlags=MaterialGlobalIlluminationFlags.BakedEmissive;m.EnableKeyword("_EMISSION");EditorUtility.SetDirty(m);AssetDatabase.SaveAssetIfDirty(m);AssetDatabase.ImportAsset(path,ImportAssetOptions.ForceSynchronousImport);
  var s=SceneManager.GetActiveScene();var group=s.GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular")).transform.Find("B5_천장조명");
  foreach(var l in group.GetComponentsInChildren<Light>()){l.GetUniversalAdditionalLightData().usePipelineSettings=false;l.shadowBias=.01f;l.shadowNormalBias=.015f;l.shadowNearPlane=.1f;EditorUtility.SetDirty(l);EditorUtility.SetDirty(l.GetUniversalAdditionalLightData());}
  EditorSceneManager.MarkSceneDirty(s);EditorSceneManager.SaveScene(s);
  return new{emission=m.IsKeywordEnabled("_EMISSION"),flags=m.globalIlluminationFlags.ToString(),shadowBiasCorrected=group.GetComponentsInChildren<Light>().Length};
 }
}
