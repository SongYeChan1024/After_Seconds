from pathlib import Path
import json,math
H=Path(__file__).resolve().parent;p=json.loads((H/'layout.json').read_text(encoding='utf8'))
assert not any(q['name'].endswith('_관측석내부') for q in p['workspaces'])
for a in p['newPlacements']:
 if a['model'] not in ['BX_ObservationBooth','BX_PrecisionPlatform']:continue
 z=.6 if a['model']=='BX_ObservationBooth' else 0
 yaw=math.radians(a['yaw']);point=[a['position'][0]+z*math.sin(yaw),0,a['position'][2]+z*math.cos(yaw)]
 p['workspaces'].append({'name':a['name']+('_관측석내부' if z else '_실험체계측위치'),'room':a['room'],'point':point,'roleCheck':True})
(H/'layout.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Work positions',len(p['workspaces']))
