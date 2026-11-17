if(Application.isPlaying)throw new System.Exception("Edit mode required");
var settings=AssetDatabase.LoadAssetAtPath<PlayerThrowSettings>("Assets/Afrer_Seconds/06.Data/PlayerThrowSettings.asset");
var so=new SerializedObject(settings);
so.FindProperty("underhandSpeed").floatValue=6f;so.FindProperty("underhandAngle").floatValue=35f;
so.FindProperty("underhandHandOffset").vector3Value=new Vector3(.26f,-.34f,.68f);
so.ApplyModifiedPropertiesWithoutUndo();EditorUtility.SetDirty(settings);
var hands=AssetDatabase.LoadAssetAtPath<PlayerHandSettings>("Assets/Afrer_Seconds/06.Data/PlayerHandSettings.asset");
hands.underhandZoomLift=.08f;EditorUtility.SetDirty(hands);AssetDatabase.SaveAssets();
return new{settings.OverhandSpeed,settings.OverhandAngle,settings.UnderhandSpeed,settings.UnderhandAngle,hand=settings.UnderhandHandOffset.ToString()};
