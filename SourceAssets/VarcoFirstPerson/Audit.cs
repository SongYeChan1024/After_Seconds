const string root="Assets/Afrer_Seconds/";
var motion=AssetDatabase.LoadAssetAtPath<PlayerHandAnimationSet>(root+"06.Data/PlayerHandAnimations.asset");
var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(root+"05.Model/Player/Player_Dummy_V0.1.prefab");
var hands=prefab.GetComponent<PlayerFirstPersonHands>();var so=new SerializedObject(hands);
var throwing=AssetDatabase.LoadAssetAtPath<PlayerThrowSettings>(root+"06.Data/PlayerThrowSettings.asset");
var handSettings=AssetDatabase.LoadAssetAtPath<PlayerHandSettings>(root+"06.Data/PlayerHandSettings.asset");
var body=(Animator)so.FindProperty("bodyAnimator").objectReferenceValue;
var lower=(SkinnedMeshRenderer)so.FindProperty("lowerBody").objectReferenceValue;
var console=typeof(Editor).Assembly.GetType("UnityEditor.LogEntries");object[] counts={0,0,0};
console.GetMethod("GetCountsByType",System.Reflection.BindingFlags.Static|System.Reflection.BindingFlags.Public).Invoke(null,counts);
var ctrl=(UnityEditor.Animations.AnimatorController)body.runtimeAnimatorController;
var motions=new List<object>();
void Motion(UnityEngine.Motion m)
{
    if(m is UnityEditor.Animations.BlendTree tree)
    {foreach(var c in tree.children){motions.Add(new{name=c.motion.name,c.threshold,c.timeScale,c.cycleOffset});Motion(c.motion);}}
}
foreach(var state in ctrl.layers[0].stateMachine.states)Motion(state.state.motion);
var report=new{Application.isPlaying,scene=UnityEngine.SceneManagement.SceneManager.GetActiveScene().name,dirty=UnityEngine.SceneManagement.SceneManager.GetActiveScene().isDirty,
    missingScripts=prefab.GetComponentsInChildren<Transform>(true).Sum(t=>GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject)),
    hands=hands.UsesAnimationClips,animationReference=so.FindProperty("animations").objectReferenceValue==motion,
    animator=body.name,controller=AssetDatabase.GetAssetPath(body.runtimeAnimatorController),body.cullingMode,
    lowerTriangles=lower.sharedMesh.triangles.Length/3,sharedBodyBones=lower.bones.All(b=>body.GetComponentsInChildren<Transform>(true).Contains(b)),
    overhand=AssetDatabase.GetAssetPath(motion.overhandSource),clipMeshes=AssetDatabase.LoadAllAssetsAtPath(AssetDatabase.GetAssetPath(motion.overhandSource)).OfType<Mesh>().Count(),
    errors=counts[0],warnings=counts[1],logs=counts[2],motions,
    throwing.OverhandSpeed,throwing.UnderhandSpeed,throwing.UnderhandAngle,underhandPosition=throwing.UnderhandHandOffset.ToString(),handSettings.underhandZoomLift,
    background=PlayerSettings.runInBackground,inputBehavior=UnityEngine.InputSystem.InputSystem.settings.backgroundBehavior.ToString(),editorInputBehavior=UnityEngine.InputSystem.InputSystem.settings.editorInputBehaviorInPlayMode.ToString()};
System.IO.File.WriteAllText(System.IO.Path.GetFullPath(System.IO.Path.Combine(Application.dataPath,"../../../Docs/Review/2026-11-17_VarcoFirstPerson/audit.json")),Newtonsoft.Json.JsonConvert.SerializeObject(report,Newtonsoft.Json.Formatting.Indented));return report;
