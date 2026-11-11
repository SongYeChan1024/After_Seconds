import bpy,bmesh,json,struct,numpy as np
from pathlib import Path
H=Path(__file__).resolve().parent
def read(key):
 with (H/(key+'.bin')).open('rb') as f:
  n,s=struct.unpack('<ii',f.read(8));v=np.frombuffer(f.read(n*12),dtype='<f4').reshape(-1,3).copy();uv=np.frombuffer(f.read(n*8),dtype='<f4').reshape(-1,2).copy();ix=[];mi=[]
  for k in range(s):
   count=struct.unpack('<i',f.read(4))[0];tri=np.frombuffer(f.read(count*4),dtype='<i4').reshape(-1,3);ix.extend(tri.tolist());mi.extend([k]*len(tri))
 return v,uv,np.array(ix),mi
if __name__=='__main__':
 report=[]
 for row in json.loads((H/'export.json').read_text()):
  v,uv,ix,mi=read(row['key']);m=bpy.data.meshes.new(row['key']);m.from_pydata(v.tolist(),[],ix.tolist());bm=bmesh.new();bm.from_mesh(m);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
  boundary=[e for e in bm.edges if e.is_boundary];nonman=[e for e in bm.edges if not e.is_manifold and not e.is_boundary];bad=[f for f in bm.faces if f.calc_area()<1e-10]
  rr=dict(key=row['key'],min=v.min(0).tolist(),max=v.max(0).tolist(),welded=len(bm.verts),boundary=len(boundary),nonmanifold=len(nonman),degenerate=len(bad));report.append(rr);print(rr,flush=True)
  bm.free();bpy.data.meshes.remove(m)
 (H/'topology.json').write_text(json.dumps(report,indent=2))
