from pathlib import Path
import json,hashlib,collections
H=Path(__file__).resolve().parent;R=H.parents[1];A=R/'Unity/After_Seconds_Build_V0.01/Assets'
guard=H/'protected_before.json'
if guard.exists():raise RuntimeError('Snapshot exists; do not overwrite')
ps=list(A.rglob('*.cs'))+list(A.rglob('*.controller'))+list((A/'Afrer_Seconds/01.Scenes').rglob('*.unity'))
guard.write_text(json.dumps({str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in ps},indent=2),encoding='utf-8')
d=json.loads((R/'Docs/도면/Decision/원형공동/facility_layout.json').read_text('utf-8'))
rows=[p for p in d['placements'] if p['floor']=='B5' and p['room']=='C01']
cats=[c for c in d['catalog'] if c['code'] in {p['code'] for p in rows}]
(H/'source_c01.json').write_text(json.dumps({'placements':rows,'catalog':cats},ensure_ascii=False,indent=2),encoding='utf-8')
print('ROWS',len(rows),'TYPES',len(cats))
for p in rows:print(p['id'],p['code'],p['name'],p['role'],p.get('parent'),p['x'],p['v'],p['base'],p['yaw'])
print('ASSETS')
for c in cats:print(c['code'],c['name'],c.get('asset'))
