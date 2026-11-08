from pathlib import Path
import json,copy
H=Path(__file__).resolve().parent
p=json.loads((H/'layout.json').read_text(encoding='utf-8'))
changes=[]
def move(room,index,x,z,yaw):
 a=next(a for a in p['placements'] if a['room']==room and a['name'].endswith(f'_{index:02}'))
 changes.append({'name':a['name'],'before':copy.deepcopy(a),'position':[x,0,z],'yaw':yaw})
 a.update(position=[x,0,z],yaw=yaw)
def clone(room,index,name,x,z,yaw):
 a=copy.deepcopy(next(a for a in p['placements'] if a['room']==room and a['name'].endswith(f'_{index:02}')))
 changes.append({'name':name,'cloneFrom':a['name'],'position':[x,0,z],'yaw':yaw})
 a.update(name=name,position=[x,0,z],yaw=yaw);p['placements'].append(a)
for desk,chair,x in [(2,3,-2.6),(4,5,0),(6,7,2.6)]:
 move('N01',desk,x,5.0,180);move('N01',chair,x,3.98,0)
move('N01',12,-4.3,4.6,90)
clone('N01',12,'B4_N01_관제구획_가림_13',4.3,4.6,90)
for desk,chair,z in [(1,2,-3),(3,4,0),(5,6,3)]:
 move('E02',desk,5.2,z,270);move('E02',chair,4.18,z,90)
move('E02',11,5.3,-1.5,0)
clone('E02',11,'B4_E02_집중작업구획_12',5.3,1.5,0)
move('E02',7,.8,4.5,0)
clone('E02',2,'B4_E02_검토회의석_13',.8,5.8,180)
clone('E02',2,'B4_E02_검토회의석_14',.8,3.2,0)
move('C04',1,4.65,2.685,240)
move('C04',2,-1.54,-5.20,16.5)
p['refinement']='관제 화면을 바라보는 작업석, 연구 작업열/구획과 회의석, 분석 작업섬. 실제 충돌 이동 검수로 출입 동선 확인.'
(H/'layout.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(H/'refinements.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(len(changes),len(p['placements']))
