if (Application.isPlaying) throw new System.Exception("Edit mode required");
const string path="Assets/Afrer_Seconds/07.Animator/Player/Clips/VarcoFirstPerson/Player_Overhand_Varco.fbx";
AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
var importer=(ModelImporter)AssetImporter.GetAtPath(path);
importer.animationType=ModelImporterAnimationType.Human;
importer.avatarSetup=ModelImporterAvatarSetup.CreateFromThisModel;
importer.importAnimation=true;importer.materialImportMode=ModelImporterMaterialImportMode.None;
importer.animationCompression=ModelImporterAnimationCompression.Off;importer.SaveAndReimport();
var def=importer.defaultClipAnimations.Single();def.name="Player_Overhand_Varco";
def.loopTime=false;def.loopPose=false;def.lockRootRotation=true;def.keepOriginalOrientation=true;
def.lockRootPositionXZ=true;def.keepOriginalPositionXZ=true;def.lockRootHeightY=true;def.keepOriginalPositionY=true;
importer.clipAnimations=new[]{def};importer.SaveAndReimport();
var clip=AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>().Single(c=>!c.name.StartsWith("__preview__"));
var avatar=AssetDatabase.LoadAllAssetsAtPath(path).OfType<Avatar>().Single();
if(!avatar.isValid||!avatar.isHuman||!clip.isHumanMotion)throw new System.Exception("Invalid humanoid animation");
var preview=new PreviewRenderUtility();var graph=UnityEngine.Playables.PlayableGraph.Create("VarcoThrowScan");
var rows=new List<object>();
try
{
    var go=preview.InstantiatePrefabInScene(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Afrer_Seconds/05.Model/Player/PlayerDummy_Rigged_V0.3.fbx"));
    var a=go.GetComponent<Animator>();a.runtimeAnimatorController=null;a.applyRootMotion=false;a.cullingMode=AnimatorCullingMode.AlwaysAnimate;
    graph.SetTimeUpdateMode(UnityEngine.Playables.DirectorUpdateMode.Manual);
    var play=UnityEngine.Animations.AnimationClipPlayable.Create(graph,clip);play.SetApplyFootIK(false);
    var output=UnityEngine.Animations.AnimationPlayableOutput.Create(graph,"pose",a);
    UnityEngine.Playables.PlayableOutputExtensions.SetSourcePlayable(output,play);graph.Play();
    Vector3 Local(HumanBodyBones b)=>go.transform.InverseTransformPoint(a.GetBoneTransform(b).position);
    float[] V(Vector3 v)=>new[]{v.x,v.y,v.z};
    for(int i=0;i<=100;i++)
    {
        float time=i*clip.length/100;
        UnityEngine.Playables.PlayableExtensions.SetTime(play,time);graph.Evaluate(.000001f);
        rows.Add(new {time,right=V(Local(HumanBodyBones.RightHand)-Local(HumanBodyBones.RightUpperArm)),left=V(Local(HumanBodyBones.LeftHand)-Local(HumanBodyBones.LeftUpperArm))});
    }
}
finally{if(graph.IsValid())graph.Destroy();preview.Cleanup();}
var result=new {clip.name,clip.length,clip.frameRate,avatar.isValid,avatar.isHuman,clip.isHumanMotion,rows};
System.IO.File.WriteAllText(System.IO.Path.GetFullPath(System.IO.Path.Combine(Application.dataPath,"../../../SourceAssets/VarcoFirstPerson/throw_scan.json")),Newtonsoft.Json.JsonConvert.SerializeObject(result,Newtonsoft.Json.Formatting.Indented));
return new {clip.name,clip.length,clip.frameRate,avatar.isValid,avatar.isHuman,clip.isHumanMotion};
