var scene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
var meshes = scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<UnityEngine.MeshFilter>(true)).ToArray();
var record = new {
    scene = scene.path,
    dirty = scene.isDirty,
    playing = UnityEditor.EditorApplication.isPlaying,
    domes = meshes.Where(m => m.name.StartsWith("CF_B5_") && m.name.Contains("Dome")).Select(m => new {m.name, active = m.gameObject.activeInHierarchy, center = m.GetComponent<UnityEngine.Renderer>().bounds.center.ToString(), size = m.GetComponent<UnityEngine.Renderer>().bounds.size.ToString()}).ToArray(),
    tunnels = meshes.Where(m => m.name.StartsWith("CF_B5-T") && m.name.Contains("Vault")).Select(m => new {m.name, active = m.gameObject.activeInHierarchy}).ToArray()
};
var repo = System.IO.Path.GetFullPath(System.IO.Path.Combine(UnityEngine.Application.dataPath, "../../.."));
var dest = System.IO.Path.Combine(repo,"Docs/도면/Decision/원형공동/B5_섹터/scene_reference.json");
System.IO.Directory.CreateDirectory(System.IO.Path.GetDirectoryName(dest));
System.IO.File.WriteAllText(dest, Newtonsoft.Json.JsonConvert.SerializeObject(record, Newtonsoft.Json.Formatting.Indented));
return record;
