using System;using System.IO;using System.Linq;using UnityEngine;using UnityEngine.SceneManagement;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.Rendering;
public static class PolishSector {
 const string E="Assets/Afrer_Seconds/05.Model/Environment/B5/";
 public static object Run(){var s=SceneManager.GetActiveScene();if(s.isDirty||Application.isPlaying)throw new Exception("Saved edit scene required");var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular")).transform;var g=root.Find("Sector01_CompletedArt");
 foreach(var l in g.GetComponentsInChildren<Light>()){if(l.name=="Wall_Worklight"){l.intensity=20;l.renderMode=LightRenderMode.ForcePixel;}if(l.name=="Pod_Interior_Task"){l.intensity=16;l.range=12;l.renderMode=LightRenderMode.ForcePixel;}if(l.name=="Living_Indirect"){l.intensity=1.5f;l.range=6;}}
 foreach(string name in new[]{"Shell","Coat"}){var m=AssetDatabase.LoadAssetAtPath<Material>(E+"Materials/S1_"+name+".mat");m.SetColor("_BaseColor",new Color(.88f,.93f,.97f));EditorUtility.SetDirty(m);}
 var lamp=AssetDatabase.LoadAssetAtPath<Material>(E+"Materials/S1_Lamp.mat");lamp.SetColor("_EmissionColor",new Color(.65f,.80f,.9f)*1.4f);EditorUtility.SetDirty(lamp);
 var unused=g.Cast<Transform>().FirstOrDefault(t=>t.name.StartsWith("S1_ServiceRiser")&&t.localPosition.z<0);if(unused)UnityEngine.Object.DestroyImmediate(unused.gameObject);
 AssetDatabase.SaveAssets();EditorSceneManager.SaveScene(s);return "C01 light balance and unused disconnected conduit corrected";}
}
