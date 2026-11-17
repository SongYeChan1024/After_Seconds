if (Application.isPlaying) throw new System.Exception("Edit mode required");
const string root="Assets/Afrer_Seconds/";
AnimationClip Clip(string name)=>AssetDatabase.LoadAllAssetsAtPath(root+"07.Animator/Player/Clips/"+name+".fbx").OfType<AnimationClip>().Single(c=>!c.name.StartsWith("__preview__"));
var walk=Clip("Rigged_V0.3/Player_Walk");var run=Clip("Rigged_V0.3/Player_Run");var overhand=Clip("VarcoFirstPerson/Player_Overhand_Varco");
var data=ScriptableObject.CreateInstance<PlayerHandAnimationSet>();
data.walkSource=walk;data.runSource=run;data.overhandSource=overhand;
var preview=new PreviewRenderUtility();
var go=preview.InstantiatePrefabInScene(AssetDatabase.LoadAssetAtPath<GameObject>(root+"05.Model/Player/PlayerDummy_Rigged_V0.3.fbx"));
var animator=go.GetComponent<Animator>();animator.runtimeAnimatorController=null;animator.applyRootMotion=false;animator.cullingMode=AnimatorCullingMode.AlwaysAnimate;
Vector3 Local(HumanBodyBones b)=>go.transform.InverseTransformPoint(animator.GetBoneTransform(b).position);
(Vector3[],Vector3[]) Sample(AnimationClip clip,float start,float end,int count)
{
    var graph=UnityEngine.Playables.PlayableGraph.Create("BakeVarcoHands");
    var r=new Vector3[count+1];var l=new Vector3[count+1];
    try
    {
        graph.SetTimeUpdateMode(UnityEngine.Playables.DirectorUpdateMode.Manual);
        var play=UnityEngine.Animations.AnimationClipPlayable.Create(graph,clip);play.SetApplyFootIK(false);
        var output=UnityEngine.Animations.AnimationPlayableOutput.Create(graph,"pose",animator);
        UnityEngine.Playables.PlayableOutputExtensions.SetSourcePlayable(output,play);graph.Play();
        for(int i=0;i<=count;i++)
        {
            UnityEngine.Playables.PlayableExtensions.SetTime(play,Mathf.Lerp(start,end,(float)i/count));graph.Evaluate(.000001f);
            r[i]=Local(HumanBodyBones.RightHand)-Local(HumanBodyBones.RightUpperArm);
            l[i]=Local(HumanBodyBones.LeftHand)-Local(HumanBodyBones.LeftUpperArm);
        }
    }
    finally{if(graph.IsValid())graph.Destroy();}
    return(r,l);
}
HandVectorCurve Curves(Vector3[] points,bool loop)
{
    AnimationCurve Axis(int axis)
    {
        var curve=new AnimationCurve(points.Select((v,i)=>new Keyframe((float)i/(points.Length-1),v[axis])).ToArray());
        for(int i=0;i<curve.length;i++)
        {AnimationUtility.SetKeyLeftTangentMode(curve,i,AnimationUtility.TangentMode.ClampedAuto);AnimationUtility.SetKeyRightTangentMode(curve,i,AnimationUtility.TangentMode.ClampedAuto);}
        if(loop)
        {
            curve.preWrapMode=curve.postWrapMode=WrapMode.Loop;
            float tangent=(points[1][axis]-points[points.Length-2][axis])*(points.Length-1)*.5f;
            var first=curve.keys[0];first.inTangent=first.outTangent=tangent;curve.MoveKey(0,first);
            var last=curve.keys[curve.length-1];last.inTangent=last.outTangent=tangent;curve.MoveKey(curve.length-1,last);
        }
        return curve;
    }
    return new HandVectorCurve{x=Axis(0),y=Axis(1),z=Axis(2)};
}
HandVectorCurve Locomotion(Vector3[] points)
{
    var drift=points[points.Length-1]-points[0];
    for(int i=0;i<points.Length;i++)points[i]-=drift*((float)i/(points.Length-1));
    for(int axis=0;axis<3;axis++)
    {
        float min=points.Min(v=>v[axis]),max=points.Max(v=>v[axis]);float center=(max+min)*.5f,range=(max-min)*.5f;
        for(int i=0;i<points.Length;i++)points[i][axis]=range>.003f?(points[i][axis]-center)/range:0f;
    }
    points[points.Length-1]=points[0];return Curves(points,true);
}
HandVectorCurve Gesture(Vector3[] points,float scale,float cap,bool fade)
{
    var origin=points[0];
    for(int i=0;i<points.Length;i++)
    {
        float t=(float)i/(points.Length-1);
        points[i]=Vector3.ClampMagnitude((points[i]-origin)*scale,cap);
        if(fade)points[i]*=1f-Mathf.SmoothStep(0f,1f,Mathf.InverseLerp(.65f,1f,t));
    }
    return Curves(points,false);
}
try
{
    var w=Sample(walk,0,walk.length,60);data.walkRight=Locomotion(w.Item1);data.walkLeft=Locomotion(w.Item2);
    var r=Sample(run,0,run.length,80);data.runRight=Locomotion(r.Item1);data.runLeft=Locomotion(r.Item2);
    var p=Sample(overhand,2f,data.sourceReleaseTime,20);data.prepareRight=Gesture(p.Item1,.18f,.045f,false);data.prepareLeft=Gesture(p.Item2,.14f,.025f,false);
    var s=Sample(overhand,data.sourceReleaseTime,data.sourceReleaseEnd,50);data.releaseRight=Gesture(s.Item1,.35f,.16f,true);data.releaseLeft=Gesture(s.Item2,.15f,.06f,true);
}
finally{preview.Cleanup();}
string assetPath=root+"06.Data/PlayerHandAnimations.asset";
var asset=AssetDatabase.LoadAssetAtPath<PlayerHandAnimationSet>(assetPath);
if(asset==null){asset=data;AssetDatabase.CreateAsset(asset,assetPath);}else{EditorUtility.CopySerialized(data,asset);UnityEngine.Object.DestroyImmediate(data);EditorUtility.SetDirty(asset);}
string prefabPath=root+"05.Model/Player/Player_Dummy_V0.1.prefab";
var player=PrefabUtility.LoadPrefabContents(prefabPath);
try
{
    var hands=player.GetComponent<PlayerFirstPersonHands>();
    var body=player.GetComponentsInChildren<Animator>(true).Single(a=>a.gameObject.activeInHierarchy&&a.isHuman&&a.runtimeAnimatorController!=null);
    var so=new SerializedObject(hands);so.FindProperty("animations").objectReferenceValue=asset;so.FindProperty("bodyAnimator").objectReferenceValue=body;so.ApplyModifiedPropertiesWithoutUndo();
    PrefabUtility.SaveAsPrefabAsset(player,prefabPath);
}
finally{PrefabUtility.UnloadPrefabContents(player);}
AssetDatabase.SaveAssets();
var report=new {walk=new{walk.name,walk.length,walk.frameRate},run=new{run.name,run.length,run.frameRate},overhand=new{overhand.name,overhand.length,overhand.frameRate},asset.sourceReleaseTime,asset.sourceReleaseEnd,asset.releaseDuration,curves=new[]{new{name="walkRight",keys=asset.walkRight.x.length},new{name="runRight",keys=asset.runRight.x.length},new{name="releaseRight",keys=asset.releaseRight.x.length}},prefabPath,assetPath};
System.IO.File.WriteAllText(System.IO.Path.GetFullPath(System.IO.Path.Combine(Application.dataPath,"../../../SourceAssets/VarcoFirstPerson/bake.json")),Newtonsoft.Json.JsonConvert.SerializeObject(report,Newtonsoft.Json.Formatting.Indented));
return report;
