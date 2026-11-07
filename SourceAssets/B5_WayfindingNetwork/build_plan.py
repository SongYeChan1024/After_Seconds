"""B5 전체 목적지·안내선 제작 배치안. 작성자 송예찬. Unity 씬은 변경하지 않는다."""
from pathlib import Path
import json, math, heapq, hashlib

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'Docs/도면/Decision/원형공동/B5_안내체계'
OUT.mkdir(parents=True,exist_ok=True)
source=ROOT/'Docs/도면/Decision/원형공동/facility_layout.json'
data=json.loads(source.read_text(encoding='utf-8'))
floor=next(f for f in data['floors'] if f['id']=='B5')
survey=json.loads((HERE/'survey.json').read_text(encoding='utf-8'))
names={'C01':'실험동','C02':'보안관제동','C03':'냉각설비동','C04':'유틸리티동','W01':'제1격리생활동','W02':'제2격리생활동','W03':'의료검사동','E01':'물자보급동','E02':'급식지원동','E03':'제염동','N01':'중앙관제동','S01':'폐쇄시험동','VA':'계단 A','VB':'계단 B','VL':'화물 승강기'}
sectors={'C':'중앙 실험·운영','W':'격리·의료','E':'생활지원','N':'중앙관제','S':'폐쇄시험'}
rooms={r['id']:dict(code=r['id'],name=names[r['id']],sector=r['id'][0] if r['kind']=='cavern' else 'CORE',position=[r['x'],-r['v']],radius=r['r'],kind=r['kind'],restricted=r['id']=='S01') for r in floor['rooms']}
codes={'R1':dict(name='직원 이동',color='#DEE6E9',width=.29,pattern='double'), 'S1':dict(name='시료 이송',color='#5E9C9A',width=.09,pattern='square'), 'M1':dict(name='설비 정비',color='#BC9B5A',width=.075,pattern='dashed')}
sectorplan=json.loads((source.parent/'B5_섹터/sector_plan.json').read_text(encoding='utf-8'))
routes={'R1':[f'T{i:02}' for i in range(1,20) if i not in [3,4,11]],'S1':['T11','T03','T04','T06'],'M1':['T04','T06']}
edges={}
for t in sectorplan['corridor_area']['segments']:
 code=t['id'][3:];members=[k for k in codes if code in routes[k]]
 offsets={c:0.0 for c in members}
 if code=='T04':offsets={'S1':-.30,'M1':.30}
 if code=='T06':offsets={'R1':-.60,'S1':0.,'M1':.60}
 edges[code]=dict(code=code,a=t['from_room'],b=t['to_room'],p=[t['p'][0],-t['p'][1]],q=[t['q'][0],-t['q'][1]],width=t['width'],lanes=offsets)

def add(a,b):return [a[0]+b[0],a[1]+b[1]]
def sub(a,b):return [a[0]-b[0],a[1]-b[1]]
def mul(a,t):return [a[0]*t,a[1]*t]
def norm(a):return mul(a,1/math.hypot(*a))
def dist(a,b):return math.dist(a,b)
def segdist(p,a,b):
 d=sub(b,a);dd=d[0]**2+d[1]**2
 if dd==0:return dist(p,a)
 t=max(0,min(1,((p[0]-a[0])*d[0]+(p[1]-a[1])*d[1])/dd))
 return dist(p,add(a,mul(d,t)))

paths=[];ports={r:{c:[] for c in codes} for r in rooms};labels=[]
for e in edges.values():
 d=norm(sub(e['q'],e['p']));right=[d[1],-d[0]];length=dist(e['p'],e['q']);e['length']=length
 for code,offset in e['lanes'].items():
  p=add(e['p'],mul(right,offset));q=add(e['q'],mul(right,offset))
  paths.append(dict(id=e['code']+'_'+code,code=code,kind='corridor',edge=e['code'],points=[p,q]))
  ports[e['a']][code].append(dict(edge=e['code'],point=p));ports[e['b']][code].append(dict(edge=e['code'],point=q))
 for reverse in [False,True]:
  a,b=(e['q'],e['p']) if reverse else (e['p'],e['q']);direction=norm(sub(b,a));side=[direction[1],-direction[0]];dest=e['a'] if reverse else e['b']
  for end in ['departure','arrival']:
   distance=2.5 if end=='departure' else length-2.5
   center=add(add(a,mul(direction,distance)),mul(side,1.15))
   labels.append(dict(id=f"{e['code']}_{dest}_{end}",edge=e['code'],target=dest,name=names[dest],sector=rooms[dest]['sector'],position=center,forward=direction,width=.60,length=1.40,kind=end,restricted=rooms[dest]['restricted']))

