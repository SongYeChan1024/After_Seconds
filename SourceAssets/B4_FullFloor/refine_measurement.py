from pathlib import Path
import json,copy
H=Path(__file__).resolve().parent;p=json.loads((H/'layout.json').read_text(encoding='utf-8'));changes=[]
def move(room,index,x,z,yaw):
 a=next(a for a in p['placements'] if a['room']==room and a['name'].endswith(f'_{index:02}'))
 changes.append({'name':a['name'],'before':copy.deepcopy(a),'position':[x,0,z],'yaw':yaw});a.update(position=[x,0,z],yaw=yaw)
move('E01',1,0,6.15,180)
for desk,chair,x in [(2,3,-1.3),(4,5,1.3)]:
 move('E01',desk,x,3.5,180);move('E01',chair,x,2.48,0)
move('E01',8,3.1,3.6,90)
move('W01',1,-1.2,3.25,165)
move('W01',7,1.8,4.2,165)
move('W02',1,-3.85,.575,96)
move('W02',8,-4.8,-1.8,6)
move('S01',1,1.01,-4.85,351)
(H/'layout.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(H/'refinements_measurement.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
s=(H/'Refine.cs').read_text(encoding='utf-8').replace('BFFRefine','BFFMeasureRefine').replace('refinements.json','refinements_measurement.json')
(H/'MeasureRefine.cs').write_text(s,encoding='utf-8')
print(len(changes))
