"""실험동 안내선·시설 표식 제작 준비. 작성자: 송예찬."""
from pathlib import Path
import datetime, hashlib, json, math, shutil, tempfile
H=Path(__file__).resolve().parent;R=H.parents[1];U=R/'Unity/After_Seconds_Build_V0.01';O=R/'Docs/검수/2026-11-07_C01_Wayfinding'
if (H/'baseline.json').exists():raise SystemExit('Baseline already exists')
backup=Path(tempfile.gettempdir())/('AfterSeconds_C01Wayfinding_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));backup.mkdir()
scene=U/'Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular.unity';shutil.copy2(scene,backup/scene.name)
protected={}
for p in (U/'Assets/Afrer_Seconds').rglob('*'):
    if p.is_file():protected[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
(H/'baseline.json').write_text(json.dumps(dict(backup=str(backup),scene=str(scene.relative_to(R)),sceneHash=hashlib.sha256(scene.read_bytes()).hexdigest(),protected=protected),indent=2),encoding='utf-8')
print(json.dumps(dict(backup=str(backup),protected=len(protected))))
