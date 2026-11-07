"""Operational fit-out preservation baseline. Author 송예찬."""
from pathlib import Path
import json,hashlib,subprocess
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_B5_OperationalDetail';D.mkdir(parents=True,exist_ok=True)
old=R/'SourceAssets/B5_SpatialRefinement'
s=(old/'Inspect.cs').read_text(encoding='utf-8').replace('SpatialInspect','OperationalInspect').replace('B5_SpatialRefinement','B5_OperationalDetail').replace('AfterSeconds_Spatial_','AfterSeconds_Operational_')
(H/'Inspect.cs').write_text(s,encoding='utf-8')
A=R/'Unity/After_Seconds_Build_V0.01/Assets'
if not (H/'assets_before.json').exists():
 (H/'assets_before.json').write_text(json.dumps({str(p.relative_to(A)):hashlib.sha256(p.read_bytes()).hexdigest() for p in A.rglob('*') if p.is_file()},indent=2),encoding='utf-8')
 (H/'git_before.txt').write_text(subprocess.check_output(['git','status','--porcelain','--untracked-files=normal'],cwd=R,text=True,encoding='utf-8'),encoding='utf-8')
print('Baseline ready')
