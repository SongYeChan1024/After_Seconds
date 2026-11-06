"""Widen corridor strips while keeping rooms, door openings and stair core dimensions.
Author 송예찬. Baseline JSON is immutable; outputs are repeatable from that baseline.
"""
import json,math,hashlib,copy
from pathlib import Path
SRC=Path(__file__).resolve().parent; REPO=SRC.parents[1]
def interp(x,points):
 for (a,b),(c,d) in zip(points,points[1:]):
  if x<=c:return b+(x-a)*(d-b)/(c-a)
 return x+points[-1][1]-points[-1][0]
def fx(u):
 delta=0
 for a in (0,19,36):
  if u<a:return u+delta
  if u<=a+3:return interp(u,[(a,a+delta),(a+.75,a+delta+1.35),(a+2.25,a+delta+2.85),(a+3,a+delta+4.2)])
  delta+=1.2
 return u+delta
def fy(v,core=False):
 if core:return v+.8
 return interp(v,[(0,0),(.75,1.15),(3.25,3.65),(4,4.8),(24,24.8),(24.75,26.15),(26.25,27.65),(27,29)])
def pt(p):return [round(fx(p[0]),6),round(fy(p[1],p[0]>=38.99),6)]
def transform(obj):
 if isinstance(obj,dict):
  result={k:transform(v) for k,v in obj.items()}
  if 'x' in obj and 'y' in obj:
   u,v=obj['x'],obj['y'];core=(u+obj.get('w',0)/2)>=38.99
   result['x']=round(fx(u),6);result['y']=round(fy(v,core),6)
   if 'w' in obj:result['w']=round(fx(u+obj['w'])-fx(u),6)
   if 'h' in obj:result['h']=round(fy(v+obj['h'],core)-fy(v,core),6)
  return result
 if isinstance(obj,list):
  if len(obj)==2 and all(isinstance(v,(int,float)) for v in obj):return pt(obj)
  if len(obj)>1 and all(isinstance(p,list) and len(p)==2 and all(isinstance(n,(int,float)) for n in p) for p in obj):
   result=[pt(p) for p in obj]
   # Crossing a rigid core must pass the door orthogonally before turning in the corridor.
   for i,(a,b) in enumerate(zip(obj,obj[1:])):
    if a[0]<39<=b[0]:result[i][1]=result[i+1][1]
    elif b[0]<39<=a[0]:result[i+1][1]=result[i][1]
   return result
  return [transform(v) for v in obj]
 return obj
def main():
 plan=transform(json.loads((SRC/'layout_before.json').read_text(encoding='utf-8-sig')))
 plan['title']='After Seconds 터널·돔 구조 층별 평면 V0.04'
 plan['status']='B5/B4/B3 복도 확장 제작 기준. B2/B1/1F는 수직 코어를 맞춘 설계 가안.'
 for f in plan['floors']:
  f['version']='V0.04';f['width']=51.6;f['height']=max(r['y']+r['h'] for r in f['rooms'])
  f['notes'].append('복도 4.2m / 북측 4.8m. 방·문 폭·계단 치수 유지, 코어는 동쪽 3.6m·남쪽 0.8m 이동.')
  f['notes'].append('큰 차폐벽 철거. 벽 쪽 설비 엄폐 / 터널 천장 / 주요실 돔 / 문 앞 연결부를 함께 설계.')
  f['blocks']=[b for b in f['blocks'] if b.get('kind')!='baffle']
  f['serviceBays']=[]
  for i,(u,v,angle) in enumerate(((13.85,.42,0),(27.55,4.38,180),(12.35,25.22,0),(28.55,28.58,180))):
   f['serviceBays'].append(dict(id='EQ'+str(i+1),x=u,y=v,yaw=angle,prefab='SD_PPEStation',scale=[1.1,1.12,1],width=1.06,depth=.45,height=1.85,role='벽면 설비 엄폐'))
   f['blocks'].append(dict(name='설비 '+str(i+1),x=u-.53,y=v-.225,w=1.06,h=.45,kind='equipment'))
  for room in f['rooms']:
   rid=room['id'];kind=room['kind']
   if kind=='corridor':room['roof']=dict(kind='barrel',crown=4,spring=4-.045-(min(room['w'],room['h'])/2-.16),shell=.13,ribDepth=.44,ribThickness=.24)
   elif kind=='room' and not rid.startswith('SUP'):
    crown=7.2 if f['floor']=='B5' and rid=='A' else 5.2 if f['floor']=='B5' else 5.6 if f['floor']=='B4' and rid=='D' else 4.4 if f['floor']=='B3' and rid=='D' else 4.8
    spring=5.95 if f['floor']=='B5' and rid=='A' else 4.5 if f['floor']=='B4' and rid=='D' else 3.6 if f['floor']=='B3' and rid=='A' else 3.1
    room['roof']=dict(kind='dome',crown=crown,spring=spring,shell=.13)
   else:room['roof']=dict(kind='retained',reason='계단·리프트 단면과 지원실 기능 유지')
 dest=REPO/'Docs/도면/잠입_탐색/layout.json';dest.write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
 routes=transform(json.loads((SRC/'routes_before.json').read_text(encoding='utf-8-sig')))
 routes['version']='V0.04';routes['sourceSHA256']=hashlib.sha256(dest.read_bytes()).hexdigest().upper()
 for route in routes['routes']:
  for leg in route['legs']:leg['length']=round(sum(math.dist(a,b) for a,b in zip(leg['points'],leg['points'][1:])),3)
  route['walkingMetres']=round(sum(l['length'] for l in route['legs']),1)
 (dest.parent/'플레이어_예상이동/player_routes.json').write_text(json.dumps(routes,ensure_ascii=False,indent=2),encoding='utf-8')
 print('Wide layout written, 6 floors, 18 routes')
if __name__=='__main__':main()
