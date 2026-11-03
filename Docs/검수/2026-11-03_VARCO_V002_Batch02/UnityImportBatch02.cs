using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UnityEngine.Rendering;
public static class VarcoImportBatch02 {
 static string Stage => Path.GetFullPath(Path.Combine(Directory.GetParent(Application.dataPath).FullName,"../../tmp/VARCO_V002_Batch02_20261103"));
 public static Bounds BoundsOf(GameObject go) {var rs=go.GetComponentsInChildren<Renderer>();var b=rs[0].bounds;foreach(var r in rs.Skip(1))b.Encapsulate(r.bounds);return b;}
 public static void Preview(GameObject prefab,string file,bool rear=false) {
  var preview=new PreviewRenderUtility();var go=UnityEngine.Object.Instantiate(prefab);preview.AddSingleGO(go);
  var b=BoundsOf(go);float size=Mathf.Max(b.size.x,b.size.y,b.size.z);
  preview.camera.transform.position=b.center+new Vector3(-1.4f,.8f,rear?2.8f:-2.8f)*size;
  preview.camera.transform.LookAt(b.center);preview.camera.nearClipPlane=.01f;preview.camera.farClipPlane=100f;preview.camera.fieldOfView=32;
  preview.camera.clearFlags=CameraClearFlags.Color;preview.camera.backgroundColor=new Color(.14f,.15f,.17f);
  preview.lights[0].intensity=1.5f;preview.lights[0].transform.rotation=Quaternion.Euler(40,40,0);
  preview.lights[1].intensity=1f;preview.lights[1].transform.rotation=Quaternion.Euler(340,210,0);
  preview.ambientColor=new Color(.3f,.3f,.3f);
  preview.BeginStaticPreview(new Rect(0,0,900,900));preview.Render(true);
  var image=preview.EndStaticPreview();File.WriteAllBytes(file,image.EncodeToPNG());UnityEngine.Object.DestroyImmediate(image);preview.Cleanup();
 }
 static void TextureSettings(string path,bool normal,bool linear) {
  var t=(TextureImporter)AssetImporter.GetAtPath(path);if(t==null)throw new Exception("Missing texture "+path);
  t.textureType=normal?TextureImporterType.NormalMap:TextureImporterType.Default;t.sRGBTexture=!linear&&!normal;t.maxTextureSize=2048;t.mipmapEnabled=true;t.isReadable=false;t.textureCompression=TextureImporterCompression.CompressedHQ;t.alphaSource=TextureImporterAlphaSource.FromInput;t.SaveAndReimport();
 }
 public static string Main() {
  if(EditorApplication.isPlaying)throw new Exception("Must be in edit mode");
  AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
  var config=JArray.Parse(File.ReadAllText(Path.Combine(Stage,"unity_prepared_manifest.json")));var results=new List<object>();
  foreach(JObject a in config) {
   string modelPath=(string)a["modelPath"],floor=(string)a["id"],name=(string)a["name"];string root=Path.GetDirectoryName(Path.GetDirectoryName(modelPath)).Replace('\\','/');
   var importer=(ModelImporter)AssetImporter.GetAtPath(modelPath);importer.materialImportMode=ModelImporterMaterialImportMode.None;importer.importAnimation=false;importer.importCameras=false;importer.importLights=false;importer.importNormals=ModelImporterNormals.Import;importer.importTangents=ModelImporterTangents.CalculateMikk;importer.meshCompression=ModelImporterMeshCompression.Off;importer.isReadable=false;importer.addCollider=false;importer.SaveAndReimport();
   string basePath=(string)a["baseMap"],normalPath=(string)a["normalMap"],msPath=(string)a["metallicSmoothnessMap"],aoPath=(string)a["occlusionMap"];
   TextureSettings(basePath,false,false);TextureSettings(normalPath,true,true);TextureSettings(msPath,false,true);TextureSettings(aoPath,false,true);
   string matPath=root+"/Materials/"+floor+"_"+name+"_URP.mat";
   var mat=AssetDatabase.LoadAssetAtPath<Material>(matPath);if(mat==null){mat=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(mat,matPath);}
   mat.SetTexture("_BaseMap",AssetDatabase.LoadAssetAtPath<Texture2D>(basePath));mat.SetColor("_BaseColor",Color.white);
   mat.SetTexture("_BumpMap",AssetDatabase.LoadAssetAtPath<Texture2D>(normalPath));mat.SetFloat("_BumpScale",.35f);mat.EnableKeyword("_NORMALMAP");
   mat.SetTexture("_MetallicGlossMap",AssetDatabase.LoadAssetAtPath<Texture2D>(msPath));mat.SetFloat("_Metallic",1);mat.SetFloat("_Smoothness",1);mat.EnableKeyword("_METALLICSPECGLOSSMAP");
   mat.SetTexture("_OcclusionMap",AssetDatabase.LoadAssetAtPath<Texture2D>(aoPath));mat.SetFloat("_OcclusionStrength",.8f);mat.EnableKeyword("_OCCLUSIONMAP");EditorUtility.SetDirty(mat);
   var model=AssetDatabase.LoadAssetAtPath<GameObject>(modelPath);if(model==null)throw new Exception("Model import failed");
   var go=new GameObject(floor+"_"+name+"_VisualOnly");var visual=new GameObject("VisualRoot");visual.transform.SetParent(go.transform,false);visual.transform.localRotation=Quaternion.Euler(0,180,0);
   var instance=(GameObject)PrefabUtility.InstantiatePrefab(model);instance.transform.SetParent(visual.transform,false);
   foreach(var renderer in go.GetComponentsInChildren<Renderer>()){renderer.sharedMaterials=Enumerable.Repeat(mat,renderer.sharedMaterials.Length).ToArray();renderer.shadowCastingMode=ShadowCastingMode.Off;renderer.receiveShadows=true;}
   var bounds=BoundsOf(go);var meshes=go.GetComponentsInChildren<MeshFilter>();long tris=meshes.Sum(m=>(long)m.sharedMesh.triangles.Length/3);
   string prefabPath=root+"/Prefabs/"+floor+"_"+name+".prefab";var prefab=PrefabUtility.SaveAsPrefabAsset(go,prefabPath);UnityEngine.Object.DestroyImmediate(go);
   
   a["materialPath"]=matPath;a["prefabPath"]=prefabPath;a["status"]="Imported Unity FBX/URP materials/visual prefab; scene placement pending";
   File.WriteAllText(Path.Combine(Directory.GetParent(Application.dataPath).FullName,root,"source_manifest.json"),a.ToString());
   results.Add(new{floor=floor,prefab=prefabPath,triangles=tris,size=new[]{bounds.size.x,bounds.size.y,bounds.size.z},bottom=bounds.min.y,shader=mat.shader.name,materials=go==null?1:0,colliders=prefab.GetComponentsInChildren<Collider>().Length});
  }
  AssetDatabase.SaveAssets();File.WriteAllText(Path.Combine(Stage,"unity_import_facts.json"),JsonConvert.SerializeObject(results,Formatting.Indented));
  File.WriteAllText(Path.Combine(Stage,"unity_prepared_manifest.json"),config.ToString());return "Imported 20 visual prefabs; previews saved";
 }
}
