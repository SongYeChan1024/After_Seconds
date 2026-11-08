using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEngine.SceneManagement;
using UnityEngine.Rendering.Universal;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

public static class CeilingAudit {
 static string Repo=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 static Vector3 V(JToken j)=>new Vector3((float)j[0],(float)j[1],(float)j[2]);
 static string Id(UnityEngine.Object o)=>GlobalObjectId.GetGlobalObjectIdSlow(o).ToString();
 static float[] Extents(MeshFilter f,Vector3 origin,Vector3 axis){var s=f.sharedMesh.vertices.Select(v=>Vector3.Dot(f.transform.TransformPoint(v)-origin,axis)).ToArray();return new[]{s.Min(),s.Max()};}
 public static object Run(){
  var s=SceneManager.GetActiveScene();if(s.isDirty||Application.isPlaying)throw new Exception("Saved Edit required");
  var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular")).transform;var group=root.Find("B5_CeilingLights");
  var plan=JObject.Parse(File.ReadAllText(Repo+"/SourceAssets/B5_CeilingLighting/plan.json"));var issues=new List<string>();var domes=new List<object>();var tunnels=new List<object>();
  int missingMaterial=0,vertexCount=0;float minCeilingInset=100,minFixtureHeight=100;
  foreach(var spec in plan["rooms"]){string code=(string)spec["code"];var room=group.Find(code+"_천장Lights");var center=V(spec["center"]);float radius=(float)spec["radius"];if(room.childCount!=(int)spec["count"])issues.Add(code+": fixture count");
   foreach(Transform fixture in room){var l=fixture.GetComponentInChildren<Light>();if(!l||!l.enabled||l.type!=LightType.Spot)issues.Add(fixture.name+": light missing");else{if(Vector3.Angle(l.transform.forward,-fixture.up)>.01f)issues.Add(fixture.name+": orientation");if(l.GetUniversalAdditionalLightData().usePipelineSettings)issues.Add(fixture.name+": pipeline bias");}
    foreach(var r in fixture.GetComponentsInChildren<Renderer>()){missingMaterial+=r.sharedMaterials.Count(m=>!m||!m.shader);var emission=r.sharedMaterials.FirstOrDefault(m=>m&&m.name=="DL_CeilingDiffuser");if(!emission||!emission.IsKeywordEnabled("_EMISSION"))issues.Add(fixture.name+": emission disabled");}
    foreach(var f in fixture.GetComponentsInChildren<MeshFilter>())foreach(var v in f.sharedMesh.vertices){var world=f.transform.TransformPoint(v);minCeilingInset=Mathf.Min(minCeilingInset,radius-Vector3.Distance(world,center));minFixtureHeight=Mathf.Min(minFixtureHeight,world.y+82);vertexCount++;}
   }
   domes.Add(new{code,fixtures=room.childCount,lights=room.GetComponentsInChildren<Light>().Length});
  }
  var filters=root.GetComponentsInChildren<MeshFilter>().Where(f=>f.GetComponent<Renderer>()&&f.GetComponent<Renderer>().enabled).ToArray();float minRibGap=100,minDoorGap=100;
  foreach(var t in plan["tunnels"]){var p=V(t["p"]);var forward=V(t["forward"]);float length=(float)t["length"];
   var fixtures=filters.Where(f=>AssetDatabase.GetAssetPath(f.sharedMesh).EndsWith("CFD_SealedLight.fbx")).Where(f=>{var d=f.transform.position-p;float a=Vector3.Dot(d,forward);var cross=d-forward*a;return a>0&&a<length&&new Vector2(cross.x,cross.z).magnitude<.05f;}).ToArray();
   var ribIds=t["ribs"].Select(r=>(string)r["id"]).ToHashSet();var ribs=filters.Where(f=>ribIds.Contains(Id(f.GetComponent<Renderer>()))).ToArray();
   var positions=new List<float>();
   foreach(var f in fixtures){var e=Extents(f,p,forward);positions.Add(Vector3.Dot(f.transform.position-p,forward));float dg=Mathf.Min(e[0]-.8f,length-.8f-e[1]);minDoorGap=Mathf.Min(minDoorGap,dg);if(dg<0)issues.Add((string)t["id"]+": door overlap");
    foreach(var rib in ribs){var b=Extents(rib,p,forward);float gap=Mathf.Max(b[0]-e[1],e[0]-b[1]);minRibGap=Mathf.Min(minRibGap,gap);if(gap<0)issues.Add((string)t["id"]+": rib overlap");}
   }
   var expected=t["moves"].Concat(t["additions"]).Select(a=>(float)a["s"]).OrderBy(x=>x).ToArray();var actual=positions.OrderBy(x=>x).ToArray();if(expected.Length!=actual.Length||expected.Where((e,i)=>i<actual.Length&&Mathf.Abs(e-actual[i])>.001f).Any())issues.Add((string)t["id"]+": bay centers");
   tunnels.Add(new{id=(string)t["id"],fixtures=fixtures.Length,ribs=ribs.Length});
  }
  if(minCeilingInset<-.02f)issues.Add("Fixture crosses dome shell");if(missingMaterial>0)issues.Add("Missing material");
  var result=new{scene=s.path,domes,tunnels,ceilingVertices=vertexCount,minCeilingInset,minFixtureHeight,minRibGap,minDoorGap,missingMaterial,issues,lightCount=root.GetComponentsInChildren<Light>(true).Length,newRuntimeScripts=group.GetComponentsInChildren<MonoBehaviour>().Where(b=>b&&b.GetType()!=typeof(UniversalAdditionalLightData)).Select(b=>b.GetType().FullName).ToArray()};
  File.WriteAllText(Repo+"/Docs/검수/2026-11-08_B5_CeilingLighting/audit.json",JsonConvert.SerializeObject(result,Formatting.Indented));if(issues.Count>0)throw new Exception(string.Join("; ",issues));return result;
 }
}
