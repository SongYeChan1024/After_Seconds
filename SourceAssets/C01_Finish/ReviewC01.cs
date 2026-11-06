using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEngine.SceneManagement;
using UnityEditor.SceneManagement;
using UnityEngine.Rendering.Universal;
public static class ReviewC01 {
    static string O=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../../Docs/검수/2026-11-07_C01_Finish/"));
    static void Shot(string file,Vector3 pos,Vector3 look,float fov=75) {
        var go=new GameObject("C01_Review_Temporary");var c=go.AddComponent<Camera>();
        c.transform.position=pos;c.transform.LookAt(look);c.nearClipPlane=.04f;c.farClipPlane=250;c.fieldOfView=fov;
        c.clearFlags=CameraClearFlags.SolidColor;c.backgroundColor=new Color(.027f,.037f,.05f);
        c.GetUniversalAdditionalCameraData().renderPostProcessing=false;c.allowMSAA=true;
        var rt=new RenderTexture(1600,1000,24){antiAliasing=4};var prior=RenderTexture.active;Texture2D tex=null;
        try{c.targetTexture=rt;c.Render();RenderTexture.active=rt;tex=new Texture2D(1600,1000,TextureFormat.RGB24,false);tex.ReadPixels(new Rect(0,0,1600,1000),0,0);tex.Apply();File.WriteAllBytes(O+file+".png",tex.EncodeToPNG());}
        finally{RenderTexture.active=prior;c.targetTexture=null;if(tex)UnityEngine.Object.DestroyImmediate(tex);UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(go);}
    }
    static object Capture(string phase) {
        var s=SceneManager.GetActiveScene();if(s.isDirty||Application.isPlaying||!s.path.EndsWith("Level_B5_Circular.unity"))throw new Exception("Saved B5 edit scene required");
        Directory.CreateDirectory(O);var hidden=s.GetRootGameObjects().Where(g=>g.name.StartsWith("Player")).SelectMany(g=>g.GetComponentsInChildren<Renderer>()).ToDictionary(r=>r,r=>r.enabled);
        try{foreach(var r in hidden.Keys)r.enabled=false;
            Shot(phase+"_Observation",new Vector3(-9.2f,-80.35f,-10),new Vector3(-20.3f,-78.4f,-4.9f));
            Shot(phase+"_WestExit",new Vector3(-20.6f,-80.35f,-10.3f),new Vector3(-30,-79.5f,-13.2f));
            Shot(phase+"_Crown",new Vector3(-15,-78.2f,-10),new Vector3(-15,-68,-10));
            Shot(phase+"_Wall",new Vector3(-15,-79.3f,-9),new Vector3(-15,-76,-19.7f));
            if(phase=="After"){
                Shot("After_ConsoleA",new Vector3(-17.3f,-80.35f,-3.3f),new Vector3(-20.8f,-80.9f,-4),65);
                Shot("After_ConsoleB",new Vector3(-8.4f,-80.35f,-10.7f),new Vector3(-9.8f,-81,-15),65);
                Shot("After_Analyzer",new Vector3(-17.7f,-80.35f,-14.4f),new Vector3(-20.9f,-80.9f,-16.7f),65);
            }
        }finally{foreach(var kv in hidden)kv.Key.enabled=kv.Value;EditorSceneManager.OpenScene(s.path);}
        return new{phase,images=phase=="After"?7:4,output=O};
    }
    public static object Before()=>Capture("Before");
    public static object After()=>Capture("After");
}
