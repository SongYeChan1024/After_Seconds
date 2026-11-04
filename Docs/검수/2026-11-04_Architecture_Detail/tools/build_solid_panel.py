"""겹치는 조립 면이 없는 닫힌 단일 프로파일 패널을 제작하고 검증된 배치 변환을 재사용한다."""
import json, shutil, math
from pathlib import Path
import numpy as np
repo=Path(__file__).resolve().parents[4];tmp=repo/'tmp/ArchitectureDetail_20261104';out=repo/'Docs/검수/2026-11-04_Architecture_Detail';path=tmp/'panel_template.json'
old=json.loads(path.read_text());backup=tmp/'panel_template.before_solid_profile.json'
if not backup.exists():shutil.copyfile(path,backup)
ov=np.asarray(old['vertices']);reference=json.loads(backup.read_text());rv=np.asarray(reference['vertices']);ouv=np.asarray(reference['uv']);oldtri=np.asarray(reference['submeshes'][0]).reshape(-1,3)
def sample(start,end):
 ids=oldtri[start:end];cross=np.cross(rv[ids[:,1]]-rv[ids[:,0]],rv[ids[:,2]]-rv[ids[:,0]]);i=int(np.argmax(np.linalg.norm(cross,axis=1)));return ouv[ids[i]].mean(axis=0)
paint=sample(236,280);rubber=sample(0,44);steel=sample(280,308)
physical=[];normals=[];uv=[];indices=[]
scale=np.array([1.,1.2,.0176])
def triangle(a,b,c,spot):
 a,b,c=np.asarray(a),np.asarray(b),np.asarray(c);n=np.cross(b-a,c-a);n/=np.linalg.norm(n);n=n*scale;n/=np.linalg.norm(n)
 for p in (a,b,c):
  physical.append((p/scale).tolist());normals.append(n.tolist());uv.append((spot+np.array([p[0],p[1]])*.00005).tolist());indices.append(len(indices))
def ring(w,h,z,corner):
 return np.array([[-w/2+corner,-h/2,z],[w/2-corner,-h/2,z],[w/2,-h/2+corner,z],[w/2,h/2-corner,z],[w/2-corner,h/2,z],[-w/2+corner,h/2,z],[-w/2,h/2-corner,z],[-w/2,-h/2+corner,z]])
rings=[ring(.994,1.194,-.0088,.009),ring(1.,1.2,.004,.009),ring(.988,1.188,.0088,.009),ring(.950,1.150,.0088,.009),ring(.940,1.140,.0035,.009)]
for level in range(4):
 a,b=rings[level],rings[level+1];spot=rubber if level==3 else paint
 for i in range(8):
  j=(i+1)%8;triangle(a[i],a[j],b[j],spot);triangle(a[i],b[j],b[i],spot)
for i in range(8):
 j=(i+1)%8;triangle([0,0,-.0088],rings[0][j],rings[0][i],rubber);triangle([0,0,.0035],rings[-1][i],rings[-1][j],paint)
for x in (-.455,.455):
 for y in (-.545,.545):
  lower=np.array([[x+.005*math.cos(i*math.pi/4),y+.005*math.sin(i*math.pi/4),.0025] for i in range(8)])
  upper=lower.copy();upper[:,2]=.006
  for i in range(8):
   j=(i+1)%8;triangle(lower[i],lower[j],upper[j],steel);triangle(lower[i],upper[j],upper[i],steel);triangle([x,y,.006],upper[i],upper[j],steel);triangle([x,y,.0025],lower[j],lower[i],steel)
new={'vertices':physical,'normals':normals,'uv':uv,'uv2':[],'submeshes':[indices],'front':'+Z','sourceBounds':old['sourceBounds'],'materials':old['materials']}
manifest=json.loads((tmp/'panel_manifest.json').read_text());nv=np.asarray(physical);nn=np.asarray(normals);nu=np.asarray(uv);fit=np.c_[ov,np.ones(len(ov))];newfit=np.c_[nv,np.ones(len(nv))];changed=0
for item in manifest:
 file=tmp/'panels'/(item['id']+'.json');data=json.loads(file.read_text());v=np.asarray(data['vertices']);count=item['panels'];columns=math.ceil(math.sqrt(count));rows=math.ceil(count/columns);verts=[];norms=[];uvs=[];uv2=[];ii=[]
 assert len(v)==len(ov)*count
 for number in range(count):
  block=v[number*len(ov):(number+1)*len(ov)];coeff=np.linalg.lstsq(fit,block,rcond=None)[0];assert np.max(abs(fit@coeff-block))<1e-5
  points=newfit@coeff;normal=nn@np.linalg.inv(coeff[:3,:]).T;normal/=np.linalg.norm(normal,axis=1)[:,None]
  base=len(verts);verts.extend(points.tolist());norms.extend(normal.tolist());uvs.extend(uv);uv2.extend(((nu*.9+.05+np.array([number%columns,number//columns]))/np.array([columns,rows])).tolist());ii.extend(i+base for i in indices)
 data={'vertices':verts,'normals':norms,'uv':uvs,'uv2':uv2,'submeshes':[ii]};file.write_text(json.dumps(data,separators=(',',':')));item['triangles']=len(ii)//3;changed+=1
path.write_text(json.dumps(new,separators=(',',':')));(tmp/'panel_manifest.json').write_text(json.dumps(manifest,indent=2))
report={'method':'One watertight stepped panel body plus four embedded bolt heads; no separately overlapping frame and center plate','trianglesPerPanel':len(indices)//3,'verticesPerPanel':len(physical),'updatedWallMeshes':changed,'panels':sum(i['panels'] for i in manifest),'retainedPlacementTransforms':True,'constantPaintPatchUV':True,'normalMapRequired':False}
(out/'panel_solid_profile.json').write_text(json.dumps(report,indent=2));print('SOLID_PROFILE_READY',json.dumps(report),flush=True)

