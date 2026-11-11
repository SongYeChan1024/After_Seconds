from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
s=(R/'SourceAssets/ZFightingReview/Export.cs').read_text(encoding='utf8').replace('class ZFExport','class B1GeometryExport').replace('if(!File.Exists(file)||(mesh.name.StartsWith("ZF_")&&!written.Contains(key)))','if(!File.Exists(file)||AssetDatabase.GetAssetPath(mesh).Contains("/B1/")||(mesh.name.StartsWith("ZF_")&&!written.Contains(key)))')
(H/'GeometryExport.cs').write_text(s,encoding='utf8')
s=(H/'Finish.cs').read_text(encoding='utf8').replace('var parent=new GameObject("B1_Reflections");','var parent=GameObject.Find("B1_Reflections")??new GameObject("B1_Reflections");').replace('var g=new GameObject("Reflection_"+id);','var existing=parent.transform.Find("Reflection_"+id);var g=existing?existing.gameObject:new GameObject("Reflection_"+id);').replace('var p=g.AddComponent<ReflectionProbe>();','var p=g.GetComponent<ReflectionProbe>()??g.AddComponent<ReflectionProbe>();')
s=s.replace('public static object Status(){','public static object Rebake(){Check();StaticOcclusionCulling.GenerateInBackground();return new{running=StaticOcclusionCulling.isRunning};}public static object Status(){')
(H/'Finish.cs').write_text(s,encoding='utf8')
