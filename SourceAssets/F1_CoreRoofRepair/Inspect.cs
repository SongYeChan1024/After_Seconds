// 검수 순서: 저장된 1F 편집 상태 확인 -> 누락 참조와 지붕 조사 -> 임시 카메라 캡처 -> 임시 리소스 복구.
using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEngine.SceneManagement;
using UnityEngine.Rendering.Universal;
using Newtonsoft.Json;
public static class F1ResumeInspect
{
    static readonly string Output = Path.Combine(Path.GetTempPath(), "AfterSeconds_1F_Review_20261113");
    public static object Run()
    {
        var scene = SceneManager.GetActiveScene();
        if (scene.isDirty || Application.isPlaying || !scene.path.EndsWith("Level_1F_Factory.unity")) throw new Exception("Saved 1F edit mode required.");
        var all = scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<Transform>(true)).ToArray();
        var result = new {
            scene = scene.path,
            missingScripts = all.Sum(t => GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject)),
            missingMeshes = all.SelectMany(t => t.GetComponents<MeshFilter>()).Where(f => !f.sharedMesh).Select(f => f.name).ToArray(),
            missingMaterials = all.SelectMany(t => t.GetComponents<Renderer>()).Where(r => r.sharedMaterials.Any(m => !m || !m.shader)).Select(r => r.name).ToArray(),
            roofs = all.Where(t => t.name.StartsWith("AE_") && t.name.EndsWith("_Roof")).Select(t => new {
                t.name, position = t.position.ToString(),
                meshes = t.GetComponentsInChildren<MeshFilter>(true).Select(f => new { f.name, asset = AssetDatabase.GetAssetPath(f.sharedMesh), vertices = f.sharedMesh ? f.sharedMesh.vertexCount : 0 }).ToArray()
            }).ToArray()
        };
        File.WriteAllText(Path.Combine(Output, "audit.json"), JsonConvert.SerializeObject(result, Formatting.Indented));
        Shot("VA", new Vector3(-41.5f,1.7f,24.8f), new Vector3(-44,1.9f,32.8f),88);
        Shot("VB", new Vector3(44,1.7f,-28), new Vector3(48.8f,2.8f,-25),82);
        Shot("VL", new Vector3(42,1.7f,29.5f), new Vector3(48.8f,2.8f,31),82);
        Shot("Production",new Vector3(-23,1.7f,-10),new Vector3(-8,1.6f,5),86);
        Shot("Approach",new Vector3(-86,1.7f,-31),new Vector3(-20,5,4),67);
        Shot("Courtyard",new Vector3(5,1.7f,36),new Vector3(2,5,10),80);
        Shot("Exterior",new Vector3(-44,1.7f,-7),new Vector3(-20,5,8),75);
        return new { output = Output, audit = result, dirtyAfter = scene.isDirty };
    }
    static void Shot(string name,Vector3 pos,Vector3 target,float fov)
    {
        var go = new GameObject("Temporary1FReviewCamera") { hideFlags=HideFlags.HideAndDontSave };
        var cam=go.AddComponent<Camera>();
        cam.transform.position=pos;cam.transform.LookAt(target);cam.fieldOfView=fov;cam.nearClipPlane=.03f;cam.farClipPlane=400;cam.useOcclusionCulling=false;
        cam.GetUniversalAdditionalCameraData().renderPostProcessing=false;
        var rt=new RenderTexture(1600,1000,24){antiAliasing=4};var active=RenderTexture.active;var asyncBefore=ShaderUtil.allowAsyncCompilation;Texture2D tex=null;
        try { ShaderUtil.allowAsyncCompilation=false;cam.targetTexture=rt;cam.Render();cam.Render();RenderTexture.active=rt;tex=new Texture2D(1600,1000,TextureFormat.RGB24,false);tex.ReadPixels(new Rect(0,0,1600,1000),0,0);tex.Apply();File.WriteAllBytes(Path.Combine(Output,name+".jpg"),tex.EncodeToJPG(92)); }
        finally { ShaderUtil.allowAsyncCompilation=asyncBefore;RenderTexture.active=active;cam.targetTexture=null;if(tex)UnityEngine.Object.DestroyImmediate(tex);UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(go); }
    }
}