from pathlib import Path
import json,hashlib,os
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-13_1F_EnvironmentalStory'
before=json.loads((O/'protected_before.json').read_text());changed=[]
for p,digest in before.items():
 f=R/p
 if not f.exists() or hashlib.sha256(f.read_bytes()).hexdigest()!=digest:changed.append(p)
b=json.loads((O/'before_transforms.json').read_text());a=json.loads((O/'after_transforms.json').read_text());am={q['path']:q for q in a};transforms=[q['path'] for q in b if q!=am.get(q['path'])]
temp=Path(os.environ['LOCALAPPDATA'])/'Temp/AfterSeconds_EnvironmentalStory_20261113/before';E=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/1F'
guids={name:(temp/name).read_text()==(E/name).read_text() for name in ['AE_WallIvy.fbx.meta','AEWeathering.hlsl.meta']}
report=dict(protectedFiles=len(before),changedProtected=changed,beforeTransforms=len(b),afterTransforms=len(a),changedTransforms=transforms,colliders=sum(len(q['colliders']) for q in a),preservedMeta=guids)
(O/'audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
