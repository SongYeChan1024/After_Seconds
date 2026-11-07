"""Preservation baseline for B5 structural/detail revision. Author 송예찬."""
from pathlib import Path
import hashlib,json,subprocess
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_B5_SpatialRefinement';D.mkdir(parents=True,exist_ok=True)
old=R/'SourceAssets/B5_RemainingDomes'
s=(old/'Inspect.cs').read_text(encoding='utf-8').replace('RemainingInspect','SpatialInspect').replace('2026-11-08_B5_RemainingDomes','2026-11-08_B5_SpatialRefinement').replace('AfterSeconds_Remaining_','AfterSeconds_Spatial_')
(H/'Inspect.cs').write_text(s,encoding='utf-8')
A=R/'Unity/After_Seconds_Build_V0.01/Assets'
if not (H/'assets_before.json').exists():(H/'assets_before.json').write_text(json.dumps({str(p.relative_to(A)):hashlib.sha256(p.read_bytes()).hexdigest() for p in A.rglob('*') if p.is_file()},indent=2),encoding='utf-8')
(H/'git_before.txt').write_text(subprocess.check_output(['git','status','--porcelain','--untracked-files=normal'],cwd=R,text=True,encoding='utf-8'),encoding='utf-8')
print('Source, report, assets baseline prepared')
