"""Compare preserved assets and scene state. Author 송예찬."""
from pathlib import Path
import json, hashlib, collections
H=Path(__file__).resolve().parent; R=H.parents[1]
D=R/'Docs/검수/2026-11-08_B5_CorridorOnlyGuidance'; A=R/'Unity/After_Seconds_Build_V0.01/Assets'
before=json.loads((D/'before.json').read_text(encoding='utf-8'))
after=json.loads((D/'audit.json').read_text(encoding='utf-8'))
baseline=json.loads((H/'assets_before.json').read_text(encoding='utf-8'))
changed=[]; missing=[]
for name,h in baseline.items():
 p=A/Path(name)
 if not p.exists():missing.append(name)
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=h:changed.append(name)
def count(items):return collections.Counter(json.dumps(i,sort_keys=True) for i in items)
oldlights=count(before['lights']); newlights=count(after['lights'])
oldhierarchy=count(before['hierarchy']); newhierarchy=count(after['hierarchy'])
out=dict(author='송예찬',baselineAssets=len(baseline),unchanged=len(baseline)-len(changed)-len(missing),changed=changed,missing=missing,lightsBefore=len(before['lights']),lightsAfter=len(after['lights']),lightsUnchanged=oldlights==newlights,oldTransforms=len(before['hierarchy']),oldTransformsChanged=list((oldhierarchy-newhierarchy).elements()),newTransforms=sum((newhierarchy-oldhierarchy).values()))
(D/'preservation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=True))
assert not missing and oldlights==newlights and not out['oldTransformsChanged']
assert all(n.replace('\\','/')=='Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular.unity' for n in changed),changed
