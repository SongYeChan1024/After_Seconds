import json,hashlib,math
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1];A=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds'
d=json.loads((R/'Docs/도면/Decision/원형공동/facility_layout.json').read_text(encoding='utf-8'))
f=next(f for f in d['floors'] if f['id']=='B2')
print('floor keys',list(f))
print('art',d['floor_art_direction']['B2'])
print('mezz',d['mezzanines'][0])
print('catalog',[c for c in d['catalog'] if c['code'] in ['P19','P20','P21']])
(H/'source_design.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
before={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['02.Scripts','07.Animator'] for p in (A/folder).rglob('*') if p.is_file()}
for p in (A/'01.Scenes').rglob('*.unity'):before[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
(H/'protected_before.json').write_text(json.dumps(before,indent=2),encoding='utf-8')
cat=json.loads((R/'SourceAssets/B3_FullFloor/catalog.json').read_text(encoding='utf-8'))
print('models',[c for c in cat if any(n in c['name'] for n in ['ReactorTank','CoolingPump','HVACUnit'])])
import openpyxl
w=openpyxl.load_workbook(R/'Docs/도면/Decision/원형공동/AfterSeconds_프랍환경_제작목록.xlsx',read_only=True,data_only=True)
rows=[]
for s in w:
 for i,r in enumerate(s.iter_rows(values_only=True),1):
  if any('B2' in str(v) for v in r):rows.append({'sheet':s.title,'row':i,'values':r})
(H/'workbook_B2.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
print('workbook B2 rows',len(rows))
