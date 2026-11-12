from pathlib import Path
import hashlib,json,time
H=Path(__file__).resolve().parent;R=H.parents[1];t=time.time();baseline=json.loads((H/'protected_before.json').read_text(encoding='utf8'));changed=[];missing=[]
for n,digest in baseline.items():
 p=R/n
 if not p.exists():missing.append(n);continue
 if hashlib.file_digest(p.open('rb'),'sha256').hexdigest()!=digest:changed.append(n)
result=dict(checked=len(baseline),unchanged=len(baseline)-len(changed)-len(missing),changed=changed,missing=missing,seconds=round(time.time()-t,2))
(R/'Docs/Review/2026-11-12_1F_FullFloor/protected.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result),flush=True)
assert not changed and not missing,'Protected pre-existing Unity files changed'
