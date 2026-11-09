from pathlib import Path
import json,math,copy,html
from PIL import Image,ImageDraw,ImageFont
from shapely.geometry import LineString
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-09_B3_StructureRepair'
master=R/'Docs/도면/Decision/원형공동/facility_layout.json';D=master.parent/'B3_구조보수';D.mkdir(exist_ok=True)
p=json.loads((H/'layout_after.json').read_text(encoding='utf-8'));rooms={r['id']:r for r in p['rooms']}
paths={a['id']:a['points'] for a in json.loads((O/'routes.json').read_text())}
def point(r,d):return [r['x']+d['x'],-49,-r['v']+d['z']]
def inside(rid,source,target):
 r=rooms[rid];ids=[d['id'] for d in r['doors']];a,b=ids.index(source),ids.index(target)
 def get(i):return [point(r,r['doors'][0])] if i==0 else paths[f'{rid}_door_0_{i}']
 aa,bb=get(a),get(b);common=0
 while common+1<min(len(aa),len(bb)) and math.dist(aa[common+1],bb[common+1])<.001:common+=1
 return aa[common:][::-1]+bb[common+1:]
def route(sequence):
 out=[];prev=None
 for a,b in zip(sequence,sequence[1:]):
  t=next(t for t in p['tunnels'] if {t['a'],t['b']}=={a,b})
  if prev:out.extend(inside(a,prev,t['id']))
  line=t.get('path',[t['p'],t['q']]);line=line if t['a']==a else line[::-1]
  out.extend([[v[0],-49,-v[1]] for v in line]);prev=t['id']
 cleaned=[]
 for q in out:
  if not cleaned or math.dist(q,cleaned[-1])>.001:cleaned.append(q)
 return [[q[0],-q[2]] for q in cleaned]
for field,seq in [('route','main'),('alternate','alt')]:
 p[field]=route(p[seq]);p[field+'_length']=round(sum(math.dist(a,b) for a,b in zip(p[field],p[field][1:])),2)
p['route_basis']='Unity CharacterController 통과 경로 연결. 시작/종료 코어의 첫/마지막 터널 출입점 기준. 게임 이동 UI가 아닌 도면 검토 경로.'
p['sourceVersion']='Decision V0.05 / B3 구조·밀도 보수 V0.01';p['asBuiltVersion']='V0.01'
data=json.loads(master.read_text(encoding='utf-8-sig'));other=copy.deepcopy([f for f in data['floors'] if f['id']!='B3'])
b=next(f for f in data['floors'] if f['id']=='B3');t=next(t for t in b['tunnels'] if t['id']=='B3-T08');t.update(copy.deepcopy(next(t for t in p['tunnels'] if t['id']=='B3-T08')))
for r in b['rooms']:
 if r['id'] in ['C03','C04']:r['doors']=rooms[r['id']]['doors']
