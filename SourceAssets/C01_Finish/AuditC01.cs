using System;using System.IO;using System.Linq;using System.Collections.Generic;using UnityEngine;using UnityEditor;using UnityEngine.SceneManagement;using Newtonsoft.Json;
public static class AuditC01 {
 static string PathOf(Transform t)=>t.parent?PathOf(t.parent)+"/"+t.name:t.name;
 public static object Run(){
    var s=SceneManager.GetActiveScene();if(s.isDirty||Application.isPlaying)throw new Exception("Saved edit scene required");
    var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular")).transform;
    var c01=root.Find("C01_Experiment_Art");var rib=c01.Find("AF_C01_ThreePortalRibs").GetComponentInChildren<MeshCollider>();
    Physics.SyncTransforms();var misses=new List<object>();var spread=new List<float>();var unequal=new List<object>();int rays=0;
    for(int p=1;p<=171;p++){
        float phi=p*.5f*Mathf.Deg2Rad;var distances=new List<float>();
        for(int i=0;i<8;i++){
            // Offset identically from each face centre to avoid exact shared-triangle-edge rays.
            float angle=(32.55f+45*i)*Mathf.Deg2Rad;var d=new Vector3(Mathf.Cos(angle)*Mathf.Cos(phi),Mathf.Sin(phi),Mathf.Sin(angle)*Mathf.Cos(phi));RaycastHit hit;rays++;
            if(!rib.Raycast(new Ray(c01.position,c01.TransformDirection(d)),out hit,10.1f))misses.Add(new{rib=i+1,elevation=p*.5f});else distances.Add(hit.distance);
        }
        if(distances.Count==8){float difference=distances.Max()-distances.Min();spread.Add(difference);if(difference>.001f)unequal.Add(new{elevation=p*.5f,difference,distances});}
    }
    var boxes=root.GetComponentsInChildren<BoxCollider>().Where(c=>c.enabled&&Vector3.Distance(c.bounds.center,c01.position)<12&&c.bounds.size.magnitude<6).ToArray();var ribIntersections=new List<object>();
    foreach(var box in boxes){Vector3 d;float depth;if(Physics.ComputePenetration(box,box.transform.position,box.transform.rotation,rib,rib.transform.position,rib.transform.rotation,out d,out depth)&&depth>.035f)ribIntersections.Add(new{path=PathOf(box.transform),depth});}
    var props=c01.Find("C01_Finish_Props").GetComponentsInChildren<BoxCollider>().Where(c=>c.enabled).ToArray();var propIssues=new List<object>();
    foreach(var box in props)foreach(var c in Physics.OverlapBox(box.bounds.center,box.bounds.extents,Quaternion.identity,~0,QueryTriggerInteraction.Ignore).Where(c=>c!=box&&!c.transform.IsChildOf(box.transform)&&c.transform.IsChildOf(root)&&!c.name.Contains("Floor"))){Vector3 d;float depth;if(Physics.ComputePenetration(box,box.transform.position,box.transform.rotation,c,c.transform.position,c.transform.rotation,out d,out depth)&&depth>.035f)propIssues.Add(new{prop=PathOf(box.transform),other=PathOf(c.transform),depth});}
    var mf=rib.GetComponent<MeshFilter>();var vs=mf.sharedMesh.vertices;var tri=mf.sharedMesh.triangles;int badTriangles=0;for(int i=0;i<tri.Length;i+=3)if(Vector3.Cross(vs[tri[i+1]]-vs[tri[i]],vs[tri[i+2]]-vs[tri[i]]).sqrMagnitude<1e-16f)badTriangles++;
    var player=s.GetRootGameObjects().Single(g=>g.name.StartsWith("Player"));
    var result=new{rays,gaps=misses,maximumEightWayRadiusDifferenceMeters=spread.Max(),unequal,ribIntersections,checkedNearbyBoxes=boxes.Length,checkedNewProps=props.Length,propIssues,badTriangles,missingMaterials=root.GetComponentsInChildren<Renderer>().Count(r=>r.sharedMaterials.Any(m=>!m||!m.shader||m.shader.name=="Hidden/InternalErrorShader")),playerPosition=player.transform.position.ToString("F4"),playerRotation=player.transform.eulerAngles.ToString("F4")};
    var o=Path.GetFullPath(Path.Combine(Application.dataPath,"../../../Docs/검수/2026-11-07_C01_Finish/"));File.WriteAllText(o+"rib_and_prop_audit.json",JsonConvert.SerializeObject(result,Formatting.Indented));return result;
 }
}
