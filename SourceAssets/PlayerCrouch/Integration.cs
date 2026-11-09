using System;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine.SceneManagement;
using UnityEngine.InputSystem;
public static class AS_CrouchIntegration {
 const string ControllerPath="Assets/Afrer_Seconds/07.Animator/Player/Controllers/Player_Animator_Blend.controller";
 const string PrefabPath="Assets/Afrer_Seconds/05.Model/Player/Player_Dummy_V0.1.prefab";
 public static object VerifySavedPlayer(){
 var scene=UnityEditor.SceneManagement.EditorSceneManager.OpenPreviewScene("Assets/Afrer_Seconds/01.Scenes/Player.unity");
 try{
 var rows=scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<PlayerAnimationSystem>(true)).Select(b=>{var a=(Animator)new SerializedObject(b).FindProperty("animator").objectReferenceValue;return new{player=PathOf(b.transform),controller=AssetDatabase.GetAssetPath(a.runtimeAnimatorController),a.applyRootMotion};}).ToArray();
 if(rows.Length==0||rows.Any(r=>r.controller!=ControllerPath||r.applyRootMotion))throw new Exception("Saved Player scene controller mismatch");
 return new{playerScene=rows,devices=InputSystem.devices.Select(d=>new{d.name,d.enabled}).ToArray(),current=Inspect()};
 }finally{UnityEditor.SceneManagement.EditorSceneManager.ClosePreviewScene(scene);}
 }
 public static object PlayStatus()=>new{Time.frameCount,Time.time,Time.timeScale,tests=AppDomain.CurrentDomain.GetAssemblies().Select(a=>a.GetType("AS_CrouchIntegrationPlay")).Where(t=>t!=null).Select(t=>new{assembly=t.Assembly.FullName,step=t.GetField("step",System.Reflection.BindingFlags.Static|System.Reflection.BindingFlags.NonPublic).GetValue(null),stageTime=t.GetField("stageTime",System.Reflection.BindingFlags.Static|System.Reflection.BindingFlags.NonPublic).GetValue(null)}).ToArray()};
 public static object Apply(){
 if(EditorApplication.isPlaying)throw new Exception("Edit mode required");
 var c=AssetDatabase.LoadAssetAtPath<AnimatorController>(ControllerPath);
 if(!c)throw new Exception("Blend controller missing");
 foreach(var s in c.layers[0].stateMachine.states.Where(s=>s.state.name=="Standing"||s.state.name=="Crouching"))
 foreach(var t in s.state.transitions.Where(t=>t.destinationState&&(t.destinationState.name=="Standing"||t.destinationState.name=="Crouching"))){
 t.hasExitTime=false;t.duration=.28f;t.hasFixedDuration=true;
 // Only the destination's reverse stance transition may interrupt this blend.
 // Rechecking the source with unordered interruption can restart the same blend forever.
 t.interruptionSource=TransitionInterruptionSource.Destination;t.orderedInterruption=false;
 EditorUtility.SetDirty(t);
 }
 AssetDatabase.SaveAssetIfDirty(c);
 var root=PrefabUtility.LoadPrefabContents(PrefabPath);
 try {
 var bridge=root.GetComponent<PlayerAnimationSystem>();
 var animator=(Animator)new SerializedObject(bridge).FindProperty("animator").objectReferenceValue;
 if(!animator||!animator.avatar||!animator.avatar.isHuman)throw new Exception("Player animator/avatar missing");
 animator.runtimeAnimatorController=c;animator.applyRootMotion=false;
 PrefabUtility.RecordPrefabInstancePropertyModifications(animator);
 PrefabUtility.SaveAsPrefabAsset(root,PrefabPath);
 }finally{PrefabUtility.UnloadPrefabContents(root);}
 return Inspect();
 }
 static string PathOf(Transform t)=>t.parent?PathOf(t.parent)+"/"+t.name:t.name;
 public static object Inspect(){
 return new {
 playing=EditorApplication.isPlaying,
 scenes=Enumerable.Range(0,SceneManager.sceneCount).Select(i=>{var s=SceneManager.GetSceneAt(i);return new{s.path,s.isDirty};}).ToArray(),
 players=UnityEngine.Object.FindObjectsByType<PlayerPresenter>(FindObjectsInactive.Include,FindObjectsSortMode.None).Select(p=>{
 var a=p.GetComponent<PlayerAnimationSystem>();var motor=p.GetComponent<PlayerMotor>();var look=p.GetComponent<PlayerLook>();var cc=p.GetComponent<CharacterController>();var input=p.GetComponent<PlayerInput>();
 var aa=a?new SerializedObject(a).FindProperty("animator").objectReferenceValue as Animator:null;
 var settings=motor?new SerializedObject(motor).FindProperty("settings").objectReferenceValue as PlayerMotorSettings:null;
 var camera=look?new SerializedObject(look).FindProperty("cameraRoot").objectReferenceValue as Transform:null;
 return new{path=PathOf(p.transform),p.gameObject.activeInHierarchy,prefab=PrefabUtility.GetPrefabAssetPathOfNearestInstanceRoot(p.gameObject),animator=aa?PathOf(aa.transform):null,controller=aa?AssetDatabase.GetAssetPath(aa.runtimeAnimatorController):null,rootMotion=aa&&aa.applyRootMotion,avatar=aa?AssetDatabase.GetAssetPath(aa.avatar):null,height=cc?cc.height:0,center=cc?cc.center.ToString():null,camera=camera?PathOf(camera):null,cameraPosition=camera?camera.localPosition.ToString():null,settings=settings?new{path=AssetDatabase.GetAssetPath(settings),settings.MoveSpeed,settings.SprintSpeed,settings.CrouchSpeed,settings.CrouchSprintSpeed,settings.CrouchHeight}:null,input=input?new{input.notificationBehavior,input.defaultActionMap,actions=AssetDatabase.GetAssetPath(input.actions),events=input.actionEvents.Select(e=>new{e.actionName,callbacks=Enumerable.Range(0,e.GetPersistentEventCount()).Select(i=>e.GetPersistentMethodName(i)).ToArray()}).ToArray()}:null};
 }).ToArray(),
 prefabs=AssetDatabase.FindAssets("Player t:Prefab").Select(AssetDatabase.GUIDToAssetPath).ToArray()
 };
 }
}
