from pathlib import Path
import os,json,hashlib,subprocess,shutil
R=Path(__file__).resolve().parents[2];O=R/'Docs/Review/2026-11-13_1F_EnvironmentalStory';T=Path(os.environ['LOCALAPPDATA'])/'Temp/AfterSeconds_EnvironmentalStory_20261113/before';T.mkdir(parents=True,exist_ok=True)
base='Unity/After_Seconds_Build_V0.01/'
allowed=[base+'Assets/Afrer_Seconds/05.Model/Environment/1F/',base+'Assets/Afrer_Seconds/01.Scenes/Stage/Level_1F_Factory.unity',base+'Assets/Afrer_Seconds/01.Scenes/Stage/Level_1F_Factory/']
files=subprocess.check_output(['git','ls-files','-z','Unity'],cwd=R).decode().split('\0');protected={}
for p in files:
 if not p or any(p.startswith(a) for a in allowed):continue
 protected[p]=hashlib.sha256((R/p).read_bytes()).hexdigest()
(O/'protected_before.json').write_text(json.dumps(protected,indent=2))
E=R/base/'Assets/Afrer_Seconds/05.Model/Environment/1F';S=R/base/'Assets/Afrer_Seconds/01.Scenes/Stage/Level_1F_Factory.unity'
paths=[S,Path(str(S)+'.meta'),*E.glob('AE_WallIvy*'),*E.glob('AEWeathering*'),*E.glob('Textures/AE_Reflection*')]
for p in paths:shutil.copy2(p,T/p.name)
(O/'backup.json').write_text(json.dumps([str(p.relative_to(R)) for p in paths],indent=2))
print('PROTECTED',len(protected),'BACKUP',len(paths))
