"""Inventory and preservation baseline. Author 송예찬."""
import json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_B5_RemainingDomes';A=R/'Unity/After_Seconds_Build_V0.01/Assets'
before=json.loads((D/'before.json').read_text(encoding='utf-8'))
if not (H/'assets_before.json').exists():
 (H/'assets_before.json').write_text(json.dumps({str(p.relative_to(A)):hashlib.sha256(p.read_bytes()).hexdigest() for p in A.rglob('*') if p.is_file()},indent=2),encoding='utf-8')
for r in before['renderers']:
 if r['active'] and r['enabled'] and any(x in r['path'] for x in ['Existing_Props_FirstPass','Outer_Caverns_Props']):print(r['path'].split('B5_Circular_Core_V0.03/')[-1],r['position'],[round(a,2) for a in r['size']])
