"""Floor-directed furnishing schedule. Author 송예찬."""
import json,math
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
floor=next(f for f in json.loads((R/'Docs/도면/Decision/원형공동/facility_layout.json').read_text(encoding='utf-8'))['floors'] if f['id']=='B5')
rooms={r['id']:dict(r,position=[r['x'],-82,-r['v']]) for r in floor['rooms']}
for r in rooms.values():
 r['doors']=[]
 for t in floor['tunnels']:
  if r['id'] in (t['a'],t['b']):
   p=t['p'] if t['a']==r['id'] else t['q'];r['doors'].append(dict(id=t['id'],angle=math.degrees(math.atan2(-p[1]+r['v'],p[0]-r['x'])),position=[p[0],-p[1]]))
placements=[]
def add(room,model,x,z,yaw=0,y=0,collision=True):
 placements.append(dict(id=f'{room}_{len(placements):03}_{model}',room=room,model='RD_'+model,position=[round(x,5),y,round(z,5)],yaw=round(yaw,4),collision=collision))
def delta(a,b):return abs((a-b+180)%360-180)
def ring(room,models,occupied=None,start=90):
 r=rooms[room];used=list(occupied or []);rad=r['r']-1.42
 for model in models:
  candidates=[a for a in range(0,360,5) if all(delta(a,d['angle'])>math.degrees(math.asin(min(1,3.3/rad))) for d in r['doors']) and all(delta(a,b)>spacing for b,spacing in used)]
  if not candidates:raise RuntimeError((room,model,used))
  a=min(candidates,key=lambda a:delta(a,start));used.append((a,40 if model=='CentralVideoWall' else 21 if r['r']>=9 else 26));t=math.radians(a);x,z=rad*math.cos(t),rad*math.sin(t);add(room,model,x,z,math.degrees(math.atan2(-x,-z)));start=(a+30)%360
 return used
for room in ['W01','W02']:
 r=rooms[room];rad=r['r']-2.45;used=[]
 for desired in [80,165,255,340]:
  choices=[a for a in range(0,360,5) if all(delta(a,d['angle'])>37 for d in r['doors']) and all(delta(a,b)>49 for b in used)]
  a=min(choices,key=lambda a:delta(a,desired));used.append(a);a=math.radians(a);x,z=rad*math.cos(a),rad*math.sin(a);yaw=math.atan2(-x,-z)
  for model,xx,zz in [('LivingAlcove',0,0),('LivingBed',-.85,-.18),('LivingDesk',.82,-.92),('SanitaryBasin',.86,.43),('PersonalLocker',-.85,1.47)]:
   add(room,model,x+math.cos(yaw)*xx+math.sin(yaw)*zz,z-math.sin(yaw)*xx+math.cos(yaw)*zz,math.degrees(yaw))
 # A compact clinical/transfer island is offset from the inter-portal through route.
 ring(room,['IsolationNurseStation','LinenReturnCart','MealTransportCart'],[(a,30) for a in used],start=0)
ring('W03',['MedicalSterilizer','MedicationCabinet','DoubleWashSink','LinenRack','SupplyRack','WaitingBench','VitalCart','UltrasoundCart','IsolationNurseStation'])
for x in [-2.5,2.5]:
 add('W03','MedicalBed',x,3.0,180);add('W03','PrivacyCurtain',x-1.1,3,0);add('W03','ExaminationLight',x+.9,4,180)
ring('C03',['PlateHeatExchanger','TwinCoolingPump','ExpansionVessel','ElectricalSwitchgear','PlateHeatExchanger','MaintenanceBench','ExpansionVessel','AirHandlingUnit','SupplyRack','TwinCoolingPump'])
ring('C04',['AirHandlingUnit','ElectricalSwitchgear','MaintenanceBench'],start=90)
ring('E01',['LinenRack','SupplyRack','PersonalLocker','LinenRack','SealedSupplyCrates','LinenReturnCart','SupplyRack','MaintenanceBench'])
add('E01','SealedSupplyCrates',0,2.8,90);add('E01','LinenReturnCart',-2.6,2.4,90)
ring('E02',['ColdStorage','MealPreparation','DoubleWashSink','TrayDishwasher','MealTransportCart','SupplyRack','ColdStorage','WaitingBench','MealPreparation'])
add('E02','MealTransportCart',-1.8,3.2,90);add('E02','SealedSupplyCrates',1.4,3.2)
ring('E03',['DeconShower','DeconShower','PPEDispenser','BootDryingRack','DoubleWashSink','LinenReturnCart','MedicationCabinet','PPEDispenser'])
ring('N01',['CentralVideoWall','DataRecorderRack','ElectricalSwitchgear','SupplyRack','DataRecorderRack','MaintenanceBench','WaitingBench'],start=90)
for x in [-2.6,0,2.6]:add('N01','CentralOperatorDesk',x,3.6,180)
ring('S01',['TestControlConsole','ElectricalSwitchgear','SealedSupplyCrates','MaintenanceBench','MedicationCabinet','DataRecorderRack','MedicalSterilizer','SealedSupplyCrates'])
add('S01','TestGantry',0,3.1);add('S01','MedicalBed',-3.1,3.4,90)
data=dict(author='송예찬',rooms=rooms,tunnels=floor['tunnels'],placements=placements,completedPreserved=['C01','C02','VA','B5-T01','B5-T02'],construction=[k for k in rooms if k not in ['C01','C02','VA']])
(H/'plan.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('Planned',len(placements),'placements /',len(data['construction']),'rooms and cores')
