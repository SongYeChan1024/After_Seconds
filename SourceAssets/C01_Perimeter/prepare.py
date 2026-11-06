from pathlib import Path
import datetime,hashlib,json,os,shutil
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent;P=R/'Unity/After_Seconds_Build_V0.01'
scene=P/'Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular.unity'
backup=Path(os.environ['TEMP'])/('AfterSeconds_Perimeter_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));backup.mkdir()
shutil.copy2(scene,backup/scene.name)
protected={str(p.relative_to(R)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in (P/'Assets').rglob('*') if p.is_file() and (p.suffix in ['.cs','.controller','.overrideController'] or (p.suffix=='.unity' and p!=scene) or p.name.startswith('AF_C01_ThreePortalRibs'))}
(H/'baseline.json').write_text(json.dumps({'backup':str(backup),'protected':protected},indent=2),encoding='utf-8')
print(json.dumps({'backup':str(backup),'protected':len(protected)}))
