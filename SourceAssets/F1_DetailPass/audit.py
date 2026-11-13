from pathlib import Path
import json,hashlib,os,re,subprocess
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent;O=R/'Docs/Review/2026-11-13_1F_DetailPass'
def read(n):return json.loads((O/n).read_text(encoding='utf-8-sig'))
protected=read('protected_before.json');changed=[]
for p,sha in protected.items():
 if not (R/p).exists() or hashlib.sha256((R/p).read_bytes()).hexdigest()!=sha:changed.append(p)
old={q['path']:q for q in read('before_transforms.json')};new={q['path']:q for q in read('after_transforms.json')};differences=[]
for p,b in old.items():
 if p not in new:differences.append(p+' missing');continue
 a=new[p]
 for key in ['position','local','rotation','scale']:
  if any(abs(x-y)>.00001 for x,y in zip(b[key],a[key])):differences.append(p+' '+key)
 if b['active']!=a['active']:differences.append(p+' active')
 if b['colliders']!=a['colliders']:differences.append(p+' collider')
tmp=Path(os.environ['LOCALAPPDATA'])/'Temp/AfterSeconds_DetailPass_20261113/before';guid=[]
for p in read('backup.json'):
 if not p.endswith('.meta'):continue
 before=re.search(r'^guid: (\w+)',(tmp/Path(p).name).read_text(),re.M)[1];after=re.search(r'^guid: (\w+)',(R/p).read_text(),re.M)[1]
 if before!=after:guid.append(p)
result=dict(protectedExistingFiles=len(protected),changedProtectedFiles=changed,beforeTransforms=len(old),afterTransforms=len(new),originalTransformChanges=differences,changedGUIDs=guid)
(O/'preservation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=False))
assert not changed and not differences and not guid
