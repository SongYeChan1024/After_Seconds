// B5/B4/B3 art dressing V0.01. External Editor-only authoring; no game C#.
using System;using System.IO;using System.Linq;using System.Collections.Generic;
using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.SceneManagement;
using UnityEngine.Rendering;using Newtonsoft.Json;using Newtonsoft.Json.Linq;
public static class ApplyDressing{
 const string Root="Assets/Afrer_Seconds/";const string Props=Root+"05.Model/Props/Common/";
 static string Repo=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 static string Src=>Repo+"/SourceAssets/B345_Dressing/";static string Out=>Repo+"/Docs/검수/2026-11-06_B345_Dressing/";
 static string[] types={"SpecimenCase","DiagnosticCart","CylinderTrolley","PPEStation","CentrifugeBench","MaintenanceStation"};
 static string[] skins={"TealBand","OchreTwin","BlueVertical","AmberChevrons","SageBlocks","RedSeal"};
 static void Ready(){if(EditorApplication.isPlaying||SceneManager.GetActiveScene().isDirty)throw new Exception("Saved edit scene required");}
 static Vector3 V(JToken p)=>new Vector3((float)p[0],(float)p[1],(float)p[2]);
 static float[] A(Vector3 p)=>new[]{p.x,p.y,p.z};
 static string P(Transform t)=>t.parent?P(t.parent)+"/"+t.name:t.name;
 static void Write(string name,object obj){Directory.CreateDirectory(Out);File.WriteAllText(Out+name+".json",JsonConvert.SerializeObject(obj,Formatting.Indented));}
 static Transform Child(string n,Transform p){var g=new GameObject(n);g.transform.SetParent(p,false);return g.transform;}
 static Material Material(string name,JToken row,string albedo=null,Color? tint=null){
  string path=Props+"Materials/"+name+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);if(!m){m=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(m,path);}
  m.name=name;m.enableInstancing=true;m.SetColor("_BaseColor",tint??new Color(.82f,.84f,.82f,1));m.SetTexture("_BaseMap",AssetDatabase.LoadAssetAtPath<Texture>(Props+"Textures/"+(albedo??(string)row["Albedo"])));m.SetFloat("_Smoothness",.78f);
  if(row["MetallicSmoothness"]!=null){m.SetTexture("_MetallicGlossMap",AssetDatabase.LoadAssetAtPath<Texture>(Props+"Textures/"+row["MetallicSmoothness"]));m.EnableKeyword("_METALLICSPECGLOSSMAP");}
  if(row["Normal"]!=null){m.SetTexture("_BumpMap",AssetDatabase.LoadAssetAtPath<Texture>(Props+"Textures/"+row["Normal"]));m.SetFloat("_BumpScale",.8f);m.EnableKeyword("_NORMALMAP");}
  EditorUtility.SetDirty(m);AssetDatabase.SaveAssetIfDirty(m);return m;
 }
 static void Prefab(string type,string name,Material mat){
  var root=new GameObject(name);try{
   var model=AssetDatabase.LoadAssetAtPath<GameObject>(Props+"SD_"+type+".fbx");var v=(GameObject)PrefabUtility.InstantiatePrefab(model,root.transform);PrefabUtility.UnpackPrefabInstance(v,PrefabUnpackMode.Completely,InteractionMode.AutomatedAction);v.name="Visual";
   foreach(var old in v.GetComponentsInChildren<LODGroup>())UnityEngine.Object.DestroyImmediate(old);
   var rs=v.GetComponentsInChildren<MeshRenderer>();foreach(var r in rs){r.sharedMaterials=r.sharedMaterials.Select(_=>mat).ToArray();r.shadowCastingMode=ShadowCastingMode.On;}
   var lods=new List<LOD>();for(int i=0;i<3;i++){var rr=rs.Where(r=>r.name.EndsWith("_LOD"+i)).Cast<Renderer>().ToArray();if(rr.Length==0)throw new Exception("Missing LOD "+type+" "+i);lods.Add(new LOD(i==0?.24f:i==1?.08f:.006f,rr));}
   var group=root.AddComponent<LODGroup>();group.SetLODs(lods.ToArray());group.RecalculateBounds();
   var b=rs[0].bounds;foreach(var r in rs.Skip(1))b.Encapsulate(r.bounds);var c=root.AddComponent<BoxCollider>();c.center=b.center;c.size=b.size;
   PrefabUtility.SaveAsPrefabAsset(root,Props+name+".prefab");
  }finally{UnityEngine.Object.DestroyImmediate(root);}
 }
 public static object Import(){Ready();var logs=new List<string>();Application.LogCallback cb=(m,s,t)=>{if(t==LogType.Warning||t==LogType.Error||t==LogType.Exception)logs.Add(m);};Application.logMessageReceived+=cb;var data=new List<object>();
  try{AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
   foreach(string file in Directory.GetFiles(Props+"Textures","SD_*.png")){var p=file.Replace('\\','/');var im=(TextureImporter)AssetImporter.GetAtPath(p);im.sRGBTexture=p.Contains("Albedo");im.textureType=p.Contains("_Normal")?TextureImporterType.NormalMap:TextureImporterType.Default;im.maxTextureSize=p.Contains("Case_")?1024:2048;im.textureCompression=TextureImporterCompression.CompressedHQ;im.mipmapEnabled=true;im.anisoLevel=4;im.isReadable=false;im.SaveAndReimport();}
   foreach(string type in types){string path=Props+"SD_"+type+".fbx";var im=(ModelImporter)AssetImporter.GetAtPath(path);im.importAnimation=false;im.importCameras=false;im.importLights=false;im.isReadable=false;im.SaveAndReimport();var row=JObject.Parse(File.ReadAllText(Src+type+"_manifest.json"));var mat=Material("SD_"+type,row["materials"][0]);Prefab(type,"SD_"+type,mat);
    if(type=="SpecimenCase"){Color[] colors={new Color(.82f,.86f,.83f),new Color(.84f,.78f,.65f),new Color(.65f,.75f,.82f),new Color(.76f,.77f,.73f),new Color(.68f,.78f,.69f),new Color(.82f,.73f,.68f)};for(int i=0;i<skins.Length;i++){var m=Material("SD_Case_"+skins[i],row["materials"][0],"SD_Case_"+skins[i]+"_Albedo.png",colors[i]);Prefab(type,"SD_Case_"+skins[i],m);}}
    data.Add(new{type,triangles=row["triangles"]});
   }
   string arch=Root+"05.Model/Environment/B3/SD_B3_Architecture.fbx";var ai=(ModelImporter)AssetImporter.GetAtPath(arch);ai.importAnimation=false;ai.importCameras=false;ai.importLights=false;ai.SaveAndReimport();AssetDatabase.SaveAssets();
  }finally{Application.logMessageReceived-=cb;}Write("import",new{logs,assets=data});return new{logs,assets=data};
 }
 static List<Vector3> RoutePoints(string floor){var points=new List<Vector3>();var routes=JObject.Parse(File.ReadAllText(Repo+"/Docs/도면/잠입_탐색/플레이어_예상이동/player_routes.json"))["routes"];
  foreach(var r in routes.Where(t=>(string)t["floor"]==floor))foreach(var leg in r["legs"]){var pp=leg["points"].Select(p=>new Vector3((float)p[0]-24,0,(float)p[1]-16)).ToArray();for(int i=1;i<pp.Length;i++){int n=Mathf.CeilToInt(Vector3.Distance(pp[i-1],pp[i])/.25f);for(int j=0;j<=n;j++)points.Add(Vector3.Lerp(pp[i-1],pp[i],(float)j/n));}}var root=SceneManager.GetActiveScene().GetRootGameObjects().Single(g=>g.name.StartsWith(floor+"_Stealth_Level"));foreach(string group in new[]{"Lab_Doors","TransitionDoors"}){var doors=root.transform.Find(group);if(!doors)continue;foreach(Transform d in doors)for(int i=-6;i<=6;i++)points.Add(d.TransformPoint(new Vector3(0,0,i*.25f)));}return points;
 }
 static bool Clear(Transform t,List<Vector3> routes,JToken room){var c=t.GetComponent<BoxCollider>();Physics.SyncTransforms();var b=c.bounds;
  if(b.min.x<(float)room["x"]-24+.2f||b.max.x>(float)room["x"]+(float)room["w"]-24-.2f||b.min.z<(float)room["y"]-16+.2f||b.max.z>(float)room["y"]+(float)room["h"]-16-.2f)return false;
  if(Physics.OverlapBox(t.TransformPoint(c.center),Vector3.Scale(c.size*.5f,t.lossyScale)-Vector3.one*.025f,t.rotation,~0,QueryTriggerInteraction.Ignore).Any(h=>h!=c&&!h.transform.IsChildOf(t)&&!h.transform.root.name.StartsWith("Player")))return false;
  foreach(var p in routes){var q=t.InverseTransformPoint(p+Vector3.up*.8f)-c.center;var e=c.size*.5f;if(Mathf.Abs(q.x)<e.x+.38f&&Mathf.Abs(q.z)<e.z+.38f&&Mathf.Abs(q.y)<e.y+.8f)return false;}
  return true;
 }
 static void Cases(Transform root){var parent=Child("Specimen_Cases_6Patterns",root);int n=0;
  foreach(float u in new[]{5f,10f,15f})foreach(float v in new[]{7f,16f})foreach(float h in new[]{.18f,.95f,1.72f,2.49f})for(int bay=0;bay<6;bay++)for(int side=0;side<2;side++){
   int variant=(bay*3+side*2+Mathf.RoundToInt(u)+Mathf.RoundToInt(h*10)+Mathf.RoundToInt(v))%6;
   var g=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Props+"SD_Case_"+skins[variant]+".prefab"),parent);
   g.name="Case_"+(n++).ToString("D3")+"_"+skins[variant];g.transform.localPosition=new Vector3(u+.39f+side*.72f-24,h+.035f,v+.42f+bay*.82f-16);g.transform.localRotation=Quaternion.Euler(0,(bay+side)%2==0?0:180,0);g.GetComponent<BoxCollider>().enabled=false;PrefabUtility.RecordPrefabInstancePropertyModifications(g.GetComponent<BoxCollider>());
  }if(n!=288)throw new Exception("Case count mismatch");
 }
 public static object Clearances(){Ready();string original=SceneManager.GetActiveScene().path;var changes=new List<object>();var plans=JObject.Parse(File.ReadAllText(Repo+"/Docs/도면/잠입_탐색/layout.json"))["floors"];
  try{foreach(string floor in new[]{"B5","B4","B3"}){var s=EditorSceneManager.OpenScene(Root+"01.Scenes/Stage/Level_"+floor+"_Stealth.unity");var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith(floor+"_Stealth_Level"));var routes=RoutePoints(floor);var plan=plans.Single(f=>(string)f["floor"]==floor);var rows=JArray.Parse(File.ReadAllText(Out+"placed_"+floor+".json"));
   foreach(var row in rows){var t=root.transform.Find("Dressing_Props/"+(string)row["name"]);var room=plan["rooms"].Single(r=>(string)r["id"]==(string)row["room"]);if(Clear(t,routes,room))continue;var before=t.position;bool ok=false;float[] offsets={0,.45f,-.45f,.9f,-.9f,1.35f,-1.35f,1.8f,-1.8f,2.25f,-2.25f};
    foreach(float radius in new[]{.46f,.91f,1.36f,1.81f,2.26f}){foreach(float dx in offsets){foreach(float dz in offsets){if(Mathf.Max(Mathf.Abs(dx),Mathf.Abs(dz))>radius)continue;t.position=before+new Vector3(dx,0,dz);if(Clear(t,routes,room)){ok=true;break;}}if(ok)break;}if(ok)break;}
    if(!ok)throw new Exception("No clear placement "+floor+" "+t.name);PrefabUtility.RecordPrefabInstancePropertyModifications(t);row["position"]=JArray.FromObject(A(t.position));changes.Add(new{floor,name=t.name,before=A(before),after=A(t.position)});
   }Write("placed_"+floor,rows);EditorSceneManager.MarkSceneDirty(s);EditorSceneManager.SaveScene(s);
  }}finally{EditorSceneManager.OpenScene(original);}Write("clearance_corrections",changes);return changes;
 }
 public static object Apply(){Ready();var specs=JObject.Parse(File.ReadAllText(Src+"placements.json"))["floors"];var plans=JObject.Parse(File.ReadAllText(Repo+"/Docs/도면/잠입_탐색/layout.json"))["floors"];var report=new List<object>();string original=SceneManager.GetActiveScene().path;
  try{foreach(string floor in new[]{"B5","B4","B3"}){var s=EditorSceneManager.OpenScene(Root+"01.Scenes/Stage/Level_"+floor+"_Stealth.unity");var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith(floor+"_Stealth_Level"));if(root.transform.Find("Dressing_Props")){report.Add(new{floor,alreadyApplied=true});continue;}
   var parent=Child("Dressing_Props",root.transform);var routes=RoutePoints(floor);var plan=plans.Single(r=>(string)r["floor"]==floor);var placed=new List<object>();var failures=new List<string>();int index=0;
   foreach(var row in specs[floor]){string type=(string)row[0],roomId=(string)row[4];string name=type=="SpecimenCase"?"SD_Case_"+skins[index%skins.Length]:"SD_"+type;var g=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Props+name+".prefab"),parent);g.name=roomId+"_"+type+"_"+(index++).ToString("D2");
    var wanted=new Vector3((float)row[1]-24,row.Count()>5?(float)row[5]:0,(float)row[2]-16);g.transform.rotation=Quaternion.Euler(0,(float)row[3],0);var room=plan["rooms"].Single(r=>(string)r["id"]==roomId);bool ok=false;
    float[] offsets={0,.45f,-.45f,.9f,-.9f,1.35f,-1.35f};foreach(float radius in new[]{0f,.46f,.91f,1.36f,1.92f}){foreach(float dx in offsets){foreach(float dz in offsets){if(Mathf.Max(Mathf.Abs(dx),Mathf.Abs(dz))>radius)continue;g.transform.position=wanted+new Vector3(dx,0,dz);if(Clear(g.transform,routes,room)){ok=true;break;}}if(ok)break;}if(ok)break;}
    if(!ok){failures.Add(g.name);UnityEngine.Object.DestroyImmediate(g);continue;}placed.Add(new{name=g.name,type,room=roomId,wanted=A(wanted),position=A(g.transform.position),yaw=(float)row[3]});
   }
   if(failures.Count>0)throw new Exception("Unplaced props "+floor+": "+string.Join(",",failures));
   if(floor=="B3"){var old=root.transform.Find("Architecture_Sections");if(old.GetComponentsInChildren<Collider>().Length>0)throw new Exception("Architecture has collision");var mats=old.GetComponentsInChildren<Renderer>().SelectMany(r=>r.sharedMaterials).Distinct().ToDictionary(m=>m.name,m=>m);var model=AssetDatabase.LoadAssetAtPath<GameObject>(Root+"05.Model/Environment/B3/SD_B3_Architecture.fbx");var arch=(GameObject)PrefabUtility.InstantiatePrefab(model,root.transform);arch.name="Architecture_Sections";foreach(var r in arch.GetComponentsInChildren<Renderer>()){r.sharedMaterials=old.GetComponentsInChildren<Renderer>().Single(previous=>previous.name==r.name).sharedMaterials;PrefabUtility.RecordPrefabInstancePropertyModifications(r);}UnityEngine.Object.DestroyImmediate(old.gameObject);Cases(root.transform);}
   EditorSceneManager.MarkSceneDirty(s);EditorSceneManager.SaveScene(s);report.Add(new{floor,placed,caseCount=floor=="B3"?288:0});Write("placed_"+floor,placed);
  }}finally{if(!SceneManager.GetActiveScene().isDirty)EditorSceneManager.OpenScene(original);}Write("placement",report);return report.Select(r=>r).ToArray();
 }
}
