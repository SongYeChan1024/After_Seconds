// After Seconds 편집 모드 전용. 원본 Animator/본/메시를 수정하지 않고 하체 표시만 연결한다.
if (!Application.dataPath.Contains("After_Seconds_Build") || EditorApplication.isPlaying)
    throw new System.InvalidOperationException("After Seconds edit mode required");
const string root = "Assets/Afrer_Seconds/";
string path = root + "05.Model/Player/Player_Dummy_V0.1.prefab";
var player = PrefabUtility.LoadPrefabContents(path);
try
{
    var hands = player.GetComponent<PlayerFirstPersonHands>();
    if (hands == null) throw new System.Exception("Existing first-person hands required");
    var animator = player.transform.Find("VisualRoot").GetComponentsInChildren<Animator>(true)
        .Single(a => a.gameObject.activeSelf && a.isHuman);
    var source = animator.GetComponentsInChildren<SkinnedMeshRenderer>(true)
        .First(r => r.name != "FirstPersonLowerBody");
    var mesh = UnityEngine.Object.Instantiate(source.sharedMesh);
    mesh.name = "Player_FirstPersonLowerBody";
    // 자동 웨이트의 섞임을 경계로 쓰면 허벅지/복부에 구멍이 남는다.
    // 원본 T 포즈의 가슴 아래 기하를 보존한다. 팔/머리는 이 높이 위에 있다.
    int chestIndex = System.Array.IndexOf(source.bones, animator.GetBoneTransform(HumanBodyBones.UpperChest));
    float chestHeight = mesh.bindposes[chestIndex].inverse.MultiplyPoint3x4(Vector3.zero).y;
    int shoulderIndex = System.Array.IndexOf(source.bones, animator.GetBoneTransform(HumanBodyBones.LeftUpperArm));
    Vector3 shoulderBind = mesh.bindposes[shoulderIndex].inverse.MultiplyPoint3x4(Vector3.zero);
    float cutoff = shoulderBind.y - 0.015f;
    float torsoHalfWidth = Mathf.Abs(shoulderBind.x) + 0.02f;
    var vertices = mesh.vertices;
    bool Keep(int i) => vertices[i].y < cutoff &&
        (vertices[i].y < chestHeight || Mathf.Abs(vertices[i].x) < torsoHalfWidth);
    int triangleCount = 0;
    for (int sub = 0; sub < mesh.subMeshCount; sub++)
    {
        var triangles = mesh.GetTriangles(sub); var selected = new List<int>();
        for (int i = 0; i < triangles.Length; i += 3)
            if (Keep(triangles[i]) && Keep(triangles[i+1]) && Keep(triangles[i+2]))
            { selected.Add(triangles[i]); selected.Add(triangles[i+1]); selected.Add(triangles[i+2]); }
        mesh.SetTriangles(selected, sub); triangleCount += selected.Count / 3;
    }
    if (triangleCount < 500) throw new System.Exception("Unexpected lower-body mesh selection: " + triangleCount);
    string meshPath = root + "05.Model/Player/Player_FirstPersonLowerBody.asset";
    var existing = AssetDatabase.LoadAssetAtPath<Mesh>(meshPath);
    if (existing != null)
    {
        EditorUtility.CopySerialized(mesh, existing);
        // CopySerialized만으로는 열린 Editor의 기존 GPU 인덱스가 남을 수 있다.
        for (int sub = 0; sub < mesh.subMeshCount; sub++) existing.SetTriangles(mesh.GetTriangles(sub), sub);
        existing.UploadMeshData(false);
        UnityEngine.Object.DestroyImmediate(mesh); mesh = existing;
    }
    else AssetDatabase.CreateAsset(mesh, meshPath);
    EditorUtility.SetDirty(mesh);
    var child = source.transform.Find("FirstPersonLowerBody");
    if (child == null) { child = new GameObject("FirstPersonLowerBody").transform; child.SetParent(source.transform, false); }
    var lower = child.GetComponent<SkinnedMeshRenderer>();
    if (lower == null) lower = child.gameObject.AddComponent<SkinnedMeshRenderer>();
    lower.sharedMesh = mesh; lower.sharedMaterials = source.sharedMaterials;
    lower.bones = source.bones; lower.rootBone = source.rootBone;
    lower.localBounds = source.localBounds; lower.updateWhenOffscreen = true;
    lower.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
    lower.receiveShadows = true; lower.enabled = false;
    // 시선을 위로 돌려 몸이 화면 밖에 있어도 다음 걸음 포즈를 갱신한다.
    animator.cullingMode = AnimatorCullingMode.AlwaysAnimate;
    var so = new SerializedObject(hands); so.FindProperty("lowerBody").objectReferenceValue = lower;
    so.ApplyModifiedPropertiesWithoutUndo();
    var handSettings = AssetDatabase.LoadAssetAtPath<PlayerHandSettings>(root + "06.Data/PlayerHandSettings.asset");
    handSettings.sprintOffset = new Vector3(-0.015f, -0.015f, -0.01f);
    handSettings.leftRestingHand = new Vector3(-0.24f, -0.17f, 0.43f);
    handSettings.rightShoulder.z = handSettings.leftShoulder.z = -0.015f;
    handSettings.runSwing.z = 0.09f;
    EditorUtility.SetDirty(handSettings);
    var throwSettings = AssetDatabase.LoadAssetAtPath<PlayerThrowSettings>(root + "06.Data/PlayerThrowSettings.asset");
    var ts = new SerializedObject(throwSettings);
    ts.FindProperty("showFullTrajectory").boolValue = true;
    ts.FindProperty("trajectoryOpacity").floatValue = 0.65f;
    ts.ApplyModifiedPropertiesWithoutUndo();
    EditorUtility.SetDirty(throwSettings);
    PrefabUtility.SaveAsPrefabAsset(player, path); AssetDatabase.SaveAssets();
    return "Lower-body triangles=" + triangleCount + "; existing Animator bones shared; original renderer=" + source.name;
}
finally { PrefabUtility.UnloadPrefabContents(player); }