class RoomGrid:
 def __init__(self,room):
  self.room=room;self.g=next(g for g in survey['rooms'] if g['id']==room);self.free={(i,j) for j,row in enumerate(self.g['rows']) for i,c in enumerate(row) if c=='.'};self.reserved=[]
 def world(self,n):return [self.g['x0']+n[0]*self.g['step'],self.g['z0']+n[1]*self.g['step']]
 def usable(self,code):
  return {n for n in self.free if all(segdist(self.world(n),a,b)>=((codes[code]['width']+codes[other]['width'])/2+.18) for other,a,b in self.reserved if other!=code)}
 def nearest(self,p,nodes):return min(nodes,key=lambda n:dist(self.world(n),p))
 def astar(self,a,b,nodes):
  queue=[(0,0,a)];cost={a:0};parent={};done=set()
  while queue:
   _,_,n=heapq.heappop(queue)
   if n in done:continue
   done.add(n)
   if n==b:
    route=[n]
    while n in parent:n=parent[n];route.append(n)
    return route[::-1]
   for dx,dz in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
    q=(n[0]+dx,n[1]+dz)
    if q not in nodes or q in done:continue
    if dx and dz and ((n[0]+dx,n[1]) not in nodes or (n[0],n[1]+dz) not in nodes):continue
    value=cost[n]+math.hypot(dx,dz)
    if value<cost.get(q,1e9):cost[q]=value;parent[q]=n;heapq.heappush(queue,(value+dist(q,b),value,q))
  raise ValueError(f'No non-overlapping path in {self.room}: {a} -> {b}')
 def route(self,code,a,b):
  nodes=self.usable(code);na=self.nearest(a,nodes);nb=self.nearest(b,nodes)
  if dist(self.world(na),a)>.46:raise ValueError(f'Port blocked {self.room} {code} {dist(self.world(na),a):.3f}')
  pts=[a]+[self.world(n) for n in self.astar(na,nb,nodes)]+[b]
  pts=[p for i,p in enumerate(pts) if i==0 or dist(p,pts[i-1])>.0001]
  # Collapse exactly collinear grid runs only; do not shortcut across sampled obstacles.
  clean=[pts[0]]
  for i in range(1,len(pts)-1):
   a1=norm(sub(pts[i],clean[-1]));b1=norm(sub(pts[i+1],pts[i]))
   if dist(a1,b1)>.00001:clean.append(pts[i])
  clean.append(pts[-1])
  def clear(a,b):
   n=max(1,math.ceil(dist(a,b)/.06))
   for i in range(n+1):
    q=add(a,mul(sub(b,a),i/n));cell=(round((q[0]-self.g['x0'])/self.g['step']),round((q[1]-self.g['z0'])/self.g['step']))
    if cell not in nodes:return False
    if any(segdist(q,x,y)<(codes[code]['width']+codes[other]['width'])/2+.18 for other,x,y in self.reserved if other!=code):return False
   return True
  simplified=[clean[0]];i=0
  while i<len(clean)-1:
   j=len(clean)-1
   while j>i+1 and not clear(clean[i],clean[j]):j-=1
   simplified.append(clean[j]);i=j
  self.reserved.extend((code,a,b) for a,b in zip(simplified,simplified[1:]));return simplified

failures=[]
for rid,r in rooms.items():
 if rid=='S01':continue # Two closed entries are destinations, never a through-route.
 grid=RoomGrid(rid)
 for code in ['M1','S1','R1']:
  pp=ports[rid][code]
  if not pp:continue
  try:
   if len(pp)==1:
    start=pp[0]['point'];toward=norm(sub(r['position'],start));target=add(start,mul(toward,1.5 if code!='R1' else 2.0));available=grid.usable(code);target=grid.world(grid.nearest(target,available))
    pts=grid.route(code,start,target);paths.append(dict(id=f'{rid}_{code}_arrival',code=code,kind='room',room=rid,points=pts,terminal=True))
   else:
    # Connect ports in an acyclic chain; same-purpose junctions are intentional.
    ordered=sorted(pp,key=lambda p:math.atan2(p['point'][1]-r['position'][1],p['point'][0]-r['position'][0]))
    for j in range(1,len(ordered)):
     pts=grid.route(code,ordered[j-1]['point'],ordered[j]['point']);paths.append(dict(id=f'{rid}_{code}_{j}',code=code,kind='room',room=rid,points=pts,terminal=False))
  except ValueError as e:failures.append(str(e))

plan=dict(title='B5 구역·목적지·전체 안내선 배치안 V0.01',author='송예찬',date='2026-11-07',status='도면 검토안 / Unity 미반영',basis='사용자 승인 5섹터 구분; 용도별 선 유지 방식은 질문 응답 전 기존 체계를 적용한 제안',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),coordinate='Unity world X/Z; floor Y=-82m',sectors=sectors,destinations=list(rooms.values()),route_codes=codes,route_edges=routes,corridors=list(edges.values()),paths=paths,labels=labels,room_routing_failures=failures,notes=['구역 이름은 바닥 안내선 옆에 표기. 별도 구역 명판 없음.','S01은 폐쇄 목적지: 양쪽 입구에서 끝내고 내부 통과 경로로 사용하지 않음.','R1은 직원 접근 네트워크이며 모든 가지가 출구를 뜻하지 않음. 계단 A/B·화물 승강기는 별도 목적지.','S1은 W03 의료검사동–C01 실험동–C03/C04 통과–VL 화물 인계 구역.','M1은 VL–C04 유틸리티동–C03 냉각설비동.','같은 노선의 접속은 연결점, 서로 다른 노선의 교차·중첩은 금지.','C01 기존 R1 서측 연장은 새 배치안에서 S1 의료/시료 동선과 대조해 교체할 항목.','도면의 노선 연결과 실제 층간 구조·게임 동작 완성은 별도.'])
(OUT/'wayfinding_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(paths=len(paths),labels=len(labels),rooms=len(rooms),corridors=len(edges),room_routing_failures=failures),ensure_ascii=False))
