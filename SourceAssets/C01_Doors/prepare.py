from pathlib import Path
import json,hashlib,shutil,tempfile,datetime
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent;U=R/'Unity/After_Seconds_Build_V0.01'
scene=U/'Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular.unity'
if (H/'baseline.json').exists():raise SystemExit('Baseline already exists')
backup=Path(tempfile.gettempdir())/('AfterSeconds_C01Doors_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));backup.mkdir()
shutil.copy2(scene,backup/scene.name)
previous=json.loads((R/'SourceAssets/C01_PropRepair/baseline.json').read_text('utf-8'))
paths=[R/p for p in previous['protected']]
paths+=list((U/'Assets/Afrer_Seconds/05.Model/Props').rglob('*'))
paths+=list((U/'Assets/Afrer_Seconds/05.Model/Environment').rglob('*'))
protected={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}
(H/'baseline.json').write_text(json.dumps(dict(backup=str(backup),scene=str(scene.relative_to(R)),sceneHash=hashlib.sha256(scene.read_bytes()).hexdigest(),protected=protected),indent=2),encoding='utf-8')
print(json.dumps(dict(backup=str(backup),protected=len(protected))))
