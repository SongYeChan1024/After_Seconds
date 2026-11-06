using System;using System.IO;using System.Linq;using UnityEngine;using UnityEngine.SceneManagement;using UnityEditor;using UnityEditor.SceneManagement;
public static class FinishSector {
 public static object Run(){var s=SceneManager.GetActiveScene();if(Application.isPlaying||s.isDirty)throw new Exception("Saved edit scene required");var r=s.GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular")).transform;var g=r.Find("Sector01_CompletedArt");var mf=r.GetComponentsInChildren<MeshFilter>().Single(f=>f.name.StartsWith("CF_B5_C01_Dome"));var m=mf.sharedMesh;var v=m.vertices;var n=m.normals;int count=0;
 // On the concave shell face, boolean/bevel vertices at the two portal crowns
 // must follow the same spherical shading as adjacent shell vertices.
 for(int i=0;i<v.Length;i++){var d=mf.transform.TransformPoint(v[i])-new Vector3(-15,-82,-10);float rad=d.magnitude;if(rad>9.88f&&rad<10.10f&&d.y>.2f){n[i]=mf.transform.InverseTransformDirection(-d.normalized);count++;}}
 m.normals=n;m.RecalculateTangents();EditorUtility.SetDirty(m);
 var plate=g.Cast<Transform>().Single(t=>t.name.StartsWith("S1_SpecimenPlate"));plate.localPosition=new Vector3(.64f,.84f,-4.01f);plate.localRotation=Quaternion.Euler(0,180,0);
 // The plate is fastened to the preserved feeding-hatch backing, not floating on glass.
 var folder=Path.GetFullPath(Path.Combine(Application.dataPath,"../../../Docs/검수/2026-11-06_B5_Sector01/"));foreach(string suffix in new[]{"Inside","Outside"}){string p="Assets/Temp/Sector01_Play_"+suffix+".png";if(File.Exists(p)){File.Copy(p,folder+"S1_Play_"+suffix+".png",true);AssetDatabase.DeleteAsset(p);}}
 AssetDatabase.SaveAssets();EditorSceneManager.SaveScene(s);return new{portalNormalVertices=count};}
}
