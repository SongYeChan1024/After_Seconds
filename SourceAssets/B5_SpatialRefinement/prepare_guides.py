from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
s=(R/'SourceAssets/B5_RemainingDomes/guides.py').read_text(encoding='utf-8').replace("f'RD_","f'SF_")
s=s.replace('for r in routes:reserve(r)','')
pos=s.index("for t in plan['tunnels'][2:]:")
s=s[:pos]+'''# Preserve C01 exactly while routing the C02 portion around the new control suite.
for route in routes:
 ids=[i for i,p in enumerate(route['points']) if math.hypot(p[0]+22,p[1]-18)<7.3]
 if ids:
  a,b=ids[0],ids[-1];ps=path('C02',route['points'][a],route['points'][b],route['code'],True)
  route['points']=route['points'][:a]+dense(ps)+route['points'][b+1:]
 reserve(route)
''' +s[pos:]
s=s.replace("if code in ['C01','C02','VA']:","if code=='C01':")
(H/'guides.py').write_text(s,encoding='utf-8')
s=(R/'SourceAssets/B5_RemainingDomes/walk_plan.py').read_text(encoding='utf-8').replace("[('VB',44,-28)]","[('VA',-44,28),('VB',44,-28)]")
# Include usable access to every living/exam compartment and work area's main aisle.
insert='''
for room in [r for r in plan['rooms'] if r!='C01']:
 r=plan['rooms'][room];cx,cz=r['position'][0],r['position'][2];door=r['doors'][0];a=[door['position'][0]-.75*math.cos(math.radians(door['angle'])),door['position'][1]-.75*math.sin(math.radians(door['angle']))]
 targets=[]
 for s in plan['structures']:
  if s['room']!=room:continue
  if s['kind'] in ['living_suite','exam_suite','command_suite','control_booth','observation_booth','review_booth','test_cell']:
   targets.append((s['kind']+'_'+str(len(targets)),[cx+s['x'],cz+s['z']]))
 if room=='N01':targets += [('rear_operator_access',[cx+3.9,cz+4.8])]
 for name,b in targets:
  ps=path(room,a,b,'');err=math.dist(ps[-1],b)
  if err>.65:raise RuntimeError(('Interior target blocked',room,name,b,ps[-1],err))
  routes.append(dict(id=room+'_'+name,points=[[p[0],-82,p[1]] for p in dense(ps)]))
'''
s=s.replace("(H/'walk_plan.json')",insert+"\n(H/'walk_plan.json')")
(H/'walk_plan.py').write_text(s,encoding='utf-8')
