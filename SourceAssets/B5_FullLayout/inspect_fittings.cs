var s=UnityEngine.SceneManagement.SceneManager.GetActiveScene();
var root=s.GetRootGameObjects().Single(g=>g.name.StartsWith("B5_Circular")).transform;
return root.Find("B5_Art_C01_T01").Cast<UnityEngine.Transform>().Select(t=>new{t.name,pos=t.localPosition.ToString(),rot=t.localEulerAngles.ToString(),bounds=t.GetComponentsInChildren<UnityEngine.Renderer>().Select(r=>new{r.name,center=r.bounds.center.ToString(),size=r.bounds.size.ToString()}).ToArray()}).ToArray();
