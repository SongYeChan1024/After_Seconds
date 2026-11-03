// 작성자 송예찬 · 2026-11-03 · 임시 Editor 작업 도구
// [의사코드]
// 1. B5 Room01의 기존 구조와 사용자 회전값을 기록한다.
// 2. 12×14m, 높이7.2m의 방 외형을 기존 공용 모듈로 먼저 만든다.
// 3. 타일의 실측 bounds와 충돌/스크립트 없음이 확인된 뒤 기존 구조 치수만 바꾼다.
// 4. 겹치는 옛 외형 Renderer만 숨긴다. 원본 오브젝트와 뒤집힌 천장 회전은 보존한다.
// 5. 조명 기구를 올리고 기존 색상을 유지한다. 작업 결과는 tmp에 기록하며 씬은 저장하지 않는다.

// [코딩]
#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using Object = UnityEngine.Object;

public static class HabitatArchitecture
{
    const string Source = "Assets/Afrer_Seconds/05.Model/Environment/B5/";
    const string Marker = "Habitat_Architecture_Visuals";

    [Serializable] public sealed class Pose
    {
        public Vector3 localPosition;
        public Quaternion localRotation;
        public Vector3 localScale;
        public Pose(Transform t) { localPosition=t.localPosition; localRotation=t.localRotation; localScale=t.localScale; }
    }
    [Serializable] public sealed class Change
    {
        public string path;
        public string action;
        public Pose before;
        public Pose after;
        public string note;
    }
    [Serializable] public sealed class Surface
    {
        public string name;
        public string sourcePrefab;
        public int tiles;
        public Bounds requestedRoomBounds;
        public Bounds actualWorldBounds;
        public float worldBoundsError;
    }
    [Serializable] public sealed class LightChange
    {
        public string path;
        public float rangeBefore, rangeAfter, intensityBefore, intensityAfter;
        public Color colorBefore, colorAfter;
    }
    [Serializable] public sealed class Report
    {
        public string scene;
        public string room;
        public string status;
        public string note = "Room01-only visual/collision envelope expansion. Scene remains unsaved for caller review.";
        public List<Change> touchedOriginalPaths = new List<Change>();
        public List<string> hiddenRendererPaths = new List<string>();
        public List<Surface> surfaces = new List<Surface>();
        public List<LightChange> lights = new List<LightChange>();
        public int newTiles;
        public int newColliders;
        public int newRuntimeScripts;
        public int hiddenSourceInstances;
        public int preservedLegacyFloorRotations;
        public int preservedLegacyCeilingRotations;
    }
    public static Report LastReport { get; private set; }

    sealed class Structure
    {
        public string name;
        public Vector3 pos, size;
        public Structure(string n, Vector3 p, Vector3 s) { name=n; pos=p; size=s; }
    }

