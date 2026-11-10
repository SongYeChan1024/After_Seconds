import sys,json,importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding='utf8')
H=Path(__file__).resolve().parent; R=H.parents[1]
print('shapely',bool(importlib.util.find_spec('shapely')))
a=json.loads((H/'before.json').read_text()); by={t['name']:t for t in a}
for room in ['C02','C04','W02','E01','E02']:
 print('\nROOM',room)
 for t in a:
  if t['enabled'] and t['name'].startswith('B2_'+room+'_') and t['parent'] in ['Equipment','Mezzanine']:
   print(t['name'],t['local'],t['rotation'],t['scale'])
print('groups',[(t['name'],t['parent'],t['local']) for t in a if ('ProcessIsland' in t['name'] or 'ServiceMezzanine' in t['name'] or 'Supplement' in t['name'])])
print('BN props')
d=json.loads((R/'SourceAssets/B2_DomeNetwork/layout.json').read_text(encoding='utf8'))
for p in {p['model']:p for p in d['placements']}.values(): print(p['model'],p.get('size'),p.get('center'),p.get('asset'))
