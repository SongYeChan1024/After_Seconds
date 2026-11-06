using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEngine.SceneManagement;
using UnityEditor.SceneManagement;
using Newtonsoft.Json;
public static class ApplyRibs {
    const string E="Assets/Afrer_Seconds/05.Model/Environment/B5/";
    public static object SavePending(){var s=SceneManager.GetActiveScene();if(Application.isPlaying||!s.path.EndsWith("Level_B5_Circular.unity"))throw new Exception("B5 edit scene required");return new{saved=EditorSceneManager.SaveScene(s),dirty=s.isDirty};}
    public static object Run(){
        var s=SceneManager.GetActiveScene();
        if(s.isDirty||Application.isPlaying||!s.path.EndsWith("Level_B5_Circular.unity"))throw new Exception("Saved B5 edit scene required");
        var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular")).transform;
        var t=root.Find("C01_Experiment_Art/AF_C01_ThreePortalRibs");if(!t)throw new Exception("Missing target ribs");
        var messages=new List<string>();Application.LogCallback cb=(m,stack,type)=>{if(type==LogType.Warning||type==LogType.Error||type==LogType.Exception)messages.Add(type+": "+m);};Application.logMessageReceived+=cb;
        try{
            var names=new[]{"AF_C01_RibMetal","AF_C01_RibJoint","AF_C01_RibAnchor"};
            var colors=new[]{new Color(.47f,.55f,.60f),new Color(.32f,.40f,.45f),new Color(.57f,.63f,.67f)};
            var metal=new[]{.64f,.68f,.8f};var smooth=new[]{.43f,.5f,.6f};
            var mats=new Dictionary<string,Material>();
            for(int i=0;i<names.Length;i++){
                string path=E+"Materials/"+names[i]+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);
                if(!m){m=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(m,path);}
                m.SetColor("_BaseColor",colors[i]);m.SetFloat("_Metallic",metal[i]);m.SetFloat("_Smoothness",smooth[i]);m.SetFloat("_SpecularHighlights",1);m.SetFloat("_EnvironmentReflections",1);
                EditorUtility.SetDirty(m);AssetDatabase.SaveAssetIfDirty(m);mats[names[i]]=m;
            }
            string asset=E+"AF_C01_ThreePortalRibs.fbx";
            AssetDatabase.ImportAsset(asset,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);
            var importer=(ModelImporter)AssetImporter.GetAtPath(asset);
            foreach(var kv in mats)importer.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material),kv.Key),kv.Value);
            importer.SaveAndReimport();
            var model=AssetDatabase.LoadAssetAtPath<GameObject>(asset);
            var source=model.GetComponentInChildren<MeshFilter>();var sourceRenderer=source.GetComponent<Renderer>();
            var mf=t.GetComponentInChildren<MeshFilter>();var rr=mf.GetComponent<Renderer>();var collider=mf.GetComponent<MeshCollider>();
            Undo.RecordObjects(new UnityEngine.Object[]{mf,rr,collider},"C01 continuous symmetrical ribs");
            mf.sharedMesh=source.sharedMesh;rr.sharedMaterials=sourceRenderer.sharedMaterials;
            collider.sharedMesh=null;collider.sharedMesh=mf.sharedMesh;
            foreach(var c in new UnityEngine.Object[]{mf,rr,collider}){EditorUtility.SetDirty(c);PrefabUtility.RecordPrefabInstancePropertyModifications(c);}
            Physics.SyncTransforms();EditorSceneManager.MarkSceneDirty(s);EditorSceneManager.SaveScene(s);
            var result=new{asset,guid=AssetDatabase.AssetPathToGUID(asset),vertices=mf.sharedMesh.vertexCount,triangles=mf.sharedMesh.triangles.Length/3,materials=rr.sharedMaterials.Select(m=>m.name).ToArray(),colliderMatches=collider.sharedMesh==mf.sharedMesh,position=t.position.ToString("F4"),messages};
            var o=Path.GetFullPath(Path.Combine(Application.dataPath,"../../../Docs/검수/2026-11-07_C01_Finish/"));Directory.CreateDirectory(o);File.WriteAllText(o+"rib_import.json",JsonConvert.SerializeObject(result,Formatting.Indented));return result;
        }finally{Application.logMessageReceived-=cb;}
    }
}
