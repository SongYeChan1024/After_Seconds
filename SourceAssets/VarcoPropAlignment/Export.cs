using System;using System.IO;using System.Linq;using System.Collections.Generic;using UnityEngine;using UnityEditor;using UnityEngine.SceneManagement;using Newtonsoft.Json;using Newtonsoft.Json.Linq;
// Read-only export in prop-root coordinates; includes all authored LODs and UVs.
public static class VAExport {
 static string R=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 public static object Run(){var s=SceneManager.GetActiveScene();if(Application.isPlaying||s.isDirty||!s.path.EndsWith("Level_B2_Circular.unity"))throw new Exception("Saved B2 required");
 var h=R+"/SourceAssets/VarcoPropAlignment";var d=JObject.Parse(File.ReadAllText(h+"/before.json"));var names=new[]{"BM_CoolingPump","BM_HVACUnit","BM_Centrifuge","B2_EmergencyGenerator","SD_CylinderTrolley"};var all=s.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Transform>(true)).ToArray();var records=new List<object>();
 foreach(var group in d["rows"].Where(x=>names.Contains((string)x["model"])).GroupBy(x=>(string)x["model"])){
 var row=group.First();var root=all.Single(t=>t.name==(string)row["name"]);int i=0;
 foreach(var r in root.GetComponentsInChildren<MeshRenderer>().Where(x=>x.enabled)){var mesh=r.GetComponent<MeshFilter>().sharedMesh;var mat=root.worldToLocalMatrix*r.localToWorldMatrix;string key=group.Key+"_"+i++;if(group.Key=="BM_HVACUnit"&&i==1){mesh=AssetDatabase.LoadAllAssetsAtPath("Assets/Afrer_Seconds/05.Model/Props/B2/Props_HVACUnit.fbx").OfType<Mesh>().OrderByDescending(x=>x.vertexCount).First();key="BM_HVACUnit_source";}var v=mesh.vertices;var uv=mesh.uv;var normals=mesh.normals;
 using(var w=new BinaryWriter(File.Create(h+"/"+key+".bin"))){w.Write(v.Length);w.Write(mesh.subMeshCount);foreach(var p in v){var q=mat.MultiplyPoint3x4(p);w.Write(q.x);w.Write(q.y);w.Write(q.z);}foreach(var p in uv){w.Write(p.x);w.Write(p.y);}for(int j=0;j<mesh.subMeshCount;j++){var ix=mesh.GetIndices(j);w.Write(ix.Length);foreach(int k in ix)w.Write(k);}}
 records.Add(new{key,model=group.Key,root=root.name,path=(string)row["path"],renderer=GlobalObjectId.GetGlobalObjectIdSlow(r).ToString(),asset=AssetDatabase.GetAssetPath(mesh),mesh=mesh.name,vertices=v.Length,triangles=mesh.triangles.Length/3,uvs=uv.Length,materials=r.sharedMaterials.Select(a=>AssetDatabase.GetAssetPath(a)).ToArray()});
 }}File.WriteAllText(h+"/export.json",JsonConvert.SerializeObject(records,Formatting.Indented));return new{meshes=records.Count};}
}
