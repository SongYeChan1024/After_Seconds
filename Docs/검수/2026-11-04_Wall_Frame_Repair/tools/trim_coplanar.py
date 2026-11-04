"""같은 방향 공면의 중복 시각 면만 차집합으로 정리한다. 원본 좌표·UV/UV2 보존."""
# 의사코드: 전층 원본 메시 → 월드 평면/우선순위 분류 → 겹친 삼각형 차집합
# → 면적 보존 검사 → 원래 로컬 공간으로 보간 → 파생 시각 메시 출력.
import json,sys,math,random
from pathlib import Path
from collections import defaultdict
ROOT=Path(sys.argv[1]);AFTER='--after' in sys.argv
PLANE=0.0005;MIN_TRI_AREA=.00005;MIN_OVERLAP=1e-8;MIN_REPAIR_AREA=.0001

def signed_area(p):return sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))*.5 if len(p)>2 else 0
def area(p):return abs(signed_area(p))
def clean(p):
 out=[]
 for v in p:
  if not out or math.dist(v,out[-1])>1e-9:out.append(v)
 if len(out)>1 and math.dist(out[0],out[-1])<1e-9:out.pop()
 return out if len(out)>2 and area(out)>1e-12 else []
def halfplane(poly,a,b,sign,inside=True):
 if not poly:return []
 def side(p):return sign*((b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]))
 result=[]
 for i,p in enumerate(poly):
  q=poly[(i+1)%len(poly)];sp,sq=side(p),side(q)
  if (sp>=0 if inside else sp<=0):result.append(p)
  if (sp>0 and sq<0) or (sp<0 and sq>0):
   t=sp/(sp-sq);result.append([p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])])
 return clean(result)
def intersection(poly,cutter):
 sign=1 if signed_area(cutter)>0 else -1
 for i,a in enumerate(cutter):
  poly=halfplane(poly,a,cutter[(i+1)%len(cutter)],sign)
  if not poly:break
 return poly
def difference(poly,cutter):
 if area(intersection(poly,cutter))<MIN_OVERLAP:return [poly]
 sign=1 if signed_area(cutter)>0 else -1
 result=[];remaining=poly
 for i,a in enumerate(cutter):
  b=cutter[(i+1)%len(cutter)];outside=halfplane(remaining,a,b,sign,False)
  if outside:result.append(outside)
  remaining=halfplane(remaining,a,b,sign,True)
  if not remaining:break
 return result
def self_test():
 tri=[[0.,0.],[2.,0.],[0.,2.]]
 for cutter,expected in [([[0,0],[1,0],[0,1]],1.5),([[-1,-1],[5,-1],[-1,5]],0),([[3,3],[4,3],[3,4]],2),([[2,0],[4,0],[2,2]],2)]:
  assert abs(sum(area(p) for p in difference(tri,cutter))-expected)<1e-9
 rng=random.Random(641104)
 for _ in range(150):
  c=[[rng.uniform(-1,3),rng.uniform(-1,3)] for i in range(3)]
  if area(c)<1e-7:continue
  assert abs(sum(area(p) for p in difference(tri,c))+area(intersection(tri,c))-area(tri))<1e-7
 print('GEOMETRY_SELF_TEST_OK',flush=True)

def bbox(p):return [min(v[0] for v in p),min(v[1] for v in p),max(v[0] for v in p),max(v[1] for v in p)]
def intersects(a,b):return a[0]<b[2]-1e-8 and b[0]<a[2]-1e-8 and a[1]<b[3]-1e-8 and b[1]<a[3]-1e-8
def transform(v,m):return [sum(m[r*4+c]*v[c] for c in range(3))+m[r*4+3] for r in range(3)]
def priority(path,axis,sign):
 n=path.lower();value=0
 if '/frame_' in n:value+=10000
 elif 'door' in n:value+=5000
 if 'visualjunction' in n:value+=1800
 if 'rebuiltarchitecturevisual' in n:value+=1000
 # B4 근접 3시점 검수: 이 벽은 연속된 외피를 유지하고 접속 복도 쪽을 자른다.
 if 'room03_observationcorridor/wall_n/' in n:value+=2000
 if axis==1:
  if sign>0 and any(x in n for x in ('floor','deck','landing')):value+=600
  if sign<0 and 'ceiling' in n:value+=600
 elif 'wall' in n:value+=600
 return value

def collect(geometry,instances):
 records=[];by_instance=defaultdict(dict)
 for inst in instances:
  mesh=geometry[inst['mesh']];world=[transform(v,inst['matrix']) for v in mesh['vertices']]
  for slot,indices in enumerate(mesh['submeshes']):
   for offset in range(0,len(indices),3):
    ids=indices[offset:offset+3];p=[world[i] for i in ids]
    u=[p[1][i]-p[0][i] for i in range(3)];v=[p[2][i]-p[0][i] for i in range(3)]
    cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];length=math.sqrt(sum(x*x for x in cross))
    if length*.5<MIN_TRI_AREA:continue
    axis=max(range(3),key=lambda i:abs(cross[i]));sign=1 if cross[axis]>0 else -1
    if abs(cross[axis])/length<.99999 or max(q[axis] for q in p)-min(q[axis] for q in p)>.00005:continue
    axes=[i for i in range(3) if i!=axis];poly=[[q[i] for i in axes] for q in p];plane=sum(q[axis] for q in p)/3
    rec={'inst':inst,'slot':slot,'offset':offset,'ids':ids,'poly':poly,'bbox':bbox(poly),'axis':axis,'axes':axes,'sign':sign,'plane':plane,'priority':priority(inst['path'],axis,sign),'fragments':[poly]}
    records.append(rec);by_instance[inst['id']][(slot,offset)]=rec
 return records,by_instance

