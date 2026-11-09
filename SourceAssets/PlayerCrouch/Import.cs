using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
public static class AS_CrouchImport
{
    const string Folder="Assets/Afrer_Seconds/07.Animator/Player/Clips/Crouch";
    public static object Run()
    {
        AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        var rows=new System.Collections.Generic.List<object>();
        foreach(var name in new[]{"Idle","Forward","Back","Left","Right","Stand"})
        {
            string path=Folder+"/Player_Crouch_"+name+".fbx";
            var mi=(ModelImporter)AssetImporter.GetAtPath(path);
            mi.animationType=ModelImporterAnimationType.Human;
            mi.avatarSetup=ModelImporterAvatarSetup.CreateFromThisModel;
            mi.importAnimation=true;
            mi.materialImportMode=ModelImporterMaterialImportMode.None;
            mi.animationCompression=ModelImporterAnimationCompression.Off;
            mi.SaveAndReimport();
            var defs=mi.defaultClipAnimations;
            if(defs.Length!=1) throw new Exception("Unexpected takes: "+path);
            var d=defs[0];d.name="Player_Crouch_"+name;
            d.loopTime=name!="Stand";d.loopPose=name!="Stand";
            d.lockRootRotation=true;d.keepOriginalOrientation=true;
            d.lockRootPositionXZ=true;d.keepOriginalPositionXZ=true;
            d.lockRootHeightY=true;d.keepOriginalPositionY=false;d.heightFromFeet=true;
            mi.clipAnimations=new[]{d};mi.SaveAndReimport();
            var avatar=AssetDatabase.LoadAllAssetsAtPath(path).OfType<Avatar>().Single();
            var clip=AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>().Single(c=>!c.name.StartsWith("__preview__"));
            if(!avatar.isHuman||!avatar.isValid||!clip.isHumanMotion) throw new Exception("Invalid Humanoid "+name);
            rows.Add(new{name,avatar=avatar.name,avatar.isHuman,avatar.isValid,clip.isHumanMotion,clip.length,clip.frameRate,d.firstFrame,d.lastFrame,meshCount=AssetDatabase.LoadAllAssetsAtPath(path).OfType<Mesh>().Count()});
        }
        return rows;
    }
}
