using System;
using System.Linq;
using UnityEngine;
using UnityEditor;
public static class AS_CrouchSprint {
 const string Folder="Assets/Afrer_Seconds/07.Animator/Player/Clips/Crouch";
 public static object Import(){
 AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);string path=Folder+"/Player_Crouch_Sprint.fbx";
 var mi=(ModelImporter)AssetImporter.GetAtPath(path);mi.animationType=ModelImporterAnimationType.Human;mi.avatarSetup=ModelImporterAvatarSetup.CreateFromThisModel;mi.importAnimation=true;mi.materialImportMode=ModelImporterMaterialImportMode.None;mi.animationCompression=ModelImporterAnimationCompression.Off;mi.SaveAndReimport();
 var d=mi.defaultClipAnimations.Single();d.name="Player_Crouch_Sprint";d.loopTime=true;d.loopPose=true;d.lockRootRotation=true;d.keepOriginalOrientation=true;d.lockRootPositionXZ=true;d.keepOriginalPositionXZ=true;d.lockRootHeightY=true;d.keepOriginalPositionY=true;d.heightFromFeet=false;mi.clipAnimations=new[]{d};mi.SaveAndReimport();
 var clip=AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>().Single(c=>!c.name.StartsWith("__preview__"));
 return new{clip.name,clip.length,clip.isHumanMotion,armBindings=AnimationUtility.GetCurveBindings(clip).Where(b=>b.propertyName.Contains("Arm")||b.propertyName.Contains("Hand")||b.propertyName.Contains("Shoulder")).Select(b=>b.propertyName).ToArray()};
 }
 public static object Unarmed(){
 var src=AssetDatabase.LoadAllAssetsAtPath(Folder+"/Player_Crouch_Sprint.fbx").OfType<AnimationClip>().Single(c=>!c.name.StartsWith("__preview__"));
 var walk=AssetDatabase.LoadAllAssetsAtPath(Folder+"/Player_Crouch_Forward.fbx").OfType<AnimationClip>().Single(c=>!c.name.StartsWith("__preview__"));
 var dst=new AnimationClip{name="Player_Crouch_Sprint_UnarmedSource",frameRate=30};int replaced=0;
 foreach(var b in AnimationUtility.GetCurveBindings(src)){
 var curve=AnimationUtility.GetEditorCurve(src,b);var n=b.propertyName;
 bool arms=new[]{"Left Shoulder","Right Shoulder","Left Arm","Right Arm","Left Forearm","Right Forearm","Left Hand","Right Hand","LeftHand","RightHand"}.Any(prefix=>n.StartsWith(prefix));
 var reference=arms?AnimationUtility.GetEditorCurve(walk,b):null;
 if(reference!=null){var keys=new System.Collections.Generic.List<Keyframe>();int frames=Mathf.RoundToInt(src.length*30);for(int i=0;i<=frames;i++){float t=i==frames?src.length:i/30f;keys.Add(new Keyframe(t,reference.Evaluate(t/src.length*walk.length)));}curve=new AnimationCurve(keys.ToArray());for(int i=0;i<curve.length;i++){AnimationUtility.SetKeyLeftTangentMode(curve,i,AnimationUtility.TangentMode.Linear);AnimationUtility.SetKeyRightTangentMode(curve,i,AnimationUtility.TangentMode.Linear);}replaced++;}
 AnimationUtility.SetEditorCurve(dst,b,curve);}
 AnimationUtility.SetAnimationClipSettings(dst,AnimationUtility.GetAnimationClipSettings(src));string path=Folder+"/Player_Crouch_Sprint_UnarmedSource.anim";AssetDatabase.CreateAsset(dst,path);return new{replaced,dst.isHumanMotion,dst.length};
 }
}
