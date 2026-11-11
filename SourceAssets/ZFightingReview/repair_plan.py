"""Clip only redundant coplanar surface coverage; preserve original collision.
Outputs barycentric triangles for Unity to interpolate original vertex channels.
No scene/model files are modified here. A 0.05 mm plane-distance gate rejects
merely parallel or intersecting geometry. Transparent surfaces are not clipped.
"""
from analyze import *
from functools import lru_cache
import hashlib
PLAN=Path(__file__).parent/os.environ.get('ZF_PLANS','plans');PLAN.mkdir(exist_ok=True)
@lru_cache(maxsize=64)
def cached(key):return mesh(key)
def plan(path):
 d=json.loads(path.read_text());rows=d['rows'];cut=collections.defaultdict(dict);candidate_pairs=set()
 for a in d['overlaps']:candidate_pairs.add(tuple(sorted(((a['a'],a['sa']),(a['b'],a['sb'])))))
 for a in d['internal']:candidate_pairs.add(((a['renderer'],a['submesh']),(a['renderer'],a['submesh'])))
 buffers={}
 def data(ri,si):
  k=(ri,si)
  if k in buffers:return buffers[k]
  r=rows[ri];v,subs=cached(r['mesh']);ix=subs[si];m=np.array(r['matrix']).reshape(4,4);t=(v@m[:3,:3].T+m[:3,3])[ix]
  nn=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(nn,axis=1);ok=area>2e-7;n=nn/np.maximum(area[:,None],1e-30);dist=np.sum(n*t[:,0],axis=1)
  # Do not quantize plane distance: float32 retriangulation can straddle every
  # distance-bin boundary. Project by dominant axis/sign, query spatially, then
  # accept only the exact all-vertices plane-distance/normal tests below.
  dominant=np.argmax(abs(n),axis=1)
  keys=np.column_stack((dominant,np.sign(n[np.arange(len(n)),dominant]))).astype('int64');groups={}
  for i in np.flatnonzero(ok):groups.setdefault(tuple(keys[i]),[]).append(int(i))
  result=(t,n,dist,groups);buffers[k]=result;return result
 def priority(rs):
  ri,si=rs;r=rows[ri];mat=r['materials'][min(si,len(r['materials'])-1)] if r['materials'] else None
  if mat and mat['queue']>=3000:return None
  # Fine overlay materials take precedence inside a mesh; explicit floor surfaces
  # take precedence over corridor shells at their shared entrance.
  return (int('Floor' in r['path'].split('/')[-1]),si,-ri)
 overlaps=0
 for a,b in sorted(candidate_pairs):
  pa,pb=priority(a),priority(b)
  if pa is None or pb is None:continue
  if pa<pb:a,b=b,a;pa,pb=pb,pa
  ta,na,da,ga=data(*a);tb,nb,db,gb=data(*b)
  for key in ga.keys()&gb.keys():
   ai=np.array(ga[key]);bi=np.array(gb[key]);axis=np.argmax(abs(na[ai[0]]));axes=[k for k in range(3) if k!=axis]
   polysA=shapely.polygons(ta[ai][:,:,axes]);polysB=polysA if a==b else shapely.polygons(tb[bi][:,:,axes])
   tree=STRtree(polysA)
   for jj,ii in tree.query(polysB).T:
    ia=int(ai[ii]);ib=int(bi[jj])
    if a==b and ia>=ib:continue
    # Plane compatibility at every vertex, not just rounded plane signatures.
    if np.max(np.abs(tb[ib]@na[ia]-da[ia]))>5e-5 or np.dot(na[ia],nb[ib])<.99999999:continue
    polyA=polysA[ii];polyB=polysB[jj]
    if polyA.intersection(polyB).area<1e-8:continue
    identity=(b[0],b[1]);existing=cut[identity].get(ib,polyB)
    remaining=existing.difference(polyA)
    if existing.area-remaining.area>1e-8:cut[identity][ib]=remaining;overlaps+=1
  # Each buffers entry is reused by other pairs; the survey has already excluded LOD competition.
 patches=[];removed_area=0;replacement_error=0
 for (ri,si),triangles in cut.items():
  t,n,dist,groups=data(ri,si);edits=[]
  for ti,polygon in sorted(triangles.items()):
   axis=np.argmax(abs(n[ti]));axes=[k for k in range(3) if k!=axis];original=t[ti][:,axes]
   original_area=shapely.Polygon(original).area;removed_area+=original_area-polygon.area
   bary=[]
   if not polygon.is_empty and polygon.area>1e-10:
    parts=shapely.get_parts(shapely.constrained_delaunay_triangles(polygon))
    replacement_error=max(replacement_error,abs(sum(p.area for p in parts)-polygon.area))
    A=np.column_stack((original[1]-original[0],original[2]-original[0]))
    for tri in parts:
     xy=np.array(tri.exterior.coords)[:3]
     bc=np.linalg.solve(A,(xy-original[0]).T).T
     weights=np.column_stack((1-bc.sum(1),bc))
     # Preserve the original triangle winding in projected space.
     det=lambda q:np.linalg.det(np.stack((q[1]-q[0],q[2]-q[0])))
     if det(xy)*det(original)<0:weights=weights[[0,2,1]]
     bary.append(weights.round(10).tolist())
   edits.append(dict(triangle=ti,bary=bary))
  if edits:patches.append(dict(renderer=ri,submesh=si,edits=edits))
 # Remove exact same-facing duplicates, including lower LODs, with the survey's
 # original indices. Degenerate triangles do not contribute visible coverage.
 bykey={x['mesh']:x for x in d['duplicateMeshes']}
 index={(p['renderer'],p['submesh']):p for p in patches}
 for ri,r in enumerate(rows):
  if r['skinned'] or r['mesh'] not in bykey:continue
  for si,ids in bykey[r['mesh']]['remove'].items():
   si=int(si);entry=index.get((ri,si))
   if entry is None:entry=dict(renderer=ri,submesh=si,edits=[]);patches.append(entry);index[(ri,si)]=entry
   known={e['triangle'] for e in entry['edits']}
   for ti in ids:
    if ti not in known:entry['edits'].append(dict(triangle=ti,bary=[]))
 result=dict(scene=d['scene'],rows=rows,patches=patches,overlapPairs=overlaps,projectedRemovedArea=removed_area,maxRetriangulationAreaError=replacement_error)
 (PLAN/path.name).write_text(json.dumps(result),encoding='utf-8')
 print(json.dumps(dict(scene=path.stem,renderers=len({p['renderer'] for p in patches}),triangles=sum(len(p['edits']) for p in patches),overlaps=overlaps,area=removed_area,maxAreaError=replacement_error)),flush=True)
if __name__=='__main__':
 for p in sorted(OUT.glob('*.json')):
  if len(sys.argv)>1 and sys.argv[1] not in p.stem:continue
  if not (PLAN/p.name).exists():plan(p)
