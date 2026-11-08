from pathlib import Path
H=Path(__file__).resolve().parent
f=H/'Review.cs';s=f.read_text(encoding='utf-8')
s=s.replace('public static object Capture(){var s=Check();var plan=Plan();try{','public static object Capture(){var s=Check();var plan=Plan();var player=s.GetRootGameObjects().Single(g=>g.name.StartsWith("Player"));player.SetActive(false);try{')
insert='''
 public static object Details(){var s=Check();var plan=Plan();var player=s.GetRootGameObjects().Single(g=>g.name.StartsWith("Player"));player.SetActive(false);int count=0;
  try{foreach(string code in new[]{"N01","E01","E02","W01","W02","S01","E03","VL","VA"}){var r=plan["rooms"].Single(q=>(string)q["id"]==code);var c=origin+new Vector3((float)r["x"],0,-(float)r["v"]);Vector3 p,t;
   switch(code){case "N01":p=new Vector3(-1,1.7f,.5f);t=new Vector3(0,1.8f,8);break;case "E01":p=new Vector3(-1,1.7f,-.4f);t=new Vector3(0,1.7f,6);break;case "E02":p=new Vector3(.5f,1.7f,-1);t=new Vector3(5.5f,1.1f,1.2f);break;case "W01":p=new Vector3(-2.2f,1.7f,-1.9f);t=new Vector3(-1.2f,1.3f,5);break;case "W02":p=new Vector3(1.5f,1.7f,0);t=new Vector3(-4.5f,1.3f,.5f);break;case "S01":p=new Vector3(-.4f,1.7f,.3f);t=new Vector3(1,1.7f,-5);break;case "E03":p=new Vector3(-1,1.7f,-.5f);t=new Vector3(0,1.2f,-5.5f);break;case "VL":p=new Vector3(0,1.7f,3.7f);t=new Vector3(0,1.4f,-1.5f);break;default:p=new Vector3(.96f,18.7f,-1.8f);t=new Vector3(0,18,-4.5f);break;}
   Shot(code+"_detail",c+p,c+t,78);count++;}
  }finally{EditorSceneManager.OpenScene(s.path);}return new{images=count};}
'''
s=s.rstrip();s=s[:-1]+insert+'}\n';f.write_text(s,encoding='utf-8')
s=(H.parent/'B4_Observation/FinalState.cs').read_text(encoding='utf8').replace('B4FinalState','BFFFinalState').replace('B4_Observation','B4_FullFloor').replace('data.lights!=18','data.lights!=261')
(H/'FinalState.cs').write_text(s,encoding='utf8')
