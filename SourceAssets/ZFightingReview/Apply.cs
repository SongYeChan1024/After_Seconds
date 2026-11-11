using System;using System.IO;using System.Linq;using System.Collections.Generic;using System.Security.Cryptography;
using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.SceneManagement;using UnityEngine.Rendering;
using Newtonsoft.Json;using Newtonsoft.Json.Linq;
// External repair tool: derives visual-only meshes, interpolates every existing
// vertex channel, and preserves all original meshes, colliders and transforms.
public static class ZFApply {
 static string PlanFolder="plans";
 static bool RebuildEmpty=false;
 public static object RepairEmpty(string name){RebuildEmpty=true;return Run(name);}
 public static object Residual(string name){PlanFolder="residual2";return Run(name);}
 public static object Finish(string name){PlanFolder="finish_plans";return Run(name);}
 public static object Precision(string name){PlanFolder="precision_plans";return Run(name);}
 static string Root=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 static string Id(UnityEngine.Object o)=>GlobalObjectId.GetGlobalObjectIdSlow(o).ToString();
 static string State(Scene s)=>JsonConvert.SerializeObject(s.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Transform>(true)).Select(t=>new{id=Id(t),name=t.name,parent=t.parent?Id(t.parent):"",p=new[]{t.localPosition.x,t.localPosition.y,t.localPosition.z},q=new[]{t.localRotation.x,t.localRotation.y,t.localRotation.z,t.localRotation.w},scale=new[]{t.localScale.x,t.localScale.y,t.localScale.z},active=t.gameObject.activeSelf,colliders=t.GetComponents<Collider>().Select(c=>new{id=Id(c),json=EditorJsonUtility.ToJson(c)})}));
 public static object Run(string name) {
  if(Application.isPlaying||SceneManager.GetActiveScene().isDirty)throw new Exception("Clean edit required");
  string h=Root+"/SourceAssets/ZFightingReview/";var plan=JObject.Parse(File.ReadAllText(h+PlanFolder+"/"+name+".json"));string scene=(string)plan["scene"];
  if((double)plan["maxRetriangulationAreaError"]>1e-5)throw new Exception("Coverage check failed");
  string protectedFile=h+(PlanFolder=="plans"?"protected_before.json":PlanFolder=="precision_plans"?"protected_before_precision.json":PlanFolder=="finish_plans"?"protected_before_finish.json":"protected_before_second.json");var hashes=JObject.Parse(File.ReadAllText(protectedFile));
  string hash=BitConverter.ToString(SHA256.Create().ComputeHash(File.ReadAllBytes(scene))).Replace("-","").ToLowerInvariant();
  if(!RebuildEmpty && hash!=(string)hashes[scene])throw new Exception("Scene changed since baseline: "+scene);
  var s=EditorSceneManager.OpenScene(scene);string before=State(s);var records=new List<object>();
  foreach(var group in plan["patches"].GroupBy(p=>(int)p["renderer"])) {
   var row=plan["rows"][group.Key];if(!GlobalObjectId.TryParse((string)row["id"],out var gid))throw new Exception("Bad renderer id");
   var r=GlobalObjectId.GlobalObjectIdentifierToObjectSlow(gid) as MeshRenderer;if(!r)throw new Exception("Renderer missing: "+row["path"]);
   var mf=r.GetComponent<MeshFilter>();if(RebuildEmpty&&mf.sharedMesh.vertexCount>0)continue;
   var original=mf.sharedMesh;
   if(RebuildEmpty)original=AssetDatabase.LoadAllAssetsAtPath((string)row["asset"]).OfType<Mesh>().First(m=>{AssetDatabase.TryGetGUIDAndLocalFileIdentifier(m,out string g,out long l);return g+"_"+l==(string)row["mesh"];});
   AssetDatabase.TryGetGUIDAndLocalFileIdentifier(original,out string guid,out long local);
   if(guid+"_"+local!=(string)row["mesh"])throw new Exception("Mesh baseline mismatch");
   var edits=group.OrderBy(p=>(int)p["submesh"]).Select(p=>new{submesh=(int)p["submesh"],edits=p["edits"]}).ToArray();
   string signature=(string)row["mesh"]+JsonConvert.SerializeObject(edits);string sha=BitConverter.ToString(SHA256.Create().ComputeHash(System.Text.Encoding.UTF8.GetBytes(signature))).Replace("-","").Substring(0,16).ToLowerInvariant();
   string src=AssetDatabase.GetAssetPath(original);string folder=src.StartsWith("Assets/")?Path.GetDirectoryName(src).Replace('\\','/'):"Assets/Afrer_Seconds/05.Model/Environment/Common";
   string path=folder+"/ZF_"+sha+".asset";var result=AssetDatabase.LoadAssetAtPath<Mesh>(path);
   int beforeTriangles=original.triangles.Length/3;
   var existing=result;
   if(!result || RebuildEmpty) {
    var vs=new List<Vector3>(original.vertices);var ns=new List<Vector3>(original.normals);var tang=new List<Vector4>(original.tangents);var colors=new List<Color>(original.colors);
    bool hasN=ns.Count==vs.Count,hasT=tang.Count==vs.Count,hasC=colors.Count==vs.Count;
    var uvs=new List<Vector4>[8];var dimensions=new int[8];for(int k=0;k<8;k++){uvs[k]=new List<Vector4>();original.GetUVs(k,uvs[k]);dimensions[k]=original.GetVertexAttributeDimension((VertexAttribute)((int)VertexAttribute.TexCoord0+k));}
    int Make(int[] ids,JToken weights){var wd=weights.Select(x=>(double)x).ToArray();var w=wd.Select(x=>(float)x).ToArray();for(int k=0;k<3;k++)if(Math.Abs(wd[k]-1)<1e-10)return ids[k];
     int idx=vs.Count;var a=vs[ids[0]];var b=vs[ids[1]];var c=vs[ids[2]];vs.Add(new Vector3((float)((double)a.x+((double)b.x-a.x)*wd[1]+((double)c.x-a.x)*wd[2]),(float)((double)a.y+((double)b.y-a.y)*wd[1]+((double)c.y-a.y)*wd[2]),(float)((double)a.z+((double)b.z-a.z)*wd[1]+((double)c.z-a.z)*wd[2])));
     if(hasN)ns.Add((ns[ids[0]]*w[0]+ns[ids[1]]*w[1]+ns[ids[2]]*w[2]).normalized);
     if(hasT){var q=tang[ids[0]]*w[0]+tang[ids[1]]*w[1]+tang[ids[2]]*w[2];var n=new Vector3(q.x,q.y,q.z).normalized;tang.Add(new Vector4(n.x,n.y,n.z,tang[ids[0]].w));}
     if(hasC)colors.Add(colors[ids[0]]*w[0]+colors[ids[1]]*w[1]+colors[ids[2]]*w[2]);
     for(int k=0;k<8;k++)if(dimensions[k]>0)uvs[k].Add(uvs[k][ids[0]]*w[0]+uvs[k][ids[1]]*w[1]+uvs[k][ids[2]]*w[2]);return idx;}
    var indices=new int[original.subMeshCount][];
    for(int sub=0;sub<indices.Length;sub++){var old=original.GetTriangles(sub);var e=group.FirstOrDefault(p=>(int)p["submesh"]==sub);if(e==null){indices[sub]=old;continue;}
     var mapping=e["edits"].ToDictionary(p=>(int)p["triangle"],p=>p["bary"]);var list=new List<int>();
     for(int t=0;t<old.Length/3;t++){if(!mapping.TryGetValue(t,out var replacements)){list.Add(old[t*3]);list.Add(old[t*3+1]);list.Add(old[t*3+2]);continue;}
      var ids=new[]{old[t*3],old[t*3+1],old[t*3+2]};foreach(var tri in replacements){var newIds=tri.Select(w=>Make(ids,w)).ToArray();var cross=Vector3.Cross(vs[newIds[1]]-vs[newIds[0]],vs[newIds[2]]-vs[newIds[0]]);if(cross.sqrMagnitude>1e-18f)list.AddRange(newIds);}
     }indices[sub]=list.ToArray();}
    result=new Mesh();result.name="ZF_"+original.name;result.indexFormat=vs.Count>65535?IndexFormat.UInt32:IndexFormat.UInt16;result.SetVertices(vs);if(hasN)result.SetNormals(ns);if(hasT)result.SetTangents(tang);if(hasC)result.SetColors(colors);
    for(int k=0;k<8;k++)if(dimensions[k]>0){if(dimensions[k]==2)result.SetUVs(k,uvs[k].Select(x=>new Vector2(x.x,x.y)).ToList());else if(dimensions[k]==3)result.SetUVs(k,uvs[k].Select(x=>new Vector3(x.x,x.y,x.z)).ToList());else result.SetUVs(k,uvs[k]);}
    result.subMeshCount=indices.Length;for(int k=0;k<indices.Length;k++)result.SetTriangles(indices[k],k,false);result.bounds=original.bounds;
    int expected=indices.Sum(x=>x.Length);if(result.vertexCount!=vs.Count||result.triangles.Length!=expected)throw new Exception("Mesh upload verification failed");
    if(existing){EditorUtility.CopySerialized(result,existing);UnityEngine.Object.DestroyImmediate(result);result=existing;EditorUtility.SetDirty(result);}else AssetDatabase.CreateAsset(result,path);
   }
   Undo.RecordObject(mf,"Remove coincident visual surfaces");mf.sharedMesh=result;PrefabUtility.RecordPrefabInstancePropertyModifications(mf);EditorUtility.SetDirty(mf);
   records.Add(new{renderer=(string)row["path"],source=src,derived=path,beforeTriangles,afterTriangles=result.triangles.Length/3});
  }
  if(before!=State(s))throw new Exception("Transform/collider preservation failed; scene left UNSAVED");
  Undo.FlushUndoRecordObjects();AssetDatabase.SaveAssets();if(records.Count>0){EditorSceneManager.MarkSceneDirty(s);EditorSceneManager.SaveScene(s);}
  File.WriteAllText(h+(RebuildEmpty?"repaired_empty_":"applied_")+(PlanFolder=="plans"?"":PlanFolder=="precision_plans"?"precision_":PlanFolder=="finish_plans"?"finish_":"second_")+name+".json",JsonConvert.SerializeObject(new{scene,records,transformsAndCollidersUnchanged=true},Formatting.Indented));
  return new{scene,renderers=records.Count,transformsAndCollidersUnchanged=true};
 }
}
