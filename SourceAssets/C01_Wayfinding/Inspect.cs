using System;using System.IO;using System.Linq;using UnityEngine;using UnityEditor;using UnityEngine.SceneManagement;using Newtonsoft.Json;
public static class C01WayfindingInspect {
 static float[] V(Vector3 v)=>new[]{v.x,v.y,v.z};
 static string P(Transform t)=>t.parent?P(t.parent)+"/"+t.name:t.name;
 public static object Run(){
  var s=SceneManager.GetActiveScene();if(Application.isPlaying||!s.path.EndsWith("Level_B5_Circular.unity"))throw new Exception("B5 edit scene required");
  var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular")).transform;var room=root.Find("C01_Experiment_Art");
  var transforms=root.GetComponentsInChildren<Transform>(true);var all=root.GetComponentsInChildren<Renderer>(true);
  var markings=all.Where(r=>new[]{"Guide","Route","R1","S1_Line","Stripe","Marking","Arrow","Sign"}.Any(n=>r.name.IndexOf(n,StringComparison.OrdinalIgnoreCase)>=0));
  var nearby=all.Where(r=>r.gameObject.activeInHierarchy&&Vector3.Distance(r.bounds.center,room.position)<13);
  var result=new{scene=s.path,dirty=s.isDirty,root=root.name,roomPosition=V(room.position),selected=Selection.activeGameObject?P(Selection.activeGameObject.transform):null,
   children=root.Cast<Transform>().Select(t=>new{t.name,active=t.gameObject.activeSelf,position=V(t.position)}).ToArray(),
   markings=markings.Select(r=>new{path=P(r.transform),active=r.gameObject.activeInHierarchy,position=V(r.transform.position),min=V(r.bounds.min),max=V(r.bounds.max),mesh=r.GetComponent<MeshFilter>()?AssetDatabase.GetAssetPath(r.GetComponent<MeshFilter>().sharedMesh):"",materials=r.sharedMaterials.Select(m=>m?m.name:null).ToArray()}).ToArray(),
   nearby=nearby.Select(r=>new{path=P(r.transform),min=V(r.bounds.min),max=V(r.bounds.max)}).ToArray(),
   doors=root.Find("Pocket_Doors_Open").Cast<Transform>().Where(d=>Vector3.Distance(d.position,room.position)<12).Select(d=>new{d.name,position=V(d.position),forward=V(d.Find("Clinical_Portal").forward)}).ToArray(),
   colliders=root.GetComponentsInChildren<Collider>().Where(c=>c.enabled&&Vector3.Distance(c.bounds.center,room.position)<17).Select(c=>new{path=P(c.transform),type=c.GetType().Name,min=V(c.bounds.min),max=V(c.bounds.max),trigger=c.isTrigger}).ToArray(),
   lights=root.GetComponentsInChildren<Light>(true).Select(l=>new{path=P(l.transform),enabled=l.enabled,active=l.gameObject.activeInHierarchy,type=l.type.ToString(),position=V(l.transform.position),rotation=V(l.transform.eulerAngles),l.intensity,l.range,l.spotAngle,color=V(new Vector3(l.color.r,l.color.g,l.color.b))}).ToArray(),
   hierarchy=transforms.Select(t=>new{path=P(t),position=V(t.localPosition),rotation=V(t.localEulerAngles),scale=V(t.localScale),active=t.gameObject.activeSelf}).ToArray()};
  string o=Path.GetFullPath(Path.Combine(Application.dataPath,"../../../Docs/검수/2026-11-07_C01_Wayfinding/"));Directory.CreateDirectory(o);File.WriteAllText(o+"before.json",JsonConvert.SerializeObject(result,Formatting.Indented));
  return new{scene=s.path,dirty=s.isDirty,roomPosition=result.roomPosition,markings=result.markings,doors=result.doors,output=o};
 }
}
