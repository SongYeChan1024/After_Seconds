using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;
using Newtonsoft.Json;
public static class AS_CrouchIntegrationPlay {
 static readonly string Report=System.IO.Path.GetFullPath("../../SourceAssets/PlayerCrouch/integration_play.json");
 static GameObject room, player, ceiling;
 static Keyboard keyboard; static Mouse mouse;
 static PlayerMotor motor; static Animator animator; static Transform eye;
 static CharacterController capsule;
 static int startFrame,lastFrame,step; static float stageTime;
 static float initialEyeY,lastEyeY,maxEyeStep;
 static bool sawPoseTransition,sawWalkRunBlend;
 static List<object> rows=new List<object>();
 static List<object> errors=new List<object>();
 static bool[] autoSwitch; static PlayerInput[] previousInputs;
 static bool oldBackground;
 static Key[][] inputs={new Key[0],new[]{Key.C},new Key[0],new[]{Key.W},new[]{Key.W,Key.LeftShift},new[]{Key.S,Key.LeftShift},new[]{Key.A,Key.LeftShift},new[]{Key.D,Key.LeftShift},new Key[0],new[]{Key.C},new Key[0],new[]{Key.C},new Key[0],new[]{Key.C},new Key[0],new[]{Key.C},new Key[0],new[]{Key.C},new Key[0],new[]{Key.W},new[]{Key.W,Key.LeftShift},new Key[0],new[]{Key.C},new Key[0],new[]{Key.W},new[]{Key.W,Key.LeftShift},new[]{Key.S,Key.LeftShift},new Key[0]};
 static string[] labels={"standing idle","crouch press","crouch idle","crouch walk","crouch sprint","backward cannot sprint","left cannot sprint","right cannot sprint","stopped crouch","blocked stand press","blocked stand stays crouched","clear stand press","standing again","rapid crouch press","rapid release","rapid stand press","rapid release","rapid crouch press","rapid final crouch","crouch walk resumed","crouch sprint resumed","stopped final","stand press","standing settled","standing walk","standing sprint","standing backwards cannot sprint","standing stopped"};
 public static object Start(){
 if(!EditorApplication.isPlaying)throw new Exception("Enter Play mode first");
 oldBackground=Application.runInBackground;Application.runInBackground=true;
 previousInputs=UnityEngine.Object.FindObjectsByType<PlayerInput>(FindObjectsInactive.Include);autoSwitch=previousInputs.Select(x=>x.neverAutoSwitchControlSchemes).ToArray();foreach(var p in previousInputs)p.neverAutoSwitchControlSchemes=true;
 room=new GameObject("Crouch_Integration_Verification_RuntimeOnly");room.SetActive(false);room.transform.position=new Vector3(10000,100,10000);
 var floor=GameObject.CreatePrimitive(PrimitiveType.Cube);floor.transform.SetParent(room.transform,false);floor.transform.localPosition=new Vector3(0,-.1f,0);floor.transform.localScale=new Vector3(80,.2f,80);
 player=UnityEngine.Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Afrer_Seconds/05.Model/Player/Player_Dummy_V0.1.prefab"),room.transform);player.transform.localPosition=Vector3.up*.02f;player.transform.localRotation=Quaternion.identity;
 foreach(var c in player.GetComponentsInChildren<Camera>(true))c.enabled=false;foreach(var a in player.GetComponentsInChildren<AudioListener>(true))a.enabled=false;
 var bridge=player.GetComponent<PlayerAnimationSystem>();animator=(Animator)new SerializedObject(bridge).FindProperty("animator").objectReferenceValue;animator.cullingMode=AnimatorCullingMode.AlwaysAnimate;
 motor=player.GetComponent<PlayerMotor>();capsule=player.GetComponent<CharacterController>();eye=(Transform)new SerializedObject(player.GetComponent<PlayerLook>()).FindProperty("cameraRoot").objectReferenceValue;
 var pi=player.GetComponent<PlayerInput>();pi.neverAutoSwitchControlSchemes=true;
 keyboard=InputSystem.AddDevice<Keyboard>("AS_CrouchTestKeyboard");mouse=InputSystem.AddDevice<Mouse>("AS_CrouchTestMouse");
 room.SetActive(true);var scheme=pi.actions.controlSchemes.First(x=>x.deviceRequirements.Any(d=>d.controlPath=="<Keyboard>")).name;pi.SwitchCurrentControlScheme(scheme,keyboard,mouse);
 initialEyeY=eye.localPosition.y;lastEyeY=initialEyeY;maxEyeStep=0;startFrame=lastFrame=Time.frameCount;step=0;stageTime=Time.time;
 rows.Clear();errors.Clear();Application.logMessageReceived+=OnLog;EditorApplication.update+=Tick;
 Queue();return new{started=true,frame=startFrame,scheme,controller=animator.runtimeAnimatorController.name,report=Report};
 }
 static void OnLog(string message,string stack,LogType type){if(type==LogType.Error||type==LogType.Exception||type==LogType.Assert)errors.Add(new{message,stack,type=type.ToString()});}
 static void Queue(){InputSystem.QueueStateEvent(keyboard,new KeyboardState(inputs[step]));}
 static void Check(bool ok,string reason){if(!ok)throw new Exception(labels[step]+": "+reason);}
 static void Tick(){
 if(!EditorApplication.isPlaying){Finish("Play mode interrupted");return;}
 EditorApplication.QueuePlayerLoopUpdate();if(Time.frameCount==lastFrame)return;lastFrame=Time.frameCount;
 try{
 maxEyeStep=Mathf.Max(maxEyeStep,Mathf.Abs(eye.localPosition.y-lastEyeY));lastEyeY=eye.localPosition.y;
 if(animator.IsInTransition(0))sawPoseTransition=true;
 var clips=animator.GetCurrentAnimatorClipInfo(0).Where(c=>c.weight>.01f).ToArray();if(clips.Any(x=>x.clip.name.Contains("Forward"))&&clips.Any(x=>x.clip.name.Contains("Sprint")))sawWalkRunBlend=true;
 float wait=(step==1||step==9||step==11||step==13||step==14||step==15||step==16||step==17)?.07f:.65f;
 if(Time.time-stageTime<wait)return;
 bool expectedCrouch=step!=0&&step!=11&&step!=12&&step!=15&&step!=16&&step<22;
 if(step==1||step==9||step==11||step==13||step==15||step==17){Check(motor.IsCrouching==expectedCrouch,"toggle/Motor mismatch");Check(animator.GetBool("IsCrouch")==expectedCrouch,"Animator stance differs from Motor");}
 if(new[]{0,2,3,4,5,6,7,8,10,12,18,19,20,21,22,23,24,25,26,27}.Contains(step)){
 Check(motor.IsCrouching==expectedCrouch,"wrong Motor stance");Check(animator.GetCurrentAnimatorStateInfo(0).IsName(expectedCrouch?"Crouching":"Standing"),"wrong Animator state");
 float speed=(step==4||step==20||step==25)?2:(new[]{3,5,6,7,19,24,26}.Contains(step)?1:0);
 Check(Mathf.Abs(animator.GetFloat("Speed")-speed)<.04f,"wrong blended Speed");
 Check(Mathf.Abs(capsule.height-(expectedCrouch?1.2f:1.8f))<.01f,"wrong capsule height");
 Check(Mathf.Abs(eye.localPosition.y-(initialEyeY-(expectedCrouch?.6f:0)))<.015f,"eye has not reached posture");
 if(step==5)Check(clips.Any(x=>x.clip.name=="Player_Crouch_Back"&&x.weight>.9f),"backward clip missing");
 if(step==6)Check(clips.Any(x=>x.clip.name=="Player_Crouch_Left"&&x.weight>.9f),"left clip missing");
 if(step==7)Check(clips.Any(x=>x.clip.name=="Player_Crouch_Right"&&x.weight>.9f),"right clip missing");
 }
 rows.Add(new{label=labels[step],frame=Time.frameCount,crouching=motor.IsCrouching,height=capsule.height,eyeY=eye.localPosition.y,speed=animator.GetFloat("Speed"),transition=animator.IsInTransition(0),clips=clips.Select(x=>new{name=x.clip.name,x.weight}).ToArray()});
 if(step==8){ceiling=GameObject.CreatePrimitive(PrimitiveType.Cube);ceiling.transform.position=player.transform.position+Vector3.up*1.5f;ceiling.transform.localScale=new Vector3(3,.1f,3);ceiling.transform.SetParent(room.transform,true);Physics.SyncTransforms();}
 if(step==10){UnityEngine.Object.DestroyImmediate(ceiling);Physics.SyncTransforms();}
 step++;if(step==inputs.Length){Check(sawPoseTransition,"no posture blend observed");Check(sawWalkRunBlend,"no walking/running blend observed");Finish(null);return;}
 stageTime=Time.time;Queue();
 }catch(Exception ex){Finish(ex.ToString());}
 }
 static void Finish(string failure){
 EditorApplication.update-=Tick;Application.logMessageReceived-=OnLog;
 File.WriteAllText(Report,JsonConvert.SerializeObject(new{success=failure==null&&errors.Count==0,failure,frames=Time.frameCount-startFrame,passed=rows.Count,rows,sawPoseTransition,sawWalkRunBlend,maxEyeStep,errors,lastState=animator?new{current=animator.GetCurrentAnimatorStateInfo(0).shortNameHash,next=animator.GetNextAnimatorStateInfo(0).shortNameHash,transition=animator.IsInTransition(0),transitionTime=animator.GetAnimatorTransitionInfo(0).normalizedTime}:null},Formatting.Indented));
 if(keyboard!=null&&keyboard.added)InputSystem.RemoveDevice(keyboard);if(mouse!=null&&mouse.added)InputSystem.RemoveDevice(mouse);
 if(room)UnityEngine.Object.Destroy(room);for(int i=0;i<previousInputs.Length;i++)if(previousInputs[i])previousInputs[i].neverAutoSwitchControlSchemes=autoSwitch[i];
 Application.runInBackground=oldBackground;
 }
}
