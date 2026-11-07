"""Add approach paths to every new workstation, using measured scene occupancy. 송예찬."""
exec((__import__('pathlib').Path(__file__).resolve().parent/'walk_plan.py').read_text(encoding='utf-8'))
layout=json.loads((H/'layout.json').read_text(encoding='utf-8'));checks=[];failures=[]
for q in layout['placements']:
 if q['model'] in ['OD_PalletLoad_0','OD_PalletLoad_1','OD_E03_WorkflowFloor']:continue
 room=q['room'];r=plan['rooms'][room];cx,cz=r['position'][0],r['position'][2];door=r['doors'][0];a=[door['position'][0]-.75*math.cos(math.radians(door['angle'])),door['position'][1]-.75*math.sin(math.radians(door['angle']))]
 yaw=math.radians(q['yaw']);d=1.25
 if q['model']=='OD_InstrumentedTestRig':d=-2.0
 if q['model']=='OD_VL_FreightHoist':d=-2.75
 if q['model']=='OD_PipedDeconShower':d=1.5
 if q['model']=='OD_PalletTruck':d=-1.5
 b=[cx+q['position'][0]+math.sin(yaw)*d,cz+q['position'][2]+math.cos(yaw)*d]
 try:ps=path(room,a,b,'')
 except RuntimeError as ex:failures.append(dict(id=q['id'],error=str(ex),target=b));continue
 err=math.dist(ps[-1],b);checks.append(dict(id=q['id'],target=b,reached=ps[-1],offset=err))
 if err>.65:failures.append(dict(id=q['id'],error='Target blocked',target=b,reached=ps[-1],offset=err));continue
 routes.append(dict(id=q['id']+'_approach',points=[[p[0],-82,p[1]] for p in dense(ps)]))
(H/'walk_plan.json').write_text(json.dumps(routes,indent=2),encoding='utf-8');(H/'equipment_access.json').write_text(json.dumps(dict(checks=checks,failures=failures),indent=2),encoding='utf-8');print(len(routes),'routes including',len(checks),'equipment approaches');print('FAILED',json.dumps(failures))
