from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[1]
data=json.loads((H/'models.json').read_text(encoding='utf8'))
out=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/06.Data/AssetSources/B2_DetailMezzanine.json'
record={'version':'0.02','author':'송예찬','date':'2026-11-10','source':'Blender 5.2.2 LTS','scene':'Assets/Afrer_Seconds/01.Scenes/Stage/Level_B2_Circular.unity','sources':['SourceAssets/B2_DetailMezzanine/build.py','SourceAssets/B2_DetailMezzanine/services.py'],'description':'19 crouching service walkways with upper process pipes; 29 equipment connections; reduced red industrial practical lighting. No runtime gameplay code changes.','models':[]}
for name,m in data.items():
 p=Path(m['asset']);record['models'].append({'name':name,'asset':p.relative_to(R/'Unity/After_Seconds_Build_V0.01').as_posix(),'triangles':m['triangles'],'lod':bool(m.get('distance_only'))})
out.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
print('Recorded',len(record['models']),'models')
