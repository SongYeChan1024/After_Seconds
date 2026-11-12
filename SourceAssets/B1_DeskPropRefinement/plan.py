from pathlib import Path
import json,math,collections
H=Path(__file__).resolve().parent;R=H.parents[1]
p=json.loads((R/'SourceAssets/B1_InteriorRedesign/layout.json').read_text(encoding='utf8'));count=collections.Counter();targets=[]
for q in p['placements']:
 m=q['model'];room=q['room'];i=count[(room,m)];count[(room,m)]+=1;v=None
 if m=='BL_ResearchDesk':
  # No two workstations in a six-desk room use the same tabletop arrangement.
  numbers={'C01':[0,1,2,3,4,5],'W01':[6,7,8,9,10,11],'N01':[2,7,4,9,0,11],'C02':[1,8],'C03':[3,10],'E02':[5],'S01':[6]}
  v='DP_Desk_'+str(numbers[room][i]).zfill(2)
 elif m in ['SF_SC_OperatorDesk_A','SF_SC_OperatorDesk_B']:v='DP_Security_'+m[-1]
 elif m=='SF_SC_IncidentReview':v='DP_Review_'+room
 elif m=='SF_BriefingTable':v='DP_Comparison_'+room+'_'+str(i)
 elif m=='BL_ConferenceTable':v='DP_Meeting'
 elif m=='BL_DiningSet':v='DP_Dining_'+str(i)
 elif m=='SF_SC_RadioDutyStation':v='DP_Radio_'+room
 elif m in ['SF_VitalCart','SF_UltrasoundCart']:v='DP_'+('VitalCart' if m=='SF_VitalCart' else 'UltrasoundCart')
 elif m=='BL_HandheldRecorder':v='DP_Recorder'
 if v:targets.append({'name':q['name'],'room':room,'source':m,'variant':v})
relocations=[]
for q in p['placements']:
 if q['model']!='BL_HandheldRecorder':continue
 desks=[d for d in p['placements'] if d['room']==q['room'] and d['model']=='BL_ResearchDesk'];desk=min(desks,key=lambda d:(d['position'][0]-q['position'][0])**2+(d['position'][2]-q['position'][2])**2)
 a=math.radians(desk['yaw']);x=.57;z=-.245;pos=[desk['position'][0]+math.cos(a)*x+math.sin(a)*z,.824,desk['position'][2]-math.sin(a)*x+math.cos(a)*z]
 relocations.append({'name':q['name'],'room':q['room'],'desk':desk['name'],'position':pos,'yaw':desk['yaw']+(7 if len(relocations)%2 else -9)})
result={'version':'V0.01','targets':targets,'relocations':relocations,'variants':len(set(q['variant'] for q in targets)),'scope':'B1 tabletop props; preserve furniture placement, original geometry below worktop, colliders, architecture and game code'}
(H/'plan.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print('Targets',len(targets),'variants',result['variants'])