def process(records,repair):
 groups=defaultdict(list);pairs=defaultdict(float)
 for t in sorted(records,key=lambda r:(-r['priority'],r['inst']['path'],r['slot'],r['offset'])):
  inst=t['inst'];key=(inst['scene'],t['axis'],t['sign'],round(t['plane']/PLANE));cutters=[]
  for delta in (-1,0,1):
   for other in groups[(key[0],key[1],key[2],key[3]+delta)]:
    if inst['id']==other['inst']['id'] or abs(t['plane']-other['plane'])>PLANE or not intersects(t['bbox'],other['bbox']):continue
    overlap=area(intersection(t['poly'],other['poly']))
    if overlap<MIN_OVERLAP:continue
    names=tuple(sorted([inst['path'],other['inst']['path']]));pairs[(inst['scene'],)+names]+=overlap;cutters.append(other)
  if repair:
   original_area=area(t['poly']);fragments=t['fragments'];removed=0
   for cutter in cutters:
    new=[]
    for p in fragments:new.extend(difference(p,cutter['poly']))
    new_area=sum(area(p) for p in new);old_area=sum(area(p) for p in fragments)
    if new_area>old_area+1e-7:raise RuntimeError('Clipping increased area')
    removed+=old_area-new_area;fragments=new
    if not fragments:break
   t['fragments']=fragments;t['removed']=max(0,removed)
   if abs(sum(area(p) for p in fragments)+removed-original_area)>1e-6:raise RuntimeError('Area conservation failed')
  groups[key].append(t)
 return [{'scene':k[0],'a':k[1],'b':k[2],'area':v} for k,v in sorted(pairs.items(),key=lambda x:x[1],reverse=True) if v>.002]

def bary(point,tri):
 a,b,c=tri;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
 u=((b[1]-c[1])*(point[0]-c[0])+(c[0]-b[0])*(point[1]-c[1]))/den
 v=((c[1]-a[1])*(point[0]-c[0])+(a[0]-c[0])*(point[1]-c[1]))/den
 return [u,v,1-u-v]

def write_mesh(inst,mesh,records):
 out={k:[v[:] for v in mesh.get(k,[])] for k in ('vertices','normals','uv','uv2','tangents')};out['submeshes']=[]
 removed=0;changed=0
 for slot,indices in enumerate(mesh['submeshes']):
  result=[]
  for offset in range(0,len(indices),3):
   t=records.get((slot,offset))
   if not t or t.get('removed',0)<MIN_OVERLAP:result.extend(indices[offset:offset+3]);continue
   removed+=t['removed'];changed+=1
   for poly in t['fragments']:
    new_ids=[]
    for p in poly:
     weights=bary(p,t['poly']);idx=len(out['vertices']);new_ids.append(idx)
     for attribute in ('vertices','normals','uv','uv2','tangents'):
      values=mesh.get(attribute,[])
      if len(values)!=len(mesh['vertices']):continue
      value=[sum(values[t['ids'][j]][i]*weights[j] for j in range(3)) for i in range(len(values[0]))]
      if attribute=='normals':
       length=math.sqrt(sum(x*x for x in value));value=[x/length for x in value] if length>1e-10 else values[t['ids'][0]][:]
      if attribute=='tangents':
       length=math.sqrt(sum(x*x for x in value[:3]));value=[x/length for x in value[:3]]+[1 if value[3]>=0 else -1] if length>1e-10 else values[t['ids'][0]][:]
      out[attribute].append(value)
    for i in range(1,len(new_ids)-1):
     if area([poly[0],poly[i],poly[i+1]])>1e-11:result.extend([new_ids[0],new_ids[i],new_ids[i+1]])
  out['submeshes'].append(result)
 return out,removed,changed

self_test()
geometry=json.loads((ROOT/('geometry_after.json' if AFTER else 'geometry.json')).read_text(encoding='utf-8-sig'))
instances=json.loads((ROOT/('instances_after.json' if AFTER else 'instances.json')).read_text(encoding='utf-8-sig'))
triangles,per_instance=collect(geometry,instances);pairs=process(triangles,not AFTER)
if AFTER:
 (ROOT/'remaining_overlaps.json').write_text(json.dumps({'trianglesChecked':len(triangles),'pairs':pairs,'count':len(pairs)},indent=2),encoding='utf-8')
 print('REMAINING_OVERLAPS',len(pairs),flush=True)
else:
 output=ROOT/'output';output.mkdir(exist_ok=True);manifest=[]
 for inst in instances:
  records=per_instance[inst['id']]
  if not any(t.get('removed',0)>MIN_OVERLAP for t in records.values()):continue
  mesh,removed,count=write_mesh(inst,geometry[inst['mesh']],records)
  if removed<MIN_REPAIR_AREA:continue
  (output/(inst['id']+'.json')).write_text(json.dumps(mesh,separators=(',',':')),encoding='utf-8')
  manifest.append({**{k:inst[k] for k in ('id','scene','floor','path','mesh')},'removedArea':removed,'modifiedTriangles':count,'retainedAreaChecked':True})
 (ROOT/'trim_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
 (ROOT/'overlaps_before.json').write_text(json.dumps({'trianglesChecked':len(triangles),'pairs':pairs,'count':len(pairs)},indent=2),encoding='utf-8')
 print('TRIM_PREPARED',len(manifest),'PAIR_CANDIDATES',len(pairs),flush=True)
