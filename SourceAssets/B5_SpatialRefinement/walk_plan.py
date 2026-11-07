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
for core,x,z in [('VA',-44,28),('VB',44,-28)]:
 ps=[[x-.96,-82,z-2.38]]
 for f in range(8):
  xx=-.96 if f%2==0 else .96;direction=1 if f%2==0 else-1;z0=-1.68*direction
  for i in range(12):ps.append([x+xx,-82+f*2+(i+1)/6,z+z0+direction*(i+.5)*.28])
  ps.append([x+xx,-82+f*2+2,z-z0+direction*.7])
  if f<7:ps.append([x-xx,-82+f*2+2,z-z0+direction*.7])
 routes.append(dict(id=core+'_96stairs_up',points=ps));routes.append(dict(id=core+'_96stairs_down',points=ps[::-1]))

for room in [r for r in plan['rooms'] if r!='C01']:
 r=plan['rooms'][room];cx,cz=r['position'][0],r['position'][2];door=r['doors'][0];a=[door['position'][0]-.75*math.cos(math.radians(door['angle'])),door['position'][1]-.75*math.sin(math.radians(door['angle']))]
 targets=[]
 for s in plan['structures']:
  if s['room']!=room:continue
  if s['kind'] in ['living_suite','exam_suite','command_suite','control_booth','observation_booth','review_booth','test_cell','security_suite']:
   loc={'living_suite':(0,0),'exam_suite':(.75,.2),'command_suite':(4.15,0),'control_booth':(0,.85),'observation_booth':(0,.85),'review_booth':(.9,.8),'test_cell':(0,-1.95),'security_suite':(0,-.6)}[s['kind']];ang=math.radians(s['yaw']);targets.append((s['kind']+'_'+str(len(targets)),[cx+s['x']+math.cos(ang)*loc[0]+math.sin(ang)*loc[1],cz+s['z']-math.sin(ang)*loc[0]+math.cos(ang)*loc[1]]))
 if room=='N01':targets += [('rear_operator_access',[cx+3.9,cz+4.8])]
 for name,b in targets:
  ps=path(room,a,b,'');err=math.dist(ps[-1],b)
  if err>.65:raise RuntimeError(('Interior target blocked',room,name,b,ps[-1],err))
  routes.append(dict(id=room+'_'+name,points=[[p[0],-82,p[1]] for p in dense(ps)]))

(H/'walk_plan.json').write_text(json.dumps(routes,indent=2),encoding='utf-8');print(len(routes),'walking routes')
