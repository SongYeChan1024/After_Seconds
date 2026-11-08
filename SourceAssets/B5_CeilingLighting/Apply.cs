using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEngine.SceneManagement;
using UnityEditor.SceneManagement;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

public static class CeilingApply {
 const string E="Assets/Afrer_Seconds/05.Model/Environment/B5/";
 const string Common="Assets/Afrer_Seconds/05.Model/Environment/Common/";
 static string Repo=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 static Vector3 V(JToken j)=>new Vector3((float)j[0],(float)j[1],(float)j[2]);
 static float[] V(Vector3 v)=>new[]{v.x,v.y,v.z};
 static string Id(UnityEngine.Object o)=>GlobalObjectId.GetGlobalObjectIdSlow(o).ToString();
 static T Obj<T>(string id) where T:UnityEngine.Object {if(!GlobalObjectId.TryParse(id,out var g))throw new Exception("Invalid ID");var o=GlobalObjectId.GlobalObjectIdentifierToObjectSlow(g) as T;if(!o)throw new Exception("Missing ID "+id);return o;}
 static GameObject Child(string name,Transform parent){var g=new GameObject(name);g.transform.SetParent(parent,false);return g;}
 static void Record(GameObject g){foreach(var t in g.GetComponentsInChildren<Transform>(true))if(PrefabUtility.IsPartOfPrefabInstance(t)){PrefabUtility.RecordPrefabInstancePropertyModifications(t);PrefabUtility.RecordPrefabInstancePropertyModifications(t.gameObject);foreach(var r in t.GetComponents<Renderer>())PrefabUtility.RecordPrefabInstancePropertyModifications(r);}}
 public static object Run(){
  var s=SceneManager.GetActiveScene();if(Application.isPlaying||!s.path.EndsWith("Level_B5_Circular.unity"))throw new Exception("B5 Edit required");
  var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular")).transform;if(root.Find("B5_천장조명"))throw new Exception("Already applied");
  var backup=Path.Combine(Path.GetTempPath(),"AfterSeconds_CeilingApply_"+DateTime.Now.ToString("yyyyMMdd_HHmmss")+".unity");
  if(!EditorSceneManager.SaveScene(s,backup,true))throw new Exception("Backup failed");
  var plan=JObject.Parse(File.ReadAllText(Repo+"/SourceAssets/B5_CeilingLighting/plan.json"));
  var diffuser=new Material(AssetDatabase.LoadAssetAtPath<Material>(E+"Materials/CL_Lamp.mat"));diffuser.name="DL_CeilingDiffuser";
  diffuser.SetColor("_BaseColor",new Color(.88f,.94f,.98f));diffuser.SetColor("_EmissionColor",new Color(.91f,.96f,1)*2.2f);diffuser.EnableKeyword("_EMISSION");diffuser.globalIlluminationFlags=MaterialGlobalIlluminationFlags.BakedEmissive;diffuser.SetFloat("_Smoothness",.28f);AssetDatabase.CreateAsset(diffuser,E+"Materials/DL_CeilingDiffuser.mat");
  var ceiling=Child("B5_천장조명",root).transform;var added=Child("B5_복도조명_보강",root).transform;
  var moves=new List<object>();var created=new List<object>();var affectedTransforms=new HashSet<string>();var changedLights=new HashSet<string>();int lamps=0;
  foreach(var r in plan["rooms"]){
   string code=(string)r["code"];var room=Child(code+"_천장조명",ceiling).transform;var center=V(r["center"]);float radius=(float)r["radius"],ring=(float)r["ring"];int n=(int)r["count"];
   for(int i=0;i<n;i++){
    float a=((float)r["angle"]+360f*i/n)*Mathf.Deg2Rad;var normal=new Vector3(Mathf.Cos(a)*.55f,Mathf.Sqrt(1-.55f*.55f),Mathf.Sin(a)*.55f);var tangent=new Vector3(-Mathf.Sin(a),0,Mathf.Cos(a));
    var rotation=Quaternion.LookRotation(Vector3.Cross(tangent,normal),normal);
    var g=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(E+"CL_PodCeilingLight.fbx"),room);
    g.name=code+"_천장등_"+(i+1).ToString("00");g.transform.SetPositionAndRotation(center+normal*(radius-.235f),rotation);g.transform.localScale=Vector3.one*1.25f;
    foreach(var rr in g.GetComponentsInChildren<Renderer>()){rr.sharedMaterials=rr.sharedMaterials.Select(m=>m.name.Contains("Lamp")?diffuser:m).ToArray();rr.shadowCastingMode=ShadowCastingMode.On;}
    // A light belongs to its visible diffuser and points along the fixture's inward normal.
    var lg=Child("광원",g.transform);lg.transform.localPosition=new Vector3(0,-.055f,0);lg.transform.localRotation=Quaternion.Euler(90,0,0);var l=lg.AddComponent<Light>();l.type=LightType.Spot;l.spotAngle=125;l.innerSpotAngle=86;l.range=(float)r["range"];l.intensity=(float)r["intensity"];l.color=new Color(.91f,.96f,1);l.shadows=LightShadows.Soft;l.shadowBias=.01f;l.shadowNormalBias=.015f;l.shadowNearPlane=.1f;
    l.GetUniversalAdditionalLightData().usePipelineSettings=false;var lightData=new SerializedObject(l.GetUniversalAdditionalLightData());lightData.FindProperty("m_AdditionalLightsShadowResolutionTier").intValue=0;lightData.ApplyModifiedPropertiesWithoutUndo();
    Record(g);lamps++;
   }
  }
  int clone=0,attached=0;
  foreach(var t in plan["tunnels"]){
   string code=((string)t["id"]).Replace("B5-","");var parent=Child(code+"_보강조명",added).transform;
   foreach(var m in t["moves"]){var rr=Obj<Renderer>((string)m["id"]);var g=rr.gameObject;var before=V(g.transform.position);
    foreach(var tr in g.GetComponentsInChildren<Transform>(true))affectedTransforms.Add(Id(tr));
    g.transform.position=V(m["position"]);Record(g);moves.Add(new{id=(string)m["id"],path=(string)m["path"],before,after=V(g.transform.position)});
   }
   foreach(var a in t["additions"]){
    GameObject g;
    if(a["cloneId"]!=null){var source=Obj<Renderer>((string)a["cloneId"]);g=UnityEngine.Object.Instantiate(source.gameObject,parent);clone++;}
    else{g=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Common+"CFD_SealedLight.prefab"),parent);foreach(var l in g.GetComponentsInChildren<Light>(true))UnityEngine.Object.DestroyImmediate(l);foreach(var c in g.GetComponentsInChildren<Collider>(true))UnityEngine.Object.DestroyImmediate(c);attached++;}
    g.name=code+"_천장등_보강_"+(parent.childCount).ToString("00");g.transform.position=V(a["position"]);g.transform.rotation=Quaternion.LookRotation(V(t["forward"]),Vector3.up);
    foreach(var rr in g.GetComponentsInChildren<Renderer>())rr.sharedMaterials=rr.sharedMaterials.Select(m=>m.name.Contains("Lamp")?diffuser:m).ToArray();
    if(a["existingLight"]!=null){var l=Obj<Light>((string)a["existingLight"]);affectedTransforms.Add(Id(l.transform));changedLights.Add(Id(l));l.transform.position=g.transform.position+Vector3.down*.14f;PrefabUtility.RecordPrefabInstancePropertyModifications(l.transform);}
    Record(g);created.Add(new{code,position=V(g.transform.position),existingLight=(string)a["existingLight"],cloneId=(string)a["cloneId"]});
   }
  }
  AssetDatabase.SaveAssets();Physics.SyncTransforms();EditorSceneManager.MarkSceneDirty(s);if(!EditorSceneManager.SaveScene(s))throw new Exception("Save failed");
  var result=new{backup,domes=12,ceilingFixtures=lamps,corridorMoves=moves,corridorCreated=created,newCorridorLights=clone,attachedExistingLights=attached,affectedTransforms=affectedTransforms.ToArray(),changedLights=changedLights.ToArray(),lights=root.GetComponentsInChildren<Light>(true).Length};
  File.WriteAllText(Repo+"/Docs/검수/2026-11-08_B5_CeilingLighting/apply.json",JsonConvert.SerializeObject(result,Formatting.Indented));
  return new{domes=12,ceilingFixtures=lamps,corridorMoved=moves.Count,corridorAdded=created.Count,newCorridorLights=clone,attachedExistingLights=attached,result.lights};
 }
}
