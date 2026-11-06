using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEngine.SceneManagement;
using Newtonsoft.Json;
public static class InspectC01 {
    static string PathOf(Transform t) => t.parent ? PathOf(t.parent)+"/"+t.name : t.name;
    public static object Run() {
        var s=SceneManager.GetActiveScene();
        var roots=s.GetRootGameObjects();
        var all=roots.SelectMany(g=>g.GetComponentsInChildren<Transform>(true)).ToArray();
        var targets=all.Where(t=>t.name.Contains("ThreePortal")||t.name=="C01_Experiment_Art"||t.name.Contains("CurvedLining")||t.name=="AF_B5_PortalCollars").ToArray();
        var details=targets.Select(t=>new {path=PathOf(t),pos=t.position.ToString("F4"),local=t.localPosition.ToString("F4"),rotation=t.eulerAngles.ToString("F4"),scale=t.lossyScale.ToString("F4"),active=t.gameObject.activeInHierarchy,
            meshes=t.GetComponentsInChildren<MeshFilter>().Where(m=>m.name.Contains("ThreePortal")||m.name.Contains("CurvedLining")||m.name.Contains("PortalCollars")).Select(m=>new {path=PathOf(m.transform),mesh=AssetDatabase.GetAssetPath(m.sharedMesh),verts=m.sharedMesh.vertexCount,bounds=m.GetComponent<Renderer>().bounds.ToString(),materials=m.GetComponent<Renderer>().sharedMaterials.Select(a=>new{a.name,path=AssetDatabase.GetAssetPath(a),color=a.HasProperty("_BaseColor")?a.GetColor("_BaseColor").ToString():"",metal=a.HasProperty("_Metallic")?a.GetFloat("_Metallic"):-1,smooth=a.HasProperty("_Smoothness")?a.GetFloat("_Smoothness"):-1}).ToArray()}).ToArray()}).ToArray();
        var c01=all.SingleOrDefault(t=>t.name=="C01_Experiment_Art");
        var result=new{scene=s.path,dirty=s.isDirty,playing=Application.isPlaying,roots=roots.Select(g=>g.name).ToArray(),details,children=c01?c01.Cast<Transform>().Select(t=>new{t.name,pos=t.localPosition.ToString("F3"),active=t.gameObject.activeSelf}).ToArray():null,player=roots.Where(g=>g.name.StartsWith("Player")).Select(g=>new{g.name,pos=g.transform.position.ToString("F4"),rotation=g.transform.eulerAngles.ToString("F4")}).ToArray()};
        var o=Path.GetFullPath(Path.Combine(Application.dataPath,"../../../SourceAssets/C01_Finish/inspection.json"));
        File.WriteAllText(o,JsonConvert.SerializeObject(result,Formatting.Indented));return result;
    }
}
