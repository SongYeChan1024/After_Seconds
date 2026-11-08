from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];P=R/'Unity/After_Seconds_Build_V0.01';O=R/'Docs/검수/2026-11-08_B5_CeilingLighting'
before=json.loads((O/'before.json').read_text(encoding='utf-8'));after=json.loads((O/'after.json').read_text(encoding='utf-8'));apply=json.loads((O/'apply.json').read_text(encoding='utf-8'))
allowed=set(apply['affectedTransforms']);transforms=[];protected=[];missing=[]
new={v['id']:v for v in after['hierarchy']}
for old in before['hierarchy']:
 n=new.get(old['id'])
 if not n:missing.append(old['path']);continue
 keys=[k for k in old if old[k]!=n[k]]
 if keys:
  row=dict(path=old['path'],fields=keys);transforms.append(row)
  if old['id'] not in allowed or any(k not in ['position','localPosition'] for k in keys):protected.append(row)
lights=[];params=[];new={v['id']:v for v in after['lights']}
def strip_refs(j):
 if isinstance(j,dict):return {k:strip_refs(v) for k,v in j.items() if k not in ['instanceID','m_GameObject']}
 if isinstance(j,list):return [strip_refs(v) for v in j]
 return j
for old in before['lights']:
 n=new.get(old['id'])
 if not n:missing.append(old['path']);continue
 keys=[k for k in old if k!='json' and old[k]!=n[k]]
 if keys:lights.append(dict(path=old['path'],fields=keys))
 if any(k!='position' for k in keys) or strip_refs(json.loads(old['json']))!=strip_refs(json.loads(n['json'])):params.append(old['path'])
colliders=[];new={v['id']:v for v in after['colliders']}
for old in before['colliders']:
 n=new.get(old['id'])
 if not n:missing.append(old['path']);continue
 if strip_refs(json.loads(old['json']))!=strip_refs(json.loads(n['json'])):colliders.append(old['path'])
renderers=[];new={v['id']:v for v in after['renderers']}
for old in before['renderers']:
 n=new.get(old['id'])
 if not n:missing.append(old['path']);continue
 keys=[k for k in ['active','enabled','rotation','mesh','prefab','materials'] if old[k]!=n[k]]
 if keys:renderers.append(dict(path=old['path'],fields=keys))
baseline=json.loads((R/'SourceAssets/B5_CeilingLighting/baseline.json').read_text(encoding='utf-8'));changed=[];deleted=[]
for name,h in baseline.items():
 p=P/name
 if not p.exists():deleted.append(name)
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=h:changed.append(name)
result=dict(baselineFiles=len(baseline),changedFiles=changed,deletedFiles=deleted,missingObjects=missing,transformChanges=transforms,unexpectedTransformChanges=protected,lightPositionChanges=lights,lightParameterChanges=params,colliderChanges=colliders,rendererChanges=renderers,ambientUnchanged=before['ambient']==after['ambient'],renderPipelineUnchanged=before['renderPipeline']==after['renderPipeline'],oldLights=len(before['lights']),newLights=len(after['lights'])-len(before['lights']))
(O/'preservation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['transformChanges','lightPositionChanges']},ensure_ascii=True,indent=2))
assert not protected and not params and not colliders and not renderers and not missing and not deleted
assert changed==['Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular.unity'],changed
