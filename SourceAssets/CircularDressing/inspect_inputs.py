from pathlib import Path
import json,hashlib,openpyxl
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
U=ROOT/'Unity/After_Seconds_Build_V0.01'
SRC=next(Path('C:/Users/503-26/Documents/Codex/2026-11-06/dl/outputs/after_seconds_multilevel').glob('*.xlsx'))
w=openpyxl.load_workbook(SRC,data_only=False)
info={'source':str(SRC),'sheets':[]}
for s in w:
 rows=list(s.values)
 info['sheets'].append({'name':s.title,'rows':s.max_row,'cols':s.max_column,'values':rows,'tables':{k:v.ref for k,v in s.tables.items()} if False else [dict(name=t.name,ref=t.ref) for t in s.tables.values()]})
 print(s.title,'row5',rows[4],'row6',rows[5])
(HERE/'workbook_source.json').write_text(json.dumps(info,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
protected={}
for p in U.rglob('*'):
 if not p.is_file() or not (p.is_relative_to(U/'Assets') or p.is_relative_to(U/'ProjectSettings')):continue
 if p.suffix in ['.cs','.unity','.meta'] or p.is_relative_to(U/'ProjectSettings'):
  protected[str(p.relative_to(U))]=hashlib.sha256(p.read_bytes()).hexdigest()
(HERE/'protected_before.json').write_text(json.dumps(protected,indent=2),encoding='utf-8')
print('SCENES',[str(p.relative_to(U)) for p in (U/'Assets').rglob('*.unity') if '/Samples/' not in p.as_posix()])
d=json.loads((ROOT/'Docs/도면/원형공동/facility_layout.json').read_text('utf-8'))
print('CATALOG',[(x['code'],x['name']) for x in d['catalog']])
print('B5 tunnels',d['floors'][0]['tunnels'][:7])
