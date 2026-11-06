using System;using System.IO;using System.Linq;using System.Collections.Generic;using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.SceneManagement;using UnityEngine.Rendering;using Newtonsoft.Json;
public static class RefineSector{
 const string A="Assets/Afrer_Seconds/",E=A+"05.Model/Environment/B5/",P=A+"05.Model/Props/B5/";
 static string R=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 static GameObject Find(Transform g,string prefix)=>g.Cast<Transform>().Single(t=>t.name.StartsWith(prefix)).gameObject;
 public static object Run(){var s=SceneManager.GetActiveScene();if(s.isDirty||EditorApplication.isPlaying)throw new Exception("Saved edit scene required");var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular")).transform;var group=root.Find("Sector01_CompletedArt");
 // Continuous spherical normals and UVs only on this dome's interior.
 var mf=root.GetComponentsInChildren<MeshFilter>().Single(f=>f.name.StartsWith("CF_B5_C01_Dome"));string meshpath=E+"S1_C01_InteriorNormals.asset";var existing=AssetDatabase.LoadAssetAtPath<Mesh>(meshpath);var src=UnityEngine.Object.Instantiate(mf.sharedMesh);src.name="S1_C01_InteriorNormals";var verts=src.vertices;var nn=src.normals;var uv=src.uv;
 for(int i=0;i<verts.Length;i++){var world=mf.transform.TransformPoint(verts[i]);var d=world-new Vector3(-15,-82,-10);var normal=mf.transform.TransformDirection(nn[i]);float rad=d.magnitude;if(rad>9.70f&&rad<10.3f&&world.y>-81.98f&&Mathf.Abs(Vector3.Dot(normal.normalized,d.normalized))>.72f){float sign=Vector3.Dot(normal,d)>0?1:-1;nn[i]=mf.transform.InverseTransformDirection(d.normalized*sign);uv[i]=new Vector2((Mathf.Atan2(d.z,d.x)/(2*Mathf.PI)+.5f)*8,Mathf.Asin(Mathf.Clamp01(d.y/rad))/Mathf.PI*8);}}
 src.normals=nn;src.uv=uv;src.RecalculateTangents();if(existing){EditorUtility.CopySerialized(src,existing);UnityEngine.Object.DestroyImmediate(src);}else{AssetDatabase.CreateAsset(src,meshpath);existing=src;}mf.sharedMesh=existing;PrefabUtility.RecordPrefabInstancePropertyModifications(mf);
 // Light sources emit into the room; their own metal housings do not cast giant point-source shadows.
 foreach(var t in group.Cast<Transform>().Where(t=>t.name.StartsWith("S1_WallTaskLight"))){foreach(var r in t.GetComponentsInChildren<Renderer>())r.shadowCastingMode=ShadowCastingMode.Off;var l=t.GetComponentInChildren<Light>();l.type=LightType.Spot;l.transform.localRotation=Quaternion.LookRotation(new Vector3(0,-.72f,.70f));l.spotAngle=118;l.innerSpotAngle=70;l.intensity=6.0f;l.range=11;l.shadows=LightShadows.Soft;l.shadowNormalBias=.08f;}
 var podlight=group.Find("Pod_Interior_Task").GetComponent<Light>();podlight.intensity=3.5f;podlight.range=8.5f;
 var fill=group.Find("Living_Indirect").GetComponent<Light>();fill.intensity=.85f;fill.range=5.5f;
 var glass=AssetDatabase.LoadAssetAtPath<Material>(E+"Materials/S1_PodGlass.mat");glass.SetFloat("_SpecularHighlights",0);glass.EnableKeyword("_SPECULARHIGHLIGHTS_OFF");glass.SetColor("_BaseColor",new Color(.85f,.91f,.95f,.055f));EditorUtility.SetDirty(glass);
 // Staff-side clock and record are physically backed by a bolted stand.
 foreach(string name in new[]{"S1_ServiceBackboard","S1_HygieneShelf"}){
  var old=group.Find(name+"_Support");if(old)UnityEngine.Object.DestroyImmediate(old.gameObject);var a=AssetDatabase.LoadAssetAtPath<GameObject>((name.Contains("Hygiene")?P:E)+name+".prefab");var g=(GameObject)PrefabUtility.InstantiatePrefab(a,group);g.name=name+"_Support";g.transform.localPosition=name.Contains("Hygiene")?new Vector3(.36f,0,2.6f):new Vector3(0,0,-8.76f);
 }
 Find(group,"S1_Clock").transform.localPosition=new Vector3(-.02f,1.72f,-8.70f);Find(group,"S1_RecordBoard").transform.localPosition=new Vector3(-.23f,1.25f,-8.70f);
 Find(group,"S1_HygieneKit").transform.localPosition=new Vector3(.36f,.962f,2.6f);
 // Fit tabletop accessories to the real reused desk top instead of an assumed height.
 var desk=root.Find("Existing_Props_FirstPass/B5-03_P03");var surface=desk.GetComponentsInChildren<Renderer>().Single(r=>r.name=="LivingDesk_Body");var kit=Find(group,"S1_TabletopKit");var wp=surface.bounds.center;wp.y=surface.bounds.max.y+.002f;kit.transform.position=wp;
 // Place the panel on the actual screen face and the camera at the top of its stand.
 var call=Find(group,"S1_CallPanel");call.transform.localPosition=new Vector3(-.68f,.88f,1.438f);call.transform.localRotation=Quaternion.Euler(0,180,0);
 var camera=group.Find("S1_CCTV_Static");var pole=group.Cast<Transform>().Where(t=>t.name.StartsWith("S1_ServiceRiser")).Last();camera.localPosition=pole.localPosition+pole.localRotation*new Vector3(.52f,2.86f,0);
 Physics.SyncTransforms();AssetDatabase.SaveAssets();EditorSceneManager.SaveScene(s);return new{domeVertices=verts.Length,lights=4,physicalSupports=2,deskTop=surface.bounds.max.y};}
}
