using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEngine.Animations;
using UnityEngine.Playables;
public static class AS_PreviewBlend {
 public static object Run(){
 var output=Path.GetFullPath("../../SourceAssets/PlayerCrouch/Preview");
 var files=new System.Collections.Generic.List<string>();
 foreach(var sample in new[]{new{name="Blend_Standing",frames=0,speed=0f},new{name="Blend_Middle",frames=8,speed=0f},new{name="Blend_Crouched",frames=30,speed=0f},new{name="Blend_CrouchRun",frames=60,speed=2f}}){
 var preview=new PreviewRenderUtility();var graph=PlayableGraph.Create("CrouchBlendPreview");var meshes=new System.Collections.Generic.List<Mesh>();
 try{
 var go=preview.InstantiatePrefabInScene(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Afrer_Seconds/05.Model/Player/PlayerDummy_Rigged_V0.3.fbx"));go.transform.position=Vector3.up*.7750726f;
 var animator=go.GetComponent<Animator>();animator.runtimeAnimatorController=null;animator.applyRootMotion=false;animator.cullingMode=AnimatorCullingMode.AlwaysAnimate;
 graph.SetTimeUpdateMode(DirectorUpdateMode.Manual);var controller=AnimatorControllerPlayable.Create(graph,AssetDatabase.LoadAssetAtPath<RuntimeAnimatorController>("Assets/Afrer_Seconds/07.Animator/Player/Controllers/Player_Animator_Blend.controller"));var o=AnimationPlayableOutput.Create(graph,"Pose",animator);o.SetSourcePlayable(controller);graph.Play();for(int i=0;i<30;i++)graph.Evaluate(1/60f);
 controller.SetBool("IsCrouch",true);controller.SetFloat("Speed",sample.speed);controller.SetFloat("MoveY",1);for(int i=0;i<sample.frames;i++)graph.Evaluate(1/60f);
 foreach(var skin in go.GetComponentsInChildren<SkinnedMeshRenderer>()){var mesh=new Mesh();skin.BakeMesh(mesh);meshes.Add(mesh);var frozen=new GameObject("Pose");preview.AddSingleGO(frozen);frozen.transform.SetPositionAndRotation(skin.transform.position,skin.transform.rotation);frozen.transform.localScale=skin.transform.lossyScale;frozen.AddComponent<MeshFilter>().sharedMesh=mesh;frozen.AddComponent<MeshRenderer>().sharedMaterials=skin.sharedMaterials;}
 go.SetActive(false);
 preview.camera.transform.position=new Vector3(1.5f,1.3f,2);preview.camera.transform.LookAt(new Vector3(0,.5f,0));preview.camera.nearClipPlane=.05f;preview.camera.farClipPlane=20;preview.camera.fieldOfView=31;preview.camera.clearFlags=CameraClearFlags.SolidColor;preview.camera.backgroundColor=new Color(.12f,.14f,.17f);
 preview.lights[0].intensity=1.3f;preview.lights[0].transform.rotation=Quaternion.Euler(40,35,0);preview.lights[1].intensity=1.1f;preview.lights[1].transform.rotation=Quaternion.Euler(20,210,0);preview.ambientColor=new Color(.4f,.4f,.4f);
 preview.BeginStaticPreview(new Rect(0,0,420,560));preview.Render(true);var texture=preview.EndStaticPreview();var file=Path.Combine(output,sample.name+".png");File.WriteAllBytes(file,texture.EncodeToPNG());UnityEngine.Object.DestroyImmediate(texture);files.Add(file);
 }finally{if(graph.IsValid())graph.Destroy();preview.Cleanup();foreach(var m in meshes)UnityEngine.Object.DestroyImmediate(m);}
 }
 return new{files};
 }
}
