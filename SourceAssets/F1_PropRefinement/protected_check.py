from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/Review/2026-11-13_1F_PropRefinement'
before=json.loads((O/'protected_before.json').read_text());allowed=lambda p:p.endswith('/Level_1F_Factory.unity') or ('/Textures/AE_Reflection_' in p and p.endswith('.exr'))
# All original assets remain protected. Hashing is read-only and runs after the final save.
changed=[];approved=[]
for p,h in before.items():
 if not (R/p).is_file() or hashlib.sha256((R/p).read_bytes()).hexdigest()!=h:
  (approved if allowed(p) else changed).append(p)
b={v['path']:v for v in json.loads((O/'before_transforms.json').read_text())};a={v['path']:v for v in json.loads((O/'after_transforms.json').read_text())};different=[]
for p,v in b.items():
 if p not in a or any(v[k]!=a[p][k] for k in ['local','rotation','scale','active']):different.append(p)
# Collider JSON includes stable serialized instance references in this same saved scene.
def colliders(v):
 result=[]
 def clean(obj):
  if isinstance(obj,dict):return {k:clean(v) for k,v in obj.items() if k!='instanceID'}
  if isinstance(obj,list):return [clean(x) for x in obj]
  return obj
 for c in v['colliders']:result.append({'type':c['type'],'settings':clean(json.loads(c['json']))})
 return result
collider_changes=[p for p,v in b.items() if p not in a or colliders(v)!=colliders(a[p])]
result={'protectedFiles':len(before),'unexpectedFileChanges':changed,'allowedFileChanges':approved,'existingTransforms':len(b),'transformChanges':different,'addedTransforms':len(a)-len(b),'colliderChanges':collider_changes}
(O/'protected_check.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2));assert not changed and not different and not collider_changes
