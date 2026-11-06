var root=UnityEngine.SceneManagement.SceneManager.GetActiveScene().GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular")).transform;
var desk=root.Find("Existing_Props_FirstPass/B5-03_P03");
return new{desk=desk.GetComponentsInChildren<UnityEngine.Renderer>().Select(r=>new{r.name,pos=r.bounds.center.ToString(),size=r.bounds.size.ToString()}).ToArray(),colliders=desk.GetComponentsInChildren<UnityEngine.Collider>().Select(c=>new{c.name,pos=c.bounds.center.ToString(),size=c.bounds.size.ToString()}).ToArray(),pipeline=UnityEngine.Rendering.GraphicsSettings.currentRenderPipeline.name};