    // [의사코드] 새 모듈의 기하 검증이 끝나기 전에는 기존 물리 구조를 변경하지 않는다.
    public static void Apply(Transform room)
    {
        if (EditorApplication.isPlaying) throw new InvalidOperationException("Edit mode is required.");
        if (!room || room.name != "Room01_Isolation" || !room.gameObject.scene.name.Contains("B5"))
            throw new ArgumentException("Only B5 Room01_Isolation is authorized.");
        if (room.Find(Marker)) throw new InvalidOperationException("Habitat architecture already exists; restore/review before rerunning.");
        if ((room.lossyScale-Vector3.one).sqrMagnitude>.000001f)
            throw new InvalidOperationException("Room01 must retain meter scale; dome scale is separate.");

        var report = new Report { scene=room.gameObject.scene.path, room=PathOf(room), status="building" };
        LastReport = report;
        var specs = new[] {
            new Structure("Floor_Room01",new Vector3(0,-.15f,9),new Vector3(12,.3f,14)),
            new Structure("Wall_West",new Vector3(-6.12f,3.6f,9),new Vector3(.24f,7.2f,14.48f)),
            new Structure("Wall_East",new Vector3(6.12f,3.6f,9),new Vector3(.24f,7.2f,14.48f)),
            new Structure("Wall_South",new Vector3(0,3.6f,16.12f),new Vector3(12,7.2f,.24f)),
            new Structure("Wall_North_Left",new Vector3(-3.5f,3.6f,1.88f),new Vector3(5,7.2f,.24f)),
            new Structure("Wall_North_Right",new Vector3(3.5f,3.6f,1.88f),new Vector3(5,7.2f,.24f)),
            new Structure("Wall_North_AboveDoor",new Vector3(0,5,1.88f),new Vector3(2,4.4f,.24f)),
            new Structure("Ceiling_Main",new Vector3(0,7.32f,9),new Vector3(12.48f,.24f,14.48f))
        };
        var geometry = room.Find("Geometry");
        if (!geometry) throw new InvalidOperationException("Room01 Geometry missing.");
        var originals = specs.ToDictionary(s=>s.name,s=>geometry.Find(s.name));
        foreach (var s in specs)
        {
            var t=originals[s.name];
            if (!t || !t.GetComponent<BoxCollider>() || !t.GetComponent<MeshFilter>())
                throw new InvalidOperationException("Missing original structure: "+s.name);
        }
        var wall=Load("Env_ConcreteWall_4m.prefab");
        var floor=Load("Env_FloorSlab_4m.prefab");
        var ceiling=Load("Env_CeilingPanel_4m.prefab");
        var group=new GameObject(Marker);
        group.transform.SetParent(room,false);
        try
        {
            // 3열×4행. 바닥 상면만 물리 바닥보다2mm 올려 이전 접합부와의 겹침을 피한다.
            BuildTiles(group.transform,"Floor",floor,new Bounds(new Vector3(0,-.058f,9),new Vector3(12,.12f,14)),3,1,4,Quaternion.Euler(180,0,0),report);
            // Source ceiling detail faces +Y; only new visual children flip so detail faces down.
            BuildTiles(group.transform,"Ceiling",ceiling,new Bounds(new Vector3(0,7.275f,9),new Vector3(12.48f,.15f,14.48f)),3,1,4,Quaternion.Euler(180,0,0),report);
            foreach (var s in specs.Where(s=>s.name.StartsWith("Wall_") && s.name!="Wall_North_AboveDoor"))
            {
                bool alongZ=s.size.z>s.size.x;
                int lengthTiles=Mathf.CeilToInt((alongZ?s.size.z:s.size.x)/4f);
                BuildTiles(group.transform,s.name,wall,new Bounds(s.pos,s.size),alongZ?1:lengthTiles,2,alongZ?lengthTiles:1,
                    alongZ?Quaternion.Euler(0,90,0):Quaternion.identity,report);
            }
            BuildFlatDoorHeader(group.transform,originals["Wall_North_AboveDoor"],wall,
                new Bounds(new Vector3(0,5,1.88f),new Vector3(2,4.4f,.24f)),report);
            report.newColliders=group.GetComponentsInChildren<Collider>(true).Length;
            report.newRuntimeScripts=group.GetComponentsInChildren<MonoBehaviour>(true).Length;
            if (report.newColliders!=0 || report.newRuntimeScripts!=0)
                throw new InvalidOperationException("Visual architecture contains gameplay/physics components.");
        }
        catch
        {
            Object.DestroyImmediate(group);
            report.status="failed_before_original_mutation";
            Write(report);
            throw;
        }

        // Apply only the eight approved structural transforms; each original local rotation stays exact.
        foreach (var s in specs)
        {
            var t=originals[s.name];var before=new Pose(t);
            Undo.RecordObject(t,"Expand Room01 habitat envelope");
            t.localPosition=s.pos;t.localScale=s.size;
            report.touchedOriginalPaths.Add(new Change { path=PathOf(t),action="approved structure expansion",before=before,after=new Pose(t),note="Original rotation and BoxCollider parameters retained; transform updates collision envelope." });
            HideRenderers(t,report);
        }
        var oldVisuals=room.Find("VARCO_Visuals");
        if (oldVisuals)
        {
            foreach (Transform t in oldVisuals)
            {
                if (!t.name.StartsWith("Room01_",StringComparison.Ordinal)) continue;
                if (t.name.StartsWith("Room01_Floor_")) report.preservedLegacyFloorRotations++;
                if (t.name.StartsWith("Room01_Ceiling_")) report.preservedLegacyCeilingRotations++;
                HideRenderers(t,report);report.hiddenSourceInstances++;
            }
        }
        var lighting=room.Find("Lighting");
        foreach (string name in new[]{"Light_01A","Light_01B","Light_01C","Light_01D","Cell_Lamp"})
        {
            var t=lighting?lighting.Find(name):null;if (!t) continue;
            var before=new Pose(t);var pos=t.localPosition;pos.y=6.85f;
            Undo.RecordObject(t,"Raise habitat ceiling fixture");t.localPosition=pos;
            report.touchedOriginalPaths.Add(new Change {path=PathOf(t),action="raise existing ceiling light fixture",before=before,after=new Pose(t),note="X/Z, rotation, scale and authored fixture details retained."});
            foreach (var light in t.GetComponentsInChildren<Light>(true))
            {
                var record=new LightChange {path=PathOf(light.transform),rangeBefore=light.range,intensityBefore=light.intensity,colorBefore=light.color};
                Undo.RecordObject(light,"Adjust range for taller habitat");
                light.range=name=="Cell_Lamp"?11f:13f;light.intensity=name=="Cell_Lamp"?2.4f:4.2f;
                record.rangeAfter=light.range;record.intensityAfter=light.intensity;record.colorAfter=light.color;
                report.lights.Add(record);EditorUtility.SetDirty(light);
            }
        }
        report.status="applied_unsaved";
        Physics.SyncTransforms();
        EditorSceneManager.MarkSceneDirty(room.gameObject.scene);
        Write(report);
    }

