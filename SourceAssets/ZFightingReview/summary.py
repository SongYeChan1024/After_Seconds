from pathlib import Path
import json,sys
sys.stdout.reconfigure(encoding='utf-8')
for p in sorted((Path(__file__).parent/'results').glob('*.json')):
 if len(sys.argv)>1 and sys.argv[1] not in p.stem:continue
 d=json.loads(p.read_text());r=d['rows'];print('\nSCENE',p.stem)
 print('DUPLICATES',[(a['asset'].split('/')[-1],a['count']) for a in d['duplicateMeshes']])
 for a in d['overlaps'][:25]:print('CROSS',round(a['area'],3),r[a['a']]['path'],a['sa'],'<>',r[a['b']]['path'],a['sb'],'at',a['point'])
 for a in d['internal'][:15]:print('INTERNAL',round(a['excess'],3),r[a['renderer']]['path'],a['submesh'],a['point'])
