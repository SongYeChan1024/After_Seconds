from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'Unity/After_Seconds_Build_V0.01';O=R/'Docs/검수/2026-11-08_B4_Observation'
baseline=json.loads((H/'baseline.json').read_text(encoding='utf-8'));changed=[];missing=[]
for rel,digest in baseline.items():
 p=P/rel
 if not p.exists():missing.append(rel)
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=digest:changed.append(rel)
r={'protectedFiles':len(baseline),'unchanged':len(baseline)-len(changed)-len(missing),'changed':changed,'missing':missing,'excluded':'Assets/Temp capture cache only','B5SceneUnchanged':'Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular.unity' not in changed+missing}
(O/'preservation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=True))
if changed or missing:raise SystemExit(1)
