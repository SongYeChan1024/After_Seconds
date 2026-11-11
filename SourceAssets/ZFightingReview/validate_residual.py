"""Recheck all final broad-phase candidates against the final saved geometry."""
from repair_plan import *
H=Path(__file__).parent;target=H/'verified_candidates';target.mkdir(exist_ok=True)
for p in sorted((H/'final').glob('*.json')):
    d=json.loads(p.read_text());current=json.loads((CACHE/p.name).read_text())
    assert [r['id'] for r in d['rows']]==[r['id'] for r in current['rows']]
    d['rows']=current['rows'];d['duplicateMeshes']=[]
    # The finish pass changes only these meshes; check new exact duplicates too.
    seen=set()
    for r in d['rows']:
        if r['skinned'] or r['mesh'] in seen:continue
        seen.add(r['mesh'])
        if '/ZF_' not in r['asset']:continue
        v,subs=mesh(r['mesh']);dup={};count=0
        for si,ix in enumerate(subs):
            if not len(ix):continue
            xyz=np.round(v[ix]*1e5).astype('int64');start=np.lexsort((xyz[:,:,2],xyz[:,:,1],xyz[:,:,0]),axis=1)[:,0]
            xyz=np.take_along_axis(xyz,((np.arange(3)[None,:]+start[:,None])%3)[:,:,None],axis=1)
            _,first,inv=np.unique(xyz.reshape(-1,9),axis=0,return_index=True,return_inverse=True)
            removal=np.where(np.arange(len(ix))!=first[inv])[0]
            if len(removal):dup[str(si)]=removal.tolist();count+=len(removal)
        if count:d['duplicateMeshes'].append(dict(mesh=r['mesh'],asset=r['asset'],remove=dup,count=count))
    q=target/p.name;q.write_text(json.dumps(d));plan(q)
