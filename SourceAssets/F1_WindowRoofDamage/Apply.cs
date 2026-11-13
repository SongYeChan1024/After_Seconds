// 송예찬 V0.01. Scoped native import, preserving all existing object transforms/GUIDs.
using System;using System.IO;using System.Linq;using System.Collections.Generic;using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.SceneManagement;using Newtonsoft.Json;using Newtonsoft.Json.Linq;
public static class F1WindowRoofApply {
 const string E="Assets/Afrer_Seconds/05.Model/Environment/1F/";
 static string Root=>Path.GetFullPath(Application.dataPath+"/../../..");
 static void Check(){var s=SceneManager.GetActiveScene();if(s.isDirty||Application.isPlaying||!s.path.EndsWith("Level_1F_Factory.unity"))throw new Exception("Saved 1F edit required");}
 public static object Run()=>RunModels(0);
 public static object Concrete()=>RunModels(1);
 public static object Metal()=>RunModels(2);
 static object RunModels(int scope){Check();bool concreteOnly=scope==1;
 void Mat(string n,Color c,float metal,float smooth){string p=E+"Materials/AE_M_"+n+".mat";var mat=AssetDatabase.LoadAssetAtPath<Material>(p);if(!mat){mat=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(mat,p);}mat.SetColor("_BaseColor",c);mat.SetFloat("_Metallic",metal);mat.SetFloat("_Smoothness",smooth);mat.SetTexture("_BaseMap",AssetDatabase.LoadAssetAtPath<Texture2D>(E+"Textures/AE_Grain_Albedo.png"));mat.SetTextureScale("_BaseMap",new Vector2(14,14));EditorUtility.SetDirty(mat);}
 Mat("RoofFracture",new Color(.39f,.385f,.34f),0,.08f);Mat("RoofAggregate",new Color(.52f,.50f,.43f),0,.13f);Mat("RoofRawSteel",new Color(.23f,.25f,.24f),.72f,.32f);Mat("RoofEdgeRust",new Color(.20f,.095f,.038f),.04f,.10f);
 var mats=Directory.GetFiles(E+"Materials","AE_M_*.mat").Select(p=>AssetDatabase.LoadAssetAtPath<Material>(p.Replace('\\','/'))).ToDictionary(m=>m.name);
 var models=JArray.Parse(File.ReadAllText(Root+"/SourceAssets/F1_WindowRoofDamage/models.json"));var results=new List<object>();
 foreach(var q in models){string name=(string)q["name"],path=E+name+".fbx";if(concreteOnly&&name!="AE_C03_Roof"&&name!="AE_C04_Roof")continue;if(scope==2&&(!name.EndsWith("_Roof")||name=="AE_C03_Roof"||name=="AE_C04_Roof"))continue;string guid=AssetDatabase.AssetPathToGUID(path);if(string.IsNullOrEmpty(guid))throw new Exception("Expected existing asset "+path);File.Copy(Path.Combine(Path.GetTempPath(),"AfterSeconds_WindowRoofDamage_20261113/candidate/"+name+".fbx"),path,true);AssetDatabase.ImportAsset(path,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);
 var imp=(ModelImporter)AssetImporter.GetAtPath(path);foreach(var n in q["materials"].Values<string>())imp.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material),n),mats[n]);imp.SaveAndReimport();if(guid!=AssetDatabase.AssetPathToGUID(path))throw new Exception("GUID changed");
 var proto=AssetDatabase.LoadAssetAtPath<GameObject>(path);var mesh=proto.GetComponentInChildren<MeshFilter>().sharedMesh;var materials=proto.GetComponentInChildren<Renderer>().sharedMaterials;var go=GameObject.Find(name);if(!go)throw new Exception("Missing "+name);
 foreach(var f in go.GetComponentsInChildren<MeshFilter>(true)){f.sharedMesh=mesh;f.GetComponent<Renderer>().sharedMaterials=materials;var col=f.GetComponent<MeshCollider>();if(col){col.sharedMesh=null;col.sharedMesh=mesh;}foreach(var c in f.GetComponents<Component>())if(c&&PrefabUtility.IsPartOfPrefabInstance(c))PrefabUtility.RecordPrefabInstancePropertyModifications(c);}
 results.Add(new{name,guid,vertices=mesh.vertexCount,materials=materials.Select(m=>m.name).ToArray()});}
 Physics.SyncTransforms();AssetDatabase.SaveAssets();EditorSceneManager.MarkSceneDirty(SceneManager.GetActiveScene());EditorSceneManager.SaveScene(SceneManager.GetActiveScene());File.WriteAllText(Root+"/Docs/Review/2026-11-13_1F_WindowRoofDamage/"+(concreteOnly?"concrete_finish.json":scope==2?"metal_finish.json":"import.json"),JsonConvert.SerializeObject(results,Formatting.Indented));return new{imported=results.Count,saved=true};}
}
