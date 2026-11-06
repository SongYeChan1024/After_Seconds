import json, hashlib, collections
from pathlib import Path
from pypdf import PdfReader
import openpyxl
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
SOURCE=Path('C:/Users/503-26/Documents/Codex/2026-11-06/dl/outputs/after_seconds_multilevel')
OUT=REPO/'Docs/도면/원형공동'
OUT.mkdir(parents=True,exist_ok=True)
d=json.loads(next(SOURCE.glob('*.json')).read_text(encoding='utf-8'))
pdf=PdfReader(next(SOURCE.glob('*.pdf')))
text='\n'.join(p.extract_text() for p in pdf.pages)
wb=openpyxl.load_workbook(next(SOURCE.glob('*.xlsx')),read_only=True,data_only=False)
files={str(p.relative_to(SOURCE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.iterdir() if p.is_file()}
summary={'source':str(SOURCE),'source_hashes':files,'pdf_pages':len(pdf.pages),'counts':{k:len(d[k]) for k in ['floors','rooms','tunnels','vertical','placements','catalog','activity_program']},'workbook':{s.title:{'rows':s.max_row,'columns':s.max_column} for s in wb},'roles':dict(collections.Counter(p.get('role','') for p in d['placements'])),'missing_terms':{k:k not in text for k in ['메자닌','그레이팅','인수인계 기록','바닥 안내선','조명 스위치']},'asset_candidates':[]}
for c in d['catalog']:
 if c.get('asset'): summary['asset_candidates'].append({'code':c['code'],'asset':c['asset'],'exists':(REPO/'Unity/After_Seconds_Build_V0.01'/c['asset']).exists()})
(HERE/'source_audit.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'source_design.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'source_pdf_text.txt').write_text(text,encoding='utf-8')
protected={}
unity=REPO/'Unity/After_Seconds_Build_V0.01'
for p in (unity/'Assets').rglob('*'):
 if p.is_file() and (p.suffix in ('.cs','.unity','.meta') or p.name.startswith('AD_WallPanel')):
  protected[str(p.relative_to(unity))]=hashlib.sha256(p.read_bytes()).hexdigest()
(HERE/'protected_before.json').write_text(json.dumps(protected,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k not in ['asset_candidates','source_hashes']},ensure_ascii=False))
print('existing assets',len(summary['asset_candidates']),'missing',sum(not a['exists'] for a in summary['asset_candidates']),'protected',len(protected))
