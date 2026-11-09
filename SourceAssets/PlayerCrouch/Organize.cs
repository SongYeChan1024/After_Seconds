using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
public static class AS_CrouchOrganize {
 static void Bool(AnimatorStateTransition t,string p,bool v)=>t.AddCondition(v?AnimatorConditionMode.If:AnimatorConditionMode.IfNot,0,p);
 static AnimatorStateTransition Link(AnimatorState a,AnimatorState b,string name){var t=a.AddTransition(b);t.name=name;t.hasExitTime=false;t.hasFixedDuration=true;t.duration=.16f;t.canTransitionToSelf=false;t.interruptionSource=TransitionInterruptionSource.Destination;return t;}
 public static object Run(){
 string path="Assets/Afrer_Seconds/07.Animator/Player/Controllers/Player_Animator.controller";var c=AssetDatabase.LoadAssetAtPath<AnimatorController>(path);var root=c.layers[0].stateMachine;
 if(root.stateMachines.Any(x=>x.stateMachine.name=="Standing"))throw new Exception("Already organized; do not rerun.");
 AssetDatabase.SaveAssetIfDirty(c);File.Copy(path,Path.GetFullPath(Path.Combine(Application.dataPath,"../../../SourceAssets/PlayerCrouch/BeforeOrganization.controller.txt")),false);
 var old=root.states;Func<string,AnimatorState> find=n=>old.Single(x=>x.state.name==n).state;
 var crouch=find("Player_Crouch");var enter=find("Player_Crouch_Enter");var exit=find("Player_Crouch_Exit");
 var sprint=root.AddState("Player_Crouch_Sprint");sprint.motion=AssetDatabase.LoadAssetAtPath<AnimationClip>("Assets/Afrer_Seconds/07.Animator/Player/Clips/Crouch/Player_Crouch_Sprint.anim");sprint.iKOnFeet=false;
 var t=Link(crouch,sprint,"Forward crouch sprint");Bool(t,"IsCrouch",true);Bool(t,"IsMoving",true);Bool(t,"IsSprint",true);t.AddCondition(AnimatorConditionMode.Greater,.001f,"MoveY");
 t=Link(sprint,exit,"Stand up");Bool(t,"IsCrouch",false);
 t=Link(sprint,crouch,"Sprint released");Bool(t,"IsCrouch",true);Bool(t,"IsSprint",false);
 t=Link(sprint,crouch,"No forward input");Bool(t,"IsCrouch",true);t.AddCondition(AnimatorConditionMode.Less,.00101f,"MoveY");
 t=Link(sprint,crouch,"Movement stopped");Bool(t,"IsCrouch",true);Bool(t,"IsMoving",false);
 var standing=root.AddStateMachine("Standing",new Vector3(250,40,0));
 var crouching=root.AddStateMachine("Crouching",new Vector3(250,290,0));
 standing.states=new[]{new ChildAnimatorState{state=find("Player_Idle"),position=new Vector3(250,60,0)},new ChildAnimatorState{state=find("Player_Walk"),position=new Vector3(250,230,0)},new ChildAnimatorState{state=find("Player_Run"),position=new Vector3(550,230,0)}};
 standing.defaultState=find("Player_Idle");standing.entryPosition=new Vector3(10,60,0);standing.anyStatePosition=new Vector3(10,-70,0);standing.exitPosition=new Vector3(800,60,0);
 crouching.states=new[]{new ChildAnimatorState{state=enter,position=new Vector3(240,70,0)},new ChildAnimatorState{state=crouch,position=new Vector3(520,70,0)},new ChildAnimatorState{state=sprint,position=new Vector3(520,280,0)},new ChildAnimatorState{state=exit,position=new Vector3(800,70,0)}};
 crouching.defaultState=enter;crouching.entryPosition=new Vector3(10,70,0);crouching.anyStatePosition=new Vector3(10,-70,0);crouching.exitPosition=new Vector3(1080,70,0);
 root.states=new[]{new ChildAnimatorState{state=find("Player_Jump"),position=new Vector3(550,40,0)},new ChildAnimatorState{state=find("Player_Land"),position=new Vector3(850,40,0)},new ChildAnimatorState{state=find("Player_Pickup"),position=new Vector3(550,-180,0)}};
 root.defaultState=null;root.AddEntryTransition(standing);root.entryPosition=new Vector3(10,40,0);root.anyStatePosition=new Vector3(250,-180,0);root.exitPosition=new Vector3(850,290,0);
 foreach(var o in new UnityEngine.Object[]{root,standing,crouching,c,sprint,crouch})EditorUtility.SetDirty(o);AssetDatabase.SaveAssetIfDirty(c);Selection.activeObject=c;AssetDatabase.OpenAsset(c);
 return new{rootStates=root.states.Select(x=>x.state.name).ToArray(),groups=root.stateMachines.Select(x=>new{name=x.stateMachine.name,states=x.stateMachine.states.Select(s=>s.state.name).ToArray()}).ToArray(),forwardSprintGuard="IsCrouch && IsMoving && IsSprint && MoveY > 0.001",note="Preserves the current forward-input rule, including forward diagonals."};
 }
}
