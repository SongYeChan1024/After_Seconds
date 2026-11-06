from pathlib import Path
import json,hashlib,shutil,tempfile,datetime
H=Path(__file__).resolve().parent;R=H.parents[1];U=R/'Unity/After_Seconds_Build_V0.01';O=R/'Docs/검수/2026-11-07_C01_Lighting';O.mkdir(exist_ok=True)
if (H/'baseline.json').exists():raise SystemExit('Baseline exists')
B=Path(tempfile.gettempdir())/('AfterSeconds_C01Lighting_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));B.mkdir();scene=U/'Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular.unity';shutil.copy2(scene,B/scene.name)
paths=[p for p in (U/'Assets/Afrer_Seconds/05.Model').rglob('*') if p.is_file()];paths+=list((U/'Assets/Afrer_Seconds/02.Scripts').rglob('*.cs'))
for p in paths:
 if p.suffix=='.mat':dst=B/p.relative_to(R);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
(H/'baseline.json').write_text(json.dumps(dict(backup=str(B),scene=str(scene.relative_to(R)),protected={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}),indent=2),encoding='utf-8')
print(json.dumps(dict(backup=str(B),protected=len(paths))))
