from pathlib import Path
import json,hashlib,shutil
H=Path(__file__).resolve().parent;R=H.parents[1];U=R/'Unity/After_Seconds_Build_V0.01';O=R/'Docs/검수/2026-11-06_B5_FullLayout'
O.mkdir(parents=True,exist_ok=True)
scene=U/'Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular.unity'
if (H/'protected_before.json').exists():raise SystemExit('Snapshot already exists; not overwriting.')
shutil.copy2(scene,H/'before.unity')
paths=list((U/'Assets/Afrer_Seconds/02.Scripts').rglob('*.cs'))+list((U/'Assets/Afrer_Seconds/07.Animator').rglob('*.controller'))+list((U/'Assets/Afrer_Seconds/01.Scenes').rglob('*.unity'))
(H/'protected_before.json').write_text(json.dumps({str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2),encoding='utf-8')
print('Saved baseline',len(paths))
