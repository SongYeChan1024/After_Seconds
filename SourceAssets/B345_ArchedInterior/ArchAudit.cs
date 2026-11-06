// Read-only final material / geometry / placement audit, plus reusable art prefabs.
using System;using System.IO;using System.Linq;using System.Collections.Generic;
using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.SceneManagement;
using Newtonsoft.Json;using Newtonsoft.Json.Linq;
public static class ArchAudit {
 const string Root="Assets/Afrer_Seconds/";const string Props=Root+"05.Model/Props/Common/";
 static string Repo=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 static string Out=>Repo+"/Docs/검수/2026-11-06_B345_ArchedInterior/";
 static void Ready(){if(EditorApplication.isPlaying||SceneManager.GetActiveScene().isDirty)throw new Exception("Saved edit scene required");}
 static string P(Transform t)=>t.parent?P(t.parent)+"/"+t.name:t.name;
 static float[] V(Vector3 v)=>new[]{v.x,v.y,v.z};
 static bool Same(Vector3 v,JToken j){var a=j.ToObject<float[]>();return Vector3.Distance(v,new Vector3(a[0],a[1],a[2]))<.00001f;}
 static void Write(string name,object data)=>File.WriteAllText(Out+name+".json",JsonConvert.SerializeObject(data,Formatting.Indented));
 public static object Prefabs(){Ready();var result=new List<string>();foreach(string skin in new[]{"LightDust","CornerDust","Handling","WipeMarks","Scuffed","Stored"}){
  string name="SW_Case_"+skin;var mat=AssetDatabase.LoadAssetAtPath<Material>(Props+"Materials/"+name+".mat");if(!mat)throw new Exception(name);
  var g=PrefabUtility.LoadPrefabContents(Props+"SD_SpecimenCase.prefab");try{g.name=name;foreach(var r in g.GetComponentsInChildren<Renderer>(true))r.sharedMaterials=r.sharedMaterials.Select(_=>mat).ToArray();PrefabUtility.SaveAsPrefabAsset(g,Props+name+".prefab");result.Add(name);}finally{PrefabUtility.UnloadPrefabContents(g);}
 }return result;}
 public static object Inspect(){Ready();string original=SceneManager.GetActiveScene().path;var rows=new List<object>();var errors=new List<string>();
  try{foreach(string f in new[]{"B5","B4","B3"}){
   var s=EditorSceneManager.OpenScene(Root+"01.Scenes/Stage/Level_"+f+"_Stealth.unity");var roots=s.GetRootGameObjects();var all=roots.SelectMany(g=>g.GetComponentsInChildren<Transform>(true)).ToArray();var root=roots.Single(g=>g.name.StartsWith(f+"_Stealth_Level"));
   var baseline=JObject.Parse(File.ReadAllText(Out+"Before/"+f+"_snapshot.json"));var changed=new List<string>();var byPath=all.GroupBy(P).ToDictionary(g=>g.Key,g=>new Queue<Transform>(g));
   foreach(var b in baseline["transforms"]){string path=(string)b["path"];if(!byPath.ContainsKey(path)||byPath[path].Count==0){changed.Add("missing "+path);continue;}var t=byPath[path].Dequeue();if(!Same(t.localPosition,b["position"])||!Same(t.localEulerAngles,b["rotation"])||!Same(t.localScale,b["scale"])||t.gameObject.activeSelf!=(bool)b["active"])changed.Add(path);}
   Physics.SyncTransforms();var colliders=root.GetComponentsInChildren<Collider>().Where(c=>c.enabled&&!P(c.transform).Contains("/Arched_Interior/")).Select(c=>new{path=P(c.transform),center=V(c.bounds.center),size=V(c.bounds.size),type=c.GetType().Name});bool sameCollider=JToken.DeepEquals(JToken.Parse(JsonConvert.SerializeObject(colliders)),baseline["colliders"]);
   var lower=new HashSet<Renderer>();foreach(var lod in root.GetComponentsInChildren<LODGroup>())foreach(var level in lod.GetLODs().Skip(1))foreach(var r in level.renderers)lower.Add(r);
   long triangles=0;int activeRenderers=0;foreach(var r in roots.SelectMany(g=>g.GetComponentsInChildren<Renderer>(true)).Where(r=>r.enabled&&r.gameObject.activeInHierarchy)){
    activeRenderers++;if(r.sharedMaterials.Any(m=>!m||!m.shader||m.shader.name=="Hidden/InternalErrorShader"))errors.Add(f+" missing material "+r.name);
    if(lower.Contains(r))continue;var mesh=r is SkinnedMeshRenderer?((SkinnedMeshRenderer)r).sharedMesh:r.GetComponent<MeshFilter>()?.sharedMesh;if(mesh)for(int k=0;k<mesh.subMeshCount;k++)triangles+=(long)mesh.GetIndexCount(k)/3;
   }
   var cases=root.GetComponentsInChildren<LODGroup>(true).Where(g=>g.GetComponentsInChildren<MeshFilter>(true).Any(m=>m.sharedMesh&&AssetDatabase.GetAssetPath(m.sharedMesh).EndsWith("SD_SpecimenCase.fbx"))).ToArray();
   var pairs=new List<object>();for(int i=0;i<cases.Length;i++)for(int j=i+1;j<cases.Length;j++)if(Vector3.Distance(cases[i].transform.position,cases[j].transform.position)<1.05f){string a=cases[i].GetComponentInChildren<Renderer>().sharedMaterial.name,b=cases[j].GetComponentInChildren<Renderer>().sharedMaterial.name;if(a==b)pairs.Add(new{a=cases[i].name,b=cases[j].name,material=a});}
   foreach(var c in cases)if(c.GetComponentsInChildren<Renderer>(true).Any(r=>r.sharedMaterials.Any(m=>!m.name.StartsWith("SW_Case_"))))errors.Add(f+" old case material "+c.name);
   var wall=root.transform.Find("Wall_Surface_Wear");var wallMats=wall.GetComponentsInChildren<Renderer>().SelectMany(r=>r.sharedMaterials).Distinct().ToArray();foreach(var m in wallMats)foreach(string slot in new[]{"_BaseMap","_BumpMap","_MetallicGlossMap"})if(!m.GetTexture(slot))errors.Add(f+" missing texture "+m.name+" "+slot);
   rows.Add(new{floor=f,originalTransforms=baseline["transforms"].Count(),changedOriginalTransforms=changed,unchangedColliders=sameCollider,missingScripts=all.Sum(t=>GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject)),trianglesHighestLOD=triangles,activeRenderers,caseCount=cases.Length,equalWearNeighbors=pairs,wallMaterials=wallMats.Select(m=>m.name).ToArray(),wallColliders=wall.GetComponentsInChildren<Collider>().Length});
  }}finally{EditorSceneManager.OpenScene(original);}Write("preservation",new{rows,errors});return new{rows,errors};
 }
}
