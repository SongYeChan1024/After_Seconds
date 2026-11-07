from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_B5_TwoDomeGuidance'
base=json.loads((H/'baseline.json').read_text(encoding='utf-8'));missing=[];changed=[];unexpected=[]
for rel,sha in base.items():
    p=R/rel
    if not p.exists():missing.append(rel);continue
    if hashlib.sha256(p.read_bytes()).hexdigest()==sha:continue
    changed.append(rel)
    allowed=p.name=='Level_B5_Circular.unity' or p.name in [f'SC_Display_{i:02}.png' for i in range(1,5)] or ('Environment' in p.parts and p.name.startswith('ND_'))
    if not allowed:unexpected.append(rel)
out=dict(baselineFiles=len(base),preservedFiles=len(base)-len(changed)-len(missing),changed=changed,missing=missing,unexpected=unexpected)
(D/'file_preservation.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=True));assert not missing and not unexpected
