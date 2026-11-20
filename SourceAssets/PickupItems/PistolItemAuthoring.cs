#if UNITY_EDITOR
using System;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

// 의사코드: FBX의 눈금 기준점을 읽고 월드 프리팹의 앞 방향을 맞춘다.
// 메시 중심에 물리 충돌체를 두고 같은 좌표계의 파지점과 가늠자 위치를 아이템 정의에 저장한다.
public static class PistolItemAuthoring
{
    const string Root = "Assets/Afrer_Seconds/";
    public const string PrefabPath = Root + "04.Prefabs/Items/Pistol.prefab";
    public const string DefinitionPath = Root + "06.Data/Items/Item_Pistol.asset";
    public const string ReviewScenePath = Root + "01.Scenes/Review/PistolSightReview.unity";

    public static void CreateReviewScene()
    {
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        if (!AssetDatabase.IsValidFolder(Root + "01.Scenes/Review"))
            AssetDatabase.CreateFolder(Root + "01.Scenes", "Review");
        var rigAsset = AssetDatabase.LoadAssetAtPath<GameObject>(Root + "04.Prefabs/PlayerRig.prefab");
        var rig = (GameObject)PrefabUtility.InstantiatePrefab(rigAsset, scene);
        var body = rig.GetComponentInChildren<CharacterController>();
        var eye = rig.GetComponentInChildren<PlayerThrow>().Origin;
        rig.transform.rotation = Quaternion.Inverse(Quaternion.LookRotation(Vector3.ProjectOnPlane(eye.forward,Vector3.up)));
        Vector3 feet = body.transform.TransformPoint(body.center) - Vector3.up * body.height * .5f;
        rig.transform.position += Vector3.up * .01f - feet;
        Material wall = AssetDatabase.LoadAssetAtPath<Material>(Root + "05.Model/Environment/Common/Materials/FacilityWall_PaintedConcrete.mat");
        void Block(string name, Vector3 position, Vector3 size)
        {
            var block = GameObject.CreatePrimitive(PrimitiveType.Cube);
            block.name = name;
            block.transform.position = position;
            block.transform.localScale = size;
            block.GetComponent<MeshRenderer>().sharedMaterial = wall;
        }
        Block("검수실 바닥", new Vector3(0,-.1f,1.5f), new Vector3(8,.2f,8));
        Block("검수실 벽", new Vector3(0,1.75f,4.4f), new Vector3(8,3.5f,.2f));
        float top = eye.position.y - .11f;
        Vector3 stand = eye.position + Vector3.forward*.98f;
        Block("소품 받침대", new Vector3(stand.x,top*.5f,stand.z), new Vector3(.75f,top,.48f));
        var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(PrefabPath);
        var pistol = (GameObject)PrefabUtility.InstantiatePrefab(prefab,scene);
        pistol.transform.rotation=Quaternion.Euler(0,65,0);
        pistol.transform.position=new Vector3(stand.x,top + pistol.GetComponent<BoxCollider>().bounds.extents.y + .001f,stand.z-.16f);
        var lamp = new GameObject("검수실 조명").AddComponent<Light>();
        lamp.type = LightType.Directional;
        lamp.intensity = 1.65f;
        lamp.transform.rotation = Quaternion.Euler(44,-27,0);
        RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
        RenderSettings.ambientLight = new Color(.47f,.49f,.52f);
        EditorSceneManager.SaveScene(scene, ReviewScenePath);
    }

    public static void Run()
    {
        PickupArtImport.Run();
        var asset = AssetDatabase.LoadAssetAtPath<GameObject>(Root + "05.Model/Props/Common/Pickup_Pistol.fbx");
        var definition = AssetDatabase.LoadAssetAtPath<ItemDefinition>(DefinitionPath);
        if (!definition)
        {
            definition = ScriptableObject.CreateInstance<ItemDefinition>();
            AssetDatabase.CreateAsset(definition, DefinitionPath);
        }
        var root = new GameObject("Pistol");
        try
        {
            var model = (GameObject)PrefabUtility.InstantiatePrefab(asset, root.transform);
            var markers = model.GetComponentsInChildren<Transform>(true);
            var rear = markers.Single(t => t.name == "RearSightReference");
            var front = markers.Single(t => t.name == "FrontSightReference");
            var grip = markers.Single(t => t.name == "GripReference");
            model.transform.rotation = Quaternion.Inverse(Quaternion.LookRotation(front.position - rear.position, Vector3.up)) * model.transform.rotation;
            var bounds = model.GetComponentInChildren<MeshRenderer>().bounds;
            model.transform.position -= bounds.center;
            var body = root.AddComponent<Rigidbody>();
            body.mass = .65f;
            body.interpolation = RigidbodyInterpolation.Interpolate;
            body.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;
            root.AddComponent<BoxCollider>().size = bounds.size;
            root.AddComponent<ThrownObject>();
            var world = new SerializedObject(root.AddComponent<WorldItem>());
            world.FindProperty("definition").objectReferenceValue = definition;
            world.ApplyModifiedPropertiesWithoutUndo();
            root.AddComponent<SwapShotAbility>();
            if ((front.position - rear.position).normalized.z < .9999f || rear.position.y <= grip.position.y)
                throw new InvalidOperationException("Unexpected pistol model orientation");
            var prefab = PrefabUtility.SaveAsPrefabAsset(root, PrefabPath);
            var data = new SerializedObject(definition);
            data.FindProperty("displayName").stringValue = "경비 권총";
            data.FindProperty("worldPrefab").objectReferenceValue = prefab.GetComponent<ThrownObject>();
            data.FindProperty("gripOffset").vector3Value = grip.position;
            data.FindProperty("hasIronSights").boolValue = true;
            data.FindProperty("rearSightLocal").vector3Value = rear.position;
            data.FindProperty("sightEyeDistance").floatValue = .38f;
            data.ApplyModifiedPropertiesWithoutUndo();
            AssetDatabase.SaveAssets();
            if (!ThrowFlight.TryShape(definition.WorldPrefab, out _, out _))
                throw new InvalidOperationException("Pistol pickup shape failed");
            Debug.Log("PISTOL_SIGHT_PREFAB_READY " + rear.position + " " + front.position);
        }
        finally { UnityEngine.Object.DestroyImmediate(root); }
    }
}
#endif
