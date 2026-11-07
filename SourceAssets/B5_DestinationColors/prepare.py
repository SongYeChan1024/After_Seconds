from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/검수/2026-11-08_B5_DestinationColors';O.mkdir(parents=True,exist_ok=True)
if (H/'baseline.json').exists():raise SystemExit('Baseline exists')
A=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds'
(H/'baseline.json').write_text(json.dumps({str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in A.rglob('*') if p.is_file()},indent=2),encoding='utf-8')
S=R/'SourceAssets/C02_SecurityRefine'
for n in ['Prepare','Inspect','Capture','Walk']:
 s=(S/(n+'.cs')).read_text(encoding='utf-8').replace('C02Refine'+n,'Destination'+n).replace('2026-11-08_C02_Refine','2026-11-08_B5_DestinationColors').replace('AfterSeconds_C02_Refine_','AfterSeconds_DestinationColors_')
 (H/(n+'.cs')).write_text(s,encoding='utf-8')
print('Destination-color baseline and isolated authoring tools prepared')
