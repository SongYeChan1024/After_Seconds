#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using Object = UnityEngine.Object;

public static class PickupArtImport
{
    private static void Require(bool value, string message)
    {
        if (!value) throw new InvalidOperationException(message);
    }

    private static Texture2D ConfigureTexture(string path, bool normal, bool packed = false)
    {
        var importer = AssetImporter.GetAtPath(path) as TextureImporter;
        Require(importer != null, "Texture import failed: " + path);
        importer.textureType = normal ? TextureImporterType.NormalMap : TextureImporterType.Default;
        importer.sRGBTexture = !normal && !packed;
        if (packed)
        {
            importer.alphaSource = TextureImporterAlphaSource.FromInput;
            importer.alphaIsTransparency = false;
        }
        importer.maxTextureSize = 1024;
        importer.mipmapEnabled = true;
        importer.SaveAndReimport();
        var image = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        Require(image != null && image.width > 0, path);
        return image;
    }

    private static Material ConfigureMaterial(JToken item, Shader shader)
    {
        string path = (string)item["material"];
        var material = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (material == null)
        {
            material = new Material(shader);
            AssetDatabase.CreateAsset(material, path);
        }
        material.shader = shader;
        material.SetTexture("_BaseMap", ConfigureTexture((string)item["albedo"], false));
        if ((string)item["normal"] != null)
        {
            material.SetTexture("_BumpMap", ConfigureTexture((string)item["normal"], true));
            material.EnableKeyword("_NORMALMAP");
        }
        else
        {
            material.SetTexture("_BumpMap", null);
            material.DisableKeyword("_NORMALMAP");
        }
        material.SetColor("_BaseColor", Color.white);
        material.SetFloat("_Metallic", (float)item["metallic"]);
        material.SetFloat("_Smoothness", 1f - (float)item["roughness"]);
        string packed = (string)item["metallicGloss"];
        if (packed != null)
        {
            material.SetTexture("_MetallicGlossMap", ConfigureTexture(packed, false, true));
            material.SetFloat("_Smoothness", 1f);
            material.EnableKeyword("_METALLICSPECGLOSSMAP");
        }
        else
        {
            material.SetTexture("_MetallicGlossMap", null);
            material.DisableKeyword("_METALLICSPECGLOSSMAP");
        }
        material.SetFloat("_Cull", (bool)item["doubleSided"] ? (float)CullMode.Off : (float)CullMode.Back);
        EditorUtility.SetDirty(material);
        return material;
    }

    private static JObject Import(JToken item, Shader shader, UnityEngine.SceneManagement.Scene preview)
    {
        string id = (string)item["id"];
        string path = (string)item["model"];
        var mat = ConfigureMaterial(item, shader);
        var importer = AssetImporter.GetAtPath(path) as ModelImporter;
        Require(importer != null, "Missing FBX " + path);
        importer.importAnimation = false;
        importer.animationType = ModelImporterAnimationType.None;
        importer.importCameras = false;
        importer.importLights = false;
        importer.addCollider = false;
        importer.materialImportMode = ModelImporterMaterialImportMode.ImportStandard;
        importer.materialLocation = ModelImporterMaterialLocation.InPrefab;
        importer.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material), "Pickup_" + id), mat);
        importer.SaveAndReimport();
        var model = AssetDatabase.LoadAssetAtPath<GameObject>(path);
        Require(model != null, path);
        var instance = (GameObject)PrefabUtility.InstantiatePrefab(model, preview);
        try
        {
            var renderers = instance.GetComponentsInChildren<MeshRenderer>(true);
            Require(renderers.Length > 0 && renderers.All(r => r.sharedMaterials.Length > 0 && r.sharedMaterials.All(m => m == mat)), "External material binding " + id);
            Require(mat.GetTexture("_BaseMap") != null && ((string)item["normal"] != null) == (mat.GetTexture("_BumpMap") != null), "Texture binding " + id);
            string packed = (string)item["metallicGloss"];
            Require((packed != null) == mat.IsKeywordEnabled("_METALLICSPECGLOSSMAP"), "Metallic keyword " + id);
            if (packed != null)
                Require(AssetDatabase.GetAssetPath(mat.GetTexture("_MetallicGlossMap")) == packed, "Packed map binding " + id);
            float expectedSmoothness = packed == null ? 1f - (float)item["roughness"] : 1f;
            Require(Mathf.Approximately(mat.GetFloat("_Smoothness"), expectedSmoothness) &&
                    Mathf.Approximately(mat.GetFloat("_Metallic"), (float)item["metallic"]), "Surface parameters " + id);
            var bounds = renderers.First().bounds;
            foreach (var r in renderers.Skip(1)) bounds.Encapsulate(r.bounds);
            var size = bounds.size;
            float longest = Mathf.Max(size.x, Mathf.Max(size.y, size.z));
            float expected = (float)item["longestMeters"];
            Require(Mathf.Abs(longest - expected) <= expected * 0.025f, $"Metric bounds {id}: {longest} vs {expected}");
            Require(Mathf.Abs(bounds.min.y) <= expected * .025f, $"Bottom pivot {id}: {bounds.min.y}");
            long triangles = 0;
            foreach (var f in instance.GetComponentsInChildren<MeshFilter>(true))
            {
                var mesh = f.sharedMesh;
                Require(mesh != null && mesh.HasVertexAttribute(VertexAttribute.TexCoord0), "UV0 missing " + id);
                for (int sub = 0; sub < mesh.subMeshCount; ++sub)
                {
                    Require(mesh.GetTopology(sub) == MeshTopology.Triangles, "Non-triangle mesh " + id);
                    triangles += mesh.GetIndexCount(sub) / 3;
                }
            }
            Require(triangles == (long)item["triangles"], $"Triangle count {id}: {triangles}");
            return new JObject { ["id"] = id, ["triangles"] = triangles, ["longestMeters"] = longest, ["assetGuid"] = AssetDatabase.AssetPathToGUID(path), ["materialGuid"] = AssetDatabase.AssetPathToGUID((string)item["material"]) };
        }
        finally { Object.DestroyImmediate(instance); }
    }

    public static void Run()
    {
        string plan = Environment.GetEnvironmentVariable("PICKUP_ART_PLAN");
        string resultPath = Environment.GetEnvironmentVariable("PICKUP_ART_RESULT");
        var items = JArray.Parse(File.ReadAllText(plan));
        var report = new JArray();
        var problems = new List<string>();
        var shader = Shader.Find("Universal Render Pipeline/Lit");
        Require(shader != null, "Missing URP/Lit");
        AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        var preview = EditorSceneManager.NewPreviewScene();
        try
        {
            foreach (var item in items)
            {
                try { report.Add(Import(item, shader, preview)); }
                catch (Exception error) { problems.Add(item["id"] + ": " + error.Message); }
            }
            AssetDatabase.SaveAssets();
        }
        finally { EditorSceneManager.ClosePreviewScene(preview); }
        File.WriteAllText(resultPath, new JObject { ["unity"] = Application.unityVersion, ["items"] = report, ["errors"] = JArray.FromObject(problems) }.ToString());
        Require(problems.Count == 0, string.Join("\n", problems));
        Debug.Log("PICKUP_ART_VERIFIED " + report.Count);
    }
}
#endif

