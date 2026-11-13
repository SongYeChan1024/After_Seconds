import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mesh import *
d=json.loads((H/'litter_mesh.json').read_text());ground=json.loads((H/'litter_ground.json').read_text());m=Model('ES_RootLitter');m.v=d['v'];m.f=d['f'];m.fm=d['fm'];m.m=d['m']
# Keep each leaf's fold and stem thickness, conform its base to the real scene surface.
roots=json.loads((H/'roots.json').read_text())
for i,(x,y,z) in enumerate(m.v):
 root=min(roots,key=lambda r:(r['world'][0]-x)**2+(r['world'][2]-z)**2);offset=max(.003,min(.035,y-root['world'][1]));m.v[i]=(x,ground[i]+offset,z)
report=m.export();report['leaves']=922;(H/'litter.json').write_text(json.dumps(report,indent=2));print('LITTER_CONFORMED',len(m.v))
