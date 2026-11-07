from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_B5_DestinationColors';baseline=json.loads((H/'baseline.json').read_text(encoding='utf-8'))
changed=[];missing=[]
for rel,sha in baseline.items():
 p=R/rel
 if not p.exists():missing.append(rel)
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=sha:changed.append(rel)
allowed={'Level_B5_Circular.unity'}|{f'SC_Display_{i:02}.png' for i in range(1,5)}
unexpected=[rel for rel in changed if Path(rel).name not in allowed]
result=dict(baselineFiles=len(baseline),preservedFiles=len(baseline)-len(changed)-len(missing),changed=changed,missing=missing,unexpected=unexpected)
(D/'file_preservation.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=True));assert not missing and not unexpected
