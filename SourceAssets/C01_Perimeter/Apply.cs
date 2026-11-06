using System;using System.IO;using System.Linq;using System.Collections.Generic;
using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.SceneManagement;using UnityEngine.Rendering;using Newtonsoft.Json;
public static class ApplyPerimeter {
 const string A="Assets/Afrer_Seconds/05.Model/",P=A+"Props/B5/",M=P+"Materials/";
 static string H=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../../SourceAssets/C01_Perimeter/"));
 static Transform root,room,bank,retired;static List<object> placed=new List<object>(),moved=new List<object>();
 static GameObject Group(string n,Transform p){var g=new GameObject(n);g.transform.SetParent(p,false);return g;}
 static Vector3 Polar(float a,float r,float y=0)=>new Vector3(Mathf.Cos(a*Mathf.Deg2Rad)*r,y,Mathf.Sin(a*Mathf.Deg2Rad)*r);
 static Transform Find(string n)=>root.GetComponentsInChildren<Transform>(true).Single(t=>t.name==n);
 static string PathOf(Transform t)=>t.parent?PathOf(t.parent)+"/"+t.name:t.name;
 static void Retire(string n){var t=Find(n);moved.Add(new{name=n,oldPath=PathOf(t),position=t.position.ToString("F4"),rotation=t.eulerAngles.ToString("F4"),action="retired"});t.SetParent(retired,true);t.name=n+"_Previous";}
 static void Position(Transform t,float a,float r,float y=0){moved.Add(new{name=t.name,oldPath=PathOf(t),position=t.position.ToString("F4"),rotation=t.eulerAngles.ToString("F4"),action="repositioned"});t.position=room.TransformPoint(Polar(a,r,y));t.rotation=Quaternion.Euler(0,270-a,0);}
 static GameObject Model(string n,Transform parent,Vector3 pos,float yaw=0){var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(P+n+".fbx");if(!prefab)throw new Exception("Missing "+n);var g=(GameObject)PrefabUtility.InstantiatePrefab(prefab,parent);g.name=n;g.transform.localPosition=pos;g.transform.localRotation=Quaternion.Euler(0,yaw,0);return g;}
 static void Box(GameObject g,Vector3 center,Vector3 size){var b=g.GetComponent<BoxCollider>();if(!b)b=g.AddComponent<BoxCollider>();b.center=center;b.size=size;}
 static void HideVisuals(Transform t){foreach(Transform child in t)child.gameObject.SetActive(false);var lod=t.GetComponent<LODGroup>();if(lod)lod.enabled=false;}
 static Material Mat(string n,Color col,float metal,float smooth){string path=M+n+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);if(!m){m=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(m,path);}m.SetColor("_BaseColor",col);m.SetFloat("_Metallic",metal);m.SetFloat("_Smoothness",smooth);return m;}
 public static object Import(){var logs=new List<string>();Application.LogCallback cb=(m,s,t)=>{if(t==LogType.Warning||t==LogType.Error||t==LogType.Exception)logs.Add(t+": "+m);};Application.logMessageReceived+=cb;try{
    var colors=new Dictionary<string,Color>{{"Coat",new Color(.79f,.85f,.86f)},{"Steel",new Color(.63f,.69f,.72f)},{"Dark",new Color(.07f,.105f,.12f)},{"Blue",new Color(.28f,.45f,.48f)},{"Screen",new Color(.018f,.05f,.06f)},{"Trace",new Color(.22f,.72f,.68f)},{"Paper",new Color(.88f,.89f,.83f)},{"Amber",new Color(.77f,.44f,.14f)},{"Glass",new Color(.70f,.86f,.90f,.14f)},{"Rubber",new Color(.025f,.04f,.045f)}};
    var mats=new Dictionary<string,Material>();
    foreach(var kv in colors){var mat=Mat("CP_"+kv.Key,kv.Value,kv.Key=="Steel"?.78f:.08f,kv.Key=="Steel"?.5f:.32f);
      if(new[]{"Coat","Blue","Steel"}.Contains(kv.Key)){string tex=A+"Environment/Common/Textures/LP_"+(kv.Key=="Steel"?"Stainless":"Coating");mat.SetTexture("_BaseMap",AssetDatabase.LoadAssetAtPath<Texture2D>(tex+"_Base.png"));mat.SetTexture("_BumpMap",AssetDatabase.LoadAssetAtPath<Texture2D>(tex+"_Normal.png"));mat.SetFloat("_BumpScale",.15f);mat.EnableKeyword("_NORMALMAP");}
      if(kv.Key=="Trace"){mat.SetColor("_EmissionColor",kv.Value*.6f);mat.EnableKeyword("_EMISSION");}
      if(kv.Key=="Glass"){mat.SetFloat("_Surface",1);mat.SetFloat("_Blend",0);mat.SetFloat("_SrcBlend",(float)BlendMode.SrcAlpha);mat.SetFloat("_DstBlend",(float)BlendMode.OneMinusSrcAlpha);mat.SetFloat("_ZWrite",0);mat.SetFloat("_Cull",2);mat.SetFloat("_Smoothness",.82f);mat.SetOverrideTag("RenderType","Transparent");mat.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");mat.renderQueue=3000;mat.SetShaderPassEnabled("ShadowCaster",false);}
      EditorUtility.SetDirty(mat);AssetDatabase.SaveAssetIfDirty(mat);mats["CP_"+kv.Key]=mat;
    }
    var files=Directory.GetFiles(Path.Combine(Application.dataPath,"Afrer_Seconds/05.Model/Props/B5"),"CP_*.fbx");
    foreach(var file in files){string path=P+Path.GetFileName(file);AssetDatabase.ImportAsset(path,ImportAssetOptions.ForceSynchronousImport);var im=(ModelImporter)AssetImporter.GetAtPath(path);im.importAnimation=false;im.importCameras=false;im.importLights=false;im.isReadable=true;
      if(path.Contains("VitalMonitor"))im.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material),"S1_VitalMonitor"),AssetDatabase.LoadAssetAtPath<Material>(M+"S1_VitalMonitor.mat"));
      foreach(var kv in mats)im.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material),kv.Key),kv.Value);im.SaveAndReimport();}
    File.WriteAllText(H+"import.json",JsonConvert.SerializeObject(new{files=files.Length,logs},Formatting.Indented));return new{files=files.Length,logs};
 }finally{Application.logMessageReceived-=cb;}}
 public static object Apply(){
    var s=SceneManager.GetActiveScene();if(s.isDirty||Application.isPlaying||!s.path.EndsWith("Level_B5_Circular.unity"))throw new Exception("Saved B5 edit scene required");
    root=s.GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular")).transform;room=root.Find("C01_Experiment_Art");if(room.Find("C01_Perimeter_Lab"))throw new Exception("Already applied");
    bank=Group("C01_Perimeter_Lab",room).transform;retired=Group("Retired_C01_SparseFixtures",room).transform;retired.gameObject.SetActive(false);
    foreach(var n in new[]{"CD-026_CFD_ServiceBackplate","CD-028_CFD_InspectionBox","S1_ServiceBackboard_Support","S1_ServiceRiser_22","AF_C01_ConsoleConnections","Trial_Records_Cabinet","Sample_Analyzer","Clinical_PPE_Station","CD-038_CFD_TransferCabinet"})Retire(n);
    var angles=new[]{32,40,48,56,64,72,80,128,136,144,152,160,168,216,224,232,240,248,256,264,272,280,288,296,304,312,320,328,336,344};
    foreach(int a in angles){var bay=Group("Station_"+a,bank).transform;bay.localPosition=Polar(a,8.80f);bay.localRotation=Quaternion.Euler(0,270-a,0);
      string baseModel=(a==224||a==232)?"CP_WashBench":new[]{256,264,320,328}.Contains(a)?"CP_ColdStorage":a==32?"CP_PPEStation":a==168?null:a%16==0?"CP_DrawerBench":"CP_LabBench";
      if(baseModel!=null){var g=Model(baseModel,bay,Vector3.zero);float height=baseModel=="CP_ColdStorage"?2.23f:baseModel=="CP_PPEStation"?1.80f:.96f;Box(g,new Vector3(0,height/2,0),new Vector3(baseModel=="CP_ColdStorage"?1.02f:baseModel=="CP_PPEStation"?.92f:1.265f,height,baseModel=="CP_PPEStation"?.46f:.8f));if(a==32)g.name="Clinical_PPE_Station";}
      if(!new[]{32,168,256,264,320,328}.Contains(a)){
        if(a!=152)Model("CP_ServicePanel",bay,new Vector3(0,.96f,-.47f));
        if(a!=152&&a!=272){bool shelf=new[]{40,64,136,216,240,280,304,336}.Contains(a);Model(shelf?"CP_ReagentShelf":"CP_UpperCabinet",bay,new Vector3(0,shelf?1.52f:1.90f,-.18f));}
        if(new[]{48,72,128,280,304}.Contains(a))Model("CP_OpticalAnalyzer",bay,new Vector3(0,.955f,.025f));
        else if(new[]{56,288,312}.Contains(a))Model("CP_Centrifuge",bay,new Vector3(-.15f,.955f,.015f));
        else if(!new[]{152,224,232,272}.Contains(a))Model("CP_PreparationKit",bay,new Vector3(0,.955f,.03f));
      }
      placed.Add(new{angle=a,baseModel,position=bay.localPosition.ToString("F3"),width=baseModel=="CP_ColdStorage"?1.02f:baseModel=="CP_PPEStation"?.92f:baseModel==null?.8f:1.265f});
    }
    // A single main inspection panel, physically integrated into the utility station.
    Position(Find("CD-029_CFD_ServiceBackplate"),152,9.24f,.90f);Position(Find("CD-030_CFD_Vent"),152,9.24f,2.32f);Position(Find("CD-031_CFD_InspectionBox"),152,9.24f,1.30f);
    Position(Find("CD-027_CFD_Vent"),332,9.22f,2.55f);
    foreach(int a in new[]{44,76,132,228,276,308}){var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(A+"Environment/Common/CFD_Vent.prefab");var g=(GameObject)PrefabUtility.InstantiatePrefab(prefab,bank);g.name="Vent_"+a;g.transform.localPosition=Polar(a,9.20f,2.60f);g.transform.localRotation=Quaternion.Euler(0,270-a,0);}
    Position(Find("S1_Clock_20"),272,9.17f,2.05f);Position(Find("S1_RecordBoard_19"),272,9.17f,1.48f);
    Position(Find("CD-039_CFD_LinenHamper"),218,7.55f);Position(Find("Clinical_SealedWaste"),230,7.35f);
    // Preserve the cabinet's named scene root and its original model under disabled children.
    var cab=Find("CD-040_CFD_EmergencyCabinet");HideVisuals(cab);Position(cab,168,8.8f);Model("CP_EmergencyCabinet",cab,Vector3.zero);var glass=Model("CP_EmergencyGlass",cab,Vector3.zero);foreach(var r in glass.GetComponentsInChildren<Renderer>()){r.shadowCastingMode=ShadowCastingMode.Off;r.receiveShadows=false;}Box(cab.gameObject,new Vector3(0,.71f,0),new Vector3(.80f,1.42f,.48f));
    foreach(string n in new[]{"Observation_Console_A","Observation_Console_B"}){var t=Find(n);HideVisuals(t);Model("CP_ObservationConsole",t,Vector3.zero);Box(t.gameObject,new Vector3(0,.75f,-.01f),new Vector3(1.70f,1.50f,.92f));}
    var vital=Find("S1_VitalMonitor_18");HideVisuals(vital);var repaired=Model("CP_VitalMonitor_Repaired",vital,Vector3.zero);var lod=repaired.GetComponent<LODGroup>();if(!lod)lod=repaired.AddComponent<LODGroup>();var rs=repaired.GetComponentsInChildren<Renderer>();lod.SetLODs(new[]{new LOD(.25f,new[]{rs.Single(r=>r.name.EndsWith("LOD0"))}),new LOD(.10f,new[]{rs.Single(r=>r.name.EndsWith("LOD1"))}),new LOD(.02f,new[]{rs.Single(r=>r.name.EndsWith("LOD2"))})});lod.RecalculateBounds();
    Model("CP_PerimeterServiceRuns",bank,Vector3.zero);
    var lamps=Group("Integrated_Worklights",bank).transform;
    foreach(int a in new[]{52,144,232,280,328}){var g=Group("Worklight_"+a,lamps);g.transform.localPosition=Polar(a,7.95f,2.65f);g.transform.LookAt(room.TransformPoint(Polar(a,8.8f,1.1f)));var l=g.AddComponent<Light>();l.type=LightType.Spot;l.color=new Color(.79f,.89f,.93f);l.intensity=5.5f;l.range=4.5f;l.spotAngle=105;l.shadows=LightShadows.None;}
    Physics.SyncTransforms();EditorSceneManager.MarkSceneDirty(s);EditorSceneManager.SaveScene(s);
    File.WriteAllText(H+"placement.json",JsonConvert.SerializeObject(new{stations=placed,moved,addedWorklights=5,mainInspectionPanels=1,consoleReplacements=2,cabinetInterior=true,vitalOriginalSilhouette=true},Formatting.Indented));return new{stations=placed.Count,moved=moved.Count,models=bank.GetComponentsInChildren<MeshFilter>().Length};
 }
 public static object Save(){var s=SceneManager.GetActiveScene();if(Application.isPlaying||!s.path.EndsWith("Level_B5_Circular.unity"))throw new Exception("B5 edit scene required");return new{saved=EditorSceneManager.SaveScene(s),s.isDirty};}
 public static object RecoverPartial(){var s=SceneManager.GetActiveScene();var marker=s.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Transform>(true)).Single(t=>t.name=="C01_Perimeter_Lab");if(marker.childCount!=1&&marker.childCount!=36)throw new Exception("Unexpected partial stage");EditorSceneManager.OpenScene(s.path);return "Restored saved scene after authoring failure";}
}
