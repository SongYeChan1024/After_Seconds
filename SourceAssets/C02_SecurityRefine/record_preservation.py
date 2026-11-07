from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/검수/2026-11-08_C02_Refine';baseline=json.loads((H/'baseline.json').read_text(encoding='utf-8'))
modelnames=['SC_OperatorDesk_A','SC_OperatorDesk_B','SC_VideoWall','SC_IncidentReview','SC_RadioDutyStation','SC_NetworkRack','SC_RecorderRack','SC_UPSRack']
prefix='Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/'
allowed={prefix+'01.Scenes/Stage/Level_B5_Circular.unity'}
for name in modelnames:
 for suffix in ['.fbx','.fbx.meta']:allowed.add(prefix+'05.Model/Props/B5/'+name+suffix)
for i in range(1,6):
 for suffix in ['.png','.png.meta']:allowed.add(prefix+f'05.Model/Props/B5/Textures/SC_Display_{i:02}'+suffix)
changed=[];missing=[]
for rel,sha in baseline.items():
 p=R/rel
 if not p.exists():missing.append(rel)
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=sha:changed.append(rel)
unexpected=[p for p in changed if p.replace('\\','/') not in allowed]
result=dict(baselineFiles=len(baseline),preservedFiles=len(baseline)-len(changed)-len(missing),changed=changed,missing=missing,unexpected=unexpected)
(O/'file_preservation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=True));assert not missing and not unexpected
