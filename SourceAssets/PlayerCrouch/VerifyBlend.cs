using System;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine.Animations;
using UnityEngine.Playables;
public static class AS_VerifyBlend {
 public static object Run(){
 var c=AssetDatabase.LoadAssetAtPath<AnimatorController>("Assets/Afrer_Seconds/07.Animator/Player/Controllers/Player_Animator_Blend.controller");
 var preview=new PreviewRenderUtility();var graph=PlayableGraph.Create("TwoLocomotionTrees");var rows=new System.Collections.Generic.List<object>();
 try{var go=preview.InstantiatePrefabInScene(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Afrer_Seconds/05.Model/Player/PlayerDummy_Rigged_V0.3.fbx"));var a=go.GetComponent<Animator>();a.runtimeAnimatorController=null;a.applyRootMotion=false;a.cullingMode=AnimatorCullingMode.AlwaysAnimate;
 graph.SetTimeUpdateMode(DirectorUpdateMode.Manual);var p=AnimatorControllerPlayable.Create(graph,c);var output=AnimationPlayableOutput.Create(graph,"pose",a);output.SetSourcePlayable(p);graph.Play();
 Action tick=()=>{for(int i=0;i<36;i++)graph.Evaluate(1/60f);};
 foreach(bool low in new[]{false,true}){
 p.SetBool("IsCrouch",low);p.SetFloat("MoveX",0);p.SetFloat("MoveY",1);
 foreach(float speed in new[]{0f,1f,1.5f,2f}){p.SetFloat("Speed",speed);tick();var info=p.GetCurrentAnimatorStateInfo(0);if(!info.IsName(low?"Crouching":"Standing"))throw new Exception("Wrong stance");var clips=p.GetCurrentAnimatorClipInfo(0).Where(x=>x.weight>.001f).Select(x=>new{name=x.clip.name,x.weight}).ToArray();if(speed==1.5f&&(clips.Length!=2||clips.Any(x=>Mathf.Abs(x.weight-.5f)>.001f)))throw new Exception("Expected 50/50 walk-run blend");rows.Add(new{stance=low?"Crouching":"Standing",speed,clips});}
 }
 // Test the agreed parameter contract; gameplay input code is intentionally not changed.
 foreach(var d in new[]{new{name="forward",x=0f,y=1f},new{name="backward",x=0f,y=-1f},new{name="left",x=-1f,y=0f},new{name="right",x=1f,y=0f},new{name="forward diagonal",x=.7071f,y=.7071f}}){bool eligible=d.y>0;p.SetBool("IsCrouch",true);p.SetFloat("MoveX",d.x);p.SetFloat("MoveY",d.y);p.SetFloat("Speed",eligible?2:1);tick();var clips=p.GetCurrentAnimatorClipInfo(0).Where(x=>x.weight>.001f).Select(x=>new{name=x.clip.name,x.weight}).ToArray();bool actual=clips.Any(x=>x.name=="Player_Crouch_Sprint");if(actual!=eligible)throw new Exception("Wrong sprint resolution");rows.Add(new{direction=d.name,sprintEligible=eligible,clips});}
 p.SetFloat("Speed",0);p.SetBool("IsCrouch",false);tick();if(!p.GetCurrentAnimatorStateInfo(0).IsName("Standing"))throw new Exception("Standing return failed");
 return new{passed=rows.Count+1,rows,codeScope="External preview verification only; user runtime scripts untouched.",sceneDirty=UnityEngine.SceneManagement.SceneManager.GetActiveScene().isDirty};
 }finally{if(graph.IsValid())graph.Destroy();preview.Cleanup();}
 }
}
