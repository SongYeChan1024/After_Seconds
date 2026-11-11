"""Verify saved scene inventories and every referenced exported mesh (read-only)."""
from analyze import *
H=Path(__file__).parent
errors=[];scenes=[];checked=set();derived=set()
for p in sorted((H/'results').glob('*.json')):
    before=json.loads(p.read_text());after=json.loads((CACHE/p.name).read_text())
    a={r['id']:r for r in before['rows']};b={r['id']:r for r in after['rows']}
    if a.keys()!=b.keys():errors.append(p.stem+': renderer identities changed')
    changed=[]
    for key,r in b.items():
        old=a.get(key,{})
        for field in ('path','matrix','materials','lod','level','skinned'):
            if old.get(field)!=r[field]:errors.append(p.stem+': changed '+field+' '+r['path'])
        if old.get('mesh')!=r['mesh']:changed.append(r['path'])
        if r['skinned'] and old.get('mesh')!=r['mesh']:errors.append(p.stem+': skinned mesh changed')
        if '/ZF_' in r['asset']:derived.add(r['mesh'])
        if r['mesh'] in checked:continue
        checked.add(r['mesh']);v,subs=mesh(r['mesh'])
        if not len(v) or not np.isfinite(v).all():errors.append(r['asset']+': invalid vertices')
        for ix in subs:
            if len(ix) and (ix.min()<0 or ix.max()>=len(v)):errors.append(r['asset']+': invalid indices')
        if '/ZF_' in r['asset'] and not any(len(ix) for ix in subs):errors.append(r['asset']+': empty derivative')
    errors.extend(after['errors'])
    scenes.append(dict(scene=before['scene'],activeMeshRenderers=len(b),changedRenderers=len(changed),rendererPaths=changed))
report=dict(scenes=scenes,sceneCount=len(scenes),meshCount=len(checked),derivedMeshCount=len(derived),changedRenderers=sum(s['changedRenderers'] for s in scenes),errors=errors)
(H/'saved_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='scenes'},indent=2))
assert not errors
