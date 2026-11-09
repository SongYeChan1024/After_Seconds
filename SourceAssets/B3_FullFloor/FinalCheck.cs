using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEngine.SceneManagement;
using Newtonsoft.Json;

public static class B3FinalCheck
{
    public static object Run()
    {
        AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        var scene = SceneManager.GetActiveScene();
        if (Application.isPlaying || scene.isDirty || !scene.path.EndsWith("Level_B3_Circular.unity"))
            throw new Exception("Saved B3 edit mode required");
        var roots = scene.GetRootGameObjects();
        var all = roots.SelectMany(g => g.GetComponentsInChildren<Transform>(true)).ToArray();
        var player = roots.Single(g => g.name.StartsWith("Player"));
        var cameras = all.SelectMany(t => t.GetComponents<Camera>()).ToArray();
        var cameraRoot = roots.Single(g => g.name == "Camera");
        var links = new List<object>();
        foreach (var comp in cameraRoot.GetComponentsInChildren<Component>(true))
        {
            if (!comp) continue;
            var it = new SerializedObject(comp).GetIterator();
            while (it.Next(true))
            {
                if (it.propertyType != SerializedPropertyType.ObjectReference || !it.objectReferenceValue) continue;
                var value = it.objectReferenceValue;
                var target = value is GameObject go ? go.transform : value is Component co ? co.transform : null;
                if (target && (target == player.transform || target.IsChildOf(player.transform)))
                    links.Add(new { component = comp.GetType().Name, property = it.propertyPath, target = target.name });
            }
        }
        var offRooms = new[] { "C01", "C02", "W01", "W02", "E03" };
        var level = roots.Single(g => g.name == "B3_Circular_SampleFloor");
        var circuits = offRooms.Select(id => new {
            room = id,
            activeLights = level.transform.Find("B3_" + id + "_Sector/WorkLighting").GetComponentsInChildren<Light>(true).Count(l => l.enabled)
        }).ToArray();
        int missingScripts = all.Sum(t => GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject));
        int lodColliders = all.Where(t => t.name.StartsWith("Distance_LOD")).Sum(t => t.GetComponentsInChildren<Collider>(true).Length);
        var sources = new[] { "B3_FullFloor.json", "B3_FullFloor_VARCO.json", "B4_Finish.json" }.Select(n => new {
            name = n, meta = File.Exists("Assets/Afrer_Seconds/06.Data/AssetSources/" + n + ".meta")
        }).ToArray();
        if (cameras.Length != 1 || !cameras[0].CompareTag("MainCamera") || !cameras[0].enabled || links.Count == 0 || missingScripts != 0 || lodColliders != 0 || circuits.Any(c => c.activeLights != 0) || sources.Any(s => !s.meta))
            throw new Exception("Final scene integrity check failed");
        var result = new {
            scene = scene.path, saved = !scene.isDirty, playing = Application.isPlaying,
            runInBackground = Application.runInBackground, cameras = cameras.Length,
            mainCamera = cameras[0].name, cameraPlayerLinks = links,
            playerPosition = player.transform.position.ToString("F3"), playerYaw = player.transform.eulerAngles.y,
            defaultOffCircuits = circuits, missingScripts, lodColliders, sourceMetadata = sources
        };
        string root = Path.GetFullPath(Path.Combine(Application.dataPath, "../../.."));
        File.WriteAllText(root + "/Docs/Review/2026-11-09_B3_FullFloor/final_state.json", JsonConvert.SerializeObject(result, Formatting.Indented));
        return result;
    }
}
