from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'Unity/After_Seconds_Build_V0.01';O=R/'Docs/검수/2026-11-08_B4_ExperimentOperations'
b=json.loads((H/'baseline.json').read_text(encoding='utf8'));changed=[];missing=[];same=0
for rel,digest in b.items():
 p=P/rel
 if not p.exists():missing.append(rel)
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=digest:changed.append(rel)
 else:same+=1
expected=['Assets/Afrer_Seconds/01.Scenes/Stage/Level_B4_Circular.unity']
result={'protectedFiles':len(b),'unchanged':same,'changed':changed,'missing':missing,'expectedChanges':expected,'unexpectedChanges':[f for f in changed if f not in expected]}
(O/'preservation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(result,ensure_ascii=False));assert not missing and not result['unexpectedChanges']
