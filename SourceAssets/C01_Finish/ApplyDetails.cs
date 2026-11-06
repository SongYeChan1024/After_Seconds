using System;using System.IO;using System.Linq;using System.Collections.Generic;
using UnityEngine;using UnityEditor;using UnityEngine.SceneManagement;using UnityEditor.SceneManagement;using Newtonsoft.Json;
public static class ApplyDetails {
 const string M="Assets/Afrer_Seconds/05.Model/";
 static Transform root,group;
 static Bounds Bounds(GameObject g){var rs=g.GetComponentsInChildren<Renderer>(true);var b=rs[0].bounds;foreach(var r in rs.Skip(1))b.Encapsulate(r.bounds);return b;}
 static object Place(string file,string name,Vector3[] candidates,Vector3 target,float yaw){
    var holder=new GameObject(name);holder.transform.SetParent(group,false);
    var g=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(M+"Props/Common/"+file+".prefab"),holder.transform);
    float best=float.MaxValue;Quaternion choice=Quaternion.identity;
    foreach(var rot in new[]{Quaternion.identity,Quaternion.Euler(-90,0,0),Quaternion.Euler(90,0,0),Quaternion.Euler(0,0,90)}){g.transform.localRotation=rot;var b=Bounds(g);var q=new[]{Mathf.Log(b.size.x/target.x),Mathf.Log(b.size.y/target.y),Mathf.Log(b.size.z/target.z)};float mean=q.Average(),err=q.Sum(v=>(v-mean)*(v-mean));if(err<best){best=err;choice=rot;}}
    g.transform.localRotation=choice;var bb=Bounds(g);g.transform.localScale*=Mathf.Min(target.x/bb.size.x,target.y/bb.size.y,target.z/bb.size.z);bb=Bounds(g);g.transform.position+=holder.transform.position-new Vector3(bb.center.x,bb.min.y,bb.center.z);
    foreach(var c in g.GetComponentsInChildren<Collider>(true))c.enabled=false;foreach(var l in g.GetComponentsInChildren<Light>(true))l.enabled=false;
    bb=Bounds(g);var box=holder.AddComponent<BoxCollider>();box.center=holder.transform.InverseTransformPoint(bb.center);box.size=bb.size;holder.transform.localRotation=Quaternion.Euler(0,yaw,0);
    var attempts=new List<object>();bool ok=false;
    foreach(var p in candidates){holder.transform.localPosition=p;Physics.SyncTransforms();var hits=new List<string>();foreach(var c in Physics.OverlapBox(box.bounds.center,box.bounds.extents,Quaternion.identity,~0,QueryTriggerInteraction.Ignore).Where(c=>c!=box&&!c.transform.IsChildOf(holder.transform)&&c.transform.IsChildOf(root)&&!c.name.Contains("Floor"))){Vector3 d;float depth;if(Physics.ComputePenetration(box,box.transform.position,box.transform.rotation,c,c.transform.position,c.transform.rotation,out d,out depth)&&depth>.035f)hits.Add(c.name+":"+depth.ToString("F3"));}attempts.Add(new{position=p.ToString(),hits});if(hits.Count==0){ok=true;break;}}
    if(!ok){UnityEngine.Object.DestroyImmediate(holder);throw new Exception("No clear placement for "+name+": "+JsonConvert.SerializeObject(attempts));}
    return new{name,asset=file,position=holder.transform.localPosition.ToString("F3"),size=box.size.ToString("F3"),attempts};
 }
 public static object Run(){
    var s=SceneManager.GetActiveScene();if(s.isDirty||Application.isPlaying||!s.path.EndsWith("Level_B5_Circular.unity"))throw new Exception("Saved B5 edit scene required");
    root=s.GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular")).transform;var c01=root.Find("C01_Experiment_Art");if(c01.Find("C01_Finish_Props"))throw new Exception("Details already placed");
    var connections=M+"Environment/B5/AF_C01_ConsoleConnections.fbx";AssetDatabase.ImportAsset(connections,ImportAssetOptions.ForceSynchronousImport);
    var importer=(ModelImporter)AssetImporter.GetAtPath(connections);importer.importAnimation=false;importer.importCameras=false;importer.importLights=false;importer.isReadable=true;
    foreach(var n in new[]{"S1_Coat","S1_Dark","S1_Steel"})importer.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material),n),AssetDatabase.LoadAssetAtPath<Material>(M+"Environment/B5/Materials/"+n+".mat"));importer.SaveAndReimport();
    var cg=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(connections),c01);cg.name="AF_C01_ConsoleConnections";cg.transform.localPosition=Vector3.zero;
    var container=new GameObject("C01_Finish_Props");group=container.transform;group.SetParent(c01,false);
    var placed=new List<object>();
    try{
        placed.Add(Place("LP_SampleTrolley","Sample_Trolley_A",new[]{new Vector3(-4.0f,0,6.8f),new Vector3(-3.9f,0,6.2f),new Vector3(-6.8f,0,3.8f)},new Vector3(.8f,1.12f,.65f),135));
        placed.Add(Place("LP_SampleTrolley","Sample_Trolley_B",new[]{new Vector3(6.7f,0,-3.5f),new Vector3(6.9f,0,-4.0f),new Vector3(3.1f,0,-6.6f)},new Vector3(.8f,1.12f,.65f),315));
        placed.Add(Place("LP_BenchAnalyzer","Sample_Analyzer",new[]{new Vector3(-6.8f,0,-5.8f),new Vector3(-5.9f,0,-6.7f),new Vector3(-6.4f,0,-5.3f)},new Vector3(1.06f,1.43f,.7f),48));
        placed.Add(Place("SD_PPEStation","Clinical_PPE_Station",new[]{new Vector3(6.8f,0,4.9f),new Vector3(5.8f,0,6.0f),new Vector3(7.4f,0,3.9f)},new Vector3(.8f,1.8f,.5f),230));
        var light=c01.Find("Pod_Interior_Task").GetComponent<Light>();Undo.RecordObject(light,"Balance C01 task light");float old=light.intensity;light.intensity=12;EditorUtility.SetDirty(light);
        Physics.SyncTransforms();EditorSceneManager.MarkSceneDirty(s);EditorSceneManager.SaveScene(s);
        var result=new{placed,consoleConnectionPairs=2,cables=6,taskLightBefore=old,taskLightAfter=light.intensity};
        var o=Path.GetFullPath(Path.Combine(Application.dataPath,"../../../Docs/검수/2026-11-07_C01_Finish/"));File.WriteAllText(o+"prop_placement.json",JsonConvert.SerializeObject(result,Formatting.Indented));return result;
    }catch{UnityEngine.Object.DestroyImmediate(container);UnityEngine.Object.DestroyImmediate(cg);throw;}
 }
}
