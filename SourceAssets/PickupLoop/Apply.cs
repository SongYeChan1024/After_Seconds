if(Application.isPlaying)throw new System.Exception("Edit mode required");
var scene=UnityEngine.SceneManagement.SceneManager.GetActiveScene();if(scene.name!="Level_B5_Circular"||scene.isDirty)throw new System.Exception("Expected clean B5 scene");
const string root="Assets/Afrer_Seconds/";
var before=new System.Collections.Generic.Dictionary<int,string>();foreach(var tr in UnityEngine.Object.FindObjectsByType<Transform>(FindObjectsSortMode.None))before[tr.GetInstanceID()]=tr.position+"/"+tr.rotation+"/"+tr.localScale;
var settings=AssetDatabase.LoadAssetAtPath<PlayerInventorySettings>(root+"06.Data/PlayerInventorySettings.asset");if(settings==null){settings=ScriptableObject.CreateInstance<PlayerInventorySettings>();AssetDatabase.CreateAsset(settings,root+"06.Data/PlayerInventorySettings.asset");}
var definition=AssetDatabase.LoadAssetAtPath<ItemDefinition>(root+"06.Data/Items/Item_TestBall.asset");
string ballPath=AssetDatabase.GetAssetPath(definition.WorldPrefab);
var ball=PrefabUtility.LoadPrefabContents(ballPath);
try{var world=ball.GetComponent<WorldItem>();if(world==null)world=ball.AddComponent<WorldItem>();var so=new SerializedObject(world);so.FindProperty("definition").objectReferenceValue=definition;so.ApplyModifiedPropertiesWithoutUndo();PrefabUtility.SaveAsPrefabAsset(ball,ballPath);}
finally{PrefabUtility.UnloadPrefabContents(ball);}
void Configure(GameObject player)
{
    var inventory=player.GetComponent<PlayerInventory>();if(inventory==null)inventory=player.AddComponent<PlayerInventory>();var so=new SerializedObject(inventory);so.FindProperty("settings").objectReferenceValue=settings;so.ApplyModifiedPropertiesWithoutUndo();
    var thrower=player.GetComponent<PlayerThrow>();so=new SerializedObject(thrower);so.FindProperty("heldItem").objectReferenceValue=null;so.FindProperty("repeatTestItem").boolValue=false;so.ApplyModifiedPropertiesWithoutUndo();
    var input=player.GetComponent<UnityEngine.InputSystem.PlayerInput>();var presenter=player.GetComponent<PlayerPresenter>();var events=new System.Collections.Generic.List<UnityEngine.InputSystem.PlayerInput.ActionEvent>(input.actionEvents);
    void Bind(string name,UnityEngine.Events.UnityAction<UnityEngine.InputSystem.InputAction.CallbackContext> callback)
    {
        var action=input.actions.FindAction("Player/"+name,true);var evt=events.Find(x=>x.actionId==action.id.ToString());
        if(evt==null){evt=new UnityEngine.InputSystem.PlayerInput.ActionEvent(action);events.Add(evt);}
        bool found=false;for(int i=0;i<evt.GetPersistentEventCount();i++)if(evt.GetPersistentTarget(i)==presenter&&evt.GetPersistentMethodName(i)==callback.Method.Name)found=true;
        if(!found)UnityEditor.Events.UnityEventTools.AddPersistentListener(evt,callback);
    }
    Bind("Interact",presenter.OnInteract);Bind("Drop",presenter.OnDrop);Bind("Previous",presenter.OnPrevious);Bind("Next",presenter.OnNext);input.actionEvents=events.ToArray();EditorUtility.SetDirty(input);
}
var current=UnityEngine.Object.FindAnyObjectByType<PlayerThrow>();var path=PrefabUtility.GetPrefabAssetPathOfNearestInstanceRoot(current.gameObject);var prefab=PrefabUtility.LoadPrefabContents(path);
try{Configure(prefab);PrefabUtility.SaveAsPrefabAsset(prefab,path);}finally{PrefabUtility.UnloadPrefabContents(prefab);}
current=UnityEngine.Object.FindAnyObjectByType<PlayerThrow>();Configure(current.gameObject);PrefabUtility.RecordPrefabInstancePropertyModifications(current);PrefabUtility.RecordPrefabInstancePropertyModifications(current.GetComponent<UnityEngine.InputSystem.PlayerInput>());
var instance=GameObject.Find("PickupLoop_TestBall");if(instance==null){instance=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(ballPath),scene);Undo.RegisterCreatedObjectUndo(instance,"Add pickup loop ball");instance.name="PickupLoop_TestBall";}
Vector3 place=current.transform.position+current.transform.forward*1.15f;if(!Physics.Raycast(place+Vector3.up*2,Vector3.down,out RaycastHit floor,5f))throw new System.Exception("No floor for pickup ball");
instance.transform.position=floor.point+Vector3.up*.065f;PrefabUtility.RecordPrefabInstancePropertyModifications(instance.transform);
int changed=0;foreach(var tr in UnityEngine.Object.FindObjectsByType<Transform>(FindObjectsSortMode.None))if(before.TryGetValue(tr.GetInstanceID(),out string prior)&&prior!=tr.position+"/"+tr.rotation+"/"+tr.localScale)changed++;
if(changed!=0)throw new System.Exception("Existing transforms changed: "+changed);
AssetDatabase.SaveAssets();UnityEditor.SceneManagement.EditorSceneManager.SaveScene(scene);
return new{existingTransformsChanged=changed,ballPosition=instance.transform.position.ToString(),capacity=settings.capacity,inputEvents=current.GetComponent<UnityEngine.InputSystem.PlayerInput>().actionEvents.Count};
