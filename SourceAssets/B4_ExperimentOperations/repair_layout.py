"""Repack work-side access after native CharacterController review; no old assets moved."""
from pathlib import Path
import json,math,copy
H=Path(__file__).resolve().parent
scope={'__file__':str(H/'layout.py')}
exec((H/'layout.py').read_text(encoding='utf8').split('primary={')[0],scope)
turn,rect,sat,geom,old=(scope[k] for k in ['turn','rect','sat','geom','old'])
plan=json.loads((H/'layout.json').read_text(encoding='utf8'))
assert not (H/'layout_before_access_repair.json').exists()
(H/'layout_before_access_repair.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8')
changes=[]
# This narrow records room already has perimeter infrastructure. Leave its cart
# circulation open instead of retaining a freestanding emergency cabinet centrally.
removed=[p for p in plan['newPlacements'] if p['room']=='C05' and p['model']=='BX_SafetyEquipment']
for p in removed:
 plan['newPlacements'].remove(p)
 plan['workspaces']=[w for w in plan['workspaces'] if w['name']!=p['name']]
 changes.append({'name':p['name'],'remove':True,'reason':'기록 공동 중앙 운반 통로 확보; 설비 에셋은 라이브러리에 보존'})
def move(code,index,x,z,yaw):
 p=next(p for p in plan['newPlacements'] if p['room']==code and p['name'].endswith(f'_{index:02}'))
 before=copy.deepcopy(p);p['position']=[x,0,z];p['yaw']=yaw
 cx,cy,cz=p['center'];w,h,d=p['size'];dx,dz=turn(cx,cz+d/2+.57,yaw)
 p['access']=[x+dx,0,z+dz]
 space=next(q for q in plan['workspaces'] if q['name']==p['name']);space['point']=p['access'];space['polygon']=rect(x+dx,z+dz,min(w,1.8),.9,yaw)
 poly=geom(p['model'],x,z,yaw)
 blocks=old[code]+[{'name':q['name'],'poly':geom(q['model'],q['position'][0],q['position'][2],q['yaw'])} for q in plan['newPlacements'] if q['room']==code and q!=p]
 overlaps=[b['name'] for b in blocks if sat(poly,b['poly'],.10)]
 if overlaps:raise RuntimeError((p['name'],overlaps))
 changes.append({'name':p['name'],'beforePosition':before['position'],'position':p['position'],'yaw':yaw,'remove':False})
move('C05',9,0,-2.5,0)
move('W01',12,-.3,.1,0)
move('E02',3,-5.5,-2.8,90)
move('E03',9,-.5,3.3,180)
(H/'layout.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(H/'access_repairs.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(changes,ensure_ascii=False))
