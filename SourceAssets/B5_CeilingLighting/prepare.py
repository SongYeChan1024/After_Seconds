from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2]
H=Path(__file__).resolve().parent
P=R/'Unity/After_Seconds_Build_V0.01'
baseline=H/'baseline.json'
if baseline.exists(): raise RuntimeError('Baseline exists')
files={str(p.relative_to(P)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for d in ['Assets','Packages','ProjectSettings'] for p in (P/d).rglob('*') if p.is_file()}
baseline.write_text(json.dumps(files,ensure_ascii=False,indent=2),encoding='utf-8')
print('Baseline files:',len(files))
