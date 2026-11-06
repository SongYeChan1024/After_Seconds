using System;using System.IO;using System.Linq;using System.Collections.Generic;
using UnityEngine;using UnityEditor;using UnityEngine.SceneManagement;using UnityEditor.SceneManagement;using UnityEngine.Rendering;using Newtonsoft.Json;using Newtonsoft.Json.Linq;
public static class RefineCircular {
 const string A="Assets/Afrer_Seconds/";static string Repo=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));static string S=>Repo+"/SourceAssets/CircularFacility/";static string Out=>Repo+"/Docs/검수/2026-11-06_CircularFacility/";static JObject data;static Transform root;static Dictionary<Vector2Int,bool> cache=new Dictionary<Vector2Int,bool>();const float step=.4f;
 static Vector3 World(Vector2Int q)=>new Vector3(q.x*step,-82,-q.y*step);
 static bool Free(Vector2Int q){bool val;if(cache.TryGetValue(q,out val))return val;var p=World(q);if(q.x<-125||q.x>125||q.y<-90||q.y>90)return false;
  RaycastHit hit;bool ground=Physics.Raycast(p+Vector3.up*.4f,Vector3.down,out hit,1f,~0,QueryTriggerInteraction.Ignore)&&hit.collider.transform.IsChildOf(root);
  val=ground&&!Physics.OverlapCapsule(p+Vector3.up*.34f,p+Vector3.up*1.48f,.28f,~0,QueryTriggerInteraction.Ignore).Any(c=>c.transform.IsChildOf(root)&&!c.name.Contains("Floor")&&!c.name.Contains("Threshold"));cache[q]=val;return val;
 }
 static bool Clear(Vector2Int a,Vector2Int b){float len=Vector2Int.Distance(a,b);int n=Mathf.CeilToInt(len*3);for(int i=0;i<=n;i++){var p=Vector2.Lerp(a,b,(float)i/Math.Max(1,n));if(!Free(new Vector2Int(Mathf.RoundToInt(p.x),Mathf.RoundToInt(p.y))))return false;}return true;}
 static Vector2Int Snap(float x,float v){var q=new Vector2Int(Mathf.RoundToInt(x/step),Mathf.RoundToInt(v/step));if(Free(q))return q;for(int k=1;k<25;k++)for(int a=-k;a<=k;a++)foreach(int b in new[]{-k,k}){var n=q+new Vector2Int(a,b);if(Free(n))return n;}throw new Exception("No free node "+q);}
 static List<Vector2Int> Search(Vector2Int from,Vector2Int to){
  var open=new SortedSet<(float,int,int,int)>();int seq=0;var g=new Dictionary<Vector2Int,float>{{from,0}};var came=new Dictionary<Vector2Int,Vector2Int>();var done=new HashSet<Vector2Int>();open.Add((Vector2Int.Distance(from,to),seq++,from.x,from.y));int loop=0;
  while(open.Count>0&&loop++<60000){var v=open.Min;open.Remove(v);var cur=new Vector2Int(v.Item3,v.Item4);if(done.Contains(cur))continue;done.Add(cur);
   if(cur==to){var p=new List<Vector2Int>{cur};while(came.ContainsKey(cur)){cur=came[cur];p.Add(cur);}p.Reverse();return p;}
   foreach(var off in new[]{new Vector2Int(1,0),new Vector2Int(-1,0),new Vector2Int(0,1),new Vector2Int(0,-1),new Vector2Int(1,1),new Vector2Int(1,-1),new Vector2Int(-1,1),new Vector2Int(-1,-1)}){
    var nxt=cur+off;if(done.Contains(nxt)||!Free(nxt))continue;if(off.x!=0&&off.y!=0&&(!Free(cur+new Vector2Int(off.x,0))||!Free(cur+new Vector2Int(0,off.y))))continue;float cost=g[cur]+off.magnitude;
    if(!g.ContainsKey(nxt)||cost<g[nxt]){g[nxt]=cost;came[nxt]=cur;open.Add((cost+Vector2Int.Distance(nxt,to),seq++,nxt.x,nxt.y));}
   }
  }throw new Exception("Route disconnected "+from+" -> "+to+" / "+loop);
 }
 static List<Vector2Int> Prune(List<Vector2Int> p){var o=new List<Vector2Int>{p[0]};int i=0;while(i<p.Count-1){int j=p.Count-1;while(j>i+1&&!Clear(p[i],p[j]))j--;o.Add(p[j]);i=j;}return o;}
 public static object Routes(){data=JObject.Parse(File.ReadAllText(Repo+"/Docs/도면/원형공동/facility_layout.json"));EditorSceneManager.OpenScene(A+"01.Scenes/Stage/Level_B5_Circular.unity");root=SceneManager.GetActiveScene().GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular")).transform;foreach(var p in SceneManager.GetActiveScene().GetRootGameObjects().Where(g=>g.name.StartsWith("Player")))p.SetActive(false);Physics.SyncTransforms();cache.Clear();var f=data["floors"].Single(x=>(string)x["id"]=="B5");var result=new JObject();
  foreach(var key in new[]{"route","alternate"}){var old=f[key].ToArray();var start=Snap((float)old[0][0],(float)old[0][1]);var target=Snap((float)old.Last()[0],(float)old.Last()[1]);var pts=new List<Vector2Int>{start};var ids=f[key=="route"?"main":"alt"].Select(v=>(string)v).ToArray();
   foreach(string id in ids.Skip(1).Take(ids.Length-2)){var room=f["rooms"].Single(r=>(string)r["id"]==id);pts.Add(Snap((float)room["x"],(float)room["v"]));}pts.Add(target);var route=new List<Vector2Int>();
   for(int i=1;i<pts.Count;i++){var part=Prune(Search(pts[i-1],pts[i]));route.AddRange(i==1?part:part.Skip(1));}
   result[key]=new JArray(route.Select(q=>new JArray(Math.Round(q.x*step,3),Math.Round(q.y*step,3))));
  }
  File.WriteAllText(S+"validated_routes.json",new JObject{{"B5",result}}.ToString());f["route"]=result["route"].DeepClone();f["alternate"]=result["alternate"].DeepClone();foreach(var rr in data["guidance_routes"].Where(r=>(string)r["floor"]=="B5"&&(string)r["code"]!="M1"))rr["points"]=result[(string)rr["code"]=="R1"?"route":"alternate"].DeepClone();File.WriteAllText(Repo+"/Docs/도면/원형공동/facility_layout.json",data.ToString());
  var existing=root.Find("Facility_Floor_Guidance_R1");if(existing)UnityEngine.Object.DestroyImmediate(existing.gameObject);var group=new GameObject("Facility_Floor_Guidance_R1");group.transform.SetParent(root,false);var points=result["route"].Select(p=>new Vector3((float)p[0],.018f,-(float)p[1])).ToArray();var mat=AssetDatabase.LoadAssetAtPath<Material>(A+"05.Model/Environment/Common/Materials/CF_B5_Guide.mat");
  foreach(float side in new[]{-.12f,.12f}){var vs=new List<Vector3>();var tris=new List<int>();for(int i=0;i<points.Length;i++){
    Vector3 a=(points[i]-points[Math.Max(0,i-1)]).normalized,b=(points[Math.Min(points.Length-1,i+1)]-points[i]).normalized;Vector3 dir=(a+b).normalized;if(dir==Vector3.zero)dir=i==0?b:a;Vector3 right=Vector3.Cross(Vector3.up,dir);float correction=Mathf.Max(.6f,Vector3.Dot(right,Vector3.Cross(Vector3.up,i==0?b:a)));
    vs.Add(points[i]+right*((side-.025f)/correction));vs.Add(points[i]+right*((side+.025f)/correction));if(i>0){int k=i*2;tris.AddRange(new[]{k-2,k,k-1,k-1,k,k+1});}}
   var mesh=new Mesh();mesh.vertices=vs.ToArray();mesh.triangles=tris.ToArray();mesh.RecalculateNormals();string path=A+"05.Model/Environment/B5/CF_R1_Continuous_"+(side<0?"L":"R")+".asset";var old=AssetDatabase.LoadAssetAtPath<Mesh>(path);if(old){EditorUtility.CopySerialized(mesh,old);UnityEngine.Object.DestroyImmediate(mesh);mesh=old;}else AssetDatabase.CreateAsset(mesh,path);var g=new GameObject("R1_Continuous");g.transform.SetParent(group.transform,false);g.AddComponent<MeshFilter>().sharedMesh=mesh;g.AddComponent<MeshRenderer>().sharedMaterial=mat;
  }
  foreach(var p in SceneManager.GetActiveScene().GetRootGameObjects().Where(g=>g.name.StartsWith("Player")))p.SetActive(true);EditorSceneManager.SaveScene(SceneManager.GetActiveScene());return new{visited=cache.Count,mainPoints=result["route"].Count(),alternatePoints=result["alternate"].Count()};
 }
 public static object PolishB2()=>Polish("B2");
 public static object Polish(string only=null){data=JObject.Parse(File.ReadAllText(Repo+"/Docs/도면/원형공동/facility_layout.json"));var results=new List<object>();
  foreach(string fid in new[]{"B5","B2"}){if(only!=null&&fid!=only)continue;string name=fid=="B5"?"Level_B5_Circular":"Level_B2_MezzaninePreview";EditorSceneManager.OpenScene(A+"01.Scenes/Stage/"+name+".unity");var s=SceneManager.GetActiveScene();var rt=s.GetRootGameObjects().Single(g=>g.name.StartsWith(fid+"_"));float y=fid=="B5"?-82:-34;float v=fid=="B5"?.35f:.24f;RenderSettings.ambientSkyColor=new Color(v,v*1.02f,v*1.08f);RenderSettings.ambientEquatorColor=new Color(v*.85f,v*.9f,v);RenderSettings.ambientGroundColor=new Color(v*.6f,v*.64f,v*.7f);
   foreach(var l in rt.GetComponentsInChildren<Light>())if(!l.name.StartsWith("Red"))l.intensity=fid=="B5"?(l.name.Contains("_Work_")?3.74f:2.04f):(l.name.Contains("Central")?3.84f:3.2f);
   var player=s.GetRootGameObjects().Single(g=>g.name.StartsWith("Player"));var renderers=player.GetComponentsInChildren<Renderer>();var previous=renderers.Select(r=>r.enabled).ToArray();foreach(var r in renderers)r.enabled=false;
   var oldGroup=rt.transform.Find("Reflection_Probes");if(oldGroup)UnityEngine.Object.DestroyImmediate(oldGroup.gameObject);var parent=new GameObject("Reflection_Probes");parent.transform.SetParent(rt.transform,false);
   var rooms=data["floors"].Single(f=>(string)f["id"]==fid)["rooms"].Where(r=>fid=="B5"?r["wing"]==null:(string)r["id"]=="C02");int n=0;
   foreach(var r in rooms){var g=new GameObject("Probe_"+r["id"]);g.transform.SetParent(parent.transform,false);g.transform.localPosition=new Vector3((float)r["x"],2,-(float)r["v"]);var p=g.AddComponent<ReflectionProbe>();float radius=(float)r["r"];p.size=new Vector3(radius*2,radius+2,radius*2);p.center=new Vector3(0,radius*.5f-2,0);p.resolution=128;p.hdr=true;p.boxProjection=true;p.mode=ReflectionProbeMode.Custom;p.renderDynamicObjects=true;p.clearFlags=ReflectionProbeClearFlags.SolidColor;p.backgroundColor=new Color(.1f,.12f,.14f);p.intensity=1f;string file=A+"05.Model/Environment/"+fid+"/Textures/CF_Reflection_"+r["id"]+".exr";Directory.CreateDirectory(Path.GetDirectoryName(Path.Combine(Path.GetDirectoryName(Application.dataPath),file)));if(!Lightmapping.BakeReflectionProbe(p,file))throw new Exception("Probe bake failed "+file);AssetDatabase.ImportAsset(file,ImportAssetOptions.ForceSynchronousImport);p.customBakedTexture=AssetDatabase.LoadAssetAtPath<Cubemap>(file);n++;}
   for(int i=0;i<renderers.Length;i++)renderers[i].enabled=previous[i];EditorSceneManager.SaveScene(s);results.Add(new{floor=fid,probes=n});
  }EditorSceneManager.OpenScene(A+"01.Scenes/Stage/Level_B5_Circular.unity");return results;
 }
 public static object Walk(){EditorSceneManager.OpenScene(A+"01.Scenes/Stage/Level_B2_MezzaninePreview.unity");var player=SceneManager.GetActiveScene().GetRootGameObjects().Single(g=>g.name.StartsWith("Player"));var cc=player.GetComponent<CharacterController>();var original=player.transform.position;var results=new List<object>();
  foreach(float x in new[]{12.8f,25.2f})foreach(bool up in new[]{true,false}){
   Vector3 from=new Vector3(x,up?-34:-30.4f,up?-9.1f:-2.3f),to=new Vector3(x,up?-30.4f:-34,up?-2.3f:-9.1f);cc.enabled=false;player.transform.position=from+Vector3.up*(cc.height*.5f-cc.center.y+.03f);cc.enabled=true;Physics.SyncTransforms();int count=0;
   for(int i=0;i<900;i++){Vector3 delta=to-player.transform.position;delta.y=0;if(delta.magnitude<.08f)break;cc.Move(delta.normalized*.025f+Vector3.down*.08f);count++;}
   Vector3 feet=player.transform.position+Vector3.up*(cc.center.y-cc.height*.5f);results.Add(new{x,up,steps=count,feet=feet.ToString(),remaining=Vector2.Distance(new Vector2(feet.x,feet.z),new Vector2(to.x,to.z)),heightError=Mathf.Abs(feet.y-to.y)});
  }cc.enabled=false;player.transform.position=original;cc.enabled=true;File.WriteAllText(Out+"B2_controller_walk.json",JsonConvert.SerializeObject(results,Formatting.Indented));EditorSceneManager.OpenScene(A+"01.Scenes/Stage/Level_B5_Circular.unity");return results;
 }
}
