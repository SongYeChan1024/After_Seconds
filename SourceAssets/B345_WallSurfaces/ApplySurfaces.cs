// External Editor-only wall surface authoring. 송예찬. No runtime components.
using System;using System.IO;using System.Linq;using System.Collections.Generic;
using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.SceneManagement;
using UnityEngine.Rendering;using Newtonsoft.Json;using Newtonsoft.Json.Linq;
public static class ApplySurfaces {
 const string Root="Assets/Afrer_Seconds/";const string Env=Root+"05.Model/Environment/";const string Props=Root+"05.Model/Props/Common/";
 static string Repo=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 static string Src=>Repo+"/SourceAssets/B345_WallSurfaces/";static string Out=>Repo+"/Docs/검수/2026-11-06_B345_WallSurfaces/";
 static string[] families={"Clean","Staff","Steel","Concrete"};
 static string[] wear={"LightDust","CornerDust","Handling","WipeMarks","Scuffed","Stored"};
 static void Ready(){if(EditorApplication.isPlaying||SceneManager.GetActiveScene().isDirty)throw new Exception("Saved edit scene required");}
 static void Write(string name,object data){Directory.CreateDirectory(Out);File.WriteAllText(Out+name+".json",JsonConvert.SerializeObject(data,Formatting.Indented));}
 static long Tri(Renderer[] rs)=>rs.Sum(r=>{var m=r.GetComponent<MeshFilter>()?.sharedMesh;return m?Enumerable.Range(0,m.subMeshCount).Sum(i=>(long)m.GetIndexCount(i)/3):0;});
 static Bounds Bounds(Renderer[] rs){var b=rs[0].bounds;foreach(var r in rs.Skip(1))b.Encapsulate(r.bounds);return b;}
 static Material Mat(string name,string folder,float bump){
  string p=folder+"Materials/"+name+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(p);
  if(!m){m=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(m,p);}m.name=name;m.enableInstancing=true;
  m.SetColor("_BaseColor",new Color(.9f,.9f,.9f,1));m.SetTexture("_BaseMap",AssetDatabase.LoadAssetAtPath<Texture>(folder+"Textures/"+name+"_Albedo.png"));
  m.SetTexture("_MetallicGlossMap",AssetDatabase.LoadAssetAtPath<Texture>(folder+"Textures/"+name+"_MetallicSmoothness.png"));m.SetFloat("_Smoothness",name.StartsWith("SW_Case_")?.72f:1f);m.EnableKeyword("_METALLICSPECGLOSSMAP");
  string normal=folder+"Textures/"+(name.StartsWith("SW_Case_")?"SD_SpecimenCase":name)+"_Normal.png";
  m.SetTexture("_BumpMap",AssetDatabase.LoadAssetAtPath<Texture>(normal));m.SetFloat("_BumpScale",bump);m.EnableKeyword("_NORMALMAP");EditorUtility.SetDirty(m);return m;
 }
 static void Textures(string folder,string prefix){foreach(string file in Directory.GetFiles(folder+"Textures",prefix+"*.png")){
  string p=file.Replace('\\','/');var im=(TextureImporter)AssetImporter.GetAtPath(p);im.sRGBTexture=p.EndsWith("_Albedo.png");im.textureType=p.EndsWith("_Normal.png")?TextureImporterType.NormalMap:TextureImporterType.Default;im.maxTextureSize=2048;im.textureCompression=TextureImporterCompression.CompressedHQ;im.mipmapEnabled=true;im.anisoLevel=4;im.isReadable=false;im.wrapMode=TextureWrapMode.Clamp;im.SaveAndReimport();
 }}
 public static object Walls(){
  Ready();var logs=new List<string>();Application.LogCallback cb=(m,s,t)=>{if(t==LogType.Warning||t==LogType.Error||t==LogType.Exception)logs.Add(m);};Application.logMessageReceived+=cb;string original=SceneManager.GetActiveScene().path;var rows=new List<object>();
  try{AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);Textures(Env+"Common/","WS_");var mats=families.ToDictionary(f=>"WS_"+f,f=>Mat("WS_"+f,Env+"Common/",.7f));AssetDatabase.SaveAssets();
   foreach(string f in new[]{"B5","B4","B3"}){
    string path=Env+f+"/WS_"+f+"_Walls.fbx";var im=(ModelImporter)AssetImporter.GetAtPath(path);im.importAnimation=false;im.importCameras=false;im.importLights=false;im.isReadable=false;im.SaveAndReimport();
    var s=EditorSceneManager.OpenScene(Root+"01.Scenes/Stage/Level_"+f+"_Stealth.unity");var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith(f+"_Stealth_Level"));
    if(root.transform.Find("Wall_Surface_Wear"))throw new Exception("Already applied: "+f);
    var row=JObject.Parse(File.ReadAllText(Src+f+"_walls.json"));var names=new HashSet<string>(row["oldBatches"].Select(j=>(string)j));
    var old=root.transform.Find("Architecture_Sections").GetComponentsInChildren<Renderer>().Where(r=>names.Contains(r.name)).ToArray();
    if(old.Length!=names.Count||old.Any(r=>!r.enabled))throw new Exception("Source batch mismatch "+f+" "+old.Length+"/"+names.Count);
    var go=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(path),root.transform);go.name="Wall_Surface_Wear";var rr=go.GetComponentsInChildren<Renderer>();
    foreach(var r in rr){r.sharedMaterials=r.sharedMaterials.Select(m=>mats[m.name]).ToArray();r.shadowCastingMode=ShadowCastingMode.On;PrefabUtility.RecordPrefabInstancePropertyModifications(r);}
    long before=Tri(old),after=Tri(rr);var a=Bounds(old);var b=Bounds(rr);
    if(before!=after||(a.center-b.center).magnitude>.005f||(a.size-b.size).magnitude>.005f){UnityEngine.Object.DestroyImmediate(go);throw new Exception("Geometry mismatch "+f+" "+before+"/"+after+" "+a+" "+b);}
    foreach(var r in old){r.enabled=false;PrefabUtility.RecordPrefabInstancePropertyModifications(r);}
    EditorSceneManager.MarkSceneDirty(s);EditorSceneManager.SaveScene(s);rows.Add(new{floor=f,panels=(int)row["sourceObjects"],beforeTriangles=before,afterTriangles=after,oldRenderers=old.Length,newRenderers=rr.Length,variants=row["variants"],collidersAdded=go.GetComponentsInChildren<Collider>().Length});
   }
  }finally{Application.logMessageReceived-=cb;if(!SceneManager.GetActiveScene().isDirty)EditorSceneManager.OpenScene(original);}
  Write("walls_applied",new{rows,logs});return new{rows,logs};
 }
 public static object Cases(){
  Ready();AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);Textures(Props,"SW_Case_");var mats=wear.Select(w=>Mat("SW_Case_"+w,Props,.8f)).ToArray();AssetDatabase.SaveAssets();
  string original=SceneManager.GetActiveScene().path;var rows=new List<object>();
  try{foreach(string f in new[]{"B5","B4","B3"}){
   var s=EditorSceneManager.OpenScene(Root+"01.Scenes/Stage/Level_"+f+"_Stealth.unity");var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith(f+"_Stealth_Level"));
   var boxes=root.GetComponentsInChildren<LODGroup>(true).Where(g=>g.GetComponentsInChildren<MeshFilter>(true).Any(m=>m.sharedMesh&&AssetDatabase.GetAssetPath(m.sharedMesh).EndsWith("SD_SpecimenCase.fbx"))).OrderBy(g=>g.transform.position.y).ThenBy(g=>g.transform.position.z).ThenBy(g=>g.transform.position.x).ToArray();
   var rng=new System.Random(f=="B5"?11065:f=="B4"?11064:11063);var placed=new List<Tuple<Vector3,int>>();var counts=new int[6];var entries=new List<object>();
   foreach(var g in boxes){var p=g.transform.position;var nearby=placed.Where(q=>Vector3.Distance(p,q.Item1)<1.05f).Select(q=>q.Item2).ToHashSet();var candidates=Enumerable.Range(0,6).Where(i=>!nearby.Contains(i)).ToArray();if(candidates.Length==0)candidates=Enumerable.Range(0,6).ToArray();int chosen=candidates[rng.Next(candidates.Length)];
    foreach(var r in g.GetComponentsInChildren<Renderer>(true)){r.sharedMaterials=r.sharedMaterials.Select(_=>mats[chosen]).ToArray();PrefabUtility.RecordPrefabInstancePropertyModifications(r);}placed.Add(Tuple.Create(p,chosen));counts[chosen]++;entries.Add(new{name=g.name,wear=wear[chosen],position=new[]{p.x,p.y,p.z}});
   }
   EditorSceneManager.MarkSceneDirty(s);EditorSceneManager.SaveScene(s);rows.Add(new{floor=f,cases=boxes.Length,variants=wear.Select((w,i)=>new{name=w,count=counts[i]}),placements=entries});
  }}finally{if(!SceneManager.GetActiveScene().isDirty)EditorSceneManager.OpenScene(original);}Write("cases_applied",rows);return rows.Select(r=>r).ToArray();
 }
}
