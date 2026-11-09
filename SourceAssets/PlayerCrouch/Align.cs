using System;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEngine.Animations;
using UnityEngine.Playables;
public static class AS_CrouchAlign {
 static AnimationClip Load(string path)=>AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>().Single(c=>!c.name.StartsWith("__preview__"));
 static object Pose(AnimationClip clip){
 var preview=new PreviewRenderUtility();var graph=PlayableGraph.Create("AlignFeet");
 try{var go=preview.InstantiatePrefabInScene(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Afrer_Seconds/05.Model/Player/PlayerDummy_Rigged_V0.3.fbx"));var a=go.GetComponent<Animator>();a.runtimeAnimatorController=null;a.applyRootMotion=false;a.cullingMode=AnimatorCullingMode.AlwaysAnimate;
 graph.SetTimeUpdateMode(DirectorUpdateMode.Manual);var p=AnimationClipPlayable.Create(graph,clip);var output=AnimationPlayableOutput.Create(graph,"pose",a);output.SetSourcePlayable(p);graph.Play();p.SetTime(clip.length*.5f);graph.Evaluate(.00001f);
 return new{name=clip.name,a.humanScale,head=a.GetBoneTransform(HumanBodyBones.Head).position.y,lf=a.GetBoneTransform(HumanBodyBones.LeftFoot).position.y,rf=a.GetBoneTransform(HumanBodyBones.RightFoot).position.y};
 }finally{graph.Destroy();preview.Cleanup();}}
 public static object Inspect(){
 string p="Assets/Afrer_Seconds/07.Animator/Player/Clips/";
 return new[]{Pose(Load(p+"Rigged_V0.3/Player_Idle.fbx")),Pose(Load(p+"Crouch/Player_Crouch_Stand.fbx")),Pose(Load(p+"Crouch/Player_Crouch_Idle.fbx"))};}
 public static object Trial(){
 string path="Assets/Afrer_Seconds/07.Animator/Player/Clips/Crouch/Player_Crouch_Idle.fbx";
 var mi=(ModelImporter)AssetImporter.GetAtPath(path);var d=mi.clipAnimations[0];d.heightOffset=.1f;mi.clipAnimations=new[]{d};mi.SaveAndReimport();return Inspect();}
 public static object Bindings(){return AnimationUtility.GetCurveBindings(Load("Assets/Afrer_Seconds/07.Animator/Player/Clips/Crouch/Player_Crouch_Stand.fbx")).Select(b=>new{b.path,b.propertyName,type=b.type.Name}).ToArray();}
 public static object Curves(){return new[]{"Idle","Forward","Stand"}.Select(n=>{var clip=Load("Assets/Afrer_Seconds/07.Animator/Player/Clips/Crouch/Player_Crouch_"+n+".fbx");var b=AnimationUtility.GetCurveBindings(clip).First(x=>x.propertyName=="RootT.y");var cv=AnimationUtility.GetEditorCurve(clip,b);var s=AnimationUtility.GetAnimationClipSettings(clip);return new{n,clip.length,s.startTime,s.stopTime,s.loopBlendPositionY,first=cv.keys.First().time,last=cv.keys.Last().time,firstY=cv.keys.First().value,lastY=cv.keys.Last().value};}).ToArray();}
 public static object Original(){var mi=(ModelImporter)AssetImporter.GetAtPath("Assets/Afrer_Seconds/07.Animator/Player/Clips/Crouch/Player_Crouch_Idle.fbx");var d=mi.clipAnimations[0];d.heightFromFeet=false;d.keepOriginalPositionY=true;d.heightOffset=0;mi.clipAnimations=new[]{d};mi.SaveAndReimport();return Inspect();}
}
