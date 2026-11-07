import json,math,heapq,ast
from pathlib import Path
import numpy as np
H=Path(__file__).resolve().parent;plan=json.loads((H/'plan.json').read_text(encoding='utf-8'));grids=json.loads((H/'grids.json').read_text(encoding='utf-8'));reserved={c:{} for c in grids}
tree=ast.parse((H/'guides.py').read_text(encoding='utf-8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['dense','path']],type_ignores=[]),'routing','exec'))
guides=json.loads((H/'guidance.json').read_text(encoding='utf-8'));routes=[dict(id=r['id'],points=[[p[0],-82,p[1]] for p in r['points']]) for r in guides['routes']]
for room,r in plan['rooms'].items():
 ends=[]
 for d in r['doors']:
  t=math.radians(d['angle']);ends.append([d['position'][0]-.75*math.cos(t),d['position'][1]-.75*math.sin(t)])
 for i,a in enumerate(ends):
  for j,b in enumerate(ends[i+1:],i+1):
   ps=path(room,a,b,'');routes.append(dict(id=room+'_internal_'+str(i)+'_'+str(j),points=[[p[0],-82,p[1]] for p in dense(ps)]))
for core,x,z in [('VB',44,-28)]:
 ps=[[x-.96,-82,z-2.38]]
 for f in range(8):
  xx=-.96 if f%2==0 else .96;direction=1 if f%2==0 else-1;z0=-1.68*direction
  for i in range(12):ps.append([x+xx,-82+f*2+(i+1)/6,z+z0+direction*(i+.5)*.28])
  ps.append([x+xx,-82+f*2+2,z-z0+direction*.7])
  if f<7:ps.append([x-xx,-82+f*2+2,z-z0+direction*.7])
 routes.append(dict(id=core+'_96stairs_up',points=ps));routes.append(dict(id=core+'_96stairs_down',points=ps[::-1]))
(H/'walk_plan.json').write_text(json.dumps(routes,indent=2),encoding='utf-8');print(len(routes),'walking routes')
