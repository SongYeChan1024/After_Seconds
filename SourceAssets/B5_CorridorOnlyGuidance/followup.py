from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1];src=R/'SourceAssets/B5_OperationalDetail'
s=(src/'Audit.cs').read_text(encoding='utf-8').replace('B5_OperationalDetail','B5_CorridorOnlyGuidance').replace('B5_Operational_Detail','B5_CorridorOnly_Guidance').replace('OperationalAudit','CorridorAudit');(H/'Audit.cs').write_text(s,encoding='utf-8')
s=(src/'Capture.cs').read_text(encoding='utf-8').replace('B5_OperationalDetail','B5_CorridorOnlyGuidance').replace('OperationalCapture','CorridorCapture')
start=s.index(' public static object Run()')
s=s[:start]+''' public static object Run(){var s=SceneManager.GetActiveScene();if(s.isDirty||Application.isPlaying)throw new Exception("Saved Edit required");var plan=JObject.Parse(File.ReadAllText(Repo+"/SourceAssets/B5_CorridorOnlyGuidance/plan.json"));int count=0;try{foreach(var entry in (JObject)plan["rooms"]){var r=entry.Value;var o=new Vector3((float)r["x"],-82,-(float)r["v"]);var door=r["doors"][0];float a=(float)door["angle"]*Mathf.Deg2Rad;var dir=new Vector3(Mathf.Cos(a),0,Mathf.Sin(a));Shot(entry.Key+"_dome",o+dir*((float)r["r"]-1.5f)+Vector3.up*1.65f,o+Vector3.up*.70f,90);count++;}foreach(var t in plan["tunnels"]){var p=new Vector3((float)t["p"][0],-80.35f,-(float)t["p"][1]);var q=new Vector3((float)t["q"][0],-80.35f,-(float)t["q"][1]);var f=(q-p).normalized;Shot((string)t["id"]+"_corridor",p+f*2.1f,q-Vector3.up*.75f,80);count++;if(new[]{"B5-T01","B5-T05","B5-T13"}.Contains((string)t["id"])){Shot((string)t["id"]+"_threshold",p+f*2.6f,p-f*3-Vector3.up*.7f,85);count++;}}}finally{EditorSceneManager.OpenScene(s.path);}return new{images=count,output=O};}
}
'''
(H/'Capture.cs').write_text(s,encoding='utf-8')
print('Capture and audit ready')
