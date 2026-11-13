from pathlib import Path
H=Path(__file__).resolve().parent
p=H/'PlayCheck.cs';s=p.read_text(encoding='utf8').replace('FindObjectsByType<Transform>(FindObjectsSortMode.None)','FindObjectsByType<Transform>()').replace('x.name.StartsWith("F1_")&&x.name.Contains','x.parent&&x.parent.name.StartsWith("1F_")&&x.name.StartsWith("F1_")&&x.name.Contains')
s=s.replace('static void Tick(){if','static void Tick(){try{if').replace('if(elapsed>7)End(true);}','if(elapsed>7)End(true);}catch(Exception ex){errors.Add("Review tool: "+ex);End(false);}}').replace('mainCameraFar=Camera.main.farClipPlane','mainCameraFar=Camera.main?Camera.main.farClipPlane:0')
p.write_text(s,encoding='utf8')
