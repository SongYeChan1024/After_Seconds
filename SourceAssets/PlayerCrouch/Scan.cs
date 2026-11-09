using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEngine.Animations;
using UnityEngine.Playables;
public static class AS_CrouchScan {
 public static object Run(){
 var all=new System.Collections.Generic.List<object>();
 foreach(var name in new[]{"Forward","Back","Left","Right","Stand"}){
 string path="Assets/Afrer_Seconds/07.Animator/Player/Clips/Crouch/Player_Crouch_"+name+".fbx";
 var mi=(ModelImporter)AssetImporter.GetAtPath(path);var def=mi.clipAnimations[0];def.loopTime=false;def.loopPose=false;mi.clipAnimations=new[]{def};mi.SaveAndReimport();
 var clip=AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>().Single(c=>!c.name.StartsWith("__preview__"));
 var preview=new PreviewRenderUtility();var graph=PlayableGraph.Create("CrouchScan");
 try{var go=preview.InstantiatePrefabInScene(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Afrer_Seconds/05.Model/Player/PlayerDummy_Rigged_V0.3.fbx"));
 var a=go.GetComponent<Animator>();a.runtimeAnimatorController=null;a.applyRootMotion=false;a.cullingMode=AnimatorCullingMode.AlwaysAnimate;
 graph.SetTimeUpdateMode(DirectorUpdateMode.Manual);var play=AnimationClipPlayable.Create(graph,clip);play.SetApplyFootIK(false);var output=AnimationPlayableOutput.Create(graph,"pose",a);output.SetSourcePlayable(play);graph.Play();
 var rows=new System.Collections.Generic.List<object>();using(var handler=new HumanPoseHandler(a.avatar,go.transform)){
 for(int i=0;i<Mathf.FloorToInt(clip.length*30);i++){play.SetTime(i/30f);graph.Evaluate(.00001f);var pose=new HumanPose();handler.GetHumanPose(ref pose);
 Func<HumanBodyBones,float[]> xyz=b=>{var v=go.transform.InverseTransformPoint(a.GetBoneTransform(b).position);return new[]{v.x,v.y,v.z};};
 rows.Add(new{frame=i+def.firstFrame,head=xyz(HumanBodyBones.Head),hips=xyz(HumanBodyBones.Hips),lf=xyz(HumanBodyBones.LeftFoot),rf=xyz(HumanBodyBones.RightFoot),muscles=(float[])pose.muscles.Clone()});}}
 all.Add(new{name,rows});
 }finally{if(graph.IsValid())graph.Destroy();preview.Cleanup();}
 }
 return all;
 }
}
