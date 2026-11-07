from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/검수/2026-11-08_C02_Security';b=json.loads((H/'baseline.json').read_text(encoding='utf-8'));changed=[];missing=[]
for rel,sha in b.items():
 p=R/rel
 if not p.exists():missing.append(rel)
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=sha:changed.append(rel)
out=dict(baselineFiles=len(b),changed=changed,missing=missing,sceneOnly=len(changed)==1 and changed[0].endswith('Level_B5_Circular.unity'))
(O/'file_preservation.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=True));assert out['sceneOnly'] and not missing
