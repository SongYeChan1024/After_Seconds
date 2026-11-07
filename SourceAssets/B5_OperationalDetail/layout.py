"""Purpose-specific placement, preserving shell, lighting and original assets. 송예찬."""
from pathlib import Path
import json,math
H=Path(__file__).resolve().parent;R=H.parents[1];p=json.loads((R/'SourceAssets/B5_SpatialRefinement/plan.json').read_text(encoding='utf-8'));out=[]
def add(room,model,x,z,yaw=0,y=0):out.append(dict(room=room,model='OD_'+model,position=[x,y,z],yaw=yaw,id=f'{room}_OD_{len(out):03}_{model}'))
def rim(room,model,a,dist):add(room,model,dist*math.cos(math.radians(a)),dist*math.sin(math.radians(a)),-90-a)
# Warehouse: central picking, eight perimeter stock bays, receiving and pallet staging.
for x in [-2.5,2.5]:
 for j,z in enumerate([-.7,1.2,3.1]):add('E01','WarehouseRack_'+str((j+(1 if x>0 else 0))%4),x,z,90 if x<0 else 270)
for j,a in enumerate([-120,-90,0,30,60,90,120,150]):rim('E01','WarehouseRack_'+str(j%4),a,6.65)
add('E01','ReceivingInspection',0,-3.55,180);add('E01','PalletLoad_0',-4.5,-2.65,15);add('E01','PalletLoad_1',4.5,-.9,15);add('E01','PalletTruck',.3,2.8,0)
# Closed meals arriving from external catering. No scratch-cooking island.
add('E02','SealedMealInspection',0,.2);add('E02','MealRegenerationCabinet',-3.4,2.7,90)
add('E02','SealedMealCart',-3.5,-2.6,90);add('E02','SealedMealCart',-.6,-3.4)
add('E02','ControlledNutritionBank',6,1.9,270);add('E02','NutritionTransferCart',5.4,-2.7,270)
# Dirty recovery and clean issue are on opposite sides of the wet bays.
add('E03','ClosedPPEReturn',-3.1,-4.25);add('E03','ContaminatedBagSealer',-5.0,-3.4,90)
add('E03','BootSoleWasher',3.2,-3.7,180)
add('E03','CleanPPEDispenser',-2.7,4.7,180);add('E03','DeconExitCheck',1.7,4.45,180)
for x in [-3.35,3.35]:add('E03','PipedDeconShower',x,0,90 if x<0 else 270)
# Replacements preserve proven control/rig positions exactly.
replacements={'SF_TestGantry':'InstrumentedTestRig','SF_TestControlConsole':'ExchangeControl','SF_ElectricalSwitchgear':'ElectricalSwitchgear','SF_ProcessControlBay':'ProcessControlBay'}
for q in p['placements']:
 if q['model'] in replacements:add(q['room'],replacements[q['model']],q['position'][0],q['position'][2],q['yaw'],q['position'][1])
add('VL','VL_FreightHoist',0,0)
add('E03','E03_WorkflowFloor',0,0)
data=dict(author='송예찬',placements=out,replaceAllProps=['E01'],replaceModels=list(replacements)+['SF_DeconShower','SF_MealAssemblyIsland','SF_MealPreparation','SF_MealTransportCart'],replaceLimited={'E03':['SF_PPEDispenser','SF_LinenReturnCart']},rooms=p['rooms'],tunnels=p['tunnels'])
# E02 cart replacements apply only E02; original W rooms stay intact.
(H/'layout.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(len(out),'new placements',len(set(q['model'] for q in out)),'models')
