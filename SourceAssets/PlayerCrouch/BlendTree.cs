using System;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
public static class AS_CrouchBlendTree {
 public static object Run(){
 string path="Assets/Afrer_Seconds/07.Animator/Player/Controllers/Player_Animator.controller";
 var c=AssetDatabase.LoadAssetAtPath<AnimatorController>(path);var sm=c.layers[0].stateMachine;
 var crouch=sm.states.Single(x=>x.state.name=="Player_Crouch").state;
 var enter=sm.states.Single(x=>x.state.name=="Player_Crouch_Enter").state;
 var move=sm.states.FirstOrDefault(x=>x.state.name=="Player_Crouch_Walk").state;
 var tree=AssetDatabase.LoadAllAssetsAtPath(path).OfType<BlendTree>().FirstOrDefault(x=>x&&x.name=="Crouch Direction");
 if(!tree){tree=new BlendTree{name="Crouch Direction",blendType=BlendTreeType.SimpleDirectional2D,blendParameter="MoveX",blendParameterY="MoveY"};AssetDatabase.AddObjectToAsset(tree,c);foreach(var item in new[]{new{n="Forward",p=new Vector2(0,1)},new{n="Back",p=new Vector2(0,-1)},new{n="Left",p=new Vector2(-1,0)},new{n="Right",p=new Vector2(1,0)}})tree.AddChild(AssetDatabase.LoadAssetAtPath<AnimationClip>("Assets/Afrer_Seconds/07.Animator/Player/Clips/Crouch/Player_Crouch_"+item.n+".anim"),item.p);}
 if(!tree.children.Any(x=>x.position==Vector2.zero))tree.AddChild(AssetDatabase.LoadAssetAtPath<AnimationClip>("Assets/Afrer_Seconds/07.Animator/Player/Clips/Crouch/Player_Crouch_Idle.anim"),Vector2.zero);
 crouch.motion=tree;
 if(move){foreach(var t in crouch.transitions.Where(t=>t.destinationState==move).ToArray())crouch.RemoveTransition(t);foreach(var t in enter.transitions.Where(t=>t.destinationState==move).ToArray())enter.RemoveTransition(t);move.motion=null;sm.RemoveState(move);if(move)UnityEngine.Object.DestroyImmediate(move,true);}
 foreach(var t in enter.transitions.Where(t=>t.destinationState==crouch)){foreach(var condition in t.conditions.Where(x=>x.parameter=="IsMoving").ToArray())t.RemoveCondition(condition);EditorUtility.SetDirty(t);}
 var parameters=c.parameters;foreach(var p in parameters.Where(p=>p.name=="MoveX"||p.name=="MoveY"))p.defaultFloat=0;c.parameters=parameters;
 var childStates=sm.states;for(int i=0;i<childStates.Length;i++){if(childStates[i].state==crouch)childStates[i].position=new Vector3(800,380,0);}sm.states=childStates;
 EditorUtility.SetDirty(crouch);EditorUtility.SetDirty(enter);EditorUtility.SetDirty(tree);EditorUtility.SetDirty(sm);EditorUtility.SetDirty(c);AssetDatabase.SaveAssetIfDirty(c);
 return new{state=crouch.name,tree=tree.name,children=tree.children.Select(x=>new{name=x.motion.name,x=x.position.x,y=x.position.y}).ToArray(),states=sm.states.Select(x=>x.state.name).ToArray()};
 }
}
