using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
using Newtonsoft.Json;

// External, read-only geometry survey. Never saves a scene or alters imported meshes.
public static class F1GeometryExport {
 static string Root => Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 static string Cache => Path.GetFullPath(Path.Combine(Application.dataPath,"../Temp/ZFightingReview"));
 static float[] V(Vector3 v) => new[]{v.x,v.y,v.z};
 static string HP(Transform t) => t.parent ? HP(t.parent)+"/"+t.name : t.name;
 public static object Run(string scenePath) {
  if(Application.isPlaying || Enumerable.Range(0,SceneManager.sceneCount).Any(i=>SceneManager.GetSceneAt(i).isDirty)) throw new Exception("Clean edit mode required");
  Directory.CreateDirectory(Cache+"/meshes");
  var s=EditorSceneManager.OpenScene(scenePath);
  var all=s.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Renderer>(true)).ToArray();
  var rows=new List<object>(); var errors=new List<string>();var written=new HashSet<string>();
  foreach(var r in all) {
   if(!r.enabled || !r.gameObject.activeInHierarchy) continue;
   var mf=r.GetComponent<MeshFilter>(); var mesh=mf?mf.sharedMesh:(r is SkinnedMeshRenderer sm?sm.sharedMesh:null);
   if(!mesh) continue;
   AssetDatabase.TryGetGUIDAndLocalFileIdentifier(mesh,out string guid,out long local);
   var key=guid+"_"+local;
   var file=Cache+"/meshes/"+key+".bin";
   try {
    if(!written.Contains(key)&&(!File.Exists(file)||AssetDatabase.GetAssetPath(mesh).Contains("/F1_"))) {
     var vs=mesh.vertices;
     if(mesh.name.StartsWith("ZF_")&&(vs.Length==0||mesh.triangles.Length==0))errors.Add("EMPTY DERIVATIVE: "+HP(r.transform));
     if(vs.Any(v=>float.IsNaN(v.x)||float.IsNaN(v.y)||float.IsNaN(v.z)||float.IsInfinity(v.x)||float.IsInfinity(v.y)||float.IsInfinity(v.z)))errors.Add("NONFINITE VERTEX: "+HP(r.transform));
     using(var w=new BinaryWriter(File.Create(file))) {
      w.Write(vs.Length);w.Write(mesh.subMeshCount);
      foreach(var v in vs){w.Write(v.x);w.Write(v.y);w.Write(v.z);}
      for(int k=0;k<mesh.subMeshCount;k++){var ix=mesh.GetIndices(k);w.Write((int)mesh.GetTopology(k));w.Write(ix.Length);foreach(int n in ix)w.Write(n);}
     }
     written.Add(key);
    }
    var lod=r.GetComponentInParent<LODGroup>();int level=-1;
    if(lod){var ls=lod.GetLODs();for(int j=0;j<ls.Length;j++)if(ls[j].renderers.Contains(r))level=j;}
    var m=r.localToWorldMatrix; var matrix=new float[16];for(int y=0;y<4;y++)for(int x=0;x<4;x++)matrix[y*4+x]=m[y,x];
    rows.Add(new {id=GlobalObjectId.GetGlobalObjectIdSlow(r).ToString(),path=HP(r.transform),mesh=key,asset=AssetDatabase.GetAssetPath(mesh),meshName=mesh.name,vertices=mesh.vertexCount,matrix,bmin=V(r.bounds.min),bmax=V(r.bounds.max),lod=lod?HP(lod.transform):null,level,skinned=r is SkinnedMeshRenderer,materials=r.sharedMaterials.Select(a=>a?new {name=a.name,path=AssetDatabase.GetAssetPath(a),shader=a.shader.name,queue=a.renderQueue,cull=a.HasProperty("_Cull")?a.GetFloat("_Cull"):-1}:null).ToArray()});
   } catch(Exception e){errors.Add(HP(r.transform)+": "+e.Message);}
  }
  var report=new {scene=scenePath,allRenderers=all.Length,activeMeshes=rows.Count,rows,errors,cameras=s.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Camera>(true)).Select(c=>new{c.name,c.nearClipPlane,c.farClipPlane,c.enabled})};
  File.WriteAllText(Cache+"/"+s.name+".json",JsonConvert.SerializeObject(report));
  return new{scene=scenePath,allRenderers=all.Length,activeMeshes=rows.Count,errors};
 }
}
