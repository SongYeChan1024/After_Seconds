"""Resolve reused assets without modifying their importers or shared materials."""
from pathlib import Path
import json
H=Path(__file__).resolve().parent
p=json.loads((H/'plan.json').read_text(encoding='utf8'));inv=json.loads((H/'before.json').read_text(encoding='utf8'))['inventory'];models=json.loads((H/'models_props.json').read_text(encoding='utf8'))
reuse={'OfficeDesk_A':'DP_Desk_00','OfficeDesk_B':'DP_Desk_05','OfficeDesk_C':'DP_Desk_09','ShippingDesk':'DP_Desk_04','SecurityDesk':'DP_Desk_07','BreakTable':'DP_Dining_1','MotorBench':'BC_MaintenanceBench','ToolCart':'BC_ToolTrolley'}
for name,src in reuse.items():
 q=next(q for q in inv if Path(q['asset']).stem==src);models[name]=dict(asset=q['asset'],center=q['center'],size=q['size'],reuse=True,triangles=[t['triangles'] for t in q['meshes']])
for q in list(p['placements']):
 if 'Desk' in q['model']:
  import math
  yaw=q['yaw'];dx=math.sin(math.radians(yaw))*.92;dz=math.cos(math.radians(yaw))*.92
  p['placements'].append(dict(name=q['name']+'_Chair',room=q['room'],model='OfficeChair',position=[q['position'][0]+dx,0,q['position'][2]+dz],yaw=(yaw+180)%360,access=False,scale=1))
for q in p['placements']:
 assert q['model'] in models,q['model'];q.update({k:models[q['model']][k] for k in ['asset','center','size']})
 if q['name']=='F1_C01_PartsRack_10':q['position']=[-8,0,11]
 # Exact support surface coordinates for handheld dressing; desks retain their own varied accessories.
 if q['model']=='HardHat':
  support={'C01':[-5,.23,-1],'C02':[18,.23,-13],'C04':[-17.8,1.35,25.8],'C03':[-33.3,1.035,-29.4]}
  if q['room'] in ['C01','C02']:
   # Place on top of the corresponding packed shipping loads, not on machinery controls.
   support['C01']=[-22,1.035,-1];support['C02']=[18,1.035,-13]
  q['position']=support[q['room']];q['position'][1]-=models['HardHat']['center'][1]-models['HardHat']['size'][1]/2
 if q['model']=='HandRadio':
  q['position']={'C02':[19.62,.815,-1.0],'C03':[-30.38,.815,-22.3],'C04':[-13.62,.815,28.8]}[q['room']]
 if q['model']=='ShippingRecord':
  q['position']={'C01':[-19,1.12,5],'C02':[29,.94,-12],'C04':[-16.62,.815,21.3],'C03':[-34.25,1.0,-29.4]}[q['room']]
p['models']=models
(H/'resolved.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf8')
print({'placements':len(p['placements']),'reusedModels':len(reuse),'newModels':len(models)-len(reuse)})
