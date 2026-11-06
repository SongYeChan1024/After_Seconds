using System;using System.Linq;using UnityEngine;using UnityEngine.SceneManagement;using UnityEditor;using UnityEditor.SceneManagement;
public static class DeskSector {
 public static object Run(){var s=SceneManager.GetActiveScene();if(s.isDirty||Application.isPlaying)throw new Exception("Saved edit scene required");var r=s.GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular")).transform;var g=r.Find("Sector01_CompletedArt");r.Find("Existing_Props_FirstPass/B5-03_P03").gameObject.SetActive(false);var old=g.Find("S1_LivingDesk");if(old)UnityEngine.Object.DestroyImmediate(old.gameObject);
 var go=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Afrer_Seconds/05.Model/Props/B5/S1_LivingDesk.prefab"),g);go.name="S1_LivingDesk";go.transform.localPosition=new Vector3(2.55f,0,-.75f);go.transform.localRotation=Quaternion.Euler(0,270,0);
 var kit=g.Cast<Transform>().Single(t=>t.name.StartsWith("S1_TabletopKit"));kit.localPosition=new Vector3(2.55f,.769f,-.75f);kit.localRotation=Quaternion.Euler(0,270,0);
 var plate=g.Cast<Transform>().Single(t=>t.name.StartsWith("S1_SpecimenPlate"));plate.localPosition=new Vector3(.92f,.80f,-3.94f);
 Physics.SyncTransforms();EditorSceneManager.SaveScene(s);return "Desk stool now faces the living area; fitted mesh collision replaces oversized old box";}
}
