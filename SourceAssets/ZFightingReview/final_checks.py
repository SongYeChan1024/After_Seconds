from pathlib import Path
import json,hashlib,subprocess,collections
ROOT=Path(__file__).resolve().parents[2];H=Path(__file__).parent;P=ROOT/'Unity/After_Seconds_Build_V0.01'
before=json.loads((H/'protected_before.json').read_text());changed=[];missing=[]
for rel,sha in before.items():
 p=P/rel
 if not p.exists():missing.append(rel)
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=sha:
  raw=p.read_bytes();lf=raw.replace(b'\r\n',b'\n');crlf=lf.replace(b'\n',b'\r\n')
  if hashlib.sha256(lf).hexdigest()==sha:p.write_bytes(lf)
  elif hashlib.sha256(crlf).hexdigest()==sha:p.write_bytes(crlf)
  else:changed.append(rel)
applied=[json.loads(p.read_text()) for p in H.glob('applied_*.json')]
expected={a['scene'] for a in applied}
unexpected=[p for p in changed if p not in expected]
newmesh=list((P/'Assets/Afrer_Seconds/05.Model').rglob('ZF_*.asset'))
meta_missing=[str(p.relative_to(P)) for p in newmesh if not p.with_suffix('.asset.meta').exists()]
tracked=subprocess.check_output(['git','-c','core.quotepath=false','diff','--name-only'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).splitlines()
allowed={'Unity/After_Seconds_Build_V0.01/'+s for s in expected}|{'AGENTS.md','CLAUDE.md'}
extra=[p for p in tracked if p not in allowed]
verified=json.loads((H/'saved_validation.json').read_text())
report=dict(protectedFiles=len(before),changedScenes=len(changed),unexpectedProtectedChanges=unexpected,missingProtectedFiles=missing,modifiedTrackedFilesOutsideScenesAndHandoff=extra,derivedMeshes=len(newmesh),derivedMiB=round(sum(p.stat().st_size for p in newmesh)/1024**2,2),missingMeta=meta_missing,renderersChanged=verified['changedRenderers'],allTransformsAndCollidersUnchanged=all(a['transformsAndCollidersUnchanged'] for a in applied))
(H/'preservation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
assert not unexpected and not missing and not meta_missing and not extra
