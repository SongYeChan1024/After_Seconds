
if (!Application.dataPath.Contains("After_Seconds_Build") || EditorApplication.isPlaying)
    throw new System.InvalidOperationException("After Seconds 편집 모드에서 실행해야 합니다.");
const string root = "Assets/Afrer_Seconds/";
string path = root + "05.Model/Player/Player_Dummy_V0.1.prefab";
var player = PrefabUtility.LoadPrefabContents(path);
try
{
    if (player.GetComponent<PlayerFirstPersonHands>() != null) throw new System.InvalidOperationException("이미 연결된 리그입니다. 중복 생성하지 않습니다.");
    var source = player.GetComponentsInChildren<Animator>().First(a => a.gameObject.activeSelf);
    var rig = UnityEngine.Object.Instantiate(source.gameObject, player.transform.Find("CameraRoot"));
    rig.name = "FirstPersonArms_Prototype";
    rig.transform.localPosition = Vector3.zero;
    rig.transform.localRotation = Quaternion.identity;
    var animator = rig.GetComponent<Animator>();
    animator.Rebind();
    rig.transform.localScale = Vector3.one * 1.75f; // 이 모델의 재바인딩 후 팔 길이를 실제 표시 크기로 맞춘다.
    var rightUpper = animator.GetBoneTransform(HumanBodyBones.RightUpperArm);
    var rightLower = animator.GetBoneTransform(HumanBodyBones.RightLowerArm);
    var rightHand = animator.GetBoneTransform(HumanBodyBones.RightHand);
    var leftUpper = animator.GetBoneTransform(HumanBodyBones.LeftUpperArm);
    var leftLower = animator.GetBoneTransform(HumanBodyBones.LeftLowerArm);
    var leftHand = animator.GetBoneTransform(HumanBodyBones.LeftHand);
    int triangleCount = 0;
    foreach (var renderer in rig.GetComponentsInChildren<SkinnedMeshRenderer>())
    {
        var mesh = UnityEngine.Object.Instantiate(renderer.sharedMesh);
        mesh.name = "Player_FirstPersonArms";
        var weights = mesh.boneWeights;
        var arm = renderer.bones.Select(b => b != null && (b == rightUpper || b.IsChildOf(rightUpper) || b == leftUpper || b.IsChildOf(leftUpper))).ToArray();
        float Weight(int vertex)
        {
            var w = weights[vertex];
            return (arm[w.boneIndex0] ? w.weight0 : 0f) + (arm[w.boneIndex1] ? w.weight1 : 0f) +
                (arm[w.boneIndex2] ? w.weight2 : 0f) + (arm[w.boneIndex3] ? w.weight3 : 0f);
        }
        for (int sub = 0; sub < mesh.subMeshCount; sub++)
        {
            int[] triangles = mesh.GetTriangles(sub);
            var selected = new List<int>();
            for (int i = 0; i < triangles.Length; i += 3)
                if (Weight(triangles[i]) > 0.65f && Weight(triangles[i + 1]) > 0.65f && Weight(triangles[i + 2]) > 0.65f)
                { selected.Add(triangles[i]); selected.Add(triangles[i + 1]); selected.Add(triangles[i + 2]); }
            mesh.SetTriangles(selected, sub); triangleCount += selected.Count / 3;
        }
        AssetDatabase.CreateAsset(mesh, root + "05.Model/Player/Player_FirstPersonArms.asset");
        renderer.sharedMesh = mesh;
        renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        renderer.updateWhenOffscreen = true;
        renderer.localBounds = new Bounds(Vector3.zero, Vector3.one * 4f);
    }
    UnityEngine.Object.DestroyImmediate(animator);
    var settings = ScriptableObject.CreateInstance<PlayerHandSettings>();
    AssetDatabase.CreateAsset(settings, root + "06.Data/PlayerHandSettings.asset");
    var hands = player.AddComponent<PlayerFirstPersonHands>();
    var so = new SerializedObject(hands);
    void Ref(string key, UnityEngine.Object value) { so.FindProperty(key).objectReferenceValue = value; }
    Ref("settings", settings); Ref("rigRoot", rig.transform);
    Ref("rightUpper", rightUpper); Ref("rightLower", rightLower); Ref("rightHand", rightHand);
    Ref("leftUpper", leftUpper); Ref("leftLower", leftLower); Ref("leftHand", leftHand);
    var body = player.transform.Find("VisualRoot").GetComponentsInChildren<Renderer>(true);
    var bodyProperty = so.FindProperty("bodyRenderers"); bodyProperty.arraySize = body.Length;
    for (int i = 0; i < body.Length; i++) bodyProperty.GetArrayElementAtIndex(i).objectReferenceValue = body[i];
    so.ApplyModifiedPropertiesWithoutUndo();
    var line = player.transform.Find("ThrowTrajectory").GetComponent<LineRenderer>();
    line.widthCurve = AnimationCurve.Linear(0f, 1f, 1f, 1f);
    line.widthMultiplier = 0.012f;
    var material = line.sharedMaterial;
    Undo.RecordObject(material, "투척 궤적 투명도 설정");
    material.shader = Shader.Find("Universal Render Pipeline/Particles/Unlit");
    material.SetColor("_BaseColor", Color.white);
    material.SetFloat("_Surface", 1f); material.SetFloat("_Blend", 0f);
    material.SetFloat("_SrcBlend", 5f); material.SetFloat("_DstBlend", 10f); material.SetFloat("_ZWrite", 0f);
    material.EnableKeyword("_SURFACE_TYPE_TRANSPARENT"); material.renderQueue = 3000;
    EditorUtility.SetDirty(material);
    var throwSettings = AssetDatabase.LoadAssetAtPath<PlayerThrowSettings>(root + "06.Data/PlayerThrowSettings.asset");
    EditorUtility.SetDirty(throwSettings); // 초기 필드값도 에셋에 명시적으로 직렬화한다.
    PrefabUtility.SaveAsPrefabAsset(player, path);
    AssetDatabase.SaveAssets();
    Debug.Log("First-person prototype connected: arm triangles=" + triangleCount + ", original body meshes untouched.");
}
finally { PrefabUtility.UnloadPrefabContents(player); }
