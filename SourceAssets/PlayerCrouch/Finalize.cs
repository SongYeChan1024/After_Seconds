using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
public static class AS_CrouchFinalize {
 public static object Run(){
 string folder="Assets/Afrer_Seconds/07.Animator/Player/Clips/Crouch";long before=0,after=0;int reduced=0;
 foreach(string path in Directory.GetFiles(folder,"*.anim")){
 before+=new FileInfo(path).Length;var clip=AssetDatabase.LoadAssetAtPath<AnimationClip>(path);
 foreach(var binding in AnimationUtility.GetCurveBindings(clip)){var curve=AnimationUtility.GetEditorCurve(clip,binding);var k=curve.keys;if(k.Length<3)continue;if(k.All(x=>Mathf.Abs(x.value-k[0].value)<.000001f&&Mathf.Abs(x.inTangent)<.00001f&&Mathf.Abs(x.outTangent)<.00001f)){AnimationUtility.SetEditorCurve(clip,binding,new AnimationCurve(k[0],k[k.Length-1]){preWrapMode=curve.preWrapMode,postWrapMode=curve.postWrapMode});reduced++;}}
 EditorUtility.SetDirty(clip);AssetDatabase.SaveAssetIfDirty(clip);if(!clip.isHumanMotion)throw new Exception("Invalid humanoid clip "+path);after+=new FileInfo(path).Length;
 }
 var pathController="Assets/Afrer_Seconds/07.Animator/Player/Controllers/Player_Animator.controller";var c=AssetDatabase.LoadAssetAtPath<AnimatorController>(pathController);var sm=c.layers[0].stateMachine;
 var missing=sm.states.Where(x=>!x.state.motion).Select(x=>x.state.name).ToArray();if(missing.Length!=0)throw new Exception("Missing motion: "+string.Join(",",missing));
 AssetDatabase.OpenAsset(c);Selection.activeObject=sm.states.Single(x=>x.state.name=="Player_Crouch").state;
 return new{beforeBytes=before,afterBytes=after,constantCurvesReduced=reduced,missingMotionCount=missing.Length,controller=pathController,scene=UnityEngine.SceneManagement.SceneManager.GetActiveScene().path,sceneDirty=UnityEngine.SceneManagement.SceneManager.GetActiveScene().isDirty};
 }
}
