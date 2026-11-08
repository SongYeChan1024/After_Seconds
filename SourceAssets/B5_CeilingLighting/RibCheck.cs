using System;using System.IO;using System.Linq;using UnityEngine;using UnityEditor;using UnityEngine.SceneManagement;using Newtonsoft.Json;
public static class CeilingRibCheck {
 static float Segment(Vector3 p,Vector3 a,Vector3 b){var e=b-a;return Vector3.Distance(p,a+e*Mathf.Clamp01(Vector3.Dot(p-a,e)/e.sqrMagnitude));}
 static float Triangle(Vector3 p,Vector3 a,Vector3 b,Vector3 c){var n=Vector3.Cross(b-a,c-a);if(n.sqrMagnitude<1e-12f)return Mathf.Min(Segment(p,a,b),Segment(p,b,c),Segment(p,c,a));var q=p-n*(Vector3.Dot(p-a,n)/n.sqrMagnitude);if(Vector3.Dot(Vector3.Cross(b-a,q-a),n)>=0&&Vector3.Dot(Vector3.Cross(c-b,q-b),n)>=0&&Vector3.Dot(Vector3.Cross(a-c,q-c),n)>=0)return Vector3.Distance(p,q);return Mathf.Min(Segment(p,a,b),Segment(p,b,c),Segment(p,c,a));}
 public static object Run(){
  var root=SceneManager.GetActiveScene().GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular"));
  var ribs=root.GetComponentsInChildren<MeshFilter>(true).Where(m=>m.gameObject.activeInHierarchy&&m.name.Contains("ThreePortalRibs")).ToArray();
  var center=new Vector3(-15,-82,-10);
  var fixtures=root.GetComponentsInChildren<Transform>().Where(t=>t.name.StartsWith("C01_천장등_")).ToArray();
  var verts=ribs.SelectMany(m=>m.sharedMesh.vertices.Select(v=>m.transform.TransformPoint(v))).ToArray();
  var result=new{ribNames=ribs.Select(r=>r.name).ToArray(),sampleAngles=verts.Where(v=>v.y>-74.1f&&v.y<-73.7f).Select(v=>Mathf.Atan2(v.z-center.z,v.x-center.x)*Mathf.Rad2Deg).GroupBy(a=>Mathf.Round(a/5)*5).Select(g=>new{deg=g.Key,count=g.Count()}).OrderBy(x=>x.deg).ToArray(),fixtures=fixtures.Select(t=>new{t.name,position=t.position.ToString(),angle=Mathf.Atan2(t.position.z-center.z,t.position.x-center.x)*Mathf.Rad2Deg,nearestRibVertex=verts.Min(v=>Vector3.Distance(v,t.position)),radius=t.GetComponentInChildren<Renderer>().bounds.extents.magnitude}).ToArray()};
  var clearance=fixtures.Select(f=>{var bounds=f.GetComponentInChildren<Renderer>().bounds;float d=float.MaxValue;foreach(var rib in ribs){var v=rib.sharedMesh.vertices.Select(x=>rib.transform.TransformPoint(x)).ToArray();var tris=rib.sharedMesh.triangles;for(int i=0;i<tris.Length;i+=3)d=Mathf.Min(d,Triangle(bounds.center,v[tris[i]],v[tris[i+1]],v[tris[i+2]]));}return new{name=f.name,conservativeClearance=d-bounds.extents.magnitude};}).ToArray();
  var report=new{geometry=result,clearance,minClearance=clearance.Min(x=>x.conservativeClearance)};
  File.WriteAllText(Path.GetFullPath(Path.Combine(Application.dataPath,"../../../Docs/검수/2026-11-08_B5_CeilingLighting/c01_rib_clearance.json")),JsonConvert.SerializeObject(report,Formatting.Indented));
  if(report.minClearance<=0)throw new Exception("Fixture bounding sphere intersects rib mesh");
  return new{count=fixtures.Length,report.minClearance};
 }
}
