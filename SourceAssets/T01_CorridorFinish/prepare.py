"""T01 제작 전 씬·기존 에셋 보존 기록. 작성자 송예찬."""
from pathlib import Path
import tempfile,datetime,hashlib,json,shutil
H=Path(__file__).resolve().parent;R=H.parents[1]
if (H/'baseline.json').exists():raise SystemExit('Baseline already exists; do not replace it.')
assets=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds'
scene=assets/'01.Scenes/Stage/Level_B5_Circular.unity'
backup=Path(tempfile.gettempdir())/('AfterSeconds_T01_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir();shutil.copy2(scene,backup/scene.name)
files={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in assets.rglob('*') if p.is_file()}
(H/'baseline.json').write_text(json.dumps(dict(backup=str(backup),scene=str(scene.relative_to(R)),protected=files),indent=2),encoding='utf-8')
print('Backup:',backup,'protected files:',len(files))
