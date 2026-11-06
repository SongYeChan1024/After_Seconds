// Level route/section controller verification V0.01. External Editor-only temporary probes.
using System;using System.IO;using System.Linq;using System.Collections.Generic;
using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.SceneManagement;
using Newtonsoft.Json;using Newtonsoft.Json.Linq;
public static class WalkContinuation {
 static string Repo=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 static Vector3 P(float u,float h,float v)=>new Vector3(u-24,h,v-16);
 public static object Check(){
  if(EditorApplication.isPlaying||SceneManager.GetActiveScene().isDirty)throw new Exception("Saved Edit scene required");var original=SceneManager.GetActiveScene().path;var reports=new List<object>();var routes=JObject.Parse(File.ReadAllText(Repo+"/Docs/도면/잠입_탐색/플레이어_예상이동/player_routes.json"))["routes"];
  try{foreach(string floor in new[]{"B5","B4","B3"}){
   var s=EditorSceneManager.OpenScene("Assets/Afrer_Seconds/01.Scenes/Stage/Level_"+floor+"_Stealth.unity");var player=s.GetRootGameObjects().Single(g=>g.name.StartsWith("Player")).GetComponent<CharacterController>();bool enabled=player.enabled;player.enabled=false;var results=new List<object>();
   try{
    foreach(var route in routes.Where(r=>(string)r["floor"]==floor))results.Add(Walk("Route_"+route["variant"],route["legs"].SelectMany(l=>l["points"]).Select(p=>P((float)p[0],0,(float)p[1])).ToList(),0));
    if(floor=="B5"||floor=="B4"){
     float bottom=floor=="B5"?0:-7.8f;float top=bottom+7.8f;
     results.Add(Walk("StairA_Up",new List<Vector3>{P(42.3f,bottom,27),P(42.3f,0,19.25f),P(40.3f,0,19.25f),P(40.3f,0,28.25f)},top));
     results.Add(Walk("StairA_Down",new List<Vector3>{P(40.3f,top,28.25f),P(40.3f,0,19.25f),P(42.3f,0,19.25f),P(42.3f,0,27)},bottom));
    }
    if(floor=="B4"||floor=="B3"){
     float bottom=floor=="B4"?0:-6.4f;float top=bottom+6.4f;
     results.Add(Walk("StairB_Up",new List<Vector3>{P(46.65f,bottom,24.5f),P(46.65f,0,30.7f),P(44.75f,0,30.7f),P(44.75f,0,23.5f)},top));
     results.Add(Walk("StairB_Down",new List<Vector3>{P(44.75f,top,23.5f),P(44.75f,0,30.7f),P(46.65f,0,30.7f),P(46.65f,0,24.5f)},bottom));
    }
    if(floor=="B4"){
     results.Add(Walk("Deck_Up",new List<Vector3>{P(28.2f,0,14.4f),P(28.2f,0,19.4f),P(30.1f,0,19.4f)},2.5f));
     results.Add(Walk("Deck_Down",new List<Vector3>{P(30.1f,2.5f,19.4f),P(28.2f,0,19.4f),P(28.2f,0,14.4f)},0));
    }
   }finally{player.enabled=enabled;}reports.Add(new{floor,results});
  }}finally{EditorSceneManager.OpenScene(original);}File.WriteAllText(Repo+"/Docs/검수/2026-11-06_LevelContinuation/controller.json",JsonConvert.SerializeObject(new{mode="Temporary CharacterController.Move in Editor, not player/AI gameplay",settings=new{radius=.28,height=1.8,stepOffset=.3,skinWidth=.08,slopeLimit=45},reports},Formatting.Indented));return reports;
 }
    static object Walk(string name, List<Vector3> points, float expectedHeight)
    {
        var probe = new GameObject("TemporaryControllerProbe") {hideFlags=HideFlags.HideAndDontSave};
        var controller=probe.AddComponent<CharacterController>();
        controller.radius=0.28f;
        controller.height=1.8f;
        controller.center=Vector3.up*0.9f;
        controller.stepOffset=0.3f;
        controller.skinWidth=0.08f;
        controller.slopeLimit=45;
        controller.minMoveDistance=0;
        probe.transform.position=points[0]+Vector3.up*0.12f;
        Physics.SyncTransforms();
        var failures=new List<object>();
        int moves=0;
        try {
            foreach (var target in points.Skip(1)) {
                int limit=Mathf.CeilToInt(Vector3.Distance(new Vector3(probe.transform.position.x,0,probe.transform.position.z),new Vector3(target.x,0,target.z))/0.035f)+80;
                bool reached=false;
                for (int step=0;step<limit;step++) {
                    var displacement=target-probe.transform.position;
                    displacement.y=0;
                    if (displacement.magnitude<0.06f) {reached=true;break;}
                    controller.Move(Vector3.ClampMagnitude(displacement,0.035f)+Vector3.down*0.045f);
                    moves++;
                }
                if (!reached) {failures.Add(new {target=target.ToString("F2"),actual=probe.transform.position.ToString("F2")});break;}
            }
            for(int step=0;step<10;step++) controller.Move(Vector3.down*0.045f);
            float height=probe.transform.position.y;
            return new {name,moves,failures,finalPosition=probe.transform.position.ToString("F3"),expectedHeight,heightError=Mathf.Abs(height-expectedHeight),passed=failures.Count==0 && Mathf.Abs(height-expectedHeight)<0.15f};
        }
        finally {UnityEngine.Object.DestroyImmediate(probe);}
    }

}
