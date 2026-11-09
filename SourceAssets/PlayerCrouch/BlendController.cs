using System;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
public static class AS_BlendController {
 public const string Path="Assets/Afrer_Seconds/07.Animator/Player/Controllers/Player_Animator_Blend.controller";
 static AnimationClip Clip(string path)=>AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>().Single(x=>!x.name.StartsWith("__preview__"));
 static void Bool(AnimatorStateTransition t,string p,bool v)=>t.AddCondition(v?AnimatorConditionMode.If:AnimatorConditionMode.IfNot,0,p);
 static AnimatorStateTransition Link(AnimatorState a,AnimatorState b,bool atEnd=false){var t=a.AddTransition(b);t.hasExitTime=atEnd;t.exitTime=.95f;t.hasFixedDuration=true;t.duration=.2f;t.canTransitionToSelf=false;return t;}
 public static object Run(){
 if(AssetDatabase.LoadAssetAtPath<AnimatorController>(Path))throw new Exception("Draft exists; inspect before rewriting.");
 var c=AnimatorController.CreateAnimatorControllerAtPath(Path);var sm=c.layers[0].stateMachine;
 foreach(var n in new[]{"Speed","MoveX","MoveY"})c.AddParameter(n,AnimatorControllerParameterType.Float);
 foreach(var n in new[]{"IsCrouch","IsMoving","IsSprint"})c.AddParameter(n,AnimatorControllerParameterType.Bool);
 foreach(var n in new[]{"IsJump","IsLand","IsPickUp"})c.AddParameter(n,AnimatorControllerParameterType.Trigger);
 string basePath="Assets/Afrer_Seconds/07.Animator/Player/Clips/";
 Func<string,AnimationClip> standing=n=>Clip(basePath+"Rigged_V0.3/Player_"+n+".fbx");
 Func<string,AnimationClip> crouch=n=>AssetDatabase.LoadAssetAtPath<AnimationClip>(basePath+"Crouch/Player_Crouch_"+n+".anim");
 var direction=new BlendTree{name="Crouch Walk Direction",blendType=BlendTreeType.SimpleDirectional2D,blendParameter="MoveX",blendParameterY="MoveY"};AssetDatabase.AddObjectToAsset(direction,c);
 direction.AddChild(crouch("Idle"),Vector2.zero);direction.AddChild(crouch("Forward"),Vector2.up);direction.AddChild(crouch("Back"),Vector2.down);direction.AddChild(crouch("Left"),Vector2.left);direction.AddChild(crouch("Right"),Vector2.right);
 var upright=new BlendTree{name="Standing Speed",blendType=BlendTreeType.Simple1D,blendParameter="Speed",useAutomaticThresholds=false};AssetDatabase.AddObjectToAsset(upright,c);upright.AddChild(standing("Idle"),0);upright.AddChild(standing("Walk"),1);upright.AddChild(standing("Run"),2);
 var low=new BlendTree{name="Crouching Speed",blendType=BlendTreeType.Simple1D,blendParameter="Speed",useAutomaticThresholds=false};AssetDatabase.AddObjectToAsset(low,c);low.AddChild(crouch("Idle"),0);low.AddChild(direction,1);low.AddChild(crouch("Sprint"),2);
 var standState=sm.AddState("Standing",new Vector3(250,100,0));standState.motion=upright;
 var crouchState=sm.AddState("Crouching",new Vector3(250,350,0));crouchState.motion=low;sm.defaultState=standState;
 var down=Link(standState,crouchState);Bool(down,"IsCrouch",true);down.duration=.28f;
 var up=Link(crouchState,standState);Bool(up,"IsCrouch",false);up.duration=.28f;
 var jump=sm.AddState("Jump",new Vector3(550,100,0));jump.motion=standing("Jump");
 var land=sm.AddState("Land",new Vector3(850,100,0));land.motion=standing("Land");
 var pickup=sm.AddState("Pickup",new Vector3(550,350,0));pickup.motion=standing("Pickup");
 var tj=Link(standState,jump);tj.AddCondition(AnimatorConditionMode.If,0,"IsJump");Bool(tj,"IsCrouch",false);Link(jump,land,true);
 foreach(var action in new[]{land,pickup}){Bool(Link(action,standState,true),"IsCrouch",false);Bool(Link(action,crouchState,true),"IsCrouch",true);}
 var pick=sm.AddAnyStateTransition(pickup);pick.AddCondition(AnimatorConditionMode.If,0,"IsPickUp");pick.hasExitTime=false;pick.duration=.15f;pick.canTransitionToSelf=false;
 sm.entryPosition=new Vector3(10,100,0);sm.anyStatePosition=new Vector3(10,350,0);sm.exitPosition=new Vector3(850,350,0);
 EditorUtility.SetDirty(c);EditorUtility.SetDirty(sm);AssetDatabase.SaveAssetIfDirty(c);Selection.activeObject=c;AssetDatabase.OpenAsset(c);
 return new{controller=Path,assignedToPlayer=false,standing=sm.states.First(s=>s.state==standState).state.motion.name,crouching=crouchState.motion.name,thresholds=new[]{0,1,2},rule="Speed is resolved movement amount: 0 idle, 1 walk, 2 forward sprint; forward sprint eligibility remains sprintInput && moveInput.y > 0.",runtimeCodeModified=false};
 }
}
