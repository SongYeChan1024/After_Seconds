using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEngine.Animations;
using UnityEngine.Playables;
public static class AS_CrouchPreview
{
    public static object Run()=>Render(false);
    public static object SprintRaw()=>Render(true);
    static object Render(bool sprintRaw)
    {
        string output=Path.GetFullPath(Path.Combine(Application.dataPath,"../../../SourceAssets/PlayerCrouch/Preview"));
        Directory.CreateDirectory(output);
        var result=new System.Collections.Generic.List<object>();
        var model=AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Afrer_Seconds/05.Model/Player/PlayerDummy_Rigged_V0.3.fbx");
        foreach(var name in sprintRaw?new[]{"Sprint_Raw"}:new[]{"Idle","Forward","Back","Left","Right","Stand","Enter","Standing"})
        {
            var clip=AssetDatabase.LoadAllAssetsAtPath(name=="Sprint_Raw"?"Assets/Afrer_Seconds/07.Animator/Player/Clips/Crouch/Player_Crouch_Sprint.fbx":name=="Standing"?"Assets/Afrer_Seconds/07.Animator/Player/Clips/Rigged_V0.3/Player_Idle.fbx":"Assets/Afrer_Seconds/07.Animator/Player/Clips/Crouch/Player_Crouch_"+name+".anim").OfType<AnimationClip>().Single(x=>!x.name.StartsWith("__preview__"));
            var preview=new PreviewRenderUtility();var graph=PlayableGraph.Create("CrouchPreview");
            try {
                var go=preview.InstantiatePrefabInScene(model);
                go.transform.SetPositionAndRotation(new Vector3(0,sprintRaw?0:.7750726f,0),Quaternion.identity);
                var a=go.GetComponent<Animator>();a.applyRootMotion=false;a.runtimeAnimatorController=null;a.cullingMode=AnimatorCullingMode.AlwaysAnimate;
                graph.SetTimeUpdateMode(DirectorUpdateMode.Manual);
                var playable=AnimationClipPlayable.Create(graph,clip);playable.SetApplyFootIK(false);
                var animOutput=AnimationPlayableOutput.Create(graph,"Pose",a);animOutput.SetSourcePlayable(playable);graph.Play();
                var samples=new System.Collections.Generic.List<object>();
                foreach(var t in new[]{0.0f,clip.length*.25f,clip.length*.5f,clip.length*.75f,clip.length-.001f}) {
                    playable.SetTime(t);graph.Evaluate(.00001f);
                    Func<HumanBodyBones,float[]> pos=b=>{var v=go.transform.InverseTransformPoint(a.GetBoneTransform(b).position);return new[]{v.x,v.y,v.z};};
                    samples.Add(new{t,hips=pos(HumanBodyBones.Hips),head=pos(HumanBodyBones.Head),leftFoot=pos(HumanBodyBones.LeftFoot),rightFoot=pos(HumanBodyBones.RightFoot),leftHand=pos(HumanBodyBones.LeftHand),rightHand=pos(HumanBodyBones.RightHand)});
                }
                preview.camera.transform.position=new Vector3(1.5f,1.3f,2.0f);
                preview.camera.transform.LookAt(new Vector3(0,.5f,0));
                preview.camera.nearClipPlane=.05f;preview.camera.farClipPlane=20;
                preview.camera.fieldOfView=31;preview.camera.clearFlags=CameraClearFlags.SolidColor;preview.camera.backgroundColor=new Color(.12f,.14f,.17f);
                preview.lights[0].intensity=1.3f;preview.lights[0].transform.rotation=Quaternion.Euler(40,35,0);
                preview.lights[1].intensity=1.1f;preview.lights[1].transform.rotation=Quaternion.Euler(20,210,0);
                preview.ambientColor=new Color(.4f,.4f,.4f);
                foreach(var index in new[]{0,1,2}) {
                    float t=(index==0?0:index==1?clip.length*.5f:clip.length-.001f);
                    playable.SetTime(t);graph.Evaluate(.00001f);
                    var bakedObjects=new System.Collections.Generic.List<GameObject>();
                    var bakedMeshes=new System.Collections.Generic.List<Mesh>();
                    foreach(var skin in go.GetComponentsInChildren<SkinnedMeshRenderer>()) {
                        var mesh=new Mesh();skin.BakeMesh(mesh);bakedMeshes.Add(mesh);
                        var frozen=new GameObject("FrozenPose");preview.AddSingleGO(frozen);
                        frozen.transform.SetPositionAndRotation(skin.transform.position,skin.transform.rotation);
                        frozen.transform.localScale=skin.transform.lossyScale;
                        frozen.AddComponent<MeshFilter>().sharedMesh=mesh;
                        frozen.AddComponent<MeshRenderer>().sharedMaterials=skin.sharedMaterials;
                        bakedObjects.Add(frozen);
                    }
                    go.SetActive(false);
                    preview.BeginStaticPreview(new Rect(0,0,520,700));preview.Render(true);
                    var texture=preview.EndStaticPreview();File.WriteAllBytes(Path.Combine(output,name+"_"+index+".png"),texture.EncodeToPNG());UnityEngine.Object.DestroyImmediate(texture);
                    foreach(var obj in bakedObjects) UnityEngine.Object.DestroyImmediate(obj);
                    foreach(var mesh in bakedMeshes) UnityEngine.Object.DestroyImmediate(mesh);
                    go.SetActive(true);
                }
                result.Add(new{name,clip.length,samples});
            } finally {if(graph.IsValid())graph.Destroy();preview.Cleanup();}
        }
        return new{output,result};
    }
}
