if (Application.isPlaying || !Application.dataPath.Contains("After_Seconds_Build")) throw new System.Exception("After Seconds edit mode required");
const string root="Assets/Afrer_Seconds/";
var p=AssetDatabase.LoadAssetAtPath<GameObject>(root+"05.Model/Player/Player_Dummy_V0.1.prefab");
var h=p.GetComponent<PlayerFirstPersonHands>();var s=new SerializedObject(h);
var missing=new List<string>();
foreach(var field in new[]{"settings","rigRoot","rightUpper","rightLower","rightHand","leftUpper","leftLower","leftHand","lowerBody"})
    if(s.FindProperty(field).objectReferenceValue==null)missing.Add(field);
int missingScripts=p.GetComponentsInChildren<Transform>(true).Sum(x=>GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(x.gameObject));
var renderer=(SkinnedMeshRenderer)s.FindProperty("lowerBody").objectReferenceValue;
var animator=p.transform.Find("VisualRoot").GetComponentsInChildren<Animator>(true).Single(a=>a.gameObject.activeSelf&&a.isHuman);
var scene=UnityEngine.SceneManagement.SceneManager.GetActiveScene();
var type=typeof(Editor).Assembly.GetType("UnityEditor.LogEntries");object[] counts={0,0,0};
type.GetMethod("GetCountsByType",System.Reflection.BindingFlags.Static|System.Reflection.BindingFlags.Public).Invoke(null,counts);
var result=new {scene=scene.name,scene.isDirty,playing=Application.isPlaying,background=Application.runInBackground,
    missingScripts,missingReferences=missing.ToArray(),bodyTriangles=renderer.sharedMesh.triangles.Length/3,
    animator.cullingMode,bodyBones=renderer.bones.Length,bodyBoneNulls=renderer.bones.Count(b=>b==null),
    sourceController=AssetDatabase.GetAssetPath(animator.runtimeAnimatorController),consoleErrors=counts[0],consoleWarnings=counts[1]};
string text=Newtonsoft.Json.JsonConvert.SerializeObject(result,Newtonsoft.Json.Formatting.Indented);
System.IO.File.WriteAllText(System.IO.Path.GetFullPath(System.IO.Path.Combine(Application.dataPath,"../../../Docs/Review/2026-11-17_FirstPersonMotion/final_audit.json")),text);
return result;
