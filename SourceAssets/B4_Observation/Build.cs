using System;using System.IO;using System.Linq;using System.Collections.Generic;using UnityEngine;using UnityEditor;using UnityEngine.SceneManagement;using UnityEditor.SceneManagement;using UnityEngine.Rendering;using UnityEngine.Rendering.Universal;using Newtonsoft.Json;using Newtonsoft.Json.Linq;
public static class B4Build {
 const string A="Assets/Afrer_Seconds/05.Model/",E=A+"Environment/B4/",P=A+"Props/B4/",ScenePath="Assets/Afrer_Seconds/01.Scenes/Stage/Level_B4_Circular.unity";
 static string Repo=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 static Dictionary<string,Material> mats=new Dictionary<string,Material>();static Transform root;static List<object> placements=new List<object>();
 static GameObject Child(string n,Transform p){var g=new GameObject(n);g.transform.SetParent(p,false);return g;}
 static void Mat(string n,Color c,float metal,float smooth,string texture=null){
  string path=E+"Materials/B4O_"+n+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);if(!m){m=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(m,path);}m.name="B4O_"+n;m.SetColor("_BaseColor",c);m.SetFloat("_Metallic",metal);m.SetFloat("_Smoothness",smooth);
  if(texture!=null){var t=AssetDatabase.LoadAssetAtPath<Texture2D>(texture);if(!t)throw new Exception("Texture missing "+texture);m.SetTexture("_BaseMap",t);if(n.StartsWith("Display")){m.SetTexture("_EmissionMap",t);m.SetColor("_EmissionColor",Color.white*.65f);m.EnableKeyword("_EMISSION");m.globalIlluminationFlags=MaterialGlobalIlluminationFlags.BakedEmissive;m.SetFloat("_SpecularHighlights",0);}}
  if(n=="Coat"||n=="Floor"||n=="Steel"){string normal=A+"Environment/Common/Textures/LP_"+(n=="Coat"?"Coating":n=="Floor"?"Concrete":"Stainless")+"_Normal.png";var t=AssetDatabase.LoadAssetAtPath<Texture2D>(normal);if(t){m.SetTexture("_BumpMap",t);m.SetFloat("_BumpScale",.16f);m.EnableKeyword("_NORMALMAP");}}
  if(n=="Lamp"||n=="Indicator"){m.SetColor("_EmissionColor",c*(n=="Lamp"?2.0f:.6f));m.EnableKeyword("_EMISSION");m.globalIlluminationFlags=MaterialGlobalIlluminationFlags.BakedEmissive;}
  if(n=="Glass"){m.SetFloat("_Surface",1);m.SetFloat("_SrcBlend",(float)BlendMode.SrcAlpha);m.SetFloat("_DstBlend",(float)BlendMode.OneMinusSrcAlpha);m.SetFloat("_ZWrite",0);m.SetFloat("_Cull",0);m.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");m.SetOverrideTag("RenderType","Transparent");m.renderQueue=3000;}
  if(n=="FloorLabel"){m.SetFloat("_AlphaClip",1);m.SetFloat("_Cutoff",.4f);m.EnableKeyword("_ALPHATEST_ON");m.SetOverrideTag("RenderType","TransparentCutout");m.renderQueue=2450;}
  EditorUtility.SetDirty(m);AssetDatabase.SaveAssetIfDirty(m);mats[m.name]=m;
 }
 static void Materials(){
  Directory.CreateDirectory(Path.Combine(Application.dataPath,"Afrer_Seconds/05.Model/Environment/B4/Materials"));AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
  foreach(var file in Directory.GetFiles(Path.Combine(Application.dataPath,"Afrer_Seconds/05.Model/Props/B4/Textures"),"BO_*.png")){string p=P+"Textures/"+Path.GetFileName(file);AssetDatabase.ImportAsset(p,ImportAssetOptions.ForceSynchronousImport);var t=(TextureImporter)AssetImporter.GetAtPath(p);t.maxTextureSize=2048;t.mipmapEnabled=true;t.wrapMode=TextureWrapMode.Clamp;t.filterMode=FilterMode.Trilinear;t.alphaIsTransparency=p.Contains("Floor_C01");t.textureCompression=TextureImporterCompression.CompressedHQ;t.SaveAndReimport();}
  string shared=A+"Environment/Common/Textures/";
  Mat("Coat",new Color(.54f,.56f,.58f),.1f,.4f,shared+"LP_Coating_Base.png");Mat("Floor",new Color(.44f,.45f,.47f),.03f,.28f,shared+"LP_Concrete_Base.png");Mat("Steel",new Color(.36f,.39f,.42f),.72f,.48f,shared+"LP_Stainless_Base.png");
  Mat("Dark",new Color(.028f,.033f,.04f),.1f,.4f);Mat("Rubber",new Color(.02f,.023f,.028f),0,.19f);Mat("Teal",new Color(.22f,.26f,.28f),.35f,.45f);Mat("Fabric",new Color(.14f,.15f,.16f),0,.12f);Mat("Glass",new Color(.40f,.44f,.47f,.12f),.02f,.86f);Mat("Indicator",new Color(.37f,.64f,.51f),0,.7f);Mat("Paper",new Color(.74f,.75f,.72f),0,.15f);Mat("Lamp",new Color(.88f,.9f,.93f),0,.3f);Mat("Warm",new Color(.4f,.34f,.24f),.1f,.4f);Mat("Red",new Color(.45f,.12f,.1f),.05f,.42f);Mat("Hazard",new Color(.63f,.51f,.27f),.05f,.35f);Mat("Mark",new Color(.52f,.55f,.57f),.03f,.27f);Mat("Lens",new Color(.04f,.1f,.13f),.55f,.88f);
  for(int i=1;i<=6;i++)Mat("Display_"+i.ToString("00"),Color.white,0,.25f,P+"Textures/BO_Display_"+i.ToString("00")+".png");Mat("FloorLabel",Color.white,0,.2f,P+"Textures/BO_Floor_C01.png");
  foreach(string folder in new[]{E,P})foreach(var file in Directory.GetFiles(Path.Combine(Application.dataPath,"..",folder),"BO_*.fbx")){
   string path=folder+Path.GetFileName(file);AssetDatabase.ImportAsset(path,ImportAssetOptions.ForceSynchronousImport);var m=(ModelImporter)AssetImporter.GetAtPath(path);m.importAnimation=false;m.importCameras=false;m.importLights=false;m.isReadable=true;m.importNormals=ModelImporterNormals.Import;m.importTangents=ModelImporterTangents.CalculateMikk;m.materialImportMode=ModelImporterMaterialImportMode.ImportStandard;
   foreach(var kv in mats)m.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material),kv.Key),kv.Value);m.SaveAndReimport();
  }
 }
 static void Remap(GameObject g){foreach(var rr in g.GetComponentsInChildren<Renderer>()) {rr.sharedMaterials=rr.sharedMaterials.Select(m=>{if(m==null)return mats["B4O_Coat"];if(mats.TryGetValue(m.name,out var exact))return exact;string suffix=m.name.Substring(m.name.IndexOf('_')+1);return mats.TryGetValue("B4O_"+suffix,out var mat)?mat:mats["B4O_Coat"];}).ToArray();rr.shadowCastingMode=ShadowCastingMode.On;}}
 static GameObject Place(string name,string asset,Transform p,Vector3 pos,float yaw=0,bool meshCollider=false,Vector3 size=default(Vector3),Vector3 center=default(Vector3)){
  var source=AssetDatabase.LoadAssetAtPath<GameObject>(asset);if(!source)throw new Exception("Asset missing "+asset);var g=(GameObject)PrefabUtility.InstantiatePrefab(source,p);g.name=name;g.transform.localPosition=pos;g.transform.localRotation=Quaternion.Euler(0,yaw,0);Remap(g);
  foreach(var c in g.GetComponentsInChildren<Collider>(true))UnityEngine.Object.DestroyImmediate(c);
  foreach(var l in g.GetComponentsInChildren<Light>(true))UnityEngine.Object.DestroyImmediate(l);
  if(meshCollider)foreach(var mf in g.GetComponentsInChildren<MeshFilter>())mf.gameObject.AddComponent<MeshCollider>().sharedMesh=mf.sharedMesh;
  if(size!=Vector3.zero){var c=g.AddComponent<BoxCollider>();c.center=center;c.size=size;}
  placements.Add(new{name,asset,position=new[]{pos.x,pos.y,pos.z},yaw,meshCollider});return g;
 }
 static GameObject Model(string n,string id,Transform p,Vector3 pos,float yaw=0,bool env=false,bool collider=false,Vector3 size=default(Vector3),Vector3 center=default(Vector3))=>Place(n,(env?E:P)+"BO_"+id+".fbx",p,pos,yaw,collider,size,center);
 static void LightAt(string name,Transform parent,Vector3 pos,Quaternion rot,float intensity,float range,float angle=115){var g=Model(name,"SealedTaskLight",parent,pos,env:true);g.transform.localRotation=rot;var lgo=Child("광원",g.transform);lgo.transform.localPosition=new Vector3(0,-.06f,0);lgo.transform.localRotation=Quaternion.Euler(90,0,0);var l=lgo.AddComponent<Light>();l.type=LightType.Spot;l.color=new Color(.92f,.95f,1);l.intensity=intensity;l.range=range;l.spotAngle=angle;l.innerSpotAngle=angle*.69f;l.shadows=LightShadows.Soft;l.shadowBias=.01f;l.shadowNormalBias=.015f;l.shadowNearPlane=.1f;var u=l.GetUniversalAdditionalLightData();u.usePipelineSettings=false;var so=new SerializedObject(u);so.FindProperty("m_AdditionalLightsShadowResolutionTier").intValue=0;so.ApplyModifiedPropertiesWithoutUndo();}
 static void Cable(Transform p,Vector3 a,Vector3 b){var g=GameObject.CreatePrimitive(PrimitiveType.Cylinder);g.name="조명_서스펜션";g.transform.SetParent(p,false);g.transform.localPosition=(a+b)*.5f;g.transform.localRotation=Quaternion.FromToRotation(Vector3.up,b-a);g.transform.localScale=new Vector3(.016f,(b-a).magnitude*.5f,.016f);g.GetComponent<Renderer>().sharedMaterial=mats["B4O_Steel"];UnityEngine.Object.DestroyImmediate(g.GetComponent<Collider>());}
 static void Record(){foreach(var t in root.GetComponentsInChildren<Transform>(true))if(PrefabUtility.IsPartOfPrefabInstance(t)){PrefabUtility.RecordPrefabInstancePropertyModifications(t);PrefabUtility.RecordPrefabInstancePropertyModifications(t.gameObject);foreach(var rr in t.GetComponents<Renderer>())PrefabUtility.RecordPrefabInstancePropertyModifications(rr);}}
 public static object Run(){
  var old=SceneManager.GetActiveScene();if(Application.isPlaying||old.isDirty||!old.path.EndsWith("Level_B5_Circular.unity"))throw new Exception("Saved B5 edit required");if(File.Exists(Path.Combine(Application.dataPath,"..",ScenePath)))throw new Exception("B4 already exists; use a targeted repair, never rebuild over it");
  Materials();
  // Native save-as-copy retains the user's Player/Camera links. All B5 geometry is then removed from the new copy only.
  if(!EditorSceneManager.SaveScene(old,ScenePath,true))throw new Exception("Scene copy failed");var s=EditorSceneManager.OpenScene(ScenePath);
  foreach(var g in s.GetRootGameObjects().Where(g=>!g.name.StartsWith("Player")&&g.name!="Camera").ToArray())UnityEngine.Object.DestroyImmediate(g);
  Lightmapping.Clear();Lightmapping.lightingDataAsset=null;RenderSettings.skybox=null;RenderSettings.sun=null;RenderSettings.fog=false;RenderSettings.ambientMode=AmbientMode.Trilight;RenderSettings.ambientSkyColor=new Color(.30f,.31f,.33f);RenderSettings.ambientEquatorColor=new Color(.22f,.23f,.25f);RenderSettings.ambientGroundColor=new Color(.15f,.16f,.18f);RenderSettings.ambientIntensity=1;RenderSettings.reflectionIntensity=.18f;
  root=new GameObject("B4_중앙관찰동_대표구역_V0.01").transform;root.position=new Vector3(0,-66,0);
  var shell=Child("B4_C01_건축",root).transform;var props=Child("B4_C01_관측설비",root).transform;var doors=Child("B4_C01_출입구",root).transform;var lights=Child("B4_C01_조명",root).transform;var tunnel=Child("B4_T02_접근복도",root).transform;
  foreach(var pair in new[]{new[]{"Shell","돔벽체"},new[]{"Floor","시험바닥"},new[]{"PanelsRibs","벽패널_기둥"},new[]{"DeckStructure","관찰데크"},new[]{"DeckGuards","관찰데크_유리난간"},new[]{"Stairs","관찰데크_양측계단"},new[]{"Services","환기_전력배관"},new[]{"MeasurementFloor","시험영역_측정눈금"}})Model("B4_C01_"+pair[1],"C01_"+pair[0],shell,Vector3.zero,env:true,collider:new[]{"Shell","Floor","DeckStructure","DeckGuards","Stairs"}.Contains(pair[0]));
  foreach(float x in new[]{-3.5f,3.5f}){
   Model("B4_C01_상부관측석_"+(x<0?"01":"02"),"ObservationConsole",props,new Vector3(x,2.5f,8.55f),180,size:new Vector3(2.16f,1.53f,.98f),center:new Vector3(0,.77f,0));
   Place("B4_C01_상부관측의자_"+(x<0?"01":"02"),A+"Props/B5/SF_TaskChair.fbx",props,new Vector3(x,2.5f,7.65f),0,false,new Vector3(.62f,1.12f,.62f),new Vector3(0,.56f,0));
  }
  foreach(var q in new[]{new Vector3(9,0,.4f),new Vector3(4.5f,0,-8.1f)}){
   float yaw=q.x>8?270:210;Model("B4_C01_시험제어석_"+(q.x>8?"01":"02"),"TrialControlConsole",props,q,yaw,size:new Vector3(2.16f,1.53f,.98f),center:new Vector3(0,.77f,0));
   var forward=Quaternion.Euler(0,yaw,0)*Vector3.forward;Place("B4_C01_시험제어의자_"+(q.x>8?"01":"02"),A+"Props/B5/SF_TaskChair.fbx",props,q+forward*.98f,yaw+180,false,new Vector3(.62f,1.12f,.62f),new Vector3(0,.56f,0));
  }
  Model("B4_C01_센서준비대","SensorPreparationBench",props,new Vector3(0,0,-9.65f),0,size:new Vector3(1.95f,1.48f,.83f),center:new Vector3(0,.74f,0));
  Model("B4_C01_동기화계측카트","SynchronizationCart",props,new Vector3(7.1f,0,-7.2f),315,size:new Vector3(.84f,1.03f,.66f),center:new Vector3(0,.515f,0));
  Model("B4_C01_측정기록랙","AcquisitionRack",props,new Vector3(-8.9f,0,-2.9f),72,size:new Vector3(.73f,2.22f,.85f),center:new Vector3(0,1.11f,0));
  Model("B4_C01_센서보관장","SensorStorage",props,new Vector3(-9.15f,0,-.9f),90,size:new Vector3(1.34f,1.95f,.67f),center:new Vector3(0,.975f,0));
  Model("B4_C01_광학보정타깃","CalibrationTarget",props,new Vector3(-4.8f,0,-3.9f),40,size:new Vector3(.65f,1.72f,.51f),center:new Vector3(0,.86f,0));
  for(int i=0;i<4;i++){float a=(22.5f+90*i)*Mathf.Deg2Rad;var pos=new Vector3(Mathf.Cos(a)*10.95f,4.1f,Mathf.Sin(a)*10.95f);var g=Model("B4_C01_광학추적카메라_"+(i+1).ToString("00"),"OpticalTrackingCamera",props,pos);g.transform.localRotation=Quaternion.LookRotation(new Vector3(-pos.x,-1.6f,-pos.z));}
  var plan=JObject.Parse(File.ReadAllText(Repo+"/SourceAssets/B4_Observation/plan.json"));
  foreach(var t in plan["tunnels"]){string id=(string)t["id"];var v=(string)t["a"]=="C01"?t["p"]:t["q"];var dir=new Vector3((float)v[0],0,-(float)v[1]).normalized;float yaw=Quaternion.LookRotation(dir).eulerAngles.y;var pos=dir*11.62f;
   Model("B4_C01_아치문틀_"+id,"VaultPortal",doors,pos,yaw,env:true);
   if(id!="B4-T02")Model("B4_C01_닫힌문_"+id,"ClosedVaultDoor",doors,pos,yaw+180,env:true,collider:true);
  }
  Model("B4_T02_터널벽_바닥","T02_ApproachShell",tunnel,Vector3.zero,env:true,collider:true);
  var tt=plan["tunnels"].Single(t=>(string)t["id"]=="B4-T02");var start=new Vector3((float)tt["p"][0],0,-(float)tt["p"][1]);var end=new Vector3((float)tt["q"][0],0,-(float)tt["q"][1]);var fwd=(end-start).normalized;float tyaw=Quaternion.LookRotation(fwd).eulerAngles.y;
  Model("B4_T02_C02측_닫힌문","ClosedVaultDoor",tunnel,start+fwd*.12f,tyaw,env:true,collider:true);Model("B4_T02_C02측_아치문틀","VaultPortal",tunnel,start+fwd*.12f,tyaw,env:true);
  for(int i=0;i<5;i++){float d=.7f+i*2.25f;Place("B4_T02_아치기둥_"+(i+1).ToString("00"),A+"Environment/Common/CFD_TunnelRib.prefab",tunnel,start+fwd*d,tyaw);if(i<4)LightAt("B4_T02_기둥사이등_"+(i+1).ToString("00"),tunnel,start+fwd*(d+1.125f)+Vector3.up*3.31f,Quaternion.Euler(0,tyaw,0),4.5f,7f);}
  // One destination line: stays entirely in the built corridor, outside the C01 dome.
  var guide=Child("B4_T02_C01_복도안내선",tunnel);var gf=guide.AddComponent<MeshFilter>();var mesh=new Mesh{name="BO_T02_C01_Guidance"};float len=8.8f;mesh.vertices=new[]{new Vector3(-.035f,.008f,0),new Vector3(.035f,.008f,0),new Vector3(-.035f,.008f,len),new Vector3(.035f,.008f,len)};mesh.triangles=new[]{0,2,1,1,2,3};mesh.uv=new[]{Vector2.zero,Vector2.right,Vector2.up,Vector2.one};mesh.RecalculateNormals();AssetDatabase.CreateAsset(mesh,E+"BO_T02_C01_Guidance.asset");gf.sharedMesh=mesh;guide.AddComponent<MeshRenderer>().sharedMaterial=mats["B4O_Mark"];guide.transform.localPosition=start+fwd*.9f+Vector3.Cross(Vector3.up,fwd)*.65f;guide.transform.localRotation=Quaternion.Euler(0,tyaw,0);
  var label=Child("B4_T02_C01_바닥표기",tunnel);var lm=new Mesh{name="BO_FloorLabel"};lm.vertices=new[]{new Vector3(-1f,.012f,-.25f),new Vector3(1f,.012f,-.25f),new Vector3(-1f,.012f,.25f),new Vector3(1f,.012f,.25f)};lm.triangles=new[]{0,2,1,1,2,3};lm.uv=new[]{Vector2.zero,Vector2.right,Vector2.up,Vector2.one};lm.RecalculateNormals();AssetDatabase.CreateAsset(lm,E+"BO_FloorLabel.asset");label.AddComponent<MeshFilter>().sharedMesh=lm;label.AddComponent<MeshRenderer>().sharedMaterial=mats["B4O_FloorLabel"];label.transform.localPosition=start+fwd*6.3f;label.transform.localRotation=Quaternion.Euler(0,tyaw-90,0);
  for(int i=0;i<8;i++){float a=(22.5f+i*45)*Mathf.Deg2Rad;var normal=new Vector3(Mathf.Cos(a)*.55f,Mathf.Sqrt(1-.55f*.55f),Mathf.Sin(a)*.55f);var tangent=new Vector3(-Mathf.Sin(a),0,Mathf.Cos(a));LightAt("B4_C01_천장등_"+(i+1).ToString("00"),lights,normal*11.77f,Quaternion.LookRotation(Vector3.Cross(tangent,normal),normal),13f,20f,120);}
  for(int i=0;i<4;i++){float a=(65+i*16.67f)*Mathf.Deg2Rad;LightAt("B4_C01_데크하부등_"+(i+1).ToString("00"),lights,new Vector3(8.8f*Mathf.Cos(a),2.27f,8.8f*Mathf.Sin(a)),Quaternion.Euler(0,-a*Mathf.Rad2Deg,0),2.4f,5f,110);}
  foreach(float x in new[]{-3.5f,3.5f}){LightAt("B4_C01_관측석작업등_"+(x<0?"01":"02"),lights,new Vector3(x,5.7f,8.4f),Quaternion.identity,3.5f,6,100);foreach(float dx in new[]{-.45f,.45f}){float y=Mathf.Sqrt(144-(x+dx)*(x+dx)-8.4f*8.4f)-.08f;Cable(lights,new Vector3(x+dx,5.73f,8.4f),new Vector3(x+dx,y,8.4f));}}
  var player=s.GetRootGameObjects().Single(g=>g.name.StartsWith("Player"));player.transform.SetPositionAndRotation(root.position+start+fwd*2.4f+Vector3.up*.64f,Quaternion.Euler(0,tyaw,0));
  foreach(var camera in s.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Camera>(true))){camera.useOcclusionCulling=false;camera.farClipPlane=250;}
  Record();Physics.SyncTransforms();EditorSceneManager.MarkSceneDirty(s);EditorSceneManager.SaveScene(s);Selection.activeGameObject=root.gameObject;
  var result=new{scene=s.path,placements=placements.Count,renderers=root.GetComponentsInChildren<Renderer>().Length,colliders=root.GetComponentsInChildren<Collider>().Length,lights=root.GetComponentsInChildren<Light>().Length,materials=mats.Count};File.WriteAllText(Repo+"/Docs/검수/2026-11-08_B4_Observation/build.json",JsonConvert.SerializeObject(new{result,placements},Formatting.Indented));return result;
 }
}
