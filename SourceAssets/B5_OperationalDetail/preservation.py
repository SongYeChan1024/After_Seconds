"""Compare the actual final scene and asset hashes with this task's baseline. 송예찬."""
from pathlib import Path
import json,hashlib,collections
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_B5_OperationalDetail';A=R/'Unity/After_Seconds_Build_V0.01/Assets'
before=json.loads((D/'before.json').read_text(encoding='utf-8'));after=json.loads((D/'audit.json').read_text(encoding='utf-8'));baseline=json.loads((H/'assets_before.json').read_text(encoding='utf-8'));changed=[];missing=[]
for name,h in baseline.items():
 p=A/Path(name)
 if not p.exists():missing.append(name)
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=h:changed.append(name)
def counter(items):return collections.Counter(json.dumps(i,sort_keys=True) for i in items)
oldlights=counter(before['lights']);newlights=counter(after['lights']);light_removed=list((oldlights-newlights).elements());light_added=list((newlights-oldlights).elements())
protected=lambda q:'/C01_Experiment_Art' in q['path'] or '/B5_Art_C01_T01' in q['path'] or '/T01_Corridor_Finish' in q['path']
oldprotected=counter([q for q in before['hierarchy'] if protected(q)]);newprotected=counter([q for q in after['hierarchy'] if protected(q)])
out=dict(author='송예찬',baselineAssets=len(baseline),unchanged=len(baseline)-len(changed)-len(missing),changed=changed,missing=missing,lightsBefore=len(before['lights']),lightsAfter=len(after['lights']),lightRemovedOrChanged=light_removed,lightAddedOrChanged=light_added,protectedTransforms=sum(oldprotected.values()),protectedTransformsChanged=list((oldprotected-newprotected).elements()),protectedTransformsAdded=list((newprotected-oldprotected).elements()),scene=after['scene'])
(D/'preservation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(out,ensure_ascii=True))
assert not missing and not light_removed and not light_added and oldprotected==newprotected
assert all(n.replace('\\','/')=='Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular.unity' for n in changed),changed
