from pathlib import Path
H=Path(__file__).resolve().parent;old=H.parent/'F1_EnvironmentalStory'
for name in ['Finish.cs','PlayCheck.cs']:
 s=(old/name).read_text(encoding='utf8').replace('F1Story','F1Sunset').replace('1F_EnvironmentalStory','1F_SunsetSky').replace('F1_EnvironmentalStory','F1_SunsetSky')
 if name=='PlayCheck.cs':
  s=s.replace('"WallIvy",new Vector3(-3.5f,1.3f,-17.4f),new Vector3(-4.9f,1,-14.1f),63','"Wilderness",new Vector3(-82,1.65f,-29.1f),new Vector3(-550,25,-46),74').replace('"Floor",new Vector3(-22,1.65f,-10),new Vector3(-18,.08f,-9.8f),65','"Exit",new Vector3(-51,1.65f,-28),new Vector3(-230,10,-34),76').replace('c.farClipPlane=2200','c.farClipPlane=8500')
 else:s=s[:s.index(' public static object Check()')]+'\n}\n'
 (H/name).write_text(s,encoding='utf8')
print('Scoped review tools prepared')
