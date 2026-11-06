foreach(string name in new[]{"S1_FloorFinish","S1_SpecimenPlate"})UnityEditor.AssetDatabase.ImportAsset("Assets/Afrer_Seconds/05.Model/Environment/B5/"+name+".fbx",UnityEditor.ImportAssetOptions.ForceSynchronousImport|UnityEditor.ImportAssetOptions.ForceUpdate);
return "refreshed";
