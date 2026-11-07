from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_T02_StairA';D.mkdir(parents=True,exist_ok=True)
if (H/'baseline.json').exists():raise SystemExit('Baseline exists')
A=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds'
(H/'baseline.json').write_text(json.dumps({str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in A.rglob('*') if p.is_file()},indent=2),encoding='utf-8')
S=H.parent/'B5_TwoDomeGuidance'
for n in ['Prepare','Inspect']:
    t=(S/(n+'.cs')).read_text(encoding='utf-8').replace('class TwoDome'+n,'class StairA'+n).replace('B5_TwoDomeGuidance','T02_StairA').replace('AfterSeconds_TwoDomeGuidance_','AfterSeconds_StairA_')
    (H/(n+'.cs')).write_text(t,encoding='utf-8')
print('Prepared protected asset/scene inspection')
