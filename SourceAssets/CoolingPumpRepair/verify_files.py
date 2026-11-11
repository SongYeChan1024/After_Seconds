"""이번 보수 직전 백업과 비교한다. Git HEAD는 이전 깊이 충돌 보수를 포함하지 않는다."""
import json,hashlib,re,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'Unity/After_Seconds_Build_V0.01'
scene=P/'Assets/Afrer_Seconds/01.Scenes/Stage/Level_B2_Circular.unity'
backup=Path.home()/'Documents/Codex/Backups/AfterSeconds_CoolingPump_20261111'/scene.name
def blocks(p):
 text=p.read_text(encoding='utf-8');out={}
 for m in re.finditer(r'^--- !u!(\d+) &(-?\d+)[^\n]*\n([\s\S]*?)(?=^--- !u!|\Z)',text,re.M):out[m[2]]=(int(m[1]),m[3])
 return out
a,b=blocks(backup),blocks(scene);changed=[];unexpected=[]
for key,(kind,text) in a.items():
 if key not in b:unexpected.append({'removed':key,'type':kind});continue
 if b[key][1]!=text:
  changed.append({'id':key,'type':kind})
  if kind not in [4,23,1001,205]:unexpected.append({'changed':key,'type':kind})
base=json.loads((H/'protected.json').read_text());protected_changes=[k for k,v in base.items() if hashlib.sha256((R/k).read_bytes()).hexdigest()!=v]
unexpected += [{'protected':k} for k in protected_changes if k!=scene.relative_to(R).as_posix()]
result={'baseline':'Post-VARCO-three-prop-repair backup, before cooling-pump repair','originalSceneObjects':len(a),'removedOriginalObjects':len(set(a)-set(b)),'addedSceneObjects':len(set(b)-set(a)),'changedComponents':changed,'protectedChanges':protected_changes,'errors':unexpected}
(H/'preservation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'addedObjects':result['addedSceneObjects'],'changedTypes':{k:sum(x['type']==k for x in changed) for k in set(x['type'] for x in changed)},'protectedChanges':protected_changes,'errors':unexpected},ensure_ascii=False))
