from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[1]
p=json.loads((H/'props_before.json').read_text(encoding='utf8'));state=json.loads((H/'state_before.json').read_text(encoding='utf8'))
mapping={'BF_AnalysisBench':'LB_SignalAnalysisBench','BF_SensorWorkbench':'LB_OpticalCalibrationBench','SF_VitalCart':'LB_PhysiologyCart','BX_MobileAcquisitionCart':'LB_AcquisitionCart','BX_ElectrodePrepBench':'LB_ElectrodePrepBench','BX_CalibrationRack':'LB_DAQRack','BX_PrecisionPlatform':'LB_PrecisionPlatform','BX_AdaptiveTargetArray':'LB_AdaptiveTargetArray','BF_TrajectoryGantry':'LB_TrajectoryGantry','BX_LoadResistanceRig':'LB_LoadResistanceRig','PD_ProtocolTable':'LB_RecordWorkstation','BP_BenchKit_3':'LB_RecordKit'}
specific={'B4_E02_ResearchDesk_03':('LB_ElectronicsBench','B4_E02_ElectronicsBench_03'),'B4_E02_ResearchDesk_05':('LB_TestChamberBench','B4_E02_TestChamberBench_05'),'B4_E02_BriefingTable_07':('LB_SensorPrepBench','B4_E02_SensorPrepBench_07'),'B4_E02_CalibrationIsland':('LB_MetrologyIsland','B4_E02_MetrologyIsland')}
repl=[];disable=[]
for q in p:
 old=Path(q['asset']).stem;model=mapping.get(old);name=q['name']
 if name in specific:model,name=specific[name]
 if not model:continue
 repl.append(dict(id=q['id'],oldName=q['name'],name=name,oldAsset=q['asset'],model=model,collision=model not in ['LB_RecordWorkstation','LB_RecordKit'],p=q['p'],e=q['e']))
 if model not in ['LB_RecordWorkstation','LB_RecordKit']:
  disable += [c['id'] for c in q['children'] if 'BenchDetail' in c['name'] or 'BenchPedestal' in c['name']]
disable += [q['id'] for q in state if q['name'] in ['B4_E02_TaskChair_04','B4_E02_TaskChair_06']]
# Do not replace detail kits that are deliberately disabled with superseded desks.
repl=[q for q in repl if q['id'] not in disable]
plan=dict(replacements=repl,disable=disable)
(H/'changes.json').write_text(json.dumps(plan,indent=2),encoding='utf8')
layout=json.loads((R/'SourceAssets/B4_LayoutPolish/layout.json').read_text(encoding='utf8'))
for w in layout['workspaces']:
 if w['name'] in specific:w['name']=specific[w['name']][1]
(H/'layout.json').write_text(json.dumps(layout,indent=2,ensure_ascii=False),encoding='utf8')
s=(R/'SourceAssets/B4_DeskAndCollision/ReviewB4.cs').read_text(encoding='utf8').replace('CollisionReviewB4','LabWalk').replace('2026-11-09_FloorSurfaceWear','2026-11-09_B4_LabIdentity').replace('B4_LayoutPolish/layout.json','B4_LabIdentity/layout.json')
(H/'Walk.cs').write_text(s,encoding='utf8')
s=(R/'SourceAssets/B4_DeskAndCollision/Play.cs').read_text(encoding='utf8').replace('PassagePlay','LabPlay').replace('2026-11-09_FloorSurfaceWear','2026-11-09_B4_LabIdentity')
(H/'Play.cs').write_text(s,encoding='utf8')
print('Replacements',len(repl),'disabled',len(disable),'models',len(set(q['model'] for q in repl)))
