"""Fit extra work bays without intersecting existing furniture or portal lanes."""
import json,math
from pathlib import Path
H=Path(__file__).resolve().parent;data=json.loads((H/'plan.json').read_text(encoding='utf-8'));bounds={m['name']:m for m in json.loads((H/'survey.json').read_text(encoding='utf-8'))['models']}
def poly(p,margin=.06):
 b=bounds[p['model']];a=math.radians(p['yaw']);c,s=math.cos(a),math.sin(a);x,_,z=p['position'];cx,_,cz=b['center'];w,_,d=b['size'];return[(x+c*(cx+xx*(w/2+margin))+s*(cz+zz*(d/2+margin)),z-s*(cx+xx*(w/2+margin))+c*(cz+zz*(d/2+margin))) for xx,zz in [(-1,-1),(1,-1),(1,1),(-1,1)]]
def overlap(a,b):
 for pts in [a,b]:
  for i in range(4):
   p,q=pts[i],pts[(i+1)%4];v=(q[1]-p[1],p[0]-q[0]);aa=[x*v[0]+z*v[1] for x,z in a];bb=[x*v[0]+z*v[1] for x,z in b]
   if max(aa)<min(bb) or max(bb)<min(aa):return False
 return True
extra=[];changes=[]
for p in data['placements']:
 if p['model']=='RD_PrivacyCurtain':p['yaw']=90;changes.append(p)
def attempt(room,model,x,z,yaw):
 p=dict(id=f'{room}_Detail_{len(extra):03}_{model}',room=room,model='RD_'+model,position=[x,0,z],yaw=yaw,collision=True);q=poly(p);r=data['rooms'][room];b=bounds[p['model']]
 if max(math.hypot(xx,zz) for xx,zz in q)>math.sqrt(r['r']**2-(b['center'][1]+b['size'][1]/2)**2)-.08:return False
 for old in data['placements']+extra:
  if old['room']!=room:continue
  if overlap(q,poly(old)):return False
 # Door approach rectangles remain open to the room's inner circulation area.
 for door in r['doors']:
  a=math.radians(door['angle']);f=(math.cos(a),math.sin(a));right=(-f[1],f[0]);lane=[(f[0]*d+right[0]*w,f[1]*d+right[1]*w) for d,w in [(3.8,-1.5),(r['r']+.2,-1.5),(r['r']+.2,1.5),(3.8,1.5)]]
  if overlap(q,lane):return False
 extra.append(p);return True
for room,model,positions in [('W01','TransferNurseDesk',[(0,-2,0),(0,1,0)]),('W02','TransferNurseDesk',[(0,1,0),(0,-2,0)]),('E01','ReceivingIsland',[(0,-2,0),(-2,-1,90)]),('E02','MealAssemblyIsland',[(0,-2,0)]),('E03','DeconChangeBench',[(0,0,0)]),('N01','CentralOperatorDesk',[(-2.6,.3,180),(0,.3,180),(2.6,.3,180)]),('S01','ProcessControlBay',[(-3.8,1.8,90),(3.8,2,270)])]:
 for x,z,yaw in positions:
  if attempt(room,model,x,z,yaw) and room!='N01':break
groups={'C03':['ValveManifold','ProcessControlBay','FilterBank','MedicalGasStation','ValveManifold','ServiceWorkBay'],'C04':['ProcessControlBay','FilterBank'],'W01':['LinenRack','SupplyRack','WaitingBench'],'W02':['WaitingBench','LinenRack','SupplyRack'],'W03':['MedicalGasStation','ServiceWorkBay','PPEDispenser'],'E01':['LinenRack','SupplyRack','ArchiveCaseRack','LinenReturnCart'],'E02':['MealTransportCart','ServiceWorkBay','SupplyRack'],'E03':['BootDryingRack','PPEDispenser','ServiceWorkBay'],'N01':['ArchiveCaseRack','ProcessControlBay','DataRecorderRack','ServiceWorkBay','ElectricalSwitchgear','ArchiveCaseRack'],'S01':['ArchiveCaseRack','ServiceWorkBay','MedicalGasStation','FilterBank','TestControlConsole']}
unplaced=[]
for room,models in groups.items():
 r=data['rooms'][room]
 for model in models:
  b=bounds['RD_'+model];rad=math.sqrt(r['r']**2-(b['center'][1]+b['size'][1]/2)**2)-b['size'][2]/2-.18;done=False
  for offset in [0,-.4,-.8]:
   for a in range(0,360,5):
    t=math.radians(a);x,z=(rad+offset)*math.cos(t),(rad+offset)*math.sin(t)
    if attempt(room,model,x,z,math.degrees(math.atan2(-x,-z))):done=True;break
   if done:break
  if not done:unplaced.append((room,model))
data['placements'].extend(extra);(H/'plan.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');(H/'detail_plan.json').write_text(json.dumps(dict(extra=extra,changes=changes,unplaced=unplaced),ensure_ascii=False,indent=2),encoding='utf-8');print('Added',len(extra),'total',len(data['placements']),'could not fit',unplaced)
