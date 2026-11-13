// 검수 순서: 저장된 1F 확인 -> 계단 A 천장 선택/시점 지정 -> 최종 상태 기록.
using System;
using System.IO;
using UnityEngine;
using UnityEditor;
using UnityEngine.SceneManagement;
using Newtonsoft.Json;

public static class CoreRoofFinish
{
    public static object Run()
    {
        var scene = SceneManager.GetActiveScene();
        if (scene.isDirty || Application.isPlaying || !scene.path.EndsWith("Level_1F_Factory.unity"))
            throw new Exception("Saved 1F edit mode required.");
        Selection.activeGameObject = GameObject.Find("AE_VA_Roof");
        var view = SceneView.lastActiveSceneView;
        if (view)
        {
            var position = new Vector3(-41.5f, 1.7f, 24.8f);
            var target = new Vector3(-44, 2.5f, 31.8f);
            view.sceneLighting = true;
            view.LookAt(target, Quaternion.LookRotation(target-position), 4.5f, false, true);
            view.Focus();
            view.Repaint();
        }
        var result = new {
            scene = scene.path, saved = !scene.isDirty, playing = Application.isPlaying,
            selection = Selection.activeGameObject.name,
            mouseEnabled = UnityEngine.InputSystem.Mouse.current != null && UnityEngine.InputSystem.Mouse.current.enabled,
            keyboardEnabled = UnityEngine.InputSystem.Keyboard.current != null && UnityEngine.InputSystem.Keyboard.current.enabled,
            runInBackground = Application.runInBackground
        };
        var path = Path.GetFullPath(Path.Combine(Application.dataPath,
            "../../../Docs/Review/2026-11-13_1F_CoreRoof/final_state.json"));
        File.WriteAllText(path, JsonConvert.SerializeObject(result, Formatting.Indented));
        return result;
    }
}
