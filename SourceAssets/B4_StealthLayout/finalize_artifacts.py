from pathlib import Path
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
repository=Path(__file__).resolve().parents[2]
project=repository/'Unity/After_Seconds_Build_V0.01'
reports=repository/'Docs/검수/2026-11-06_B5_B4'
scene=json.loads((reports/'B4/scene_audit.json').read_text(encoding='utf-8'))
connections=json.loads((reports/'B4/connections.json').read_text(encoding='utf-8'))
controller=json.loads((reports/'B4/controller_audit.json').read_text(encoding='utf-8'))
play=json.loads((reports/'B4/play_audit.json').read_text(encoding='utf-8'))
assert not scene['missingAssets'] and scene['missingScripts']==0
assert all(item['passed'] for item in connections['doors'])
assert all(item['fromLeft'] and item['fromRight'] for item in connections['windows'])
assert not connections['missingDependencies']
assert all(item['passed'] for item in controller['results'])
assert not play['newWarningsAndErrors']
assert play['input']['distinctFrames']>10 and play['input']['distance']>0.5
assert play['restoredRunInBackground']['result'] is False
record_file=project/'Assets/Afrer_Seconds/06.Data/AssetSources/B4_Stealth_20261106.json'
record=json.loads(record_file.read_text(encoding='utf-8'))
record.update({'title':'B4 Stealth Scene V0.02','phase':'2026-11-06 final validation','staticColliders':scene['colliders'],'lights':93,'shadowLights':7,'bakedReflections':8,'highestLodTriangles':scene['highestLodTriangles'],'lodGroups':scene['lodGroups'],'details':'Assets/Afrer_Seconds/05.Model/Environment/B4/B4_ServiceDetails.fbx','floorMaterial':'Assets/Afrer_Seconds/05.Model/Environment/B4/Materials/B4SL_Floor.mat','spawnYaw':243.43494,'validation':'Docs/검수/2026-11-06_B5_B4/검수결과.md'})
record_file.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
documents=[repository/'Docs/이어하기_2026-11-06.md',reports/'검수결과.md']
missing_links=[]
for document in documents:
    for link in re.findall(r'\]\(([^)]+)\)',document.read_text(encoding='utf-8')):
        if not link.startswith(('https:','http:','#')) and not (document.parent/link.split('#')[0]).exists():
            missing_links.append({'document':str(document.relative_to(repository)),'target':link})
assert not missing_links,missing_links
new_assets=[project/'Assets/Afrer_Seconds/01.Scenes/Stage/Level_B4_Stealth.unity',project/'Assets/Afrer_Seconds/05.Model/Environment/B4/B4_Stealth_Architecture.fbx',project/'Assets/Afrer_Seconds/05.Model/Environment/B4/B4_ServiceDetails.fbx',record_file]
assert all(Path(str(asset)+'.meta').exists() for asset in new_assets)
summary={'author':'송예찬','scene':scene['scene'],'highestLodTriangles':scene['highestLodTriangles'],'colliders':scene['colliders'],'doorsPassed':len(connections['doors']),'windowChecksPassed':len(connections['windows'])*2,'controllerCasesPassed':len(controller['results']),'playMovedMetres':play['input']['distance'],'playDistinctFrames':play['input']['distinctFrames'],'newPlayWarningsAndErrors':0,'missingDocumentLinks':missing_links,'requiredAssetMetaPairs':len(new_assets),'runtimeCodeAdded':0}
(reports/'final_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
