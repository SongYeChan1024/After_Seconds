from pathlib import Path
import json,collections
H=Path(__file__).resolve().parent;d=json.loads((H/'geometry_scan/Level_B1_Circular.json').read_text());rows=d['rows']
print('DUPLICATES',[(x['asset'],x['count']) for x in d['duplicateMeshes']])
print('INTERNAL',[(rows[x['renderer']]['meshName'],round(x['excess'],3),x['submesh']) for x in d['internal'][:14]])
groups=collections.Counter()
for x in d['overlaps']:
 a,b=rows[x['a']],rows[x['b']];groups[(a['meshName'],b['meshName'])]+=1
print('OVERLAP GROUPS',groups.most_common(16))
for x in d['overlaps'][:12]:print(round(x['area'],4),rows[x['a']]['path'].split('/')[-1],rows[x['b']]['path'].split('/')[-1],x['point'])
