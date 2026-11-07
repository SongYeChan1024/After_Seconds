"""Local preservation audit. Author 송예찬."""
from pathlib import Path
import json,hashlib,collections
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_B5_RemainingDomes';A=R/'Unity/After_Seconds_Build_V0.01/Assets'
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
baseline=load(H/'assets_before.json');changed=[];missing=[]
for rel,digest in baseline.items():
 p=A/rel
 if not p.exists():missing.append(rel)
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=digest:changed.append(rel)
new=[str(p.relative_to(A)).replace('\\','/') for p in A.rglob('*') if p.is_file() and str(p.relative_to(A)) not in baseline]
models=load(H/'models.json');plan=load(H/'plan.json');before=load(D/'before.json');after=load(D/'verification.json')
oldh={o['path']:o for o in before['hierarchy']};newh={o['path']:o for o in after['hierarchy']}
def groups(rows):
 g=collections.defaultdict(list)
 for o in rows:g[o['path']].append(o)
 return g
before_h_groups=groups(before['hierarchy']);after_h_groups=groups(after['hierarchy'])
def multiset(rows):return collections.Counter(json.dumps(o,sort_keys=True) for o in rows)
duplicate_path_changes=[dict(path=k,before=v,after=after_h_groups.get(k,[])) for k,v in before_h_groups.items() if len(v)>1 and multiset(v)!=multiset(after_h_groups.get(k,[]))]
transform_changes=[];active_changes=[]
for name,o in oldh.items():
 if name not in newh:continue
 n=newh[name]
 fields=[k for k in ('position','rotation','scale') if o.get(k)!=n.get(k)]
 if fields:transform_changes.append(dict(path=name,fields=fields,before=o,after=n))
 if o.get('active')!=n.get('active'):active_changes.append(dict(path=name,before=o.get('active'),after=n.get('active')))
lights_old={o['path']:o for o in before['lights']};lights_new={o['path']:o for o in after['lights']}
lights_changed=[dict(path=k,before=o,after=lights_new.get(k)) for k,o in lights_old.items() if o!=lights_new.get(k)]
reparent_mismatch=[];archive_max_position=0;archive_max_angle=0
for k,o in oldh.items():
 if k in newh:continue
 prefix,door_and_child=k.split('/Pocket_Doors_Open/',1)
 door,child=door_and_child.split('/',1)
 nk=prefix+'/Pocket_Doors_Open/'+door+'/Previous_Rectangular_Door_Inactive/'+child
 n=newh.get(nk)
 if n is None:reparent_mismatch.append(k);continue
 pd=max(abs(x-y) for x,y in zip(o['position'],n['position']))
 rd=max(abs((x-y+180)%360-180) for x,y in zip(o['rotation'],n['rotation']))
 sd=max(abs(x-y) for x,y in zip(o['scale'],n['scale']))
 archive_max_position=max(archive_max_position,pd);archive_max_angle=max(archive_max_angle,rd)
 if pd>.0001 or rd>.001 or sd>.00001 or o['active']!=n['active']:reparent_mismatch.append(k)
result=dict(author='송예찬',baselineFiles=len(baseline),unchangedFiles=len(baseline)-len(changed)-len(missing),changedFiles=changed,missingFiles=missing,newFiles=new,gameCodeChanges=[p for p in changed+missing if p.endswith(('.cs','.controller','.overrideController','.anim'))],models=len(models),categories=dict(collections.Counter(v['category'] for v in models.values())),modelTriangles=sum(v['triangles'] for v in models.values()),placements=len(plan['placements']),placementsByRoom=dict(collections.Counter(p['room'] for p in plan['placements'])),beforeKeys=list(before),transformChanges=transform_changes,duplicatePathChanges=duplicate_path_changes,activeChanges=active_changes,reparentedOldPaths=[k for k in oldh if k not in newh],lightsBefore=len(before['lights']),lightsAfter=len(after['lights']),lightChanges=lights_changed)
(D/'preservation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
result['archivedDoorTransformMismatches']=reparent_mismatch
result['archivedDoorMaxPositionDeltaMeters']=archive_max_position
result['archivedDoorMaxAngleDeltaDegrees']=archive_max_angle
(D/'preservation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['newFiles','transformChanges','activeChanges','reparentedOldPaths','lightChanges']},ensure_ascii=True,indent=2))
print('transform changes',len(transform_changes),'active changes',len(active_changes),'reparented',len(result['reparentedOldPaths']),'lights changed',len(lights_changed))
print(json.dumps(dict(transforms=[(o['path'],o['fields']) for o in transform_changes],lights=lights_changed),ensure_ascii=True,indent=2))
