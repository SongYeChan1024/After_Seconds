// 송예찬 V0.01. Native material authoring only. No geometry or runtime scripts.
using System;using System.IO;using System.Linq;using System.Collections.Generic;using UnityEngine;using UnityEditor;using UnityEngine.SceneManagement;using Newtonsoft.Json;
public static class F1SurfaceApply {
 const string E="Assets/Afrer_Seconds/05.Model/Environment/1F/";
 static string Root=>Path.GetFullPath(Application.dataPath+"/../../..");
 static string Out=>Root+"/Docs/Review/2026-11-13_1F_SurfaceDetail/";
 static void Check(){var s=SceneManager.GetActiveScene();if(Application.isPlaying||s.isDirty||!s.path.EndsWith("Level_1F_Factory.unity"))throw new Exception("Saved 1F edit required");}
 public static object Run(){Check();File.Copy(Root+"/SourceAssets/F1_SurfaceDetail/AEWeathering.hlsl",E+"AEWeathering.hlsl",true);
 string shaderPath=E+"AEWeatheredLit.shader",input=E+"AEWeatheredInput.hlsl";string shaderText=File.ReadAllText(shaderPath);if(!shaderText.Contains("_AE_WearAmount")){shaderText=shaderText.Replace("_AE_Mode(\"Weather: Plaster 1, Steel 2, Concrete 3\", Float) = 1","_AE_Mode(\"Surface: Cladding 1, Metal 2, Concrete 3, Wood 4, Rubber 5, Fabric 6\", Float) = 1\n        _AE_WearAmount(\"Small chip coverage\", Range(0,1)) = 0.3\n        _AE_Seed(\"Surface variation\", Float) = 1");File.WriteAllText(shaderPath,shaderText);File.WriteAllText(input,File.ReadAllText(input).Replace("float _AE_MacroScale;","float _AE_MacroScale;\nfloat _AE_WearAmount;\nfloat _AE_Seed;"));}
 AssetDatabase.ImportAsset(shaderPath,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);AssetDatabase.ImportAsset(E+"AEWeathering.hlsl",ImportAssetOptions.ForceSynchronousImport);var shader=AssetDatabase.LoadAssetAtPath<Shader>(shaderPath);var changed=new List<string>();
 void Set(string name,int mode,Color color,float wear,float frequency,float metal,float smooth,float seed){var m=AssetDatabase.LoadAssetAtPath<Material>(E+"Materials/AE_M_"+name+".mat");if(!m)throw new Exception(name);m.shader=shader;m.SetFloat("_AE_Mode",mode);m.SetFloat("_AE_WearAmount",wear);m.SetFloat("_AE_MacroScale",frequency);m.SetFloat("_AE_Seed",seed);m.SetColor("_BaseColor",color);m.SetFloat("_Metallic",metal);m.SetFloat("_Smoothness",smooth);m.SetTexture("_BaseMap",AssetDatabase.LoadAssetAtPath<Texture2D>(E+"Textures/AE_Grain_Albedo.png"));m.SetTexture("_BumpMap",AssetDatabase.LoadAssetAtPath<Texture2D>(E+"Textures/AE_Grain_Normal.png"));m.SetFloat("_BumpScale",.22f);m.SetTextureScale("_BaseMap",Vector2.one*3);m.SetTexture("_MetallicGlossMap",null);m.DisableKeyword("_METALLICSPECGLOSSMAP");m.EnableKeyword("_NORMALMAP");EditorUtility.SetDirty(m);changed.Add(m.name);}
 Set("Plaster",1,new Color(.56f,.575f,.53f),.32f,1,.08f,.25f,1);
 Set("Corrosion",2,new Color(.38f,.41f,.385f),.42f,1.1f,.46f,.28f,2);
 Set("Coat",2,new Color(.56f,.56f,.49f),.25f,1.25f,.08f,.29f,3);
 Set("Green",2,new Color(.34f,.405f,.35f),.31f,1.25f,.09f,.27f,4);
 Set("Steel",2,new Color(.40f,.43f,.415f),.23f,1.2f,.72f,.34f,5);
 Set("Rust",2,new Color(.32f,.28f,.22f),.48f,1.4f,.38f,.23f,6);
 Set("Red",2,new Color(.45f,.26f,.21f),.32f,1.3f,.08f,.25f,7);
 Set("Hazard",2,new Color(.56f,.47f,.26f),.28f,1.1f,.06f,.24f,8);
 Set("Concrete",3,new Color(.43f,.445f,.405f),.15f,1,0,.15f,9);
 Set("Floor",3,new Color(.43f,.445f,.405f),.15f,1,0,.15f,9);
 Set("Wood",4,new Color(.37f,.30f,.22f),.3f,1,0,.12f,10);
 Set("Rubber",5,new Color(.15f,.16f,.145f),.2f,1,0,.23f,11);
 Set("Fabric",6,new Color(.33f,.315f,.27f),.2f,1,0,.08f,12);
 var rubble=AssetDatabase.LoadAssetAtPath<Material>(E+"Materials/AE_M_Brick.mat");rubble.SetColor("_BaseColor",new Color(.38f,.37f,.33f));EditorUtility.SetDirty(rubble);changed.Add(rubble.name);
 AssetDatabase.SaveAssets();var result=new{materials=changed,geometryModified=false,runtimeScriptsAdded=0};File.WriteAllText(Out+"apply.json",JsonConvert.SerializeObject(result,Formatting.Indented));return result;}
 public static object Validate(){var shader=AssetDatabase.LoadAssetAtPath<Shader>(E+"AEWeatheredLit.shader");var messages=ShaderUtil.GetShaderMessages(shader).Select(m=>new{m.message,severity=m.severity.ToString(),m.file,m.line}).ToArray();var renderers=GameObject.Find("1F_AbandonedFactory").GetComponentsInChildren<Renderer>(true);var brick=renderers.SelectMany(r=>r.sharedMaterials.Where(m=>m&&m.shader==shader).Select(m=>new{renderer=r.name,material=m.name,baseMap=m.GetTexture("_BaseMap")?.name,normal=m.GetTexture("_BumpMap")?.name})).Where(q=>(q.baseMap??"").Contains("Brick")||(q.normal??"").Contains("Brick")).ToArray();var result=new{shader=shader.name,supported=shader.isSupported,messages,errors=messages.Count(m=>m.severity=="Error"),brickTextureBindings=brick,affectedRenderers=renderers.Count(r=>r.sharedMaterials.Any(m=>m&&m.shader==shader))};File.WriteAllText(Out+"shader_validation.json",JsonConvert.SerializeObject(result,Formatting.Indented));return result;}
}
