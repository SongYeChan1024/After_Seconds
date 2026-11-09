using System;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine.Animations;
using UnityEngine.Playables;
public static class AS_CrouchBakeFloor {
 const string Folder="Assets/Afrer_Seconds/07.Animator/Player/Clips/Crouch";
 static AnimationClip Load(string path)=>AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>().Single(c=>!c.name.StartsWith("__preview__"));
 static float Bottom(GameObject go){float y=float.PositiveInfinity;foreach(var skin in go.GetComponentsInChildren<SkinnedMeshRenderer>()){var m=new Mesh();skin.BakeMesh(m);foreach(var v in m.vertices)y=Mathf.Min(y,go.transform.InverseTransformPoint(skin.transform.TransformPoint(v)).y);UnityEngine.Object.DestroyImmediate(m);}return y;}
 static void SaveClip(AnimationClip clip,string path){var existing=AssetDatabase.LoadAssetAtPath<AnimationClip>(path);if(existing){EditorUtility.CopySerialized(clip,existing);UnityEngine.Object.DestroyImmediate(clip);EditorUtility.SetDirty(existing);AssetDatabase.SaveAssetIfDirty(existing);}else AssetDatabase.CreateAsset(clip,path);}
 public static object Run()=>Bake(false);
 public static object Sprint()=>Bake(true);
 static object Bake(bool sprintOnly){
 var names=sprintOnly?new[]{"Sprint"}:new[]{"Idle","Forward","Back","Left","Right","Stand"};
 foreach(var n in names){var importer=(ModelImporter)AssetImporter.GetAtPath(Folder+"/Player_Crouch_"+n+".fbx");var def=importer.clipAnimations[0];def.heightOffset=0;def.keepOriginalPositionY=true;def.heightFromFeet=false;importer.clipAnimations=new[]{def};importer.SaveAndReimport();}
 var preview=new PreviewRenderUtility();var graph=PlayableGraph.Create("CrouchFloorCalibration");var rows=new System.Collections.Generic.List<object>();
 try{
 var go=preview.InstantiatePrefabInScene(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Afrer_Seconds/05.Model/Player/PlayerDummy_Rigged_V0.3.fbx"));var a=go.GetComponent<Animator>();a.runtimeAnimatorController=null;a.applyRootMotion=false;a.cullingMode=AnimatorCullingMode.AlwaysAnimate;
 graph.SetTimeUpdateMode(DirectorUpdateMode.Manual);var output=AnimationPlayableOutput.Create(graph,"Pose",a);graph.Play();
 var baseline=AnimationClipPlayable.Create(graph,Load("Assets/Afrer_Seconds/07.Animator/Player/Clips/Rigged_V0.3/Player_Idle.fbx"));baseline.SetApplyFootIK(false);output.SetSourcePlayable(baseline);baseline.SetTime(.5);graph.Evaluate(.00001f);float ground=Bottom(go);baseline.Destroy();
 var binding=EditorCurveBinding.FloatCurve("",typeof(Animator),"RootT.y");
 foreach(var name in names){
 var src=Load(Folder+"/Player_Crouch_"+name+(sprintOnly?"_UnarmedSource.anim":".fbx"));var dst=new AnimationClip{name="Player_Crouch_"+name,frameRate=src.frameRate,legacy=false};
 foreach(var b in AnimationUtility.GetCurveBindings(src))AnimationUtility.SetEditorCurve(dst,b,AnimationUtility.GetEditorCurve(src,b));
 var curve=AnimationUtility.GetEditorCurve(src,binding);if(curve==null)throw new Exception("Missing RootT.y");
 var p=AnimationClipPlayable.Create(graph,src);p.SetApplyFootIK(false);output.SetSourcePlayable(p);var keys=new System.Collections.Generic.List<Keyframe>();
 int count=Mathf.RoundToInt(src.length*30);
 for(int i=0;i<=count;i++){float t=Mathf.Min(i/30f,src.length-.00001f);p.SetTime(t);graph.Evaluate(.00001f);float delta=ground-Bottom(go);keys.Add(new Keyframe(i==count?src.length:t,curve.Evaluate(t)+delta/a.humanScale));}
 p.Destroy();var aligned=new AnimationCurve(keys.ToArray());for(int i=0;i<aligned.length;i++){AnimationUtility.SetKeyLeftTangentMode(aligned,i,AnimationUtility.TangentMode.Linear);AnimationUtility.SetKeyRightTangentMode(aligned,i,AnimationUtility.TangentMode.Linear);}AnimationUtility.SetEditorCurve(dst,binding,aligned);
 var settings=AnimationUtility.GetAnimationClipSettings(src);settings.loopBlendPositionY=true;AnimationUtility.SetAnimationClipSettings(dst,settings);SaveClip(dst,Folder+"/Player_Crouch_"+name+".anim");
 var saved=AssetDatabase.LoadAssetAtPath<AnimationClip>(Folder+"/Player_Crouch_"+name+".anim");var test=AnimationClipPlayable.Create(graph,saved);test.SetApplyFootIK(false);output.SetSourcePlayable(test);float maxError=0;float head=0;
 for(int i=0;i<10;i++){test.SetTime(saved.length*i/10f);graph.Evaluate(.00001f);maxError=Mathf.Max(maxError,Mathf.Abs(Bottom(go)-ground));head=a.GetBoneTransform(HumanBodyBones.Head).position.y;}
 test.Destroy();rows.Add(new{name,ground,maxError,headY=head});if(maxError>.025f)throw new Exception("Floor calibration failed "+name+" error "+maxError);
 }
 if(sprintOnly)return new{ground,rows};
 var stand=AssetDatabase.LoadAssetAtPath<AnimationClip>(Folder+"/Player_Crouch_Stand.anim");var down=UnityEngine.Object.Instantiate(stand);down.name="Player_Crouch_Enter";
 foreach(var b in AnimationUtility.GetCurveBindings(stand)){var c=AnimationUtility.GetEditorCurve(stand,b);var k=c.keys.Reverse().Select(x=>new Keyframe(stand.length-x.time,x.value,-x.outTangent,-x.inTangent,x.outWeight,x.inWeight){weightedMode=x.weightedMode==WeightedMode.In?WeightedMode.Out:x.weightedMode==WeightedMode.Out?WeightedMode.In:x.weightedMode}).ToArray();AnimationUtility.SetEditorCurve(down,b,new AnimationCurve(k));}SaveClip(down,Folder+"/Player_Crouch_Enter.anim");
 string controllerPath="Assets/Afrer_Seconds/07.Animator/Player/Controllers/Player_Animator.controller";var controller=AssetDatabase.LoadAssetAtPath<AnimatorController>(controllerPath);
 foreach(var s in controller.layers[0].stateMachine.states){if(s.state.name.StartsWith("Player_Crouch")){s.state.iKOnFeet=false;if(s.state.name!="Player_Crouch_Walk"){string n=s.state.name=="Player_Crouch"?"Idle":s.state.name=="Player_Crouch_Exit"?"Stand":"Enter";s.state.motion=AssetDatabase.LoadAssetAtPath<AnimationClip>(Folder+"/Player_Crouch_"+n+".anim");}EditorUtility.SetDirty(s.state);}}
 var tree=AssetDatabase.LoadAllAssetsAtPath(controllerPath).OfType<BlendTree>().Single(x=>x.name=="Crouch Direction");var children=tree.children;for(int i=0;i<children.Length;i++)children[i].motion=AssetDatabase.LoadAssetAtPath<AnimationClip>(Folder+"/"+children[i].motion.name+".anim");tree.children=children;EditorUtility.SetDirty(tree);EditorUtility.SetDirty(controller);AssetDatabase.SaveAssetIfDirty(controller);
 return new{ground,rows};
 }finally{if(graph.IsValid())graph.Destroy();preview.Cleanup();}
 }
}
