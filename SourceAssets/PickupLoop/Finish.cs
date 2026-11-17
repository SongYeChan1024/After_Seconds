if(Application.isPlaying)throw new System.Exception("Finish in Edit mode only");
var scene=UnityEngine.SceneManagement.SceneManager.GetActiveScene();
if(scene.name!="Level_B5_Circular"||scene.isDirty)throw new System.Exception("Expected saved B5 scene");
const string root="Assets/Afrer_Seconds/";
var player=UnityEngine.Object.FindAnyObjectByType<PlayerInventory>();
var problems=new System.Collections.Generic.List<string>();
int missingScripts=0,checkedComponents=0;
void CheckObject(GameObject go)
{
    foreach(var tr in go.GetComponentsInChildren<Transform>(true))missingScripts+=GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(tr.gameObject);
    foreach(var component in go.GetComponentsInChildren<Component>(true))
    {
        if(component==null)continue;checkedComponents++;
        var so=new SerializedObject(component);var prop=so.GetIterator();
        while(prop.Next(true))if(prop.propertyType==SerializedPropertyType.ObjectReference&&prop.objectReferenceValue==null&&prop.objectReferenceInstanceIDValue!=0)
            problems.Add(go.name+"/"+component.GetType().Name+"/"+prop.propertyPath);
    }
}
CheckObject(player.gameObject);
CheckObject(AssetDatabase.LoadAssetAtPath<GameObject>(root+"05.Model/Player/Player_Dummy_V0.1.prefab"));
CheckObject(AssetDatabase.LoadAssetAtPath<GameObject>(root+"04.Prefabs/Test/ThrowTestItem.prefab"));
var balls=UnityEngine.Object.FindObjectsByType<WorldItem>(FindObjectsSortMode.None);
if(balls.Length!=1)problems.Add("Expected one scene pickup ball");
else CheckObject(balls[0].gameObject);
var thrower=player.GetComponent<PlayerThrow>();var ts=new SerializedObject(thrower);
if(ts.FindProperty("heldItem").objectReferenceValue!=null||ts.FindProperty("repeatTestItem").boolValue)problems.Add("Automatic supply still enabled");
var settings=(PlayerInventorySettings)new SerializedObject(player).FindProperty("settings").objectReferenceValue;
if(settings==null||settings.capacity!=5)problems.Add("Inventory settings missing or capacity changed");
var font=AssetDatabase.LoadAssetAtPath<TMPro.TMP_FontAsset>(root+"06.Data/UI/Pickup_Korean_SDF.asset");
if(font==null||font.sourceFontFile==null||font.material==null||font.material.shader==null)problems.Add("Korean font reference missing");
var events=player.GetComponent<UnityEngine.InputSystem.PlayerInput>().actionEvents;
foreach(string method in new[]{"OnInteract","OnDrop","OnPrevious","OnNext"})
{
    int listeners=0;foreach(var evt in events)for(int i=0;i<evt.GetPersistentEventCount();i++)if(evt.GetPersistentMethodName(i)==method&&evt.GetPersistentTarget(i)==player.GetComponent<PlayerPresenter>())listeners++;
    if(listeners!=1)problems.Add(method+" listener count: "+listeners);
}
PlayerSettings.runInBackground=false;AssetDatabase.SaveAssets();
var throwSettings=(PlayerThrowSettings)ts.FindProperty("settings").objectReferenceValue;
var report=new{scene=scene.path,scene.isDirty,Application.isPlaying,checkedComponents,missingScripts,problems,canvases=UnityEngine.Object.FindObjectsByType<Canvas>(FindObjectsSortMode.None).Length,worldItems=balls.Length,capacity=settings.capacity,playerPosition=player.transform.position.ToString(),ballPosition=balls[0].transform.position.ToString(),overhandSpeed=throwSettings.OverhandSpeed,underhandSpeed=throwSettings.UnderhandSpeed,font=AssetDatabase.GetAssetPath(font),tmpResources=AssetDatabase.IsValidFolder("Assets/TextMesh Pro"),PlayerSettings.runInBackground};
string json=Newtonsoft.Json.JsonConvert.SerializeObject(report,Newtonsoft.Json.Formatting.Indented);
System.IO.File.WriteAllText(System.IO.Path.GetFullPath(System.IO.Path.Combine(Application.dataPath,"../../../Docs/Review/2026-11-17_PickupLoop/final_state.json")),json);
return json;
