"""Geometric candidates, not an automatic visual defect verdict.
Skip mutually exclusive lower LODs for cross-renderer checks. Test projected
polygon intersection (not merely AABB overlap), same-facing near-coplanar faces.
"""
from pathlib import Path
import sys,json,struct,collections,time,os
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
CACHE=ROOT/'Unity/After_Seconds_Build_V0.01/Temp/ZFightingReview'
sys.path.insert(0,str(CACHE/'deps'))
import shapely
from shapely import STRtree
OUT=ROOT/'SourceAssets/ZFightingReview'/os.environ.get('ZF_OUTPUT','results')
OUT.mkdir(exist_ok=True)
sys.stdout.reconfigure(encoding='utf-8')

def mesh(key):
    with (CACHE/'meshes'/f'{key}.bin').open('rb') as f:
        n,s=struct.unpack('<ii',f.read(8));v=np.frombuffer(f.read(n*12),'<f4').reshape(-1,3).astype('float64');subs=[]
        for i in range(s):
            topology,count=struct.unpack('<ii',f.read(8));ids=np.frombuffer(f.read(count*4),'<i4')
            subs.append(ids.reshape(-1,3) if topology==0 else np.empty((0,3),dtype=int))
    return v,subs

def audit(path):
    d=json.loads(path.read_text()); rows=d['rows'];planes=collections.defaultdict(list);dups=[];internal=[];total=0;seen={};duplicate_renderers=[]
    for ri,r in enumerate(rows):
        key=r['mesh'];v,subs=mesh(key)
        # Exact duplicates with the same winding: backfaces are not duplicates.
        if key not in seen:
            dup={};count=0
            for si,ix in enumerate(subs):
                if not len(ix):continue
                xyz=np.round(v[ix]*1e5).astype('int64')
                start=np.lexsort((xyz[:,:,2],xyz[:,:,1],xyz[:,:,0]),axis=1)[:,0]
                xyz=np.take_along_axis(xyz,((np.arange(3)[None,:]+start[:,None])%3)[:,:,None],axis=1)
                flat=np.ascontiguousarray(xyz.reshape(-1,9))
                _,first,inv,counts=np.unique(flat,axis=0,return_index=True,return_inverse=True,return_counts=True)
                removal=np.where(np.arange(len(ix))!=first[inv])[0]
                if len(removal):dup[str(si)]=removal.tolist();count+=len(removal)
            seen[key]=count
            if count:dups.append(dict(mesh=key,asset=r['asset'],remove=dup,count=count))
        if r['level']>0 or r['skinned']:continue
        m=np.array(r['matrix']).reshape(4,4);world=v@m[:3,:3].T+m[:3,3]
        total+=sum(len(ix) for ix in subs)
        for si,ix in enumerate(subs):
            if not len(ix):continue
            ts=world[ix];normal=np.cross(ts[:,1]-ts[:,0],ts[:,2]-ts[:,0]);length=np.linalg.norm(normal,axis=1)
            valid=length>0.01 # face area >= .005 m2; smaller details separately sampled visually
            ts=ts[valid];normal=normal[valid]/length[valid,None]
            if not len(ts):continue
            dist=np.sum(normal*ts[:,0],axis=1)
            keys=np.column_stack((np.round(normal*10000),np.round(dist*1000))).astype('int64')
            unique,inv=np.unique(keys,axis=0,return_inverse=True)
            order=np.argsort(inv);splits=np.split(order,np.cumsum(np.bincount(inv))[:-1])
            for k,inds in zip(unique,splits):
                triangles=ts[inds];axis=int(np.argmax(abs(normal[inds[0]])));axes=[i for i in range(3) if i!=axis]
                polys=shapely.polygons(triangles[:,:,axes]);areas=shapely.area(polys)
                poly=shapely.union_all(polys)
                if poly.is_empty or poly.area<.005:continue
                # Same-renderer overlap includes separately authored parts combined in an FBX.
                excess=float(areas.sum()-poly.area)
                if excess>.02:internal.append(dict(renderer=ri,submesh=si,excess=excess,point=triangles.mean((0,1)).tolist(),normal=normal[inds[0]].tolist(),plane=k.tolist()))
                planes[tuple(k)].append((ri,si,poly,triangles.mean((0,1)),normal[inds[0]]))
    pairs={}
    for key,patches in planes.items():
        if len(patches)<2:continue
        polys=[p[2] for p in patches];tree=STRtree(polys)
        for a,b in tree.query(polys).T:
            if a>=b:continue
            pa,pb=patches[a],patches[b]
            if pa[0]==pb[0] and pa[1]==pb[1]:continue
            area=pa[2].intersection(pb[2]).area
            if area<.005:continue
            identity=(pa[0],pa[1],pb[0],pb[1]);centroid=pa[2].intersection(pb[2]).centroid
            normal=pa[4];axis=int(np.argmax(abs(normal)));axes=[i for i in range(3) if i!=axis];point=np.zeros(3);point[axes]=[centroid.x,centroid.y]
            point[axis]=(float(np.dot(normal,pa[3]))-np.dot(normal[axes],point[axes]))/normal[axis]
            entry=pairs.setdefault(identity,dict(a=pa[0],sa=pa[1],b=pb[0],sb=pb[1],area=0,maxArea=0,point=[],normal=[]))
            entry['area']+=float(area)
            if area>entry['maxArea']:entry.update(maxArea=float(area),point=point.tolist(),normal=normal.tolist())
    result=dict(scene=d['scene'],renderers=len(rows),triangles=total,errors=d['errors'],duplicateMeshes=dups,internal=sorted(internal,key=lambda p:-p['excess']),overlaps=sorted(pairs.values(),key=lambda p:-p['area']),rows=rows,cameras=d['cameras'])
    (OUT/(path.stem+'.json')).write_text(json.dumps(result),encoding='utf-8')
    print(json.dumps(dict(scene=path.stem,triangles=total,duplicateMeshCount=len(dups),duplicateTriangles=sum(x['count'] for x in dups),internal=len(internal),overlaps=len(pairs))),flush=True)

if __name__=='__main__':
    for p in sorted(CACHE.glob('*.json')):
        if len(sys.argv)>1 and (('Circular' in p.stem) if sys.argv[1]=='Old' else sys.argv[1] not in p.stem):continue
        if (OUT/p.name).exists():continue
        audit(p)