for key in ['route','route_length','alternate','alternate_length','route_basis']:b[key]=p[key]
b['as_built_layout']='B3_구조보수/as_built_layout.json';b['as_built_note']='2026-11-09 B3 구조·밀도 보수: T08 곡선 우회, C03/C04 개구부 변경, 프랍302배치. 기존 제작목록·초기 PDF보다 이 배치와 도면을 우선한다.'
data['title']='After Seconds 원형 공동 제작 설계 V0.05';data['date']='2026-11-09';data['status']='B5/B4 역할 확정 유지 / B3 T08 구조 및 현재 배치·검수 경로 동기화'
assert other==[f for f in data['floors'] if f['id']!='B3']
master.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for target in [H/'layout_after.json',R/'SourceAssets/B3_FullFloor/layout.json',D/'as_built_layout.json']:target.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
W,HH=1900,1540;scale=6.5;ox,oy=950,740
def pt(x,v):return (ox+x*scale,oy+v*scale)
im=Image.new('RGB',(W,HH),'#f4f7f9');dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18);small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15);title=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',30)
dr.text((45,32),'B3 시료층 구조와 설비 배치 V0.01',font=title,fill='#173545');dr.text((45,80),'공동 13 · 코어 3 · 복도 22 · 프랍 302배치 | 작성자 송예찬 | 2026-11-09',font=font,fill='#355466')
dr.text((45,112),'T08 곡선 우회 · C03/C04 출입부 분리 · 원래 공동 위치와 연결 관계 유지',font=font,fill='#355466')
for t in p['tunnels']:
 line=t.get('path',[t['p'],t['q']]);outline=LineString(line).buffer(t['w']/2,cap_style=2,quad_segs=12)
 dr.polygon([pt(*v) for v in outline.exterior.coords],fill='#dca674' if t['id']=='B3-T08' else '#c5d1d9')
 mid=line[len(line)//2] if len(line)>2 else [(line[0][0]+line[1][0])/2,(line[0][1]+line[1][1])/2];dr.text(pt(*mid),t['id'].split('-')[1],font=small,fill='#526574')
for r in p['rooms']:
 x,v,rad=r['x'],r['v'],r['r'];dr.ellipse([pt(x-rad,v-rad),pt(x+rad,v+rad)],fill='#e6edf1',outline='#7796a7',width=2)
for q in p['placements']:
 if q['role']=='BenchAccessory':continue
 r=rooms[q['room']];x,y,z=q['position'];cx,cy,cz=q['center'];w,h,d=q['size'];ang=math.radians(q['yaw']);verts=[]
 for xx,zz in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]:
  xx+=cx;zz+=cz;rx=xx*math.cos(ang)+zz*math.sin(ang);rz=-xx*math.sin(ang)+zz*math.cos(ang);verts.append(pt(r['x']+x+rx,r['v']-z-rz))
 dr.polygon(verts,fill='#497387' if '_Dense_' in q['name'] else '#96acb7')
for field,color in [('alternate','#b97239'),('route','#139b97')]:dr.line([pt(*v) for v in p[field]],fill=color,width=3)
for r in p['rooms']:
 x,v=pt(r['x'],r['v']+r['r']+1.8);dr.text((x-18,v),r['id'],font=font,fill='#142f3d')
dr.text((45,HH-155),'회청색: 기존 설비   진한 청회색: 추가 설비   청록: 주 검수 경로   갈색: T08 우회 검수 경로',font=font,fill='#355466')
dr.text((45,HH-118),'문과 장비 앞 접근 경로를 실제 Unity 충돌로 검수했습니다. 경로선은 도면에만 표시합니다.',font=font,fill='#355466')
dr.text((45,HH-81),'기본 소등: C01 / C02 / W01 / W02 / E03   ·   프랍 수는 조립체 기준이며 랙 안 용기·서랍은 포함하지 않습니다.',font=font,fill='#355466')
im.save(D/'B3_구조배치도.png');im.save(O/'as_built_plan.png')
(D/'README.md').write_text('''# B3 구조와 배치 보수 V0.01

작성자 송예찬 · 2026-11-09

T02/T08와 T07/T08의 접합 외피 중첩을 T08 남쪽 곡선 우회로 해소했다. C03 폐기·환복과 C04 제염 공동의 개구부·문틀·마감·조명, 복도 리브·설비·바닥 안내선을 함께 맞췄다. 13공동·3코어·22복도의 연결 관계는 유지한다.

[현재 구조·배치도](B3_구조배치도.png)와 [배치 JSON](as_built_layout.json)은 실제 Unity 보수와 일치한다. 주·우회 경로는 실제 통행 검수 경로를 연결한 도면용 선이며 게임에 표시하지 않았다. 프랍은150개에서302개로 늘리고 기존14개를 재배치했다. 내부 랙 열, 저온 저장 열, 검수·포장 작업대, 제염·멸균·폐기 구역을 구분했다.

기존 Excel V0.03은 수급 목록으로 보존했다. 초기 PDF·SVG·생성 조감도의 T08 직선 연결과 실내 배치보다 이 자료를 우선한다. 다른 층의 좌표와 도면은 변경하지 않았다. 모델·게임 기능의 최종 사용자 검수와 문·스위치·AI·층 전환 구현은 별도다.

[검수 결과](../../../../Review/2026-11-09_B3_StructureRepair/Review.md) · [실제 화면](../../../../Review/2026-11-09_B3_StructureRepair/review.html)

## 변경 기록

- V0.01: T08 구조 보수와302배치·실제 검수 경로 반영.
''',encoding='utf-8')
print('Decision V0.05, B3 as-built synced; routes',p['route_length'],p['alternate_length'])
