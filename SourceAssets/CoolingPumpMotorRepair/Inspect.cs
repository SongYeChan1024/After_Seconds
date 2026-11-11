using System;using System.IO;using System.Linq;using System.Collections.Generic;using UnityEngine;using UnityEditor;using UnityEngine.SceneManagement;using Newtonsoft.Json;using Newtonsoft.Json.Linq;
public static class CMInspect {
 static string R=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 static string PathOf(Transform t)=>t.parent?PathOf(t.parent)+"/"+t.name:t.name;
 static float[] V(Vector3 x)=>new[]{x.x,x.y,x.z};
 public static object Run(){var s=SceneManager.GetActiveScene();if(Application.isPlaying||s.isDirty||!s.path.EndsWith("Level_B2_Circular.unity"))throw new Exception("Clean saved B2 required");
  string h=R+"/SourceAssets/CoolingPumpMotorRepair";Directory.CreateDirectory(h);var all=s.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Transform>(true)).ToArray();var plan=JObject.Parse(File.ReadAllText(R+"/SourceAssets/B2_CeilingDensity/plan.json"));
  var rows=new List<object>();foreach(var p in plan["placements"]){var t=all.SingleOrDefault(x=>x.name==(string)p["name"]);if(!t||!t.gameObject.activeInHierarchy)continue;
   var rr=t.GetComponentsInChildren<MeshRenderer>(true).Where(x=>x.enabled&&x.gameObject.activeInHierarchy).ToArray();var bounds=new Bounds(t.position,Vector3.zero);bool first=true;
   var details=new List<object>();foreach(var r in rr){var mf=r.GetComponent<MeshFilter>();if(!mf||!mf.sharedMesh)continue;var m=mf.sharedMesh;var lod=r.GetComponentInParent<LODGroup>();int level=-1;if(lod){var ls=lod.GetLODs();for(int i=0;i<ls.Length;i++)if(ls[i].renderers.Contains(r))level=i;}if(level<=0){if(first){bounds=r.bounds;first=false;}else bounds.Encapsulate(r.bounds);}
    details.Add(new{id=GlobalObjectId.GetGlobalObjectIdSlow(r).ToString(),path=PathOf(r.transform),asset=AssetDatabase.GetAssetPath(m),mesh=m.name,vertices=m.vertexCount,triangles=m.triangles.Length/3,level,localPosition=V(r.transform.localPosition),localEuler=V(r.transform.localEulerAngles),localScale=V(r.transform.localScale),worldUp=V(r.transform.up),worldForward=V(r.transform.forward),lossyScale=V(r.transform.lossyScale),min=V(r.bounds.min),max=V(r.bounds.max),materials=r.sharedMaterials.Select(a=>a?AssetDatabase.GetAssetPath(a):"MISSING").ToArray()});
   }
   rows.Add(new{name=t.name,path=PathOf(t),id=GlobalObjectId.GetGlobalObjectIdSlow(t).ToString(),model=(string)p["model"],source=(string)p["asset"],room=(string)p["room"],position=V(t.position),localPosition=V(t.localPosition),localEuler=V(t.localEulerAngles),localScale=V(t.localScale),worldUp=V(t.up),min=V(bounds.min),max=V(bounds.max),renderers=details,colliders=t.GetComponentsInChildren<Collider>(true).Select(c=>new{id=GlobalObjectId.GetGlobalObjectIdSlow(c).ToString(),path=PathOf(c.transform),enabled=c.enabled,json=EditorJsonUtility.ToJson(c)}).ToArray()});
  }
  File.WriteAllText(h+"/before.json",JsonConvert.SerializeObject(new{scene=s.path,rows},Formatting.Indented));
  return new{scene=s.path,placements=rows.Count};
 }
}
