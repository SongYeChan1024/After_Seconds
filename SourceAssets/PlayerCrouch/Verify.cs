using System;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine.Animations;
using UnityEngine.Playables;
public static class AS_CrouchVerify {
 public static object Run(){
 string path="Assets/Afrer_Seconds/07.Animator/Player/Controllers/Player_Animator.controller";
 var c=AssetDatabase.LoadAssetAtPath<AnimatorController>(path);
 var tree=AssetDatabase.LoadAllAssetsAtPath(path).OfType<BlendTree>().Single(t=>t.name=="Crouch Direction");tree.blendType=BlendTreeType.SimpleDirectional2D;EditorUtility.SetDirty(tree);AssetDatabase.SaveAssetIfDirty(c);
 var preview=new PreviewRenderUtility();var graph=PlayableGraph.Create("CrouchControllerVerification");
 var rows=new System.Collections.Generic.List<object>();
 try{
 var go=preview.InstantiatePrefabInScene(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Afrer_Seconds/05.Model/Player/PlayerDummy_Rigged_V0.3.fbx"));var a=go.GetComponent<Animator>();a.runtimeAnimatorController=null;a.applyRootMotion=false;a.cullingMode=AnimatorCullingMode.AlwaysAnimate;
 graph.SetTimeUpdateMode(DirectorUpdateMode.Manual);var p=AnimatorControllerPlayable.Create(graph,c);var output=AnimationPlayableOutput.Create(graph,"Controller",a);output.SetSourcePlayable(p);graph.Play();
 Action<float> tick=seconds=>{for(int i=0;i<Mathf.CeilToInt(seconds*60);i++)graph.Evaluate(1/60f);};
 Action<string,string> check=(label,expected)=>{var s=p.GetCurrentAnimatorStateInfo(0);bool pass=s.IsName(expected)&&!p.IsInTransition(0);rows.Add(new{label,expected,pass,headY=a.GetBoneTransform(HumanBodyBones.Head).position.y,clips=p.GetCurrentAnimatorClipInfo(0).Select(x=>new{name=x.clip.name,x.weight}).ToArray()});if(!pass)throw new Exception(label+" did not reach "+expected);};
 tick(.2f);check("standing idle","Player_Idle");
 p.SetBool("IsMoving",true);tick(.5f);check("standing walk","Player_Walk");
 p.SetBool("IsSprint",true);tick(.5f);check("standing run","Player_Run");
 p.SetFloat("MoveY",1);p.SetBool("IsCrouch",true);tick(2.2f);check("run to crouch, sprint held","Player_Crouch_Sprint");
 p.SetFloat("MoveY",0);p.SetBool("IsMoving",false);tick(.5f);check("crouch idle","Player_Crouch");
 if(!p.GetCurrentAnimatorClipInfo(0).Any(x=>x.clip.name=="Player_Crouch_Idle"&&x.weight>.99f))throw new Exception("Center is not idle");
 p.SetBool("IsSprint",false);p.SetBool("IsMoving",true);tick(.5f);
 foreach(var d in new[]{new{name="Forward",x=0f,y=1f},new{name="Back",x=0f,y=-1f},new{name="Left",x=-1f,y=0f},new{name="Right",x=1f,y=0f},new{name="Diagonal",x=.7071f,y=.7071f}}){p.SetFloat("MoveX",d.x);p.SetFloat("MoveY",d.y);tick(.4f);check("crouch "+d.name,"Player_Crouch");var infos=p.GetCurrentAnimatorClipInfo(0);if(d.name!="Diagonal"&&!infos.Any(x=>x.clip.name=="Player_Crouch_"+d.name&&x.weight>.99f))throw new Exception("Wrong directional weights "+d.name);}
 p.SetBool("IsSprint",true);p.SetFloat("MoveX",0);p.SetFloat("MoveY",1);tick(.5f);check("crouch forward sprint","Player_Crouch_Sprint");
 p.SetFloat("MoveY",-1);tick(.5f);check("back cannot sprint","Player_Crouch");
 p.SetFloat("MoveX",1);p.SetFloat("MoveY",0);tick(.5f);check("strafe cannot sprint","Player_Crouch");
 p.SetFloat("MoveX",.7071f);p.SetFloat("MoveY",.7071f);tick(.5f);check("forward diagonal follows current input rule","Player_Crouch_Sprint");
 p.SetBool("IsCrouch",false);tick(2.2f);check("stand and resume sprint","Player_Run");
 p.SetBool("IsSprint",false);tick(.5f);p.SetBool("IsCrouch",true);tick(2.2f);p.SetBool("IsCrouch",false);tick(2.2f);check("stand and resume walk","Player_Walk");
 p.SetFloat("MoveX",0);p.SetFloat("MoveY",0);p.SetBool("IsMoving",false);tick(.5f);p.SetBool("IsCrouch",true);tick(2.2f);p.SetBool("IsCrouch",false);tick(2.2f);check("stand and remain idle","Player_Idle");
 p.SetBool("IsCrouch",true);tick(.3f);p.SetBool("IsCrouch",false);tick(2.2f);check("cancel crouch entry","Player_Idle");
 p.SetBool("IsCrouch",true);tick(2.2f);p.SetBool("IsCrouch",false);tick(.3f);p.SetBool("IsCrouch",true);tick(2.2f);check("cancel crouch exit","Player_Crouch");
 return new{passed=rows.Count,rows,playing=EditorApplication.isPlaying,activeScene=UnityEngine.SceneManagement.SceneManager.GetActiveScene().path,sceneDirty=UnityEngine.SceneManagement.SceneManager.GetActiveScene().isDirty};
 }finally{if(graph.IsValid())graph.Destroy();preview.Cleanup();}
 }
}
