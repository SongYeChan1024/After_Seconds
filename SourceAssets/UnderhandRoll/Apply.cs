if(Application.isPlaying)throw new System.Exception("Edit mode required");
var settings=AssetDatabase.LoadAssetAtPath<PlayerThrowSettings>("Assets/Afrer_Seconds/06.Data/PlayerThrowSettings.asset");
var serialized=new SerializedObject(settings);Undo.RecordObject(settings,"Tune underhand roll");
const string materialPath="Assets/Afrer_Seconds/06.Data/UnderhandRoll.physicMaterial";
var material=AssetDatabase.LoadAssetAtPath<PhysicsMaterial>(materialPath);
if(material==null){material=new PhysicsMaterial("UnderhandRoll");AssetDatabase.CreateAsset(material,materialPath);}
material.dynamicFriction=.2f;material.staticFriction=.2f;material.frictionCombine=PhysicsMaterialCombine.Minimum;material.bounciness=0;material.bounceCombine=PhysicsMaterialCombine.Minimum;EditorUtility.SetDirty(material);
serialized.FindProperty("underhandPhysicsMaterial").objectReferenceValue=material;
serialized.FindProperty("underhandSpeed").floatValue=4.5f;
serialized.FindProperty("underhandAngle").floatValue=-12f;
serialized.FindProperty("underhandMaxElevation").floatValue=-5f;
serialized.FindProperty("underhandDamping").floatValue=.8f;
serialized.ApplyModifiedProperties();EditorUtility.SetDirty(settings);
var hands=AssetDatabase.LoadAssetAtPath<PlayerHandSettings>("Assets/Afrer_Seconds/06.Data/PlayerHandSettings.asset");
Undo.RecordObject(hands,"Tune underhand follow through");hands.underhandFollowThrough=new Vector3(-.03f,-.06f,.18f);EditorUtility.SetDirty(hands);
AssetDatabase.SaveAssets();return new{speed=settings.UnderhandSpeed,angle=settings.UnderhandAngle,damping=settings.UnderhandDamping,hand=hands.underhandFollowThrough};
