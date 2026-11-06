var player=UnityEngine.SceneManagement.SceneManager.GetActiveScene().GetRootGameObjects().Single(g=>g.name.StartsWith("Player"));
var cc=player.GetComponent<UnityEngine.CharacterController>();cc.enabled=false;player.transform.SetPositionAndRotation(new UnityEngine.Vector3(-14.4f,-81.32f,-12.7f),UnityEngine.Quaternion.Euler(0,0,0));cc.enabled=true;
var cam=UnityEngine.Camera.main;if(cam==null)throw new System.Exception("Main camera unavailable");
return new{frame=UnityEngine.Time.frameCount,camera=cam.transform.position.ToString()};
