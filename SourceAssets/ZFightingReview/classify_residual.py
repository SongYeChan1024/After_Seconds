"""Distinguish float32 edge slivers from overlaps with a nontrivial interior."""
from analyze import *
from functools import lru_cache
H=Path(__file__).parent
if os.environ.get('ZF_FILTER'):(H/'precision_plans').mkdir(exist_ok=True)
@lru_cache(maxsize=16)
def cached(key):return mesh(key)
rows=[];remaining=[]
for p in sorted((H/'verified_residual').glob('*.json')):
    d=json.loads(p.read_text());area=0;largest=0;corearea=0;slivers=0;cores=[]
    keep=[]
    for patch in d['patches']:
        edits=[]
        r=d['rows'][patch['renderer']];v,subs=cached(r['mesh']);m=np.array(r['matrix']).reshape(4,4)
        for e in patch['edits']:
            tri=v[subs[patch['submesh']][e['triangle']]]@m[:3,:3].T+m[:3,3]
            n=np.cross(tri[1]-tri[0],tri[2]-tri[0]);axis=np.argmax(abs(n));axes=[i for i in range(3) if i!=axis]
            xy=tri[:,axes];original=shapely.Polygon(xy)
            replacement=shapely.union_all([shapely.Polygon(np.array(t)@xy) for t in e['bary']])
            overlap=original.difference(replacement);core=overlap.buffer(-.00005)
            area+=overlap.area;largest=max(largest,overlap.area)
            if core.area>1e-8:
                edits.append(e)
                corearea+=core.area;cores.append(dict(renderer=r['path'],triangle=e['triangle'],area=overlap.area,coreArea=core.area))
            else:slivers+=1
        if edits:keep.append(dict(renderer=patch['renderer'],submesh=patch['submesh'],edits=edits))
    rec=dict(scene=p.stem,residualProjectedArea=area,largestResidualFaceArea=largest,float32EdgeSliverTriangles=slivers,interiorOverlaps=len(cores),interiorArea=corearea,details=cores)
    rows.append(rec);remaining.extend(cores)
    if os.environ.get('ZF_FILTER'):
        d['patches']=keep;(H/'precision_plans'/p.name).write_text(json.dumps(d))
report=dict(edgeToleranceMetres=.00005,scenes=rows,nontrivialInteriorOverlaps=len(remaining),note='Planar overlap at the float32 edge precision limit is reported, not repeatedly retriangulated. Zero interior means erosion by 0.05 mm removes the entire remainder; it does not mean mathematically zero overlap.')
(H/'residual_summary.json').write_text(json.dumps(report,indent=2))
print(json.dumps(dict(nontrivialInteriorOverlaps=len(remaining),scenes=[{k:v for k,v in r.items() if k!='details'} for r in rows]),indent=2))
