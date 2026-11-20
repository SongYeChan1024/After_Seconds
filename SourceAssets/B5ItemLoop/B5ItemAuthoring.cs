using System;
using System.Linq;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class B5ItemAuthoring
{
    public const string Root = "Assets/Afrer_Seconds/";
    public const string B5 = Root + "01.Scenes/Stage/Level_B5_Circular.unity";
    public const string Review = Root + "01.Scenes/Review/PistolSightReview.unity";
    const string GuardPath = Root + "04.Prefabs/B5_MealGuard.prefab";
    public static readonly string[] Items = { "Pen","Spoon","MetalCup","WaterBottle","DocumentFolder","UsbDrive","DataShard","Pager","Flashlight" };
    static readonly string[] Names = { "펜","숟가락","금속컵","물병","서류철","USB","데이터 샤드","휴대 호출기","손전등" };
    static readonly float[] Mass = { .018f,.04f,.18f,.4f,.22f,.025f,.06f,.12f,.24f };
    public static string DefPath(string id) => Root+"06.Data/Items/Item_"+id+".asset";
    public static string PrefabPath(string id) => Root+"04.Prefabs/Items/"+id+".prefab";

    static void CreateItem(int index)
    {
        string id=Items[index];
        string folder=index>=1 && index<=3 || id=="Pager" ? "B5" : "Common";
        var model=AssetDatabase.LoadAssetAtPath<GameObject>(Root+"05.Model/Props/"+folder+"/Pickup_"+id+".fbx");
        if (!model) throw new InvalidOperationException(id+" model");
        var data=AssetDatabase.LoadAssetAtPath<ItemDefinition>(DefPath(id));
        if(!data){data=ScriptableObject.CreateInstance<ItemDefinition>();AssetDatabase.CreateAsset(data,DefPath(id));}
        var obj=new GameObject(id);
        try
        {
            var art=(GameObject)PrefabUtility.InstantiatePrefab(model,obj.transform);
            var renderer=art.GetComponentInChildren<MeshRenderer>();
            var size=renderer.bounds.size;
            if(id=="Pen" || id=="Spoon" || id=="Flashlight")
            {
                Vector3 longest=size.y>size.x && size.y>size.z?Vector3.up:size.x>size.z?Vector3.right:Vector3.forward;
                art.transform.rotation=Quaternion.FromToRotation(longest,Vector3.forward)*art.transform.rotation;
            }
            else if(id=="DocumentFolder" || id=="UsbDrive" || id=="DataShard" || id=="Pager")
            {
                Vector3 thin=size.y<size.x && size.y<size.z?Vector3.up:size.x<size.z?Vector3.right:Vector3.forward;
                art.transform.rotation=Quaternion.FromToRotation(thin,Vector3.up)*art.transform.rotation;
            }
            var bounds=renderer.bounds;
            art.transform.position-=bounds.center;
            var rb=obj.AddComponent<Rigidbody>();rb.mass=Mass[index];rb.interpolation=RigidbodyInterpolation.Interpolate;
            rb.collisionDetectionMode=CollisionDetectionMode.ContinuousDynamic;
            obj.AddComponent<BoxCollider>().size=Vector3.Max(bounds.size,Vector3.one*.012f);
            obj.AddComponent<ThrownObject>();
            var world=new SerializedObject(obj.AddComponent<WorldItem>());
            world.FindProperty("definition").objectReferenceValue=data;
            world.ApplyModifiedPropertiesWithoutUndo();
            var prefab=PrefabUtility.SaveAsPrefabAsset(obj,PrefabPath(id));
            var so=new SerializedObject(data);
            so.FindProperty("displayName").stringValue=Names[index];
            so.FindProperty("worldPrefab").objectReferenceValue=prefab.GetComponent<ThrownObject>();
            so.FindProperty("gripOffset").vector3Value=id=="DocumentFolder" ? new Vector3(bounds.extents.x*.65f,0,-bounds.extents.z*.55f) :
                new Vector3(0, 0, -bounds.extents.z*.35f);
            so.ApplyModifiedPropertiesWithoutUndo();
            if(!ThrowFlight.TryShape(data.WorldPrefab,out _,out _)) throw new InvalidOperationException("Invalid pickup "+id);
        }
        finally { UnityEngine.Object.DestroyImmediate(obj); }
    }

    static void EquipGuards()
    {
        var pistol=AssetDatabase.LoadAssetAtPath<ItemDefinition>(DefPath("Pistol"));
        var config=new SerializedObject(pistol);
        config.FindProperty("initialRounds").intValue=3;
        config.FindProperty("swapShotRange").floatValue=30;
        config.ApplyModifiedPropertiesWithoutUndo();
        var guard=PrefabUtility.LoadPrefabContents(GuardPath);
        try
        {
            var equipment=guard.GetComponent<GuardLoadout>() ?? guard.AddComponent<GuardLoadout>();
            var so=new SerializedObject(equipment);
            so.FindProperty("carriedItem").objectReferenceValue=pistol;
            so.FindProperty("characterVisual").objectReferenceValue=guard.GetComponentInChildren<Animator>().transform;
            so.ApplyModifiedPropertiesWithoutUndo();
            PrefabUtility.SaveAsPrefabAsset(guard,GuardPath);
        }
        finally { PrefabUtility.UnloadPrefabContents(guard); }
    }

    static GameObject Spawn(string path,Transform parent)
    {
        var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(path);
        if(!prefab) throw new InvalidOperationException(path);
        return (GameObject)PrefabUtility.InstantiatePrefab(prefab,parent);
    }

    static Vector3 ClearFloor(Vector3 near,Vector3 halfSize)
    {
        Vector3[] offsets={Vector3.zero,Vector3.left,Vector3.right,Vector3.forward,Vector3.back,Vector3.left+Vector3.back,Vector3.right+Vector3.forward};
        foreach(var offset in offsets)
        {
            var top=near+offset+Vector3.up*.45f;
            if(!Physics.Raycast(top,Vector3.down,out var floor,.85f,~0,QueryTriggerInteraction.Ignore) || floor.normal.y<.96f) continue;
            if(!Physics.CheckBox(floor.point+Vector3.up*(halfSize.y+.016f),halfSize,Quaternion.identity,~0,QueryTriggerInteraction.Ignore)) return floor.point;
        }
        throw new InvalidOperationException("No clear floor near "+near);
    }

    static void PlaceCart(Transform group,string room,Vector3 near,string[] ids)
    {
        var feet=ClearFloor(near,new Vector3(.46f,.55f,.28f));
        var cart=Spawn(Root+"05.Model/Props/Common/LP_SampleTrolley.prefab",group);
        cart.name=room+"_PickupCart";
        cart.transform.position=feet;
        SetShelfContents(group,cart,ids);
        PrefabUtility.RecordPrefabInstancePropertyModifications(cart.transform);
        Debug.Log(room+" pickup cart "+feet.ToString("F3"));
    }

    // 원본 시료 카트의 케이스와 시료통만 제외한 메시를 두 카트에서 공유한다.
    static Mesh EmptyTopMesh(MeshFilter filter, Transform cart)
    {
        const string path=Root+"05.Model/Props/B5/B5_PickupCartShelf.asset";
        var variant=AssetDatabase.LoadAssetAtPath<Mesh>(path);
        if(variant) return variant;
        var source=filter.sharedMesh;
        variant=UnityEngine.Object.Instantiate(source);
        variant.name="B5_PickupCartShelf";
        var toCart=cart.worldToLocalMatrix*filter.transform.localToWorldMatrix;
        var inside=source.vertices.Select(vertex=>{
            var v=toCart.MultiplyPoint3x4(vertex);
            return v.y>.85f && Mathf.Abs(v.x)<.35f && Mathf.Abs(v.z)<.20f;
        }).ToArray();
        int removed=0;
        for(int sub=0;sub<source.subMeshCount;sub++){
            var input=source.GetTriangles(sub);var keep=new List<int>(input.Length);
            for(int i=0;i<input.Length;i+=3){
                if(inside[input[i]]&&inside[input[i+1]]&&inside[input[i+2]]){removed++;continue;}
                keep.Add(input[i]);keep.Add(input[i+1]);keep.Add(input[i+2]);
            }
            variant.SetTriangles(keep,sub,false);
        }
        if(removed==0)throw new InvalidOperationException("Cart accessories missing from source geometry");
        AssetDatabase.CreateAsset(variant,path);
        return variant;
    }

    static void SetShelfContents(Transform group,GameObject cart,string[] ids)
    {
        var feet=cart.transform.position;
        var filter=cart.GetComponentsInChildren<MeshFilter>().Single();
        filter.sharedMesh=EmptyTopMesh(filter,cart.transform);
        PrefabUtility.RecordPrefabInstancePropertyModifications(filter);
        foreach(var box in cart.GetComponentsInChildren<BoxCollider>()){
            box.enabled=false;
            PrefabUtility.RecordPrefabInstancePropertyModifications(box);
        }
        var shelf=filter.GetComponent<MeshCollider>() ?? filter.gameObject.AddComponent<MeshCollider>();
        shelf.sharedMesh=filter.sharedMesh;
        if(PrefabUtility.IsPartOfPrefabInstance(shelf))PrefabUtility.RecordPrefabInstancePropertyModifications(shelf);
        Physics.SyncTransforms();
        Vector3[] slots={new Vector3(-.22f,0,-.11f),new Vector3(.18f,0,-.11f),new Vector3(-.22f,0,.12f),new Vector3(.18f,0,.12f)};
        for(int i=0;i<ids.Length;i++)
        {
            Vector3 slot = ids[i]=="DocumentFolder" ? new Vector3(-.17f,0f,-.075f) : slots[i];
            var from=feet+slot+Vector3.up*1.5f;
            if(!shelf.Raycast(new Ray(from,Vector3.down),out var hit,1.4f) || hit.normal.y<.85f || Mathf.Abs(hit.point.y-feet.y-.848f)>.02f)
                throw new InvalidOperationException("No shelf under "+ids[i]+" at "+from);
            var existing=group.Find(ids[i]);
            var item=existing ? existing.gameObject : Spawn(PrefabPath(ids[i]),group);
            if(ids[i]=="DocumentFolder") item.transform.rotation=Quaternion.Euler(0,90,0);
            var box=item.GetComponent<BoxCollider>();
            item.transform.position=hit.point+Vector3.up*(box.size.y*.5f+.003f);
            PrefabUtility.RecordPrefabInstancePropertyModifications(item.transform);
        }
    }

    public static void RefreshCarts()
    {
        var scene=EditorSceneManager.OpenScene(B5);
        var group=GameObject.Find("B5_UsableItems").transform;
        SetShelfContents(group,group.Find("C01_PickupCart").gameObject,new[]{"Pen","Spoon","MetalCup","WaterBottle"});
        SetShelfContents(group,group.Find("C02_PickupCart").gameObject,new[]{"DocumentFolder","UsbDrive","DataShard","Pager"});
        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene);
        AssetDatabase.SaveAssets();
    }

    public static void Run()
    {
        for(int i=0;i<Items.Length;i++) CreateItem(i);
        EquipGuards();
        AssetDatabase.SaveAssets();
        var scene=EditorSceneManager.OpenScene(B5);
        if(!GameObject.Find("B5_UsableItems"))
        {
            var group=new GameObject("B5_UsableItems");
            Physics.SyncTransforms();
            PlaceCart(group.transform,"C01",new Vector3(-10.7f,-82f,-9.6f),new[]{"Pen","Spoon","MetalCup","WaterBottle"});
            PlaceCart(group.transform,"C02",new Vector3(-24.95f,-82f,20f),new[]{"DocumentFolder","UsbDrive","DataShard","Pager"});
            var pos=ClearFloor(new Vector3(-22,-82,18),new Vector3(.34f,.9f,.34f));
            var guard=Spawn(GuardPath,group.transform);
            guard.name="B5_ControlGuard";
            guard.transform.SetPositionAndRotation(pos,Quaternion.Euler(0,30,0));
            PrefabUtility.RecordPrefabInstancePropertyModifications(guard.transform);
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene);
        }
        scene=EditorSceneManager.OpenScene(Review);
        if(!GameObject.Find("Flashlight"))
        {
            var stand=GameObject.Find("소품 받침대").GetComponent<BoxCollider>().bounds;
            var lamp=Spawn(PrefabPath("Flashlight"),null);
            lamp.transform.position=new Vector3(stand.center.x+.25f,stand.max.y+lamp.GetComponent<BoxCollider>().size.y*.5f+.003f,stand.center.z);
            PrefabUtility.RecordPrefabInstancePropertyModifications(lamp.transform);
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene);
        }
        Debug.Log("B5_ITEM_LOOP_AUTHORED");
    }
}
