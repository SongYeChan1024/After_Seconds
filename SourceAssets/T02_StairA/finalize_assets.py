from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_T02_StairA'
base=json.loads((H/'baseline.json').read_text(encoding='utf-8'));changed=[];missing=[];unexpected=[]
for rel,sha in base.items():
    p=R/rel
    if not p.exists():missing.append(rel);continue
    if hashlib.sha256(p.read_bytes()).hexdigest()==sha:continue
    changed.append(rel)
    allowed=p.name=='Level_B5_Circular.unity' or p.name in [f'SC_Display_{i:02}.png' for i in range(1,5)] or ('Environment' in p.parts and p.name.startswith('ND_'))
    if not allowed:unexpected.append(rel)
result=dict(baselineFiles=len(base),preservedFiles=len(base)-len(changed)-len(missing),changed=changed,missing=missing,unexpected=unexpected)
(D/'file_preservation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
assert not missing and not unexpected,result
print(json.dumps(dict(baseline=len(base),changed=len(changed),preserved=result['preservedFiles']),ensure_ascii=True))
p=H/'Audit.cs';s=p.read_text(encoding='utf-8');old='newBehaviours=art.GetComponentsInChildren<MonoBehaviour>().Length,headroomSamples='
new='newBehaviours=art.GetComponentsInChildren<MonoBehaviour>().Length,newBehaviourTypes=art.GetComponentsInChildren<MonoBehaviour>().Select(b=>b.GetType().FullName).Distinct().ToArray(),newGameplayBehaviours=art.GetComponentsInChildren<MonoBehaviour>().Count(b=>b.GetType().FullName!="UnityEngine.Rendering.Universal.UniversalAdditionalLightData"),headroomSamples='
if old in s:p.write_text(s.replace(old,new),encoding='utf-8')
p=H/'RecordSource.cs';s=p.read_text(encoding='utf-8');s=s.replace('plan,method="Local Unity floor meshes and printed destination stencils; non-emissive paint; no new runtime code"','plan,architecture=JObject.Parse(File.ReadAllText(repo+"/SourceAssets/T02_StairA/geometry.json")),models=JObject.Parse(File.ReadAllText(repo+"/SourceAssets/T02_StairA/model_manifest.json")),method="Local manufactured stair core/corridor meshes with bevels and shared PBR maps; destination floor paint; 8 upper luminaire lights; no new gameplay code"')
p.write_text(s,encoding='utf-8')