    static GameObject Load(string name)
    {
        var p=AssetDatabase.LoadAssetAtPath<GameObject>(Source+name);
        if (!p) throw new InvalidOperationException("Missing source prefab: "+Source+name);
        if (p.GetComponentsInChildren<Collider>(true).Length!=0 || p.GetComponentsInChildren<Rigidbody>(true).Length!=0 || p.GetComponentsInChildren<MonoBehaviour>(true).Length!=0)
            throw new InvalidOperationException("Expected a visual-only architecture prefab: "+name);
        return p;
    }
    static void BuildTiles(Transform group,string name,GameObject prefab,Bounds target,int nx,int ny,int nz,Quaternion facing,Report report)
    {
        var surface=new GameObject(name);surface.transform.SetParent(group,false);
        Vector3 size=new Vector3(target.size.x/nx,target.size.y/ny,target.size.z/nz);
        for (int x=0;x<nx;x++) for (int y=0;y<ny;y++) for (int z=0;z<nz;z++)
        {
            var holder=new GameObject(name+"_"+x+"_"+y+"_"+z);holder.transform.SetParent(surface.transform,false);
            var instance=(GameObject)PrefabUtility.InstantiatePrefab(prefab,group.gameObject.scene);
            instance.transform.SetParent(holder.transform,false);instance.transform.localPosition=Vector3.zero;
            instance.transform.localRotation=facing;instance.transform.localScale=Vector3.one;
            var bounds=MeshBounds(instance,holder.transform);
            var scale=new Vector3(size.x/bounds.size.x,size.y/bounds.size.y,size.z/bounds.size.z);
            holder.transform.localScale=scale;
            var centre=target.min+Vector3.Scale(size,new Vector3(x+.5f,y+.5f,z+.5f));
            holder.transform.localPosition=centre-Vector3.Scale(bounds.center,scale);
            foreach (var t in instance.GetComponentsInChildren<Transform>(true))
                GameObjectUtility.SetStaticEditorFlags(t.gameObject,StaticEditorFlags.BatchingStatic|StaticEditorFlags.ReflectionProbeStatic);
            foreach (var renderer in instance.GetComponentsInChildren<Renderer>(true).Where(r=>r.enabled))
            { renderer.shadowCastingMode=ShadowCastingMode.On;renderer.receiveShadows=true; }
        }
        var actual=RendererBounds(surface);var expected=TransformBounds(group,target);
        float error=BoundsError(actual,expected);
        if (error>.004f) throw new InvalidOperationException("Tile bounds mismatch "+name+": "+error);
        int count=nx*ny*nz;report.newTiles+=count;
        report.surfaces.Add(new Surface {name=name,sourcePrefab=AssetDatabase.GetAssetPath(prefab),tiles=count,requestedRoomBounds=target,actualWorldBounds=actual,worldBoundsError=error});
    }
    static void BuildFlatDoorHeader(Transform group,Transform old,GameObject wall,Bounds target,Report report)
    {
        // Only a plain upper panel spans the 2m doorway, without introducing an authored door/window.
        var go=new GameObject("Wall_North_AboveDoor_FlatPanel");go.transform.SetParent(group,false);
        var mesh=old.GetComponent<MeshFilter>().sharedMesh;
        if (!mesh) throw new InvalidOperationException("Original door header mesh is missing.");
        var meshBounds=mesh.bounds;
        var fit=new Vector3(target.size.x/meshBounds.size.x,target.size.y/meshBounds.size.y,target.size.z/meshBounds.size.z);
        go.transform.localScale=fit;go.transform.localPosition=target.center-Vector3.Scale(meshBounds.center,fit);
        go.AddComponent<MeshFilter>().sharedMesh=mesh;
        var materials=wall.GetComponentsInChildren<Renderer>(true).Where(r=>r.enabled).SelectMany(r=>r.sharedMaterials).Where(m=>m).Distinct().ToArray();
        var material=materials.FirstOrDefault(m=>m.name.IndexOf("White",StringComparison.OrdinalIgnoreCase)>=0 || m.name.IndexOf("Body",StringComparison.OrdinalIgnoreCase)>=0);
        if (!material) material=materials.OrderByDescending(m=>m.HasProperty("_BaseColor")?m.GetColor("_BaseColor").grayscale:0).First();
        go.AddComponent<MeshRenderer>().sharedMaterial=material;
        var actual=RendererBounds(go);float error=BoundsError(actual,TransformBounds(group,target));
        if (error>.004f) throw new InvalidOperationException("Door header bounds mismatch.");
        report.newTiles++;
        report.surfaces.Add(new Surface {name="Wall_North_AboveDoor",sourcePrefab="Existing unit Cube mesh + shared "+AssetDatabase.GetAssetPath(material),tiles=1,requestedRoomBounds=target,actualWorldBounds=actual,worldBoundsError=error});
    }
    static Bounds MeshBounds(GameObject go,Transform space)
    {
        bool any=false;var result=new Bounds();
        foreach (var renderer in go.GetComponentsInChildren<MeshRenderer>(true).Where(r=>r.enabled && r.gameObject.activeInHierarchy))
        {
            var filter=renderer.GetComponent<MeshFilter>();if (!filter || !filter.sharedMesh) throw new InvalidOperationException("Missing source mesh.");
            if (renderer.sharedMaterials.Any(m=>!m || !m.shader)) throw new InvalidOperationException("Missing source material.");
            var b=filter.sharedMesh.bounds;var matrix=space.worldToLocalMatrix*renderer.transform.localToWorldMatrix;
            for (int x=0;x<2;x++) for (int y=0;y<2;y++) for (int z=0;z<2;z++)
            {
                var p=matrix.MultiplyPoint3x4(b.center+Vector3.Scale(b.extents,new Vector3(x==0?-1:1,y==0?-1:1,z==0?-1:1)));
                if (!any) {result=new Bounds(p,Vector3.zero);any=true;} else result.Encapsulate(p);
            }
        }
        if (!any || result.size.x<=0 || result.size.y<=0 || result.size.z<=0) throw new InvalidOperationException("Empty source mesh bounds.");
        return result;
    }
    static Bounds RendererBounds(GameObject go)
    {
        var rr=go.GetComponentsInChildren<Renderer>(true).Where(r=>r.enabled && r.gameObject.activeInHierarchy).ToArray();
        if (rr.Length==0) throw new InvalidOperationException("Empty visual surface.");
        var b=rr[0].bounds;foreach(var r in rr.Skip(1))b.Encapsulate(r.bounds);return b;
    }
    static Bounds TransformBounds(Transform t,Bounds b)
    {
        bool any=false;var result=new Bounds();
        for (int x=0;x<2;x++) for(int y=0;y<2;y++) for(int z=0;z<2;z++)
        {var p=t.TransformPoint(b.center+Vector3.Scale(b.extents,new Vector3(x==0?-1:1,y==0?-1:1,z==0?-1:1)));if(!any){result=new Bounds(p,Vector3.zero);any=true;}else result.Encapsulate(p);}
        return result;
    }
    static float BoundsError(Bounds a,Bounds b)
    {
        var d0=a.min-b.min;var d1=a.max-b.max;
        return new[]{Mathf.Abs(d0.x),Mathf.Abs(d0.y),Mathf.Abs(d0.z),Mathf.Abs(d1.x),Mathf.Abs(d1.y),Mathf.Abs(d1.z)}.Max();
    }
    static void HideRenderers(Transform t,Report report)
    {
        foreach(var r in t.GetComponentsInChildren<Renderer>(true))
        {if(r.enabled){report.hiddenRendererPaths.Add(PathOf(r.transform));Undo.RecordObject(r,"Preserve superseded habitat renderer");r.enabled=false;EditorUtility.SetDirty(r);}}
    }
    static string PathOf(Transform t) {return t.parent?PathOf(t.parent)+"/"+t.name:t.name;}
    static void Write(Report report)
    {
        var folder=Path.GetFullPath(Path.Combine(Application.dataPath,"../../../tmp/Habitat_20261103"));
        Directory.CreateDirectory(folder);File.WriteAllText(Path.Combine(folder,"habitat_architecture_report.json"),JsonUtility.ToJson(report,true));
    }
}
#endif

// [주석]
// - 폴더와 재질은 복제하지 않고 기존 B5 프리팹 한 벌을 공유한다.
// - 기존 Room01_Floor/Ceiling 9개씩은 오브젝트·회전을 보존해 숨긴다. 새12개씩만 활성화한다.
// - 문 개구부는 x±1, 높이0~2.8m를 그대로 비운다. Connector와 다른 방은 탐색하지 않는다.
// - 새 방 외형에는 Collider/Rigidbody/게임 스크립트를 넣지 않는다. 기존8개 BoxCollider의
//   Transform만 승인된 치수로 확장한다. 실제 씬 저장과 게임 카메라 검수는 호출자가 한다.
