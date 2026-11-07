from pathlib import Path
import json,shutil
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_T02_StairA'
B=Path(json.loads((D/'backup.json').read_text(encoding='utf-8'))['backup'])/'guidance_assets'
A=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds'
assert not B.exists()
files=[p for p in A.rglob('*') if p.is_file() and (p.name.startswith('ND_') or p.name.startswith(tuple(f'SC_Display_{i:02}' for i in range(1,5))))]
for p in files:
    out=B/p.relative_to(A);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
print(f'Backed up {len(files)} current guidance/monitor files')
