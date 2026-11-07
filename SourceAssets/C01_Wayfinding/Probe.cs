using System;using System.IO;using System.Linq;using System.Collections.Generic;using UnityEngine;using UnityEngine.SceneManagement;using Newtonsoft.Json;using Newtonsoft.Json.Linq;
public static class C01WayfindingProbe {
 public static object Run(){
  var s=SceneManager.GetActiveScene();if(s.isDirty||Application.isPlaying||!s.path.EndsWith("Level_B5_Circular.unity"))throw new Exception("Saved B5 scene required");
  string r=Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));var plan=JObject.Parse(File.ReadAllText(r+"/SourceAssets/C01_Wayfinding/plan.json"));var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular")).transform;Vector3 origin=root.Find("C01_Experiment_Art").position;
  var blocked=new List<object>();var ground=new List<float>();int samples=0;Physics.SyncTransforms();
  foreach(var route in plan["routes"]){var p=route["points"].Select(t=>origin+new Vector3((float)t[0],0,(float)t[1])).ToArray();for(int i=1;i<p.Length;i++){int n=Mathf.CeilToInt(Vector3.Distance(p[i-1],p[i])/.16f);for(int j=0;j<=n;j++){var pos=Vector3.Lerp(p[i-1],p[i],(float)j/n);samples++;
   var hits=Physics.OverlapCapsule(pos+Vector3.up*.36f,pos+Vector3.up*1.52f,.28f,~0,QueryTriggerInteraction.Ignore).Where(c=>c.transform.IsChildOf(root)&&!c.name.Contains("Floor")&&!c.name.Contains("Threshold")).ToArray();if(hits.Length>0)blocked.Add(new{code=(string)route["id"],point=new[]{pos.x,pos.y,pos.z},hits=hits.Select(c=>c.name).ToArray()});
   var surface=Physics.RaycastAll(pos+Vector3.up*.30f,Vector3.down,.60f,~0,QueryTriggerInteraction.Ignore).Where(h=>h.collider.transform.IsChildOf(root)&&h.normal.y>.85f).OrderByDescending(h=>h.point.y).ToArray();if(surface.Length>0)ground.Add(surface[0].point.y-origin.y);
  }}}
  var result=new{samples,blocked,groundMin=ground.Min(),groundMax=ground.Max(),groundSamples=ground.Count};File.WriteAllText(r+"/Docs/검수/2026-11-07_C01_Wayfinding/route_probe.json",JsonConvert.SerializeObject(result,Formatting.Indented));return result;
 }
}
