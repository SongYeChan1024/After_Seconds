using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
public static class AS_CrouchConnect {
 const string Folder="Assets/Afrer_Seconds/07.Animator/Player/Clips/Crouch";
 const string Controller="Assets/Afrer_Seconds/07.Animator/Player/Controllers/Player_Animator.controller";
 static AnimationClip Clip(string n)=>AssetDatabase.LoadAllAssetsAtPath(Folder+"/Player_Crouch_"+n+".fbx").OfType<AnimationClip>().Single(c=>!c.name.StartsWith("__preview__"));
 static void Cond(AnimatorStateTransition t,string p,bool value){t.AddCondition(value?AnimatorConditionMode.If:AnimatorConditionMode.IfNot,0,p);}
 static AnimatorStateTransition Link(AnimatorState from,AnimatorState to,bool exit=false){var t=from.AddTransition(to);t.hasExitTime=exit;t.exitTime=.94f;t.hasFixedDuration=true;t.duration=.16f;t.canTransitionToSelf=false;t.interruptionSource=TransitionInterruptionSource.Destination;return t;}
 public static object Run(){
 var controller=AssetDatabase.LoadAssetAtPath<AnimatorController>(Controller);
 if(controller.layers[0].stateMachine.states.Any(x=>x.state.name=="Player_Crouch_Walk"))throw new Exception("Already configured; inspect before reapplying.");
 string source=Path.GetFullPath(Path.Combine(Application.dataPath,"../../../SourceAssets/PlayerCrouch"));
 // Preserve the user's current in-memory controller before extending it.
 AssetDatabase.SaveAssetIfDirty(controller);
 File.Copy(Controller,Path.Combine(source,"Before.controller.txt"),false);
 File.Copy(Controller+".meta",Path.Combine(source,"Before.controller.meta.txt"),false);
 var specs=new[]{new{name="Forward",first=52f,last=93f},new{name="Back",first=51f,last=95f},new{name="Left",first=90f,last=130f},new{name="Right",first=85f,last=128f},new{name="Stand",first=38f,last=78f}};
 foreach(var s in specs){var mi=(ModelImporter)AssetImporter.GetAtPath(Folder+"/Player_Crouch_"+s.name+".fbx");var d=mi.clipAnimations[0];d.firstFrame=s.first;d.lastFrame=s.last;d.loopTime=s.name!="Stand";d.loopPose=d.loopTime;mi.clipAnimations=new[]{d};mi.SaveAndReimport();}
 var stand=Clip("Stand");var down=UnityEngine.Object.Instantiate(stand);down.name="Player_Crouch_Enter";
 foreach(var binding in AnimationUtility.GetCurveBindings(stand)){
 var original=AnimationUtility.GetEditorCurve(stand,binding);var keys=original.keys.Reverse().Select(k=>new Keyframe(stand.length-k.time,k.value,-k.outTangent,-k.inTangent,k.outWeight,k.inWeight){weightedMode=k.weightedMode==WeightedMode.In?WeightedMode.Out:k.weightedMode==WeightedMode.Out?WeightedMode.In:k.weightedMode}).ToArray();
 var curve=new AnimationCurve(keys){preWrapMode=WrapMode.ClampForever,postWrapMode=WrapMode.ClampForever};AnimationUtility.SetEditorCurve(down,binding,curve);
 }
 AnimationUtility.SetAnimationEvents(down,new AnimationEvent[0]);var settings=AnimationUtility.GetAnimationClipSettings(stand);settings.loopTime=false;settings.loopBlend=false;AnimationUtility.SetAnimationClipSettings(down,settings);
 AssetDatabase.CreateAsset(down,Folder+"/Player_Crouch_Enter.anim");
 Undo.RegisterCompleteObjectUndo(controller,"Connect player crouch animations");
 var sm=controller.layers[0].stateMachine;
 Func<string,AnimatorState> find=n=>sm.states.Single(x=>x.state.name==n).state;
 var idle=find("Player_Idle");var walk=find("Player_Walk");var run=find("Player_Run");var crouch=find("Player_Crouch");
 if(crouch.motion||crouch.transitions.Length!=0)throw new Exception("Player_Crouch changed since inspection.");
 crouch.motion=Clip("Idle");crouch.iKOnFeet=true;
 var enter=sm.AddState("Player_Crouch_Enter",new Vector3(550,280,0));enter.motion=down;enter.iKOnFeet=true;
 var move=sm.AddState("Player_Crouch_Walk",new Vector3(800,400,0));move.iKOnFeet=true;
 var up=sm.AddState("Player_Crouch_Exit",new Vector3(550,530,0));up.motion=stand;up.iKOnFeet=true;
 if(!controller.parameters.Any(p=>p.name=="IsCrouch"))controller.AddParameter("IsCrouch",AnimatorControllerParameterType.Bool);
 foreach(var parameter in new[]{new{name="MoveX",value=0f},new{name="MoveY",value=1f}}){if(controller.parameters.Any(p=>p.name==parameter.name))throw new Exception("Direction parameter already exists; inspect its use first.");controller.AddParameter(new AnimatorControllerParameter{name=parameter.name,type=AnimatorControllerParameterType.Float,defaultFloat=parameter.value});}
 var tree=new BlendTree{name="Crouch Direction",blendType=BlendTreeType.SimpleDirectional2D,blendParameter="MoveX",blendParameterY="MoveY",useAutomaticThresholds=false};AssetDatabase.AddObjectToAsset(tree,controller);
 tree.AddChild(Clip("Forward"),new Vector2(0,1));tree.AddChild(Clip("Back"),new Vector2(0,-1));tree.AddChild(Clip("Left"),new Vector2(-1,0));tree.AddChild(Clip("Right"),new Vector2(1,0));move.motion=tree;
 // Crouch takes priority over standing locomotion; preserve all original transitions.
 foreach(var from in new[]{idle,walk,run}){foreach(var old in from.transitions)if(!old.conditions.Any(c=>c.parameter=="IsCrouch"))Cond(old,"IsCrouch",false);var t=Link(from,enter);Cond(t,"IsCrouch",true);var transitions=from.transitions;from.transitions=new[]{t}.Concat(transitions.Where(x=>x!=t)).ToArray();}
 foreach(var from in new[]{enter,crouch,move}){var t=Link(from,up);Cond(t,"IsCrouch",false);}
 var t1=Link(enter,crouch,true);Cond(t1,"IsCrouch",true);Cond(t1,"IsMoving",false);
 var t2=Link(enter,move,true);Cond(t2,"IsCrouch",true);Cond(t2,"IsMoving",true);
 var t3=Link(crouch,move);Cond(t3,"IsCrouch",true);Cond(t3,"IsMoving",true);
 var t4=Link(move,crouch);Cond(t4,"IsCrouch",true);Cond(t4,"IsMoving",false);
 var back=Link(up,enter);Cond(back,"IsCrouch",true);
 var stop=Link(up,idle,true);Cond(stop,"IsCrouch",false);Cond(stop,"IsMoving",false);
 var toRun=Link(up,run,true);Cond(toRun,"IsCrouch",false);Cond(toRun,"IsMoving",true);Cond(toRun,"IsSprint",true);
 var toWalk=Link(up,walk,true);Cond(toWalk,"IsCrouch",false);Cond(toWalk,"IsMoving",true);Cond(toWalk,"IsSprint",false);
 EditorUtility.SetDirty(controller);EditorUtility.SetDirty(sm);AssetDatabase.SaveAssetIfDirty(controller);AssetDatabase.SaveAssetIfDirty(down);
 Selection.activeObject=controller;EditorGUIUtility.PingObject(controller);
 return new{controller=Controller,states=sm.states.Select(x=>new{name=x.state.name,motion=x.state.motion?x.state.motion.name:null}).ToArray(),parameters=controller.parameters.Select(p=>new{p.name,type=p.type.ToString(),p.defaultFloat}).ToArray(),enterHuman=down.isHumanMotion,clipCount=7};
 }
}
